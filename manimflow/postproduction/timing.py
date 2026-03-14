"""Timing analysis — extract actual scene durations from Manim code.

Used to generate voiceover narration that matches the video's actual pacing,
instead of hoping the video matches the voiceover.

Flow: render video first → analyze code for scene timing → rewrite narration → generate TTS
"""

import re
import subprocess


def extract_scene_timings(code: str) -> list[dict]:
    """Parse Manim code to estimate actual duration of each scene section.

    Scans for scene boundary comments and sums up run_time + wait() within each.
    Returns list of {name, start_time, duration, end_time}.
    """
    lines = code.split("\n")
    scenes = []
    current_scene = None
    current_time = 0.0

    scene_pattern = re.compile(
        r'^\s*#\s*={2,}\s*(.*?)(?:\s*={2,})?\s*$|'  # # === SCENE NAME ===
        r'^\s*#\s*(?:Scene|Act|Section)\s*\d*[:\s]*(.*)',  # # Scene 1: Name
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip()

        # Detect scene boundary
        m = scene_pattern.match(stripped)
        if m:
            name = (m.group(1) or m.group(2) or "").strip(" =")
            if name:
                # Close previous scene
                if current_scene:
                    current_scene["duration"] = round(current_time - current_scene["start_time"], 1)
                    current_scene["end_time"] = round(current_time, 1)
                    scenes.append(current_scene)

                # Start new scene
                current_scene = {
                    "name": name,
                    "start_time": round(current_time, 1),
                    "duration": 0,
                    "end_time": 0,
                }
            continue

        # Accumulate time
        rt_match = re.search(r'run_time\s*=\s*([0-9.]+)', stripped)
        if rt_match:
            current_time += float(rt_match.group(1))
        elif "self.play(" in stripped and "run_time" not in stripped:
            current_time += 1.0  # default run_time

        wt_match = re.search(r'self\.wait\(([0-9.]*)\)', stripped)
        if wt_match:
            val = wt_match.group(1)
            current_time += float(val) if val else 1.0

    # Close last scene
    if current_scene:
        current_scene["duration"] = round(current_time - current_scene["start_time"], 1)
        current_scene["end_time"] = round(current_time, 1)
        scenes.append(current_scene)

    return scenes


def get_video_duration(video_path: str) -> float:
    """Get actual video duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return float(result.stdout.strip())
    return 0.0


async def rewrite_narration_for_timing(story: dict, scene_timings: list[dict]) -> dict:
    """Update story narration to fit actual video scene durations.

    Uses LLM to rewrite narration text so TTS output matches each scene's length.
    Rough rule: ~150 words per minute for clear narration = 2.5 words/second.
    """
    from ..core.agent import call_llm, extract_json

    WORDS_PER_SECOND = 2.0  # Conservative — ensures narration fits within scene duration

    scenes_with_budget = []
    for i, scene in enumerate(story.get("scenes", [])):
        # Find matching timing
        timing = scene_timings[i] if i < len(scene_timings) else None
        actual_dur = timing["duration"] if timing else scene.get("duration_seconds", 15)

        # Target word count for this scene
        target_words = int(actual_dur * WORDS_PER_SECOND)
        current_narration = scene.get("narration", "")
        current_words = len(current_narration.split())

        scenes_with_budget.append({
            "scene_id": scene.get("id", i + 1),
            "name": scene.get("name", f"scene_{i}"),
            "video_duration": actual_dur,
            "target_words": target_words,
            "current_narration": current_narration,
            "current_words": current_words,
            "needs_rewrite": abs(current_words - target_words) > target_words * 0.3,
        })

    # Only call LLM if narration needs significant rewriting
    needs_rewrite = [s for s in scenes_with_budget if s["needs_rewrite"]]
    if not needs_rewrite:
        return story  # Narration already fits

    prompt = (
        "Rewrite the narration for these video scenes to match their actual durations.\n"
        "Each scene has a target word count based on video timing (~2.5 words/second).\n"
        "Keep the same meaning and tone, just adjust length.\n\n"
    )
    for s in scenes_with_budget:
        prompt += (
            f"Scene '{s['name']}' ({s['video_duration']:.0f}s video, "
            f"target ~{s['target_words']} words, currently {s['current_words']} words):\n"
            f"  Current: \"{s['current_narration']}\"\n\n"
        )

    prompt += (
        "Return JSON: {\"narrations\": {\"scene_id\": \"rewritten narration text\", ...}}\n"
        "Only include scenes that need rewriting. Keep others unchanged."
    )

    try:
        response = await call_llm(
            "You rewrite educational narration to fit specific time budgets. "
            "Keep the same teaching content and tone.",
            prompt,
        )
        result = extract_json(response)

        # Apply rewrites
        narrations = result.get("narrations", {})
        for scene in story.get("scenes", []):
            scene_id = str(scene.get("id", ""))
            if scene_id in narrations:
                scene["narration"] = narrations[scene_id]

    except Exception:
        pass  # Keep original narration if rewrite fails

    return story
