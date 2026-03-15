"""CLI interface for ManimFlow."""

import argparse
import asyncio
import sys

from .pipeline import generate_video
from .reference.categories import list_categories, CATEGORIES
from .reference.topics import get_suggested_topics


def main():
    # Handle subcommands first (before argparse, to avoid conflict with topic positional)
    if len(sys.argv) >= 2:
        if sys.argv[1] == "categories":
            _print_categories()
            return
        if sys.argv[1] == "topics":
            # Parse topics-specific args
            count = 10
            category = None
            for i, arg in enumerate(sys.argv[2:], 2):
                if arg in ("--count", "-n") and i + 1 < len(sys.argv):
                    count = int(sys.argv[i + 1])
                if arg in ("--category", "-c") and i + 1 < len(sys.argv):
                    category = sys.argv[i + 1]
            _print_topics(category, count)
            return

    parser = argparse.ArgumentParser(
        description="ManimFlow - Generate math/physics explainer videos from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run manimflow "Why is e^(ipi) = -1?"
  uv run manimflow "Explain the Pythagorean theorem" --quality h --duration 300
  uv run manimflow "What is a derivative?" --category proof
  uv run manimflow "The butterfly curve" --category visual_beauty --duration 60
  uv run manimflow topics
  uv run manimflow categories

Categories:
  mind_blown      Paradoxes, surprising results
  how_it_works    Mechanism explainers
  proof           Proofs and derivations
  what_if         Thought experiments
  formula         Famous equations decoded
  visual_beauty   Mathematical art and patterns
  quick_fact      60-second explainers
        """,
    )

    parser.add_argument(
        "topic",
        help="Math/physics question, equation, or concept to explain",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory (default: output/<timestamp>)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        choices=["l", "m", "h", "k"],
        default="l",
        help="Render quality: l=480p, m=720p, h=1080p, k=4K (default: l)",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Open video after rendering",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=120,
        help="Target duration: 60=short, 120=standard, 300=deep, 480=long (default: 120)",
    )
    parser.add_argument(
        "--category",
        "-c",
        choices=list(CATEGORIES.keys()),
        default=None,
        help="Content category (auto-detected if omitted)",
    )
    parser.add_argument(
        "--voice",
        "-v",
        choices=["male_us", "female_us", "male_uk", "female_uk", "male_au", "none"],
        default="male_us",
        help="Voiceover voice (default: male_us, use 'none' to disable)",
    )
    parser.add_argument(
        "--max-fix-attempts",
        type=int,
        default=5,
        help="Max code fix attempts (default: 5)",
    )
    parser.add_argument(
        "--max-quality-loops",
        type=int,
        default=2,
        help="Max quality improvement rounds (default: 2)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    # Auto-generate output dir from timestamp if not provided
    if args.output is None:
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"output/{ts}"

    result = asyncio.run(
        generate_video(
            topic=args.topic,
            output_dir=args.output,
            quality=args.quality,
            duration=args.duration,
            category=args.category,
            voice=args.voice if args.voice != "none" else None,
            max_fix_attempts=args.max_fix_attempts,
            max_quality_loops=args.max_quality_loops,
            preview=args.preview,
            verbose=not args.quiet,
        )
    )

    if result["success"]:
        print(f"\n{'=' * 50}")
        print(f"VIDEO READY: {result['video_path']}")
        print(f"  Story:    {result['story_path']}")
        print(f"  Code:     {result['code_path']}")
        print(f"  Category: {result.get('story', {}).get('category', 'auto')}")
        print(f"{'=' * 50}")
    else:
        print("\nGeneration failed")
        print(f"  Last error: {result.get('error', 'unknown')[:200]}")
        sys.exit(1)


def _print_categories():
    """Print available content categories."""
    print("\nAvailable Content Categories:\n")
    for cat in list_categories():
        print(f"  {cat['id']:15s}  {cat['name']}")
        print(f"  {'':15s}  {cat['description']}")
        print(f"  {'':15s}  Duration: ~{cat['duration']}s")
        print(f"  {'':15s}  Examples: {', '.join(cat['examples'])}")
        print()


def _print_topics(category: str | None, count: int):
    """Print suggested topics."""
    topics = get_suggested_topics(category, count)
    print("\nSuggested Topics (sorted by engagement potential):\n")
    for i, t in enumerate(topics, 1):
        score = t["intuition_score"] * t["visual_score"]
        print(f"  {i:2d}. [{score:3d}] {t['topic']}")
        print(f"      Hook: {t['hook']}")
        print(
            f"      Intuition: {t['intuition_score']}/10 | Visual: {t['visual_score']}/10"
        )
        print()


if __name__ == "__main__":
    main()
