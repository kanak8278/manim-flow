---
source: https://github.com/3b1b/videos/blob/main/_2022/borwein/main.py
project: 3blue1brown
domain: [calculus, signal_processing, number_theory, mathematics]
elements: [axes, function_plot, area_under_curve, equation, formula, riemann_rectangles, label, number_line]
animations: [write, transform, replacement_transform, fade_in, fade_out, flash, draw, highlight, zoom_in, move]
layouts: [centered, vertical_stack, side_by_side]
techniques: [value_tracker, always_redraw, moving_camera, helper_function, progressive_disclosure, scipy_integration]
purpose: [demonstration, derivation, step_by_step, exploration]
mobjects: [Axes, VMobject, OldTex, OldTexText, DecimalNumber, VGroup, Line, Arc, Circle, Rectangle, GlowDot, Dot]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, FadeTransform, TransformMatchingTex, FlashAround, ReplacementTransform, TransformFromCopy, GrowArrow, UpdateFromAlphaFunc]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 1841
scene_classes: [ShowIntegrals, SineLimit, WriteFullIntegrals, WriteMoreFullIntegrals, WriteOutIntegrals, WriteOutIntegralsWithPi, InsertTwoCos, WriteTwoCosPattern, MovingAverages, ShowReciprocalSums, MoreGeneralFact, WaysToCombineFunctions, ReplaceXWithPiX, FourierProblemSolvingSchematic, WhatWeNeedToShow, ConvolutionTheoremDiagram, MultiplyBigNumbers]
---

## Summary

Explores the Borwein integrals, a famous sequence of sinc function products that equal pi until they suddenly don't. Visualizes the sinc function, its progressive products, Riemann integral areas, moving average convolutions, and the connection to Fourier analysis. Uses dual-axes layouts (upper graph + lower stretched sinc) to build the surprising pattern interactively, with color-coded sinc terms and animated area computations.

## Design Decisions

- **Color-coded sinc terms by denominator**: Each `sin(x/k)/x/k` term gets a distinct color (BLUE, TEAL, GREEN_B, GREEN_C through YELLOW to RED_B), making it visually trackable as the product grows.
- **Riemann rectangles instead of filled area**: Uses `get_riemann_rectangles` with very small dx (0.01*PI) for precise area visualization, with positive areas in BLUE_D and negative in RED.
- **Dual-axes layout for comparison**: Upper axes show the growing product integral, lower axes show the individual sinc(x/k) being multiplied in, revealing how each term stretches the function.
- **Progressive disclosure of integrals**: Each new integral is animated as a TransformMatchingTex from the previous one, so the viewer sees exactly what changed.
- **Moving window visualization for convolutions**: The MovingAverages scene uses a colored rectangle sliding across the top graph to show how convolution physically works as a windowed average.
- **Plateau shrinkage as key visual**: Yellow lines mark the flat-top plateau of each convolution result, with braces showing its width, making the eventual loss of the plateau viscerally clear.

## Composition

- **ShowIntegrals axes**: `x_range=(-10*PI, 10*PI, PI)`, `y_range=(-0.5, 1, 0.5)`, width=1.3*FRAME_WIDTH, height=3.5
- **Dual layout**: Upper axes shifted above midpoint (1.5*DOWN), lower axes height=2.5, placed below midpoint with MED_LARGE_BUFF
- **Integral label**: `.to_corner(UL)`, scales down progressively (0.9 at n=4, 0.8 at n=5, 0.7 for n>5)
- **MovingAverages**: Graphs arranged vertically, upper and lower axes, with window rectangle width = `x_axis.unit_size / k`
- **Camera frame**: Expands to height=10 for dual-axes layout

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| sin(x)/x graph | BLUE | stroke_width=3 |
| sin(x/3)/(x/3) | TEAL | Color-coded in tex |
| sin(x/5)/(x/5) | GREEN_B | Color-coded in tex |
| sin(x/7)/(x/7) | GREEN_C | Progressively shifts toward yellow |
| sin(x/15)/(x/15) | RED_B | The term that breaks the pattern |
| Positive area | BLUE_D | Riemann rectangles, fill_opacity=0.5 |
| Negative area | RED | Riemann rectangles |
| Moving avg window | GREEN | fill_opacity=0.35, stroke_width=0 |
| Plateau line | YELLOW | stroke_width=3 |
| 1/x envelope | YELLOW | stroke_width=2 |
| GlowDots | default | Used for convergence demos |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Graph creation (ShowCreation) | 3s | `run_time=3` for initial sinc |
| Area write | 4s | `lag_ratio=0.01` for Riemann rects |
| FlashAround rhs | 2s | Emphasizes = pi result |
| TransformMatchingTex | default | Between successive integrals |
| Moving average pass | 3s | `rate_func=linear` |
| Total video | ~3-5 min | Multiple scenes |

