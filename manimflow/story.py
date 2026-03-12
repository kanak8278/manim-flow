"""Story generation engine - turns a question/equation into a narrative script."""

import anthropic
import json

STORY_SYSTEM_PROMPT = """You are a world-class educational content creator, combining the visual storytelling of 3Blue1Brown with the narrative clarity of Feynman.

Your job: Given a math or physics question/equation, create a compelling 90-second explainer video script.

RULES:
1. HOOK (0-10s): Start with something surprising, a question, or a visual that grabs attention. Never start with "Today we'll learn..."
2. SETUP (10-30s): Introduce the concept with intuition, not formalism. Use analogies.
3. BUILD (30-60s): Progressive revelation. Show the math visually, building complexity step by step.
4. CLIMAX (60-80s): The "aha!" moment. Everything clicks together.
5. RESOLVE (80-90s): Clean summary, leave them thinking.

CONSTRAINTS:
- Total duration: ~90 seconds (short, punchy)
- Each scene must be visually interesting (no walls of text)
- Max 3-4 sentences of text on screen at any point
- Use color to encode meaning consistently
- Build complexity progressively — never dump everything at once

OUTPUT FORMAT: Return valid JSON with this exact structure:
{
  "title": "Video title (catchy, short)",
  "hook_question": "The opening hook question/statement",
  "scenes": [
    {
      "id": 1,
      "name": "scene_name",
      "duration_seconds": 10,
      "narration": "What would be spoken (for future voiceover)",
      "visual_description": "Detailed description of what appears on screen",
      "animations": [
        {
          "type": "text|equation|curve|transform|fadeout|axes|highlight|wait",
          "content": "The actual content",
          "position": "UP*2|CENTER|DOWN*1",
          "color": "WHITE|BLUE|etc",
          "font_size": 36,
          "run_time": 2,
          "details": {}
        }
      ],
      "teaching_goal": "What the viewer should understand after this scene"
    }
  ],
  "color_scheme": {
    "primary": "BLUE",
    "secondary": "GREEN",
    "accent": "YELLOW",
    "highlight": "RED"
  },
  "math_components": {
    "equations": ["list of key equations"],
    "variables": {"var": "meaning"},
    "key_insight": "The core aha moment"
  }
}

IMPORTANT: Every scene must have concrete, implementable animation instructions. Be specific about positions, colors, sizes, and timing. Think about what a Manim programmer needs to implement each frame."""


def generate_story(topic: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Generate a story script from a topic/question/equation."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=STORY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Create an engaging 90-second explainer video script for:\n\n{topic}\n\nMake it visually stunning and intellectually satisfying. Focus on building intuition, not just showing formulas."
            }
        ]
    )

    response_text = message.content[0].text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    return json.loads(response_text.strip())


def refine_story(story: dict, feedback: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Refine a story based on feedback."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=STORY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here's a video script that needs improvement:\n\n{json.dumps(story, indent=2)}\n\nFeedback: {feedback}\n\nReturn the improved version in the same JSON format."
            }
        ]
    )

    response_text = message.content[0].text
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    return json.loads(response_text.strip())
