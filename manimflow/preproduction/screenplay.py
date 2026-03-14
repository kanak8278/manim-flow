"""Screenplay — converts visual story prose into structured shot specifications.

Input: visual story (prose with design specs) + design rules
Output: structured JSON with shots, elements (semantic positions), animations, bookmarks

Uses semantic positioning (not absolute coordinates):
  - position: "center", "top_left", etc. for standalone elements
  - position_on: "number_line_1", value: 0.9 for elements on other elements
  - position_relative_to: "card_a", direction: "right" for labels/annotations
  - from_element / to_element for arrows
  - inside: "container" for contained elements
  - overlaps_with: ["circle_1"] for intentional overlaps

The code generator resolves semantic positions to actual Manim coordinates.

Uses the knowledge base to find real examples of how specific visual techniques
were implemented in production Manim videos.
"""

import json
import re
from dataclasses import dataclass, field
from ..agent import Agent, extract_json
from ..knowledge.tool import TOOLS, get_knowledge_context_screenplay
from ..prompts.screenplay import SCREENPLAY_SYSTEM


@dataclass
class Shot:
    """One shot in the screenplay."""
    id: int
    narration: str  # with <bookmark> tags
    elements: list[dict]  # semantic positioning, typed elements
    animation_sequence: list[dict]  # actions including simultaneous groups
    cleanup: list[str]  # element names to FadeOut at end
    persists: list[str]  # element names that carry to next shot


@dataclass
class Screenplay:
    """Complete structured screenplay."""
    title: str
    design_rules: dict  # palette, color_roles, typography, animation vocab
    shots: list[Shot]


async def write_screenplay(
    title: str,
    visual_story: str,
    design_rules: str,
) -> Screenplay:
    """Convert visual story into structured shot specifications.

    Args:
        title: Video title
        visual_story: Enriched prose with all visual details (from design system)
        design_rules: Global design rules text (from design system)

    Returns:
        Screenplay with structured shots using semantic positioning
    """
    system = SCREENPLAY_SYSTEM + "\n\n" + get_knowledge_context_screenplay()

    agent = Agent(
        system_prompt=system,
        tools=TOOLS,
        enable_thinking=True,
    )

    agent.add_user_message(
        f"TITLE: {title}\n\n"
        f"DESIGN RULES:\n{design_rules}\n\n"
        f"VISUAL STORY:\n{visual_story}\n\n"
        f"EXTRACT the visual specifications from the story into structured shots.\n"
        f"The story describes everything — your job is to structure it precisely.\n\n"
        f"Use SEMANTIC positions (center, top_left, position_on, position_relative_to) "
        f"— NOT absolute coordinates like UP * 2 or LEFT * 3.\n\n"
        f"Every transform MUST have a to_element with full spec.\n"
        f"Every move_to MUST have an end position.\n"
        f"Every intentional overlap MUST be declared with overlaps_with.\n\n"
        f"Use the search_knowledge tool to find real examples of how specific "
        f"techniques were implemented.\n\n"
        f"Return ONLY valid JSON."
    )

    response = await agent.run(max_tool_rounds=6)
    data = extract_json(response)

    # Parse design rules from response
    rules = data.get("design_rules", {})

    # Parse shots
    shots = []
    for s in data.get("shots", []):
        shots.append(Shot(
            id=s.get("id", len(shots) + 1),
            narration=s.get("narration", ""),
            elements=s.get("elements", []),
            animation_sequence=s.get("animation_sequence", []),
            cleanup=s.get("cleanup", []),
            persists=s.get("persists", []),
        ))

    return Screenplay(
        title=title,
        design_rules=rules,
        shots=shots,
    )


# ─── CODEGEN CONTEXT ───

