"""Manim code generation engine - turns a story script into working Manim code."""

import json
from .llm import call_llm, extract_code
from .manim_reference import MANIM_API_REFERENCE
from .transitions import get_transition_guide

_RULES = r"""
RULES (follow exactly — violations = broken video):

1. Imports:
   from manim import *
   from manim_voiceover import VoiceoverScene
   from manim_voiceover.services.gtts import GTTSService
   import numpy as np

2. Class: `GeneratedScene(VoiceoverScene)` with `def construct(self):`
3. First line in construct:
   self.set_speech_service(GTTSService(transcription_model="base"))
4. Background: `self.camera.background_color = BLACK`
5. NO MathTex. Use Text() for everything including math.
6. rate_func: ONLY use smooth, linear, rush_into, rush_from, there_and_back
7. ASCII only in Text() — no special chars (they render as grey boxes)

## VOICEOVER SYNC (CRITICAL — this is how audio matches animation)
Wrap each scene's animations in a `with self.voiceover()` block.
Use <bookmark mark="X"/> tags to sync specific animations to specific words.

PATTERN:
```python
with self.voiceover(
    text='Here is <bookmark mark="circle"/>a circle that <bookmark mark="grow"/>grows bigger.'
) as tracker:
    self.wait_until_bookmark("circle")
    self.play(Create(circle), run_time=tracker.time_until_bookmark("grow"))
    self.wait_until_bookmark("grow")
    self.play(circle.animate.scale(2), run_time=2)
```

RULES FOR VOICEOVER BLOCKS:
- Each scene section gets ONE voiceover block with narration text
- Put bookmarks BEFORE the word where the animation should trigger
- Use tracker.duration for animations that should fill the whole narration
- Use tracker.time_until_bookmark("X") for animations between bookmarks
- Keep narration text CONCISE — 2-3 sentences per voiceover block
- Between voiceover blocks, add self.wait(0.5) for breathing room
- FadeOut previous scene elements BEFORE the next voiceover block
- Narration should describe what's visually happening

EXAMPLE SCENE:
```python
# === SCENE 1: Hook ===
title = Text("Why Pi?", font_size=48, color=BLUE).move_to(UP * 2)
circle = Circle(radius=1.5, color=GREEN).move_to(DOWN * 0.5)

with self.voiceover(
    text='<bookmark mark="title"/>Why does every circle hide <bookmark mark="circle"/>the same magical number?'
) as tracker:
    self.wait_until_bookmark("title")
    self.play(Write(title), run_time=1.5)
    self.wait_until_bookmark("circle")
    self.play(Create(circle), run_time=tracker.duration - tracker.get_remaining())

self.wait(0.5)
self.play(FadeOut(title), FadeOut(circle), run_time=1)
```

## TEXT RULES
- FadeOut ALL elements at end of each scene section
- Keep ALL text within y=[-3, 3]
- Minimum 1.2 units vertical gap between text
- Long text (>30 chars): font_size 24 or break into lines
- ASCII only — no emojis, bullets, special chars

## QUALITY RULES
- EVERY scene needs shapes/curves/arrows, not just text
- Use Transform() for equation progression (at least 3 per video)
- Use Indicate() for emphasis (at least 2 per video)
- End with dramatic final scene
"""

CODEGEN_SYSTEM_PROMPT = (
    "You are an expert Manim animator creating 3Blue1Brown-style videos with synchronized voiceover. "
    "Your code uses VoiceoverScene with bookmark-synced narration. "
    "Every scene has visual elements AND narration that plays in sync.\n\n"
    + MANIM_API_REFERENCE
    + _RULES
    + "\n" + get_transition_guide()
    + "\nReturn ONLY Python code. No markdown.\n"
)


def generate_manim_code(story: dict) -> str:
    """Generate Manim code with voiceover sync from a story script."""
    target_duration = story.get("duration_target", 120)

    # Build narration hints per scene
    scene_hints = []
    for scene in story.get("scenes", []):
        name = scene.get("name", "scene")
        narration = scene.get("narration", "")
        visual = scene.get("visual_description", "")[:80]
        scene_hints.append(f"  Scene '{name}': narration=\"{narration[:100]}\" visual=\"{visual}\"")

    user_prompt = (
        f"Generate a complete VoiceoverScene (~{target_duration}s) for this story:\n\n"
        + json.dumps(story, indent=2)
        + "\n\nSCENE NARRATION TO USE:\n" + "\n".join(scene_hints)
        + "\n\nCRITICAL:"
        "\n- Use VoiceoverScene with GTTSService(transcription_model='base')"
        "\n- Wrap each scene in `with self.voiceover(text=...)` with bookmark tags"
        "\n- Narration text comes from the story's 'narration' field for each scene"
        "\n- Add <bookmark mark='X'/> tags at key animation trigger points"
        "\n- FadeOut everything between voiceover blocks"
        "\n- Every scene must have visual elements, not just text"
        "\n- ASCII only in Text() — no special characters"
        "\n\nReturn ONLY Python code."
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
