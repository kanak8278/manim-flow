"""Thumbnail generation — extract the most visually striking frame.

Research showed thumbnails drive 14% CTR vs 4-5% average.
Strategy: extract multiple candidate frames, pick the one with most visual content.
"""

import subprocess
import os


def generate_thumbnail(
    video_path: str, output_dir: str, num_candidates: int = 10
) -> dict:
    """Extract the best frame from a video as a thumbnail.

    Strategy:
    1. Extract N evenly-spaced frames (skipping first/last 10%)
    2. Pick the frame with the largest file size (= most visual content)
    3. Save as high-quality PNG

    Returns dict with path and metadata.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Get video duration
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"success": False, "error": "ffprobe failed"}

    duration = float(result.stdout.strip())

    # Skip first/last 10% (often blank or fade)
    start = duration * 0.1
    end = duration * 0.9
    span = end - start

    # Extract candidate frames
    candidates = []
    for i in range(num_candidates):
        timestamp = start + (i / max(num_candidates - 1, 1)) * span
        frame_path = os.path.join(output_dir, f"thumb_candidate_{i:02d}.png")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(timestamp),
                "-i",
                video_path,
                "-vframes",
                "1",
                "-q:v",
                "1",  # Highest quality
                frame_path,
            ],
            capture_output=True,
            text=True,
        )

        if os.path.exists(frame_path):
            size = os.path.getsize(frame_path)
            candidates.append(
                {
                    "path": frame_path,
                    "timestamp": timestamp,
                    "size": size,
                }
            )

    if not candidates:
        return {"success": False, "error": "No frames extracted"}

    # Pick the frame with most visual content (largest file = most detail)
    best = max(candidates, key=lambda c: c["size"])

    # Copy best to final thumbnail path
    thumbnail_path = os.path.join(output_dir, "thumbnail.png")
    subprocess.run(["cp", best["path"], thumbnail_path])

    # Clean up candidates
    for c in candidates:
        if c["path"] != thumbnail_path and os.path.exists(c["path"]):
            os.remove(c["path"])

    return {
        "success": True,
        "path": thumbnail_path,
        "timestamp": best["timestamp"],
        "size": best["size"],
    }


def generate_thumbnail_with_title(video_path: str, output_dir: str, title: str) -> dict:
    """Generate thumbnail with title text overlay.

    Uses ffmpeg to add bold text to the best frame.
    """
    # First get the base thumbnail
    result = generate_thumbnail(video_path, output_dir)
    if not result.get("success"):
        return result

    base_path = result["path"]
    final_path = os.path.join(output_dir, "thumbnail_titled.png")

    # Overlay title text using ffmpeg
    # Clean title for ffmpeg (escape special chars)
    safe_title = title.replace("'", "").replace(":", "").replace("\\", "")
    if len(safe_title) > 40:
        # Split into two lines
        mid = len(safe_title) // 2
        space_idx = safe_title.rfind(" ", 0, mid + 10)
        if space_idx > 0:
            safe_title = safe_title[:space_idx] + "\n" + safe_title[space_idx + 1 :]

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        base_path,
        "-vf",
        (
            f"drawtext=text='{safe_title}':"
            f"fontsize=48:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-text_h-40:"
            f"font=Arial"
        ),
        "-q:v",
        "1",
        final_path,
    ]

    sub_result = subprocess.run(cmd, capture_output=True, text=True)

    if sub_result.returncode != 0:
        # Fall back to untitled thumbnail
        return result

    return {
        "success": True,
        "path": final_path,
        "base_path": base_path,
        "title": title,
    }
