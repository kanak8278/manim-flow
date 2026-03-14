"""Writers Room — creative exploration, story drafting, and director review.

Step 1 of video creation: find the best story angle BEFORE any code generation.

Flow:
  topic → explore angles → evaluate → draft story → director review → revise → approved story

Every visual description must be in terms of what Manim can actually render.
No cinema. No crowds. No 3D. No photography. Just 2D programmatic animation.
"""

from dataclasses import dataclass, field
from .agent import call_llm, extract_json
from .domain_knowledge import get_storytelling_knowledge, VISUAL_VOCABULARY

# ─── MANIM MEDIUM AWARENESS ───
# This gets injected into every prompt that involves visual descriptions.

MANIM_MEDIUM = """
## YOUR MEDIUM: 2D Programmatic Animation (Manim)

You are writing for a SPECIFIC MEDIUM — not cinema, not illustration, not live action.
Your medium is Manim: a Python library that renders 2D mathematical animations on a black canvas.

Think of it like writing a play for a specific theater: you work WITHIN the constraints to create
something beautiful, not against them.

### WHAT YOU CAN PUT ON SCREEN (the complete visual toolkit):

ELEMENTS:
- **Text**: Any text string. Has font_size (20-48), color, position. Use for titles, labels, narration highlights.
- **Card**: A labeled rounded rectangle — the atomic unit for concepts/entities.
  RoundedRectangle with Text inside. Has width, height, color, label text.
  Use for: representing any concept, entity, step, or category.
- **Arrow**: Connects two elements. Shows relationships, flow, cause-and-effect.
- **Line**: Connects two points. Use for hierarchy connections, dividers, underlines.
- **Circle**: With optional label. Use for mathematical objects, nodes, points.
- **Dot**: A point marker. Use on number lines, graphs, coordinate planes.
- **NumberLine**: A labeled number range. Use for showing positions, intervals, convergence.
- **Axes + Graph**: Coordinate system with plotted functions. Use for any mathematical function.
- **VGroup**: Group multiple elements. They move/animate together as one unit.
- **Table**: Grid of text values. Use for comparisons, data display.
- **Brace**: Curly brace with label. Use for annotating parts of equations or diagrams.

ANIMATIONS (how things move):
- **Write**: Text appears letter by letter (1-2s)
- **Create**: Shape draws its outline (1-2s)
- **FadeIn**: Element appears smoothly (0.5-1s)
- **FadeOut**: Element disappears (0.5-1s)
- **Transform**: Morph one shape into another (1-2s) — shows conceptual connection
- **ReplacementTransform**: Same as Transform but replaces the original
- **Indicate**: Brief highlight pulse on an element (0.3-0.5s)
- **GrowFromCenter**: Element grows from a point (0.8-1.5s)
- **MoveToTarget**: Smoothly move to new position (1-2s)
- **Circumscribe**: Draw a highlight circle/rectangle around an element
- **Flash**: Brief bright flash at a point (for emphasis)

SCREEN CONSTRAINTS:
- Canvas: 14 units wide × 8 units tall (x: -7 to 7, y: -4 to 4)
- Safe area: keep content within x: -6 to 6, y: -3.5 to 3.5
- Maximum 4 elements on screen at once (visual working memory limit)
- Every element MUST be cleaned up (FadeOut) before it leaves the narrative
- Black background, bright elements

### WHAT YOU CANNOT DO (impossible in this medium):

- NO human figures, faces, expressions, crowds, body language
- NO photorealistic images, photographs, video clips
- NO 3D scenes, camera orbits, depth effects
- NO physics simulations (gravity, particles, fluid, smoke)
- NO camera pans or zooms (the frame is fixed)
- NO sound effects (audio is voiceover only)
- NO complex illustrations (buildings, landscapes, machines)

### HOW TO THINK ABOUT VISUALS:

Instead of "show a runner racing on a track" → use a labeled card sliding along a NumberLine
Instead of "crowd holding signs" → use two text elements showing opposing claims
Instead of "camera zooms into the equation" → the equation grows larger via scale animation
Instead of "confetti falls" → use Flash or Indicate on the result
Instead of "split-screen comparison" → two cards side by side with arrows

EVERY visual must be a combination of the elements listed above. If you can't express it
using these building blocks, it's not possible in this medium. Redesign the visual.
"""

# ─── EDUCATIONAL BEAT STRUCTURE ───

