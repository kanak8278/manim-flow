---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/calculus.py
project: manim-scripts
domain: [mathematics, calculus, algebra]
elements: [equation, formula, axes, function_plot, parametric_curve, surrounding_rect, number_line]
animations: [write, transform, replacement_transform, fade_in, fade_out, draw, move]
layouts: [centered, vertical_stack, edge_anchored]
techniques: [moving_camera, data_driven]
purpose: [derivation, step_by_step, demonstration, transformation]
mobjects: [MathTex, VGroup, Axes, NumberPlane, SurroundingRectangle, Text]
manim_animations: [Write, Transform, TransformMatchingTex, ReplacementTransform, FadeIn, FadeOut, Create, Succession]
scene_type: [Scene, MovingCameraScene]
manim_version: manim_community
complexity: intermediate
lines: 169
scene_classes: [expandPart, Plot, MaclaurinSine, MovingFrameBox, MatchingEquationParts, solvingEquation]
---

## Summary

A collection of calculus and algebra scenes covering polynomial expansion, data plotting with polynomial fit, Maclaurin series approximation of sine with camera zoom, product rule derivation with moving frame box, and step-by-step equation transformation using TransformMatchingTex. The Maclaurin scene is the standout — it uses MovingCameraScene with frame scaling to show series convergence at multiple zoom levels.

## Design Decisions

- **TransformMatchingTex for equation steps**: Morphs matching LaTeX substrings between equations, so shared terms stay in place while new terms grow in. This is far more readable than replacing the entire equation each step.
- **MovingCameraScene for Maclaurin**: The series approximation diverges wildly at the edges. Camera starts zoomed in (scale 0.6) to show local accuracy, then zooms out (scale 3x) during animation to reveal the full behavior. Without camera movement, either the detail or the big picture would be lost.
- **Succession of Transforms for series**: 20 Maclaurin terms animate as a Succession of Transforms on the same previous_graph object. Each term replaces the previous approximation, showing progressive convergence.
- **SurroundingRectangle as focus indicator**: The moving frame box highlights which term is being discussed in the product rule. ReplacementTransform between rectangles creates a smooth "focus shifts" effect.
- **Vertical stacking for equation derivation**: Each step appears below the previous, building a visual proof chain from top to bottom.

## Composition

- **Plot scene axes**: x_range=[0, pi+0.1, 1], y_range=[0, 1.1, 0.2], x_length=7, y_length=5
- **MaclaurinSine**: Camera frame scale starts at 0.6, animates to ~1.8 (0.6*3). NumberPlane as background grid. Parametric curves t_range=[-17, 17].
- **Equation positioning**: exp1 to_edge(LEFT), subsequent expressions use next_to(previous, DOWN, buff=0.2) with aligned_edge=LEFT
- **MovingFrameBox**: MathTex with 4 indexed parts. SurroundingRectangle buff=0.1

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Plot curve | ORANGE | Polynomial fit |
| MathTex | WHITE | Default |
| SurroundingRectangle | YELLOW | Default, buff=0.1 |
| Maclaurin curves | WHITE | Default parametric |
| Branding text | RED, TEAL, ORANGE, PINK | cycle for "Enstoic" letters |
| NumberPlane grid | Default | Maclaurin background |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Maclaurin term Transform | run_time=0.4 each | 20 terms in Succession |
| Camera zoom | Concurrent with Succession | self.camera.frame.animate.scale(3) |
| TransformMatchingTex | Default (~1s) | Per equation step |
| Wait between steps | 2s | Standard for readability |
| Total (MaclaurinSine) | ~12s | 20 * 0.4 + waits |
| Total (MatchingEquationParts) | ~12s | 4 transforms + waits |

## Patterns

### Pattern: Maclaurin Series with Camera Zoom

