"""Manim code generation engine - turns a story script into working Manim code."""

import json
from .llm import call_llm, extract_code
from .manim_reference import MANIM_API_REFERENCE

_RULES = r"""
CRITICAL RULES (violations cause crashes):
1. Always import: `from manim import *` and `import numpy as np`
2. Class must be named `GeneratedScene` and extend `Scene`
3. All code goes in `def construct(self):`
4. Set `self.camera.background_color = BLACK` first
5. Always FadeOut elements before reusing screen space
6. ParametricFunction needs t_range=[start, end, step]
7. Use np.array([x, y, 0]) for points
8. Clean object lifecycle: create -> position -> animate -> fadeout
9. For Transform: source must already be on screen
10. Never use emojis in Text() — use VGroup with separate Text objects
11. MathTex is for PURE MATH ONLY. NEVER use \text{} inside MathTex — it crashes.
    BAD:  MathTex(r"\text{Area} = \pi r^2")  # CRASHES
    GOOD: MathTex(r"\pi r^2")  # Pure math symbols only
    GOOD: Text("Area = ") placed next to MathTex(r"\pi r^2") via VGroup().arrange(RIGHT)
12. Use MathTex for: fractions, integrals, Greek letters, superscripts, summations
    Use Text() for: English words, labels, titles, descriptions

ANIMATION STYLE (3Blue1Brown aesthetic):
- Black background
- Clean, minimal text (font_size 24-36 body, 42-56 titles)
- Smooth animations (1-4s text, 3-6s curves)
- Progressive revelation
- Color-coded elements
- wait() between concepts (1-2s)
- Gradient colors for emphasis

TARGET: ~90 seconds total. Control pacing with run_time and wait().

Return ONLY Python code. No markdown, no explanation.
"""

CODEGEN_SYSTEM_PROMPT = (
    "You are an expert Manim Community Edition programmer who creates beautiful, "
    "educational mathematical animations.\n\n"
    "Your job: Given a structured video script (JSON), generate a complete, working "
    "Manim scene that renders without errors.\n\n"
    + MANIM_API_REFERENCE
    + _RULES
)


def generate_manim_code(story: dict) -> str:
    """Generate Manim code from a story script."""
    target_duration = story.get("duration_target", 120)
    user_prompt = (
        "Generate a complete, working Manim scene for this video script:\n\n"
        + json.dumps(story, indent=2)
        + f"\n\nThe code must render without errors. Target total animation time: "
        f"~{target_duration} seconds. Return ONLY Python code, no markdown."
    )

    response = call_llm(CODEGEN_SYSTEM_PROMPT, user_prompt)
    return extract_code(response)


def fix_manim_code(code: str, error: str) -> str:
    """Fix broken Manim code based on error output."""
    system = (
        CODEGEN_SYSTEM_PROMPT
        + "\n\nYou are fixing broken code. Return ONLY the complete fixed Python "
        "file. No explanations, no markdown."
    )

    user_prompt = (
        "This Manim code has an error. Fix it.\n\nCODE:\n```python\n"
        + code
        + "\n```\n\nERROR:\n```\n"
        + error
        + "\n```\n\nReturn the COMPLETE fixed Python code. Fix ALL issues. "
        "Return ONLY code, no markdown."
    )

    response = call_llm(system, user_prompt)
    return extract_code(response)
