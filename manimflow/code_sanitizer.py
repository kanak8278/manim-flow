"""Code sanitizer - fixes common LLM code generation mistakes before rendering.

Faster and cheaper than an auto-fix LLM loop. Catches the most frequent issues:
- Invalid rate functions
- Invalid color names
- Invalid position constants
- LaTeX issues in MathTex
- Missing imports
"""

import re


# Valid rate functions in Manim (that don't need special imports)
VALID_RATE_FUNCS = {
    "linear", "smooth", "rush_into", "rush_from", "slow_into",
    "there_and_back", "there_and_back_with_pause", "running_start",
    "not_quite_there", "wiggle", "lingering",
    "double_smooth", "exponential_decay",
}

# Rate functions that need: from manim.utils.rate_functions import ...
RATE_FUNC_ALIASES = {
    "ease_in_cubic": "smooth",
    "ease_out_cubic": "smooth",
    "ease_in_out_cubic": "smooth",
    "ease_in_quad": "smooth",
    "ease_out_quad": "smooth",
    "ease_in_out_quad": "smooth",
    "ease_in_sine": "smooth",
    "ease_out_sine": "smooth",
    "ease_in_out_sine": "smooth",
    "ease_in_expo": "smooth",
    "ease_out_expo": "smooth",
    "ease_in_out_expo": "smooth",
    "ease_in_bounce": "there_and_back",
    "ease_out_bounce": "there_and_back",
    "ease_in_out_bounce": "there_and_back",
    "ease_in_elastic": "smooth",
    "ease_out_elastic": "smooth",
    "ease_in_out_elastic": "smooth",
    "ease_in_back": "smooth",
    "ease_out_back": "smooth",
    "ease_in_out_back": "smooth",
}

# Position constants
POSITION_FIXES = {
    "CENTER": "ORIGIN",
}

# Invalid colors -> valid replacements
COLOR_FIXES = {
    "CYAN": '"#00FFFF"',
    "LIME": "GREEN",
    "CORAL": "ORANGE",
    "INDIGO": "PURPLE",
    "VIOLET": "PURPLE",
}


def _convert_mathtex_to_text(line: str) -> str:
    """Convert a MathTex() call to Text() with readable math content."""
    # Replace MathTex with Text
    line = line.replace("MathTex(", "Text(")

    # Convert LaTeX symbols to readable text
    latex_to_text = {
        "\\\\pi": "pi",
        "\\pi": "pi",
        "\\\\times": " x ",
        "\\times": " x ",
        "\\\\div": " / ",
        "\\div": " / ",
        "\\\\frac": "",
        "\\frac": "",
        "\\\\cdot": " . ",
        "\\cdot": " . ",
        "\\\\rightarrow": " -> ",
        "\\rightarrow": " -> ",
        "\\\\infty": "inf",
        "\\infty": "inf",
        "\\\\approx": " ~ ",
        "\\approx": " ~ ",
        "\\\\neq": " != ",
        "\\neq": " != ",
        "\\\\leq": " <= ",
        "\\leq": " <= ",
        "\\\\geq": " >= ",
        "\\geq": " >= ",
        "\\\\theta": "theta",
        "\\theta": "theta",
        "\\\\alpha": "alpha",
        "\\alpha": "alpha",
        "\\\\beta": "beta",
        "\\beta": "beta",
        "\\\\Delta": "Delta",
        "\\Delta": "Delta",
        "\\\\sqrt": "sqrt",
        "\\sqrt": "sqrt",
    }
    for latex, text in latex_to_text.items():
        line = line.replace(latex, text)

    # Remove remaining backslashes (LaTeX commands we don't have mappings for)
    # But preserve escaped quotes and actual backslashes in Python strings
    # Only remove \command patterns inside string literals
    line = re.sub(r'\\([a-zA-Z]+)', r'\1', line)

    # Also handle: TransformMatchingTex -> Transform (since we're not using Tex anymore)
    line = line.replace("TransformMatchingTex(", "Transform(")

    return line


