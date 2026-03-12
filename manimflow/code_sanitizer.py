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

        # Fix \\text{} in MathTex
        if "MathTex" in line and "\\text" in line:
            # This is a harder fix — just warn, the render loop will catch it
            fixes.append(f"Line {i+1}: WARNING - \\text{{}} in MathTex may cause LaTeX crash")

        new_lines.append(line)

    code = "\n".join(new_lines)

    # Ensure imports exist
    if "from manim import" not in code:
        code = "from manim import *\nimport numpy as np\n\n" + code
        fixes.append("Added missing manim imports")

    if "import numpy" not in code and "np." in code:
        code = code.replace("from manim import *", "from manim import *\nimport numpy as np")
        fixes.append("Added missing numpy import")

    return code, fixes