BEAT_STRUCTURE = """
## EDUCATIONAL BEAT STRUCTURE

Every video follows this emotional/intellectual arc. Each scene maps to one or more beats.

1. **HOOK** (first 10% of duration)
   What viewer KNOWS: nothing yet
   What viewer FEELS: curiosity, surprise, or intrigue
   Visual: A question on screen, a surprising number, a bold claim — ONE element that demands attention

2. **MISCONCEPTION** (10-25%)
   What viewer KNOWS: the obvious (wrong) answer
   What viewer FEELS: confidence in their wrong intuition
   Visual: Show the "obvious" answer visually, let viewer commit to it

3. **DISRUPTION** (25-35%)
   What viewer KNOWS: their intuition was wrong
   What viewer FEELS: confusion, cognitive dissonance
   Visual: The visual proof that breaks their model — a counter-example, a contradiction

4. **BUILD** (35-65%)
   What viewer KNOWS: pieces of the correct model, one at a time
   What viewer FEELS: growing understanding, "oh, I see..."
   Visual: Progressive disclosure — add one element at a time, each building on the previous

5. **AHA** (65-80%)
   What viewer KNOWS: the complete picture clicks into place
   What viewer FEELS: satisfaction, wonder, "that's beautiful"
   Visual: The most dynamic animation — Transform, color change, elements connecting

6. **RESOLUTION** (80-100%)
   What viewer KNOWS: the insight and its implications
   What viewer FEELS: satisfied, wanting to share this
   Visual: Callback to opening question, now answered. Clean, minimal final frame.

Not every video needs all 6 beats. Short videos (60s) can skip MISCONCEPTION.
The AHA must ALWAYS be the most visual, most animated moment.
"""


@dataclass
class StoryAngle:
    """One possible approach to explaining the topic."""
    id: str
    title: str
    hook: str
    approach: str
    visual_metaphor: str  # must be expressible in Manim primitives
    emotional_arc: str
    aha_moment: str
    uniqueness: str
    feasibility_notes: str = ""
    manim_elements: list[str] = field(default_factory=list)  # key Manim element types needed


@dataclass
class DirectorNotes:
    """Feedback from the director on a story draft."""
    overall_verdict: str  # "approve", "revise", "restart"
    score: float  # 1-10
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    specific_fixes: list[str] = field(default_factory=list)
    tone_notes: str = ""
    pacing_notes: str = ""
    visual_notes: str = ""
    missing_elements: list[str] = field(default_factory=list)
    feasibility_issues: list[str] = field(default_factory=list)


@dataclass
class ApprovedStory:
    """A story that passed director review."""
    title: str
    angle: StoryAngle
    scenes: list[dict]
    narration_draft: list[str]
    director_notes: DirectorNotes
    revision_count: int = 0


# ─── PHASE 1: EXPLORE ANGLES ───

EXPLORE_PROMPT = """You are a creative team brainstorming story angles for an educational animation video.

""" + MANIM_MEDIUM + """

Given a topic, generate 3-4 DIFFERENT approaches to explaining it. Each approach should be
a completely different creative angle — not just different wording, but different visual metaphors,
different emotional arcs, different entry points.

Think like a filmmaker who KNOWS their medium:
- What analogy from everyday life makes this click?
- What's the most SURPRISING way to reveal this truth?
- What visual using CARDS, ARROWS, NUMBER LINES, GRAPHS would make someone stop scrolling?
- What question would make them NEED to know the answer?

For each angle, your visual_metaphor MUST be expressible using the Manim elements listed above.
Not "runners racing on a track" — that's cinema. Think "labeled dots converging on a number line."

Return JSON:
{
  "angles": [
    {
      "id": "number_line_convergence",
      "title": "The Gap That Doesn't Exist",
      "hook": "What if I told you two numbers that look different are actually the same?",
      "approach": "Show 0.999... as a dot approaching 1 on a number line, then prove the gap is zero",
      "visual_metaphor": "A dot sliding along a number line, getting closer to 1, with the gap shrinking to nothing",
      "emotional_arc": "Disbelief → curiosity → visual proof → aha → wonder",
      "aha_moment": "When the gap measurement shows exactly 0.000... = 0, the two dots merge into one",
      "uniqueness": "Makes the abstract concrete — you can SEE there's no gap",
      "manim_elements": ["number_line", "dot", "brace", "text", "arrow"]
    }
  ]
}"""


