"""Screenplay structural validator — checks completeness and consistency.

Runs AFTER screenplay generation, BEFORE codegen.

Validates:
- Element completeness: every element has name, type, and positioning
- Semantic position refs: position_on, position_relative_to reference real elements
- Bookmark consistency: animation bookmarks match narration bookmarks
- Transform specs: every transform has a full to_element definition
- Move targets: every move_to has an end position
- Cleanup tracking: every element is in cleanup or persists
- Overlap declarations: overlaps_with references real elements
- Simultaneous groups: not empty, sub-animations reference real targets

NOT geometric — doesn't check overlaps or bounding boxes.
Spatial_analyzer does that on the resolved code.
"""

import re
from dataclasses import dataclass


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
            if not to_elem.get("label") and to_elem.get("type") in ("card", "text"):
                issues.append(StructuralIssue(
                    shot_id, "warning", "transform_no_label",
                    f"Transform to_element for '{target}' is a {to_elem['type']} with no label"))

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

    Args:
        screenplay_data: Full screenplay dict with "shots" list

    Returns:
        Dict with valid (bool), errors (int), warnings (int), issues list, stats
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
        narration_bookmarks = set(re.findall(r"<bookmark\s+mark=['\"](\w+)['\"]", narration))
        sequence = shot.get("animation_sequence", [])

        # Collect bookmarks from top-level and inside simultaneous groups
        used_bookmarks = set()
        for a in sequence:
            if a.get("action") == "wait_bookmark":
                used_bookmarks.add(a.get("mark", ""))
            if a.get("action") == "simultaneous":
                for sub in a.get("animations", []):
                    if sub.get("action") == "wait_bookmark":
                        used_bookmarks.add(sub.get("mark", ""))
        used_bookmarks.discard("")

        for bm in used_bookmarks - narration_bookmarks:
            issues.append(StructuralIssue(
                shot_id, "error", "undefined_bookmark",
                f"Animation references bookmark '{bm}' not defined in narration"))
        for bm in narration_bookmarks - used_bookmarks - {"start"}:
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
        known_names = all_persisted.copy()

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

            # ── Positioning ──
            has_position = bool(elem.get("position"))
            has_position_on = bool(elem.get("position_on"))
            has_relative = bool(elem.get("position_relative_to"))
            has_inside = bool(elem.get("inside"))
            has_from_to = bool(elem.get("from_element") or elem.get("from_pos"))

            if not any([has_position, has_position_on, has_relative, has_inside, has_from_to]):
                if etype not in ("vgroup",):
                    issues.append(StructuralIssue(
                        shot_id, "warning", "no_position",
                        f"Element '{name}' has no positioning specified"))

            # Validate semantic position
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
                        f"Element '{name}' has non-semantic position '{pos}'"))

            # Validate position_on reference
            if has_position_on:
                ref = elem.get("position_on", "")
                if ref not in known_names and ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "error", "position_on_unknown",
                        f"Element '{name}' positioned on '{ref}' which doesn't exist"))
                if elem.get("value") is None:
                    issues.append(StructuralIssue(
                        shot_id, "warning", "position_on_no_value",
                        f"Element '{name}' positioned on '{ref}' but no value specified"))

            # Validate relative position reference
            if has_relative:
                ref = elem.get("position_relative_to", "")
                if ref not in known_names and ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "error", "relative_to_unknown",
                        f"Element '{name}' relative to '{ref}' which doesn't exist"))

            # Validate inside reference
            if has_inside:
                ref = elem.get("inside", "")
                if ref not in known_names and ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "error", "inside_unknown",
                        f"Element '{name}' inside '{ref}' which doesn't exist"))

            # Validate from/to element references (arrows)
            if has_from_to:
                for ref_field in ("from_element", "to_element"):
                    ref = elem.get(ref_field, "")
                    if ref and ref not in known_names and ref not in shot_element_names:
                        issues.append(StructuralIssue(
                            shot_id, "error", "endpoint_unknown",
                            f"Element '{name}' {ref_field}='{ref}' which doesn't exist"))

            # Validate overlap declarations
            for overlap_ref in elem.get("overlaps_with", []):
                if overlap_ref not in known_names and overlap_ref not in shot_element_names:
                    issues.append(StructuralIssue(
                        shot_id, "warning", "overlap_unknown",
                        f"Element '{name}' declares overlap with '{overlap_ref}' which doesn't exist"))

            shot_element_names.add(name)
            all_element_names.add(name)

        known_names |= shot_element_names

        # ── Animation sequence ──
        if not sequence:
            issues.append(StructuralIssue(
                shot_id, "warning", "no_animations",
                "Shot has no animation_sequence"))

        for i, anim in enumerate(sequence):
            action = anim.get("action", "")
            target = anim.get("target", "")

            if not action:
                issues.append(StructuralIssue(
                    shot_id, "error", "no_action",
                    f"Animation {i} has no 'action' field"))
                continue

            if action in ("wait", "wait_bookmark"):
                continue

            if action == "simultaneous":
                sub_anims = anim.get("animations", [])
                if not sub_anims:
                    issues.append(StructuralIssue(
                        shot_id, "error", "empty_simultaneous",
                        f"Simultaneous group at position {i} has no animations"))
                else:
                    for sub in sub_anims:
                        sub_target = sub.get("target", "")
                        if sub_target and sub_target not in known_names:
                            issues.append(StructuralIssue(
                                shot_id, "error", "unknown_target",
                                f"Simultaneous animation targets '{sub_target}' which doesn't exist"))
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

        visible_at_end = set(shot_element_names) | all_persisted

        # Add elements created by transforms
        for anim in sequence:
            if anim.get("action") == "transform":
                to_elem = anim.get("to_element")
                if isinstance(to_elem, dict) and to_elem.get("name"):
                    visible_at_end.add(to_elem["name"])
            elif anim.get("action") == "simultaneous":
                for sub in anim.get("animations", []):
                    if sub.get("action") == "transform":
                        to_elem = sub.get("to_element")
                        if isinstance(to_elem, dict) and to_elem.get("name"):
                            visible_at_end.add(to_elem["name"])

        # Remove elements that were faded out during the sequence
        for anim in sequence:
            if anim.get("action") == "fade_out":
                visible_at_end.discard(anim.get("target", ""))
            elif anim.get("action") == "simultaneous":
                for sub in anim.get("animations", []):
                    if sub.get("action") == "fade_out":
                        visible_at_end.discard(sub.get("target", ""))

        accounted = cleanup | persists
        for name in visible_at_end - accounted:
            issues.append(StructuralIssue(
                shot_id, "warning", "unaccounted_element",
                f"Element '{name}' not in cleanup or persists"))

        for name in cleanup:
            if name not in visible_at_end:
                issues.append(StructuralIssue(
                    shot_id, "warning", "cleanup_invisible",
                    f"Cleanup references '{name}' which isn't visible in this shot"))

        all_persisted = persists

    # ── Global checks ──
    total_elements = len(all_element_names)
    if total_elements == 0:
        issues.append(StructuralIssue(0, "error", "no_elements_total",
                                      "Screenplay has no elements at all"))
    elif total_elements < len(shots):
        issues.append(StructuralIssue(0, "warning", "few_elements",
                                      f"Only {total_elements} elements across {len(shots)} shots"))

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
