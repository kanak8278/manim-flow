"""Layout Checker — compares screenplay intent vs code geometry.

Takes:
1. Screenplay (structured JSON with semantic positions and relationships)
2. Scene snapshots (exact geometry from scene_inspector)

Produces actionable layout bugs by checking:
- Compliance: does the code follow screenplay intent?
- Violations: does the code have problems the screenplay didn't intend?

Used after codegen, before render. Feeds bugs back to codegen for fixing.
"""

import re
from dataclasses import dataclass, field
from .scene_inspector import SceneSnapshot, ElementGeometry


# Screen regions → approximate coordinate ranges
REGION_BOUNDS = {
    "top_left":      {"x": (-7, -2), "y": (1.5, 4)},
    "top_center":    {"x": (-3, 3),  "y": (1.5, 4)},
    "top_right":     {"x": (2, 7),   "y": (1.5, 4)},
    "center_left":   {"x": (-7, -2), "y": (-1.5, 1.5)},
    "center":        {"x": (-3, 3),  "y": (-1.5, 1.5)},
    "center_right":  {"x": (2, 7),   "y": (-1.5, 1.5)},
    "bottom_left":   {"x": (-7, -2), "y": (-4, -1.5)},
    "bottom_center": {"x": (-3, 3),  "y": (-4, -1.5)},
    "bottom_right":  {"x": (2, 7),   "y": (-4, -1.5)},
    "above_center":  {"x": (-4, 4),  "y": (0.5, 3)},
    "below_center":  {"x": (-4, 4),  "y": (-3, -0.5)},
}

# Frame bounds
FRAME_X = (-7.11, 7.11)
FRAME_Y = (-4.0, 4.0)


@dataclass
class LayoutIssue:
    """A layout problem found by comparing screenplay intent vs code reality."""
    severity: str  # "error", "warning"
    category: str  # "compliance", "violation"
    issue_type: str
    description: str
    shot_id: int = 0
    step: int = 0
    elements: list[str] = field(default_factory=list)
    fix_hint: str = ""


def check_layout(
    screenplay_data: dict,
    snapshots: list[SceneSnapshot],
) -> list[LayoutIssue]:
    """Compare screenplay intent against code geometry.

    Args:
        screenplay_data: Full screenplay dict with shots and design_rules
        snapshots: SceneSnapshot list from scene_inspector

    Returns:
        List of LayoutIssue objects
    """
    issues = []
    shots = screenplay_data.get("shots", [])

    # Build relationship map from screenplay
    relationships = _build_relationship_map(shots)

    # Check each snapshot for violations
    for snap in snapshots:
        if not snap.elements:
            continue

        # 1. Off-screen check
        _check_offscreen(snap, issues)

        # 2. Unintentional overlap check
        _check_overlaps(snap, relationships, issues)

        # 3. Overcrowding check
        _check_overcrowding(snap, issues)

    # Check compliance: screenplay intent followed?
    _check_region_compliance(shots, snapshots, issues)
    _check_relationship_compliance(shots, snapshots, relationships, issues)
    _check_cleanup_compliance(shots, snapshots, issues)

    return issues


# ─── RELATIONSHIP MAP ───

@dataclass
class Relationship:
    """A spatial relationship declared in the screenplay."""
    element_a: str
    element_b: str
    rel_type: str  # "on", "relative", "inside", "overlaps", "connects"
    direction: str = ""  # "above", "below", "left", "right"
    shot_id: int = 0


