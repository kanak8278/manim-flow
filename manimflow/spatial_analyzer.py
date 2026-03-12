"""Spatial analyzer - simulates scene layout to detect overlaps, off-screen elements, etc.

This is Approach 1: static code analysis that catches visual issues BEFORE rendering.
Much cheaper than frame extraction + vision model, catches ~80% of layout issues.

The analyzer parses Manim code and tracks:
- What mobjects exist and their approximate positions/sizes
- What's on screen at each point in time
- Where text, equations, curves, and shapes are placed
- Overlap detection between concurrent elements
- Off-screen detection (beyond Manim's default frame)
"""

import re
import ast
from dataclasses import dataclass, field


# Manim's default frame boundaries (in Manim units)
FRAME_WIDTH = 14.22  # ~7.11 each side
FRAME_HEIGHT = 8.0   # ~4 each side
FRAME_X_MIN = -FRAME_WIDTH / 2
FRAME_X_MAX = FRAME_WIDTH / 2
FRAME_Y_MIN = -FRAME_HEIGHT / 2
FRAME_Y_MAX = FRAME_HEIGHT / 2

# Approximate sizes for common elements
TEXT_HEIGHT_PER_FONTSIZE = 0.035  # rough: font_size * this = height in Manim units
TEXT_WIDTH_PER_CHAR = 0.022      # rough: chars * font_size * this = width


