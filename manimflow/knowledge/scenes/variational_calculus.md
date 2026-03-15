---
source: https://github.com/vivek3141/videos/blob/main/variational.py
project: vivek3141_videos
domain: [mathematics, calculus, physics, mechanics]
elements: [axes, parametric_curve, function_plot, equation, label, arrow, dot, dashed_line, surrounding_rect]
animations: [write, transform, fade_in, animate_parameter, indicate]
layouts: [centered, side_by_side, dual_panel]
techniques: [value_tracker, add_updater, progressive_disclosure]
purpose: [derivation, step_by_step, definition, comparison]
mobjects: [Axes, ParametricFunction, FunctionGraph, TexMobject, TextMobject, VGroup, Circle, Arrow, Line, DashedLine, BackgroundRectangle, ScreenRectangle, ImageMobject]
manim_animations: [Write, Transform, TransformFromCopy, FadeInFromDown, Uncreate, ApplyMethod, Indicate]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 563
scene_classes: [EQScene, Intro, Functional, Difference, DistanceFunc, Brac, IntroToProblem, Proof, EulerLagrange, DistanceFunc2, Wolfram]
---

## Summary

Introduces variational calculus by visualizing the problem of finding the shortest path between two points. A parametric curve between fixed points A and B is animated by varying a parameter alpha via ValueTracker, causing the curve to oscillate while the endpoints stay fixed. The Euler-Lagrange equation is derived step by step. Key visual: a rotated parametric function (theta=PI/4) with oscillating perturbation, showing how the path length functional D(f) depends on the curve shape. Compares traditional calculus (R -> R) with variational calculus (f(x) -> R) using a side-by-side diagram.

## Design Decisions

- **Rotated parametric curve**: The curve between A and B is a rotated cosine: f_r(theta, alpha) returns (t*cos(theta) - f(t,alpha)*sin(theta), t*sin(theta) + f(t,alpha)*cos(theta)). Rotation by PI/4 makes the endpoints sit on a diagonal, which looks more natural than horizontal endpoints.
- **ValueTracker for curve perturbation**: Alpha parameter oscillates via `tracker.increment_value, 8, rate_func=linear`. The updater recreates the ParametricFunction each frame. This shows the "family of curves" concept central to variational calculus.
- **Side-by-side traditional vs variational**: Left panel shows f: R -> R with arrows. Right panel shows functional: f(x) -> R. Direct visual comparison of the two paradigms.
- **Euler-Lagrange as multi-step reveal**: The equation is constructed from colored partial derivatives and assembled piece by piece with highlights for F (YELLOW), y (GREEN), x (BLUE).
- **BackgroundRectangle for emphasis**: The integrand to minimize gets a GOLD-bordered BackgroundRectangle with "Minimize this" text below. This focuses attention on the key expression.

## Composition

- **Stationary points intro**: Axes x=[-2,4], y=[-2,4], function f(x)=x*sin(cos(x))+2, graph shifted to 3*LEFT
- **Functional diagram**: Axes x=[-3,3], y=[-2,2], parametric curve, points at +/-sqrt(2) on diagonal
- **Comparison layout**: Side-by-side at 3.5*LEFT and 3.5*RIGHT, separated by vertical Line(6*UP, 6*DOWN) and horizontal Line(10*LEFT, 10*RIGHT) at 2*UP
- **Proof curves**: Three parametric curves (alpha=1, 0.6, 0.2) in TEAL/RED, centered at 2.5*RIGHT + 2.5*UP, scaled 1.5x
- **Euler-Lagrange equation**: scale=1.25, assembled from separate Tex objects with color maps

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Function f(x) | YELLOW | FunctionGraph label |
| Variable D (functional) | BLUE | tex_to_color_map |
| Variable f (curve) | RED | tex_to_color_map |
| Variable x | GREEN or BLUE | Context-dependent |
| Points A, B | YELLOW | Circle(radius=0.05, fill_opacity=1) |
| Stationary points | BLUE | Horizontal lines at tangent |
| Dashed reference lines | WHITE | stroke_opacity=0.7, dash_length=0.1 |
| Optimal curve q(x) | RED | ParametricFunction |
| Perturbed curves | TEAL | q(x) + s*delta_q(x) |
| ds element | GREEN | tex_to_color_map |
| Boundary values | YELLOW | x_1, x_2 in tex_to_color_map |
| F (integrand) | PURPLE or YELLOW | Euler-Lagrange equation |
| Minimize box | GOLD | BackgroundRectangle, fill_opacity=0 |
| Minimize text | ORANGE | "Minimize this" |
| Wolfram result box | RED | Rectangle around key expression |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Curve oscillation | run_time=4*DEFAULT | tracker increments by 8, linear |
| Path sweep (DistanceFunc) | run_time=4*DEFAULT | tracker increments by 1+3*PI, linear |
| Equation transforms | ~1s each | Standard |
| Indicate | ~1s | Pulse highlight |
| Total | ~3 minutes | 11 scenes |

## Patterns

### Pattern: Oscillating Parametric Curve via ValueTracker

**What**: A parametric curve between two fixed points with a cosine perturbation whose amplitude is driven by a ValueTracker. The curve is recreated each frame via add_updater + become(). The rotation theta=PI/4 places endpoints on a diagonal. Alpha controls the perturbation amplitude via sin(tracker.get_value()).

