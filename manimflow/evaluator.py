"""Video quality evaluator - uses frame extraction + vision LLM to assess quality."""

import subprocess
import os
import json
import base64
from pathlib import Path

from .agent import call_llm


def extract_keyframes(video_path: str, output_dir: str, num_frames: int = 8) -> list[str]:
    """Extract evenly-spaced keyframes from video using ffmpeg."""
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Get video duration
    duration_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    duration = float(result.stdout.strip())

    # Extract frames at evenly spaced intervals, skipping first 0.5s (always black in Manim)
    frame_paths = []
    start_offset = min(0.5, duration * 0.05)
    effective_duration = duration - start_offset
    for i in range(num_frames):
        timestamp = start_offset + (i / max(num_frames - 1, 1)) * effective_duration
        frame_path = os.path.join(frames_dir, f"frame_{i:03d}.png")

        cmd = [
            "ffmpeg", "-y", "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            frame_path,
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        if os.path.exists(frame_path):
            frame_paths.append(frame_path)

    return frame_paths


async def evaluate_frames_with_code(code: str, story: dict) -> dict:
    """Evaluate quality by analyzing the code and story (no vision needed)."""
    evaluation_prompt = """You are a video quality evaluator for educational math/physics animations.

Analyze this Manim code and story script. Score each dimension 1-10 and explain issues.

EVALUATION DIMENSIONS:
1. VISUAL CLARITY (1-10): Will text be readable? Any overlaps? Proper spacing?
2. PACING (1-10): Are run_time and wait() values appropriate? Too rushed or too slow?
3. PROGRESSIVE BUILD (1-10): Does complexity build gradually or dump everything?
4. COLOR USAGE (1-10): Do colors encode meaning consistently? Good contrast on black bg?
5. TEXT MANAGEMENT (1-10): Clean text lifecycle? FadeOut before new text? No accumulation?
6. MATHEMATICAL & VISUAL ACCURACY (1-10): Are equations correct? Do visualizations
   accurately represent the data? If code shows fill_opacity=0.5 for "50.7%", that's wrong.
   If a pie chart angle doesn't match the percentage, that's wrong.
7. ENGAGEMENT (1-10): Hook quality? "Aha" moment? Narrative arc?
8. ANIMATION VARIETY (1-10): Mix of Create, Transform, FadeIn? Not repetitive?

Return JSON:
{
  "scores": {
    "visual_clarity": {"score": 7, "issues": ["text at UP*3.5 might be off-screen"]},
    "pacing": {"score": 8, "issues": []},
    "progressive_build": {"score": 6, "issues": ["jumps from eq to curve too fast"]},
    "color_usage": {"score": 9, "issues": []},
    "text_management": {"score": 5, "issues": ["scene 3 doesn't FadeOut title"]},
    "math_accuracy": {"score": 8, "issues": []},
    "engagement": {"score": 7, "issues": ["hook is weak"]},
    "animation_variety": {"score": 6, "issues": ["only uses Write and FadeOut"]}
  },
  "overall_score": 7.0,
  "critical_issues": ["list of must-fix problems"],
  "suggestions": ["list of improvement ideas"],
  "verdict": "PASS|NEEDS_FIXES|FAIL"
}

A score below 6 in any dimension = NEEDS_FIXES. Below 4 in any = FAIL."""

    user_prompt = f"""Evaluate this educational animation:

STORY SCRIPT:
{json.dumps(story, indent=2)}

MANIM CODE:
```python
{code}
```

Return ONLY valid JSON evaluation."""

    response = await call_llm(evaluation_prompt, user_prompt)

    # Extract JSON from response
    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            block = response.split("```")[1].split("```")[0]
            if block.strip().startswith("{"):
                response = block

        start = response.find("{")
        depth = 0
        for i in range(start, len(response)):
            if response[i] == "{":
                depth += 1
            elif response[i] == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(response[start:i+1])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "scores": {},
        "overall_score": 0,
        "critical_issues": ["Failed to parse evaluation"],
        "suggestions": [],
        "verdict": "FAIL",
    }


