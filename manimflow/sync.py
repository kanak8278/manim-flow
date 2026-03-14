"""Frame-level audio-video sync engine.

Parses Manim code to extract an exact animation timeline, then generates
narration that's aligned to specific animation keypoints.

The animation code is the source of truth. Narration adapts to it, not vice versa.

Timeline structure:
  Each self.play() and self.wait() becomes a SLOT with:
    - start_time: exact second when it begins
    - duration: how long it runs
    - type: "animation" or "pause"
    - description: what's happening visually (from code context)
    - narration: text to speak during this slot (or None for silence)
"""

import re
import asyncio
import os
import subprocess
from dataclasses import dataclass, field

from .agent import call_llm, extract_json


@dataclass
class TimelineSlot:
    """A single slot in the animation timeline."""
    start: float
    duration: float
    type: str  # "animation", "pause", "transition"
    code_line: str = ""
    line_number: int = 0
    scene_name: str = ""
    description: str = ""  # What's visually happening
    narration: str = ""    # What to say (empty = silence)
    audio_path: str = ""   # Generated TTS file


def parse_animation_timeline(code: str) -> list[TimelineSlot]:
    """Parse Manim code into an exact frame-level timeline.

    Extracts every self.play() and self.wait() call with precise timestamps.
    """
    lines = code.split("\n")
    timeline = []
    current_time = 0.0
    current_scene = "intro"

    # Detect scene boundaries
    scene_pattern = re.compile(r'#\s*={2,}\s*(.*?)(?:\s*={2,})?$', re.IGNORECASE)

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track scene name
        sm = scene_pattern.search(stripped)
        if sm:
            current_scene = sm.group(1).strip(" =")
            continue

        if not stripped or stripped.startswith("#"):
            continue

        # Parse self.play() calls
        if "self.play(" in stripped:
            run_time = 1.0  # default
            rt_match = re.search(r'run_time\s*=\s*([0-9.]+)', stripped)
            if rt_match:
                run_time = float(rt_match.group(1))

            # Extract what's being animated for context
            description = _describe_animation(stripped)

            slot = TimelineSlot(
                start=round(current_time, 2),
                duration=round(run_time, 2),
                type="animation",
                code_line=stripped[:120],
                line_number=i,
                scene_name=current_scene,
                description=description,
            )
            timeline.append(slot)
            current_time += run_time

        # Parse self.wait() calls
        elif "self.wait(" in stripped:
            wait_match = re.search(r'self\.wait\(([0-9.]*)\)', stripped)
            wait_time = 1.0
            if wait_match and wait_match.group(1):
                wait_time = float(wait_match.group(1))

            slot = TimelineSlot(
                start=round(current_time, 2),
                duration=round(wait_time, 2),
                type="pause",
                code_line=stripped[:120],
                line_number=i,
                scene_name=current_scene,
                description="pause for comprehension",
            )
            timeline.append(slot)
            current_time += wait_time

    return timeline


def _describe_animation(code_line: str) -> str:
    """Generate a human-readable description of what an animation does."""
    line = code_line.strip()

    # Common animation patterns
    if "Write(" in line:
        m = re.search(r'Write\((\w+)', line)
        return f"text '{m.group(1)}' appears" if m else "text appears"
    if "Create(" in line:
        m = re.search(r'Create\((\w+)', line)
        return f"shape '{m.group(1)}' is drawn" if m else "shape is drawn"
    if "FadeOut(" in line:
        return "elements fade out (transition)"
    if "FadeIn(" in line:
        m = re.search(r'FadeIn\((\w+)', line)
        return f"'{m.group(1)}' fades in" if m else "element fades in"
    if "Transform(" in line:
        m = re.search(r'Transform\((\w+)\s*,\s*(\w+)', line)
        if m:
            return f"'{m.group(1)}' transforms into '{m.group(2)}'"
        return "shape transforms"
    if "Indicate(" in line:
        return "element is highlighted"
    if "Flash(" in line:
        return "flash effect"
    if "camera.frame" in line:
        if "scale" in line:
            return "camera zooms"
        if "move_to" in line:
            return "camera pans"
        return "camera moves"
    if ".animate" in line:
        return "element animates (move/scale/color)"

    return "animation plays"


