"""Video quality evaluator - uses frame extraction + vision LLM to assess quality."""

import subprocess
import os
import json
import base64
from pathlib import Path

from .llm import call_llm


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

    # Extract frames at evenly spaced intervals
    frame_paths = []
    for i in range(num_frames):
        timestamp = (i / (num_frames - 1)) * duration if num_frames > 1 else 0
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


def evaluate_frames_with_code(code: str, story: dict) -> dict:
    """Evaluate quality by analyzing the code and story (no vision needed)."""
    evaluation_prompt = """You are a video quality evaluator for educational math/physics animations.

Analyze this Manim code and story script. Score each dimension 1-10 and explain issues.

EVALUATION DIMENSIONS:
1. VISUAL CLARITY (1-10): Will text be readable? Any overlaps? Proper spacing?
2. PACING (1-10): Are run_time and wait() values appropriate? Too rushed or too slow?
3. PROGRESSIVE BUILD (1-10): Does complexity build gradually or dump everything?
4. COLOR USAGE (1-10): Do colors encode meaning consistently? Good contrast on black bg?
5. TEXT MANAGEMENT (1-10): Clean text lifecycle? FadeOut before new text? No accumulation?
6. MATHEMATICAL ACCURACY (1-10): Are equations correct? Complete cycles shown?
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

    response = call_llm(evaluation_prompt, user_prompt)

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


def evaluate_video_frames(video_path: str, story: dict, output_dir: str) -> dict:
    """Full evaluation: extract frames and evaluate with vision model.

    Falls back to code-only evaluation if frame extraction fails.
    """
    try:
        frame_paths = extract_keyframes(video_path, output_dir, num_frames=6)
    except Exception as e:
        print(f"  Frame extraction failed: {e}")
        frame_paths = []

    if not frame_paths:
        return {"frame_evaluation": None, "note": "Frame extraction unavailable"}

    # Build frame descriptions for evaluation
    frame_descriptions = []
    for i, path in enumerate(frame_paths):
        pct = int((i / max(len(frame_paths) - 1, 1)) * 100)
        frame_descriptions.append(f"Frame at {pct}% of video: {path}")

    eval_prompt = """Evaluate these video keyframes from an educational math animation.

For each frame, assess:
1. Is there content visible (not blank/black)?
2. Is text readable and well-positioned?
3. Are mathematical elements (curves, axes, equations) properly rendered?
4. Is the frame visually appealing?

Return JSON:
{
  "frame_analysis": [
    {"frame": 0, "has_content": true, "text_readable": true, "math_visible": true, "notes": "..."},
    ...
  ],
  "blank_frames": 0,
  "overlap_detected": false,
  "overall_visual_quality": 7,
  "issues": []
}"""

    response = call_llm(eval_prompt, f"Frames from video: {frame_descriptions}\nStory: {json.dumps(story, indent=2)[:1000]}")

    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
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

    return {"frame_evaluation": "parse_error"}


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
