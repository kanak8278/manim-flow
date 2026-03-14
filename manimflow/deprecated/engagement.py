"""Engagement patterns - research-backed storytelling structures.

Based on:
- 3Blue1Brown's "motivation before definition" approach
- Veritasium's misconception-driven structure (Derek Muller's PhD research)
- Loewenstein's Information Gap Theory (curiosity gap)
- Pixar's story spine adapted for education
- Platform retention data (2025-2026)

Key insight from Veritasium: "Clarity numbs the mind, but confusion can crack it open."
Students who watch "clear" explanations learn nothing because they never engage
with their own misconceptions. The counterintuitive reveal is the mechanism.
"""

# Storytelling structures that can be injected into the story generator
STORYTELLING_STRUCTURES = {
    "misconception_breaker": {
        "name": "Misconception Breaker (Veritasium style)",
        "description": "Surface the wrong intuition, then break it. The viewer's confusion is the mechanism.",
        "best_for": ["mind_blown", "proof", "formula"],
        "template": """
STORYTELLING STRUCTURE: Misconception Breaker

1. SURFACE THE MISCONCEPTION (0-15% of video)
   - Ask what the viewer thinks happens / what the answer is
   - Show the "obvious" but wrong answer visually
   - Make the viewer commit to the wrong intuition

2. BREAK THE INTUITION (15-40%)
   - Show why the obvious answer is wrong
   - Use a visual demonstration that creates surprise
   - Let the viewer sit with the confusion briefly

3. REBUILD CORRECTLY (40-75%)
   - Present the correct model step by step
   - The viewer's mind is now open — confusion cracked it
   - Each step should feel inevitable, not arbitrary

4. THE AHA PAYOFF (75-90%)
   - Everything clicks together
   - Return to the opening question with new understanding
   - The correct answer should now feel obvious

5. EXTEND (90-100%)
   - Show a surprising implication
   - Connect to something bigger
   - Leave an open question for curiosity
""",
    },

    "discovery_narrative": {
        "name": "Discovery Narrative (3Blue1Brown style)",
        "description": "Start with a motivating example, make the viewer WANT the abstraction.",
        "best_for": ["how_it_works", "proof", "formula"],
        "template": """
STORYTELLING STRUCTURE: Discovery Narrative

1. THE PUZZLE (0-10%)
   - Present a compelling visual puzzle or question
   - Make it concrete and specific — not abstract
   - The viewer should think "I want to know why"

2. NAIVE ATTEMPT (10-25%)
   - Try the obvious approach and show it fails or is incomplete
   - This creates the felt NEED for a better tool/concept

3. THE KEY INSIGHT (25-50%)
   - Introduce the mathematical concept as a TOOL to solve the puzzle
   - Build it visually, piece by piece
   - Each step motivated by the original question

4. ELEGANT RESOLUTION (50-75%)
   - Apply the concept to solve the original puzzle
   - Show the solution emerging naturally from the math
   - This is the "aha" — the concept earns its place

5. DEEPER BEAUTY (75-100%)
   - Show this same concept solving other problems
   - Reveal the deeper pattern or connection
   - End with appreciation for mathematical elegance
""",
    },

    "challenge_format": {
        "name": "Challenge Format (viral short-form)",
        "description": "Most people get this wrong. Can you figure it out?",
        "best_for": ["mind_blown", "quick_fact"],
        "template": """
STORYTELLING STRUCTURE: Challenge Format

1. THE CHALLENGE (0-15%)
   - "Most people get this wrong" / "Can you figure this out?"
   - Present the problem clearly with a visual
   - Give the viewer 3-5 seconds to think

2. THE WRONG ANSWER (15-30%)
   - Show the intuitive but wrong answer
   - Explain why it feels right
   - "If you said X, you're not alone — but you're wrong"

3. THE TWIST (30-60%)
   - Reveal why the answer is different
   - Use a visual proof or demonstration
   - Keep it punchy — no lengthy derivations

4. THE REVEAL (60-85%)
   - Show the correct answer with visual emphasis
   - Make it dramatic — color change, scaling, pulsing

5. THE HOOK (85-100%)
   - End with "But wait — what about [related puzzle]?"
   - Or: connect to a deeper concept
   - Drives comments and shares
""",
    },

    "visual_journey": {
        "name": "Visual Journey (beauty-first)",
        "description": "Lead with the beautiful visual, then reveal the simple math behind it.",
        "best_for": ["visual_beauty", "how_it_works"],
        "template": """
STORYTELLING STRUCTURE: Visual Journey

1. THE REVEAL (0-10%)
   - Show the beautiful final result immediately
   - No explanation yet — just the visual impact
   - Dramatic music/pacing

2. THE QUESTION (10-20%)
   - "How can something so complex come from math?"
   - Show the equation — it's surprisingly simple

3. PIECE BY PIECE (20-65%)
   - Build the visual from its components
   - Start with the simplest element
   - Each addition should visually transform the result
   - Color-code each mathematical component

4. THE REBUILD (65-85%)
   - Reconstruct the full visual with all components
   - The viewer now understands each piece
   - The complexity reveals its underlying simplicity

5. THE MOMENT (85-100%)
   - Final dramatic presentation
   - Color transitions, rotations, scaling
   - "Mathematics is the language of beauty"
""",
    },
}

# Hook formulas for the first 3-10 seconds
HOOK_FORMULAS = [
    {
        "type": "question",
        "template": "Have you ever wondered why {phenomenon}?",
        "best_for": ["how_it_works", "proof"],
    },
    {
        "type": "bold_claim",
        "template": "{counterintuitive_statement}",
        "best_for": ["mind_blown", "quick_fact"],
    },
    {
        "type": "challenge",
        "template": "Most people get this wrong: {question}",
        "best_for": ["mind_blown", "quick_fact"],
    },
    {
        "type": "visual_paradox",
        "template": "[Show the paradox visually] — How is this possible?",
        "best_for": ["mind_blown", "visual_beauty"],
    },
    {
        "type": "stakes",
        "template": "This equation changed the world: {equation}",
        "best_for": ["formula", "how_it_works"],
    },
]

# Retention optimization rules
RETENTION_RULES = """
RETENTION OPTIMIZATION (based on real data):
- First 15 seconds: MUST deliver clear value proposition (18% retention boost)
- First 30 seconds: If intro is weak, 33% drop-off
- Visual resets every 10-20 seconds in first minute (Veritasium cadence)
- 25-40 seconds between major transitions after minute 1
- Question-based hooks get 218% more engagement than statements
- NEVER start with "Today we'll learn about..." — start with WHY they should care
- Each scene should have ONE clear visual focus — remove everything else
- Use open loops: pose a question early, answer it late (viewer stays to get resolution)
"""


def get_storytelling_structure(category: str) -> str:
    """Get the best storytelling structure for a category."""
    for structure in STORYTELLING_STRUCTURES.values():
        if category in structure["best_for"]:
            return structure["template"]
    # Default to discovery narrative
    return STORYTELLING_STRUCTURES["discovery_narrative"]["template"]


def get_engagement_context(category: str) -> str:
    """Get full engagement context to inject into story generation."""
    structure = get_storytelling_structure(category)
    return f"{structure}\n\n{RETENTION_RULES}"
