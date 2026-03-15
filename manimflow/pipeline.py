"""Main pipeline — orchestrates preproduction → production → postproduction.

Preproduction: story → design → screenplay (with validation)
Production:    codegen → sanitize → inspect → layout check → render
Postproduction: quality eval → audio → thumbnail
"""

import json
import os
import subprocess

from .preproduction.writers_room import run_writers_room
from .preproduction.design_system import design_story, print_designed_story
from .preproduction.screenplay import (
    write_screenplay,
    screenplay_to_codegen_context,
    print_screenplay,
)
from .preproduction.screenplay_validator import validate_screenplay
from .production.codegen import generate_manim_code, fix_manim_code
from .production.code_sanitizer import sanitize_code
from .production.renderer import render_scene, validate_code
from .production.scene_inspector import inspect_scene
from .production.layout_checker import (
    check_layout,
    format_issues_for_codegen,
    print_layout_check,
)
from .production.code_editor import surgical_fix
from .postproduction.evaluator import (
    static_code_checks,
    evaluate_frames_with_code,
    evaluate_video_frames,
    print_evaluation,
)
from .postproduction.voiceover import merge_video_audio
from .postproduction.music import select_mood, generate_ambient_track, mix_audio_tracks
from .postproduction.thumbnail import generate_thumbnail_with_title
from .postproduction.timing import get_video_duration
from .reference.platform import PlatformConfig, get_platform_config
from .core import tracing


