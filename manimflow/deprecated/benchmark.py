"""Benchmark suite — measures pipeline quality across fixed topics.

Run this after every change to prove it helps (or doesn't hurt).
Compares scores across runs to track improvement over time.
"""

import json
import os
import time
from datetime import datetime

from .reviewers.design_reviewer import DesignReviewer
from .reviewers.story_reviewer import StoryReviewer
from .reviewers.base import print_review


# Fixed benchmark topics — always test these
BENCHMARK_TOPICS = [
    {
        "topic": "Why is the area of a circle pi*r^2?",
        "category": "proof",
        "type": "math",
    },
    {
        "topic": "The Monty Hall Problem — why switching doors wins",
        "category": "mind_blown",
        "type": "math",
    },
    {
        "topic": "How does GPS use relativity to find your location?",
        "category": "how_it_works",
        "type": "physics",
    },
    {
        "topic": "Explain the Indian judiciary system",
        "category": "how_it_works",
        "type": "non_math",
    },
    {
        "topic": "What is a derivative? The slope at any point on a curve.",
        "category": "proof",
        "type": "math",
    },
]


def run_story_benchmark(story: dict, topic: str, verbose: bool = True) -> dict:
    """Benchmark a story using the story reviewer."""
    reviewer = StoryReviewer()
    result = reviewer.review(
        artifact=story,
        context={"topic": topic, "hook": story.get("hook_question", "")},
    )
    if verbose:
        print_review(result)
    return {
        "stage": "story",
        "score": result.score,
        "verdict": result.verdict,
        "issues": result.issues,
        "fixes": result.fixes,
    }


def run_design_benchmark(design: dict, topic: str, title: str = "",
                          verbose: bool = True) -> dict:
    """Benchmark a design system using the design reviewer."""
    reviewer = DesignReviewer()
    result = reviewer.review(
        artifact=design,
        context={"topic": topic, "title": title},
    )
    if verbose:
        print_review(result)
    return {
        "stage": "design",
        "score": result.score,
        "verdict": result.verdict,
        "issues": result.issues,
        "fixes": result.fixes,
    }


def benchmark_existing_outputs(output_base: str = "output", verbose: bool = True) -> dict:
    """Run reviewers on all existing test outputs to get baseline scores."""
    results = {}

    for test_dir in sorted(os.listdir(output_base)):
        dir_path = os.path.join(output_base, test_dir)
        story_path = os.path.join(dir_path, "story.json")
        design_path = os.path.join(dir_path, "design_system.json")

        if not os.path.exists(story_path):
            continue

        print(f"\n{'='*50}")
        print(f"Benchmarking: {test_dir}")
        print(f"{'='*50}")

        with open(story_path) as f:
            story = json.load(f)

        topic = story.get("title", test_dir)
        scores = {"test": test_dir, "topic": topic}

        # Story review
        story_result = run_story_benchmark(story, topic, verbose)
        scores["story_score"] = story_result["score"]

        # Design review (if available)
        if os.path.exists(design_path):
            with open(design_path) as f:
                design = json.load(f)
            design_result = run_design_benchmark(design, topic, story.get("title", ""), verbose)
            scores["design_score"] = design_result["score"]

        results[test_dir] = scores

    # Summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")
    story_scores = [r["story_score"] for r in results.values() if "story_score" in r]
    design_scores = [r["design_score"] for r in results.values() if "design_score" in r]

    if story_scores:
        print(f"Story: avg={sum(story_scores)/len(story_scores):.1f}/10 "
              f"(min={min(story_scores)}, max={max(story_scores)}, n={len(story_scores)})")
    if design_scores:
        print(f"Design: avg={sum(design_scores)/len(design_scores):.1f}/10 "
              f"(min={min(design_scores)}, max={max(design_scores)}, n={len(design_scores)})")

    return results


def save_benchmark_results(results: dict, output_path: str = "benchmark_results.json"):
    """Save benchmark results with timestamp for tracking over time."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    # Append to history
    history = []
    if os.path.exists(output_path):
        with open(output_path) as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append(entry)

    with open(output_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nSaved to {output_path} ({len(history)} benchmark runs)")
