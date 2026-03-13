"""Main pipeline - orchestrates story -> code -> evaluate -> improve -> video."""

import json
import os
import subprocess

from .story import generate_story
from .codegen import generate_manim_code, fix_manim_code
from .renderer import render_scene, validate_code
from .evaluator import (
    static_code_checks, evaluate_frames_with_code, evaluate_video_frames,
    print_evaluation,
)
from .spatial_analyzer import analyze_scene, print_spatial_analysis
from .code_sanitizer import sanitize_code
from .voiceover import generate_voiceover, merge_video_audio
from .music import select_mood, generate_ambient_track, mix_audio_tracks
from .thumbnail import generate_thumbnail_with_title
from .timing import extract_scene_timings, rewrite_narration_for_timing, get_video_duration
from .code_editor import surgical_fix
from .platform import PlatformConfig, get_platform_config, config_to_story_context
from .narrative_reviewer import review_narrative, improve_narrative, print_narrative_review


def generate_video(
    topic: str,
    output_dir: str = "output",
    quality: str = "h",
    duration: int = 120,
    category: str | None = None,
    platform: str | None = None,
    voice: str | None = None,
    max_fix_attempts: int = 5,
    max_quality_loops: int = 2,
    preview: bool = False,
    verbose: bool = True,
) -> dict:
    """
    End-to-end: topic -> story -> code -> evaluate -> fix -> render -> video.

    The pipeline has two feedback loops:
    1. Render loop: fix code until it compiles/renders (max_fix_attempts)
    2. Quality loop: evaluate rendered output and improve (max_quality_loops)
    """
    os.makedirs(output_dir, exist_ok=True)
    _log = print if verbose else lambda *a, **k: None

    # === Step 1: Generate Story ===
    _log("\n======================================")
    _log("  ManimFlow Video Generation Pipeline")
    _log("======================================")
    _log(f"\nTopic: {topic}")

    # Load platform config
    platform_config = get_platform_config(platform) if platform else PlatformConfig(duration_seconds=duration)
    if platform:
        duration = platform_config.duration_seconds
        if not voice and platform_config.voice:
            voice = platform_config.voice

    platform_context = config_to_story_context(platform_config)

    _log("\n--- Step 1/5: Generating story script ---")

    story = generate_story(topic, duration_seconds=duration, category=category)

    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, "w") as f:
        json.dump(story, f, indent=2)

    _log(f"  Story: \"{story.get('title', 'Untitled')}\"")
    _log(f"  Scenes: {len(story.get('scenes', []))}")

    # === Step 1.5: Narrative review — catch bad stories before code generation ===
    _log("\n--- Step 1.5/5: Narrative review ---")
    narrative_review = review_narrative(story, platform_context)

    if verbose:
        print_narrative_review(narrative_review)

    narrative_score = narrative_review.get("overall_score", 0)
    narrative_verdict = narrative_review.get("verdict", "IMPROVE")

    if isinstance(narrative_score, (int, float)) and narrative_score < 6:
        _log(f"  Narrative score {narrative_score}/10 — improving story...")
        story = improve_narrative(story, narrative_review)
        with open(story_path, "w") as f:
            json.dump(story, f, indent=2)
        _log(f"  Improved story: \"{story.get('title', 'Untitled')}\"")

    # === Step 2: Generate Manim Code (VIDEO FIRST — audio adapts to video later) ===
    _log("\n--- Step 2: Generating Manim code ---")

    code = generate_manim_code(story)
    code_path = os.path.join(output_dir, "scene.py")
    with open(code_path, "w") as f:
        f.write(code)

    _log(f"  Generated {len(code.splitlines())} lines")

    # Sanitize: fix common LLM mistakes (rate funcs, colors, positions)
    code, sanitize_fixes = sanitize_code(code)
    if sanitize_fixes:
        _log(f"  Sanitized {len(sanitize_fixes)} issues:")
        for fix in sanitize_fixes[:5]:
            _log(f"    {fix}")
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 2.5: Static checks before rendering ===
    _log("\n--- Step 2.5: Static code checks ---")
    static = static_code_checks(code)

    for issue in static["issues"]:
        _log(f"  [ISSUE] {issue}")
    for warning in static["warnings"]:
        _log(f"  [WARN] {warning}")
    _log(f"  Estimated duration: ~{static['estimated_duration']:.0f}s")

    if not static["pass"]:
        _log("  Static checks found issues, attempting fix...")
        issues_text = "\n".join(static["issues"] + static["warnings"])
        code = fix_manim_code(code, f"Static analysis issues:\n{issues_text}")
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 2.7: Spatial analysis (overlap, off-screen, empty screen) ===
    _log("\n--- Step 2.7: Spatial layout analysis ---")
    spatial = analyze_scene(code)

    if verbose:
        print_spatial_analysis(spatial)

    spatial_issues = spatial["issues"]
    spatial_warnings = spatial["warnings"]
    all_spatial = spatial_issues + [w for w in spatial_warnings if "off-screen" in w or "never FadeOut" in w]

    if all_spatial:
        _log(f"  {len(spatial_issues)} issues, {len(spatial_warnings)} warnings — fixing...")
        # Cap issues sent to LLM — it only needs a summary, not 800 lines
        fix_prompt = _build_spatial_fix_prompt(all_spatial[:30], spatial.get("elements", {}))
        code = fix_manim_code(code, fix_prompt)
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 3: Render with Auto-Fix Loop ===
    _log("\n--- Step 3/4: Rendering video ---")

    render_result = _render_with_fixes(code, output_dir, quality, max_fix_attempts, _log)

    if not render_result["success"]:
        return {
            "success": False,
            "error": render_result["error"],
            "story": story,
            "code": render_result["code"],
            "attempts": render_result["attempts"],
            "story_path": story_path,
            "code_path": code_path,
        }

    code = render_result["code"]
    video_path = render_result["video_path"]

    # Save working code
    with open(code_path, "w") as f:
        f.write(code)

    # === Step 4: Quality Evaluation Loop ===
    _log("\n--- Step 4/4: Quality evaluation ---")

    evaluation = {}

    for quality_round in range(max_quality_loops):
        _log(f"\n  Quality round {quality_round + 1}/{max_quality_loops}...")

        # Step 4a: Vision-based frame evaluation
        vision_feedback = []
        if video_path:
            _log("  Running frame-based vision analysis...")
            frame_eval = evaluate_video_frames(video_path, story, output_dir)
            visual_score = frame_eval.get("overall_visual_score", None)
            visual_issues = frame_eval.get("visual_issues", [])
            semantic_issues = frame_eval.get("semantic_issues", [])
            if visual_score:
                _log(f"  Vision score: {visual_score}/10")
            if semantic_issues:
                for issue in semantic_issues[:3]:
                    _log(f"    [SEMANTIC] {issue}")
            if visual_issues:
                for issue in visual_issues[:3]:
                    _log(f"    [VISION] {issue}")
                vision_feedback = visual_issues + [f"SEMANTIC: {s}" for s in semantic_issues]

        # Step 4b: Code-based evaluation
        evaluation = evaluate_frames_with_code(code, story)

        if verbose:
            print_evaluation(evaluation)

        verdict = evaluation.get("verdict", "FAIL")
        overall = evaluation.get("overall_score", 0)

        # Fallback: compute overall from individual scores if parse failed
        if not isinstance(overall, (int, float)) or overall == 0:
            scores = evaluation.get("scores", {})
            score_vals = [
                s.get("score", 5) for s in scores.values()
                if isinstance(s, dict) and isinstance(s.get("score"), (int, float))
            ]
            if score_vals:
                overall = sum(score_vals) / len(score_vals)
                evaluation["overall_score"] = overall
            if verdict in ("?", ""):
                verdict = "PASS" if overall >= 7 else "NEEDS_FIXES" if overall >= 5 else "FAIL"
                evaluation["verdict"] = verdict

        # Combine vision + code scores — vision is ground truth
        combined_score = overall
        if visual_score and isinstance(visual_score, (int, float)):
            # Weight: 40% vision, 60% code analysis
            combined_score = 0.4 * visual_score + 0.6 * overall
            if visual_score < 5:
                # Vision veto: if frames look bad, don't accept regardless of code score
                combined_score = min(combined_score, 6.0)
                _log(f"  Vision veto: frames scored {visual_score}/10, capping combined to {combined_score:.1f}")

        if verdict == "PASS" and combined_score >= 7:
            _log(f"  Quality PASSED (code: {overall}/10, vision: {visual_score}/10, combined: {combined_score:.1f}/10)")
            break

        if quality_round < max_quality_loops - 1:
            _log(f"  Quality needs improvement (combined: {combined_score:.1f}/10), regenerating...")

            # Build improvement feedback combining code analysis + vision
            critical = evaluation.get("critical_issues", [])
            suggestions = evaluation.get("suggestions", [])
            all_feedback = critical[:5] + suggestions[:3]

            # Vision feedback gets priority if vision score is low
            if vision_feedback:
                if visual_score and visual_score < 6:
                    # Vision issues are critical — put them first
                    all_feedback = [f"[CRITICAL VISION] {v}" for v in vision_feedback[:5]] + all_feedback[:3]
                else:
                    all_feedback += [f"[VISION] {v}" for v in vision_feedback[:3]]

            feedback = "Fix these issues:\n" + "\n".join(all_feedback)

            # Use surgical editor (targeted edits) instead of full rewrite
            # This prevents re-introducing bugs the sanitizer already fixed
            _log("  Applying surgical fixes...")
            new_code = surgical_fix(code, feedback)
            if new_code != code:
                code = new_code
            else:
                # Surgical fix didn't change anything — fall back to full rewrite
                _log("  Surgical fix had no effect, trying full rewrite...")
                code = fix_manim_code(code, feedback)
            code, _ = sanitize_code(code)
            with open(code_path, "w") as f:
                f.write(code)

            # Re-render with improved code
            render_result = _render_with_fixes(code, output_dir, quality, max_fix_attempts, _log)
            if render_result["success"]:
                code = render_result["code"]
                video_path = render_result["video_path"]
                with open(code_path, "w") as f:
                    f.write(code)
            else:
                _log("  Re-render failed, keeping previous version")
                break
        else:
            _log(f"  Accepting current quality (score: {overall}/10)")

    # === Step 5: Add Background Music ===
    # Note: Voiceover is now baked into the render via manim-voiceover.
    # We only need to add background music on top.
    final_video_path = video_path

    if voice:
        _log("\n--- Step 5: Adding background music ---")
        try:
            video_dur = get_video_duration(video_path)
            category = story.get("category", "formula")
            mood = select_mood(category)

            vo_dir = os.path.join(output_dir, "audio")
            os.makedirs(vo_dir, exist_ok=True)

            music_path = os.path.join(vo_dir, "background_music.mp3")
            music_result = generate_ambient_track(music_path, video_dur + 5, mood=mood)

            if music_result.get("success"):
                _log(f"  Background music: {mood} ({video_dur:.0f}s)")

                # Mix music with existing video audio (voiceover is already in the video)
                title_slug = story.get("title", "video")[:40].replace(" ", "_").replace("/", "_")
                final_path = os.path.join(output_dir, f"{title_slug}_FINAL.mp4")

                # Extract video's audio (voiceover), mix with music, re-merge
                vo_extract = os.path.join(vo_dir, "voiceover_extracted.mp3")
                subprocess.run([
                    "ffmpeg", "-y", "-i", video_path,
                    "-vn", "-c:a", "libmp3lame", "-q:a", "2", vo_extract,
                ], capture_output=True, text=True)

                if os.path.exists(vo_extract) and os.path.getsize(vo_extract) > 1000:
                    mixed_path = os.path.join(vo_dir, "mixed_audio.mp3")
                    mix_result = mix_audio_tracks(vo_extract, music_path, mixed_path)
                    if mix_result.get("success"):
                        merge_result = merge_video_audio(video_path, mixed_path, final_path)
                        if merge_result["success"]:
                            final_video_path = final_path
                            _log(f"  Final video with music: {final_path}")
                else:
                    _log(f"  No voiceover audio in video (voice=none mode)")
        except Exception as e:
            _log(f"  Music production error: {e}")

    # === Step 6: Generate Thumbnail ===
    thumbnail_path = ""
    try:
        _log("\n--- Step 6: Generating thumbnail ---")
        thumb_dir = os.path.join(output_dir, "thumbnail")
        title = story.get("title", "")
        thumb_result = generate_thumbnail_with_title(
            video_path, thumb_dir, title
        )
        if thumb_result.get("success"):
            thumbnail_path = thumb_result["path"]
            _log(f"  Thumbnail: {thumbnail_path}")
    except Exception as e:
        _log(f"  Thumbnail failed: {e}")

    _log(f"\n  Video ready: {final_video_path}")

    return {
        "success": True,
        "video_path": final_video_path,
        "story": story,
        "code": code,
        "evaluation": evaluation,
        "story_path": story_path,
        "code_path": code_path,
    }


