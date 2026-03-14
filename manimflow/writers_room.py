"""Writers Room — creative exploration, story drafting, and director review.

This is Step 1 of video creation: find the best story angle BEFORE any
code generation or visual planning happens.

Flow:
  topic → explore angles → evaluate → draft story → director review → revise → approved story
"""

from dataclasses import dataclass, field
from .llm import call_llm, extract_json
from .domain_knowledge import get_storytelling_knowledge


@dataclass
class StoryAngle:
    """One possible approach to explaining the topic."""
    id: str
    title: str
    hook: str
    approach: str  # how we'll explain it
    visual_metaphor: str  # the central visual idea
    emotional_arc: str  # what the viewer feels throughout
    aha_moment: str  # when everything clicks
    uniqueness: str  # why this angle is interesting
    feasibility_notes: str = ""  # any concerns about animating this


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

EXPLORE_PROMPT = """You are a creative team brainstorming story angles for an educational video.

Given a topic, generate 3-4 DIFFERENT approaches to explaining it. Each approach should be
a completely different creative angle — not just different wording, but different visual metaphors,
different emotional arcs, different entry points.

Think like a filmmaker, not a textbook writer:
- What analogy from everyday life makes this click?
- What's the most SURPRISING way to reveal this truth?
- What visual would make someone stop scrolling?
- What question would make them NEED to know the answer?

For each angle, describe:
- The HOOK: first 5 seconds that grab attention
- The APPROACH: how you'll build understanding
- The VISUAL METAPHOR: the central image/animation that carries the explanation
- The EMOTIONAL ARC: what the viewer feels (confused → curious → amazed)
- The AHA MOMENT: the specific instant when everything clicks
- UNIQUENESS: why this angle is better/different than the obvious explanation

Return JSON:
{
  "angles": [
    {
      "id": "pizza_proof",
      "title": "Every Pizza is a Math Lesson",
      "hook": "What if I told you your pizza delivery guy is carrying a mathematical proof?",
      "approach": "Start with a pizza, slice it, rearrange into a rectangle, derive the formula",
      "visual_metaphor": "Pizza slices rearranging into a rectangle",
      "emotional_arc": "Hungry curiosity → playful discovery → satisfying proof",
      "aha_moment": "When the rearranged slices form a perfect rectangle with sides r and πr",
      "uniqueness": "Connects abstract math to something everyone has touched"
    }
  ]
}"""


def explore_angles(topic: str, audience: str = "general") -> list[StoryAngle]:
    """Generate multiple creative angles for a topic."""
    user_prompt = (
        f"Generate 3-4 creative story angles for this educational video:\n\n"
        f"TOPIC: {topic}\n"
        f"AUDIENCE: {audience}\n\n"
        f"Make each angle genuinely DIFFERENT — different metaphors, different entry points, "
        f"different emotional journeys. Not just rewording the same idea.\n\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(EXPLORE_PROMPT, user_prompt)
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
        ))

    return angles


# ─── PHASE 2: EVALUATE AND PICK ───

EVALUATE_PROMPT = """You are evaluating story angles for an educational video. Score each on:

1. HOOK POWER (1-10): Would someone stop scrolling for this?
2. VISUAL POTENTIAL (1-10): Can this be beautifully animated? Is the central metaphor visual?
3. CLARITY (1-10): Will the audience actually understand the concept through this angle?
4. SURPRISE (1-10): Does this angle reveal something unexpected?
5. FEASIBILITY (1-10): Can this realistically be animated in Manim in 60-120 seconds?

Return JSON:
{
  "rankings": [
    {
      "angle_id": "pizza_proof",
      "scores": {"hook": 8, "visual": 9, "clarity": 8, "surprise": 6, "feasibility": 9},
      "total": 40,
      "reasoning": "Strong visual metaphor, highly feasible, but pizza angle is common"
    }
  ],
  "winner": "angle_id_of_best",
  "runner_up": "angle_id_of_second_best"
}"""


def evaluate_angles(angles: list[StoryAngle], topic: str) -> dict:
    """Score and rank story angles."""
    angles_text = "\n\n".join(
        f"ANGLE: {a.id}\n"
        f"  Title: {a.title}\n"
        f"  Hook: {a.hook}\n"
        f"  Approach: {a.approach}\n"
        f"  Visual metaphor: {a.visual_metaphor}\n"
        f"  Aha moment: {a.aha_moment}\n"
        f"  Uniqueness: {a.uniqueness}"
        for a in angles
    )

    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Evaluate these story angles:\n\n{angles_text}\n\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(EVALUATE_PROMPT, user_prompt)
    return extract_json(response)


# ─── PHASE 3: DRAFT STORY ───

