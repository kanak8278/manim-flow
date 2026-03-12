"""Manim code generation engine - turns a story script into working Manim code."""

import anthropic
import json

CODEGEN_SYSTEM_PROMPT = """You are an expert Manim Community Edition programmer who creates beautiful, educational mathematical animations.

Your job: Given a structured video script (JSON), generate a complete, working Manim scene that renders without errors.

CRITICAL MANIM RULES (violations cause crashes):
1. ONLY use standard Manim colors: RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK, WHITE, GRAY, BLACK, GOLD, DARK_BLUE
   - NEVER use: CYAN, TEAL, MAGENTA, CORAL, INDIGO, VIOLET, LIME, MAROON
   - For custom colors, use hex strings: "#00FFFF", "#008080"
2. Use Text() for regular text, MathTex() for LaTeX math
3. Always FadeOut elements before reusing screen space — no overlapping text
4. ParametricFunction t_range needs [start, end, step] format
5. Use np.array([x, y, 0]) for 3D points (Manim requires z=0 for 2D)
6. VGroup for grouping, .arrange() for layout
7. Never put emojis directly in Text() — use VGroup with separate Text objects
8. Clean object lifecycle: create → position → animate → fadeout
9. For transforms: Transform(source, target) — source must exist on screen

ANIMATION STYLE (3Blue1Brown aesthetic):
- Black background (self.camera.background_color = BLACK)
- Clean, minimal text (font_size 24-36 for body, 42-56 for titles)
- Smooth animations with appropriate run_time (1-4s for text, 3-6s for curves)
- Progressive revelation — never show everything at once
- Color-coded elements that maintain meaning throughout
- Strategic use of wait() for comprehension (1-2s between concepts)
- Gradient colors for emphasis: .set_color_by_gradient(COLOR1, COLOR2)

STRUCTURE:
```python
from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        # ... scenes follow ...
```

TARGET: ~90 seconds total video. Use run_time and wait() to control pacing.
- Hook: 10s
- Setup: 20s
- Build: 30s
- Climax: 20s
- Resolve: 10s

Return ONLY the Python code. No markdown, no explanation. Just valid Python that can be saved to a .py file and rendered with `manim -pqh file.py GeneratedScene`."""


def generate_manim_code(story: dict, model: str = "claude-sonnet-4-20250514") -> str:
    """Generate Manim code from a story script."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=CODEGEN_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Generate a complete, working Manim scene for this video script:\n\n{json.dumps(story, indent=2)}\n\nThe code must render without errors. Use only standard Manim colors. Keep total animation time around 90 seconds."
            }
        ]
    )

    code = message.content[0].text

    # Strip markdown if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]

    return code.strip()


def fix_manim_code(code: str, error: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Fix broken Manim code based on error output."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=CODEGEN_SYSTEM_PROMPT + "\n\nYou are fixing broken code. Return ONLY the complete fixed Python file. No explanations.",
        messages=[
            {
                "role": "user",
                "content": f"This Manim code has an error. Fix it.\n\nCODE:\n```python\n{code}\n```\n\nERROR:\n```\n{error}\n```\n\nReturn the complete fixed Python code. Fix ALL issues, not just the first one."
            }
        ]
    )

    fixed = message.content[0].text
    if "```python" in fixed:
        fixed = fixed.split("```python")[1].split("```")[0]
    elif "```" in fixed:
        fixed = fixed.split("```")[1].split("```")[0]

    return fixed.strip()