async def explore_angles(topic: str, audience: str = "general") -> list[StoryAngle]:
    """Generate multiple creative angles for a topic."""
    user_prompt = (
        f"Generate 3-4 creative story angles for this educational video:\n\n"
        f"TOPIC: {topic}\n"
        f"AUDIENCE: {audience}\n\n"
        f"Make each angle genuinely DIFFERENT — different metaphors, different entry points, "
        f"different emotional journeys. Not just rewording the same idea.\n\n"
        f"CRITICAL: Every visual_metaphor must be achievable with Manim 2D elements "
        f"(cards, arrows, number lines, graphs, text, dots). "
        f"No humans, no 3D, no photography, no physics simulations.\n\n"
        f"Return ONLY valid JSON."
    )

    response = await call_llm(EXPLORE_PROMPT, user_prompt)
    data = extract_json(response)

    angles = []
    for a in data.get("angles", []):
        angles.append(StoryAngle(
            id=a.get("id", ""),
            title=a.get("title", ""),
            hook=a.get("hook", ""),
            approach=a.get("approach", ""),
            visual_metaphor=a.get("visual_metaphor", ""),
            emotional_arc=a.get("emotional_arc", ""),
            aha_moment=a.get("aha_moment", ""),
            uniqueness=a.get("uniqueness", ""),
            manim_elements=a.get("manim_elements", []),
        ))

    return angles


# ─── PHASE 2: EVALUATE AND PICK ───

EVALUATE_PROMPT = """You are evaluating story angles for an educational animation video.

The animation medium is Manim — 2D programmatic animation on a black canvas.
Available elements: text, labeled cards (rounded rectangles), arrows, lines, circles, dots,
number lines, axes with graphs, groups, braces, tables.
No humans, no 3D, no photography, no physics simulations.

Score each angle on:

1. HOOK POWER (1-10): Would someone stop scrolling for this?
2. VISUAL POTENTIAL (1-10): Can this be beautifully animated using ONLY Manim 2D elements?
   High score = clever use of cards, arrows, transforms, graphs. Low score = requires cinema.
3. CLARITY (1-10): Will the audience actually understand the concept through this angle?
4. SURPRISE (1-10): Does this angle reveal something unexpected?
5. MANIM FEASIBILITY (1-10): Can every visual described actually be built with Manim elements?
   Score 1-3 if it requires humans/3D/photos. Score 7-10 if it uses cards, arrows, graphs naturally.

Return JSON:
{
  "rankings": [
    {
      "angle_id": "number_line_convergence",
      "scores": {"hook": 8, "visual": 9, "clarity": 8, "surprise": 6, "feasibility": 9},
      "total": 40,
      "reasoning": "Strong visual metaphor using number line and dots, highly feasible in Manim"
    }
  ],
  "winner": "angle_id_of_best",
  "runner_up": "angle_id_of_second_best"
}"""


async def evaluate_angles(angles: list[StoryAngle], topic: str) -> dict:
    """Score and rank story angles."""
    angles_text = "\n\n".join(
        f"ANGLE: {a.id}\n"
        f"  Title: {a.title}\n"
        f"  Hook: {a.hook}\n"
        f"  Approach: {a.approach}\n"
        f"  Visual metaphor: {a.visual_metaphor}\n"
        f"  Aha moment: {a.aha_moment}\n"
        f"  Uniqueness: {a.uniqueness}\n"
        f"  Manim elements needed: {', '.join(a.manim_elements) if a.manim_elements else 'not specified'}"
        for a in angles
    )

    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Evaluate these story angles:\n\n{angles_text}\n\n"
        f"Heavily penalize any angle that requires visuals impossible in Manim "
        f"(humans, 3D, photos, camera movement).\n\n"
        f"Return ONLY valid JSON."
    )

    response = await call_llm(EVALUATE_PROMPT, user_prompt)
    return extract_json(response)


# ─── PHASE 3: DRAFT STORY ───