**What**: Plots successive partial sums of a Taylor/Maclaurin series as parametric curves, using Transform to morph each approximation into the next. MovingCameraScene allows simultaneous camera zoom-out to reveal convergence behavior at different scales.
**When to use**: Visualizing any series approximation (Taylor, Fourier, power series), showing convergence of iterative algorithms, or any scenario where local behavior and global behavior need to be shown simultaneously.

```python
# Source: projects/manim-scripts/scenes/calculus.py:68-91
class MaclaurinSine(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(0.6)
        def nth_series(n, x):
            terms = [(((-1)**m) * (x**(2*m+1)) / (math.factorial(2*m+1))) for m in range(n)]
            return sum(terms)
        coords = NumberPlane()
        previous_graph = coords.plot_parametric_curve(
            lambda t: np.array([t, nth_series(0, t)]), t_range=[-17, 17]
        )
        transformations = []
        for i in range(1, 20):
            new_graph = coords.plot_parametric_curve(
                lambda t: np.array([t, nth_series(i, t)]), t_range=[-17, 17]
            )
            trans = Transform(previous_graph, new_graph, run_time=0.4, rate_func=rate_functions.smooth)
            transformations.append(trans)
        self.play(Succession(*transformations, lag_ratio=1), self.camera.frame.animate.scale(3))
```

### Pattern: TransformMatchingTex for Step-by-Step Algebra

**What**: MathTex objects with matching LaTeX substrings morph smoothly between steps. Shared terms stay anchored while new terms animate in. This makes algebraic derivations visually clear — the viewer sees WHAT changed.
**When to use**: Step-by-step algebraic manipulation, equation derivation, completing the square, factoring, any symbolic math where expressions transform incrementally.

```python
# Source: projects/manim-scripts/scenes/calculus.py:113-130
eq1 = MathTex("x^2", "-", "x", "+", "1")
eq2 = MathTex("x^2", "-", r"2 \cdot \frac {1}{2} \cdot x", "+", "1")
eq3 = MathTex("x^2", "-", r"2 \cdot \frac {1}{2} \cdot x", "+", r"\frac {1}{4}", "+", r"\frac {3}{4}")
self.add(eq1)
self.wait(2)
self.play(TransformMatchingTex(eq1, eq2))
self.wait(2)
self.play(TransformMatchingTex(eq2, eq3))
```

### Pattern: Moving Frame Box for Term Highlighting

**What**: A SurroundingRectangle wraps a specific indexed part of a MathTex expression. ReplacementTransform between two rectangles creates a smooth "focus shifts" animation, directing attention to different terms.
**When to use**: Explaining multi-term formulas (product rule, chain rule, summations), highlighting specific matrix entries, or any scenario where you need to sequentially focus on parts of an expression.

```python
# Source: projects/manim-scripts/scenes/calculus.py:93-109
text = MathTex(
    "\\frac{d}{dx}f(x)g(x)=", "f(x)\\frac{d}{dx}g(x)", "+",
    "g(x)\\frac{d}{dx}f(x)"
)
self.play(Write(text))
framebox1 = SurroundingRectangle(text[1], buff=.1)
framebox2 = SurroundingRectangle(text[3], buff=.1)
self.play(Create(framebox1))
self.wait()
self.play(ReplacementTransform(framebox1, framebox2))
```

## Scene Flow

1. **expandPart** (0-5s): Writes x^2 - x + 1, transforms +1 into +1/4 + 3/4.
2. **Plot** (0-12s): Axes appear, polynomial fit curve creates, fades to 0.3 opacity.
3. **MaclaurinSine** (0-12s): Camera zoomed in. 20 Maclaurin terms animate as Succession while camera zooms out to reveal full curve behavior.
4. **MovingFrameBox** (0-6s): Product rule writes. Yellow rectangle highlights first term, then morphs to highlight second term.
5. **MatchingEquationParts** (0-12s): Four-step completing the square with TransformMatchingTex.
6. **solvingEquation** (0-12s): Full derivation with vertical stacking and branding text.

> Full file: `projects/manim-scripts/scenes/calculus.py` (169 lines)
