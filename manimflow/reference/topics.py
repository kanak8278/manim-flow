"""Topic suggestion and scoring system.

Based on research finding: topics that score 7+ on BOTH "intuition violation"
AND "visual demonstrability" are the highest-performing content.

Also includes a curated library of proven viral math/physics topics.
"""

from ..core.agent import call_llm, extract_json


# Curated topic library — topics proven to drive engagement
TOPIC_LIBRARY = {
    "mind_blown": [
        {
            "topic": "Why is 0.999... exactly equal to 1?",
            "intuition_score": 10,
            "visual_score": 8,
            "hook": "This number IS one. Not approximately. Exactly. And you can prove it.",
        },
        {
            "topic": "The Monty Hall Problem — why switching doors wins",
            "intuition_score": 10,
            "visual_score": 9,
            "hook": "99% of people refuse to switch. They're all wrong.",
        },
        {
            "topic": "Some infinities are bigger than others (Cantor's diagonal argument)",
            "intuition_score": 10,
            "visual_score": 8,
            "hook": "There are more real numbers between 0 and 1 than there are whole numbers... forever.",
        },
        {
            "topic": "The Birthday Paradox — 23 people, 50% chance of a match",
            "intuition_score": 9,
            "visual_score": 9,
            "hook": "In a room of just 23 people, there's a coin-flip chance two share a birthday.",
        },
        {
            "topic": "Gabriel's Horn — infinite surface, finite volume",
            "intuition_score": 10,
            "visual_score": 10,
            "hook": "You can fill this shape with paint, but you can never paint its surface.",
        },
        {
            "topic": "Why negative times negative is positive",
            "intuition_score": 7,
            "visual_score": 8,
            "hook": "Your math teacher said 'just memorize it.' Here's why it HAS to be true.",
        },
    ],

    "proof": [
        {
            "topic": "Why is the area of a circle pi*r^2? Visual proof.",
            "intuition_score": 7,
            "visual_score": 10,
            "hook": "Slice a pizza into infinite pieces and rearrange them. Watch what happens.",
        },
        {
            "topic": "The Pythagorean theorem — the most visual proof",
            "intuition_score": 6,
            "visual_score": 10,
            "hook": "One picture. No words needed. The proof is in the shapes.",
        },
        {
            "topic": "Why the angles of a triangle always add to 180 degrees",
            "intuition_score": 7,
            "visual_score": 9,
            "hook": "Tear off the corners of any triangle. Watch them form a straight line.",
        },
        {
            "topic": "Why the sum 1 + 2 + 3 + ... + n = n(n+1)/2",
            "intuition_score": 7,
            "visual_score": 10,
            "hook": "A 10-year-old Gauss figured this out in seconds. Here's how.",
        },
    ],

    "formula": [
        {
            "topic": "E = mc^2: What does it really mean?",
            "intuition_score": 8,
            "visual_score": 7,
            "hook": "The paperclip on your desk contains enough energy to power a city for a year.",
        },
        {
            "topic": "What is Euler's identity e^(i*pi) + 1 = 0?",
            "intuition_score": 9,
            "visual_score": 9,
            "hook": "Five fundamental constants. One equation. Zero.",
        },
        {
            "topic": "F = ma — what is force really?",
            "intuition_score": 7,
            "visual_score": 8,
            "hook": "Force isn't what you think it is. Newton's second law hides a deeper truth.",
        },
        {
            "topic": "The wave equation and why everything vibrates",
            "intuition_score": 8,
            "visual_score": 10,
            "hook": "One equation describes ocean waves, guitar strings, and light itself.",
        },
    ],

    "how_it_works": [
        {
            "topic": "How does GPS use relativity to find your location?",
            "intuition_score": 8,
            "visual_score": 8,
            "hook": "Without Einstein, your GPS would be off by 10km every day.",
        },
        {
            "topic": "How does the Fourier Transform hear individual instruments in a song?",
            "intuition_score": 8,
            "visual_score": 10,
            "hook": "One equation lets your phone separate every voice in a crowded room.",
        },
        {
            "topic": "How does public key cryptography keep your messages secret?",
            "intuition_score": 8,
            "visual_score": 7,
            "hook": "You can publish the lock, keep the key, and nobody can break in.",
        },
    ],

    "visual_beauty": [
        {
            "topic": "The butterfly curve — chaos becomes beauty",
            "intuition_score": 7,
            "visual_score": 10,
            "hook": "Three simple terms. One equation. Pure mathematical beauty.",
        },
        {
            "topic": "The Mandelbrot Set — infinite complexity from z^2 + c",
            "intuition_score": 9,
            "visual_score": 10,
            "hook": "Zoom in forever. It never stops being beautiful. And it never repeats.",
        },
        {
            "topic": "Lissajous curves — when frequencies dance",
            "intuition_score": 7,
            "visual_score": 10,
            "hook": "What happens when two sine waves collide? Art.",
        },
    ],

    "what_if": [
        {
            "topic": "What if pi was exactly 3?",
            "intuition_score": 9,
            "visual_score": 9,
            "hook": "Wheels wouldn't roll. GPS would fail. The universe would break.",
        },
        {
            "topic": "What if gravity was twice as strong?",
            "intuition_score": 8,
            "visual_score": 8,
            "hook": "You couldn't stand up. Trees couldn't grow. And the sun would explode sooner.",
        },
        {
            "topic": "What happens at absolute zero? Can you actually reach it?",
            "intuition_score": 8,
            "visual_score": 7,
            "hook": "The coldest possible temperature... that you can never actually reach.",
        },
    ],

    "quick_fact": [
        {
            "topic": "Why can't you divide by zero?",
            "intuition_score": 8,
            "visual_score": 8,
            "hook": "It's not that you're 'not allowed.' It's that the answer doesn't exist.",
        },
        {
            "topic": "What is the golden ratio and why is it everywhere?",
            "intuition_score": 7,
            "visual_score": 9,
            "hook": "1.618... appears in sunflowers, galaxies, and your credit card.",
        },
        {
            "topic": "Why is a minute 60 seconds, not 100?",
            "intuition_score": 7,
            "visual_score": 7,
            "hook": "Blame the Babylonians. They counted to 60 on their fingers.",
        },
    ],
}


