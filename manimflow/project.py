"""Project management — represents a complete video creation project.

A project ties together all the pieces: topic, platform config, story,
voiceover, music, rendered video, and metadata. This is the top-level
object that a web UI or batch system would work with.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any

from .platform import PlatformConfig, get_platform_config, PLATFORM_PRESETS
from .categories import suggest_category, CATEGORIES


@dataclass
class Project:
    """A complete video creation project."""

    # Identity
    id: str = ""
    created_at: float = 0

    # Input
    topic: str = ""
    category: str = ""
    platform: str = "youtube_standard"
    platform_config: dict = field(default_factory=dict)

    # Generated artifacts
    story: dict = field(default_factory=dict)
    narrative_review: dict = field(default_factory=dict)
    code: str = ""
    spatial_analysis: dict = field(default_factory=dict)

    # Output files
    video_path: str = ""
    audio_path: str = ""
    final_video_path: str = ""
    story_path: str = ""
    code_path: str = ""
    thumbnail_path: str = ""

    # Quality metrics
    code_eval: dict = field(default_factory=dict)
    vision_eval: dict = field(default_factory=dict)
    overall_score: float = 0
    render_attempts: int = 0

    # Status
    status: str = "draft"  # draft, generating, reviewing, rendering, complete, failed
    error: str = ""

    def save(self, output_dir: str):
        """Save project metadata to JSON."""
        path = os.path.join(output_dir, "project.json")
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, default=str)
        return path

    @classmethod
    def load(cls, path: str) -> "Project":
        """Load project from JSON."""
        with open(path) as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def create_project(
    topic: str,
    platform: str = "youtube_standard",
    category: str | None = None,
    voice: str | None = None,
) -> Project:
    """Create a new project with auto-detected settings."""
    if category is None:
        category = suggest_category(topic)

    config = get_platform_config(platform)
    if voice:
        config.voice = voice

    project = Project(
        id=f"proj_{int(time.time())}",
        created_at=time.time(),
        topic=topic,
        category=category,
        platform=platform,
        platform_config=asdict(config),
        status="draft",
    )

    return project


# ═══════════════════════════════════════════════════════
# CONTENT TYPES — the full taxonomy of educational video
# ═══════════════════════════════════════════════════════

CONTENT_TYPES = {
    # === CORE MATH/PHYSICS ===
    "concept_explainer": {
        "name": "Concept Explainer",
        "description": "What is X? Why does it work?",
        "examples": ["What is a derivative?", "Why does gravity bend light?"],
        "best_categories": ["proof", "formula", "how_it_works"],
        "best_duration": 120,
    },
    "visual_proof": {
        "name": "Visual Proof",
        "description": "Prove something using only visuals — minimal text",
        "examples": ["Pythagorean theorem visual proof", "Area of circle by slicing"],
        "best_categories": ["proof", "visual_beauty"],
        "best_duration": 90,
    },
    "paradox": {
        "name": "Paradox / Mind-Bender",
        "description": "Something that seems impossible but is true",
        "examples": ["0.999... = 1", "Monty Hall", "Birthday Paradox"],
        "best_categories": ["mind_blown"],
        "best_duration": 120,
    },
    "thought_experiment": {
        "name": "Thought Experiment",
        "description": "What would happen if...?",
        "examples": ["What if pi was 3?", "What if gravity doubled?"],
        "best_categories": ["what_if"],
        "best_duration": 120,
    },

    # === REAL-WORLD CONNECTION ===
    "math_behind": {
        "name": "The Math Behind...",
        "description": "Reveal the hidden math in everyday things",
        "examples": ["Math behind GPS", "Math behind music", "Math behind encryption"],
        "best_categories": ["how_it_works"],
        "best_duration": 180,
    },
    "history_of": {
        "name": "History of Discovery",
        "description": "The human story behind a mathematical discovery",
        "examples": ["How Euler found e", "Newton vs Leibniz calculus war"],
        "best_categories": ["formula"],
        "best_duration": 300,
    },

    # === VISUAL / AESTHETIC ===
    "mathematical_art": {
        "name": "Mathematical Art",
        "description": "Beautiful visual patterns from simple equations",
        "examples": ["Butterfly curve", "Mandelbrot set", "Lissajous curves"],
        "best_categories": ["visual_beauty"],
        "best_duration": 90,
    },

    # === SHORT-FORM ===
    "quick_explainer": {
        "name": "Quick Explainer",
        "description": "One concept in 60 seconds or less",
        "examples": ["Why can't you divide by zero?", "What's the golden ratio?"],
        "best_categories": ["quick_fact"],
        "best_duration": 60,
    },
    "math_trick": {
        "name": "Math Trick",
        "description": "A clever technique or shortcut",
        "examples": ["Multiply by 11 trick", "Checking divisibility", "Squaring numbers near 50"],
        "best_categories": ["quick_fact"],
        "best_duration": 45,
    },
    "challenge": {
        "name": "Can You Solve This?",
        "description": "Pose a puzzle, let viewer think, reveal answer",
        "examples": ["The 100 prisoners problem", "How many squares on a chessboard?"],
        "best_categories": ["mind_blown"],
        "best_duration": 90,
    },

    # === SERIES / CURRICULUM ===
    "lesson": {
        "name": "Structured Lesson",
        "description": "Part of a learning series with prerequisites",
        "examples": ["Calculus 1: Limits", "Linear Algebra: Vectors"],
        "best_categories": ["proof", "formula"],
        "best_duration": 300,
    },
}


def list_content_types() -> list[dict]:
    """List all available content types."""
    return [
        {"id": k, "name": v["name"], "description": v["description"],
         "duration": v["best_duration"], "examples": v["examples"][:2]}
        for k, v in CONTENT_TYPES.items()
    ]