@tracing.observe()
async def generate_video(
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
    """End-to-end: topic → story → design → screenplay → code → render → video."""
    os.makedirs(output_dir, exist_ok=True)
    _log = print if verbose else lambda *a, **k: None

    _log("\n======================================")
    _log("  ManimFlow Video Generation Pipeline")
    _log("======================================")
    _log(f"\nTopic: {topic}")

    # Platform config
    platform_config = (
        get_platform_config(platform)
        if platform
        else PlatformConfig(duration_seconds=duration)
    )
    if platform:
        duration = platform_config.duration_seconds
        if not voice and platform_config.voice:
            voice = platform_config.voice

    # ═══════════════════════════════════════
    #  PREPRODUCTION
    # ═══════════════════════════════════════

    # === Step 1: Writers Room (parallel writers → review → revise) ===
    _log("\n--- Step 1: Writers Room ---")
    approved = await run_writers_room(
        topic=topic,
        audience="general",
        n=3,
        t=1,
        verbose=verbose,
    )
    _log(f'\n  Story: "{approved.title}" ({len(approved.story_text)} chars)')

    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, "w") as f:
        json.dump({"title": approved.title, "story": approved.story_text}, f, indent=2)

    # === Step 2: Design System (visual specs in prose) ===
    _log("\n--- Step 2: Design System ---")
    designed = await design_story(approved.title, approved.story_text)
    if verbose:
        print_designed_story(designed)

    visual_story_path = os.path.join(output_dir, "visual_story.json")
    with open(visual_story_path, "w") as f:
        json.dump(
            {
                "title": designed.title,
                "design_rules": designed.design_rules,
                "visual_story": designed.visual_story,
            },
            f,
            indent=2,
        )

    # === Step 3: Screenplay (structured shots + validation loop) ===
    _log("\n--- Step 3: Screenplay ---")
    sp = await write_screenplay(
        title=designed.title,
        visual_story=designed.visual_story,
        design_rules=designed.design_rules,
        max_fix_rounds=3,
        verbose=verbose,
    )
    if verbose:
        print_screenplay(sp)

    # Save full screenplay
    sp_data = {
        "design_rules": sp.design_rules,
        "shots": [
            {
                "id": s.id,
                "narration": s.narration,
                "elements": s.elements,
                "animation_sequence": s.animation_sequence,
                "cleanup": s.cleanup,
                "persists": s.persists,
            }
            for s in sp.shots
        ],
    }
    sp_path = os.path.join(output_dir, "screenplay.json")
    with open(sp_path, "w") as f:
        json.dump(sp_data, f, indent=2)

    # Final screenplay validation
    validation = validate_screenplay(sp_data)
    _log(
        f"  Screenplay: {len(sp.shots)} shots, {validation['errors']} errors, {validation['warnings']} warnings"
    )

    # Build context for codegen
    codegen_context = screenplay_to_codegen_context(sp)

    # Build the story dict that codegen expects
    story = {
        "title": designed.title,
        "duration_target": duration,
        "category": category or "formula",
        "story_text": approved.story_text,
        "_visual_story": designed.visual_story,
        "_screenplay_context": codegen_context,
    }

    # ═══════════════════════════════════════
    #  PRODUCTION
    # ═══════════════════════════════════════

    # === Step 4: Generate Manim Code ===
    _log("\n--- Step 4: Generating Manim code ---")
    code = await generate_manim_code(story)
    code_path = os.path.join(output_dir, "scene.py")
    with open(code_path, "w") as f:
        f.write(code)
    _log(f"  Generated {len(code.splitlines())} lines")

    # Sanitize: fix common LLM mistakes
    code, sanitize_fixes = sanitize_code(code)
    if sanitize_fixes:
        _log(f"  Sanitized {len(sanitize_fixes)} issues")
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 4.5: Static checks ===
    _log("\n--- Step 4.5: Static code checks ---")
    static = static_code_checks(code)
    _log(f"  Estimated duration: ~{static['estimated_duration']:.0f}s")

    if not static["pass"]:
        _log("  Static checks found issues, fixing...")
        issues_text = "\n".join(static["issues"] + static["warnings"])
        code = await fix_manim_code(code, f"Static analysis issues:\n{issues_text}")
        code, _ = sanitize_code(code)
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 4.7: Scene inspection + layout check ===
    _log("\n--- Step 4.7: Layout inspection ---")
    snapshots = inspect_scene(code)
    if snapshots:
        layout_issues = check_layout(sp_data, snapshots)
        layout_errors = [i for i in layout_issues if i.severity == "error"]
        layout_warnings = [i for i in layout_issues if i.severity == "warning"]
        _log(
            f"  Inspected {len(snapshots)} steps: {len(layout_errors)} errors, {len(layout_warnings)} warnings"
        )

        if layout_errors:
            if verbose:
                print_layout_check(layout_issues)
            _log("  Fixing layout issues...")
            fix_prompt = format_issues_for_codegen(layout_issues)
            code = await fix_manim_code(code, fix_prompt)
            code, _ = sanitize_code(code)
            with open(code_path, "w") as f:
                f.write(code)
    else:
        _log("  Scene inspection failed (code may have errors)")

    # === Step 5: Render with Auto-Fix Loop ===
    _log("\n--- Step 5: Rendering video ---")
    render_result = await _render_with_fixes(
        code, output_dir, quality, max_fix_attempts, _log
    )

    if not render_result["success"]:
        tracing.flush()
        return {
            "success": False,
            "error": render_result["error"],
            "story_path": story_path,
            "code_path": code_path,
            "attempts": render_result["attempts"],
        }

    code = render_result["code"]
    video_path = render_result["video_path"]
    with open(code_path, "w") as f:
        f.write(code)

    # ═══════════════════════════════════════
    #  POSTPRODUCTION
    # ═══════════════════════════════════════

    # === Step 6: Quality Evaluation Loop ===
    _log("\n--- Step 6: Quality evaluation ---")
    evaluation = {}

    for quality_round in range(max_quality_loops):
        _log(f"\n  Quality round {quality_round + 1}/{max_quality_loops}...")

        # Vision-based evaluation
        vision_feedback = []
        visual_score = None
        if video_path:
            try:
                frame_eval = await evaluate_video_frames(video_path, story, output_dir)
                visual_score = frame_eval.get("overall_visual_score")
                visual_issues = frame_eval.get("visual_issues", [])
                semantic_issues = frame_eval.get("semantic_issues", [])
                if visual_score:
                    _log(f"  Vision score: {visual_score}/10")
                if visual_issues:
                    vision_feedback = visual_issues + [
                        f"SEMANTIC: {s}" for s in semantic_issues
                    ]
            except Exception as e:
                _log(f"  Vision eval failed: {e}")

        # Code-based evaluation
        evaluation = await evaluate_frames_with_code(code, story)
        if verbose:
            print_evaluation(evaluation)

        verdict = evaluation.get("verdict", "FAIL")
        overall = evaluation.get("overall_score", 0)

        if not isinstance(overall, (int, float)) or overall == 0:
            scores = evaluation.get("scores", {})
            score_vals = [
                s.get("score", 5)
                for s in scores.values()
                if isinstance(s, dict) and isinstance(s.get("score"), (int, float))
            ]
            if score_vals:
                overall = sum(score_vals) / len(score_vals)
                evaluation["overall_score"] = overall

        combined_score = overall
        if visual_score and isinstance(visual_score, (int, float)):
            combined_score = 0.4 * visual_score + 0.6 * overall
            if visual_score < 5:
                combined_score = min(combined_score, 6.0)

        if verdict == "PASS" and combined_score >= 7:
            _log(f"  Quality PASSED ({combined_score:.1f}/10)")
            break

        if quality_round < max_quality_loops - 1:
            _log(f"  Quality needs improvement ({combined_score:.1f}/10), fixing...")

            critical = evaluation.get("critical_issues", [])
            suggestions = evaluation.get("suggestions", [])
            all_feedback = critical[:5] + suggestions[:3]
            if vision_feedback:
                all_feedback = [
                    f"[VISION] {v}" for v in vision_feedback[:5]
                ] + all_feedback[:3]

            feedback = "Fix these issues:\n" + "\n".join(all_feedback)

            new_code = await surgical_fix(code, feedback)
            if new_code != code:
                code = new_code
            else:
                code = await fix_manim_code(code, feedback)
            code, _ = sanitize_code(code)
            with open(code_path, "w") as f:
                f.write(code)

            render_result = await _render_with_fixes(
                code, output_dir, quality, max_fix_attempts, _log
            )
            if render_result["success"]:
                code = render_result["code"]
                video_path = render_result["video_path"]
                with open(code_path, "w") as f:
                    f.write(code)
            else:
                _log("  Re-render failed, keeping previous version")
                break
        else:
            _log(f"  Accepting quality ({overall}/10)")

    # === Step 7: Background Music ===
    final_video_path = video_path

    if voice:
        _log("\n--- Step 7: Background music ---")
        try:
            video_dur = get_video_duration(video_path)
            mood = select_mood(category or "formula")
            vo_dir = os.path.join(output_dir, "audio")
            os.makedirs(vo_dir, exist_ok=True)

            music_path = os.path.join(vo_dir, "background_music.mp3")
            music_result = generate_ambient_track(music_path, video_dur + 5, mood=mood)

            if music_result.get("success"):
                title_slug = designed.title[:40].replace(" ", "_").replace("/", "_")
                final_path = os.path.join(output_dir, f"{title_slug}_FINAL.mp4")

                vo_extract = os.path.join(vo_dir, "voiceover_extracted.mp3")
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        video_path,
                        "-vn",
                        "-c:a",
                        "libmp3lame",
                        "-q:a",
                        "2",
                        vo_extract,
                    ],
                    capture_output=True,
                    text=True,
                )

                if os.path.exists(vo_extract) and os.path.getsize(vo_extract) > 1000:
                    mixed_path = os.path.join(vo_dir, "mixed_audio.mp3")
                    mix_result = mix_audio_tracks(vo_extract, music_path, mixed_path)
                    if mix_result.get("success"):
                        merge_result = merge_video_audio(
                            video_path, mixed_path, final_path
                        )
                        if merge_result["success"]:
                            final_video_path = final_path
                            _log(f"  Final video: {final_path}")
        except Exception as e:
            _log(f"  Music error: {e}")

    # === Step 8: Thumbnail ===
    thumbnail_path = ""
    try:
        _log("\n--- Step 8: Thumbnail ---")
        thumb_dir = os.path.join(output_dir, "thumbnail")
        thumb_result = generate_thumbnail_with_title(
            video_path, thumb_dir, designed.title
        )
        if thumb_result.get("success"):
            thumbnail_path = thumb_result["path"]
            _log(f"  Thumbnail: {thumbnail_path}")
    except Exception as e:
        _log(f"  Thumbnail failed: {e}")

    _log(f"\n  Video ready: {final_video_path}")

    # Score in Langfuse
    overall_score = evaluation.get("overall_score", 0)
    if (
        tracing.is_enabled()
        and isinstance(overall_score, (int, float))
        and overall_score > 0
    ):
        tracing.score_trace("quality", overall_score / 10.0)
    tracing.flush()

    return {
        "success": True,
        "video_path": final_video_path,
        "story_path": story_path,
        "code_path": code_path,
        "evaluation": evaluation,
    }


async def _render_with_fixes(
    code: str,
    output_dir: str,
    quality: str,
    max_attempts: int,
    _log,
) -> dict:
    """Render loop: try to render, auto-fix on failure."""
    syntax = validate_code(code)
    if not syntax["valid"]:
        _log("  Syntax error, fixing...")
        code = await fix_manim_code(code, syntax["error"])

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
            for line in last_error.strip().split("\n")[-5:]:
                _log(f"    {line}")

            if attempt < max_attempts:
                _log("  Auto-fixing...")
                code = await fix_manim_code(code, last_error)
                code, _ = sanitize_code(code)
                with open(os.path.join(output_dir, "scene.py"), "w") as f:
                    f.write(code)

    return {
        "success": False,
        "error": last_error,
        "code": code,
        "attempts": attempt,
    }