# Mapping from semantic positions to Manim code hints
POSITION_HINTS = {
    "top_left": "UP * 2.5 + LEFT * 4",
    "top_center": "UP * 2.5",
    "top_right": "UP * 2.5 + RIGHT * 4",
    "center_left": "LEFT * 4",
    "center": "ORIGIN",
    "center_right": "RIGHT * 4",
    "bottom_left": "DOWN * 2.5 + LEFT * 4",
    "bottom_center": "DOWN * 2.5",
    "bottom_right": "DOWN * 2.5 + RIGHT * 4",
    "above_center": "UP * 1.5",
    "below_center": "DOWN * 1.5",
}


def screenplay_to_codegen_context(sp: Screenplay) -> str:
    """Convert a screenplay into a detailed prompt for the code generator.

    Translates semantic positions into Manim code hints so codegen
    knows how to resolve them.
    """
    lines = [
        "## SCREENPLAY (implement EXACTLY as specified)\n",
        f"Title: {sp.title}",
    ]

    # Design rules
    if sp.design_rules:
        lines.append("\nDESIGN RULES:")
        rules = sp.design_rules
        if isinstance(rules, dict):
            for key, val in rules.items():
                lines.append(f"  {key}: {val}")

    # Position resolution guide
    lines.append("\nPOSITION RESOLUTION:")
    lines.append("  Semantic positions → Manim code:")
    for name, code in POSITION_HINTS.items():
        lines.append(f"    {name} → .move_to({code})")
    lines.append("  position_on + value → .move_to(element.number_to_point(value))")
    lines.append("  position_relative_to + direction → .next_to(element, DIRECTION, buff=buff)")
    lines.append("  inside → .move_to(container.get_center())")
    lines.append("  from_element + to_element → Arrow(elem_a.get_center(), elem_b.get_center())")

    lines.append(f"\nSHOTS ({len(sp.shots)} total):")

    for shot in sp.shots:
        lines.append(f"\n--- SHOT {shot.id} ---")
        lines.append(f"Narration: \"{shot.narration}\"")

        lines.append("Elements:")
        for elem in shot.elements:
            name = elem.get("name", "?")
            etype = elem.get("type", "?")
            label = elem.get("label", "")
            color = elem.get("color", "")

            # Build position description
            pos_parts = []
            if elem.get("position"):
                pos = elem["position"]
                hint = POSITION_HINTS.get(pos, pos)
                pos_parts.append(f"at {pos} → .move_to({hint})")
            if elem.get("position_on"):
                pos_parts.append(f"on {elem['position_on']} at value={elem.get('value', '?')}")
            if elem.get("position_relative_to"):
                direction = elem.get("direction", "right")
                buff = elem.get("buff", 0.3)
                pos_parts.append(f"next_to {elem['position_relative_to']} {direction} buff={buff}")
            if elem.get("inside"):
                pos_parts.append(f"inside {elem['inside']}")
            if elem.get("from_element"):
                pos_parts.append(f"from {elem['from_element']} to {elem.get('to_element', '?')}")

            pos_str = ", ".join(pos_parts) if pos_parts else "no position"

            # Extra params
            extras = {k: v for k, v in elem.items()
                      if k not in ("name", "type", "label", "position", "color",
                                   "position_on", "value", "position_relative_to",
                                   "direction", "buff", "inside", "from_element",
                                   "to_element", "from_value", "to_value",
                                   "overlaps_with") and v}
            extra_str = f" {extras}" if extras else ""

            overlaps = elem.get("overlaps_with", [])
            overlap_str = f" [intentionally overlaps: {overlaps}]" if overlaps else ""

            lines.append(f"  {name}: {etype} \"{label}\" {pos_str} color={color}{extra_str}{overlap_str}")

        lines.append("Animation Sequence:")
        for anim in shot.animation_sequence:
            lines.append(f"  {_format_animation(anim)}")

        if shot.cleanup:
            lines.append(f"Cleanup: FadeOut({', '.join(shot.cleanup)})")
        if shot.persists:
            lines.append(f"Persists: {', '.join(shot.persists)}")

    return "\n".join(lines)


