"""Step-level testing — run and benchmark individual pipeline stages.

Instead of running the full pipeline (5+ minutes), test one step at a time:
  python -m manimflow.step_test story "Indian judiciary system"
  python -m manimflow.step_test design output/test/story.json
  python -m manimflow.step_test code output/test/story.json
  python -m manimflow.step_test render output/test/scene.py

Each step loads the previous step's output, runs the current step,
saves the result, and benchmarks it.
"""

import json
import os
import sys
import time

from .writers_room import run_writers_room
from .design_system import generate_design_system
from .codegen import generate_manim_code
from .code_sanitizer import sanitize_code
from .spatial_analyzer import analyze_scene, print_spatial_analysis
from .renderer import render_scene, validate_code
from .reviewers.story_reviewer import StoryReviewer
from .reviewers.design_reviewer import DesignReviewer
from .reviewers.base import print_review


def test_story(topic: str, output_dir: str = "output/step_test"):
    """Test just the writers room — generate and benchmark a story."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n=== STEP TEST: Story Generation ===")
    print(f"Topic: {topic}")

    start = time.time()
    approved = run_writers_room(topic=topic, duration=120, max_revisions=2, verbose=True)
    elapsed = time.time() - start

    # Save
    story = {
        "title": approved.title,
        "duration_target": 120,
        "hook_question": approved.angle.hook,
        "scenes": approved.scenes,
    }
    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, "w") as f:
        json.dump(story, f, indent=2)

    # Benchmark
    reviewer = StoryReviewer()
    result = reviewer.review(artifact=story, context={"topic": topic})
    print_review(result)

    print(f"\n  Time: {elapsed:.0f}s")
    print(f"  Score: {result.score}/10")
    print(f"  Saved: {story_path}")
    return result.score


def test_design(story_path: str, output_dir: str = None):
    """Test just the design system — generate and benchmark from existing story."""
    with open(story_path) as f:
        story = json.load(f)

    if output_dir is None:
        output_dir = os.path.dirname(story_path)

    print(f"\n=== STEP TEST: Design System ===")
    print(f"Story: {story.get('title', '?')}")

    start = time.time()
    design = generate_design_system(story, angle_title=story.get("title", ""))
    elapsed = time.time() - start

    # Save
    design_path = os.path.join(output_dir, "design_system.json")
    with open(design_path, "w") as f:
        json.dump(design.to_dict(), f, indent=2)

    # Benchmark
    reviewer = DesignReviewer()
    result = reviewer.review(
        artifact=design.to_dict(),
        context={"topic": story.get("title", ""), "title": story.get("title", "")},
    )
    print_review(result)

    print(f"\n  Time: {elapsed:.0f}s")
    print(f"  Score: {result.score}/10")
    print(f"  Saved: {design_path}")
    return result.score


def test_code(story_path: str, output_dir: str = None):
    """Test just code generation — generate, sanitize, and analyze."""
    with open(story_path) as f:
        story = json.load(f)

    if output_dir is None:
        output_dir = os.path.dirname(story_path)

    print(f"\n=== STEP TEST: Code Generation ===")
    print(f"Story: {story.get('title', '?')}")

    start = time.time()
    code = generate_manim_code(story)

    # Sanitize
    code, fixes = sanitize_code(code)
    if fixes:
        print(f"  Sanitized {len(fixes)} issues")

    # Save code BEFORE validation (for debugging)
    code_path = os.path.join(output_dir, "scene.py")
    with open(code_path, "w") as f:
        f.write(code)

    # Validate syntax
    syntax = validate_code(code)
    if not syntax["valid"]:
        print(f"  SYNTAX ERROR: {syntax['error']}")
        print(f"  Saved (broken): {code_path}")
        return 0

    # Spatial analysis
    spatial = analyze_scene(code)
    print_spatial_analysis(spatial)

    elapsed = time.time() - start

    accum = sum(1 for w in spatial["warnings"] if "never FadeOut" in w)
    overlaps = len(spatial["issues"])

    print(f"\n  Time: {elapsed:.0f}s")
    print(f"  Lines: {len(code.splitlines())}")
    print(f"  Overlaps: {overlaps}")
    print(f"  Accumulation: {accum}")
    print(f"  Syntax: {'OK' if syntax['valid'] else 'ERROR'}")
    print(f"  Saved: {code_path}")

    # Score: fewer issues = better
    score = max(0, 10 - overlaps * 0.5 - accum * 0.3)
    print(f"  Score: {score:.1f}/10")
    return score


def test_render(scene_path: str, output_dir: str = None):
    """Test just rendering — does the code render without errors?"""
    with open(scene_path) as f:
        code = f.read()

    if output_dir is None:
        output_dir = os.path.dirname(scene_path)

    print(f"\n=== STEP TEST: Render ===")

    start = time.time()
    result = render_scene(code=code, output_dir=output_dir, quality="l")
    elapsed = time.time() - start

    if result["success"]:
        print(f"  RENDERED: {result['video_path']}")
        print(f"  Time: {elapsed:.0f}s")
        return 10
    else:
        error_lines = result["error"].strip().split("\n")
        for line in error_lines[-5:]:
            print(f"  {line}")
        print(f"  FAILED after {elapsed:.0f}s")
        return 0


def main():
    """CLI for step testing."""
    if len(sys.argv) < 3:
        print("Usage:")
        print('  uv run python -m manimflow.step_test story "topic"')
        print("  uv run python -m manimflow.step_test design output/test/story.json")
        print("  uv run python -m manimflow.step_test code output/test/story.json")
        print("  uv run python -m manimflow.step_test render output/test/scene.py")
        sys.exit(1)

    step = sys.argv[1]
    arg = sys.argv[2]

    if step == "story":
        test_story(arg)
    elif step == "design":
        test_design(arg)
    elif step == "code":
        test_code(arg)
    elif step == "render":
        test_render(arg)
    else:
        print(f"Unknown step: {step}")
        sys.exit(1)


if __name__ == "__main__":
    main()
