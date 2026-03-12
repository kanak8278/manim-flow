"""Main pipeline - orchestrates story → code → video generation with auto-fix loop."""

import json
import os
import time
from pathlib import Path

from .story import generate_story
from .codegen import generate_manim_code, fix_manim_code
from .renderer import render_scene, validate_code


def generate_video(
    topic: str,
    output_dir: str = "output",
    quality: str = "h",
    max_fix_attempts: int = 5,
    preview: bool = False,
    model: str = "claude-sonnet-4-20250514",
    verbose: bool = True,
) -> dict:
    """
    End-to-end: topic → video file.

    Args:
        topic: Math/physics question or equation
        output_dir: Where to save output
        quality: Render quality (l/m/h/k)
        max_fix_attempts: Max code fix iterations
        preview: Open video after render
        model: Claude model to use
        verbose: Print progress

    Returns:
        dict with success, video_path, story, code, attempts
    """
    os.makedirs(output_dir, exist_ok=True)
    _log = print if verbose else lambda *a, **k: None

    # ─── Step 1: Generate Story ───
    _log("\n╔══════════════════════════════════════╗")
    _log("║  ManimFlow Video Generation Pipeline ║")
    _log("╚══════════════════════════════════════╝")
    _log(f"\n📝 Topic: {topic}")
    _log("\n─── Step 1/3: Generating story script ───")

    story = generate_story(topic, model=model)

    # Save story
    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, "w") as f:
        json.dump(story, f, indent=2)

    _log(f"  ✓ Story: \"{story.get('title', 'Untitled')}\"")
    _log(f"  ✓ Scenes: {len(story.get('scenes', []))}")
    _log(f"  ✓ Saved to: {story_path}")

    # ─── Step 2: Generate Manim Code ───
    _log("\n─── Step 2/3: Generating Manim code ───")

    code = generate_manim_code(story, model=model)

    # Save initial code
    code_path = os.path.join(output_dir, "scene.py")
    with open(code_path, "w") as f:
        f.write(code)

    _log(f"  ✓ Generated {len(code.splitlines())} lines of Manim code")

    # Validate syntax first
    syntax = validate_code(code)
    if not syntax["valid"]:
        _log(f"  ⚠ Syntax error: {syntax['error']}")
        _log("  → Attempting fix...")
        code = fix_manim_code(code, syntax["error"], model=model)
        with open(code_path, "w") as f:
            f.write(code)

    # ─── Step 3: Render with Auto-Fix Loop ───
    _log("\n─── Step 3/3: Rendering video ───")

    attempt = 0
    last_error = None

    while attempt < max_fix_attempts:
        attempt += 1
        _log(f"\n  Attempt {attempt}/{max_fix_attempts}...")

        result = render_scene(
            code=code,
            output_dir=output_dir,
            quality=quality,
            preview=preview and attempt == max_fix_attempts,
        )

        if result["success"]:
            _log(f"\n  ✓ Video rendered successfully!")
            _log(f"  ✓ Output: {result['video_path']}")

            # Save final code
            with open(code_path, "w") as f:
                f.write(code)

            return {
                "success": True,
                "video_path": result["video_path"],
                "story": story,
                "code": code,
                "attempts": attempt,
                "story_path": story_path,
                "code_path": code_path,
            }
        else:
            last_error = result["error"]
            _log(f"  ✗ Render failed:")

            # Show condensed error
            error_lines = last_error.strip().split("\n")
            for line in error_lines[-10:]:
                _log(f"    {line}")

            if attempt < max_fix_attempts:
                _log(f"\n  → Auto-fixing (attempt {attempt + 1})...")
                code = fix_manim_code(code, last_error, model=model)

                # Save each attempt
                attempt_path = os.path.join(output_dir, f"scene_attempt_{attempt}.py")
                with open(attempt_path, "w") as f:
                    f.write(code)

                # Re-save as main scene file
                with open(code_path, "w") as f:
                    f.write(code)

    _log(f"\n  ✗ Failed after {max_fix_attempts} attempts")
    return {
        "success": False,
        "error": last_error,
        "story": story,
        "code": code,
        "attempts": attempt,
        "story_path": story_path,
        "code_path": code_path,
    }