DRAFT_PROMPT = """You are writing a complete story draft for an educational animation video.

""" + MANIM_MEDIUM + """

""" + BEAT_STRUCTURE + """

""" + VISUAL_VOCABULARY + """

Given a winning story angle, write a COMPLETE scene-by-scene draft.
This draft is the SOURCE OF TRUTH for the entire video pipeline. Everything downstream
depends on it being thorough, specific, and implementable.

For each scene you MUST specify ALL of the following:

1. **narration**: The EXACT words the narrator says. Conversational, like explaining to a friend.
   Short sentences (<15 words). Active voice. ASCII characters only.

2. **visual_elements**: Every element visible on screen, described as a Manim object:
   - name: unique identifier (snake_case)
   - type: one of [text, card, arrow, line, circle, dot, number_line, axes, graph, brace, table, vgroup]
   - label: the text displayed (for text/card types)
   - position: Manim position like "UP * 2", "LEFT * 3 + DOWN * 1", "ORIGIN"
   - color: hex color like "#3498db" or named color like "WHITE"
   - Additional params: width, height, font_size, etc.

3. **animations**: Ordered list of what happens, using Manim animation names:
   - action: one of [write, create, fade_in, fade_out, transform, indicate, grow_from_center, move_to, circumscribe, flash]
   - target: the visual_element name
   - run_time: duration in seconds (0.3-3.0)
   - For transform: also specify "transform_to" (what it becomes)

4. **cleanup**: List of element names that must be FadeOut'd at the end of this scene.
   EVERY element must either persist into the next scene (explicitly stated) or be cleaned up.

5. **teaching_goal**: One sentence — what the viewer understands after this scene.
6. **emotion**: What the viewer feels (curiosity, surprise, understanding, satisfaction).
7. **duration**: Total seconds for this scene (10-30s).
8. **beat**: Which beat this scene corresponds to (hook, misconception, disruption, build, aha, resolution).

Return JSON:
{
  "title": "video title",
  "scenes": [
    {
      "id": 1,
      "name": "hook",
      "beat": "hook",
      "duration": 12,
      "narration": "What if I told you that zero point nine nine nine repeating is exactly equal to one?",
      "visual_elements": [
        {
          "name": "question_text",
          "type": "text",
          "label": "Does 0.999... = 1?",
          "position": "UP * 1",
          "color": "#f39c12",
          "font_size": 42
        },
        {
          "name": "number_line",
          "type": "number_line",
          "position": "DOWN * 1",
          "color": "WHITE"
        }
      ],
      "animations": [
        {"action": "write", "target": "question_text", "run_time": 2.0},
        {"action": "create", "target": "number_line", "run_time": 1.5}
      ],
      "cleanup": ["question_text"],
      "persists": ["number_line"],
      "teaching_goal": "The viewer is hooked by a surprising claim",
      "emotion": "surprise and disbelief"
    }
  ],
  "color_assignments": {
    "concept_name": "#hex_color"
  }
}

CRITICAL RULES:
- Every visual_element MUST have a type from the allowed list
- Maximum 4 visual_elements per scene
- Every element name must be unique across the entire story
- Every element must appear in either cleanup or persists
- Narration must be exact words, not summaries
- Duration must add up to approximately the target duration
"""


async def draft_story(angle: StoryAngle, topic: str, duration: int = 120) -> dict:
    """Write a complete story draft from a winning angle."""
    user_prompt = (
        f"Write a COMPLETE scene-by-scene story draft for this video:\n\n"
        f"TOPIC: {topic}\n"
        f"DURATION: ~{duration} seconds\n"
        f"CHOSEN ANGLE:\n"
        f"  Title: {angle.title}\n"
        f"  Hook: {angle.hook}\n"
        f"  Approach: {angle.approach}\n"
        f"  Visual metaphor: {angle.visual_metaphor}\n"
        f"  Emotional arc: {angle.emotional_arc}\n"
        f"  Aha moment: {angle.aha_moment}\n"
        f"  Manim elements: {', '.join(angle.manim_elements) if angle.manim_elements else 'cards, arrows, text'}\n\n"
        f"Write 5-8 scenes totaling ~{duration} seconds.\n"
        f"EVERY visual_element must be a Manim type (text, card, arrow, number_line, axes, etc.).\n"
        f"EVERY scene must have narration, visual_elements, animations, cleanup, teaching_goal, emotion.\n"
        f"Narration must be the EXACT words spoken — not a summary.\n"
        f"Return ONLY valid JSON."
    )

    response = await call_llm(DRAFT_PROMPT, user_prompt)
    return extract_json(response)


# ─── PHASE 4: DIRECTOR REVIEW ───