def _build_relationship_map(shots: list[dict]) -> list[Relationship]:
    """Extract all spatial relationships from the screenplay."""
    rels = []

    for shot in shots:
        shot_id = shot.get("id", 0)
        for elem in shot.get("elements", []):
            name = elem.get("name", "")
            if not name:
                continue

            # position_on → "on" relationship
            if elem.get("position_on"):
                rels.append(Relationship(
                    element_a=name,
                    element_b=elem["position_on"],
                    rel_type="on",
                    shot_id=shot_id,
                ))

            # position_relative_to → "relative" relationship
            if elem.get("position_relative_to"):
                rels.append(Relationship(
                    element_a=name,
                    element_b=elem["position_relative_to"],
                    rel_type="relative",
                    direction=elem.get("direction", ""),
                    shot_id=shot_id,
                ))

            # inside → "inside" relationship
            if elem.get("inside"):
                rels.append(Relationship(
                    element_a=name,
                    element_b=elem["inside"],
                    rel_type="inside",
                    shot_id=shot_id,
                ))

            # overlaps_with → "overlaps" relationship
            for other in elem.get("overlaps_with", []):
                rels.append(Relationship(
                    element_a=name,
                    element_b=other,
                    rel_type="overlaps",
                    shot_id=shot_id,
                ))

            # from_element / to_element → "connects" relationship
            if elem.get("from_element") and elem.get("to_element"):
                rels.append(Relationship(
                    element_a=name,
                    element_b=elem["from_element"],
                    rel_type="connects",
                    shot_id=shot_id,
                ))
                rels.append(Relationship(
                    element_a=name,
                    element_b=elem["to_element"],
                    rel_type="connects",
                    shot_id=shot_id,
                ))

    return rels


def _is_intentional_overlap(a_name: str, b_name: str, relationships: list[Relationship]) -> bool:
    """Check if overlap between two elements is declared in screenplay."""
    for rel in relationships:
        # Direct overlap declaration
        if rel.rel_type == "overlaps":
            if (rel.element_a == a_name and rel.element_b == b_name) or \
               (rel.element_a == b_name and rel.element_b == a_name):
                return True

        # "on" relationship implies overlap (dot on number_line)
        if rel.rel_type == "on":
            if (rel.element_a == a_name and rel.element_b == b_name) or \
               (rel.element_a == b_name and rel.element_b == a_name):
                return True

        # "inside" relationship implies overlap
        if rel.rel_type == "inside":
            if (rel.element_a == a_name and rel.element_b == b_name) or \
               (rel.element_a == b_name and rel.element_b == a_name):
                return True

        # "connects" — arrow touching its endpoints
        if rel.rel_type == "connects":
            if rel.element_a == a_name and rel.element_b == b_name:
                return True
            if rel.element_a == b_name and rel.element_b == a_name:
                return True

        # "relative" with small buff — slight overlap is expected
        if rel.rel_type == "relative":
            if (rel.element_a == a_name and rel.element_b == b_name) or \
               (rel.element_a == b_name and rel.element_b == a_name):
                return True

    return False


# ─── VIOLATION CHECKS ───

def _check_offscreen(snap: SceneSnapshot, issues: list):
    """Check for elements outside the visible frame."""
    for name, geom in snap.elements.items():
        if geom.is_offscreen():
            issues.append(LayoutIssue(
                severity="error",
                category="violation",
                issue_type="offscreen",
                description=f"'{name}' is off-screen at ({geom.center_x:.1f}, {geom.center_y:.1f})",
                step=snap.step,
                elements=[name],
                fix_hint=f"Move '{name}' within frame bounds x=[{FRAME_X[0]:.1f}, {FRAME_X[1]:.1f}], y=[{FRAME_Y[0]:.1f}, {FRAME_Y[1]:.1f}]",
            ))
        elif (geom.left < FRAME_X[0] or geom.right > FRAME_X[1]
              or geom.bottom < FRAME_Y[0] or geom.top > FRAME_Y[1]):
            issues.append(LayoutIssue(
                severity="warning",
                category="violation",
                issue_type="partially_offscreen",
                description=f"'{name}' extends beyond frame at ({geom.center_x:.1f}, {geom.center_y:.1f}) size={geom.width:.1f}x{geom.height:.1f}",
                step=snap.step,
                elements=[name],
                fix_hint=f"Reduce size or reposition '{name}' to fit within frame",
            ))


