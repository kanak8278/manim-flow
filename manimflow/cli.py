"""CLI interface for ManimFlow."""

import argparse
import sys

from .pipeline import generate_video
from .categories import list_categories, CATEGORIES
from .topics import get_suggested_topics


def main():
    parser = argparse.ArgumentParser(
        description="ManimFlow - Generate math/physics explainer videos from text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  manimflow "Why is e^(ipi) = -1?"
  manimflow "Explain the Pythagorean theorem" --quality h --duration 300
  manimflow "What is a derivative?" --category proof
  manimflow "The butterfly curve" --category visual_beauty --duration 60

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

    subparsers = parser.add_subparsers(dest="command")

    # Subcommands
    subparsers.add_parser("categories", help="List available content categories")
    topics_parser = subparsers.add_parser("topics", help="Get suggested topics")
    topics_parser.add_argument("--category", "-c", default=None, help="Filter by category")
    topics_parser.add_argument("--count", "-n", type=int, default=10, help="Number of topics")

    # Default: generate video
    parser.add_argument(
        "topic",
        nargs="?",
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
        help="Render quality: l=480p, m=720p, h=1080p, k=4K (default: l)",
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
        help="Target duration: 60=short, 120=standard, 300=deep, 480=long (default: 120)",
    )
    parser.add_argument(
        "--category", "-c",
        choices=list(CATEGORIES.keys()),
        default=None,
        help="Content category (auto-detected if omitted)",
    )
    parser.add_argument(
        "--voice", "-v",
        choices=["male_us", "female_us", "male_uk", "female_uk", "male_au"],
        default=None,
        help="Add voiceover narration (default: no voiceover)",
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

    # Handle subcommands
    if args.command == "categories":
        _print_categories()
        return
    if args.command == "topics":
        _print_topics(args.category, args.count)
        return

    if not args.topic:
        parser.print_help()
        sys.exit(1)

    result = generate_video(
        topic=args.topic,
        output_dir=args.output,
        quality=args.quality,
        duration=args.duration,
        category=args.category,
        voice=args.voice,
        max_fix_attempts=args.max_fix_attempts,
        max_quality_loops=args.max_quality_loops,
        preview=args.preview,
        verbose=not args.quiet,
    )

    if result["success"]:
        print(f"\n{'='*50}")
        print(f"VIDEO READY: {result['video_path']}")
        print(f"  Story:    {result['story_path']}")
        print(f"  Code:     {result['code_path']}")
        print(f"  Category: {result.get('story', {}).get('category', 'auto')}")
        print(f"{'='*50}")
    else:
        print(f"\nGeneration failed")
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
        print(f"      Intuition: {t['intuition_score']}/10 | Visual: {t['visual_score']}/10")
        print()


if __name__ == "__main__":
    main()