def _render_with_fixes(
    code: str,
    output_dir: str,
    quality: str,
    max_attempts: int,
    _log,
) -> dict:
    """Render loop: try to render, auto-fix on failure."""
    # Validate syntax first
    syntax = validate_code(code)
    if not syntax["valid"]:
        _log(f"  Syntax error, fixing...")
        code = fix_manim_code(code, syntax["error"])

    attempt = 0
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        _log(f"  Render attempt {attempt}/{max_attempts}...")

        result = render_scene(code=code, output_dir=output_dir, quality=quality)

        if result["success"]:
            _log(f"  Rendered: {result['video_path']}")
            return {
                "success": True,
                "video_path": result["video_path"],
                "code": code,
                "attempts": attempt,
            }
        else:
            last_error = result["error"]
            error_lines = last_error.strip().split("\n")
            for line in error_lines[-5:]:
                _log(f"    {line}")

            if attempt < max_attempts:
                _log(f"  Auto-fixing...")
                code = fix_manim_code(code, last_error)
                code, _ = sanitize_code(code)  # Re-sanitize after fix

                code_path = os.path.join(output_dir, "scene.py")
                with open(code_path, "w") as f:
                    f.write(code)

    return {
        "success": False,
        "error": last_error,
        "code": code,
        "attempts": attempt,
    }