async def evaluate_video_frames(video_path: str, story: dict, output_dir: str) -> dict:
    """Extract frames from rendered video and evaluate with Claude Vision.

    This is Approach 2: actually LOOK at the video to catch visual issues
    that code analysis can't detect (rendering glitches, color clashing,
    font issues, actual overlap appearance, composition quality).
    """
    try:
        frame_paths = extract_keyframes(video_path, output_dir, num_frames=6)
    except Exception as e:
        print(f"  Frame extraction failed: {e}")
        return {"frame_evaluation": None, "note": f"Frame extraction failed: {e}"}

    if not frame_paths:
        return {"frame_evaluation": None, "note": "No frames extracted"}

    print(f"  Extracted {len(frame_paths)} keyframes for vision analysis")

    # Build frame labels for context
    frame_labels = []
    for i, path in enumerate(frame_paths):
        pct = int((i / max(len(frame_paths) - 1, 1)) * 100)
        frame_labels.append(f"Frame {i+1} (at {pct}% of video)")

    # Build scene descriptions so vision can check semantic correctness
    scene_descriptions = []
    for scene in story.get("scenes", []):
        scene_descriptions.append(
            f"Scene '{scene.get('name', '?')}': {scene.get('visual_description', '')[:100]}"
        )

    eval_system = """You are a STRICT video quality evaluator for educational math/physics animations.
You look at actual rendered frames and evaluate BOTH visual quality AND correctness.
You must catch issues like: wrong chart proportions, misaligned fills, misleading visuals."""

    eval_prompt = f"""These are {len(frame_paths)} keyframes from an educational animation.
Video title: {story.get('title', 'Unknown')}
Frame timestamps: {', '.join(frame_labels)}

EXPECTED CONTENT (what the story intends to show):
{chr(10).join(scene_descriptions)}

For EACH frame, evaluate:

A. VISUAL QUALITY:
1. Is there content (not just black)?
2. Is text overlapping other text?
3. Is text readable (size, contrast, not cut off)?
4. Is the composition clean?

B. SEMANTIC CORRECTNESS (CRITICAL — most evaluators miss this):
5. Do charts/graphs/visualizations accurately represent the data shown?
   - Is a "50%" fill actually showing 50%? Or is it misaligned?
   - Does a number line have correct spacing?
   - Are proportions in diagrams correct?
6. Does the visual match what the text/labels say?
   - If text says "increases exponentially" does the curve look exponential?
   - If it says "50.7%" is the visual approximately 50.7%, not 50%?
7. Are mathematical shapes rendered correctly?
   - Circles should be round, not oval
   - Lines that should be straight ARE straight
   - Fills/shading should align with boundaries

C. RENDERING ISSUES (check carefully):
8. Are there GREY BOXES or GREY SQUARES anywhere? These are font rendering failures.
   Small grey rectangles near text = non-ASCII characters the font can't render.
   This is a CRITICAL BUG — score should be 3/10 or lower if present.
9. Are there stray characters, random letters, or truncated text?
10. Are there any visual elements that look broken or glitched?

D. PRODUCTION QUALITY:
11. Does this look professional or amateurish?
12. Would you be embarrassed to post this on YouTube?

Return JSON:
{{
  "frame_analysis": [
    {{"frame": 1, "has_content": true, "overlap_detected": false, "text_readable": true,
      "cutoff": false, "semantic_correct": true, "composition": "good|fair|poor",
      "notes": "description of what you see and any correctness issues"}}
  ],
  "blank_frame_count": 0,
  "overlap_detected_in_any": false,
  "cutoff_detected_in_any": false,
  "semantic_issues": ["list of correctness problems — charts wrong, proportions off, etc"],
  "overall_visual_score": 7,
  "visual_issues": ["list of visual quality issues"],
  "visual_strengths": ["list of things that look good"]
}}"""

    try:
        response = await call_llm(eval_system, eval_prompt, images=frame_paths)
        return _parse_json_response(response)
    except Exception as e:
        print(f"  Vision evaluation failed: {e}")
        return {"frame_evaluation": None, "note": f"Vision eval failed: {e}"}


