"""Wireframe — two tools for pre-render validation.

1. Static frame renderer: render quick wireframe PNGs from Manim code (no animation).
   Useful for human inspection or vision LLM review before committing to full render.

2. Screenplay structural validator: check completeness and consistency of screenplay data.
   NOT geometric — doesn't check overlaps (spatial_analyzer does that on code).
   Checks: element completeness, persist/cleanup consistency, transform targets, shot structure.
"""

import os
from dataclasses import dataclass, field


# ─── PART 1: SCREENPLAY STRUCTURAL VALIDATION ───

@dataclass
class StructuralIssue:
    """A structural problem in the screenplay."""
    shot_id: int
    severity: str  # "error", "warning"
    issue_type: str
    description: str


def _validate_single_anim(anim: dict, shot_id: int, known_names: set, issues: list):
    """Validate a single animation action (transform, move_to, etc.)."""
    action = anim.get("action", "")
    target = anim.get("target", "")

    if action == "transform":
        to_elem = anim.get("to_element")
        if not to_elem:
            issues.append(StructuralIssue(
                shot_id, "warning", "transform_no_target",
                f"Transform of '{target}' doesn't specify 'to_element'"))
        elif isinstance(to_elem, dict):
            new_name = to_elem.get("name", "")
            if new_name:
                known_names.add(new_name)
            if not to_elem.get("type"):
                issues.append(StructuralIssue(
                    shot_id, "warning", "transform_incomplete",
                    f"Transform to_element for '{target}' missing 'type'"))

    elif action == "move_to":
        has_end = bool(
            anim.get("end_position")
            or anim.get("end_position_on")
            or anim.get("end_value") is not None
        )
        if not has_end:
            issues.append(StructuralIssue(
                shot_id, "warning", "move_no_end",
                f"move_to for '{target}' doesn't specify end position"))
        # Validate end_position_on references a known element
        end_on = anim.get("end_position_on", "")
        if end_on and end_on not in known_names:
            issues.append(StructuralIssue(
                shot_id, "error", "move_to_unknown_ref",
                f"move_to for '{target}' references '{end_on}' which doesn't exist"))


