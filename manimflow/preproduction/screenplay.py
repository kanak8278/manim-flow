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

from dataclasses import dataclass
from ..core.agent import Agent, extract_json
from ..core import tracing
from ..core.config import MAX_TOKENS_SCREENPLAY, SCREENPLAY_MAX_TOOL_ROUNDS
from ..knowledge.tool import TOOLS, get_knowledge_context_screenplay
from ..prompts.screenplay import SCREENPLAY_SYSTEM
from .screenplay_validator import validate_screenplay as _validate, StructuralIssue


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


def _parse_shots(data: dict) -> list[Shot]:
    """Parse shot dicts into Shot objects."""
    shots = []
    for s in data.get("shots", []):
        shots.append(
            Shot(
                id=s.get("id", len(shots) + 1),
                narration=s.get("narration", ""),
                elements=s.get("elements", []),
                animation_sequence=s.get("animation_sequence", []),
                cleanup=s.get("cleanup", []),
                persists=s.get("persists", []),
            )
        )
    return shots


def _shots_to_dicts(shots: list[Shot]) -> list[dict]:
    """Convert Shot objects back to dicts for validation/serialization."""
    return [
        {
            "id": s.id,
            "narration": s.narration,
            "elements": s.elements,
            "animation_sequence": s.animation_sequence,
            "cleanup": s.cleanup,
            "persists": s.persists,
        }
        for s in shots
    ]


def _format_issues_for_llm(issues: list[StructuralIssue]) -> str:
    """Format validation issues into a clear message for the LLM."""
    lines = ["The following structural issues were found in your screenplay:\n"]

    # Group by shot
    by_shot = {}
    for issue in issues:
        by_shot.setdefault(issue.shot_id, []).append(issue)

    for shot_id in sorted(by_shot.keys()):
        shot_issues = by_shot[shot_id]
        if shot_id == 0:
            lines.append("GLOBAL ISSUES:")
        else:
            lines.append(f"SHOT {shot_id}:")

        for issue in shot_issues:
            prefix = "ERROR" if issue.severity == "error" else "WARNING"
            lines.append(f"  [{prefix}] {issue.description}")

    lines.append(
        "\nFix ALL errors and as many warnings as possible. "
        "Return ONLY the corrected shots as a JSON array. "
        "Include ONLY the shots that need changes — I will patch them "
        "into the full screenplay by matching shot IDs."
    )

    return "\n".join(lines)