DIRECTOR_PROMPT = """You are a creative director reviewing a story draft for an educational animation.

You have TWO areas of expertise:
1. STORYTELLING — pacing, hooks, emotional arc, clarity (trained under McKee and Veritasium)
2. MANIM FEASIBILITY — you know exactly what Manim can and cannot render

""" + get_storytelling_knowledge() + """

""" + MANIM_MEDIUM + """

Review criteria:

NARRATIVE QUALITY:
1. HOOK: Does scene 1 grab in 3 seconds? Would YOU keep watching?
2. FLOW: Does each scene naturally lead to the next? Any jarring jumps?
3. PACING: Are complex ideas given enough time? Are simple parts too slow?
4. AHA MOMENT: Is the reveal dramatic enough? Does it earn the payoff?
5. ENDING: Does it land? Callback to opening?
6. NARRATION: Is it conversational? Short sentences? Active voice?

MANIM FEASIBILITY:
7. VISUAL ELEMENTS: Is every visual_element a valid Manim type? No cinema descriptions?
8. SCREEN LIMITS: Maximum 4 elements per scene? All within screen bounds?
9. CLEANUP: Does every scene clean up its elements or explicitly persist them?
10. COMPLETENESS: Does every scene have narration, visual_elements, animations, teaching_goal?

Be specific and actionable — not "make it better" but "scene 3 needs a card for 'Proof Step 2'
at position DOWN * 1, not a vague 'mathematical demonstration'."

Flag ANY visual description that can't be built in Manim as a feasibility_issue.

Return JSON:
{
  "overall_verdict": "approve|revise|restart",
  "score": 7.5,
  "strengths": ["strong hook", "great use of number line in scene 3"],
  "weaknesses": ["scene 4 has no visual_elements", "pacing too fast in proof section"],
  "specific_fixes": [
    "Scene 3: Add a brace element showing the gap between 0.999... and 1",
    "Scene 5: Replace vague 'algebraic proof appears' with specific text elements for each step"
  ],
  "tone_notes": "Narration in scene 2 sounds like a textbook.",
  "pacing_notes": "Scenes 3-4 rush through the proof in 20s. Need 30s minimum.",
  "visual_notes": "Scene 5 needs a Transform from the series cards to the equation card.",
  "missing_elements": ["No misconception beat", "Never address why people think they're different"],
  "feasibility_issues": ["Scene 2 describes 'crowd holding signs' — impossible in Manim, use text elements instead"]
}"""


async def director_review(story_draft: dict, angle: StoryAngle, topic: str) -> DirectorNotes:
    """Get director feedback on a story draft."""
    scenes_text = ""
    for i, s in enumerate(story_draft.get("scenes", [])):
        if not isinstance(s, dict):
            continue
        scenes_text += (
            f"\nSCENE {s.get('id', i+1)}: {s.get('name', '')}"
            f" [{s.get('beat', '?')}] ({s.get('duration', '?')}s)\n"
        )
        scenes_text += f"  Narration: \"{s.get('narration', '')}\"\n"
        scenes_text += f"  Teaching: {s.get('teaching_goal', '')}\n"
        scenes_text += f"  Emotion: {s.get('emotion', '')}\n"

        # Show visual elements
        for elem in s.get("visual_elements", []):
            scenes_text += (
                f"  Element: {elem.get('name', '?')} ({elem.get('type', '?')}) "
                f"\"{elem.get('label', '')}\" at {elem.get('position', '?')}\n"
            )

        # Show animations
        for anim in s.get("animations", []):
            scenes_text += (
                f"  Animation: {anim.get('action', '?')}({anim.get('target', '?')}, "
                f"run_time={anim.get('run_time', '?')})\n"
            )

        cleanup = s.get("cleanup", [])
        persists = s.get("persists", [])
        if cleanup:
            scenes_text += f"  Cleanup: {', '.join(cleanup)}\n"
        if persists:
            scenes_text += f"  Persists: {', '.join(persists)}\n"

    user_prompt = (
        f"Review this story draft:\n\n"
        f"TOPIC: {topic}\n"
        f"TITLE: {story_draft.get('title', '')}\n"
        f"ANGLE: {angle.title} — {angle.approach}\n\n"
        f"SCENES:\n{scenes_text}\n\n"
        f"Be brutally honest. Flag EVERY visual that can't be built in Manim.\n"
        f"Check that EVERY scene has complete visual_elements with Manim types.\n"
        f"Return ONLY valid JSON."
    )

    response = await call_llm(DIRECTOR_PROMPT, user_prompt)
    data = extract_json(response)

    return DirectorNotes(
        overall_verdict=data.get("overall_verdict", "revise"),
        score=data.get("score", 5),
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        specific_fixes=data.get("specific_fixes", []),
        tone_notes=data.get("tone_notes", ""),
        pacing_notes=data.get("pacing_notes", ""),
        visual_notes=data.get("visual_notes", ""),
        missing_elements=data.get("missing_elements", []),
        feasibility_issues=data.get("feasibility_issues", []),
    )


