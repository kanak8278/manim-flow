"""Story generation engine - turns a question/equation into a narrative script."""

from .llm import call_llm, extract_json

# Duration presets — think like a content creator
DURATION_PRESETS = {
    "short": {
        "seconds": 60,
        "label": "60s TikTok/Reel",
        "structure": """
STRUCTURE (60 seconds total):
1. HOOK (0-8s): One punchy question or surprising visual. Maximum impact, minimum words.
2. CORE (8-40s): ONE concept explained visually. No detours. Build to the insight.
3. REVEAL (40-55s): The "aha!" — show why it works/matters.
4. TAG (55-60s): One-line takeaway. Leave them wanting more.

CONSTRAINTS:
- Max 4 scenes
- Max 2 text elements on screen at once
- Every second must be visual — no lecture slides
""",
    },
    "standard": {
        "seconds": 120,
        "label": "2-minute explainer",
        "structure": """
STRUCTURE (120 seconds total):
1. HOOK (0-10s): Surprising question or paradox that creates curiosity.
2. SETUP (10-30s): Introduce the concept with intuition and analogy. No formalism yet.
3. BUILD (30-70s): Progressive revelation. Show the math visually, step by step.
4. CLIMAX (70-100s): The "aha!" moment. Everything clicks together.
5. RESOLVE (100-120s): Clean summary, connect to bigger picture.

CONSTRAINTS:
- 5-7 scenes
- Max 3 text elements on screen at once
- Use analogies before equations
""",
    },
    "deep": {
        "seconds": 300,
        "label": "5-minute deep dive",
        "structure": """
STRUCTURE (300 seconds / 5 minutes total):
1. HOOK (0-15s): Compelling question or real-world mystery.
2. CONTEXT (15-45s): Why this matters. Historical context or real-world application.
3. INTUITION (45-90s): Build understanding with analogies, visual metaphors. No math yet.
4. FOUNDATION (90-150s): Introduce the math gradually. Each equation earns its place.
5. BUILD (150-210s): Progressive complexity. Show how pieces fit together.
6. CLIMAX (210-250s): The full picture comes together. "Aha!" moment.
7. EXTENSIONS (250-280s): What this connects to. Surprising applications or consequences.
8. RESOLVE (280-300s): Elegant summary. Leave them thinking deeper.

CONSTRAINTS:
- 8-12 scenes
- Can show 3-4 text elements at once but clean between sections
- Use history, analogies, multiple visual approaches
- Each major concept gets its own scene with breathing room
""",
    },
    "long": {
        "seconds": 480,
        "label": "8-minute comprehensive",
        "structure": """
STRUCTURE (480 seconds / 8 minutes total):
1. HOOK (0-20s): Start with the punchline — show the beautiful result first.
2. MYSTERY (20-50s): Create tension. Why is this true? What's going on?
3. HISTORY (50-90s): Who discovered this? What problem were they solving? Brief human story.
4. INTUITION (90-150s): Build understanding from scratch. Multiple analogies.
5. FOUNDATION (150-210s): Gentle math introduction. Visual first, symbolic second.
6. BUILD Part 1 (210-270s): First major proof/derivation step. Step by step.
7. BUILD Part 2 (270-330s): Second major step. Increasing complexity.
8. CLIMAX (330-390s): Everything comes together. The proof completes or the formula emerges.
9. APPLICATIONS (390-430s): Real-world uses. Why this matters beyond math.
10. RESOLVE (430-480s): Return to the opening. New perspective on the original question.

CONSTRAINTS:
- 10-15 scenes
- Rich visual variety — curves, transforms, diagrams, annotations
- Include historical/biographical elements where relevant
- Multiple "mini-aha" moments building to the main revelation
- Pacing: faster in familiar territory, slower on new concepts
""",
    },
}


def _get_duration_preset(duration_seconds: int) -> dict:
    """Pick the best preset for a given duration target."""
    if duration_seconds <= 75:
        return DURATION_PRESETS["short"]
    elif duration_seconds <= 150:
        return DURATION_PRESETS["standard"]
    elif duration_seconds <= 360:
        return DURATION_PRESETS["deep"]
    else:
        return DURATION_PRESETS["long"]


STORY_SYSTEM_PROMPT_TEMPLATE = """You are a world-class educational content creator, combining the visual storytelling of 3Blue1Brown with the narrative clarity of Feynman.

Your job: Given a math or physics question/equation, create a compelling video script.

{structure}

VISUAL RULES:
- Each scene must be visually interesting (no walls of text)
- Max text on screen: see constraints above
- Use color to encode meaning consistently (same concept = same color throughout)
- Build complexity progressively — never dump everything at once
- EVERY text/equation must have a specific position (UP*2, DOWN*1, etc.)
- EVERY text must eventually be FadeOut'd before new content in same area
- Screen bounds: x=[-7,7], y=[-4,4]. Keep all content within y=[-3.5,3.5]

OUTPUT FORMAT: Return valid JSON:
{{
  "title": "Video title (catchy, short)",
  "duration_target": {duration},
  "hook_question": "The opening hook question/statement",
  "scenes": [
    {{
      "id": 1,
      "name": "scene_name",
      "duration_seconds": 10,
      "narration": "What would be spoken (for future voiceover)",
      "visual_description": "Detailed description of what appears on screen",
      "animations": [
        {{
          "type": "text|equation|curve|transform|fadeout|axes|highlight|wait",
          "content": "The actual content",
          "position": "UP*2|CENTER|DOWN*1",
          "color": "WHITE|BLUE|etc",
          "font_size": 36,
          "run_time": 2
        }}
      ],
      "teaching_goal": "What the viewer should understand after this scene"
    }}
  ],
  "color_scheme": {{
    "primary": "BLUE",
    "secondary": "GREEN",
    "accent": "YELLOW",
    "highlight": "RED"
  }},
  "math_components": {{
    "equations": ["list of key equations"],
    "variables": {{"var": "meaning"}},
    "key_insight": "The core aha moment"
  }}
}}

CRITICAL: Every scene must have concrete, implementable animation instructions.
Return ONLY the JSON. No other text."""


def generate_story(topic: str, duration_seconds: int = 120) -> dict:
    """Generate a story script from a topic/question/equation.

    Args:
        topic: The math/physics question or concept
        duration_seconds: Target video duration (30-480s)
            30-75s  = short TikTok/Reel style
            75-150s = standard 2-min explainer
            150-360s = 5-min deep dive
            360-480s = 8-min comprehensive
    """
    preset = _get_duration_preset(duration_seconds)

    system_prompt = STORY_SYSTEM_PROMPT_TEMPLATE.format(
        structure=preset["structure"],
        duration=duration_seconds,
    )

    user_prompt = (
        f"Create an engaging {preset['label']} video script for:\n\n"
        f"{topic}\n\n"
        f"Target duration: ~{duration_seconds} seconds.\n"
        f"Make it visually stunning and intellectually satisfying. "
        f"Focus on building intuition, not just showing formulas.\n\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(system_prompt, user_prompt)
    return extract_json(response)