def _check_overlaps(snap: SceneSnapshot, relationships: list[Relationship], issues: list):
    """Check for unintentional overlaps."""
    elems = list(snap.elements.values())
    checked = set()

    for i in range(len(elems)):
        for j in range(i + 1, len(elems)):
            a, b = elems[i], elems[j]
            pair = (min(a.name, b.name), max(a.name, b.name))
            if pair in checked:
                continue
            checked.add(pair)

            if not a.overlaps(b):
                continue

            # Check if intentional
            if _is_intentional_overlap(a.name, b.name, relationships):
                continue

            area = a.overlap_area(b)
            smaller = min(a.area, b.area)
            if smaller == 0:
                continue
            pct = area / smaller * 100

            if pct > 50:
                issues.append(LayoutIssue(
                    severity="error",
                    category="violation",
                    issue_type="unintentional_overlap",
                    description=f"'{a.name}' and '{b.name}' overlap {pct:.0f}% — not declared in screenplay",
                    step=snap.step,
                    elements=[a.name, b.name],
                    fix_hint=f"Move '{b.name}' away from '{a.name}'. {a.name} is at ({a.center_x:.1f}, {a.center_y:.1f}), {b.name} at ({b.center_x:.1f}, {b.center_y:.1f})",
                ))
            elif pct > 15:
                issues.append(LayoutIssue(
                    severity="warning",
                    category="violation",
                    issue_type="unintentional_overlap",
                    description=f"'{a.name}' and '{b.name}' overlap {pct:.0f}%",
                    step=snap.step,
                    elements=[a.name, b.name],
                    fix_hint=f"Consider adding spacing between '{a.name}' and '{b.name}'",
                ))


def _check_overcrowding(snap: SceneSnapshot, issues: list):
    """Check for too many elements on screen."""
    count = len(snap.elements)
    if count > 6:
        issues.append(LayoutIssue(
            severity="warning",
            category="violation",
            issue_type="overcrowded",
            description=f"Step {snap.step}: {count} elements on screen (recommended max: 4)",
            step=snap.step,
            elements=list(snap.elements.keys()),
            fix_hint="Consider removing or grouping elements to reduce visual clutter",
        ))


# ─── COMPLIANCE CHECKS ───

def _find_element_in_snapshots(name: str, snapshots: list[SceneSnapshot]) -> ElementGeometry | None:
    """Find an element across all snapshots (returns first occurrence)."""
    for snap in snapshots:
        if name in snap.elements:
            return snap.elements[name]
    return None


def _check_region_compliance(shots: list[dict], snapshots: list[SceneSnapshot], issues: list):
    """Check that elements are in the screen region the screenplay specified."""
    for shot in shots:
        shot_id = shot.get("id", 0)
        for elem in shot.get("elements", []):
            name = elem.get("name", "")
            position = elem.get("position", "")

            if not name or not position or position == "same":
                continue

            if position not in REGION_BOUNDS:
                continue  # not a semantic region — can't check

            bounds = REGION_BOUNDS[position]
            geom = _find_element_in_snapshots(name, snapshots)
            if not geom:
                continue  # element not found in code

            x_ok = bounds["x"][0] <= geom.center_x <= bounds["x"][1]
            y_ok = bounds["y"][0] <= geom.center_y <= bounds["y"][1]

            if not x_ok or not y_ok:
                issues.append(LayoutIssue(
                    severity="error",
                    category="compliance",
                    issue_type="wrong_region",
                    description=(
                        f"'{name}' should be at '{position}' "
                        f"(x:[{bounds['x'][0]},{bounds['x'][1]}], y:[{bounds['y'][0]},{bounds['y'][1]}]) "
                        f"but is at ({geom.center_x:.1f}, {geom.center_y:.1f})"
                    ),
                    shot_id=shot_id,
                    elements=[name],
                    fix_hint=f"Move '{name}' to the {position} region",
                ))


