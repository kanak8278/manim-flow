"""Manim code generation engine - turns a story script into working Manim code."""

import json
from .llm import call_llm, extract_code
from .manim_reference import MANIM_API_REFERENCE
from .transitions import get_transition_guide

_RULES = r"""
RULES (follow exactly — violations = broken video):

1. Import: `from manim import *` and `import numpy as np`
2. Class: `GeneratedScene(MovingCameraScene)` with `def construct(self):`
   NOTE: Use MovingCameraScene, NOT Scene. This enables camera zoom/pan.
3. Background: `self.camera.background_color = BLACK`
4. NO MathTex. Use Text() for everything including math. Write "pi*r^2" not LaTeX.
5. rate_func: ONLY use smooth, linear, rush_into, rush_from, there_and_back
6. For points: np.array([x, y, 0])

TEXT RULES:
- FadeOut ALL elements at end of each scene section before starting next
- Keep ALL text within y=[-3, 3]. Title at UP*2.5, content at ORIGIN, labels at DOWN*2
- Minimum 1.2 units vertical gap between text
- Long text (>30 chars): use font_size 24 or break into lines
- USE THE FULL SCREEN. Center content vertically. Don't leave 80% of screen black.
  Put title at UP*2, main visual at ORIGIN, explanation at DOWN*2.
- NEVER use Cross() — it renders as an ugly grey box. Use red Line() instead.
- NEVER use special characters, bullets, or symbols in Text(). ASCII only.
  BAD: "✓", "•", "→", "★", "▪", emojis
  GOOD: "YES", "-", "->", "*"
  Non-ASCII characters render as GREY BOXES in Manim's default font.
- When placing text near shapes (circles, graphs), ensure text is ABOVE or BELOW
  the shape, NOT overlapping it. Visual elements and text must not share space.
- When using VGroup with many items (>10 dots, people icons), keep them SMALL
  and in a dedicated area. Don't let them spread across the whole screen.

QUALITY RULES (the difference between a 6/10 and 8+/10 video):
- EVERY scene needs shapes/curves/arrows, not just text
- Use Transform() to morph between related equations (at least 3 per video)
- Use Indicate() or Circumscribe() for emphasis (at least 2 per video)
- Use VGroup().arrange() for clean multi-element layouts
- wait(1.5-2) between key concepts, wait(0.5) between quick steps
- End with dramatic final scene: scale up, gradient, or rotation
- Use .set_color_by_gradient() for titles

CAMERA (use at least 2 camera moves per video):
- Zoom INTO key equations/diagrams when explaining details:
  self.play(self.camera.frame.animate.scale(0.6).move_to(element), run_time=2)
- Zoom OUT to show the big picture after zooming in:
  self.play(Restore(self.camera.frame), run_time=1.5)
- Save camera state at start: self.camera.frame.save_state()
- Always Restore() before final scene so ending looks clean
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

    # Build per-scene timing budget if audio durations are available
    timing_instructions = _build_timing_instructions(story)

    user_prompt = (
        f"Generate a complete Manim scene (~{target_duration}s) for this story:\n\n"
        + json.dumps(story, indent=2)
        + timing_instructions
        + "\n\nCRITICAL: Every scene must have visual elements (shapes, curves, diagrams) "
        "not just text. FadeOut everything between scenes. Use Transform() for equation "
        "progression. No MathTex — use Text() only. Return ONLY Python code."
    )

    response = call_llm(CODEGEN_SYSTEM_PROMPT, user_prompt)
    return extract_code(response)


def _build_timing_instructions(story: dict) -> str:
    """Build explicit per-scene timing budgets from audio durations.

    This is critical for audio-video sync. Without it, the LLM generates
    animations that run in 80s while the voiceover is 120s.
    """
    scenes = story.get("scenes", [])
    has_audio = any(s.get("audio_duration") for s in scenes)

    if not has_audio:
        return ""

    lines = [
        "\n\n## TIMING BUDGET (CRITICAL — video must match voiceover duration)",
        "Each scene has a voiceover narration. The animation MUST fill the same duration.",
        "If a scene has audio_duration=15s, your animations + waits for that scene MUST total ~15s.",
        "",
        "PER-SCENE TIMING:",
    ]

    total = 0
    for scene in scenes:
        audio_dur = scene.get("audio_duration", 0)
        if not audio_dur:
            continue
        name = scene.get("name", "scene")
        total += audio_dur

        # Calculate suggested breakdown
        anim_time = min(audio_dur * 0.6, audio_dur - 3)  # 60% for animations
        wait_time = audio_dur - anim_time  # Rest for waits/pauses

        lines.append(
            f"  Scene '{name}': MUST be {audio_dur:.0f}s total"
            f" (suggest: {anim_time:.0f}s animations + {wait_time:.0f}s waits)"
        )

    lines.append(f"\n  TOTAL VIDEO MUST BE: ~{total:.0f}s")
    lines.append("")
    lines.append("HOW TO HIT THE TIMING:")
    lines.append("- Add `self.wait(2)` or `self.wait(3)` between animations to fill time")
    lines.append("- Use longer run_time values: run_time=3 instead of run_time=1")
    lines.append("- Add a comment `# Scene total: ~Xs` at the end of each scene section")
    lines.append("- If a scene feels too short, add more visual detail or longer pauses")
    lines.append("- NEVER rush through content — the viewer needs time to absorb")

    return "\n".join(lines)


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