def _build_spatial_fix_prompt(issues: list[str], elements: dict) -> str:
    """Build a specific, actionable fix prompt from spatial analysis."""
    lines = ["SPATIAL LAYOUT PROBLEMS — fix ALL of these:\n"]

    # Group issues by type
    overlaps = [i for i in issues if "overlap" in i.lower()]
    offscreen = [i for i in issues if "off-screen" in i.lower()]
    accumulation = [i for i in issues if "never FadeOut" in i.lower()]

    if overlaps:
        lines.append("## TEXT OVERLAPS (elements on top of each other):")
        for o in overlaps[:5]:
            lines.append(f"  - {o}")
        lines.append("FIX: Move overlapping text elements further apart vertically.")
        lines.append("  Safe text positions: UP*3, UP*2, UP*0.5, DOWN*1, DOWN*2.5")
        lines.append("  Minimum gap between text: 1.0 Manim units\n")

    if offscreen:
        lines.append("## OFF-SCREEN ELEMENTS (outside visible frame):")
        for o in offscreen[:5]:
            lines.append(f"  - {o}")
        lines.append("FIX: Manim visible frame is x=[-7,7], y=[-4,4].")
        lines.append("  - Use smaller font_size (24-28) for long text")
        lines.append("  - Break long text into multiple lines")
        lines.append("  - Keep all .move_to() positions within y=[-3.5, 3.5]\n")

    if accumulation:
        lines.append("## TEXT ACCUMULATION (elements never removed):")
        for a in accumulation[:5]:
            lines.append(f"  - {a}")
        lines.append("FIX: Add FadeOut() for EVERY text element before the scene ends")
        lines.append("  or before new text is added to the same area.\n")

    lines.append("Return the complete fixed code.")
    return "\n".join(lines)
