"""Screenplay — detailed scene-by-scene visual script.

Like a movie screenplay: every moment specifies what's on screen, what's said,
what the viewer feels, and how it connects to the next moment.

The code generator receives this and has NO creative decisions left —
just implementation.

Inspired by:
- Kurzgesagt's storyboard process (200 panels per video)
- Professional storyboard format (shot, action, dialogue, camera, duration)
- 3Blue1Brown's "each scene is a visual idea that teaches one thing"
"""

from dataclasses import dataclass, field
from .agent import Agent, call_llm, extract_json
from .domain_knowledge import get_full_design_knowledge, VISUAL_VOCABULARY
from .knowledge.tool import TOOLS, get_knowledge_system_context


@dataclass
class Shot:
    """One visual moment in the screenplay."""
    id: int
    duration: float  # seconds
    narration: str  # exact words spoken
    screen_elements: list[dict]  # what's visible: name, type, position, color, size, label
    animations: list[dict]  # what happens: action, target, style, run_time
    camera: str  # static, zoom_in, zoom_out, pan
    teaching_point: str  # what the viewer should understand
    emotional_beat: str  # what the viewer feels
    transition_to_next: str  # how this connects to the next shot


@dataclass
class Screenplay:
    """Complete visual screenplay for a video."""
    title: str
    shots: list[Shot]
    color_assignments: dict  # concept → color (consistent throughout)
    visual_metaphors: dict  # abstract concept → concrete visual representation


SCREENPLAY_PROMPT = """You are a visual screenplay writer for educational animations.
You write screenplays so detailed that a code generator can produce the animation
without making any creative decisions.

""" + get_full_design_knowledge() + """

""" + VISUAL_VOCABULARY + """

For each SHOT (moment in the video), you must specify:
1. EXACT narration text (what the narrator says)
2. EVERY element on screen: name, type (card/circle/arrow/axes/line/text), position, color, size, label
3. EVERY animation: what appears, disappears, transforms, and how
4. Camera action: static, zoom into something, zoom out
5. What the viewer should learn from this shot
6. How this connects to the next shot

RULES:
- Use the CONCEPT CARD pattern for entities (RoundedRectangle + Text label inside)
- Use ARROWS for relationships between concepts
- Use AXES + GRAPH for mathematical functions
- Maximum 4 elements on screen at once
- Every shape must have a text label
- Colors must be consistent (assign once, use everywhere)
- Positions must be specific: UP*2, LEFT*3, ORIGIN, etc.
- Sizes must be specific: width=3.5, height=1.5, radius=1.5, font_size=28

Return JSON:
{
  "title": "video title",
  "color_assignments": {"concept_name": "#hex_color", ...},
  "visual_metaphors": {"abstract_concept": "concrete_visual_description", ...},
  "shots": [
    {
      "id": 1,
      "duration": 15,
      "narration": "exact words spoken",
      "screen_elements": [
        {
          "name": "supreme_court",
          "type": "card",
          "label": "Supreme Court",
          "position": "UP * 2",
          "color": "#e74c3c",
          "width": 3.5,
          "height": 1.5
        },
        {
          "name": "title_text",
          "type": "text",
          "label": "How Courts Work",
          "position": "UP * 3",
          "color": "WHITE",
          "font_size": 42
        }
      ],
      "animations": [
        {"action": "write", "target": "title_text", "run_time": 1.5},
        {"action": "create", "target": "supreme_court", "run_time": 2.0},
        {"action": "indicate", "target": "supreme_court", "run_time": 0.5}
      ],
      "camera": "static",
      "teaching_point": "The Supreme Court is the highest authority",
      "emotional_beat": "awe at the system's structure",
      "transition_to_next": "fade out all, introduce the lower courts"
    }
  ]
}"""