**When to use**: Variational calculus demonstrations, showing families of curves with fixed endpoints, geodesic visualization, any "which path minimizes..." problem. Also applicable to mode shape animations in vibration analysis.

```python
# Source: projects/vivek3141_videos/variational.py:115-144
tracker = ValueTracker(-1)

func = ParametricFunction(
    self.f_r(theta=PI/4), color=RED, t_min=-2, t_max=2)
func.add_updater(lambda x: x.become(
    ParametricFunction(
        self.f_r(theta=PI/4, alpha=np.sin(tracker.get_value())),
        color=RED, t_min=-2, t_max=2)
).shift(0.5 * DOWN))

p1 = Circle(radius=0.05, fill_opacity=1, color=YELLOW)
p1.shift([-np.sqrt(2), -np.sqrt(2) - 0.5, 0])
p2 = Circle(radius=0.05, fill_opacity=1, color=YELLOW)
p2.shift([np.sqrt(2), np.sqrt(2) - 0.5, 0])

self.play(tracker.increment_value, 8,
          rate_func=linear, run_time=4*DEFAULT_ANIMATION_RUN_TIME)

def f(self, x, alpha=0):
    return alpha * np.cos(PI/4 * x)

def f_r(self, theta=PI/4, alpha=0):
    return lambda t: [
        t * np.cos(theta) - self.f(t, alpha=alpha) * np.sin(theta),
        t * np.sin(theta) + self.f(t, alpha=alpha) * np.cos(theta), 0]
```

### Pattern: BackgroundRectangle as Emphasis Box

**What**: A BackgroundRectangle with `fill_opacity=0, stroke_opacity=1, stroke_width=DEFAULT_STROKE_WIDTH` wraps a key expression. Combined with a text label below, this draws attention to the critical part of a complex equation. Used here to highlight the integrand that must be minimized.

**When to use**: Highlighting key results in derivations, marking the "important part" of a long equation, drawing attention to terms that will be manipulated next, boxing final answers.

```python
# Source: projects/vivek3141_videos/variational.py:300-308
rect = BackgroundRectangle(
    eq3[1:], stroke_width=DEFAULT_STROKE_WIDTH,
    stroke_opacity=1, color=GOLD, fill_opacity=0, buff=0.1)
self.play(Write(rect))

txt = TextMobject("Minimize this", color=ORANGE)
txt.next_to(rect, DOWN)
self.play(Write(txt))
```

### Pattern: Comparison Layout for Two Paradigms

**What**: Split screen with vertical and horizontal dividing lines. Left panel shows one concept (traditional calculus: f maps R -> R), right panel shows the other (variational calculus: functional maps f(x) -> R). Each side has its own diagram with colored arrows showing input/output types.

**When to use**: Comparing two mathematical frameworks, showing old vs new approach, Riemann vs Lebesgue, Lagrangian vs Hamiltonian, any paired concept presentation.

```python
# Source: projects/vivek3141_videos/variational.py:173-217
t1 = TextMobject("Traditional Calculus", color=GOLD)
t2 = TextMobject("Variational Calculus", color=PURPLE)
t1.shift(3.5 * LEFT + 3 * UP).scale(1.25)
t2.shift(3.5 * RIGHT + 3 * UP).scale(1.25)

l1 = Line(6 * UP, 6 * DOWN)  # Vertical divider
l2 = Line(10 * LEFT, 10 * RIGHT).shift(2 * UP)  # Horizontal divider

# Left: f: R -> R
f1 = TexMobject("f", color=RED)
i1 = TexMobject(r"\mathbb{R}", color=YELLOW).shift(1.5 * LEFT)
o1 = TexMobject(r"\mathbb{R}", color=YELLOW).shift(1.5 * RIGHT)
eq1 = VGroup(f1, i1, o1, Arrow(...), Arrow(...))
eq1.shift(3.5 * LEFT).scale(1.5)

# Right: functional: f(x) -> R
i2 = TexMobject(r"f(x)", color=BLUE).shift(1.5 * LEFT)
o2 = TexMobject(r"\mathbb{R}", color=YELLOW).shift(1.5 * RIGHT)
```

## Scene Flow

1. **Intro** (0-15s): Function f(x) with stationary points. DashedLines to extrema. "f'(x)=0" boxed. "sign of f''(x)" boxed.
2. **Functional** (15-35s): D(f) functional introduced. Curve between A, B oscillates via ValueTracker. "Distance from A to B along f" with arrow.
3. **Difference** (35-45s): Side-by-side: Traditional Calculus (R -> R) vs Variational Calculus (f(x) -> R).
4. **DistanceFunc** (45-65s): Arc length formula D(y) = integral sqrt(1 + y'^2) dx. BackgroundRectangle highlights integrand. "Minimize this" label.
5. **IntroToProblem** (65-75s): General variational problem statement: find f making I[f] = integral F(x, f, f') dx stationary.
6. **Proof** (75-85s): Three curves (optimal in RED, perturbed in TEAL) between fixed points with DashedLine reference.
7. **EulerLagrange** (85-95s): Euler-Lagrange equation assembled with colored partial derivatives.
8. **DistanceFunc2 + Wolfram** (95-110s): Apply Euler-Lagrange to distance functional. Wolfram Alpha screenshot. Result: f''(x) = 0, so f(x) = c_0 + c_1*x (straight line).

> Full file: `projects/vivek3141_videos/variational.py` (563 lines)
