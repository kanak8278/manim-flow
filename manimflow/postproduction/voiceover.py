"""Voiceover generation - converts narration text to speech and merges with video.

Uses edge-tts (Microsoft Edge TTS) for high-quality, free text-to-speech.
Then merges audio with the rendered video using ffmpeg.
"""

import asyncio
import os
import subprocess

# Fix SSL certs for edge-tts (uv-managed Python may lack system certs)
try:
    import truststore

    truststore.inject_into_ssl()
except Exception:
    try:
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except ImportError:
        pass


# Good voices for educational content
VOICES = {
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-JennyNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_au": "en-AU-WilliamNeural",
    "default": "en-US-GuyNeural",
}


async def _generate_tts(text: str, output_path: str, voice: str) -> dict:
    """Generate TTS audio file using edge-tts."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

    # Get duration using ffprobe
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            output_path,
        ],
        capture_output=True,
        text=True,
    )
    duration = float(result.stdout.strip()) if result.returncode == 0 else 0

    return {"path": output_path, "duration": duration}


def generate_voiceover(story: dict, output_dir: str, voice: str = "default") -> dict:
    """Generate voiceover audio from story narration.

    Combines all scene narrations into a single audio file with
    appropriate pauses between scenes.
    """
    os.makedirs(output_dir, exist_ok=True)
    voice_name = VOICES.get(voice, VOICES["default"])

    scenes = story.get("scenes", [])
    if not scenes:
        return {"error": "No scenes in story"}

    # Generate audio for each scene's narration
    scene_audios = []
    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "")
        if not narration:
            continue

        audio_path = os.path.join(output_dir, f"scene_{i:02d}.mp3")
        try:
            result = asyncio.run(_generate_tts(narration, audio_path, voice_name))
            scene_audios.append(
                {
                    "scene_id": scene.get("id", i),
                    "scene_name": scene.get("name", f"scene_{i}"),
                    "narration": narration,
                    "audio_path": result["path"],
                    "duration": result["duration"],
                }
            )
        except Exception as e:
            print(f"  TTS failed for scene {i}: {e}")
            continue

    if not scene_audios:
        return {"error": "No narration could be generated"}

    # Concatenate all scene audios with pauses
    final_audio = os.path.join(output_dir, "voiceover.mp3")
    _concatenate_with_pauses(scene_audios, final_audio, pause_seconds=1.0)

    total_duration = sum(s["duration"] for s in scene_audios)
    total_duration += (len(scene_audios) - 1) * 1.0

    return {
        "audio_path": final_audio,
        "scene_timings": scene_audios,
        "total_duration": total_duration,
        "voice": voice_name,
    }


def _concatenate_with_pauses(
    scene_audios: list, output_path: str, pause_seconds: float = 1.0
):
    """Concatenate audio files with silence gaps between them."""
    concat_dir = os.path.dirname(output_path)
    concat_file = os.path.join(concat_dir, "concat_list.txt")

    # Generate silence file
    silence_path = os.path.join(concat_dir, "silence.mp3")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=24000:cl=mono",
            "-t",
            str(pause_seconds),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "9",
            silence_path,
        ],
        capture_output=True,
        text=True,
    )

    # Build concat list
    with open(concat_file, "w") as f:
        for i, audio in enumerate(scene_audios):
            f.write(f"file '{os.path.abspath(audio['audio_path'])}'\n")
            if i < len(scene_audios) - 1:
                f.write(f"file '{os.path.abspath(silence_path)}'\n")

    # Concatenate
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            output_path,
        ],
        capture_output=True,
        text=True,
    )

    # Cleanup
    for f in [concat_file, silence_path]:
        if os.path.exists(f):
            os.remove(f)


def merge_video_audio(video_path: str, audio_path: str, output_path: str) -> dict:
    """Merge video and audio into final output."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            output_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {"success": False, "error": result.stderr}

    return {"success": True, "path": output_path}


def list_voices() -> list[dict]:
    """List available voice options."""
    return [
        {"id": k, "name": v, "description": k.replace("_", " ").title()}
        for k, v in VOICES.items()
        if k != "default"
    ]