@tracing.observe()
async def write_screenplay(
    title: str,
    visual_story: str,
    design_rules: str,
    max_fix_rounds: int = 3,
    verbose: bool = True,
) -> Screenplay:
    """Convert visual story into structured shot specifications.

    Generates the screenplay, validates it, and fixes issues in a conversation loop.
    The same agent maintains context across rounds — no need to resend previous output.

    Args:
        title: Video title
        visual_story: Enriched prose with all visual details (from design system)
        design_rules: Global design rules text (from design system)
        max_fix_rounds: Max validation-fix rounds (default 3)
        verbose: Print progress

    Returns:
        Screenplay with structured shots using semantic positioning
    """
    _log = print if verbose else lambda *a: None
    system = SCREENPLAY_SYSTEM + "\n\n" + get_knowledge_context_screenplay()

    agent = Agent(
        system_prompt=system,
        tools=TOOLS,
        max_tokens=MAX_TOKENS_SCREENPLAY,
    )

    # ── First pass: generate full screenplay ──
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

    response = await agent.run(max_tool_rounds=SCREENPLAY_MAX_TOOL_ROUNDS)
    data = extract_json(response)
    agent.add_assistant_message(response)

    rules = data.get("design_rules", {})
    shots = _parse_shots(data)

    _log(
        f"  Screenplay: {len(shots)} shots, {sum(len(s.elements) for s in shots)} elements"
    )

    # ── Validation-fix loop ──
    for fix_round in range(max_fix_rounds):
        # Validate the full screenplay
        sp_data = {"shots": _shots_to_dicts(shots), "design_rules": rules}
        validation = _validate(sp_data)

        errors = [i for i in validation["issues"] if i.severity == "error"]
        warnings = [i for i in validation["issues"] if i.severity == "warning"]

        _log(
            f"  Validation round {fix_round + 1}: {len(errors)} errors, {len(warnings)} warnings"
        )

        if not errors:
            _log(f"  Screenplay valid (0 errors, {len(warnings)} warnings)")
            break

        # Log the issues
        for issue in errors[:5]:
            _log(f"    [ERROR] Shot {issue.shot_id}: {issue.description}")
        for issue in warnings[:3]:
            _log(f"    [WARN] Shot {issue.shot_id}: {issue.description}")

        # Send issues to the LLM for fixing (same conversation — it has full context)
        issues_text = _format_issues_for_llm(
            errors + warnings[:10]
        )  # prioritize errors
        agent.add_user_message(issues_text)

        _log(f"  Fixing {len(errors)} errors...")
        fix_response = await agent.run(max_tool_rounds=2)
        agent.add_assistant_message(fix_response)

        # Parse the corrected shots
        try:
            fix_data = extract_json(fix_response)
        except Exception as e:
            _log(f"  Could not parse fix response: {e}")
            break

        # The LLM returns: [{"id":2,...}] or {"shots":[...]} or {"id":2,...} (single shot)
        if isinstance(fix_data, list):
            fixed_shot_list = fix_data
        elif isinstance(fix_data, dict) and "shots" in fix_data:
            fixed_shot_list = fix_data["shots"]
        elif isinstance(fix_data, dict) and "id" in fix_data:
            fixed_shot_list = [fix_data]  # single shot dict
        else:
            fixed_shot_list = []

        if not fixed_shot_list:
            _log("  No corrected shots returned")
            break

        # Patch corrected shots into the full screenplay by matching shot IDs
        fixed_by_id = {}
        for s in fixed_shot_list:
            sid = s.get("id")
            if sid is not None:
                fixed_by_id[sid] = s

        patched = 0
        for i, shot in enumerate(shots):
            if shot.id in fixed_by_id:
                fixed = fixed_by_id[shot.id]
                shots[i] = Shot(
                    id=shot.id,
                    narration=fixed.get("narration", shot.narration),
                    elements=fixed.get("elements", shot.elements),
                    animation_sequence=fixed.get(
                        "animation_sequence", shot.animation_sequence
                    ),
                    cleanup=fixed.get("cleanup", shot.cleanup),
                    persists=fixed.get("persists", shot.persists),
                )
                patched += 1

        _log(f"  Patched {patched} shots")

        # Also update design_rules if the fix included them
        if isinstance(fix_data, dict) and "design_rules" in fix_data:
            rules = fix_data["design_rules"]

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
    lines.append(
        "  position_relative_to + direction → .next_to(element, DIRECTION, buff=buff)"
    )
    lines.append("  inside → .move_to(container.get_center())")
    lines.append(
        "  from_element + to_element → Arrow(elem_a.get_center(), elem_b.get_center())"
    )

    lines.append(f"\nSHOTS ({len(sp.shots)} total):")

    for shot in sp.shots:
        lines.append(f"\n--- SHOT {shot.id} ---")
        lines.append(f'Narration: "{shot.narration}"')

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
                pos_parts.append(
                    f"on {elem['position_on']} at value={elem.get('value', '?')}"
                )
            if elem.get("position_relative_to"):
                direction = elem.get("direction", "right")
                buff = elem.get("buff", 0.3)
                pos_parts.append(
                    f"next_to {elem['position_relative_to']} {direction} buff={buff}"
                )
            if elem.get("inside"):
                pos_parts.append(f"inside {elem['inside']}")
            if elem.get("from_element"):
                pos_parts.append(
                    f"from {elem['from_element']} to {elem.get('to_element', '?')}"
                )

            pos_str = ", ".join(pos_parts) if pos_parts else "no position"

            # Extra params
            extras = {
                k: v
                for k, v in elem.items()
                if k
                not in (
                    "name",
                    "type",
                    "label",
                    "position",
                    "color",
                    "position_on",
                    "value",
                    "position_relative_to",
                    "direction",
                    "buff",
                    "inside",
                    "from_element",
                    "to_element",
                    "from_value",
                    "to_value",
                    "overlaps_with",
                )
                and v
            }
            extra_str = f" {extras}" if extras else ""

            overlaps = elem.get("overlaps_with", [])
            overlap_str = f" [intentionally overlaps: {overlaps}]" if overlaps else ""

            lines.append(
                f'  {name}: {etype} "{label}" {pos_str} color={color}{extra_str}{overlap_str}'
            )

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
        return f'{prefix}wait_bookmark("{anim.get("mark", "?")}")'

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
            to_desc = f'→ {to_elem.get("name", "?")} ({to_elem.get("type", "?")} "{to_elem.get("label", "")}")'
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
    print(f'\n--- Screenplay: "{sp.title}" ({len(sp.shots)} shots) ---')

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
        print(f'    Narration: "{narration_preview}..."')

        for e in shot.elements[:4]:
            pos_desc = _describe_position(e)
            print(
                f'    {e.get("name")}: {e.get("type")} "{e.get("label", "")[:25]}" {pos_desc}'
            )

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
