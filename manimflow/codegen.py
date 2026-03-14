"""Manim code generation engine - turns a story script into working Manim code."""

import json
from .llm import call_llm, extract_code
from .manim_reference import MANIM_API_REFERENCE
from .transitions import get_transition_guide
from .domain_knowledge import get_full_design_knowledge

_TECHNICAL_RULES = r"""
## TECHNICAL RULES (violations = crash)

1. Imports:
   from manim import *
   from manim_voiceover import VoiceoverScene
   from manimflow.edge_tts_service import EdgeTTSService
   import numpy as np

2. Class: `GeneratedScene(VoiceoverScene)` with `def construct(self):`
3. First line: self.set_speech_service(EdgeTTSService(transcription_model="base"))
4. Background: self.camera.background_color = BLACK
5. NO MathTex — use Text() for everything including math
6. rate_func: ONLY smooth, linear, rush_into, rush_from, there_and_back
7. ASCII only in Text() — no special chars (grey boxes)

## VOICEOVER SYNC
Wrap each scene in `with self.voiceover(text=...) as tracker:`
Use <bookmark mark="X"/> tags to sync animations to words.
Always start with <bookmark mark="start"/> at the beginning.
Use self.wait_until_bookmark("X") to wait for that word.

## MANIM CODE PATTERNS

Concept Card:
```python
def make_card(text, color, width=3, height=1.2):
    rect = RoundedRectangle(width=width, height=height, corner_radius=0.2,
                            color=color, fill_color=color, fill_opacity=0.15)
    label = Text(text, font_size=24, color=WHITE).move_to(rect.get_center())
    return VGroup(rect, label)
```

Flow Diagram:
```python
cards = [make_card(name, color) for name, color in items]
group = VGroup(*cards).arrange(RIGHT, buff=1.0)
arrows = [Arrow(cards[i].get_right(), cards[i+1].get_left(), buff=0.1)
          for i in range(len(cards)-1)]
```

Hierarchy:
```python
parent = make_card("Parent", BLUE).move_to(UP * 2)
children = VGroup(*[make_card(n, GREEN) for n in names]).arrange(RIGHT, buff=0.8).move_to(DOWN * 0.5)
lines = [Line(parent.get_bottom(), c.get_top(), buff=0.1) for c in children]
```
"""

CODEGEN_SYSTEM_PROMPT = (
    "You are an expert educational animator. You create 3Blue1Brown-style videos.\n"
    "Every shape must MEAN something. No decorative geometry.\n"
    "Use labeled concept cards, arrows, and diagrams — not random shapes.\n\n"
    + MANIM_API_REFERENCE
    + "\n" + _TECHNICAL_RULES
    + "\n" + get_full_design_knowledge()
    + "\n" + get_transition_guide()
    + "\nReturn ONLY Python code. No markdown.\n"
)


def generate_manim_code(story: dict) -> str:
    """Generate Manim code with voiceover sync from a story script."""
    target_duration = story.get("duration_target", 120)

    # Include design system if available
    design_context = story.pop("_design_context", "")

    # Build narration hints
    scene_hints = []
    for scene in story.get("scenes", []):
        if isinstance(scene, dict):
            name = scene.get("name", "scene")
            narration = scene.get("narration", "")
            visual = scene.get("visual", scene.get("visual_description", ""))
            if isinstance(visual, str):
                visual = visual[:80]
            scene_hints.append(f"  Scene '{name}': narration=\"{narration[:100]}\" visual=\"{visual}\"")

    user_prompt = (
        f"Generate a VoiceoverScene (~{target_duration}s) for this story:\n\n"
        + json.dumps(story, indent=2)
    )

    if design_context:
        user_prompt += f"\n\n{design_context}"

    user_prompt += (
        "\n\nSCENE NARRATION:\n" + "\n".join(scene_hints)
        + "\n\nCRITICAL REMINDERS:"
        "\n- Use VoiceoverScene with EdgeTTSService(transcription_model='base')"
        "\n- Every shape must be a labeled concept card or diagram element"
        "\n- Use make_card() pattern for entities, Arrow() for relationships"
        "\n- Maximum 4 elements on screen at once"
        "\n- FadeOut everything between scenes"
        "\n- Progressive disclosure: one element at a time"
        "\n- ASCII only, no MathTex"
        "\n\nReturn ONLY Python code."
    )

    response = call_llm(CODEGEN_SYSTEM_PROMPT, user_prompt)
    return extract_code(response)


def fix_manim_code(code: str, error: str) -> str:
    """Fix broken Manim code."""
    system = CODEGEN_SYSTEM_PROMPT + "\n\nFix the broken code. Return ONLY complete Python."
    user_prompt = "Fix:\n```python\n" + code + "\n```\nERROR:\n" + error + "\n\nReturn ONLY code."
    response = call_llm(system, user_prompt)
    return extract_code(response)