# ─── PHASE 5: REVISE STORY ───

REVISE_PROMPT = """You are revising a story draft based on director feedback.

Apply EVERY fix the director requested. Don't ignore any notes.
Keep what the director said works. Fix what they said doesn't.

CRITICAL: Every visual_element MUST have ALL of these fields:
- "name": unique snake_case identifier (e.g. "card_5", "swap_arrow", "result_text")
- "type": one of [text, card, arrow, line, circle, dot, number_line, axes, graph, brace, table, vgroup]
- "label": display text (for text/card types)
- "position": Manim position like "UP * 2", "LEFT * 3", "ORIGIN"
- "color": hex color like "#3498db"

Every scene MUST have: id, name, beat, duration, narration, visual_elements, animations, cleanup, persists, teaching_goal, emotion.
Every animation MUST have: action, target (matching an element name), run_time.
Maximum 4 visual_elements per scene.
Narration must be exact words, not summaries.
Fix ALL feasibility issues — replace any cinema descriptions with Manim elements.

Return the COMPLETE revised story in the same JSON format. Include ALL scenes."""


async def revise_story(story_draft: dict, director_notes: DirectorNotes, angle: StoryAngle) -> dict:
    """Revise a story based on director feedback."""
    fixes = "\n".join(f"  - {f}" for f in director_notes.specific_fixes)
    weaknesses = "\n".join(f"  - {w}" for w in director_notes.weaknesses)
    feasibility = "\n".join(f"  - {f}" for f in director_notes.feasibility_issues)

    user_prompt = (
        f"Revise this story draft based on director feedback:\n\n"
        f"ORIGINAL DRAFT:\n{_story_to_text(story_draft)}\n\n"
        f"DIRECTOR NOTES (score: {director_notes.score}/10):\n"
        f"Weaknesses:\n{weaknesses}\n\n"
        f"Specific fixes:\n{fixes}\n\n"
    )

    if feasibility:
        user_prompt += f"FEASIBILITY ISSUES (must fix ALL of these):\n{feasibility}\n\n"

    user_prompt += (
        f"Tone: {director_notes.tone_notes}\n"
        f"Pacing: {director_notes.pacing_notes}\n"
        f"Visual: {director_notes.visual_notes}\n"
        f"Missing: {', '.join(director_notes.missing_elements)}\n\n"
        f"Apply ALL fixes. Replace ALL cinema-style visuals with Manim elements.\n"
        f"Return complete revised story as JSON."
    )

    response = await call_llm(REVISE_PROMPT, user_prompt)
    return extract_json(response)


def _story_to_text(story: dict) -> str:
    """Convert story dict to readable text for revision prompt."""
    lines = [f"Title: {story.get('title', '')}"]

    if story.get("color_assignments"):
        lines.append(f"Colors: {story['color_assignments']}")

    for s in story.get("scenes", []):
        if not isinstance(s, dict):
            continue
        lines.append(f"\nScene {s.get('id', '?')}: {s.get('name', '')} [{s.get('beat', '?')}] ({s.get('duration', '?')}s)")
        lines.append(f"  Narration: \"{s.get('narration', '')}\"")
        lines.append(f"  Teaching: {s.get('teaching_goal', '')}")
        lines.append(f"  Emotion: {s.get('emotion', '')}")

        for elem in s.get("visual_elements", []):
            lines.append(
                f"  Element: {elem.get('name', '?')} ({elem.get('type', '?')}) "
                f"\"{elem.get('label', '')}\" at {elem.get('position', '?')} color={elem.get('color', '?')}"
            )
        for anim in s.get("animations", []):
            lines.append(
                f"  Anim: {anim.get('action', '?')}({anim.get('target', '?')}, {anim.get('run_time', '?')}s)"
            )

        cleanup = s.get("cleanup", [])
        persists = s.get("persists", [])
        if cleanup:
            lines.append(f"  Cleanup: {', '.join(cleanup)}")
        if persists:
            lines.append(f"  Persists: {', '.join(persists)}")

    return "\n".join(lines)