DRAFT_PROMPT = """You are writing a story draft for an educational animation video.

Given a winning story angle, write a complete scene-by-scene draft.

For each scene, write:
- WHAT THE VIEWER SEES (specific visual elements, not vague descriptions)
- WHAT THE NARRATOR SAYS (actual narration text, conversational tone)
- WHAT THE VIEWER FEELS (the emotional beat)
- THE TEACHING GOAL (what they understand after this scene)

Keep narration conversational — like explaining to a smart friend, not lecturing.
Each scene: 15-25 seconds. Total: 5-7 scenes.

Return JSON:
{
  "title": "video title",
  "scenes": [
    {
      "id": 1,
      "name": "hook",
      "duration": 15,
      "visual": "detailed description of what appears on screen — shapes, colors, motion",
      "narration": "exact words the narrator says",
      "emotion": "what the viewer feels",
      "teaching_goal": "what they understand after this",
      "key_elements": ["circle", "radius_line", "question_text"]
    }
  ]
}"""


def draft_story(angle: StoryAngle, topic: str, duration: int = 120) -> dict:
    """Write a complete story draft from a winning angle."""
    user_prompt = (
        f"Write a scene-by-scene story draft for this video:\n\n"
        f"TOPIC: {topic}\n"
        f"DURATION: ~{duration} seconds\n"
        f"CHOSEN ANGLE:\n"
        f"  Title: {angle.title}\n"
        f"  Hook: {angle.hook}\n"
        f"  Approach: {angle.approach}\n"
        f"  Visual metaphor: {angle.visual_metaphor}\n"
        f"  Emotional arc: {angle.emotional_arc}\n"
        f"  Aha moment: {angle.aha_moment}\n\n"
        f"Write 5-7 scenes totaling ~{duration} seconds.\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(DRAFT_PROMPT, user_prompt)
    return extract_json(response)


# ─── PHASE 4: DIRECTOR REVIEW ───

DIRECTOR_PROMPT = """You are a creative director reviewing a story draft for an educational animation.

You've trained at film school, studied under Robert McKee, and worked with Veritasium on content strategy.

""" + get_storytelling_knowledge() + """
Be specific and actionable — not "make it better" but "scene 3 needs a visual transition
between the circle and the rectangle, use a morphing animation."

Review criteria:
1. HOOK: Does scene 1 grab in 3 seconds? Would YOU keep watching?
2. FLOW: Does each scene naturally lead to the next? Any jarring jumps?
3. VISUAL RICHNESS: Is every scene visual? Or are some just "text appears"?
4. PACING: Are complex ideas given enough time? Are simple parts too slow?
5. AHA MOMENT: Is the reveal dramatic enough? Does it earn the payoff?
6. ENDING: Does it land? Does the viewer feel satisfied AND curious for more?
7. NARRATION: Is it conversational? Does it sound like a person, not a textbook?

Give a score (1-10) and specific notes.

Return JSON:
{
  "overall_verdict": "approve|revise|restart",
  "score": 7.5,
  "strengths": ["strong hook", "great visual metaphor in scene 3"],
  "weaknesses": ["scene 4 is just text with no visual", "pacing too fast in proof section"],
  "specific_fixes": [
    "Scene 3: Add a 2-second pause after the rectangle forms — let the aha breathe",
    "Scene 4: Replace the text explanation with an animated number line showing convergence",
    "Scene 6: The ending is flat — add a callback to the opening hook"
  ],
  "tone_notes": "Narration in scene 2 sounds like a textbook. Make it more conversational.",
  "pacing_notes": "Scenes 3-4 rush through the proof in 20s. Give it 30s minimum.",
  "visual_notes": "Scene 5 needs a shape on screen — right now it's all text.",
  "missing_elements": ["No moment of surprise/twist", "Never address the misconception"]
}"""


def director_review(story_draft: dict, angle: StoryAngle, topic: str) -> DirectorNotes:
    """Get director feedback on a story draft."""
    scenes_text = "\n\n".join(
        f"SCENE {s.get('id', i+1)}: {s.get('name', '')}\n"
        f"  Duration: {s.get('duration', '?')}s\n"
        f"  Visual: {s.get('visual', '')}\n"
        f"  Narration: \"{s.get('narration', '')}\"\n"
        f"  Emotion: {s.get('emotion', '')}\n"
        f"  Teaching: {s.get('teaching_goal', '')}"
        for i, s in enumerate(story_draft.get("scenes", []))
    )

    user_prompt = (
        f"Review this story draft:\n\n"
        f"TOPIC: {topic}\n"
        f"TITLE: {story_draft.get('title', '')}\n"
        f"ANGLE: {angle.title} — {angle.approach}\n\n"
        f"SCENES:\n{scenes_text}\n\n"
        f"Be brutally honest. Give specific, actionable fixes.\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(DIRECTOR_PROMPT, user_prompt)
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
    )


# ─── PHASE 5: REVISE STORY ───

REVISE_PROMPT = """You are revising a story draft based on director feedback.

Apply EVERY fix the director requested. Don't ignore any notes.
Keep what the director said works. Fix what they said doesn't.

Return the COMPLETE revised story in the same JSON format as the original."""


def revise_story(story_draft: dict, director_notes: DirectorNotes, angle: StoryAngle) -> dict:
    """Revise a story based on director feedback."""
    fixes = "\n".join(f"  - {f}" for f in director_notes.specific_fixes)
    weaknesses = "\n".join(f"  - {w}" for w in director_notes.weaknesses)

    user_prompt = (
        f"Revise this story draft based on director feedback:\n\n"
        f"ORIGINAL DRAFT:\n{_story_to_text(story_draft)}\n\n"
        f"DIRECTOR NOTES (score: {director_notes.score}/10):\n"
        f"Weaknesses:\n{weaknesses}\n\n"
        f"Specific fixes:\n{fixes}\n\n"
        f"Tone: {director_notes.tone_notes}\n"
        f"Pacing: {director_notes.pacing_notes}\n"
        f"Visual: {director_notes.visual_notes}\n"
        f"Missing: {', '.join(director_notes.missing_elements)}\n\n"
        f"Apply ALL fixes. Keep what works. Return complete revised story as JSON."
    )

    response = call_llm(REVISE_PROMPT, user_prompt)
    return extract_json(response)


def _story_to_text(story: dict) -> str:
    """Convert story dict to readable text."""
    lines = [f"Title: {story.get('title', '')}"]
    for s in story.get("scenes", []):
        lines.append(f"\nScene {s.get('id', '?')}: {s.get('name', '')}")
        lines.append(f"  Visual: {s.get('visual', '')}")
        lines.append(f"  Narration: \"{s.get('narration', '')}\"")
    return "\n".join(lines)


# ─── ORCHESTRATOR: RUN THE FULL WRITERS ROOM ───

def run_writers_room(
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
    angles = explore_angles(topic, audience)
    for a in angles:
        _log(f"  [{a.id}] {a.title}")
        _log(f"    Hook: {a.hook[:80]}")
        _log(f"    Visual: {a.visual_metaphor[:60]}")

    # Phase 2: Evaluate and pick
    _log("\n--- Writers Room: Evaluating angles ---")
    evaluation = evaluate_angles(angles, topic)

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
    story_draft = draft_story(winner, topic, duration)
    _log(f"  Title: {story_draft.get('title', '')}")
    _log(f"  Scenes: {len(story_draft.get('scenes', []))}")

    # Phase 4-5: Director review + revise loop
    revision = 0
    while revision < max_revisions:
        _log(f"\n--- Writers Room: Director review (round {revision + 1}) ---")
        notes = director_review(story_draft, winner, topic)

        _log(f"  Score: {notes.score}/10 — {notes.overall_verdict}")
        for s in notes.strengths[:3]:
            _log(f"  [+] {s}")
        for w in notes.weaknesses[:3]:
            _log(f"  [-] {w}")
        for f in notes.specific_fixes[:3]:
            _log(f"  [fix] {f}")

        if notes.overall_verdict == "approve" or notes.score >= 8:
            _log(f"  Director approved!")
            break

        if notes.overall_verdict == "restart":
            _log(f"  Director says restart — trying runner-up angle")
            runner_id = evaluation.get("runner_up", "")
            runner = next((a for a in angles if a.id == runner_id), None)
            if runner:
                winner = runner
                story_draft = draft_story(winner, topic, duration)
            revision += 1
            continue

        _log(f"  Revising based on director notes...")
        revised = revise_story(story_draft, notes, winner)

        # Validate revision — keep original if revision is worse
        revised_scenes = revised.get("scenes", [])
        orig_scenes = story_draft.get("scenes", [])

        # Check if revision has real narration (not placeholders)
        has_real_narration = any(
            isinstance(s, dict) and len(s.get("narration", "")) > 20
            for s in revised_scenes
        )

        if has_real_narration and len(revised_scenes) >= len(orig_scenes) * 0.5:
            story_draft = revised
            _log(f"  Revised: {story_draft.get('title', '')}")
        else:
            _log(f"  Revision produced bad output (placeholder narration), keeping original")
        revision += 1

    # Build approved story — handle scenes that might be strings instead of dicts
    raw_scenes = story_draft.get("scenes", [])
    narrations = []
    clean_scenes = []
    for s in raw_scenes:
        if isinstance(s, dict):
            narrations.append(s.get("narration", ""))
            clean_scenes.append(s)
        elif isinstance(s, str):
            narrations.append(s)
            clean_scenes.append({"narration": s, "visual": s, "name": f"scene"})
    story_draft["scenes"] = clean_scenes

    return ApprovedStory(
        title=story_draft.get("title", topic),
        angle=winner,
        scenes=story_draft.get("scenes", []),
        narration_draft=narrations,
        director_notes=notes,
        revision_count=revision,
    )
