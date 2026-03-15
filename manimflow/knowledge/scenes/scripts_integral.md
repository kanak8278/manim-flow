---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/integral.py
project: manim-scripts
domain: [mathematics, calculus, probability, statistics]
elements: [equation, formula, label]
animations: [write, fade_in, fade_out, transform]
layouts: [vertical_stack, edge_anchored, centered]
techniques: [data_driven, progressive_disclosure]
purpose: [derivation, step_by_step, proof]
mobjects: [MathTex, Text, VGroup]
manim_animations: [Write, FadeIn, FadeOut, Transform, TransformMatchingTex]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 315
scene_classes: [IntegralSolution, IntegralSolution2, IntegralSolution3, IntegralSolution4, IntegralSolution5, IISC2]
---

## Summary

Five progressive iterations of visualizing the integral of 1/(x^2 - x + 1) dx, each adding more derivation detail — from simple completing-the-square to full u-substitution with arctan formula. IntegralSolution5 is the most complete, showing the standard integral form comparison. IISC2 is a separate probability scene about 100-dice problems with binomial coefficients. The file demonstrates iterative refinement of the same mathematical derivation.

## Design Decisions

- **Five iterations of the same integral**: Each scene class adds more intermediate steps. This is useful as a reference for how much derivation detail to show — from minimal (IntegralSolution4: just 4 equations) to exhaustive (IntegralSolution5: full substitution).
- **FadeOut old + Write new pattern**: Each derivation step fades out the previous expression and writes the new one. This keeps the screen uncluttered but sacrifices the ability to see all steps simultaneously.
- **Corner anchoring for reference expressions**: The original integral moves to UL corner (scaled to 0.8) to serve as a persistent reference while new steps appear in the center/below.
- **TransformMatchingTex for algebraic steps (IntegralSolution5)**: Used to morph between equation forms where substrings match, showing the algebraic manipulation visually.
- **Binomial probability formatting**: IISC2 uses MathTex with `{100 \choose k}` and fraction notation to display the standard binomial probability formula.
- **t2c for emphasis**: Problem text uses `t2c={'Problem': YELLOW}` to highlight the word "Problem" in yellow.

## Composition

- **Reference integral**: to_corner(UL), scale=0.8
- **Derivation steps**: next_to(previous, DOWN, buff=0.2), aligned_edge=LEFT for vertical chain
- **Substitution text**: scale=0.7, next_to formula
- **Final result**: scale=0.8, to_corner(UR)
- **IISC2 text positioning**: text1 at UP*3.5, subsequent texts next_to(previous, DOWN)
- **Formula arrangement**: arrange(direction=RIGHT) for probability formula parts

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| MathTex expressions | WHITE | Default |
| "Problem" keyword | YELLOW | Via t2c map |
| Problem text | WHITE | scale=0.8, 0.5 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Write expression | Default (~1s) | Each derivation step |
| FadeIn integral | Default | Opening |
| Wait between steps | 2s | Standard |
| FadeOut transition | Default | Between steps |
| Total (IntegralSolution4) | ~12s | 4 steps + waits |
| Total (IntegralSolution5) | ~30s | Full derivation |
| Total (IISC2) | ~20s | Problem + 2 formulas |

## Patterns

### Pattern: Progressive Derivation with Corner Reference

**What**: Move the original expression to UL corner at reduced scale, then write derivation steps below it. The original stays visible as a reference while new work happens in the main area. FadeOut intermediate steps to keep the screen clean.
**When to use**: Any multi-step mathematical derivation — integration, differentiation, proof steps, algebraic simplification. The persistent reference prevents the viewer from losing context.

```python
# Source: projects/manim-scripts/scenes/integral.py:14-18
integral_expression.to_edge(LEFT)
self.play(Write(square_part.next_to(integral_expression, RIGHT)))
self.wait(1)
self.play(FadeOut(square_part), integral_expression.animate.to_corner(UL))
self.play(Write(completed_square))
```

### Pattern: Sequential Equation Replacement

**What**: Show a sequence of equivalent equations, each replacing the previous with FadeOut/Write. The simplest approach for step-by-step derivations where you do not need to show matching parts.
**When to use**: When equations change substantially between steps (unlike TransformMatchingTex which needs matching substrings). Good for integral evaluation, differential equation solutions, or any chain of transformations.

```python
# Source: projects/manim-scripts/scenes/integral.py:147-163
integral_expression1 = MathTex(r"\int \frac{1}{x^2 - x + 1} \, dx")
integral_expression2 = MathTex(r"\int \frac{1}{x^2 - x + \frac{1}{4} + \frac{3}{4}} \, dx")
integral_expression3 = MathTex(r"\int \frac{1}{(x - \frac{1}{2})^2 + (\frac{\sqrt{3}}{2})^2} \, dx")
integral_expression4 = MathTex(r"\frac{2}{3} \sqrt{3} \arctan \left( ... \right) + C")
self.play(Write(integral_expression1))
self.wait(2)
self.play(FadeOut(integral_expression1), Write(integral_expression2))
self.wait(2)
# ... repeat pattern ...
```

### Pattern: Binomial Probability Formula Display

**What**: Display a binomial probability formula with MathTex, using `{n \choose k}` notation and fraction terms arranged horizontally.
**When to use**: Probability problems involving dice, coins, sampling, or any binomial distribution scenario. Also useful for combinatorics visualizations.

```python
# Source: projects/manim-scripts/scenes/integral.py:281-295
formula1 = MathTex(
    r"P(\text{Exactly one 4}) = ",
    r"{100 \choose 1}",
    r"\left(\frac{1}{6}\right)^1",
    r"\left(\frac{5}{6}\right)^{99}"
)
formula1.arrange(direction=RIGHT)
self.play(Write(formula1))
```

## Scene Flow

1. **IntegralSolution** (0-15s): Integral appears, completing the square shown, arctan introduced, final result.
2. **IntegralSolution2-3** (0-20s): More detailed intermediate steps including decomposition.
3. **IntegralSolution4** (0-12s): Cleanest version — 4 sequential equations, FadeOut/Write transitions.
4. **IntegralSolution5** (0-30s): Full derivation with u-substitution, standard form comparison, back-substitution.
5. **IISC2** (0-20s): Problem text, exactly-one-4 binomial formula, at-most-one-4 summation formula.

> Full file: `projects/manim-scripts/scenes/integral.py` (315 lines)