# ─── STORY VALIDATION ───

def validate_story(story: dict) -> dict:
    """Validate a story draft for completeness and Manim feasibility.

    Returns dict with 'valid' bool, 'issues' list, 'warnings' list.
    """
    issues = []
    warnings = []
    scenes = story.get("scenes", [])

    if not scenes:
        issues.append("No scenes found")
        return {"valid": False, "issues": issues, "warnings": warnings}

    valid_types = {
        "text", "card", "arrow", "line", "circle", "dot",
        "number_line", "axes", "graph", "brace", "table", "vgroup",
    }
    valid_actions = {
        "write", "create", "fade_in", "fade_out", "transform",
        "indicate", "grow_from_center", "move_to", "circumscribe", "flash",
    }

    all_element_names = set()
    total_duration = 0

    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            issues.append(f"Scene {i+1}: not a dict")
            continue

        scene_id = scene.get("id", i + 1)
        prefix = f"Scene {scene_id}"

        # Required fields
        if not scene.get("narration"):
            issues.append(f"{prefix}: missing narration")
        elif len(scene.get("narration", "")) < 20:
            warnings.append(f"{prefix}: narration too short ({len(scene.get('narration', ''))} chars)")

        if not scene.get("teaching_goal"):
            warnings.append(f"{prefix}: missing teaching_goal")

        if not scene.get("duration"):
            warnings.append(f"{prefix}: missing duration")
        else:
            total_duration += scene.get("duration", 0)

        # Visual elements
        elements = scene.get("visual_elements", [])
        if not elements:
            issues.append(f"{prefix}: no visual_elements")

        if len(elements) > 4:
            warnings.append(f"{prefix}: {len(elements)} elements (max 4 recommended)")

        for elem in elements:
            name = elem.get("name", "")
            etype = elem.get("type", "")

            if not name:
                issues.append(f"{prefix}: element missing name")
            elif name in all_element_names:
                warnings.append(f"{prefix}: duplicate element name '{name}'")
            all_element_names.add(name)

            if etype and etype not in valid_types:
                issues.append(f"{prefix}: invalid element type '{etype}' for '{name}'")

        # Animations
        for anim in scene.get("animations", []):
            action = anim.get("action", "")
            if action and action not in valid_actions:
                warnings.append(f"{prefix}: unknown animation '{action}'")

        # Cleanup tracking
        cleanup = set(scene.get("cleanup", []))
        persists = set(scene.get("persists", []))
        element_names = {e.get("name") for e in elements if e.get("name")}
        unaccounted = element_names - cleanup - persists
        if unaccounted:
            warnings.append(f"{prefix}: elements not in cleanup or persists: {unaccounted}")

    # Cinema detection - flag descriptions that sound like film, not Manim
    cinema_words = [
        "camera pan", "camera zoom", "close-up", "wide shot",
        "crowd", "audience", "person", "people", "face", "expression",
        "building", "landscape", "photograph", "realistic",
        "3d", "depth", "shadow", "lighting", "smoke", "particle",
        "explosion", "fire", "water", "rain", "snow",
    ]
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        narration = scene.get("narration", "").lower()
        visual_text = str(scene.get("visual_elements", "")).lower()
        combined = narration + " " + visual_text
        for word in cinema_words:
            if word in combined:
                warnings.append(
                    f"Scene {scene.get('id', '?')}: cinema term '{word}' detected — "
                    f"may not be implementable in Manim"
                )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "total_duration": total_duration,
        "scene_count": len(scenes),
        "element_count": len(all_element_names),
    }


# ─── ORCHESTRATOR: RUN THE FULL WRITERS ROOM ───

