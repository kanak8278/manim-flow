"""Design System — takes a free-form story and enriches it with complete visual specs.

Input: free-form story prose (from writers room)
Output: design rules + visual story (prose with every color, size, position, animation specified)

The design system doesn't change WHAT happens — it decides HOW everything looks.
"""

import re
from dataclasses import dataclass
from ..agent import Agent
from ..prompts.design_system import DESIGN_SYSTEM_SYSTEM


@dataclass
class DesignedStory:
    """Story with complete visual specifications."""
    title: str
    design_rules: str  # global rules (palette, typography, etc.)
    visual_story: str  # enriched prose with all visual details
    raw_response: str  # full LLM response for debugging


def _extract_xml_tag(text: str, tag: str) -> str:
    """Extract content between <tag>...</tag>."""
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


async def design_story(title: str, story_text: str) -> DesignedStory:
    """Take a free-form story and add complete visual specifications.

    Args:
        title: Video title
        story_text: Free-form story prose from writers room

    Returns:
        DesignedStory with design_rules and visual_story
    """
    agent = Agent(system_prompt=DESIGN_SYSTEM_SYSTEM)
    agent.add_user_message(
        f"TITLE: {title}\n\n"
        f"STORY:\n{story_text}\n\n"
        f"Read this story carefully. Then:\n"
        f"1. Establish global design rules (palette, color roles, typography, animation vocabulary)\n"
        f"2. Rewrite the COMPLETE story with every visual detail specified — "
        f"exact hex colors, font sizes, Manim positions, card dimensions, "
        f"animation types with run_times, transition cleanup.\n\n"
        f"Output:\n"
        f"<design_rules>...global rules...</design_rules>\n"
        f"<visual_story>...complete enriched story...</visual_story>"
    )

    content, _, _ = await agent.call()
    response_text = Agent.extract_text(content)

    design_rules = _extract_xml_tag(response_text, "design_rules")
    visual_story = _extract_xml_tag(response_text, "visual_story")

    # Fallback: if no XML tags, try to split on obvious markers
    if not visual_story:
        if "VISUAL STORY" in response_text.upper():
            parts = re.split(r"(?i)visual.?story", response_text, maxsplit=1)
            if len(parts) > 1:
                visual_story = parts[1].strip()
        else:
            # Treat everything as the visual story
            visual_story = response_text

    if not design_rules:
        if "DESIGN RULES" in response_text.upper() or "PALETTE" in response_text.upper():
            parts = re.split(r"(?i)visual.?story", response_text, maxsplit=1)
            if len(parts) > 1:
                design_rules = parts[0].strip()

    return DesignedStory(
        title=title,
        design_rules=design_rules,
        visual_story=visual_story,
        raw_response=response_text,
    )


def print_designed_story(ds: DesignedStory):
    """Pretty-print a designed story summary."""
    print(f"\n--- Design System: \"{ds.title}\" ---")
    print(f"  Design rules: {len(ds.design_rules)} chars")
    print(f"  Visual story: {len(ds.visual_story)} chars")

    # Show first few lines of design rules
    if ds.design_rules:
        for line in ds.design_rules.split("\n")[:8]:
            line = line.strip()
            if line:
                print(f"  | {line[:90]}")
