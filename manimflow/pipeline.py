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
from .writers_room import run_writers_room, validate_story
from .design_system import generate_design_system, design_to_codegen_context, print_design_system
from .screenplay import write_screenplay, screenplay_to_codegen_prompt, print_screenplay
from .reviewers.design_reviewer import DesignReviewer
from .reviewers.base import print_review
from . import tracing


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
    """
    End-to-end: topic -> story -> code -> evaluate -> fix -> render -> video.

    The pipeline has two feedback loops:
    1. Render loop: fix code until it compiles/renders (max_fix_attempts)
    2. Quality loop: evaluate rendered output and improve (max_quality_loops)
    """
    os.makedirs(output_dir, exist_ok=True)
    _log = print if verbose else lambda *a, **k: None

    # Start Langfuse trace for the full pipeline run
    trace_ctx = tracing.trace(
        "generate_video",
        metadata={"topic": topic, "duration": duration, "quality": quality},
    )
    _trace = trace_ctx.__enter__()

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

    # === Step 1: Writers Room (explore angles → draft → director review → revise) ===
    _log("\n--- Step 1: Writers Room ---")

    with tracing.span("writers_room", metadata={"topic": topic}) as wr_span:
        approved = await run_writers_room(
            topic=topic,
            audience="general",
            duration=duration,
            max_revisions=2,
            verbose=verbose,
        )
        wr_span.update(output={
            "title": approved.title,
            "angle": approved.angle.title,
            "scenes": len(approved.scenes),
            "revisions": approved.revision_count,
            "director_score": approved.director_notes.score,
        })

    # Convert approved story to the format the rest of the pipeline expects
    story = {
        "title": approved.title,
        "duration_target": duration,
        "category": category or "formula",
        "hook_question": approved.angle.hook,
        "scenes": approved.scenes,
        "color_scheme": {},
        "math_components": {
            "key_insight": approved.angle.aha_moment,
        },
    }

    # Preserve color_assignments from the story draft if present
    # (the new writers room produces these)
    first_scene = approved.scenes[0] if approved.scenes else {}
    if isinstance(first_scene, dict):
        # Color assignments may be at story level
        pass
    # Check if the story draft had color_assignments
    for scene in approved.scenes:
        if isinstance(scene, dict) and scene.get("color_assignments"):
            story["color_assignments"] = scene["color_assignments"]
            break

    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, "w") as f:
        json.dump(story, f, indent=2)

    # Validate story completeness
    validation = validate_story(story)
    _log(f"\n  Approved story: \"{approved.title}\"")
    _log(f"  Angle: {approved.angle.title}")
    _log(f"  Director score: {approved.director_notes.score}/10")
    _log(f"  Scenes: {len(approved.scenes)}")
    _log(f"  Revisions: {approved.revision_count}")
    _log(f"  Elements: {validation.get('element_count', '?')}, Duration: ~{validation.get('total_duration', '?')}s")
    if validation.get("issues"):
        _log(f"  Story validation issues: {len(validation['issues'])}")
        for issue in validation["issues"][:3]:
            _log(f"    [!] {issue}")

    # === Step 1.5: Design System ===
    _log("\n--- Step 1.5: Generating design system ---")
    with tracing.span("design_system") as ds_span:
        design = await generate_design_system(
            story,
            angle_title=approved.angle.title,
            angle_mood=approved.angle.emotional_arc,
        )
    if verbose:
        print_design_system(design)

    # Save design system
    import json as _json
    design_path = os.path.join(output_dir, "design_system.json")
    with open(design_path, "w") as f:
        _json.dump(design.to_dict(), f, indent=2)

    # Review design — regenerate if below threshold
    design_reviewer = DesignReviewer()
    design_review = await design_reviewer.review(
        artifact=design.to_dict(),
        context={"topic": topic, "title": story.get("title", "")},
    )
    if verbose:
        print_review(design_review)

    if design_review.score < 5 and design_review.fixes:
        _log(f"  Design score {design_review.score}/10 — regenerating with feedback...")
        # Feed reviewer fixes back to design generator
        feedback = "\n".join(design_review.fixes[:5])
        story["_design_feedback"] = feedback
        design = await generate_design_system(
            story,
            angle_title=approved.angle.title,
            angle_mood=approved.angle.emotional_arc + f"\n\nFix these design issues:\n{feedback}",
        )
        if verbose:
            print_design_system(design)

    # Inject design context into story for code generation
    story["_design_context"] = design_to_codegen_context(design)

    # === Step 1.7: Screenplay (detailed shot-by-shot visual script) ===
    _log("\n--- Step 1.7: Writing screenplay ---")
    with tracing.span("screenplay") as sp_span:
        sp = await write_screenplay(story, topic)
        sp_span.update(output={"shots": len(sp.shots), "colors": len(sp.color_assignments)})
    if verbose:
        print_screenplay(sp)

    # The screenplay gives the code generator exact specifications
    story["_screenplay_context"] = screenplay_to_codegen_prompt(sp)

    # Save screenplay — FULL shot data, not just summary
    sp_path = os.path.join(output_dir, "screenplay.json")
    with open(sp_path, "w") as f:
        json.dump({
            "title": sp.title,
            "color_assignments": sp.color_assignments,
            "visual_metaphors": sp.visual_metaphors,
            "shots": [
                {
                    "id": shot.id,
                    "duration": shot.duration,
                    "narration": shot.narration,
                    "screen_elements": shot.screen_elements,
                    "animations": shot.animations,
                    "camera": shot.camera,
                    "teaching_point": shot.teaching_point,
                    "emotional_beat": shot.emotional_beat,
                    "transition_to_next": shot.transition_to_next,
                }
                for shot in sp.shots
            ],
        }, f, indent=2)

    _log(f"  Screenplay: {len(sp.shots)} shots, {len(sp.color_assignments)} colors")

    # === Step 2: Generate Manim Code ===
    _log("\n--- Step 2: Generating Manim code ---")

    with tracing.span("codegen") as cg_span:
        code = await generate_manim_code(story)
        cg_span.update(output={"lines": len(code.splitlines())})
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
        code = await fix_manim_code(code, f"Static analysis issues:\n{issues_text}")
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
        code = await fix_manim_code(code, fix_prompt)
        with open(code_path, "w") as f:
            f.write(code)

    # === Step 3: Render with Auto-Fix Loop ===
    _log("\n--- Step 3/4: Rendering video ---")

    with tracing.span("render") as render_span:
        render_result = await _render_with_fixes(code, output_dir, quality, max_fix_attempts, _log)
        render_span.update(output={
            "success": render_result["success"],
            "attempts": render_result.get("attempts", 0),
        })

    if not render_result["success"]:
        result = {
            "success": False,
            "error": render_result["error"],
            "story": story,
            "code": render_result["code"],
            "attempts": render_result["attempts"],
            "story_path": story_path,
            "code_path": code_path,
        }
        _trace.update(output={"success": False, "error": render_result["error"][:200]})
        trace_ctx.__exit__(None, None, None)
        tracing.flush()
        return result

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
            frame_eval = await evaluate_video_frames(video_path, story, output_dir)
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
        evaluation = await evaluate_frames_with_code(code, story)

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
            new_code = await surgical_fix(code, feedback)
            if new_code != code:
                code = new_code
            else:
                # Surgical fix didn't change anything — fall back to full rewrite
                _log("  Surgical fix had no effect, trying full rewrite...")
                code = await fix_manim_code(code, feedback)
            code, _ = sanitize_code(code)
            with open(code_path, "w") as f:
                f.write(code)

            # Re-render with improved code
            render_result = await _render_with_fixes(code, output_dir, quality, max_fix_attempts, _log)
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

    result = {
        "success": True,
        "video_path": final_video_path,
        "story": story,
        "code": code,
        "evaluation": evaluation,
        "story_path": story_path,
        "code_path": code_path,
    }

    # Close Langfuse trace
    overall_score = evaluation.get("overall_score", 0)
    _trace.update(output={
        "success": True,
        "quality_score": overall_score,
        "video_path": final_video_path,
    })
    # Score the trace for Langfuse dashboards
    if tracing.is_enabled() and isinstance(overall_score, (int, float)) and overall_score > 0:
        _trace.score(name="quality", value=overall_score / 10.0)
    trace_ctx.__exit__(None, None, None)
    tracing.flush()

    return result


