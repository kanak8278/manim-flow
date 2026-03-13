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


def _estimate_code_duration(lines: list[str]) -> float:
    """Estimate total animation duration from run_time and wait() calls."""
    total = 0
    for line in lines:
        if "run_time=" in line:
            try:
                rt = float(re.search(r'run_time\s*=\s*([0-9.]+)', line).group(1))
                total += rt
            except (AttributeError, ValueError):
                total += 1  # default run_time
        elif "self.wait(" in line:
            try:
                wt = float(re.search(r'self\.wait\(([0-9.]+)', line).group(1))
                total += wt
            except (AttributeError, ValueError):
                total += 1
        elif "self.play(" in line and "run_time" not in line:
            total += 1  # default 1s for play() without explicit run_time
    return total


def _estimate_target_duration(code: str) -> float:
    """Extract target duration from the injected comment."""
    # Look for: # TOTAL TARGET DURATION: 112s
    m = re.search(r'# TOTAL TARGET DURATION:\s*(\d+)s', code)
    if m:
        return float(m.group(1))

    # Fallback: look for any duration hint
    m = re.search(r'# TOTAL.*?(\d+)s', code, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # Count scenes and estimate 15s each
    scene_count = len(re.findall(r'#\s*={2,}.*(?:scene|act)', code, re.IGNORECASE))
    if scene_count > 0:
        return scene_count * 18  # ~18s per scene average

    return 0


def _inject_scene_cleanup(lines: list[str], fixes: list[str]) -> list[str]:
    """Auto-inject FadeOut between scene sections.

    Detects scene boundaries from:
    - Comments like '# === SCENE' or '# Scene N'
    - `with self.voiceover(` blocks (manim-voiceover scenes)
    Inserts cleanup before each new scene starts.
    """
    result = []
    boundary_patterns = [
        re.compile(r'^\s*#\s*={2,}.*(?:scene|act|section|part)\s*', re.IGNORECASE),
        re.compile(r'^\s*with\s+self\.voiceover\('),
    ]
    injected_count = 0

    for i, line in enumerate(lines):
        is_boundary = any(p.search(line) for p in boundary_patterns)

        if is_boundary and i > 10:
            # Check the lines before this boundary
            recent = "\n".join(lines[max(0, i-5):i])

            if "self.mobjects" not in recent:
                # There's a FadeOut but it might be PARTIAL (missing elements).
                # Or there's no FadeOut at all.
                # Inject a catch-all cleanup that clears everything.
                indent = "        "  # 8 spaces (inside construct method)
                # Always use the same catch-all pattern (analyzable + animated)
                cleanup_line = f"{indent}self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)  # auto-cleanup"
                result.append(cleanup_line)
                injected_count += 1

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

    # Check if video duration roughly matches target
    # If too short, add padding wait at the end
    target_duration = _estimate_target_duration(code)
    estimated_duration = _estimate_code_duration(new_lines)

    if target_duration > 0 and estimated_duration < target_duration * 0.8:
        # Video is more than 20% too short — add padding
        deficit = target_duration - estimated_duration
        # Find the last line in construct() and add a wait before it
        for i in range(len(new_lines) - 1, -1, -1):
            stripped = new_lines[i].strip()
            if stripped and not stripped.startswith("#") and "self." in stripped:
                # Insert padding wait before the last animation
                padding = min(deficit, 15)  # Cap at 15s padding
                indent = "        "
                new_lines.insert(i, f"{indent}self.wait({padding:.1f})  # Padding to match voiceover duration")
                fixes.append(f"Added {padding:.1f}s wait padding (video was {estimated_duration:.0f}s, target {target_duration:.0f}s)")
                break

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