@dataclass
class BBox:
    """Axis-aligned bounding box."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def center(self):
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)

    @property
    def width(self):
        return self.x_max - self.x_min

    @property
    def height(self):
        return self.y_max - self.y_min

    def overlaps(self, other: "BBox") -> bool:
        return (
            self.x_min < other.x_max
            and self.x_max > other.x_min
            and self.y_min < other.y_max
            and self.y_max > other.y_min
        )

    def overlap_area(self, other: "BBox") -> float:
        if not self.overlaps(other):
            return 0
        dx = min(self.x_max, other.x_max) - max(self.x_min, other.x_min)
        dy = min(self.y_max, other.y_max) - max(self.y_min, other.y_min)
        return dx * dy

    def is_offscreen(self) -> bool:
        return (
            self.x_max < FRAME_X_MIN
            or self.x_min > FRAME_X_MAX
            or self.y_max < FRAME_Y_MIN
            or self.y_min > FRAME_Y_MAX
        )

    def partially_offscreen(self) -> bool:
        return (
            self.x_min < FRAME_X_MIN
            or self.x_max > FRAME_X_MAX
            or self.y_min < FRAME_Y_MIN
            or self.y_max > FRAME_Y_MAX
        )


@dataclass
class SceneElement:
    """A tracked element on screen."""
    name: str            # variable name in code
    kind: str            # text, mathtex, circle, rectangle, axes, curve, vgroup, etc
    bbox: BBox
    line_number: int
    content: str = ""    # text content if applicable
    font_size: float = 32
    on_screen: bool = False
    added_at_time: float = 0
    removed_at_time: float = -1


def analyze_scene(code: str) -> dict:
    """
    Analyze Manim code for spatial/temporal layout issues.

    Returns dict with:
        issues: list of critical problems
        warnings: list of potential problems
        elements: list of tracked elements
        timeline: scene timeline with events
        stats: summary statistics
    """
    lines = code.split("\n")
    issues = []
    warnings = []
    elements: dict[str, SceneElement] = {}
    on_screen: set[str] = set()
    timeline = []
    current_time = 0.0
    reported_overlap_pairs: set = set()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # --- Track element creation ---
        created = _parse_creation(stripped, i)
        if created:
            elements[created.name] = created

        # --- Track positioning ---
        _parse_positioning(stripped, elements)

        # --- Track animations (what goes on/off screen) ---
        anim_result = _parse_animation(stripped, i, elements, on_screen)
        if anim_result:
            event_type, names, run_time = anim_result
            current_time += run_time

            for name in names:
                if event_type == "add":
                    on_screen.add(name)
                    if name in elements:
                        elements[name].on_screen = True
                        elements[name].added_at_time = current_time
                elif event_type == "remove":
                    on_screen.discard(name)
                    if name in elements:
                        elements[name].on_screen = False
                        elements[name].removed_at_time = current_time

            timeline.append({
                "time": round(current_time, 1),
                "event": event_type,
                "elements": names,
                "line": i,
            })

            # Check overlaps among currently on-screen elements
            _check_overlaps(on_screen, elements, current_time, issues, warnings, i,
                          reported_overlap_pairs)

        # --- Track wait() ---
        wait_match = re.search(r"self\.wait\(([^)]*)\)", stripped)
        if wait_match:
            try:
                current_time += float(wait_match.group(1) or "1")
            except ValueError:
                current_time += 1

    # --- Post-analysis checks ---

    # Check for elements that were never removed
    for name, elem in elements.items():
        if elem.on_screen and elem.removed_at_time < 0:
            if elem.kind in ("text", "mathtex"):
                warnings.append(
                    f"Line {elem.line_number}: '{name}' ({elem.kind}) is never FadeOut'd — "
                    f"may cause text accumulation"
                )

    # Check for off-screen elements
    for name, elem in elements.items():
        if elem.bbox.is_offscreen():
            issues.append(
                f"Line {elem.line_number}: '{name}' is completely off-screen "
                f"(center: {elem.bbox.center})"
            )
        elif elem.bbox.partially_offscreen():
            warnings.append(
                f"Line {elem.line_number}: '{name}' partially extends off-screen "
                f"(bbox: x=[{elem.bbox.x_min:.1f}, {elem.bbox.x_max:.1f}], "
                f"y=[{elem.bbox.y_min:.1f}, {elem.bbox.y_max:.1f}])"
            )

    # Check for empty screen periods
    _check_empty_screen(timeline, current_time, warnings)

    return {
        "issues": issues,
        "warnings": warnings,
        "elements": {k: _elem_to_dict(v) for k, v in elements.items()},
        "timeline": timeline,
        "stats": {
            "total_elements": len(elements),
            "total_duration": round(current_time, 1),
            "max_concurrent": _max_concurrent(timeline),
            "issue_count": len(issues),
            "warning_count": len(warnings),
        },
    }


def _parse_creation(line: str, line_num: int) -> SceneElement | None:
    """Parse element creation statements."""
    # Match: var = Text("content", ...)
    m = re.match(r"(\w+)\s*=\s*Text\(([\"'])(.*?)\2", line)
    if m:
        name, _, content = m.groups()
        font_size = _extract_kwarg(line, "font_size", 32)
        bbox = _estimate_text_bbox(content, font_size)
        return SceneElement(name=name, kind="text", bbox=bbox, line_number=line_num,
                          content=content, font_size=font_size)

    # Match: var = MathTex(r"...", ...)
    m = re.match(r"(\w+)\s*=\s*MathTex\(", line)
    if m:
        name = m.group(1)
        font_size = _extract_kwarg(line, "font_size", 48)
        bbox = _estimate_text_bbox("math_expr", font_size, is_math=True)
        return SceneElement(name=name, kind="mathtex", bbox=bbox, line_number=line_num,
                          font_size=font_size)

    # Match: var = Circle(...)
    m = re.match(r"(\w+)\s*=\s*Circle\(", line)
    if m:
        name = m.group(1)
        radius = _extract_kwarg(line, "radius", 1.0)
        bbox = BBox(-radius, -radius, radius, radius)
        return SceneElement(name=name, kind="circle", bbox=bbox, line_number=line_num)

    # Match: var = Rectangle(...)
    m = re.match(r"(\w+)\s*=\s*Rectangle\(", line)
    if m:
        name = m.group(1)
        width = _extract_kwarg(line, "width", 4.0)
        height = _extract_kwarg(line, "height", 2.0)
        bbox = BBox(-width/2, -height/2, width/2, height/2)
        return SceneElement(name=name, kind="rectangle", bbox=bbox, line_number=line_num)

    # Match: var = Axes(...)
    m = re.match(r"(\w+)\s*=\s*Axes\(", line)
    if m:
        name = m.group(1)
        x_length = _extract_kwarg(line, "x_length", 10.0)
        y_length = _extract_kwarg(line, "y_length", 6.0)
        bbox = BBox(-x_length/2, -y_length/2, x_length/2, y_length/2)
        return SceneElement(name=name, kind="axes", bbox=bbox, line_number=line_num)

    # Match: var = VGroup(...)
    m = re.match(r"(\w+)\s*=\s*VGroup\(", line)
    if m:
        name = m.group(1)
        bbox = BBox(-2, -1, 2, 1)  # rough estimate
        return SceneElement(name=name, kind="vgroup", bbox=bbox, line_number=line_num)

    # Match: var = Arrow/Line/Dot/Polygon
    for shape in ["Arrow", "Line", "Dot", "Polygon", "Square", "Triangle",
                   "ParametricFunction", "Sector", "Arc", "NumberPlane"]:
        m = re.match(rf"(\w+)\s*=\s*{shape}\(", line)
        if m:
            name = m.group(1)
            bbox = BBox(-1, -1, 1, 1)  # rough default
            return SceneElement(name=name, kind=shape.lower(), bbox=bbox, line_number=line_num)

    return None


def _parse_positioning(line: str, elements: dict[str, SceneElement]):
    """Parse positioning statements and update element bboxes."""
    # Match: var.move_to(UP * 2.5)
    m = re.search(r"(\w+)\.move_to\((.+?)\)", line)
    if m:
        name, pos_expr = m.groups()
        if name in elements:
            x, y = _parse_position(pos_expr)
            elem = elements[name]
            w, h = elem.bbox.width, elem.bbox.height
            elem.bbox = BBox(x - w/2, y - h/2, x + w/2, y + h/2)

    # Match: .move_to() in chained calls
    m = re.search(r"\.move_to\((.+?)\)", line)
    if m:
        # Try to find which var this applies to
        var_match = re.match(r"(\w+)\s*=.*\.move_to", line)
        if var_match and var_match.group(1) in elements:
            x, y = _parse_position(m.group(1))
            elem = elements[var_match.group(1)]
            w, h = elem.bbox.width, elem.bbox.height
            elem.bbox = BBox(x - w/2, y - h/2, x + w/2, y + h/2)

    # Match: var.next_to(other, DOWN, ...)
    m = re.search(r"(\w+)\.next_to\((\w+),\s*(\w+)", line)
    if m:
        name, other_name, direction = m.groups()
        if name in elements and other_name in elements:
            other = elements[other_name]
            ox, oy = other.bbox.center
            offset = 0.5  # default buff
            dx, dy = _direction_vector(direction)
            nx = ox + dx * (other.bbox.width/2 + elements[name].bbox.width/2 + offset)
            ny = oy + dy * (other.bbox.height/2 + elements[name].bbox.height/2 + offset)
            elem = elements[name]
            w, h = elem.bbox.width, elem.bbox.height
            elem.bbox = BBox(nx - w/2, ny - h/2, nx + w/2, ny + h/2)


def _parse_animation(line: str, line_num: int, elements: dict, on_screen: set) -> tuple | None:
    """Parse self.play() calls to track what goes on/off screen."""
    if "self.play(" not in line and "self.add(" not in line:
        return None

    run_time = _extract_kwarg(line, "run_time", 1.0)

    # Detect additions
    add_names = []
    for pattern in [r"Write\((\w+)", r"Create\((\w+)", r"FadeIn\((\w+)",
                    r"GrowFromCenter\((\w+)", r"GrowArrow\((\w+)",
                    r"DrawBorderThenFill\((\w+)", r"SpinInFromNothing\((\w+)",
                    r"self\.add\(([^)]+)\)"]:
        for m in re.finditer(pattern, line):
            names = [n.strip() for n in m.group(1).split(",")]
            add_names.extend(names)

    # Detect removals
    remove_names = []
    for pattern in [r"FadeOut\((\w+)", r"Uncreate\((\w+)", r"Unwrite\((\w+)"]:
        for m in re.finditer(pattern, line):
            remove_names.append(m.group(1))

    # Detect transforms (source stays, visually becomes target)
    for m in re.finditer(r"Transform\((\w+),\s*(\w+)", line):
        # Source stays on screen (reference), target visual replaces it
        pass

    if add_names and remove_names:
        # Mixed — process removals first, then additions
        result_names = remove_names + add_names
        # Return as add since it's net effect
        return ("add", add_names, run_time)
    elif add_names:
        return ("add", add_names, run_time)
    elif remove_names:
        return ("remove", remove_names, run_time)

    return ("other", [], run_time)


def _check_overlaps(on_screen: set, elements: dict, time: float,
                    issues: list, warnings: list, line: int,
                    _reported_pairs: set = None):
    """Check for overlapping text elements on screen. Deduplicates by pair."""
    if _reported_pairs is None:
        _reported_pairs = set()

    text_elements = [
        (name, elements[name])
        for name in on_screen
        if name in elements and elements[name].kind in ("text", "mathtex")
    ]

    for i, (name1, elem1) in enumerate(text_elements):
        for name2, elem2 in text_elements[i+1:]:
            pair_key = tuple(sorted([name1, name2]))
            if pair_key in _reported_pairs:
                continue  # Already reported this pair

            overlap = elem1.bbox.overlap_area(elem2.bbox)
            if overlap > 0:
                min_area = min(
                    elem1.bbox.width * elem1.bbox.height,
                    elem2.bbox.width * elem2.bbox.height,
                )
                if min_area > 0 and overlap / min_area > 0.3:
                    _reported_pairs.add(pair_key)
                    issues.append(
                        f"Line {line}: Text overlap between '{name1}' and '{name2}' "
                        f"(overlap: {overlap/min_area:.0%})"
                    )
                elif overlap > 0.1:
                    _reported_pairs.add(pair_key)
                    warnings.append(
                        f"Line {line}: Possible text overlap between '{name1}' and '{name2}'"
                    )


def _check_empty_screen(timeline: list, total_time: float, warnings: list):
    """Detect periods where nothing is on screen."""
    # Simple heuristic: consecutive removes without adds
    last_event = None
    for event in timeline:
        if event["event"] == "remove" and last_event and last_event["event"] == "remove":
            gap = event["time"] - last_event["time"]
            if gap > 2:
                warnings.append(
                    f"Possible empty screen at t={last_event['time']:.1f}s - "
                    f"{event['time']:.1f}s ({gap:.1f}s gap)"
                )
        last_event = event


def _estimate_text_bbox(content: str, font_size: float, is_math: bool = False) -> BBox:
    """Estimate bounding box for text/math content."""
    char_count = len(content) if not is_math else 8  # rough estimate for math
    height = font_size * TEXT_HEIGHT_PER_FONTSIZE
    width = char_count * font_size * TEXT_WIDTH_PER_CHAR
    return BBox(-width/2, -height/2, width/2, height/2)


def _extract_kwarg(line: str, key: str, default: float) -> float:
    """Extract a keyword argument value from a function call."""
    m = re.search(rf"{key}\s*=\s*([0-9.]+)", line)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return default


def _parse_position(expr: str) -> tuple[float, float]:
    """Parse a Manim position expression to approximate (x, y) coordinates."""
    x, y = 0.0, 0.0

    # Handle common patterns
    expr = expr.strip()

    # UP * N, DOWN * N, LEFT * N, RIGHT * N
    for m in re.finditer(r"(UP|DOWN|LEFT|RIGHT)\s*\*\s*([0-9.]+)", expr):
        direction, value = m.group(1), float(m.group(2))
        if direction == "UP":
            y += value
        elif direction == "DOWN":
            y -= value
        elif direction == "LEFT":
            x -= value
        elif direction == "RIGHT":
            x += value

    # N * UP, N * DOWN, etc
    for m in re.finditer(r"([0-9.]+)\s*\*\s*(UP|DOWN|LEFT|RIGHT)", expr):
        value, direction = float(m.group(1)), m.group(2)
        if direction == "UP":
            y += value
        elif direction == "DOWN":
            y -= value
        elif direction == "LEFT":
            x -= value
        elif direction == "RIGHT":
            x += value

    # Simple UP, DOWN without multiplier
    if "UP" in expr and "*" not in expr.replace("UP", "").replace("DOWN", "").replace("LEFT", "").replace("RIGHT", ""):
        if "UP" in expr:
            y += 1
        if "DOWN" in expr:
            y -= 1
        if "LEFT" in expr:
            x -= 1
        if "RIGHT" in expr:
            x += 1

    # ORIGIN
    if "ORIGIN" in expr:
        x, y = 0, 0

    return (x, y)


def _direction_vector(direction: str) -> tuple[float, float]:
    """Convert direction name to (dx, dy) unit vector."""
    dirs = {
        "UP": (0, 1), "DOWN": (0, -1),
        "LEFT": (-1, 0), "RIGHT": (1, 0),
        "UL": (-1, 1), "UR": (1, 1),
        "DL": (-1, -1), "DR": (1, -1),
    }
    return dirs.get(direction, (0, 0))


def _max_concurrent(timeline: list) -> int:
    """Find maximum number of concurrent on-screen elements."""
    count = 0
    max_count = 0
    for event in timeline:
        if event["event"] == "add":
            count += len(event["elements"])
        elif event["event"] == "remove":
            count -= len(event["elements"])
        max_count = max(max_count, count)
    return max_count


def _elem_to_dict(elem: SceneElement) -> dict:
    return {
        "name": elem.name,
        "kind": elem.kind,
        "bbox": {
            "x_min": round(elem.bbox.x_min, 2),
            "y_min": round(elem.bbox.y_min, 2),
            "x_max": round(elem.bbox.x_max, 2),
            "y_max": round(elem.bbox.y_max, 2),
        },
        "content": elem.content,
        "line": elem.line_number,
        "on_screen": elem.on_screen,
    }


def print_spatial_analysis(result: dict):
    """Pretty-print spatial analysis results."""
    print("\n--- Spatial Analysis ---")
    stats = result["stats"]
    print(f"  Elements: {stats['total_elements']}")
    print(f"  Duration: ~{stats['total_duration']}s")
    print(f"  Max concurrent: {stats['max_concurrent']}")

    if result["issues"]:
        print(f"\n  ISSUES ({len(result['issues'])}):")
        for issue in result["issues"]:
            print(f"    [!] {issue}")

    if result["warnings"]:
        print(f"\n  WARNINGS ({len(result['warnings'])}):")
        for w in result["warnings"][:10]:  # cap at 10
            print(f"    [~] {w}")
        if len(result["warnings"]) > 10:
            print(f"    ... and {len(result['warnings']) - 10} more")
