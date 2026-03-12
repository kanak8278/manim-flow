"""LLM backend - uses Claude CLI (already authenticated) or Anthropic API."""

import subprocess
import json
import os


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 8192) -> str:
    """Call Claude via the best available method."""
    # Try Anthropic API first (if key is set)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _call_api(system_prompt, user_prompt, max_tokens)

    # Fall back to Claude CLI (unset CLAUDECODE to allow nested calls)
    return _call_cli(system_prompt, user_prompt)


def _call_api(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """Call via Anthropic API."""
    import anthropic

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_cli(system_prompt: str, user_prompt: str) -> str:
    """Call via Claude CLI (claude --print)."""
    full_prompt = f"{system_prompt}\n\n---\n\nUSER REQUEST:\n{user_prompt}"

    # Remove CLAUDECODE env var to allow running from within Claude Code sessions
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    result = subprocess.run(
        ["claude", "--print", "--model", "sonnet", full_prompt],
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed: {result.stderr}")

    return result.stdout.strip()


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response (handles markdown code blocks)."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        block = text.split("```")[1].split("```")[0]
        if block.strip().startswith("{"):
            text = block

    text = text.strip()

    # Try to find JSON object in the text
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON found in response: {text[:200]}")

    # Find matching closing brace
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

    # If no code blocks, assume the whole thing is code
    if "from manim" in text or "class " in text:
        return text.strip()

    raise ValueError(f"No Python code found in response: {text[:200]}")
