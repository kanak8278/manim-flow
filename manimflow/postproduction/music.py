"""Music and sound design system.

Manages background music selection, volume ducking during narration,
and sound effects for emphasis moments (reveal, transition, etc).

Currently uses generated silence/tones. Can be extended with:
- YouTube Audio Library (royalty-free)
- Epidemic Sound API
- AI-generated music (Suno, Udio)
"""

import subprocess
import os


# Music mood presets (describes what to generate or select)
MUSIC_MOODS = {
    "ambient_curious": {
        "description": "Soft pads with gentle movement. Wonder and exploration.",
        "bpm": 72,
        "energy": "low",
        "instruments": "synth pads, soft piano",
        "use_for": ["proof", "how_it_works", "formula"],
    },
    "building_tension": {
        "description": "Starts quiet, builds to a crescendo. For paradoxes and reveals.",
        "bpm": 90,
        "energy": "building",
        "instruments": "strings, subtle percussion",
        "use_for": ["mind_blown", "what_if"],
    },
    "upbeat_playful": {
        "description": "Energetic lo-fi beat. For quick facts and challenges.",
        "bpm": 110,
        "energy": "high",
        "instruments": "lo-fi drums, synth bass, keys",
        "use_for": ["quick_fact", "challenge"],
    },
    "dramatic_reveal": {
        "description": "Cinematic tension building to a dramatic payoff.",
        "bpm": 80,
        "energy": "dramatic",
        "instruments": "orchestra, timpani, brass",
        "use_for": ["mind_blown"],
    },
    "gentle_wonder": {
        "description": "Delicate and beautiful. For mathematical art and visual beauty.",
        "bpm": 60,
        "energy": "minimal",
        "instruments": "piano, celeste, harp",
        "use_for": ["visual_beauty"],
    },
}


def select_mood(category: str) -> str:
    """Select the best music mood for a content category."""
    for mood_id, mood in MUSIC_MOODS.items():
        if category in mood["use_for"]:
            return mood_id
    return "ambient_curious"


def generate_ambient_track(
    output_path: str, duration: float, mood: str = "ambient_curious"
) -> dict:
    """Generate a simple ambient background track using ffmpeg.

    This creates a basic sine-wave pad as placeholder music.
    For production, replace with actual music library integration.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    mood_config = MUSIC_MOODS.get(mood, MUSIC_MOODS["ambient_curious"])
    mood_config["bpm"]

    # Generate a quiet ambient drone using ffmpeg's audio synthesis
    # Multiple sine waves at different frequencies for a pad-like sound
    frequencies = {
        "ambient_curious": "220:v=0.03|330:v=0.02|440:v=0.01",
        "building_tension": "110:v=0.04|165:v=0.02|220:v=0.02",
        "upbeat_playful": "440:v=0.03|550:v=0.02|660:v=0.01",
        "dramatic_reveal": "110:v=0.05|220:v=0.03|330:v=0.02",
        "gentle_wonder": "330:v=0.02|495:v=0.015|660:v=0.01",
    }

    frequencies.get(mood, frequencies["ambient_curious"])

    # Generate layered ambient pad with multiple frequencies for richer sound
    # Base note + fifth + octave creates a pleasant chord
    base_freqs = {
        "ambient_curious": (220, 330, 440),  # A minor chord
        "building_tension": (146, 220, 293),  # D minor
        "upbeat_playful": (261, 329, 392),  # C major
        "dramatic_reveal": (174, 220, 293),  # F minor
        "gentle_wonder": (261, 392, 523),  # C major (higher)
    }
    freqs = base_freqs.get(mood, (220, 330, 440))
    fade_out_start = max(0, duration - 3)

    # Generate three sine waves and mix them for a pad-like sound
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={freqs[0]}:sample_rate=44100:duration={duration}",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={freqs[1]}:sample_rate=44100:duration={duration}",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency={freqs[2]}:sample_rate=44100:duration={duration}",
        "-filter_complex",
        f"[0:a]volume=0.03[a];"
        f"[1:a]volume=0.02[b];"
        f"[2:a]volume=0.015[c];"
        f"[a][b][c]amix=inputs=3[mixed];"
        f"[mixed]lowpass=f=2000,highpass=f=80,"
        f"afade=t=in:st=0:d=3,"
        f"afade=t=out:st={fade_out_start}:d=3[out]",
        "-map",
        "[out]",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "4",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {"success": False, "error": result.stderr}

    return {"success": True, "path": output_path, "duration": duration, "mood": mood}


def mix_audio_tracks(
    voiceover_path: str, music_path: str, output_path: str, music_volume: float = 0.15
) -> dict:
    """Mix voiceover with background music, ducking music under speech.

    Uses ffmpeg's sidechaincompress to automatically lower music when speech is present.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        voiceover_path,
        "-i",
        music_path,
        "-filter_complex",
        f"[1:a]volume={music_volume}[music];"
        f"[music][0:a]sidechaincompress=threshold=0.02:ratio=6:attack=200:release=1000[ducked];"
        f"[0:a][ducked]amix=inputs=2:duration=first[out]",
        "-map",
        "[out]",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "2",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Fallback: simple mix without ducking
        cmd_simple = [
            "ffmpeg",
            "-y",
            "-i",
            voiceover_path,
            "-i",
            music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first[out]",
            "-map",
            "[out]",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            output_path,
        ]
        result = subprocess.run(cmd_simple, capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

    return {"success": True, "path": output_path}