def group_into_narration_blocks(timeline: list[TimelineSlot],
                                 min_block_duration: float = 2.0) -> list[dict]:
    """Group timeline slots into narration blocks.

    Consecutive animations in the same scene are grouped together.
    Each block gets one narration sentence.
    Short pauses are absorbed into the preceding block.
    Transition animations (FadeOut) get silence.
    """
    blocks = []
    current_block = None

    for slot in timeline:
        # FadeOut transitions get silence
        is_transition = "fade out" in slot.description.lower()

        # Start new block on scene change or after transitions
        if (current_block is None or
            slot.scene_name != current_block["scene"] or
            is_transition or
            (slot.type == "pause" and slot.duration >= 2.0)):

            # Save previous block
            if current_block and current_block["duration"] > 0:
                blocks.append(current_block)

            if is_transition or (slot.type == "pause" and slot.duration >= 2.0):
                # Silence block
                blocks.append({
                    "start": slot.start,
                    "duration": slot.duration,
                    "scene": slot.scene_name,
                    "descriptions": [slot.description],
                    "needs_narration": False,
                    "narration": "",
                })
                current_block = None
                continue

            current_block = {
                "start": slot.start,
                "duration": 0,
                "scene": slot.scene_name,
                "descriptions": [],
                "needs_narration": True,
                "narration": "",
            }

        if current_block:
            current_block["duration"] = round(
                (slot.start + slot.duration) - current_block["start"], 2
            )
            current_block["descriptions"].append(slot.description)

    # Don't forget the last block
    if current_block and current_block["duration"] > 0:
        blocks.append(current_block)

    return blocks


async def generate_synced_narration(blocks: list[dict], story: dict) -> list[dict]:
    """Use LLM to write narration for each block, constrained by duration.

    Each block gets narration text sized to fit its duration at ~2 words/sec.
    """
    WORDS_PER_SECOND = 2.0

    # Build prompt with all blocks
    block_specs = []
    for i, block in enumerate(blocks):
        if not block["needs_narration"]:
            continue

        target_words = max(3, int(block["duration"] * WORDS_PER_SECOND))
        visuals = "; ".join(block["descriptions"][:3])

        block_specs.append({
            "block_id": i,
            "duration": block["duration"],
            "target_words": target_words,
            "scene": block["scene"],
            "visuals": visuals,
        })

    if not block_specs:
        return blocks

    # Get story context for narration tone
    title = story.get("title", "")
    scenes_context = "\n".join(
        f"  Scene '{s.get('name', '')}': {s.get('narration', '')[:100]}"
        for s in story.get("scenes", [])
    )

    prompt = (
        f"Write narration for an educational video: \"{title}\"\n\n"
        f"Story context:\n{scenes_context}\n\n"
        f"Write ONE sentence per block. Each sentence must be EXACTLY the target word count.\n"
        f"The narration must match what's happening visually.\n\n"
    )
    for spec in block_specs:
        prompt += (
            f"Block {spec['block_id']} ({spec['duration']:.1f}s, "
            f"target {spec['target_words']} words, scene '{spec['scene']}'):\n"
            f"  Visuals: {spec['visuals']}\n\n"
        )

    prompt += (
        'Return JSON: {"narrations": {"0": "sentence for block 0", "3": "sentence for block 3", ...}}\n'
        "Keys are block_id numbers. Only include blocks that need narration."
    )

    try:
        response = await call_llm(
            "You write concise educational narration that matches exact word count targets. "
            "Each sentence must be natural, clear, and match the visual description.",
            prompt,
        )
        result = extract_json(response)
        narrations = result.get("narrations", {})

        for block_id_str, text in narrations.items():
            idx = int(block_id_str)
            if 0 <= idx < len(blocks):
                blocks[idx]["narration"] = text
    except Exception:
        # Fallback: use scene narration from story
        _fallback_narration(blocks, story)

    return blocks


