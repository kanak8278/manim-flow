"""
Agent — LLM wrapper with retry, caching, thinking, and token tracking.

Adapted from the document-update agent_core for manimflow's pipeline.

Usage:
    agent = Agent(system_prompt="...", tools=[])
    agent.add_user_message("Generate 3 story angles for...")

    content, stop_reason, usage = await agent.call()
    text = agent.extract_text(content)  # convenience

    # Single-shot convenience (backward compat with old call_llm):
    text = await call_llm(system_prompt, user_prompt)
"""

import asyncio
import base64
import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

import anthropic
from anthropic import APIError
from httpx import RemoteProtocolError, ConnectError, TimeoutException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    retry_if_exception_type,
)

from . import tracing
from .config import (
    MODEL as DEFAULT_MODEL,
    LLM_PROVIDER,
    BEDROCK_MODEL_ID,
    ADAPTIVE_THINKING_MODELS,
    CONTEXT_1M_MODELS,
    MAX_TOKENS_DEFAULT,
    ENABLE_THINKING,
    THINKING_BUDGET,
    ENABLE_1M_CONTEXT,
    ENABLE_CACHING,
    CACHE_TTL,
)

logger = logging.getLogger(__name__)

BEDROCK_REGION = os.environ.get("AWS_REGION", "us-east-1")


