"""Transition vocabulary — maps semantic relationships to Manim animation types.

Key insight from 3Blue1Brown: Transitions ARE the explanation.
A morph from equation A to B isn't decoration — it shows the mathematical relationship.

This module tells the codegen WHICH transition to use based on the
relationship between concepts, not just "fade in, fade out".
"""

# Semantic transition map — what relationship between concepts drives which animation
TRANSITION_VOCABULARY = {
    "derivation": {
        "description": "Concept B is mathematically derived from concept A",
        "manim_code": "self.play(ReplacementTransform(eq_a, eq_b), run_time=2)",
        "example": "x^2 → 2x (differentiation)",
    },
    "equivalence": {
        "description": "Two representations of the same thing",
        "manim_code": "self.play(TransformMatchingShapes(form_a, form_b), run_time=2)",
        "example": "0.999... ↔ 1",
    },
    "zoom_detail": {
        "description": "Examining a specific part of something larger",
        "manim_code": (
            "# Use MovingCameraScene\n"
            "self.play(self.camera.frame.animate.scale(0.5).move_to(detail), run_time=2)"
        ),
        "example": "Zoom into one term of an equation",
    },
    "zoom_context": {
        "description": "Pulling back to see the big picture",
        "manim_code": "self.play(self.camera.frame.animate.scale(2).move_to(ORIGIN), run_time=2)",
        "example": "After explaining a component, show full formula",
    },
    "topic_change": {
        "description": "Moving to an entirely new topic/section",
        "manim_code": (
            "self.play(*[FadeOut(m, shift=LEFT) for m in self.mobjects], run_time=1)\n"
            "# ... new content ...\n"
            "self.play(FadeIn(new_content, shift=RIGHT), run_time=1)"
        ),
        "example": "From 'What is a derivative?' to 'Why does it matter?'",
    },
    "cause_effect": {
        "description": "A causes B — showing consequence",
        "manim_code": (
            "self.play(Indicate(cause, color=YELLOW), run_time=1)\n"
            "arrow = Arrow(cause, effect, color=YELLOW)\n"
            "self.play(GrowArrow(arrow), run_time=1)\n"
            "self.play(FadeIn(effect), run_time=1)"
        ),
        "example": "Dividing by zero → contradiction",
    },
    "comparison": {
        "description": "Showing two things side by side",
        "manim_code": (
            "group = VGroup(item_a, item_b).arrange(RIGHT, buff=2)\n"
            "self.play(FadeIn(item_a, shift=LEFT), FadeIn(item_b, shift=RIGHT), run_time=2)"
        ),
        "example": "Finite vs infinite",
    },
    "progressive_build": {
        "description": "Adding complexity step by step",
        "manim_code": (
            "self.play(Write(step1), run_time=1.5)\n"
            "self.wait(1)\n"
            "self.play(Write(step2), run_time=1.5)\n"
            "self.play(Indicate(VGroup(step1, step2)), run_time=1)"
        ),
        "example": "Building an equation term by term",
    },
    "reveal": {
        "description": "Dramatic reveal of key result",
        "manim_code": (
            "result.scale(0)\n"
            "self.play(result.animate.scale(1), run_time=1.5, rate_func=rush_from)\n"
            "self.play(Flash(result.get_center(), color=YELLOW), run_time=1)\n"
            "self.play(Circumscribe(result, color=YELLOW), run_time=1.5)"
        ),
        "example": "The final answer / aha moment",
    },
    "contradiction": {
        "description": "Showing something leads to an impossibility",
        "manim_code": (
            "self.play(statement.animate.set_color(RED), run_time=1)\n"
            "cross = Cross(statement, color=RED, stroke_width=6)\n"
            "self.play(Create(cross), run_time=1)"
        ),
        "example": "If 1/0 = x, then 0*x = 1, but 0*x = 0. Contradiction!",
    },
}


def get_transition_guide() -> str:
    """Generate a transition guide for the codegen prompt."""
    lines = [
        "## TRANSITION VOCABULARY (use the right transition for each concept relationship):"
    ]
    for name, t in TRANSITION_VOCABULARY.items():
        lines.append(f"\n### {name.upper()}: {t['description']}")
        lines.append(f"Example: {t['example']}")
        lines.append(f"```python\n{t['manim_code']}\n```")
    return "\n".join(lines)
