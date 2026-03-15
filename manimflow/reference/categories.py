"""Content categories and templates for different types of educational videos.

Inspired by what works on YouTube, TikTok, and educational platforms:
- "Mind-blown" content (paradoxes, surprising results)
- "How does X work?" (mechanism explainers)
- "Why is this true?" (proof/derivation walkthroughs)
- "What if?" (thought experiments)
- "History of" (biographical/discovery stories)
"""

from dataclasses import dataclass


@dataclass
class ContentCategory:
    id: str
    name: str
    description: str
    example_topics: list[str]
    story_hints: str  # Extra context for the story generator
    visual_style: str  # Hints for the code generator
    recommended_duration: int  # seconds


CATEGORIES = {
    "mind_blown": ContentCategory(
        id="mind_blown",
        name="Mind-Blown Moment",
        description="Surprising mathematical results, paradoxes, counter-intuitive truths",
        example_topics=[
            "Why is 0.999... = 1?",
            "The Banach-Tarski paradox",
            "Why is e^(i*pi) = -1?",
            "Infinity comes in different sizes",
            "Gabriel's Horn: infinite surface, finite volume",
        ],
        story_hints=(
            "Start with the surprising result. Let the viewer's disbelief build. "
            "Then systematically dismantle their intuition and rebuild it correctly. "
            "The aha moment should feel like a magic trick revealed. "
            "End by showing the deeper truth that makes it obvious in hindsight."
        ),
        visual_style=(
            "High contrast, dramatic reveals. Use color transitions from confused/red "
            "to understanding/blue. Big bold equations that transform. "
            "Pulsing or scaling effects at the reveal moment."
        ),
        recommended_duration=120,
    ),
    "how_it_works": ContentCategory(
        id="how_it_works",
        name="How Does It Work?",
        description="Mechanism explainers — how mathematical/physical processes work",
        example_topics=[
            "How does GPS use relativity?",
            "How does Fourier Transform break signals into waves?",
            "How does public key cryptography work?",
            "How do neural networks learn?",
            "How does gravity bend light?",
        ],
        story_hints=(
            "Start with the real-world application people can relate to. "
            "Progressively zoom into the mechanism, layer by layer. "
            "Use analogies to bridge from familiar to unfamiliar. "
            "Show the process in action before explaining why it works."
        ),
        visual_style=(
            "Process diagrams, step-by-step animations. Arrows showing flow. "
            "Split screen to show input vs output. Progressive building "
            "of complexity with labeled stages."
        ),
        recommended_duration=180,
    ),
    "proof": ContentCategory(
        id="proof",
        name="Why Is This True?",
        description="Proof walkthroughs, derivations, 'why' explanations",
        example_topics=[
            "Why is the area of a circle pi*r^2?",
            "Why does the Pythagorean theorem work?",
            "Why is the sum of angles in a triangle 180°?",
            "Why does e appear everywhere?",
            "Why is 1+2+3+... = -1/12?",
        ],
        story_hints=(
            "State the result clearly first. Build the proof step by step, "
            "but make each step feel inevitable, not arbitrary. "
            "Use visual proofs where possible — geometry over algebra. "
            "The journey matters more than the destination."
        ),
        visual_style=(
            "Geometric constructions, step-by-step equation building. "
            "Color-code each step of the proof. Use Transform animations "
            "to show algebraic manipulations. Axes and graphs for function proofs."
        ),
        recommended_duration=180,
    ),
    "what_if": ContentCategory(
        id="what_if",
        name="What If?",
        description="Thought experiments, hypotheticals, extreme scenarios",
        example_topics=[
            "What if pi was exactly 3?",
            "What if gravity was twice as strong?",
            "What if you could travel at the speed of light?",
            "What if the Earth stopped spinning?",
            "What happens at absolute zero?",
        ],
        story_hints=(
            "Set up the scenario vividly — make the viewer picture it. "
            "Explore consequences step by step, from obvious to surprising. "
            "Use 'and then...' structure to build chain reactions. "
            "End by connecting back to why reality works the way it does."
        ),
        visual_style=(
            "Simulation-style animations. Before/after comparisons. "
            "Dramatic parameter changes with ValueTracker. "
            "Physics simulations with changing constants. "
            "Split screen showing normal vs hypothetical."
        ),
        recommended_duration=180,
    ),
    "formula": ContentCategory(
        id="formula",
        name="Famous Formula",
        description="Deep dives into iconic equations and what they mean",
        example_topics=[
            "E = mc^2: What does it really mean?",
            "F = ma: What is force?",
            "The Schrodinger equation explained",
            "Maxwell's equations in 5 minutes",
            "The wave equation and why it matters",
        ],
        story_hints=(
            "Don't just show the formula — decode it. Each symbol is a character "
            "in a story. Build up to the formula by showing the physics/math "
            "it describes. Then show how the formula captures that reality "
            "in compact notation. End by showing what predictions it makes."
        ),
        visual_style=(
            "Large, central equation that gets annotated piece by piece. "
            "Color-code each variable. Use braces and arrows to label parts. "
            "Show physical scenarios that correspond to each term. "
            "Animate what happens when you change each variable."
        ),
        recommended_duration=120,
    ),
    "visual_beauty": ContentCategory(
        id="visual_beauty",
        name="Mathematical Beauty",
        description="Visually stunning mathematical objects and patterns",
        example_topics=[
            "The butterfly curve",
            "Mandelbrot set zoom",
            "Lissajous curves and harmony",
            "The heart curve equation",
            "Spirograph mathematics",
            "Fractals in nature",
        ],
        story_hints=(
            "Lead with the visual — show the beautiful result immediately. "
            "Then reveal the surprisingly simple math behind it. "
            "Build the shape progressively, component by component. "
            "Use color and motion to enhance the aesthetic experience. "
            "Connect math to art, music, or nature."
        ),
        visual_style=(
            "Rich color gradients, smooth parametric curves. "
            "Progressive curve building with color transitions. "
            "Dramatic final reveals with rotation and scaling. "
            "Rainbow color sweeps. Slow, meditative pacing for curves."
        ),
        recommended_duration=120,
    ),
    "quick_fact": ContentCategory(
        id="quick_fact",
        name="Quick Math Fact",
        description="60-second explainers perfect for short-form content",
        example_topics=[
            "Why can't you divide by zero?",
            "What is the golden ratio?",
            "Why is a negative times a negative positive?",
            "What does 'undefined' really mean?",
            "The difference between average and median",
        ],
        story_hints=(
            "ONE concept. ONE visual. ONE punchline. "
            "Hook in first 3 seconds with a question or bold claim. "
            "Build for 30 seconds. Reveal in 15. Tag in 10. "
            "No detours, no context, no history — pure focused insight."
        ),
        visual_style=(
            "Bold, simple visuals. Large text. High contrast. "
            "One main animation that tells the whole story. "
            "Minimal scene transitions. Fast pacing."
        ),
        recommended_duration=60,
    ),
}


