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
5. ParametricFunction needs t_range=[start, end, step]
6. Use np.array([x, y, 0]) for points
7. For Transform: source must already be on screen via self.play() or self.add()
8. Never use emojis in Text() — use VGroup with separate Text objects
9. MathTex is for PURE MATH ONLY. NEVER use \text{} inside MathTex — it crashes.
10. For rate_func: use smooth, linear, rush_into, rush_from, there_and_back ONLY.
    DO NOT use ease_in_cubic, ease_out_cubic etc. — they don't exist as bare names.

## TEXT MANAGEMENT (THE #1 MOST IMPORTANT RULE)
Every scene transition MUST follow this pattern:
```python
# === SCENE N ===
# 1. Create scene elements
title = Text("Title", font_size=42, color=BLUE).move_to(UP * 3)
content = Text("Content", font_size=28).move_to(UP * 1)

# 2. Animate in
self.play(Write(title), run_time=1.5)
self.play(Write(content), run_time=2)
self.wait(2)

# 3. CLEAN UP EVERYTHING before next scene
self.play(FadeOut(title), FadeOut(content), run_time=1)

# === SCENE N+1 ===
# Now the screen is clean for new content
```

MANDATORY: Before starting any new scene/section, FadeOut ALL text and labels from the
previous section. Use `self.play(*[FadeOut(mob) for mob in self.mobjects])` if unsure.

## SCREEN LAYOUT
- Screen bounds: x=[-7,7], y=[-4,4]. Keep text within y=[-3.5, 3.5]
- Title position: UP * 3 (max UP * 3.2)
- Subtitle: UP * 2
- Main content: ORIGIN to UP * 1
- Labels/notes: DOWN * 2 to DOWN * 3
- NEVER put two text elements at the same vertical position
- Minimum vertical gap between text: 1.0 Manim units
- Long text (>40 chars): use font_size 22-26 or split into two lines

## ANIMATION STYLE (3Blue1Brown aesthetic)
- Black background
- Clean, minimal text (font_size 24-36 body, 42-56 titles)
- Smooth animations (1-3s text, 3-6s curves)
- Progressive revelation — never show everything at once
- Color-coded elements that stay consistent
- wait(1.5) between concepts for comprehension
- Gradient colors for emphasis: .set_color_by_gradient(COLOR1, COLOR2)
- Use Indicate() or Flash() to draw attention to key moments

## VISUAL VARIETY (CRITICAL — don't make text-only slideshows!)
Your animation MUST include visual elements beyond text. For EVERY scene, include at least
ONE of these visual patterns:

1. GEOMETRIC SHAPES: Circle, Rectangle, Arrow, Line, Dot for diagrams
   ```python
   satellite = Circle(radius=0.3, color=BLUE, fill_opacity=0.8).move_to(UP*2+RIGHT*3)
   earth = Circle(radius=1, color=GREEN, fill_opacity=0.5).move_to(ORIGIN)
   signal = DashedLine(satellite, earth, color=YELLOW)
   ```

2. ANIMATED MOTION: Objects that move, rotate, scale
   ```python
   self.play(satellite.animate.move_to(UP*2+LEFT*3), run_time=3)
   self.play(Rotate(gear, PI/2), run_time=2)
   ```

3. FUNCTION GRAPHS: Plot mathematical relationships
   ```python
   axes = Axes(x_range=[0, 10], y_range=[0, 5], x_length=8, y_length=4)
   graph = axes.plot(lambda x: x**2 / 20, color=RED)
   self.play(Create(axes), Create(graph), run_time=3)
   ```

4. VALUE TRACKERS: Animate changing numbers
   ```python
   tracker = ValueTracker(0)
   number = always_redraw(lambda: DecimalNumber(tracker.get_value()).move_to(UP))
   self.play(tracker.animate.set_value(100), run_time=4)
   ```

5. ANNOTATIONS: Braces, arrows, labels that explain diagrams
   ```python
   brace = Brace(rectangle, DOWN, color=YELLOW)
   label = brace.get_text("width = 5")
   ```

6. TRANSFORMS: Morph between shapes to show relationships
   ```python
   self.play(Transform(circle, rectangle), run_time=3)
   ```

RULE: If a scene has more than 2 Text() objects and no shapes/curves/diagrams, you are
making a slideshow, not an animation. Add visual elements.

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
        f"~{target_duration} seconds.\n\n"
        "CRITICAL REMINDERS:\n"
        "- FadeOut ALL text before each new scene/section\n"
        "- Keep all text within y=[-3.5, 3.5] screen bounds\n"
        "- Never overlap text elements at same vertical position\n"
        "- Use smooth or linear for rate_func (NOT ease_in_cubic etc.)\n"
        "- No \\text{} in MathTex\n"
        "- If scenes have 'audio_duration', match total run_time + wait() to that duration\n"
        "  Use self.wait() at end of each scene section to fill remaining time\n\n"
        "Return ONLY Python code, no markdown."
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
