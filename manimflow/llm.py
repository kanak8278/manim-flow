"""LLM backend - uses Claude CLI (already authenticated) or Anthropic API."""

import subprocess
import json
import os


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 8192,
             images: list[str] | None = None) -> str:
    """Call Claude via the best available method.

    Args:
        system_prompt: System prompt
        user_prompt: User prompt text
        max_tokens: Max response tokens
        images: Optional list of image file paths to include (for vision)
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _call_api(system_prompt, user_prompt, max_tokens, images)

    # Fall back to Claude CLI (no vision support)
    return _call_cli(system_prompt, user_prompt)


def _call_api(system_prompt: str, user_prompt: str, max_tokens: int,
              images: list[str] | None = None) -> str:
    """Call via Anthropic API with optional vision."""
    import anthropic
    import base64

    client = anthropic.Anthropic()

    # Build content blocks
    content = []

    # Add images first if provided
    if images:
        for img_path in images:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    img_data = base64.standard_b64encode(f.read()).decode("utf-8")

                ext = img_path.rsplit(".", 1)[-1].lower()
                media_type = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "gif": "image/gif",
                    "webp": "image/webp",
                }.get(ext, "image/png")

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data,
                    },
                })

    # Add text prompt
    content.append({"type": "text", "text": user_prompt})

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
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