def _inject_scene_cleanup(lines: list[str], fixes: list[str]) -> list[str]:
    """Auto-inject FadeOut between scene sections.

    Detects scene boundaries from comments like '# === SCENE' or '# Scene N'
    and inserts `self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)`
    before each new scene starts (if not already present).
    """
    result = []
    scene_boundary_pattern = re.compile(
        r'^\s*#\s*={2,}.*(?:scene|act|section|part)\s*',
        re.IGNORECASE,
    )
    prev_was_boundary = False
    injected_count = 0

    for i, line in enumerate(lines):
        # Detect scene boundary comments
        if scene_boundary_pattern.search(line):
            # Check if there's already a FadeOut nearby (within 3 lines before)
            recent = "\n".join(lines[max(0, i-3):i])
            if "FadeOut" not in recent and "self.mobjects" not in recent and i > 10:
                # Inject cleanup before this scene boundary
                indent = "        "  # 8 spaces (inside construct method)
                cleanup_line = f"{indent}self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)"
                result.append(cleanup_line)
                injected_count += 1
            prev_was_boundary = True
        else:
            prev_was_boundary = False

        result.append(line)

    if injected_count > 0:
        fixes.append(f"Auto-injected {injected_count} FadeOut cleanup(s) between scenes")

    return result


def sanitize_code(code: str) -> tuple[str, list[str]]:
    """
    Fix common issues in generated Manim code.

    Returns:
        (fixed_code, list_of_fixes_applied)
    """
    fixes = []
    lines = code.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        original = line

        # Fix rate functions
        for bad_name, good_name in RATE_FUNC_ALIASES.items():
            if bad_name in line:
                line = line.replace(bad_name, good_name)
                if line != original:
                    fixes.append(f"Line {i+1}: Replaced rate_func '{bad_name}' with '{good_name}'")

        # Fix position constants
        for bad_pos, good_pos in POSITION_FIXES.items():
            # Only replace bare CENTER, not in strings
            if re.search(rf'\b{bad_pos}\b', line.split("#")[0].split('"')[0]):
                line = re.sub(rf'\b{bad_pos}\b', good_pos, line)
                if line != original:
                    fixes.append(f"Line {i+1}: Replaced '{bad_pos}' with '{good_pos}'")

        # Convert ALL MathTex to Text — avoids dvisvgm/LaTeX rendering issues entirely
        # Our highest-scoring videos (7-8.5/10) all used Text() only
        if "MathTex(" in line and "TransformMatchingTex" not in line:
            old_line = line
            # Convert LaTeX content to readable text
            line = _convert_mathtex_to_text(line)
            if line != old_line:
                fixes.append(f"Line {i+1}: Converted MathTex to Text (avoids LaTeX rendering)")

        new_lines.append(line)

    code = "\n".join(new_lines)

    # Fix non-ASCII characters in Text() — render as grey boxes
    for i, line in enumerate(new_lines):
        if "Text(" in line:
            # Find string content in Text()
            text_matches = re.findall(r'Text\(["\']([^"\']*)["\']', line)
            for text_content in text_matches:
                # Check for non-ASCII characters
                cleaned = ''.join(c if ord(c) < 128 else '' for c in text_content)
                if cleaned != text_content:
                    original = line
                    line = line.replace(text_content, cleaned)
                    new_lines[i] = line
                    if line != original:
                        removed_chars = set(c for c in text_content if ord(c) >= 128)
                        fixes.append(f"Line {i+1}: Removed non-ASCII chars {removed_chars} from Text()")

    # Fix Cross() — renders as ugly grey box
    for i, line in enumerate(new_lines):
        if "Cross(" in line and "cross" not in line.lower().split("=")[0] if "=" in line else True:
            # Check if it's actually the Cross mobject
            if re.search(r'\bCross\(', line):
                original = line
                # Replace Cross(obj) with two diagonal Lines
                line = line.replace("Cross(", "# Cross removed — use Line() strike-through instead # Cross(")
                if line != original:
                    fixes.append(f"Line {i+1}: Commented out Cross() (renders poorly)")
                    new_lines[i] = line

    # Auto-inject FadeOut between scene sections
    # Detect scene boundaries (comments like "# === SCENE" or "# Scene N" or large gaps)
    new_lines = _inject_scene_cleanup(new_lines, fixes)

    # Rebuild code from modified new_lines
    code = "\n".join(new_lines)

    # Ensure imports exist
    if "from manim import" not in code:
        code = "from manim import *\nimport numpy as np\n\n" + code
        fixes.append("Added missing manim imports")

    if "import numpy" not in code and "np." in code:
        code = code.replace("from manim import *", "from manim import *\nimport numpy as np")
        fixes.append("Added missing numpy import")

    return code, fixes