async def write_screenplay(story: dict, topic: str) -> Screenplay:
    """Convert an approved story into a detailed visual screenplay."""
    scenes_text = ""
    for i, scene in enumerate(story.get("scenes", [])):
        if isinstance(scene, dict):
            scenes_text += (
                f"\nScene {i+1}: {scene.get('name', '')}\n"
                f"  Narration: \"{scene.get('narration', '')}\"\n"
                f"  Visual idea: {scene.get('visual', '')}\n"
                f"  Teaching: {scene.get('teaching_goal', '')}\n"
                f"  Emotion: {scene.get('emotion', '')}\n"
            )

    user_prompt = (
        f"Write a detailed visual screenplay for this educational video:\n\n"
        f"TOPIC: {topic}\n"
        f"TITLE: {story.get('title', topic)}\n\n"
        f"APPROVED STORY:\n{scenes_text}\n\n"
        f"Write 8-12 shots. Each shot must specify EVERY element on screen "
        f"with exact type, position, color, size, and label.\n"
        f"Use concept cards (RoundedRectangle + Text) for entities.\n"
        f"Use arrows for relationships.\n"
        f"Maximum 4 elements per shot.\n"
        f"Return ONLY valid JSON."
    )

    system = SCREENPLAY_PROMPT + "\n\n" + get_knowledge_system_context()
    agent = Agent(system_prompt=system, tools=TOOLS)
    agent.add_user_message(user_prompt)
    response = await agent.run(max_tool_rounds=2)
    data = extract_json(response)

    shots = []
    for s in data.get("shots", []):
        shots.append(Shot(
            id=s.get("id", 0),
            duration=s.get("duration", 15),
            narration=s.get("narration", ""),
            screen_elements=s.get("screen_elements", []),
            animations=s.get("animations", []),
            camera=s.get("camera", "static"),
            teaching_point=s.get("teaching_point", ""),
            emotional_beat=s.get("emotional_beat", ""),
            transition_to_next=s.get("transition_to_next", ""),
        ))

    return Screenplay(
        title=data.get("title", story.get("title", topic)),
        shots=shots,
        color_assignments=data.get("color_assignments", {}),
        visual_metaphors=data.get("visual_metaphors", {}),
    )


def screenplay_to_codegen_prompt(sp: Screenplay) -> str:
    """Convert a screenplay into a detailed prompt for the code generator."""
    lines = [
        "## VISUAL SCREENPLAY (implement EXACTLY as specified)\n",
        f"Title: {sp.title}",
        f"\nCOLOR ASSIGNMENTS (use these EXACT colors):",
    ]
    for concept, color in sp.color_assignments.items():
        lines.append(f"  {concept}: \"{color}\"")

    if sp.visual_metaphors:
        lines.append(f"\nVISUAL METAPHORS:")
        for abstract, concrete in sp.visual_metaphors.items():
            lines.append(f"  {abstract} → {concrete}")

    lines.append(f"\nSHOTS ({len(sp.shots)} total):")

    for shot in sp.shots:
        lines.append(f"\n--- SHOT {shot.id} ({shot.duration}s) ---")
        lines.append(f"Narration: \"{shot.narration}\"")
        lines.append(f"Camera: {shot.camera}")
        lines.append(f"Teaching: {shot.teaching_point}")
        lines.append(f"Transition: {shot.transition_to_next}")

        lines.append("Elements:")
        for elem in shot.screen_elements:
            name = elem.get("name", "?")
            etype = elem.get("type", "?")
            label = elem.get("label", "")
            pos = elem.get("position", "ORIGIN")
            color = elem.get("color", "WHITE")
            w = elem.get("width", "")
            h = elem.get("height", "")
            fs = elem.get("font_size", "")
            size_info = f"width={w}, height={h}" if w else f"font_size={fs}" if fs else ""
            lines.append(f"  {name}: {etype} \"{label}\" at {pos} color={color} {size_info}")

        lines.append("Animations:")
        for anim in shot.animations:
            action = anim.get("action", "?")
            target = anim.get("target", "?")
            rt = anim.get("run_time", 1.0)
            lines.append(f"  {action}({target}, run_time={rt})")

    return "\n".join(lines)


def print_screenplay(sp: Screenplay):
    """Pretty-print a screenplay."""
    print(f"\n--- Screenplay: {sp.title} ({len(sp.shots)} shots) ---")

    if sp.color_assignments:
        print(f"\nColors: {sp.color_assignments}")

    if sp.visual_metaphors:
        print(f"\nMetaphors:")
        for k, v in sp.visual_metaphors.items():
            print(f"  {k} → {v}")

    for shot in sp.shots:
        print(f"\n  Shot {shot.id} ({shot.duration}s) [{shot.camera}]")
        print(f"  Narration: \"{shot.narration[:60]}...\"")
        print(f"  Elements: {len(shot.screen_elements)}")
        for e in shot.screen_elements[:3]:
            print(f"    {e.get('name')}: {e.get('type')} \"{e.get('label')}\" at {e.get('position')}")
        print(f"  Animations: {len(shot.animations)}")
        print(f"  Teaching: {shot.teaching_point[:50]}")
