"""Wireframe — static frame renderer from Manim code.

Renders quick wireframe PNGs from generated Manim code — one per scene section.
No animation, no voiceover, no video encoding. Just layout snapshots.

Used for:
- Human inspection before committing to full render
- Vision LLM review of layout quality
- Quick iteration on layout problems

Runs AFTER codegen produces code, BEFORE full Manim render.
For screenplay structural validation, use screenplay_validator.py.
For geometric overlap checking, use spatial_analyzer.py on the code.
"""

import os
import re
import subprocess


def render_wireframes(code: str, output_dir: str) -> list[str]:
    """Render static wireframe PNGs from Manim code — one per scene section.

    Parses the code, strips animations and voiceover, creates a version that
    just adds all elements to the scene and captures frames at each section boundary.

    Args:
        code: Manim Python code (GeneratedScene)
        output_dir: Directory to save wireframe PNGs

    Returns:
        List of PNG file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    # Build wireframe scenes — one per scene section in the code
    sections = _extract_scene_sections(code)

    if not sections:
        print("  [wireframe] No scene sections found in code")
        return []

    # Build a single Manim file with one Scene per section
    wireframe_code = _build_wireframe_file(code, sections)

    wireframe_path = os.path.join(output_dir, "_wireframe.py")
    with open(wireframe_path, "w") as f:
        f.write(wireframe_code)

    # Render each wireframe scene
    paths = []
    for i, section_name in enumerate(sections):
        scene_class = f"Wireframe_{i}"
        png_path = os.path.join(output_dir, f"wireframe_{i}_{section_name}.png")

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "manim",
                "-ql",
                "--format",
                "png",
                "--media_dir",
                output_dir,
                wireframe_path,
                scene_class,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Find the generated PNG
            for root, dirs, files in os.walk(output_dir):
                for f in files:
                    if f.endswith(".png") and scene_class in f:
                        src = os.path.join(root, f)
                        os.rename(src, png_path)
                        paths.append(png_path)
                        break
        else:
            err = result.stderr.strip().split("\n")[-1] if result.stderr else "unknown"
            print(f"  [wireframe] Section {i} ({section_name}) failed: {err}")

    # Cleanup temp file
    try:
        os.remove(wireframe_path)
    except OSError:
        pass

    return paths


def _extract_scene_sections(code: str) -> list[str]:
    """Find scene section boundaries in the code.

    Looks for patterns like:
    - # Scene 1: Hook
    - # SHOT 1: Opening
    - # --- SHOT 1 ---
    - with self.voiceover(...)  (each voiceover block = one section)
    """
    sections = []
    lines = code.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Comment markers
        match = re.match(
            r"#\s*(?:Scene|SHOT|Shot|Section)\s*(\d+)\s*[:\-]\s*(.*)", stripped
        )
        if match:
            num = match.group(1)
            name = match.group(2).strip() or f"section_{num}"
            name = re.sub(r"[^a-zA-Z0-9_]", "_", name)[:30].strip("_")
            sections.append(name)
            continue

        # Voiceover blocks as section markers (fallback)
        if "with self.voiceover" in stripped and not sections:
            sections.append(f"voiceover_{len(sections)}")

    # If no markers found, treat the whole thing as one section
    if not sections:
        sections.append("full_scene")

    return sections


def _build_wireframe_file(code: str, sections: list[str]) -> str:
    """Build a Manim file with one static Scene per code section.

    Each scene creates elements without playing animations,
    then captures a single frame.
    """
    lines = code.split("\n")

    # Extract helper functions (make_card, etc.)
    helpers = _extract_helpers(lines)

    # Extract element creations per section
    section_elements = _extract_elements_per_section(lines, len(sections))

    # Build output
    out = [
        "from manim import *",
        "import numpy as np",
        "",
    ]

    # Add helpers at module level
    for helper in helpers:
        out.append(helper)
    out.append("")

    for i, section_name in enumerate(sections):
        out.append(f"class Wireframe_{i}(Scene):")
        out.append("    def construct(self):")
        out.append("        self.camera.background_color = BLACK")

        elements = section_elements.get(i, [])
        if elements:
            for elem_line in elements:
                out.append(f"        {elem_line}")
        else:
            out.append(f"        # No elements found for section {section_name}")
            out.append("        pass")
        out.append("")

    return "\n".join(out)


def _extract_helpers(lines: list[str]) -> list[str]:
    """Extract helper function definitions (make_card, etc.)."""
    helpers = []
    in_helper = False
    current_helper = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()

        if re.match(r"def \w+\(", stripped) and "construct" not in stripped:
            in_helper = True
            current_helper = []
            # Dedent to module level
            indent_level = len(line) - len(line.lstrip())

        if in_helper:
            # Dedent the helper to module level
            if line.strip():
                dedented = (
                    line[indent_level:] if len(line) > indent_level else line.lstrip()
                )
                current_helper.append(dedented)
            else:
                current_helper.append("")

            # Check if helper ended (next non-indented, non-empty line)
            if stripped.startswith("return ") or (
                current_helper
                and len(current_helper) > 2
                and stripped
                and not stripped.startswith(" ")
                and not stripped.startswith("def ")
            ):
                helpers.extend(current_helper)
                helpers.append("")
                in_helper = False
                current_helper = []

    if current_helper:
        helpers.extend(current_helper)

    return helpers


def _extract_elements_per_section(
    lines: list[str], num_sections: int
) -> dict[int, list[str]]:
    """Extract element creation + positioning lines, grouped by section.

    Returns dict mapping section index → list of code lines that create/position elements.
    """
    section_elements = {}
    current_section = 0
    var_names = set()

    # Manim constructors to look for
    constructors = [
        "Text(",
        "RoundedRectangle(",
        "make_card(",
        "Arrow(",
        "Line(",
        "Circle(",
        "Dot(",
        "NumberLine(",
        "Axes(",
        "VGroup(",
        "Brace(",
        "Table(",
        "MathTex(",
        "Tex(",
        "Square(",
        "Rectangle(",
        "Polygon(",
        "Star(",
        "DashedLine(",
        "DoubleArrow(",
    ]

    for line in lines:
        stripped = line.strip()

        # Detect section boundaries
        if re.match(r"#\s*(?:Scene|SHOT|Shot|Section)\s*\d+", stripped):
            current_section = min(current_section + 1, num_sections - 1)
            if current_section > 0:
                # Don't increment on first match — section 0 is before first marker
                pass
            continue

        if current_section not in section_elements:
            section_elements[current_section] = []

        # Skip non-element lines
        if any(
            stripped.startswith(s)
            for s in [
                "from ",
                "import ",
                "class ",
                "def construct",
                "def ",
                "self.play(",
                "self.wait",
                "self.set_speech",
                "with self.voiceover",
                "tracker.",
                "if self.mobjects",
                "#",
            ]
        ):
            continue

        if "wait_until_bookmark" in stripped:
            continue

        # Element creation
        if "=" in stripped and any(cls in stripped for cls in constructors):
            section_elements[current_section].append(stripped)
            var_name = stripped.split("=")[0].strip()
            if var_name and not var_name.startswith("#"):
                var_names.add(var_name)
                section_elements[current_section].append(f"self.add({var_name})")
            continue

        # Positioning calls (chained or standalone)
        if any(
            m in stripped for m in [".move_to(", ".next_to(", ".shift(", ".to_edge("]
        ):
            section_elements[current_section].append(stripped)

    return section_elements