async def _render_with_fixes(
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
            error_lines = last_error.strip().split("\n")
            for line in error_lines[-5:]:
                _log(f"    {line}")

            if attempt < max_attempts:
                _log(f"  Auto-fixing...")
                code = await fix_manim_code(code, last_error)
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

    # Screen usage issues
    underutilized = [i for i in issues if "underutil" in i.lower()]
    oversized = [i for i in issues if "too large" in i.lower() or "covers" in i.lower()]

    if underutilized:
        lines.append("## SCREEN UNDERUTILIZED (too much empty space):")
        lines.append("FIX: Elements are too small. Increase sizes:")
        lines.append("  - RoundedRectangle: width=3.5-4.5, height=1.5-2.0")
        lines.append("  - Circle: radius=1.5-2.0")
        lines.append("  - Text: font_size=28-36 (not 20-24)")
        lines.append("  - Use VGroup().arrange() to spread elements across the screen")
        lines.append("  - Elements should cover at least 30% of the visible area\n")

    if oversized:
        lines.append("## OVERSIZED SHAPES (taking up too much screen):")
        for o in oversized[:3]:
            lines.append(f"  - {o}")
        lines.append("FIX: Maximum shape dimensions: width=5, height=3.")
        lines.append("  Never fill the entire screen with one shape.\n")

    if accumulation:
        lines.append("## TEXT ACCUMULATION (elements never removed):")
        for a in accumulation[:5]:
            lines.append(f"  - {a}")
        lines.append("FIX: Add FadeOut() for EVERY text element before the scene ends")
        lines.append("  or before new text is added to the same area.\n")

    lines.append("Return the complete fixed code.")
    return "\n".join(lines)
