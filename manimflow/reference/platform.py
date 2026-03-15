"""Platform configuration — defines how content is shaped for different audiences and formats.

This is the control layer between the user's intent and the generation pipeline.
It determines: duration, pacing, complexity, visual style, music, transitions.
"""

from dataclasses import dataclass


@dataclass
class PlatformConfig:
    """Configuration that shapes every aspect of video generation."""

    # === FORMAT ===
    format: str = "standard"  # reel, short, standard, deep, documentary
    duration_seconds: int = 120
    aspect_ratio: str = "16:9"  # 16:9 (YouTube), 9:16 (Reels/TikTok/Shorts)

    # === AUDIENCE ===
    audience: str = "general"  # student, general, expert, child
    age_group: str = "16-35"
    prior_knowledge: str = "none"  # none, basic, intermediate, advanced
    language_level: str = "casual"  # formal, casual, playful

    # === CONTENT STYLE ===
    tone: str = "curious"  # curious, dramatic, playful, serious, awe
    pacing: str = "medium"  # fast (reels), medium (standard), slow (deep dive)
    humor_level: int = 2  # 0=none, 1=dry, 2=light, 3=frequent

    # === MUSIC & AUDIO ===
    music_style: str = "ambient"  # ambient, dramatic, upbeat, minimal, none
    voice: str | None = None  # male_us, female_us, male_uk, etc

    # === VISUAL STYLE ===
    color_palette: str = "3b1b"  # 3b1b (dark), bright, pastel, neon, monochrome
    animation_density: str = "medium"  # sparse (clean), medium, dense (fast-paced)
    text_density: str = "low"  # low (mostly visual), medium, high (more text)


# Pre-built platform presets
PLATFORM_PRESETS = {
    "youtube_standard": PlatformConfig(
        format="standard",
        duration_seconds=180,
        aspect_ratio="16:9",
        audience="general",
        pacing="medium",
        music_style="ambient",
        tone="curious",
        animation_density="medium",
    ),
    "youtube_deep": PlatformConfig(
        format="deep",
        duration_seconds=480,
        aspect_ratio="16:9",
        audience="general",
        pacing="slow",
        music_style="ambient",
        tone="curious",
        animation_density="medium",
        text_density="medium",
    ),
    "tiktok": PlatformConfig(
        format="reel",
        duration_seconds=60,
        aspect_ratio="9:16",
        audience="general",
        age_group="16-25",
        pacing="fast",
        music_style="upbeat",
        tone="playful",
        animation_density="dense",
        text_density="low",
        humor_level=3,
    ),
    "instagram_reel": PlatformConfig(
        format="reel",
        duration_seconds=30,
        aspect_ratio="9:16",
        audience="general",
        pacing="fast",
        music_style="upbeat",
        tone="dramatic",
        animation_density="dense",
        text_density="low",
    ),
    "youtube_shorts": PlatformConfig(
        format="short",
        duration_seconds=55,
        aspect_ratio="9:16",
        audience="general",
        pacing="fast",
        music_style="minimal",
        tone="curious",
        animation_density="dense",
    ),
    "educational": PlatformConfig(
        format="standard",
        duration_seconds=300,
        aspect_ratio="16:9",
        audience="student",
        prior_knowledge="basic",
        pacing="slow",
        music_style="minimal",
        tone="serious",
        language_level="formal",
        animation_density="medium",
        text_density="medium",
    ),
    "kids": PlatformConfig(
        format="short",
        duration_seconds=90,
        aspect_ratio="16:9",
        audience="child",
        age_group="8-14",
        pacing="medium",
        music_style="upbeat",
        tone="playful",
        humor_level=3,
        language_level="playful",
        animation_density="dense",
        color_palette="bright",
    ),
}


def get_platform_config(preset: str) -> PlatformConfig:
    """Get a preset platform configuration."""
    return PLATFORM_PRESETS.get(preset, PLATFORM_PRESETS["youtube_standard"])


def config_to_story_context(config: PlatformConfig) -> str:
    """Convert platform config into story generation context."""
    lines = ["TARGET PLATFORM & AUDIENCE:"]
    lines.append(
        f"- Format: {config.format} ({config.duration_seconds}s, {config.aspect_ratio})"
    )
    lines.append(
        f"- Audience: {config.audience} (age {config.age_group}, prior knowledge: {config.prior_knowledge})"
    )
    lines.append(f"- Tone: {config.tone}, humor level: {config.humor_level}/3")
    lines.append(f"- Language: {config.language_level}")

    # Pacing instructions
    if config.pacing == "fast":
        lines.append("- PACING: Fast cuts every 3-5s. Hook in first 2s. No dead time.")
        lines.append("- Max 2 sentences on screen at once. Visual-first.")
    elif config.pacing == "slow":
        lines.append("- PACING: Generous breathing room. 15-25s per concept.")
        lines.append("- Let ideas sink in. Multiple examples per concept.")
    else:
        lines.append("- PACING: Balanced. 10-15s per concept with natural transitions.")

    # Audience adaptation
    if config.audience == "child":
        lines.append("- Use simple language, avoid jargon, use fun analogies.")
        lines.append("- Make characters/objects anthropomorphic when possible.")
        lines.append("- Celebrate the 'wow' moments with big visual effects.")
    elif config.audience == "student":
        lines.append(
            "- Be precise with terminology but explain each term on first use."
        )
        lines.append("- Connect to exam-relevant concepts where appropriate.")
        lines.append("- Show problem-solving steps explicitly.")
    elif config.audience == "expert":
        lines.append("- Skip basic background. Assume notation familiarity.")
        lines.append("- Focus on the elegant/surprising aspects.")
        lines.append("- Show connections to related advanced topics.")

    # Visual density
    if config.animation_density == "dense":
        lines.append(
            "- Visual changes every 2-3 seconds. Dynamic, energetic animations."
        )
    elif config.animation_density == "sparse":
        lines.append(
            "- Clean, focused visuals. One element at a time. Let breathing room."
        )

    return "\n".join(lines)


def config_to_music_context(config: PlatformConfig) -> dict:
    """Generate music/audio directives from config."""
    music_map = {
        "ambient": {
            "description": "Soft ambient pads, low volume under narration",
            "energy": "low",
            "moments": {
                "hook": "slight volume swell",
                "reveal": "brief crescendo then back to ambient",
                "ending": "fade out over 3 seconds",
            },
        },
        "dramatic": {
            "description": "Building tension, crescendo at reveal moments",
            "energy": "building",
            "moments": {
                "hook": "tension-building percussion",
                "reveal": "full orchestral hit or bass drop",
                "ending": "triumphant resolution chord",
            },
        },
        "upbeat": {
            "description": "Energetic lo-fi or electronic beats",
            "energy": "high",
            "moments": {
                "hook": "beat drop",
                "reveal": "beat switch or bass boost",
                "ending": "quick fadeout",
            },
        },
        "minimal": {
            "description": "Quiet piano or no music, focus on narration",
            "energy": "minimal",
            "moments": {
                "hook": "single piano note",
                "reveal": "gentle chord progression",
                "ending": "silence",
            },
        },
        "none": {
            "description": "No background music",
            "energy": "none",
            "moments": {},
        },
    }
    return music_map.get(config.music_style, music_map["ambient"])


def list_presets() -> list[dict]:
    """List available platform presets."""
    return [
        {
            "id": name,
            "format": cfg.format,
            "duration": cfg.duration_seconds,
            "audience": cfg.audience,
            "aspect": cfg.aspect_ratio,
            "tone": cfg.tone,
        }
        for name, cfg in PLATFORM_PRESETS.items()
    ]
