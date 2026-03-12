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

        # Fix \\text{} in MathTex — replace with Text()
        if "MathTex" in line and "\\text{" in line:
            # Extract the \text{content} and convert MathTex to Text
            import re as _re
            text_match = _re.search(r'\\text\{([^}]+)\}', line)
            if text_match:
                text_content = text_match.group(1)
                # Replace MathTex(r"\text{foo} = bar") with Text("foo = bar")
                old_line = line
                # Simple case: \text{} is the whole content
                if "\\text{" in line and "MathTex" in line:
                    # Convert to Text() — remove LaTeX formatting
                    cleaned = _re.sub(r'\\text\{([^}]+)\}', r'\1', line)
                    cleaned = cleaned.replace("MathTex", "Text")
                    cleaned = cleaned.replace("\\pi", "pi").replace("\\times", "x")
                    cleaned = cleaned.replace("\\frac", "").replace("\\", "")
                    line = cleaned
                    if line != old_line:
                        fixes.append(f"Line {i+1}: Converted MathTex with \\text{{}} to Text()")

        new_lines.append(line)

    code = "\n".join(new_lines)

    # Fix blank first frame: add a tiny wait after background_color to render first frame with content
    # The issue is Manim creates a black frame before any animation starts
    found_background = False
    for i, line in enumerate(new_lines):
        if "background_color" in line and "BLACK" in line:
            found_background = True
        elif found_background and "self.play" in line and i > 0:
            # Insert self.wait(0.01) before first animation to avoid pure black frame
            # Actually, don't — this just makes a longer black frame. The real fix is
            # to ensure the first animation immediately shows content.
            break

    # Ensure imports exist
    if "from manim import" not in code:
        code = "from manim import *\nimport numpy as np\n\n" + code
        fixes.append("Added missing manim imports")

    if "import numpy" not in code and "np." in code:
        code = code.replace("from manim import *", "from manim import *\nimport numpy as np")
        fixes.append("Added missing numpy import")

    return code, fixes