def validate_screenplay(screenplay_data: dict) -> dict:
    """Validate screenplay structure for completeness and consistency.

    NOT geometric — doesn't check overlaps or positions.
    Checks that the screenplay is well-formed and implementable.

    Args:
        screenplay_data: Full screenplay dict with "shots" list

    Returns:
        Dict with pass/fail, issues list, and summary stats
    """
    issues = []
    shots = screenplay_data.get("shots", [])

    if not shots:
        issues.append(StructuralIssue(0, "error", "empty", "No shots in screenplay"))
        return _build_result(issues)

    all_element_names = set()
    all_persisted = set()  # elements currently persisted from previous shots

    for shot in shots:
        shot_id = shot.get("id", 0)

        # ── Narration ──
        narration = shot.get("narration", "")
        if not narration:
            issues.append(StructuralIssue(
                shot_id, "error", "missing_narration",
                "Shot has no narration text"))
        elif len(narration) < 10:
            issues.append(StructuralIssue(
                shot_id, "warning", "short_narration",
                f"Narration very short ({len(narration)} chars)"))

        # ── Bookmark consistency ──
        # Find bookmarks defined in narration
        import re
        narration_bookmarks = set(re.findall(r"<bookmark\s+mark=['\"](\w+)['\"]", narration))
        # Find bookmarks referenced in animation_sequence
        sequence = shot.get("animation_sequence", [])
        used_bookmarks = {a.get("mark", "") for a in sequence if a.get("action") == "wait_bookmark"}
        used_bookmarks.discard("")

        undefined_bookmarks = used_bookmarks - narration_bookmarks
        unused_bookmarks = narration_bookmarks - used_bookmarks - {"start"}  # 'start' often unused

        for bm in undefined_bookmarks:
            issues.append(StructuralIssue(
                shot_id, "error", "undefined_bookmark",
                f"Animation references bookmark '{bm}' not defined in narration"))
        for bm in unused_bookmarks:
            issues.append(StructuralIssue(
                shot_id, "warning", "unused_bookmark",
                f"Narration defines bookmark '{bm}' but no animation waits for it"))

        # ── Elements ──
        elements = shot.get("elements", [])
        if not elements and not all_persisted:
            issues.append(StructuralIssue(
                shot_id, "warning", "no_elements",
                "Shot has no elements and nothing persisted from previous shot"))

        shot_element_names = set()
        for elem in elements:
            name = elem.get("name", "")
            etype = elem.get("type", "")

            if not name:
                issues.append(StructuralIssue(
                    shot_id, "error", "unnamed_element",
                    f"Element missing 'name' field (type={etype})"))
                continue

            if not etype:
                issues.append(StructuralIssue(
                    shot_id, "error", "untyped_element",
                    f"Element '{name}' missing 'type' field"))

            if name in all_element_names:
                issues.append(StructuralIssue(
                    shot_id, "warning", "duplicate_name",
                    f"Element name '{name}' already used in a previous shot"))

            # Check positioning: must have at least one positioning method
            has_position = bool(elem.get("position"))
            has_position_on = bool(elem.get("position_on"))
            has_relative = bool(elem.get("position_relative_to"))
            has_inside = bool(elem.get("inside"))
            has_from_to = bool(elem.get("from_element") or elem.get("from_pos"))

            if not any([has_position, has_position_on, has_relative, has_inside, has_from_to]):
                if etype not in ("vgroup",):  # vgroups don't need explicit position
                    issues.append(StructuralIssue(
                        shot_id, "warning", "no_position",
                        f"Element '{name}' has no positioning specified"))

            # Check semantic position validity
            if has_position:
                valid_positions = {
                    "top_left", "top_center", "top_right",
                    "center_left", "center", "center_right",
                    "bottom_left", "bottom_center", "bottom_right",
                    "above_center", "below_center", "same",
                }
                pos = elem.get("position", "")
                if pos and pos not in valid_positions:
                    issues.append(StructuralIssue(
                        shot_id, "warning", "invalid_position",
                        f"Element '{name}' position '{pos}' is not a valid semantic region "
                        f"(use absolute coordinates like UP * 2 in codegen, not screenplay)"))

            # Check position_on references an element in this shot
            if has_position_on:
                ref = elem.get("position_on", "")
                if ref and ref not in known_names and ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "error", "position_on_unknown",
                        f"Element '{name}' positioned on '{ref}' which doesn't exist"))
                if elem.get("value") is None:
                    issues.append(StructuralIssue(
                        shot_id, "warning", "position_on_no_value",
                        f"Element '{name}' positioned on '{ref}' but no value specified"))

            # Check relative position references
            if has_relative:
                ref = elem.get("position_relative_to", "")
                if ref and ref not in known_names and ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "error", "relative_to_unknown",
                        f"Element '{name}' relative to '{ref}' which doesn't exist"))

            # Check overlap declarations reference real elements
            for overlap_ref in elem.get("overlaps_with", []):
                if overlap_ref not in known_names and overlap_ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "warning", "overlap_unknown",
                        f"Element '{name}' declares overlap with '{overlap_ref}' which doesn't exist"))

            shot_element_names.add(name)
            all_element_names.add(name)

        # ── Animation sequence ──
        if not sequence:
            issues.append(StructuralIssue(
                shot_id, "warning", "no_animations",
                "Shot has no animation_sequence"))

        known_names = shot_element_names | all_persisted
        for i, anim in enumerate(sequence):
            action = anim.get("action", "")
            target = anim.get("target", "")

            if not action:
                issues.append(StructuralIssue(
                    shot_id, "error", "no_action",
                    f"Animation {i} has no 'action' field"))
                continue

            # Skip non-targeted actions
            if action in ("wait", "wait_bookmark"):
                continue

            if action == "simultaneous":
                sub_anims = anim.get("animations", [])
                if not sub_anims:
                    issues.append(StructuralIssue(
                        shot_id, "error", "empty_simultaneous",
                        f"Simultaneous group at position {i} has no animations"))
                else:
                    # Validate each sub-animation
                    for j, sub in enumerate(sub_anims):
                        sub_target = sub.get("target", "")
                        sub_action = sub.get("action", "")
                        if sub_target and sub_target not in known_names:
                            issues.append(StructuralIssue(
                                shot_id, "error", "unknown_target",
                                f"Simultaneous animation targets '{sub_target}' which doesn't exist"))
                        # Check transform/move_to inside simultaneous
                        _validate_single_anim(sub, shot_id, known_names, issues)
                continue

            if target and target not in known_names:
                issues.append(StructuralIssue(
                    shot_id, "error", "unknown_target",
                    f"Animation targets '{target}' which doesn't exist in this shot"))

            _validate_single_anim(anim, shot_id, known_names, issues)

        # ── Cleanup / Persists consistency ──
        cleanup = set(shot.get("cleanup", []))
        persists = set(shot.get("persists", []))

        # Elements that are neither cleaned up nor persisted
        visible_at_end = shot_element_names | all_persisted
        accounted = cleanup | persists
        unaccounted = visible_at_end - accounted

        # Elements created by transforms during animation
        for anim in sequence:
            if anim.get("action") == "transform":
                to_elem = anim.get("to_element")
                if isinstance(to_elem, dict) and to_elem.get("name"):
                    visible_at_end.add(to_elem["name"])

        unaccounted = visible_at_end - accounted
        for name in unaccounted:
            issues.append(StructuralIssue(
                shot_id, "warning", "unaccounted_element",
                f"Element '{name}' not in cleanup or persists — will it stay on screen?"))

        # Cleaning up something that's not visible
        for name in cleanup:
            if name not in visible_at_end:
                issues.append(StructuralIssue(
                    shot_id, "warning", "cleanup_invisible",
                    f"Cleanup references '{name}' which isn't visible in this shot"))

        # Update persisted set for next shot
        all_persisted = persists

    # ── Global checks ──

    # Element count stats
    total_elements = len(all_element_names)
    if total_elements == 0:
        issues.append(StructuralIssue(0, "error", "no_elements_total", "Screenplay has no elements at all"))
    elif total_elements < len(shots):
        issues.append(StructuralIssue(0, "warning", "few_elements",
                                      f"Only {total_elements} elements across {len(shots)} shots — visually sparse"))

    return _build_result(issues, len(shots), total_elements)


