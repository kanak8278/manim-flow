"""Interactive editor — modify generated videos via text prompts.

Inspired by InVideo's "Magic Box": type a natural language edit command
and the system applies it to the existing code/story.

Examples:
  "Make scene 3 slower"
  "Add a zoom on the equation in scene 2"
  "Change the voice to female"
  "Make the hook more dramatic"
  "Add a visual metaphor for infinity"
"""

import json
import os
from .agent import call_llm, extract_code
from .code_editor import surgical_fix


async def apply_edit(
    edit_command: str,
    code: str,
    story: dict,
    output_dir: str,
) -> dict:
    """Apply a natural language edit to existing code.

    Returns dict with:
        code: modified code
        story: modified story (if applicable)
        changes: description of what changed
    """
    # Determine if this is a code edit, story edit, or both
    edit_type = _classify_edit(edit_command)

    changes = []

    if edit_type in ("code", "both"):
        new_code = await _edit_code(edit_command, code, story)
        if new_code != code:
            code = new_code
            changes.append(f"Code modified: {edit_command}")

    if edit_type in ("story", "both"):
        new_story = await _edit_story(edit_command, story)
        if new_story != story:
            story = new_story
            changes.append(f"Story modified: {edit_command}")

    return {
        "code": code,
        "story": story,
        "changes": changes,
        "edit_type": edit_type,
    }


def _classify_edit(command: str) -> str:
    """Classify whether an edit targets code, story, or both."""
    cmd = command.lower()

    # Code-only edits
    code_keywords = ["slower", "faster", "zoom", "color", "position", "font",
                     "animation", "transition", "fade", "scale", "rotate",
                     "wait", "pause", "timing", "move", "bigger", "smaller"]

    # Story-only edits
    story_keywords = ["hook", "narration", "voice", "script", "rewrite",
                      "tone", "audience", "explain", "simplify"]

    is_code = any(k in cmd for k in code_keywords)
    is_story = any(k in cmd for k in story_keywords)

    if is_code and is_story:
        return "both"
    elif is_story:
        return "story"
    else:
        return "code"  # Default to code edits


async def _edit_code(command: str, code: str, story: dict) -> str:
    """Apply a code edit using the surgical editor."""
    edit_prompt = (
        f"USER EDIT REQUEST: {command}\n\n"
        f"Apply this change to the Manim code. "
        f"Only modify the parts that need to change."
    )
    return await surgical_fix(code, edit_prompt)


async def _edit_story(command: str, story: dict) -> dict:
    """Apply a story edit."""
    system = (
        "You are editing an existing video story script. "
        "Apply the user's requested change while keeping everything else the same. "
        "Return the complete modified story as JSON."
    )

    user_prompt = (
        f"Current story:\n{json.dumps(story, indent=2)}\n\n"
        f"Edit request: {command}\n\n"
        f"Return the modified story as valid JSON."
    )

    response = await call_llm(system, user_prompt)

    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        start = response.find("{")
        depth = 0
        for i in range(start, len(response)):
            if response[i] == "{":
                depth += 1
            elif response[i] == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(response[start:i+1])
    except (json.JSONDecodeError, ValueError):
        pass

    return story  # Return original if edit fails
