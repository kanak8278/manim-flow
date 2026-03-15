---
source: https://github.com/vivek3141/videos/blob/main/lebesgue.py
project: vivek3141_videos
domain: [mathematics, calculus, probability, statistics]
elements: [axes, function_plot, riemann_rectangles, area_under_curve, equation, label, arrow]
animations: [write, transform, draw, fade_in]
layouts: [centered, dual_panel, vertical_stack]
techniques: [color_gradient, progressive_disclosure, value_tracker, add_updater]
purpose: [comparison, step_by_step, derivation, definition]
mobjects: [Axes, FunctionGraph, ParametricFunction, Rectangle, VGroup, TexMobject, TextMobject, BulletedList, Polygon, ThreeDAxes, Prism, ImageMobject, BackgroundRectangle, Brace, Arrow]
manim_animations: [Write, ShowCreation, Transform, DrawBorderThenFill, FadeInFromDown, Uncreate, ApplyMethod]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 597
scene_classes: [IntroQuote, FTC, Problems, HigherDim, PieceWise, IRFunc, IRGraph, IRExp, Integ2, LebesguePart, HenriLebesgue, LebesgueIntegral, IRLebesgue, LebesgueEq, Electric, ExpectedProb, Expected, Thumbnail]
---

## Summary

Compares Riemann and Lebesgue integration through progressive visual techniques. Riemann integration is shown via vertical rectangles that refine (dx from 0.2 to 0.05), while Lebesgue integration uses horizontal rectangles that slice by function value (y-ranges from 0 to 2.4). A key scene demonstrates the Dirichlet function (1 for irrationals, 0 for rationals) which Riemann cannot integrate but Lebesgue can. Uses 3D Prism blocks for higher-dimensional Riemann sums and a ValueTracker-driven rectangle for the piecewise function animation.

## Design Decisions

- **Vertical vs horizontal rectangles**: Riemann rectangles partition the x-axis (vertical slices), Lebesgue rectangles partition the y-axis (horizontal slices). This is the core visual distinction and is shown by literally rotating the slicing direction.
- **Refinement animation via Transform**: Riemann rectangles at decreasing dx (0.2, 0.15, 0.1, 0.05) are pre-computed and shown via Transform, so the viewer sees the approximation improve.
- **Lebesgue rectangles with color gradient**: Horizontal rectangles colored BLUE->GREEN gradient from bottom to top. Each rectangle's width is computed from the inverse function, creating the characteristic "stacked horizontal bars" look.
- **Dirichlet function as counterexample**: The 1_irrational function is shown to have well-defined Lebesgue integral (=1) via measure theory, while Riemann integration fails. This motivates why Lebesgue integration exists.
- **Piecewise function with ValueTracker**: A rectangle whose height animates via ValueTracker demonstrates that Riemann sums can handle simple functions but struggle with discontinuities.
- **3D Riemann cubes**: Higher-dimensional integration shown via Prism blocks at grid points, demonstrating that the concept extends but becomes more complex.

## Composition

- **Riemann GraphScene**: x_max=4, y_max=2, function `0.1*(x-2)^2 + 1`, rectangles from x=0 to x=3
- **Lebesgue rectangles**: Axes x_min=0, x_max=5, y_min=0, y_max=3, function `-0.9*(x-2.5)^2 + 2.5`, y-range [0, 2.4], centered and scaled 2x
- **3D cubes**: ThreeDAxes [-5,5]x[-5,5]x[-3.5,3.5], Prism blocks at 0.5-unit spacing for sin(x)+cos(y)
- **Probability curve**: Gaussian e^(-t^2), axes x=[-3,3], y=[0,2], scaled 2x, shifted 2*DOWN
- **Lebesgue measure diagram**: Split-screen with arrows from function set to A_0 (rational) and A_1 (irrational)

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Riemann rectangles | Default gradient | DrawBorderThenFill, stroke_width=4*dx |
| Lebesgue rectangles | BLUE->GREEN gradient | color_gradient, fill_opacity=1 |
| Piecewise colors | BLUE->GREEN gradient | 3 colors for 3 segments |
| Function curve | WHITE | stroke_width=2 |
| Measure mu | GOLD | tex_to_color_map |
| Set A_i | BLUE | tex_to_color_map |
| Simple function f_n | BLUE | tex_to_color_map |
| Probability shading | BLUE->PURPLE gradient | fill_opacity=1, stroke_width=0 |
| Electric current | RED | FunctionGraph |
| Result highlight | YELLOW | BackgroundRectangle stroke |
| Henri Lebesgue quote | YELLOW | Author attribution |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| DrawBorderThenFill (Riemann) | run_time=2, lag_ratio=0.5 | Rectangles appear sequentially |
| Transform (refinement) | run_time=2, lag_ratio=0.5 | Each dx step |
| Lebesgue refinement | ~1s each Transform | 4 refinement steps |
| ValueTracker (piecewise) | run_time=3, there_and_back | Rectangle height animation |
| 3D ambient rotation | 30s | begin_ambient_camera_rotation(rate=0.08) |
| Total video | ~4-5 minutes | 18 scenes |

## Patterns

### Pattern: Lebesgue Horizontal Rectangles

**What**: Generates horizontal rectangles that partition the y-axis (function range) instead of the x-axis. For a function f(x) = -0.9*(x-2.5)^2 + 2.5, each rectangle's width is 2*|x - 2.5| where x is the inverse of the y-value. Rectangles are colored with a BLUE->GREEN gradient. Refinement is shown by decreasing dy from 0.5 to 0.1.

**When to use**: Lebesgue integration visualization, measure theory concepts, any comparison between "slicing by x" vs "slicing by y" approaches. Also useful for showing level sets of a function.