def _format_animation(anim: dict, indent: int = 0) -> str:
    """Format a single animation action for the codegen context."""
    prefix = "  " * indent
    action = anim.get("action", "?")

    if action == "wait_bookmark":
        return f"{prefix}wait_bookmark(\"{anim.get('mark', '?')}\")"

    if action == "wait":
        return f"{prefix}wait({anim.get('duration', '?')}s)"

    if action == "simultaneous":
        sub_lines = [f"{prefix}SIMULTANEOUS:"]
        for sub in anim.get("animations", []):
            sub_lines.append(f"  {_format_animation(sub, indent + 1)}")
        return "\n".join(sub_lines)

    if action == "transform":
        to_elem = anim.get("to_element", {})
        if isinstance(to_elem, dict):
            to_desc = f"→ {to_elem.get('name', '?')} ({to_elem.get('type', '?')} \"{to_elem.get('label', '')}\")"
        else:
            to_desc = f"→ {to_elem}"
        return f"{prefix}transform({anim.get('target', '?')} {to_desc}, run_time={anim.get('run_time', '?')})"

    if action == "move_to":
        end = ""
        if anim.get("end_position"):
            end = f"→ {anim['end_position']}"
        elif anim.get("end_position_on"):
            end = f"→ {anim['end_position_on']} value={anim.get('end_value', '?')}"
        return f"{prefix}move_to({anim.get('target', '?')} {end}, run_time={anim.get('run_time', '?')})"

    target = anim.get("target", "")
    rt = anim.get("run_time", "")
    return f"{prefix}{action}({target}, run_time={rt})"


def print_screenplay(sp: Screenplay):
    """Pretty-print a screenplay summary."""
    print(f"\n--- Screenplay: \"{sp.title}\" ({len(sp.shots)} shots) ---")

    if sp.design_rules:
        palette = sp.design_rules.get("palette", {})
        roles = sp.design_rules.get("color_roles", {})
        if palette:
            print(f"  Palette: {palette}")
        if roles:
            print(f"  Roles: {roles}")

    total_elements = 0
    total_anims = 0

    for shot in sp.shots:
        narration_preview = shot.narration[:60].replace("<bookmark", "[bm")
        elem_count = len(shot.elements)
        anim_count = _count_animations(shot.animation_sequence)
        total_elements += elem_count
        total_anims += anim_count

        print(f"\n  Shot {shot.id}: {elem_count} elements, {anim_count} anims")
        print(f"    Narration: \"{narration_preview}...\"")

        for e in shot.elements[:4]:
            pos_desc = _describe_position(e)
            print(f"    {e.get('name')}: {e.get('type')} \"{e.get('label', '')[:25]}\" {pos_desc}")

        if elem_count > 4:
            print(f"    ... and {elem_count - 4} more elements")

        if shot.cleanup:
            print(f"    Cleanup: {shot.cleanup[:5]}")
        if shot.persists:
            print(f"    Persists: {shot.persists[:5]}")

    print(f"\n  Total: {total_elements} elements, {total_anims} animations")


def _describe_position(elem: dict) -> str:
    """Short human-readable position description."""
    if elem.get("position_on"):
        return f"on {elem['position_on']}={elem.get('value', '?')}"
    if elem.get("position_relative_to"):
        return f"{elem.get('direction', 'near')} {elem['position_relative_to']}"
    if elem.get("inside"):
        return f"inside {elem['inside']}"
    if elem.get("from_element"):
        return f"from {elem['from_element']} → {elem.get('to_element', '?')}"
    if elem.get("position"):
        return f"at {elem['position']}"
    return ""


def _count_animations(sequence: list[dict]) -> int:
    """Count total animations including inside simultaneous groups."""
    count = 0
    for anim in sequence:
        if anim.get("action") == "simultaneous":
            count += len(anim.get("animations", []))
        else:
            count += 1
    return count
