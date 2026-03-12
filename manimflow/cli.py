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
  manimflow "Why is e^(ipi) = -1?"
  manimflow "Explain the Pythagorean theorem" --quality h
  manimflow "What is a derivative?" --preview
  manimflow "How does projectile motion work?"
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
        "--duration", "-d",
        type=int,
        default=120,
        help="Target video duration in seconds: 60=short, 120=standard, 300=deep, 480=long (default: 120)",
    )
    parser.add_argument(
        "--max-fix-attempts",
        type=int,
        default=5,
        help="Max code fix attempts per render (default: 5)",
    )
    parser.add_argument(
        "--max-quality-loops",
        type=int,
        default=2,
        help="Max quality improvement iterations (default: 2)",
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
        duration=args.duration,
        max_fix_attempts=args.max_fix_attempts,
        max_quality_loops=args.max_quality_loops,
        preview=args.preview,
        verbose=not args.quiet,
    )

    if result["success"]:
        print(f"\n{'='*50}")
        print(f"VIDEO READY: {result['video_path']}")
        print(f"  Story:  {result['story_path']}")
        print(f"  Code:   {result['code_path']}")
        print(f"{'='*50}")
    else:
        print(f"\nGeneration failed")
        print(f"  Last error: {result.get('error', 'unknown')[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