def _check_relationship_compliance(
    shots: list[dict],
    snapshots: list[SceneSnapshot],
    relationships: list[Relationship],
    issues: list,
):
    """Check that spatial relationships from screenplay are satisfied in code."""
    for rel in relationships:
        geom_a = _find_element_in_snapshots(rel.element_a, snapshots)
        geom_b = _find_element_in_snapshots(rel.element_b, snapshots)

        if not geom_a or not geom_b:
            continue  # can't check if elements not found

        if rel.rel_type == "on":
            # A should be geometrically on B (bboxes intersect)
            if not geom_a.overlaps(geom_b):
                issues.append(LayoutIssue(
                    severity="error",
                    category="compliance",
                    issue_type="not_on_target",
                    description=(
                        f"'{rel.element_a}' should be on '{rel.element_b}' "
                        f"but they don't intersect. "
                        f"{rel.element_a} at ({geom_a.center_x:.1f}, {geom_a.center_y:.1f}), "
                        f"{rel.element_b} at ({geom_b.center_x:.1f}, {geom_b.center_y:.1f})"
                    ),
                    shot_id=rel.shot_id,
                    elements=[rel.element_a, rel.element_b],
                    fix_hint=f"Use .move_to({rel.element_b}.number_to_point(value)) to place '{rel.element_a}' on '{rel.element_b}'",
                ))

        elif rel.rel_type == "relative" and rel.direction:
            # Check directional relationship
            ok = True
            if rel.direction == "right" and geom_a.center_x <= geom_b.center_x:
                ok = False
            elif rel.direction == "left" and geom_a.center_x >= geom_b.center_x:
                ok = False
            elif rel.direction == "above" and geom_a.center_y <= geom_b.center_y:
                ok = False
            elif rel.direction == "below" and geom_a.center_y >= geom_b.center_y:
                ok = False

            if not ok:
                direction_map = {"right": "RIGHT", "left": "LEFT", "above": "UP", "below": "DOWN"}
                manim_dir = direction_map.get(rel.direction, rel.direction.upper())
                issues.append(LayoutIssue(
                    severity="error",
                    category="compliance",
                    issue_type="wrong_direction",
                    description=(
                        f"'{rel.element_a}' should be {rel.direction} of '{rel.element_b}' "
                        f"but is at ({geom_a.center_x:.1f}, {geom_a.center_y:.1f}) while "
                        f"'{rel.element_b}' is at ({geom_b.center_x:.1f}, {geom_b.center_y:.1f})"
                    ),
                    shot_id=rel.shot_id,
                    elements=[rel.element_a, rel.element_b],
                    fix_hint=f"Use .next_to({rel.element_b}, {manim_dir}, buff=0.3)",
                ))

        elif rel.rel_type == "inside":
            # A should be contained within B
            if not geom_b.contains(geom_a):
                issues.append(LayoutIssue(
                    severity="error",
                    category="compliance",
                    issue_type="not_inside",
                    description=(
                        f"'{rel.element_a}' should be inside '{rel.element_b}' "
                        f"but is not contained. "
                        f"{rel.element_a} at ({geom_a.center_x:.1f}, {geom_a.center_y:.1f}) size={geom_a.width:.1f}x{geom_a.height:.1f}, "
                        f"{rel.element_b} at ({geom_b.center_x:.1f}, {geom_b.center_y:.1f}) size={geom_b.width:.1f}x{geom_b.height:.1f}"
                    ),
                    shot_id=rel.shot_id,
                    elements=[rel.element_a, rel.element_b],
                    fix_hint=f"Use .move_to({rel.element_b}.get_center()) to place '{rel.element_a}' inside '{rel.element_b}'",
                ))

        elif rel.rel_type == "overlaps":
            # A and B should overlap
            if not geom_a.overlaps(geom_b):
                issues.append(LayoutIssue(
                    severity="error",
                    category="compliance",
                    issue_type="missing_intended_overlap",
                    description=(
                        f"'{rel.element_a}' should overlap '{rel.element_b}' (declared in screenplay) "
                        f"but they don't intersect"
                    ),
                    shot_id=rel.shot_id,
                    elements=[rel.element_a, rel.element_b],
                    fix_hint=f"Reposition '{rel.element_a}' so it intersects with '{rel.element_b}'",
                ))

        elif rel.rel_type == "connects":
            # Arrow should be near its target (within reasonable distance)
            dist_x = abs(geom_a.center_x - geom_b.center_x)
            dist_y = abs(geom_a.center_y - geom_b.center_y)
            # Arrow center should be reasonably close to at least one endpoint
            # (arrows are positioned between their endpoints)
            max_dist = max(geom_a.width, geom_a.height, geom_b.width, geom_b.height) + 2
            if dist_x > max_dist and dist_y > max_dist:
                issues.append(LayoutIssue(
                    severity="warning",
                    category="compliance",
                    issue_type="arrow_far_from_target",
                    description=(
                        f"'{rel.element_a}' (arrow) should connect to '{rel.element_b}' "
                        f"but they are far apart"
                    ),
                    shot_id=rel.shot_id,
                    elements=[rel.element_a, rel.element_b],
                    fix_hint=f"Use Arrow({rel.element_b}.get_center(), ...) to connect properly",
                ))


