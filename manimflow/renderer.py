"""Renderer - compiles Manim code to video."""

import subprocess
import tempfile
import os
import shutil
from pathlib import Path


def render_scene(
    code: str,
    output_dir: str = "output",
    quality: str = "h",  # l=low, m=medium, h=high, k=4k
    scene_name: str = "GeneratedScene",
    preview: bool = False,
) -> dict:
    """
    Render Manim code to video.

    Returns dict with:
        success: bool
        video_path: str (if successful)
        error: str (if failed)
        stderr: str (full stderr output)
    """
    os.makedirs(output_dir, exist_ok=True)

    # Write code to temp file
    temp_file = os.path.join(output_dir, "scene.py")
    with open(temp_file, "w") as f:
        f.write(code)

    # Build manim command
    cmd = [
        "uv", "run", "python", "-m", "manim",
        f"-q{quality}",
        "--media_dir", output_dir,
    ]

    if preview:
        cmd.append("-p")

    cmd.extend([temp_file, scene_name])

    print(f"  Rendering: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 min timeout
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr,
            "stderr": result.stderr,
            "stdout": result.stdout,
        }

    # Find the output video
    video_path = _find_video(output_dir, quality)

    return {
        "success": True,
        "video_path": video_path,
        "stderr": result.stderr,
        "stdout": result.stdout,
    }


def _find_video(output_dir: str, quality: str) -> str:
    """Find the rendered video file."""
    quality_map = {
        "l": "480p15",
        "m": "720p30",
        "h": "1080p60",
        "k": "2160p60",
    }
    quality_dir = quality_map.get(quality, "1080p60")

    # Search for mp4 files in the media directory
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            if f.endswith(".mp4"):
                return os.path.join(root, f)

    return ""


def validate_code(code: str) -> dict:
    """Quick syntax check without rendering."""
    try:
        compile(code, "<generated>", "exec")
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}