async def run_writers_room(
    topic: str,
    audience: str = "general",
    duration: int = 120,
    max_revisions: int = 2,
    verbose: bool = True,
) -> ApprovedStory:
    """Run the full writers room process: explore → pick → draft → review → revise."""
    _log = print if verbose else lambda *a: None

    # Phase 1: Explore angles
    _log("\n--- Writers Room: Exploring angles ---")
    angles = await explore_angles(topic, audience)
    for a in angles:
        _log(f"  [{a.id}] {a.title}")
        _log(f"    Hook: {a.hook[:80]}")
        _log(f"    Visual: {a.visual_metaphor[:60]}")
        if a.manim_elements:
            _log(f"    Manim: {', '.join(a.manim_elements)}")

    # Phase 2: Evaluate and pick
    _log("\n--- Writers Room: Evaluating angles ---")
    evaluation = await evaluate_angles(angles, topic)

    winner_id = evaluation.get("winner", angles[0].id if angles else "")
    winner = next((a for a in angles if a.id == winner_id), angles[0] if angles else None)

    if not winner:
        raise ValueError("No winning angle found")

    rankings = evaluation.get("rankings", [])
    for r in rankings:
        total = r.get("total", 0)
        _log(f"  {r.get('angle_id', '?'):20s}: {total}/50 — {r.get('reasoning', '')[:60]}")
    _log(f"\n  Winner: {winner.title}")

    # Phase 3: Draft story
    _log("\n--- Writers Room: Drafting story ---")
    story_draft = await draft_story(winner, topic, duration)
    _log(f"  Title: {story_draft.get('title', '')}")
    _log(f"  Scenes: {len(story_draft.get('scenes', []))}")

    # Validate draft
    validation = validate_story(story_draft)
    if validation["issues"]:
        _log(f"  Validation issues ({len(validation['issues'])}):")
        for issue in validation["issues"][:5]:
            _log(f"    [!] {issue}")
    if validation["warnings"]:
        _log(f"  Warnings ({len(validation['warnings'])}):")
        for w in validation["warnings"][:5]:
            _log(f"    [~] {w}")

    # Phase 4-5: Director review + revise loop
    revision = 0
    notes = None
    while revision < max_revisions:
        _log(f"\n--- Writers Room: Director review (round {revision + 1}) ---")
        notes = await director_review(story_draft, winner, topic)

        _log(f"  Score: {notes.score}/10 — {notes.overall_verdict}")
        for s in notes.strengths[:3]:
            _log(f"  [+] {s}")
        for w in notes.weaknesses[:3]:
            _log(f"  [-] {w}")
        for f in notes.specific_fixes[:3]:
            _log(f"  [fix] {f}")
        for f in notes.feasibility_issues[:3]:
            _log(f"  [INFEASIBLE] {f}")

        if notes.overall_verdict == "approve" or notes.score >= 8:
            _log(f"  Director approved!")
            break

        if notes.overall_verdict == "restart":
            _log(f"  Director says restart — trying runner-up angle")
            runner_id = evaluation.get("runner_up", "")
            runner = next((a for a in angles if a.id == runner_id), None)
            if runner:
                winner = runner
                story_draft = await draft_story(winner, topic, duration)
            revision += 1
            continue

        _log(f"  Revising based on director notes...")
        revised = await revise_story(story_draft, notes, winner)

        # Validate revision
        revised_scenes = revised.get("scenes", [])
        orig_scenes = story_draft.get("scenes", [])

        has_real_narration = any(
            isinstance(s, dict) and len(s.get("narration", "")) > 20
            for s in revised_scenes
        )

        if has_real_narration and len(revised_scenes) >= len(orig_scenes) * 0.5:
            # Validate both and keep the better one
            orig_validation = validate_story(story_draft)
            revised_validation = validate_story(revised)

            orig_issues = len(orig_validation.get("issues", []))
            revised_issues = len(revised_validation.get("issues", []))

            if revised_issues <= orig_issues:
                story_draft = revised
                _log(f"  Revised: {story_draft.get('title', '')} ({revised_issues} issues, was {orig_issues})")
            else:
                _log(f"  Revision is worse ({revised_issues} issues vs {orig_issues}), keeping original")
        else:
            _log(f"  Revision produced bad output, keeping original")
        revision += 1

    # Ensure we have notes even if loop didn't run
    if notes is None:
        notes = DirectorNotes(overall_verdict="approve", score=7)

    # Build approved story — handle scenes that might be strings
    raw_scenes = story_draft.get("scenes", [])
    narrations = []
    clean_scenes = []
    for s in raw_scenes:
        if isinstance(s, dict):
            narrations.append(s.get("narration", ""))
            clean_scenes.append(s)
        elif isinstance(s, str):
            narrations.append(s)
            clean_scenes.append({"narration": s, "visual": s, "name": "scene"})
    story_draft["scenes"] = clean_scenes

    return ApprovedStory(
        title=story_draft.get("title", topic),
        angle=winner,
        scenes=story_draft.get("scenes", []),
        narration_draft=narrations,
        director_notes=notes,
        revision_count=revision,
    )