def get_suggested_topics(category: str | None = None, count: int = 5) -> list[dict]:
    """Get suggested topics, optionally filtered by category."""
    topics = []
    if category and category in TOPIC_LIBRARY:
        topics = TOPIC_LIBRARY[category]
    else:
        for cat_topics in TOPIC_LIBRARY.values():
            topics.extend(cat_topics)

    # Sort by combined score (intuition * visual)
    topics.sort(key=lambda t: t["intuition_score"] * t["visual_score"], reverse=True)
    return topics[:count]


async def score_topic(topic: str) -> dict:
    """Score a user-provided topic on the two key axes using LLM."""
    prompt = f"""Score this educational video topic on two axes (1-10 each):

TOPIC: {topic}

1. INTUITION VIOLATION (1-10): How much does the result/concept contradict what most people expect?
   - 10: "That can't be right!" (Monty Hall, 0.999=1)
   - 7: "Hmm, I wouldn't have guessed that" (area of circle proof)
   - 4: "Makes sense, just didn't know the details"
   - 1: "Obviously true, nothing surprising"

2. VISUAL DEMONSTRABILITY (1-10): How well can this be shown with animation?
   - 10: The concept IS visual (curves, geometry, motion)
   - 7: Can be visualized with diagrams/graphs
   - 4: Mostly abstract, some visual metaphors possible
   - 1: Pure abstraction, no natural visual representation

Return JSON: {{"intuition_score": N, "visual_score": N, "combined": N, "suggested_category": "category_id", "hook_suggestion": "one-line hook"}}"""

    try:
        response = await call_llm("You are a content strategist for educational math/physics videos.", prompt)
        return extract_json(response)
    except Exception:
        return {"intuition_score": 5, "visual_score": 5, "combined": 25, "suggested_category": "formula"}
