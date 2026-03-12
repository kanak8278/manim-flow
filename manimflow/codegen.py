"""Manim code generation engine - turns a story script into working Manim code."""

import json
from .llm import call_llm, extract_code
from .manim_reference import MANIM_API_REFERENCE
from .transitions import get_transition_guide

_RULES = r"""
RULES (follow exactly — violations = broken video):

1. Import: `from manim import *` and `import numpy as np`
2. Class: `GeneratedScene(Scene)` with `def construct(self):`
3. Background: `self.camera.background_color = BLACK`
4. NO MathTex. Use Text() for everything including math. Write "pi*r^2" not LaTeX.
5. rate_func: ONLY use smooth, linear, rush_into, rush_from, there_and_back
6. For points: np.array([x, y, 0])

TEXT RULES:
- FadeOut ALL elements at end of each scene section before starting next
- Keep ALL text within y=[-3, 3]. Title at UP*2.5, content at ORIGIN, labels at DOWN*2
- Minimum 1.2 units vertical gap between text
- Long text (>30 chars): use font_size 24 or break into lines

QUALITY RULES (the difference between a 6/10 and 8+/10 video):
- EVERY scene needs shapes/curves/arrows, not just text
- Use Transform() to morph between related equations (at least 3 per video)
- Use Indicate() or Circumscribe() for emphasis (at least 2 per video)
- Use VGroup().arrange() for clean multi-element layouts
- wait(1.5-2) between key concepts, wait(0.5) between quick steps
- End with dramatic final scene: scale up, gradient, or rotation
- Use .set_color_by_gradient() for titles
"""

CODEGEN_SYSTEM_PROMPT = (
    "You are an expert Manim animator creating 3Blue1Brown-style videos. "
    "Your code must be VISUAL — shapes, curves, diagrams in every scene. "
    "NOT text slideshows.\n\n"
    + MANIM_API_REFERENCE
    + _RULES
    + "\n" + get_transition_guide()
    + "\nReturn ONLY Python code. No markdown.\n"
)


def generate_manim_code(story: dict) -> str:
    """Generate Manim code from a story script."""
    target_duration = story.get("duration_target", 120)

    user_prompt = (
        f"Generate a complete Manim scene (~{target_duration}s) for this story:\n\n"
        + json.dumps(story, indent=2)
        + "\n\nCRITICAL: Every scene must have visual elements (shapes, curves, diagrams) "
        "not just text. FadeOut everything between scenes. Use Transform() for equation "
        "progression. No MathTex — use Text() only. Return ONLY Python code."
    )

    response = call_llm(CODEGEN_SYSTEM_PROMPT, user_prompt)
    return extract_code(response)


def fix_manim_code(code: str, error: str) -> str:
    """Fix broken Manim code based on error output."""
    system = (
        CODEGEN_SYSTEM_PROMPT
        + "\n\nFix the broken code. Return ONLY the complete fixed Python file."
    )

    user_prompt = (
        "Fix this code:\n\n```python\n" + code + "\n```\n\nERROR:\n" + error
        + "\n\nReturn ONLY the complete fixed code."
    )

    response = call_llm(system, user_prompt)
    return extract_code(response)