def get_category(category_id: str) -> ContentCategory | None:
    """Get a category by ID."""
    return CATEGORIES.get(category_id)


def suggest_category(topic: str) -> str:
    """Suggest the best category for a given topic (simple keyword matching)."""
    topic_lower = topic.lower()

    # Keyword-based matching
    if any(
        w in topic_lower
        for w in ["paradox", "surprise", "impossible", "infinity", "0.999"]
    ):
        return "mind_blown"
    if any(w in topic_lower for w in ["how does", "how do", "mechanism", "process"]):
        return "how_it_works"
    if any(w in topic_lower for w in ["why", "prove", "proof", "derive", "derivation"]):
        return "proof"
    if any(
        w in topic_lower for w in ["what if", "what happens", "imagine", "hypothetical"]
    ):
        return "what_if"
    if any(w in topic_lower for w in ["equation", "formula", "= ", "e = mc"]):
        return "formula"
    if any(
        w in topic_lower for w in ["curve", "beautiful", "visual", "pattern", "fractal"]
    ):
        return "visual_beauty"
    if any(
        w in topic_lower
        for w in ["quick", "fact", "simple", "why can't", "what is the"]
    ):
        return "quick_fact"

    # Default to standard explainer
    return "formula"


def list_categories() -> list[dict]:
    """List all available categories."""
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "examples": cat.example_topics[:3],
            "duration": cat.recommended_duration,
        }
        for cat in CATEGORIES.values()
    ]
