"""CLI interface for ManimFlow."""

import argparse
import sys

from .pipeline import generate_video


def main():
    parser = argparse.ArgumentParser(
        description="ManimFlow - Generate math/physics explainer videos from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  manimflow "Why is e^(iπ) = -1?"
  manimflow "Explain the Pythagorean theorem" --quality h
  manimflow "What is a derivative?" --preview
  manimflow "How does projectile motion work?" --model claude-sonnet-4-20250514
        """,
    )

    parser.add_argument(
        "topic",
        help="Math/physics question, equation, or concept to explain",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--quality", "-q",
        choices=["l", "m", "h", "k"],
        default="l",
        help="Render quality: l=480p, m=720p, h=1080p, k=4K (default: l for fast iteration)",
    )
    parser.add_argument(
        "--preview", "-p",
        action="store_true",
        help="Open video after rendering",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help="Max auto-fix attempts (default: 5)",
    )
    parser.add_argument(
        "--model", "-m",
        default="claude-sonnet-4-20250514",
        help="Claude model to use",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    result = generate_video(
        topic=args.topic,
        output_dir=args.output,
        quality=args.quality,
        max_fix_attempts=args.max_attempts,
        preview=args.preview,
        model=args.model,
        verbose=not args.quiet,
    )

    if result["success"]:
        print(f"\n{'='*50}")
        print(f"✓ VIDEO READY: {result['video_path']}")
        print(f"  Story:  {result['story_path']}")
        print(f"  Code:   {result['code_path']}")
        print(f"  Attempts: {result['attempts']}")
        print(f"{'='*50}")
    else:
        print(f"\n✗ Generation failed after {result['attempts']} attempts")
        print(f"  Last error: {result.get('error', 'unknown')[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