def _build_result(issues: list[StructuralIssue], shot_count: int = 0, element_count: int = 0) -> dict:
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    return {
        "valid": len(errors) == 0,
        "errors": len(errors),
        "warnings": len(warnings),
        "issues": issues,
        "shot_count": shot_count,
        "element_count": element_count,
    }


def print_validation(result: dict):
    """Pretty-print screenplay validation results."""
    print(f"\n--- Screenplay Validation ---")
    print(f"  Valid: {result['valid']} ({result['shot_count']} shots, {result['element_count']} elements)")
    print(f"  Errors: {result['errors']}, Warnings: {result['warnings']}")

    for issue in result["issues"]:
        prefix = "[ERROR]" if issue.severity == "error" else "[WARN]"
        shot = f"Shot {issue.shot_id}" if issue.shot_id else "Global"
        print(f"  {prefix} {shot}: {issue.description}")


# ─── PART 2: STATIC WIREFRAME RENDERER (from Manim code) ───

def render_wireframes_from_code(code: str, output_dir: str) -> list[str]:
    """Render static wireframe PNGs from Manim code — one per scene section.

    Parses the code to find scene boundaries (comment markers like '# Scene 1:'),
    creates a stripped-down version that adds elements without playing animations,
    and renders a single frame per section.

    Much faster than full animated render — no self.play(), no voiceover, no video encoding.

    Args:
        code: Manim Python code (GeneratedScene)
        output_dir: Directory to save wireframe PNGs

    Returns:
        List of PNG file paths
    """
    try:
        from manim import Scene, config
    except ImportError:
        print("  [wireframe] Manim not available, skipping wireframe render")
        return []

    os.makedirs(output_dir, exist_ok=True)

    # Build a wireframe version of the code:
    # - Replace self.play(...) with self.add(element) where possible
    # - Remove self.wait() calls
    # - Remove voiceover blocks
    # - Keep element creation and positioning
    # - Render one frame at each scene boundary

    wireframe_code = _build_wireframe_code(code)

    if not wireframe_code:
        print("  [wireframe] Could not build wireframe version of code")
        return []

    # Write wireframe code to temp file
    wireframe_path = os.path.join(output_dir, "_wireframe_scene.py")
    with open(wireframe_path, "w") as f:
        f.write(wireframe_code)

    # Render it
    import subprocess
    result = subprocess.run(
        ["uv", "run", "python", "-m", "manim", "-ql", "--format", "png",
         "--media_dir", output_dir, wireframe_path, "WireframeScene"],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        print(f"  [wireframe] Render failed: {result.stderr[-200:]}")
        return []

    # Find generated PNGs
    paths = []
    for root, dirs, files in os.walk(output_dir):
        for f in sorted(files):
            if f.endswith(".png") and "wireframe" in f.lower():
                paths.append(os.path.join(root, f))

    return paths


def _build_wireframe_code(code: str) -> str:
    """Transform animation code into static wireframe code.

    Strategy: extract all element creation statements, strip animations,
    render all elements as white outlines on black.
    """
    import re

    lines = code.split("\n")
    wireframe_lines = [
        "from manim import *",
        "",
        "class WireframeScene(Scene):",
        "    def construct(self):",
        "        self.camera.background_color = BLACK",
        "",
    ]

    # Extract make_card helper if present
    in_helper = False
    helper_lines = []
    for line in lines:
        if "def make_card" in line:
            in_helper = True
        if in_helper:
            helper_lines.append(line)
            if line.strip().startswith("return"):
                in_helper = False

    if helper_lines:
        wireframe_lines.extend(["    " + l.lstrip() if l.strip() else "" for l in helper_lines])
        wireframe_lines.append("")

    # Extract element creation and positioning — skip animations and voiceover
    for line in lines:
        stripped = line.strip()

        # Skip imports, class def, construct, voiceover, play, wait
        if any(stripped.startswith(s) for s in [
            "from manim", "import", "class ", "def construct",
            "self.play(", "self.wait", "self.set_speech",
            "with self.voiceover", "tracker.", "if self.mobjects",
        ]):
            continue

        # Skip bookmark waits
        if "wait_until_bookmark" in stripped:
            continue

        # Keep element creation (assignments with Manim constructors)
        if "=" in stripped and any(cls in stripped for cls in [
            "Text(", "RoundedRectangle(", "make_card(", "Arrow(",
            "Line(", "Circle(", "Dot(", "NumberLine(", "Axes(",
            "VGroup(", "Brace(", "Table(",
        ]):
            wireframe_lines.append(f"        {stripped}")
            # Extract variable name and add to scene
            var_name = stripped.split("=")[0].strip()
            if var_name and not var_name.startswith("#"):
                wireframe_lines.append(f"        self.add({var_name})")
            continue

        # Keep .move_to(), .next_to(), .shift() positioning
        if any(m in stripped for m in [".move_to(", ".next_to(", ".shift(", ".to_edge("]):
            wireframe_lines.append(f"        {stripped}")

    return "\n".join(wireframe_lines)