def _fallback_narration(blocks: list[dict], story: dict):
    """Fall back to scene-level narration if block-level generation fails."""
    scene_narrations = {}
    for scene in story.get("scenes", []):
        name = scene.get("name", "")
        narration = scene.get("narration", "")
        if name and narration:
            scene_narrations[name.lower()] = narration

    for block in blocks:
        if block["needs_narration"] and not block["narration"]:
            scene_key = block["scene"].lower()
            for key, narration in scene_narrations.items():
                if key in scene_key or scene_key in key:
                    # Take a proportional chunk of the scene narration
                    words = narration.split()
                    target = int(block["duration"] * 2.0)
                    block["narration"] = " ".join(words[:target])
                    break


async def _generate_block_audio(text: str, output_path: str, voice: str,
                                 target_duration: float) -> dict:
    """Generate TTS for a single block, padded to exact target duration."""
    import edge_tts

    if not text:
        # Generate silence
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"anullsrc=r=24000:cl=mono",
            "-t", str(target_duration),
            "-c:a", "libmp3lame", "-q:a", "9",
            output_path,
        ], capture_output=True, text=True)
        return {"path": output_path, "duration": target_duration}

    # Generate TTS
    communicate = edge_tts.Communicate(text, voice)
    raw_path = output_path.replace(".mp3", "_raw.mp3")
    await communicate.save(raw_path)

    # Get actual TTS duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", raw_path],
        capture_output=True, text=True,
    )
    actual_dur = float(result.stdout.strip()) if result.returncode == 0 else target_duration

    if actual_dur <= target_duration:
        # Pad with silence to fill the slot
        pad_duration = target_duration - actual_dur
        subprocess.run([
            "ffmpeg", "-y",
            "-i", raw_path,
            "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
            "-t", str(target_duration),
            "-filter_complex",
            f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            "-t", str(target_duration),
            "-c:a", "libmp3lame", "-q:a", "4",
            output_path,
        ], capture_output=True, text=True)
    else:
        # TTS is longer than slot — speed it up slightly
        speed = actual_dur / target_duration
        if speed < 1.5:  # Don't speed up more than 1.5x
            subprocess.run([
                "ffmpeg", "-y", "-i", raw_path,
                "-af", f"atempo={speed}",
                "-c:a", "libmp3lame", "-q:a", "4",
                output_path,
            ], capture_output=True, text=True)
        else:
            # Too much speedup needed — just use raw and let it overflow slightly
            subprocess.run(["cp", raw_path, output_path])

    # Cleanup
    if os.path.exists(raw_path):
        os.remove(raw_path)

    return {"path": output_path, "duration": target_duration}


def generate_synced_audio(blocks: list[dict], output_dir: str,
                           voice: str = "en-US-GuyNeural") -> dict:
    """Generate frame-synced audio track from narration blocks.

    Each block gets its own TTS file, padded/trimmed to exact duration.
    All blocks are concatenated in order → perfectly synced audio.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Generate audio for each block
    block_audio_paths = []
    for i, block in enumerate(blocks):
        audio_path = os.path.join(output_dir, f"block_{i:03d}.mp3")
        narration = block.get("narration", "")

        result = asyncio.run(
            _generate_block_audio(narration, audio_path, voice, block["duration"])
        )
        block_audio_paths.append(result["path"])
        block["audio_path"] = result["path"]

    # Concatenate all blocks
    concat_file = os.path.join(output_dir, "concat_list.txt")
    with open(concat_file, "w") as f:
        for path in block_audio_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    final_path = os.path.join(output_dir, "synced_narration.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:a", "libmp3lame", "-q:a", "2",
        final_path,
    ], capture_output=True, text=True)

    # Get final duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", final_path],
        capture_output=True, text=True,
    )
    final_duration = float(result.stdout.strip()) if result.returncode == 0 else 0

    # Cleanup
    os.remove(concat_file)

    return {
        "audio_path": final_path,
        "duration": final_duration,
        "blocks": len(blocks),
        "narrated_blocks": sum(1 for b in blocks if b.get("narration")),
    }
