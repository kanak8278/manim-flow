"""Narrative reviewer — evaluates and improves story scripts BEFORE code generation.

This catches bad storytelling early, when it's cheap to fix (just re-prompt the LLM).
After code generation, fixes are expensive (re-render, re-evaluate, etc).

Reviews:
- Hook quality (is the first 3 seconds grabbing?)
- Narrative arc (does it build to an aha moment?)
- Visual plannability (can each scene be animated?)
- Pacing (is each scene the right length?)
- Audience fit (is the language/complexity right for the target?)
"""

import json
from .agent import call_llm, extract_json


REVIEW_PROMPT = """You are a content strategist for educational math/physics videos.
Review this story script and score it. Return JSON.

SCORING CRITERIA:
1. HOOK (1-10): Does the opening grab attention in 3 seconds? Is it a question, paradox, or bold claim?
   10 = "I NEED to keep watching" | 5 = "Interesting, I guess" | 1 = "Today we'll learn about..."

2. NARRATIVE ARC (1-10): Does it build tension and resolve with an aha moment?
   10 = Clear buildup to a mind-blowing reveal | 5 = Logical but flat | 1 = Just lists facts

3. VISUAL PLAN (1-10): Can every scene be animated with shapes, curves, and diagrams?
   10 = Every scene has a clear visual | 5 = Some scenes are text-heavy | 1 = It's a lecture

4. PACING (1-10): Are scene durations appropriate for their content?
   10 = Perfect rhythm | 5 = Some scenes rushed/dragged | 1 = Monotone pacing

5. AUDIENCE FIT (1-10): Is the language and complexity right for the target audience?
   10 = Perfect level | 5 = Occasionally too hard/easy | 1 = Completely wrong level

Return JSON:
{
  "scores": {
    "hook": {"score": 8, "feedback": "specific feedback"},
    "narrative_arc": {"score": 7, "feedback": "..."},
    "visual_plan": {"score": 6, "feedback": "Scene 3 has no clear visual — needs a diagram"},
    "pacing": {"score": 7, "feedback": "..."},
    "audience_fit": {"score": 8, "feedback": "..."}
  },
  "overall_score": 7.2,
  "verdict": "PASS|IMPROVE|REJECT",
  "critical_fixes": ["Scene 3 needs a visual element", "Hook is too generic"],
  "improved_hook": "A stronger alternative hook suggestion",
  "scene_fixes": [
    {"scene_id": 3, "issue": "no visual", "fix": "Add a number line showing convergence"}
  ]
}

Score >= 7 = PASS. Score 5-7 = IMPROVE. Score < 5 = REJECT (regenerate from scratch)."""


async def review_narrative(story: dict, platform_context: str = "") -> dict:
    """Review a story script and return scores + improvement suggestions."""
    user_prompt = (
        f"Review this video story script:\n\n{json.dumps(story, indent=2)}\n\n"
    )
    if platform_context:
        user_prompt += f"Platform context:\n{platform_context}\n\n"
    user_prompt += "Return ONLY valid JSON."

    response = await call_llm(REVIEW_PROMPT, user_prompt)

    try:
        return extract_json(response)
    except (ValueError, json.JSONDecodeError):
        return {
            "scores": {},
            "overall_score": 5,
            "verdict": "IMPROVE",
            "critical_fixes": ["Review failed to parse"],
        }


async def improve_narrative(story: dict, review: dict) -> dict:
    """Improve a story based on review feedback. Returns improved story JSON."""
    from .story import STORY_SYSTEM_PROMPT_TEMPLATE, _get_duration_preset

    duration = story.get("duration_target", 120)
    preset = _get_duration_preset(duration)

    # Build improvement prompt from review feedback
    fixes = review.get("critical_fixes", [])
    scene_fixes = review.get("scene_fixes", [])
    improved_hook = review.get("improved_hook", "")

    feedback_lines = ["IMPROVE this story script based on this feedback:"]
    for fix in fixes:
        feedback_lines.append(f"  - {fix}")
    for sf in scene_fixes:
        feedback_lines.append(f"  - Scene {sf.get('scene_id')}: {sf.get('fix', sf.get('issue'))}")
    if improved_hook:
        feedback_lines.append(f"  - Better hook: \"{improved_hook}\"")

    system = STORY_SYSTEM_PROMPT_TEMPLATE.format(
        structure=preset["structure"],
        duration=duration,
    )

    user_prompt = (
        f"Here is the original story:\n\n{json.dumps(story, indent=2)}\n\n"
        + "\n".join(feedback_lines)
        + "\n\nReturn the IMPROVED story as valid JSON. Keep what works, fix what doesn't."
    )

    response = await call_llm(system, user_prompt)
    try:
        improved = extract_json(response)
        improved["category"] = story.get("category", "formula")
        return improved
    except (ValueError, json.JSONDecodeError):
        return story  # Return original if improvement fails


def print_narrative_review(review: dict):
    """Pretty-print narrative review results."""
    print("\n--- Narrative Review ---")
    scores = review.get("scores", {})
    for dim, data in scores.items():
        if isinstance(data, dict):
            score = data.get("score", "?")
            feedback = data.get("feedback", "")
            marker = "PASS" if isinstance(score, (int, float)) and score >= 7 else "WEAK"
            print(f"  [{marker}] {dim}: {score}/10 — {feedback[:80]}")

    overall = review.get("overall_score", "?")
    verdict = review.get("verdict", "?")
    print(f"\n  Overall: {overall}/10 — {verdict}")

    fixes = review.get("critical_fixes", [])
    if fixes:
        print(f"\n  Fixes needed:")
        for f in fixes[:5]:
            print(f"    - {f}")

    hook = review.get("improved_hook", "")
    if hook:
        print(f"\n  Suggested hook: \"{hook}\"")
