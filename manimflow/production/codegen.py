"""Manim code generation engine - turns a story script into working Manim code."""

import logging

from ..core.agent import Agent, extract_code
from ..reference.manim_reference import MANIM_API_REFERENCE
from ..reference.transitions import get_transition_guide
from ..reference.domain_knowledge import get_full_design_knowledge
from ..knowledge.tool import get_knowledge_system_context

logger = logging.getLogger(__name__)

_TECHNICAL_RULES = r"""
## TECHNICAL RULES (violations = crash)

1. Imports:
   from manim import *
   from manim_voiceover import VoiceoverScene
   from manimflow.core.edge_tts_service import EdgeTTSService
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

_BASE_SYSTEM_PROMPT = (
    "You are an expert educational animator. You create 3Blue1Brown-style videos.\n"
    "Every shape must MEAN something. No decorative geometry.\n"
    "Use labeled concept cards, arrows, and diagrams — not random shapes.\n\n"
    + MANIM_API_REFERENCE
    + "\n"
    + _TECHNICAL_RULES
    + "\n"
    + get_full_design_knowledge()
    + "\n"
    + get_transition_guide()
)

# Without knowledge tool (backward compat for call_llm path)
CODEGEN_SYSTEM_PROMPT = (
    _BASE_SYSTEM_PROMPT + "\nReturn ONLY Python code. No markdown.\n"
)


def _build_codegen_system_prompt() -> str:
    """Build system prompt with knowledge base context."""
    knowledge_ctx = get_knowledge_system_context()
    return (
        _BASE_SYSTEM_PROMPT
        + "\n"
        + knowledge_ctx
        + "\nSearch the knowledge base for relevant patterns BEFORE writing code."
        "\nReturn ONLY Python code. No markdown.\n"
    )


async def generate_manim_code(story: dict) -> str:
    """Generate Manim code from screenplay specs + visual story context.

    The screenplay is the PRIMARY source — structured shots with elements,
    animations, narration with bookmarks. The visual story provides creative
    context for understanding intent.
    """
    target_duration = story.get("duration_target", 120)
    title = story.get("title", "")
    screenplay_context = story.get("_screenplay_context", "")
    visual_story = story.get("_visual_story", "")

    # Screenplay is the spec, visual story is context
    user_prompt = f"TITLE: {title}\nTARGET DURATION: ~{target_duration}s\n\n"

    if screenplay_context:
        user_prompt += (
            f"{screenplay_context}\n\n"
            f"Implement EXACTLY as specified above. Each shot becomes a "
            f"`with self.voiceover(text=...)` block. Use the narration text "
            f"(including the <bookmark> tags) from each shot as the voiceover text. "
            f"Use self.wait_until_bookmark() to sync animations to narration.\n\n"
        )

    if visual_story:
        user_prompt += (
            f"VISUAL STORY (for creative context — the screenplay above is the spec):\n"
            f"{visual_story}\n\n"
        )

    user_prompt += "Return ONLY Python code. No markdown."

    agent = Agent(system_prompt=_build_codegen_system_prompt())
    agent.add_user_message(user_prompt)
    content, _, _ = await agent.call()
    return extract_code(Agent.extract_text(content))


async def fix_manim_code(code: str, error: str) -> str:
    """Fix broken Manim code."""
    system = (
        _build_codegen_system_prompt()
        + "\n\nFix the broken code. Return ONLY complete Python."
    )
    user_prompt = (
        "Fix:\n```python\n" + code + "\n```\nERROR:\n" + error + "\n\nReturn ONLY code."
    )

    agent = Agent(system_prompt=system)
    agent.add_user_message(user_prompt)
    content, _, _ = await agent.call()
    return extract_code(Agent.extract_text(content))