def _parse_json_response(response: str) -> dict:
    """Parse JSON from LLM response."""
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0]
    elif "```" in response:
        block = response.split("```")[1].split("```")[0]
        if block.strip().startswith("{"):
            response = block

    start = response.find("{")
    if start == -1:
        return {"parse_error": True}

    depth = 0
    for i in range(start, len(response)):
        if response[i] == "{":
            depth += 1
        elif response[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(response[start:i+1])
                except json.JSONDecodeError:
                    return {"parse_error": True}

    return {"parse_error": True}


def static_code_checks(code: str) -> dict:
    """Fast, deterministic code quality checks (no LLM needed)."""
    issues = []
    warnings = []
    lines = code.split("\n")

    # Check 1: Has required structure
    if "class GeneratedScene" not in code:
        issues.append("Missing class GeneratedScene")
    if "def construct" not in code:
        issues.append("Missing construct method")
    if "from manim import" not in code:
        issues.append("Missing manim import")

    # Check 2: Background color
    if "background_color" not in code:
        warnings.append("No background color set (will default to black)")

    # Check 3: Invalid color names
    invalid_colors = ["CYAN", "LIME", "CORAL", "INDIGO", "VIOLET"]
    for color in invalid_colors:
        # Check for bare color name (not in string/hex)
        for i, line in enumerate(lines):
            # Skip comments and strings
            stripped = line.split("#")[0]
            if f"={color}" in stripped or f"= {color}" in stripped or f"({color}" in stripped or f", {color}" in stripped:
                issues.append(f"Line {i+1}: Invalid color '{color}' - use hex or standard color")

    # Check 4: Text accumulation (heuristic)
    write_count = code.count("Write(")
    fadeout_count = code.count("FadeOut(")
    if write_count > fadeout_count + 3:
        warnings.append(f"Possible text accumulation: {write_count} Write() vs {fadeout_count} FadeOut()")

    # Check 5: Timing analysis
    total_time = 0
    for line in lines:
        if "run_time=" in line:
            try:
                rt = float(line.split("run_time=")[1].split(",")[0].split(")")[0])
                total_time += rt
            except ValueError:
                pass
        if "self.wait(" in line:
            try:
                wt = float(line.split("self.wait(")[1].split(")")[0].split(",")[0])
                total_time += wt
            except ValueError:
                pass

    if total_time < 30:
        warnings.append(f"Video might be too short: ~{total_time:.0f}s estimated")
    elif total_time > 150:
        warnings.append(f"Video might be too long: ~{total_time:.0f}s estimated (target: 90s)")

    # Check 6: Empty screen detection (heuristic)
    consecutive_fadeouts = 0
    for line in lines:
        if "FadeOut" in line:
            consecutive_fadeouts += 1
        elif any(anim in line for anim in ["Write(", "Create(", "FadeIn(", "self.add("]):
            consecutive_fadeouts = 0
        if consecutive_fadeouts >= 3:
            warnings.append("Possible empty screen: multiple consecutive FadeOut without new content")
            consecutive_fadeouts = 0

    return {
        "issues": issues,
        "warnings": warnings,
        "estimated_duration": total_time,
        "pass": len(issues) == 0,
    }


def print_evaluation(eval_result: dict):
    """Pretty-print evaluation results."""
    print("\n--- Evaluation Results ---")

    scores = eval_result.get("scores", {})
    if scores:
        for dim, data in scores.items():
            score = data.get("score", "?")
            marker = "PASS" if score >= 6 else "WARN" if score >= 4 else "FAIL"
            print(f"  [{marker}] {dim}: {score}/10")
            for issue in data.get("issues", []):
                print(f"        - {issue}")

    overall = eval_result.get("overall_score", "?")
    verdict = eval_result.get("verdict", "?")
    print(f"\n  Overall: {overall}/10 - {verdict}")

    critical = eval_result.get("critical_issues", [])
    if critical:
        print(f"\n  Critical Issues:")
        for issue in critical:
            print(f"    ! {issue}")

    suggestions = eval_result.get("suggestions", [])
    if suggestions:
        print(f"\n  Suggestions:")
        for s in suggestions[:5]:
            print(f"    > {s}")
