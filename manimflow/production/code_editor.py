"""Surgical code editor — fixes Manim code with targeted edits instead of full rewrites.

Instead of asking the LLM to rewrite 200 lines from scratch (which re-introduces bugs),
this gives the LLM a tool-like interface: read specific lines, search, replace sections.

The LLM receives the code with line numbers and can specify exact edits.
"""

import json
from ..core.agent import Agent
from ..knowledge.tool import get_knowledge_system_context


EDITOR_SYSTEM_PROMPT = r"""You are a Manim code editor. You fix bugs by making SURGICAL EDITS — not by rewriting the entire file.

You will receive:
1. The current Manim code (with line numbers)
2. A description of what's wrong

You must return a JSON array of edits. Each edit is one of:
- REPLACE: Replace specific lines with new content
- INSERT: Insert new lines after a specific line
- DELETE: Delete specific lines

Format:
```json
[
  {"action": "replace", "start_line": 45, "end_line": 47, "new_content": "    self.play(FadeOut(title), run_time=1)\n    self.wait(1)"},
  {"action": "insert", "after_line": 30, "new_content": "    self.play(FadeOut(text1), FadeOut(text2), run_time=1)"},
  {"action": "delete", "start_line": 12, "end_line": 12}
]
```

RULES:
1. Make the MINIMUM number of edits needed to fix the issue
2. NEVER rewrite large sections — fix only what's broken
3. Preserve indentation (use 4 spaces for method body, 8 for nested)
4. When adding FadeOut, target specific named objects — don't use self.mobjects
5. Keep line numbers relative to the ORIGINAL code
6. Return ONLY the JSON array — no explanation

COMMON FIXES:
- Missing FadeOut: Insert `self.play(FadeOut(obj1), FadeOut(obj2), run_time=1)` before next scene
- Text overlap: Change .move_to() position — spread vertically by 1.0+ units
- Off-screen: Move positions closer to center (y between -3 and 3)
- Rate func error: Replace ease_in_cubic etc with smooth
- Empty screen: Insert content creation right after FadeOut sequence
"""


async def surgical_fix(code: str, issues: str) -> str:
    """Fix code with targeted edits instead of full rewrite."""
    # Number the lines for the LLM
    lines = code.split("\n")
    numbered = "\n".join(f"{i + 1:4d} | {line}" for i, line in enumerate(lines))

    user_prompt = (
        f"Fix this Manim code. Make SURGICAL EDITS only — do NOT rewrite the file.\n\n"
        f"CODE:\n{numbered}\n\n"
        f"ISSUES:\n{issues}\n\n"
        f"Return ONLY a JSON array of edits."
    )

    system = EDITOR_SYSTEM_PROMPT + "\n\n" + get_knowledge_system_context()
    agent = Agent(system_prompt=system)
    agent.add_user_message(user_prompt)
    content, _, _ = await agent.call()
    response = Agent.extract_text(content)

    # Parse the edit instructions
    edits = _parse_edits(response)
    if not edits:
        return code  # No valid edits — return original

    # Apply edits in reverse order (so line numbers stay valid)
    return _apply_edits(lines, edits)


def _parse_edits(response: str) -> list[dict]:
    """Parse edit instructions from LLM response."""
    # Extract JSON array
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0]
    elif "```" in response:
        response = response.split("```")[1].split("```")[0]

    # Find JSON array
    start = response.find("[")
    if start == -1:
        return []

    depth = 0
    for i in range(start, len(response)):
        if response[i] == "[":
            depth += 1
        elif response[i] == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(response[start : i + 1])
                except json.JSONDecodeError:
                    return []
    return []


def _apply_edits(lines: list[str], edits: list[dict]) -> str:
    """Apply edits to lines, processing in reverse order to preserve line numbers."""

    # Sort edits by line number, descending (so we apply from bottom to top)
    def edit_line(e):
        if e["action"] == "insert":
            return e.get("after_line", 0)
        return e.get("start_line", 0)

    edits.sort(key=edit_line, reverse=True)

    for edit in edits:
        action = edit.get("action", "")
        try:
            if action == "replace":
                start = edit["start_line"] - 1  # Convert to 0-indexed
                end = edit["end_line"]  # end_line is inclusive
                new_lines = edit["new_content"].split("\n")
                lines[start:end] = new_lines

            elif action == "insert":
                after = edit["after_line"]  # Insert after this line
                new_lines = edit["new_content"].split("\n")
                for j, new_line in enumerate(new_lines):
                    lines.insert(after + j, new_line)

            elif action == "delete":
                start = edit["start_line"] - 1
                end = edit["end_line"]
                del lines[start:end]

        except (KeyError, IndexError):
            continue  # Skip malformed edits

    return "\n".join(lines)
