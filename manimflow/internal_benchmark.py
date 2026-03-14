"""Internal benchmark — 10 fixed examples we test every change against.

Run: uv run python -m manimflow.internal_benchmark
Generates code for each topic, renders, extracts frames, scores.
Saves results for comparison across iterations.
"""

import json
import os
import time
import subprocess
from datetime import datetime

from .codegen import generate_manim_code
from .code_sanitizer import sanitize_code
from .spatial_analyzer import analyze_scene
from .renderer import render_scene, validate_code
from .reviewers.design_reviewer import DesignReviewer
from .reviewers.base import print_review


BENCHMARK_TOPICS = [
    # Math
    {"id": "circle_area", "topic": "Why is the area of a circle pi*r^2?", "type": "math"},
    {"id": "pythagorean", "topic": "Visual proof of the Pythagorean theorem", "type": "math"},
    {"id": "derivative", "topic": "What is a derivative? The slope at any point.", "type": "math"},
    # Physics
    {"id": "gravity_light", "topic": "How does gravity bend light?", "type": "physics"},
    {"id": "gps", "topic": "How does GPS use relativity?", "type": "physics"},
    # Mind blown
    {"id": "monty_hall", "topic": "The Monty Hall Problem", "type": "mind_blown"},
    {"id": "point_999", "topic": "Why is 0.999... exactly equal to 1?", "type": "mind_blown"},
    # Non-math/non-physics
    {"id": "judiciary", "topic": "Explain the Indian judiciary system", "type": "systems"},
    {"id": "democracy", "topic": "How does democracy work? Three branches of government.", "type": "systems"},
    {"id": "internet", "topic": "How does the internet actually work?", "type": "systems"},
]