```python
# Source: projects/vivek3141_videos/lebesgue.py:354-365
def get_lebesgue_rectangles(self, dx=0.2, y=(0, 2.4)):
    rects = VGroup()
    y_range = np.arange(y[0], y[1], dx)
    colors = color_gradient([BLUE, GREEN], len(y_range))
    for color, y in zip(colors, y_range):
        x = abs(2.5 - ((((y + dx) - 2.5)/(-0.9))**(1/2) + 2.5))
        rect = Rectangle(
            height=dx, width=2*x, stroke_color=BLACK,
            fill_color=color, stroke_opacity=1, fill_opacity=1,
            stroke_width=2*dx)
        rect.shift([2.5, y+dx/2, 0])
        rects.add(rect)
    return rects
```

### Pattern: Riemann Refinement Animation

**What**: Pre-compute Riemann rectangles at multiple dx values (0.2, 0.15, 0.1, 0.05). Show the first set with DrawBorderThenFill, then Transform to each finer set. The stroke_width scales with dx (4*dx) to keep visual weight proportional. Uses GraphScene's built-in `get_riemann_rectangles()`.

**When to use**: Any Riemann sum visualization, numerical integration convergence, showing how approximation improves with finer partitions.

```python
# Source: projects/vivek3141_videos/lebesgue.py:43-74
rects = VGroup()
for dx in np.arange(0.2, 0.05, -0.05):
    rect = self.get_riemann_rectangles(
        self.graph, x_min=0, x_max=self.default_right_x,
        dx=dx, stroke_width=4*dx)
    rects.add(rect)

self.play(DrawBorderThenFill(rects[0], run_time=2,
          rate_func=smooth, lag_ratio=0.5))
for rect in rects[1:]:
    self.play(Transform(rects[0], rect, run_time=2,
              rate_func=smooth, lag_ratio=0.5))
```

### Pattern: ValueTracker Rectangle Height Animation

**What**: A Rectangle whose height is driven by a ValueTracker. The updater rebuilds the rectangle each frame with the new height, maintaining its bottom edge position by computing the vertical shift. Uses `there_and_back` rate_func so the animation returns to start.

**When to use**: Animating bar heights in bar charts, showing function value changes, adjustable rectangles in integration diagrams, any dynamic resize of a rectangular element.

```python
# Source: projects/vivek3141_videos/lebesgue.py:165-181
h = ValueTracker(1.9)

def update(rect):
    r = Rectangle(height=h.get_value(), width=1,
                  stroke_opacity=1, fill_opacity=1,
                  stroke_color=BLACK, fill_color=colors[-1])
    r.next_to(r1[-1], RIGHT).shift(
        0.25 * LEFT + (h.get_value() - 1.9)/2 * UP)
    rect.become(r)

r.add_updater(update)
self.play(h.increment_value, 2,
          rate_func=there_and_back, run_time=3)
```

### Pattern: Measure Theory Set Decomposition Diagram

**What**: Shows a function's domain decomposed into level sets (A_0 for rationals, A_1 for irrationals) using branching arrows. The Lebesgue integral is then the sum of value * measure(set). This visual explains the Lebesgue approach: group by output value, multiply by measure of preimage.

**When to use**: Measure theory, probability (expected value as integral), any function decomposition by level sets, explaining Lebesgue vs Riemann conceptually.

```python
# Source: projects/vivek3141_videos/lebesgue.py:368-405
eq1 = TexMobject("f(x), x \in [0, 1]").scale(1.5).shift(3.25 * UP)
arr1 = Arrow(2.75 * UP, 2 * UP + 4 * LEFT, color=YELLOW)
arr2 = Arrow(2.75 * UP, 2 * UP + 4 * RIGHT, color=YELLOW)

a0 = TexMobject("A_0", color=BLUE).scale(1.5).shift(1.25 * UP + 4 * LEFT)
a1 = TexMobject("A_1", color=BLUE).scale(1.5).shift(1.25 * UP + 4 * RIGHT)

eq2 = TextMobject(r"\(f(x) = 0 \) \\ \(x\) is rational")
eq3 = TextMobject(r"\( f(x) = 1 \) \\ \(x\) is irrational")

integ = TexMobject(
    r"\int_0^1 f(x) \mathrm{d}\mu = 0 \cdot \mu (A_0) + 1 \cdot \mu (A_1)",
    tex_to_color_map={r"A_0": BLUE, r"A_1": BLUE, r"\mu": GOLD})
integ.shift(2 * DOWN).scale(1.5)
```

## Scene Flow

1. **IntroQuote** (0-8s): Henri Lebesgue quote about paying bills in order (Riemann) vs sorting by denomination (Lebesgue).
2. **FTC** (8-25s): Riemann rectangles refine from dx=0.2 to dx=0.05 on a parabola. "Riemann Integration" title.
3. **Problems** (25-35s): BulletedList: "Higher Dimensions", "Continuity". Fade to highlight each.
4. **HigherDim** (35-50s): 3D grid of Prism blocks for sin(x)+cos(y). Ambient rotation 30s.
5. **PieceWise** (50-60s): Piecewise function with animated rectangle height via ValueTracker.
6. **IRFunc/IRGraph** (60-75s): Dirichlet function definition. Riemann rectangles on f=1.
7. **LebesgueIntegral** (75-90s): Horizontal Lebesgue rectangles on parabola with refinement.
8. **IRLebesgue** (90-105s): Set decomposition A_0, A_1. Integral = 0*mu(A_0) + 1*mu(A_1) = 1.
9. **ExpectedProb** (105-115s): Gaussian curve with color gradient Riemann sums. E[x] = integral P(x)dx.

> Full file: `projects/vivek3141_videos/lebesgue.py` (597 lines)