@dataclass
class AgentUsage:
    """Cumulative token usage across all calls."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    api_calls: int = 0

    def add(self, usage_dict: dict):
        self.input_tokens += usage_dict.get("input_tokens", 0)
        self.output_tokens += usage_dict.get("output_tokens", 0)
        self.cache_read_input_tokens += usage_dict.get(
            "cache_read_input_tokens", 0
        )
        self.cache_creation_input_tokens += usage_dict.get(
            "cache_creation_input_tokens", 0
        )
        self.api_calls += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
        }


class Agent:
    """Manages a single LLM conversation with optional tool-use support."""

    def __init__(
        self,
        system_prompt: str,
        tools: list[dict] | None = None,
        model: str | None = None,
        provider: str | None = None,
        max_tokens: int = MAX_TOKENS_DEFAULT,
        enable_caching: bool = ENABLE_CACHING,
        cache_ttl: str = CACHE_TTL,
        enable_thinking: bool = ENABLE_THINKING,
        thinking_budget: int = THINKING_BUDGET,
        enable_1m_context: bool = ENABLE_1M_CONTEXT,
    ):
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model or DEFAULT_MODEL
        self.provider = provider or LLM_PROVIDER
        self.max_tokens = max_tokens
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.enable_thinking = enable_thinking
        self.thinking_budget = thinking_budget
        self.enable_1m_context = enable_1m_context

        self.messages: list[dict] = []
        self.usage = AgentUsage()
        self.client = self._create_client()

    # ── Client creation ─────────────────────────────────────────

    def _create_client(self):
        if self.provider == "bedrock":
            try:
                from anthropic import AnthropicBedrock

                logger.info(
                    f"Agent using Bedrock (region={BEDROCK_REGION}, model={BEDROCK_MODEL_ID})"
                )
                return AnthropicBedrock(aws_region=BEDROCK_REGION)
            except ImportError:
                logger.error(
                    "AnthropicBedrock not available — install anthropic[bedrock]"
                )
                raise
        else:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not set and provider=anthropic"
                )
            return anthropic.Anthropic(api_key=api_key)

    # ── Request building ────────────────────────────────────────

    def _build_request(self) -> dict:
        """Build the full request dict for the API call."""
        request = {
            "model": self._get_model_id(),
            "max_tokens": self.max_tokens,
            "messages": self._clean_messages(),
        }

        request["system"] = self._prepare_system()

        if self.tools:
            request["tools"] = self._prepare_tools()

        self._add_thinking_config(request)

        betas = self._collect_betas()
        if betas:
            request["betas"] = betas

        return request

    def _clean_messages(self) -> list[dict]:
        """Strip internal metadata fields before sending to API."""
        cleaned = []
        for msg in self.messages:
            if any(k.startswith("_") for k in msg):
                cleaned.append(
                    {k: v for k, v in msg.items() if not k.startswith("_")}
                )
            else:
                cleaned.append(msg)
        return cleaned

    def _get_model_id(self) -> str:
        if self.provider == "bedrock":
            return BEDROCK_MODEL_ID
        return self.model

    def _prepare_system(self):
        """System prompt with optional cache_control."""
        if self.enable_caching:
            return [
                {
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": self._cache_control(),
                }
            ]
        return self.system_prompt

    def _prepare_tools(self) -> list[dict]:
        """Tool definitions with optional cache_control on the last tool."""
        if not self.tools:
            return []
        if not self.enable_caching:
            return self.tools

        tools_copy = [dict(t) for t in self.tools]
        tools_copy[-1] = {
            **tools_copy[-1],
            "cache_control": self._cache_control(),
        }
        return tools_copy

    def _cache_control(self) -> dict:
        cc = {"type": "ephemeral"}
        if self.cache_ttl and self.cache_ttl != "5m":
            cc["ttl"] = self.cache_ttl
        return cc

    def _add_thinking_config(self, request: dict):
        if not self.enable_thinking:
            return

        model_base = (
            self.model.split("-2")[0] if "-2" in self.model else self.model
        )
        if model_base in ADAPTIVE_THINKING_MODELS:
            request["thinking"] = {"type": "adaptive"}
        else:
            request["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget,
            }

    def _collect_betas(self) -> list[str]:
        betas = []

        if self.enable_1m_context and self.model in CONTEXT_1M_MODELS:
            betas.append("context-1m-2025-08-07")

        if self.enable_thinking:
            model_base = (
                self.model.split("-2")[0]
                if "-2" in self.model
                else self.model
            )
            if model_base not in ADAPTIVE_THINKING_MODELS:
                betas.append("interleaved-thinking-2025-05-14")

        if self.enable_caching and self.cache_ttl == "1h":
            betas.append("extended-cache-ttl-2025-04-11")

        return betas

    # ── API call with retry ────────────────────────────────────

    @tracing.observe(as_type="generation")
    async def call(self) -> tuple[list, str, dict]:
        """
        Make one LLM call with current messages.

        Returns:
            (content_blocks, stop_reason, usage_dict)
        """
        request = self._build_request()
        response = await self._api_call(request)

        usage_dict = {}
        if hasattr(response, "usage"):
            usage_dict = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
            if hasattr(response.usage, "cache_read_input_tokens"):
                usage_dict["cache_read_input_tokens"] = (
                    response.usage.cache_read_input_tokens or 0
                )
            if hasattr(response.usage, "cache_creation_input_tokens"):
                usage_dict["cache_creation_input_tokens"] = (
                    response.usage.cache_creation_input_tokens or 0
                )

        self.usage.add(usage_dict)

        # Log to Langfuse
        tracing.update_generation(
            model=self.model,
            usage=usage_dict,
            metadata={
                "stop_reason": response.stop_reason,
                "has_tools": bool(self.tools),
                "call_number": self.usage.api_calls,
            },
        )

        return response.content, response.stop_reason, usage_dict

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(
            (
                RemoteProtocolError,
                ConnectError,
                TimeoutException,
            )
        )
        | retry_if_exception(
            lambda e: isinstance(e, APIError) and e.status_code in (429, 500, 529)
        ),
    )
    async def _api_call(self, request: dict):
        """Make the API call. Retries on transient errors."""
        use_beta = "betas" in request
        if use_beta:
            return await asyncio.to_thread(
                self.client.beta.messages.create, **request
            )
        else:
            return await asyncio.to_thread(
                self.client.messages.create, **request
            )

    # ── Message management ──────────────────────────────────────

    def add_user_message(self, content):
        """Append a user message (string or structured content blocks)."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        """Append an assistant message (raw content blocks from API)."""
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_results(self, results: list[dict]):
        """Append tool results as a user message."""
        self.messages.append({"role": "user", "content": results})

    # ── Anchor management ───────────────────────────────────────

    def add_anchor(self, section_id: str, round_num: int, text: str):
        """Append a fork anchor message with metadata for lookup."""
        self.messages.append(
            {
                "role": "user",
                "content": text,
                "_fork_anchor": True,
                "_section_id": section_id,
                "_round": round_num,
            }
        )

    def find_latest_anchor(
        self, section_id: str
    ) -> tuple[Optional[int], Optional[dict]]:
        """Find the most recent anchor for a section."""
        for i in range(len(self.messages) - 1, -1, -1):
            msg = self.messages[i]
            if msg.get("_section_id") == section_id and msg.get(
                "_fork_anchor"
            ):
                return i, msg
        return None, None

    # ── Snapshot & Fork ─────────────────────────────────────────

    def snapshot(self, up_to_index: int = None) -> list[dict]:
        """Return a copy of messages, optionally up to an index (inclusive)."""
        if up_to_index is not None:
            return list(self.messages[: up_to_index + 1])
        return list(self.messages)

    @classmethod
    def fork_from(cls, parent: "Agent", up_to_index: int) -> "Agent":
        """Create a new Agent forked from parent's conversation."""
        fork = cls(
            system_prompt=parent.system_prompt,
            tools=parent.tools,
            model=parent.model,
            provider=parent.provider,
            max_tokens=parent.max_tokens,
            enable_caching=parent.enable_caching,
            cache_ttl=parent.cache_ttl,
            enable_thinking=parent.enable_thinking,
            thinking_budget=parent.thinking_budget,
            enable_1m_context=parent.enable_1m_context,
        )
        fork.messages = parent.snapshot(up_to_index)
        return fork

    # ── Context window management ───────────────────────────────

    def estimate_token_count(self) -> int:
        """Rough estimate of current context size (1 token ~ 4 chars)."""
        total_chars = len(self.system_prompt)
        for msg in self.messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    total_chars += len(str(block))
        return total_chars // 4

    def should_enable_1m_context(self, threshold: int = 180_000) -> bool:
        """Check if approaching 200K context limit."""
        return self.estimate_token_count() >= threshold

    # ── Agentic loop ───────────────────────────────────────────

    @tracing.observe()
    async def run(
        self,
        tool_executor=None,
        max_tool_rounds: int = 5,
    ) -> str:
        """Run an agentic loop: call LLM, handle tool use, repeat.

        The LLM decides if/when to call tools. We execute them and feed
        results back until the LLM returns a text response (end_turn).

        Args:
            tool_executor: Callable(tool_name, tool_input) -> str.
                           If None, uses knowledge.tool.execute_tool.
            max_tool_rounds: Max tool use rounds before forcing stop.

        Returns:
            Final text response from the LLM.
        """
        if tool_executor is None:
            from ..knowledge.tool import execute_tool
            tool_executor = execute_tool

        for round_num in range(max_tool_rounds):
            content, stop_reason, usage = await self.call()

            if stop_reason != "tool_use":
                # LLM is done — return text
                return self.extract_text(content)

            # LLM wants to use tools — execute them
            self.add_assistant_message(content)

            tool_results = []
            for block in content:
                if hasattr(block, "type") and block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # Build concise summary of tool call
                    query = tool_input.get("query", "")
                    filters = {k: v for k, v in tool_input.items()
                               if k not in ("query", "limit") and v}
                    filter_str = f" filters={filters}" if filters else ""
                    print(f"    [TOOL] {tool_name}(\"{query}\"{filter_str})")
                    logger.info(f"Tool call: {tool_name}({tool_input})")

                    try:
                        result_text = tool_executor(tool_name, tool_input)
                        # Show result summary
                        result_lines = result_text.strip().split("\n")
                        doc_count = sum(1 for l in result_lines if l.startswith("## "))
                        if doc_count:
                            print(f"    [RESULT] {doc_count} docs, {len(result_text)} chars")
                        elif len(result_text) > 100:
                            print(f"    [RESULT] {len(result_text)} chars")
                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        result_text = f"Error executing {tool_name}: {e}"
                        print(f"    [ERROR] {e}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

            if tool_results:
                self.add_tool_results(tool_results)
            else:
                # stop_reason was tool_use but no tool_use blocks found
                logger.warning("stop_reason=tool_use but no tool_use blocks")
                return self.extract_text(content)

        # Max rounds — force a final response without tools
        print(f"    [TOOL] Hit max_tool_rounds={max_tool_rounds}, forcing final response")
        content, _, _ = await self.call()
        return self.extract_text(content)

    # ── Convenience helpers ─────────────────────────────────────

    @staticmethod
    def extract_text(content_blocks: list) -> str:
        """Extract concatenated text from API response content blocks."""
        texts = []
        for block in content_blocks:
            if hasattr(block, "text"):
                texts.append(block.text)
            elif isinstance(block, dict) and block.get("type") == "text":
                texts.append(block["text"])
        return "\n".join(texts)

    @staticmethod
    def extract_tool_uses(content_blocks: list) -> list[dict]:
        """Extract tool_use blocks from API response."""
        uses = []
        for block in content_blocks:
            if hasattr(block, "type") and block.type == "tool_use":
                uses.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
        return uses


# ─── Backward-compatible call_llm ────────────────────────────────

async def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 8192,
    images: list[str] | None = None,
) -> str:
    """Single-shot LLM call. Drop-in async replacement for the old call_llm.

    Creates a fresh Agent per call — no conversation history.
    For multi-turn conversations, use Agent directly.
    """
    agent = Agent(
        system_prompt=system_prompt,
        max_tokens=max_tokens,
    )

    # Build user content
    content = []

    if images:
        for img_path in images:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")

                ext = img_path.rsplit(".", 1)[-1].lower()
                media_type = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "gif": "image/gif",
                    "webp": "image/webp",
                }.get(ext, "image/png")

                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_data,
                        },
                    }
                )

    content.append({"type": "text", "text": user_prompt})

    agent.add_user_message(content)
    response_blocks, _, _ = await agent.call()
    return Agent.extract_text(response_blocks)


# ─── Parsing utilities (unchanged) ──────────────────────────────


def extract_json(text: str) -> dict | list:
    """Extract JSON from LLM response (handles markdown code blocks, objects, and arrays)."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        block = text.split("```")[1].split("```")[0]
        stripped = block.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            text = block

    text = text.strip()

    # Try array first (e.g. [{...}, {...}])
    if text.lstrip().startswith("["):
        arr_start = text.find("[")
        depth = 0
        for i in range(arr_start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    return json.loads(text[arr_start : i + 1])

    # Then try object
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON found in response: {text[:200]}")

    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])

    raise ValueError(f"Unbalanced JSON in response: {text[:200]}")


def extract_code(text: str) -> str:
    """Extract Python code from LLM response."""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        block = text.split("```")[1].split("```")[0].strip()
        if "from manim" in block or "import" in block:
            return block

    if "from manim" in text or "class " in text:
        return text.strip()

    raise ValueError(f"No Python code found in response: {text[:200]}")