def _check_cleanup_compliance(shots: list[dict], snapshots: list[SceneSnapshot], issues: list):
    """Check that elements marked for cleanup actually get removed."""
    if not snapshots:
        return

    # The last snapshot should have 0 or few elements (everything cleaned up at the end)
    last_snap = snapshots[-1]
    if last_snap.elements and len(last_snap.elements) > 0:
        # Check if the last shot's cleanup was supposed to clear everything
        if shots:
            last_shot = shots[-1]
            if not last_shot.get("persists"):
                remaining = list(last_snap.elements.keys())
                issues.append(LayoutIssue(
                    severity="warning",
                    category="compliance",
                    issue_type="incomplete_cleanup",
                    description=f"{len(remaining)} elements remain on screen after last shot: {remaining[:5]}",
                    step=last_snap.step,
                    elements=remaining[:5],
                    fix_hint="Add FadeOut for all remaining elements at the end of the scene",
                ))


def format_issues_for_codegen(issues: list[LayoutIssue]) -> str:
    """Format layout issues into a message for the codegen fix agent."""
    if not issues:
        return ""

    lines = ["LAYOUT ISSUES found by comparing your code against the screenplay specification:\n"]

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if errors:
        lines.append(f"ERRORS ({len(errors)}) — must fix:")
        for issue in errors:
            lines.append(f"  [{issue.category.upper()}] {issue.description}")
            if issue.fix_hint:
                lines.append(f"    FIX: {issue.fix_hint}")

    if warnings:
        lines.append(f"\nWARNINGS ({len(warnings)}) — should fix:")
        for issue in warnings:
            lines.append(f"  [{issue.category.upper()}] {issue.description}")
            if issue.fix_hint:
                lines.append(f"    FIX: {issue.fix_hint}")

    lines.append("\nFix ALL errors. Fix warnings if possible.")
    lines.append("Return the complete corrected code.")

    return "\n".join(lines)


def print_layout_check(issues: list[LayoutIssue]):
    """Pretty-print layout check results."""
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    compliance = [i for i in issues if i.category == "compliance"]
    violations = [i for i in issues if i.category == "violation"]

    print(f"\n--- Layout Check ---")
    print(f"  Errors: {len(errors)}, Warnings: {len(warnings)}")
    print(f"  Compliance issues: {len(compliance)}, Violations: {len(violations)}")

    for issue in issues:
        prefix = "[ERROR]" if issue.severity == "error" else "[WARN]"
        cat = issue.category.upper()
        print(f"  {prefix} [{cat}] {issue.description}")
        if issue.fix_hint:
            print(f"    → {issue.fix_hint}")