def run_code_benchmark(topic_id: str = None, output_base: str = "benchmark_output"):
    """Run code generation + spatial analysis benchmark for one or all topics."""
    topics = BENCHMARK_TOPICS
    if topic_id:
        topics = [t for t in topics if t["id"] == topic_id]

    os.makedirs(output_base, exist_ok=True)
    results = []

    for t in topics:
        tid = t["id"]
        topic = t["topic"]
        print(f"\n{'='*60}")
        print(f"BENCHMARK: {tid} — {topic}")
        print(f"{'='*60}")

        output_dir = os.path.join(output_base, tid)
        os.makedirs(output_dir, exist_ok=True)

        # Create a proper story with real narration for code generation
        story = {
            "title": topic,
            "duration_target": 90,
            "scenes": [
                {
                    "id": 1, "name": "hook", "duration_seconds": 15,
                    "narration": f"What if I told you there is something surprising about {topic}? Let me show you.",
                    "visual": "Opening hook with a surprising visual that grabs attention",
                    "teaching_goal": "Grab attention and create curiosity",
                },
                {
                    "id": 2, "name": "setup", "duration_seconds": 20,
                    "narration": f"To understand this, we first need to see the basics. Here is how {topic} is structured.",
                    "visual": "Clear diagram showing the basic structure or components",
                    "teaching_goal": "Establish the foundational concepts",
                },
                {
                    "id": 3, "name": "build", "duration_seconds": 25,
                    "narration": "Now watch what happens when we look deeper. This is where it gets interesting.",
                    "visual": "Progressive build-up showing how components interact and connect",
                    "teaching_goal": "Build understanding step by step",
                },
                {
                    "id": 4, "name": "reveal", "duration_seconds": 15,
                    "narration": "And here is the key insight that makes everything click.",
                    "visual": "The aha moment — a dramatic visual reveal of the core insight",
                    "teaching_goal": "The aha moment — everything connects",
                },
                {
                    "id": 5, "name": "conclusion", "duration_seconds": 15,
                    "narration": f"So that is why {topic} works this way. Next time you see this, you will understand.",
                    "visual": "Clean summary showing the complete picture",
                    "teaching_goal": "Reinforce the insight and leave a lasting impression",
                },
            ],
        }

        # Generate code
        start = time.time()
        try:
            code = generate_manim_code(story)
            code, fixes = sanitize_code(code)
            gen_time = time.time() - start
        except Exception as e:
            print(f"  CODE GEN FAILED: {e}")
            results.append({"id": tid, "code_gen": "FAILED", "error": str(e)})
            continue

        # Save code
        code_path = os.path.join(output_dir, "scene.py")
        with open(code_path, "w") as f:
            f.write(code)

        # Validate syntax
        syntax = validate_code(code)
        if not syntax["valid"]:
            print(f"  SYNTAX ERROR: {syntax['error']}")
            results.append({"id": tid, "syntax": "FAILED", "error": syntax["error"]})
            continue

        # Spatial analysis
        spatial = analyze_scene(code)
        overlaps = len(spatial["issues"])
        accum = sum(1 for w in spatial["warnings"] if "never FadeOut" in w)
        underutil = sum(1 for w in spatial["warnings"] if "underutil" in w)
        lines = len(code.splitlines())

        # Try rendering with fix loop (up to 3 attempts)
        render_start = time.time()
        rendered = False
        render_result = None
        for attempt in range(3):
            render_result = render_scene(code=code, output_dir=output_dir, quality="l")
            if render_result["success"]:
                rendered = True
                break
            # Fix and retry
            from .codegen import fix_manim_code
            code = fix_manim_code(code, render_result["error"])
            code, _ = sanitize_code(code)
            with open(code_path, "w") as f:
                f.write(code)
        render_time = time.time() - render_start

        # Extract best frame (try multiple timestamps, pick largest file = most content)
        frame_path = ""
        if rendered and render_result.get("video_path"):
            video_path = render_result["video_path"]
            dur_result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", video_path],
                capture_output=True, text=True,
            )
            if dur_result.returncode == 0:
                duration = float(dur_result.stdout.strip())
                candidates = []
                for pct in [0.2, 0.4, 0.6, 0.8]:
                    ts = max(0.5, duration * pct)
                    cand_path = os.path.join(output_dir, f"frame_cand_{int(pct*100)}.png")
                    subprocess.run(
                        ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
                         "-vframes", "1", "-q:v", "2", cand_path],
                        capture_output=True, text=True,
                    )
                    if os.path.exists(cand_path):
                        candidates.append((cand_path, os.path.getsize(cand_path)))

                if candidates:
                    # Pick frame with most visual content (largest file size)
                    best = max(candidates, key=lambda c: c[1])
                    frame_path = os.path.join(output_dir, "key_frame.png")
                    subprocess.run(["cp", best[0], frame_path])
                    # Cleanup candidates
                    for c, _ in candidates:
                        if c != frame_path and os.path.exists(c):
                            os.remove(c)

        # Score
        code_score = max(0, 10 - overlaps * 0.5 - accum * 0.3 - underutil * 0.2)

        result = {
            "id": tid,
            "topic": topic,
            "type": t["type"],
            "lines": lines,
            "syntax": "OK",
            "overlaps": overlaps,
            "accumulation": accum,
            "underutilized": underutil,
            "rendered": rendered,
            "code_score": round(code_score, 1),
            "gen_time": round(gen_time, 1),
            "render_time": round(render_time, 1) if rendered else None,
            "frame_path": frame_path if os.path.exists(frame_path) else "",
            "sanitizer_fixes": len(fixes),
        }
        results.append(result)

        status = "RENDERED" if rendered else "RENDER FAILED"
        print(f"  {status} | Score: {code_score:.1f}/10 | Overlaps: {overlaps} | Lines: {lines} | Time: {gen_time:.0f}s")

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY ({len(results)} topics)")
    print(f"{'='*60}")

    rendered_count = sum(1 for r in results if r.get("rendered"))
    scores = [r["code_score"] for r in results if "code_score" in r]
    overlaps_total = sum(r.get("overlaps", 0) for r in results)

    print(f"  Rendered: {rendered_count}/{len(results)}")
    if scores:
        print(f"  Avg score: {sum(scores)/len(scores):.1f}/10")
        print(f"  Min score: {min(scores):.1f}/10")
        print(f"  Max score: {max(scores):.1f}/10")
    print(f"  Total overlaps: {overlaps_total}")

    print(f"\n  Per-topic:")
    for r in results:
        score = r.get("code_score", "?")
        rendered = "OK" if r.get("rendered") else "FAIL"
        print(f"    {r['id']:15s}: score={score}/10, render={rendered}, overlaps={r.get('overlaps', '?')}")

    # Save results
    results_path = os.path.join(output_base, "benchmark_results.json")
    entry = {"timestamp": datetime.now().isoformat(), "results": results}

    history = []
    if os.path.exists(results_path):
        with open(results_path) as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    history.append(entry)
    with open(results_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"\n  Saved: {results_path}")
    return results


def main():
    import sys
    topic_id = sys.argv[1] if len(sys.argv) > 1 else None
    run_code_benchmark(topic_id)


if __name__ == "__main__":
    main()