## Patterns

### Pattern: Color-Coded Multi-Term Integral Builder

**What**: Builds a growing LaTeX integral expression where each new sinc term is color-mapped by its denominator, using `set_color_by_tex` to automatically color-code matched substrings.

**When to use**: Any mathematical expression where terms accumulate and you need the viewer to track which term is new. Product formulas, summation series, polynomial term additions.

```python
# Source: projects/videos/_2022/borwein/main.py:30-53
def get_multi_sinc_integral(ks=[1], dots_at=None, rhs="", insertion=""):
    result = OldTex(
        R"\int_{-\infty}^\infty", insertion,
        *(get_sinc_tex(k) if k != dots_at else R"\dots" for k in ks),
        "dx", rhs,
    )
    t2c = {
        R"\sin": BLUE, "x / 3": TEAL, "x / 5": GREEN_B,
        "x / 7": GREEN_C, "x / 15": RED_B,
    }
    for tex, color in t2c.items():
        result.set_color_by_tex(tex, color)
    return result
```

### Pattern: Dual-Axes Progressive Comparison

**What**: Creates two vertically stacked axes where the upper shows a cumulative result and the lower shows the next factor being multiplied in. The lower graph animates a stretch transformation to show how sinc(x/k) is a horizontally scaled version of sinc(x).

**When to use**: Showing how a function changes when multiplied/convolved with a sequence of factors. Fourier series partial sums, filter cascades, iterative approximation sequences.

```python
# Source: projects/videos/_2022/borwein/main.py:180-205
midpoint = 1.5 * DOWN
top_group = VGroup(axes, graph, area)
top_group.generate_target().next_to(midpoint, UP)
low_axes = self.get_axes(height=2.5)
low_axes.next_to(midpoint, DOWN, buff=MED_LARGE_BUFF)

low_sinc = low_axes.get_graph(sinc).set_stroke(BLUE, 2)
low_graph = low_axes.get_graph(lambda x: sinc(x / 3)).set_stroke(WHITE, 2)

self.play(TransformFromCopy(graph, low_sinc))
self.play(low_sinc.animate.stretch(3, 0).match_style(low_graph), run_time=2)
```

### Pattern: Moving Average Window Convolution Visualization

**What**: Animates a colored rectangle sliding across a function graph to show convolution as a moving windowed average. The window width = 1/k of the x-axis unit, and the resulting averaged function appears on a separate axes below.

**When to use**: Convolution explanations, signal processing demonstrations, moving average filters, kernel-based image processing concepts.

```python
# Source: projects/videos/_2022/borwein/main.py:884-899
window = Rectangle(
    width=top_axes.x_axis.unit_size / k,
    height=top_axes.y_axis.unit_size * 1.5,
)
window.set_stroke(width=0)
window.set_fill(self.window_color, self.window_opacity)
window.move_to(top_axes.c2p(-rs, 0), DOWN)
```

### Pattern: Riemann Rectangle Area with Signed Colors

**What**: Creates Riemann rectangles where positive values use one color and negative values use another, with stroke_width=0 and sorted by distance from origin for a clean radial write animation.

**When to use**: Integral visualizations where positive and negative contributions matter, signed area demonstrations, showing how cancellation works in oscillating integrals.

```python
# Source: projects/videos/_2022/borwein/main.py:295-304
def get_area(self, axes, graph, dx=0.01 * PI, fill_opacity=0.5):
    rects = axes.get_riemann_rectangles(
        graph, dx=dx,
        colors=(BLUE_D, BLUE_D),
        negative_color=RED,
    )
    rects.set_fill(opacity=fill_opacity)
    rects.set_stroke(width=0)
    rects.sort(lambda p: abs(p[0]))
    return rects
```

## Scene Flow

1. **ShowIntegrals** (0-60s): Sinc function drawn symmetrically. Sinc label and 1/x envelope shown. Limit at 0 demonstrated with converging GlowDots. Area colored with Riemann rectangles. RHS = pi revealed with flash.
2. **Dual axes** (60-90s): Screen splits, lower axes shows sinc(x/3) as stretched sinc. TransformFromCopy + horizontal stretch animation.
3. **Integral sequence** (90-180s): Progressive integrals from n=2 to n=8, each TransformMatchingTex'd. All equal pi until n=8 where result is pi - 4.62e-11. Lower graph updates each time.
4. **MovingAverages** (separate scene): Rect function shown, then convolved iteratively with scaled rect functions. Window slides across. Plateau width decreases. At n=8, plateau vanishes and f(0) drops below 1.
5. **WriteFullIntegrals**: All integrals displayed vertically with camera scrolling, building dramatic tension before the pattern breaks.
