---
source: https://github.com/3b1b/videos/blob/main/_2022/convolutions/discrete.py
project: 3blue1brown
domain: [probability, signal_processing, statistics, combinatorics, mathematics]
elements: [axes, function_plot, bar_chart, histogram, grid, label, equation, formula, dot, line, surrounding_rect, number_line]
animations: [write, fade_in, fade_out, transform, replacement_transform, transform_from_copy, highlight, color_change, stagger, lagged_start, move, draw, animate_parameter]
layouts: [centered, side_by_side, vertical_stack, horizontal_row]
techniques: [value_tracker, always_redraw, helper_function, data_driven, progressive_disclosure, scipy_integration]
purpose: [demonstration, step_by_step, derivation, exploration, distribution, comparison]
mobjects: [Axes, VMobject, VGroup, Square, Rectangle, OldTex, OldTexText, Text, DecimalNumber, Line, GlowDot, DieFace, SurroundingRectangle, Arrow, Vector]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, LaggedStartMap, LaggedStart, TransformMatchingShapes, TransformFromCopy, CountInFrom, VFadeIn, VFadeInThenOut, MoveToTarget, Rotate, FlashAround, MoveAlongPath, UpdateFromAlphaFunc, UpdateFromFunc]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 2808
scene_classes: [WaysToCombine, DiceExample, SimpleExample, MovingAverageExample, MovingAverageFast, AltMovingAverage, AltMovingAverageFast, MovingAverageFast2, CompareSizes, ImageConvolution, BoxBlurMario, BoxBlurCat, GaussianBluMario, GaussianBlurCat, GaussianBlurCatNoPause, SobelFilter1, SobelFilter2, SobelFilterCat, SobelFilterKirby, SharpenFilter]
---

## Summary

Explores discrete convolutions through three lenses: combining functions (addition, multiplication, convolution), probability via dice sums, and image processing kernels. Uses die face mobjects for probability, bar chart distributions for sums, sliding window animations for moving averages, and pixel grid convolution for image blur/sharpen/edge detection. The DiceExample scene is particularly rich, showing how the convolution of two uniform distributions produces a triangular distribution for dice sums.

## Design Decisions

- **Three-column comparison**: Functions, sequences, and operations displayed side-by-side with a vertical dividing line, making the parallel structure between continuous and discrete convolution explicit.
- **DieFace custom mobjects**: Blue and red dice with white dots create an immediately recognizable probability context. Colors distinguish the two dice being summed.
- **6x6 grid for all outcomes**: All 36 die combinations displayed in a grid with mini dice pairs, making the sample space concrete before showing diagonal groupings.
- **Sliding row alignment for convolution**: One row of dice reverses and slides across the other, with SurroundingRectangles highlighting aligned pairs for each sum value. This is the core visual metaphor for discrete convolution.
- **Bar chart distribution from computed values**: `dist_to_bars` helper creates Rectangle bars with heights proportional to distribution values, colored by gradient (BLUE_D to GREEN_D).
- **Image convolution with actual images**: BoxBlur, Gaussian, Sobel, and Sharpen kernels applied to real images (Mario, cat) showing practical signal processing.

## Composition

- **WaysToCombine**: Vertical line dividing screen. Left: sequences (font_size=48). Right: 3 axes stacked (width=FRAME_WIDTH*0.5 - 1, height=2.0).
- **DiceExample**: Die faces arranged horizontally, buff=MED_LARGE_BUFF. Grid: 6x6 squares, height=6, to_edge(LEFT, buff=2.0), shifted 0.5*DOWN. Mini dice at 0.6*square width.
- **Bar charts**: Rectangle width=0.5, total height=2.0, colors BLUE_D to GREEN_D, centered.
- **Image kernels**: Pixel grids at various resolutions, kernels displayed as labeled grids.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Blue dice | BLUE_E | fill with white dots |
| Red dice | RED_E | fill with white dots |
| f(x) graph | BLUE | stroke_width=2 |
| g(x) graph | YELLOW | stroke_width=2 |
| Combined result | TEAL | stroke_width=2 |
| Sequence a | BLUE | tex_to_color_map |
| Sequence b | YELLOW | tex_to_color_map |
| Distribution bars | BLUE_D to GREEN_D | gradient, fill_opacity=1 |
| Bar dividing lines | GREY_C | stroke_width=1, opacity=0.75 |
| Pair rects | default | SurroundingRectangle, corner_radius=0.1 |
| Diagonal highlight | TEAL | For matching sum lines |
| Operation labels | TEAL | "Addition", "Multiplication", "Convolution" |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Die face intro | 2s | LaggedStart, rate_func=overshoot |
| Grid write | 2s | stroke_color=YELLOW, stroke_width=4 |
| Mini dice placement | 2s | LaggedStartMap MoveToTarget, lag_ratio=0.02 |
| CountInFrom | 2s | 36 combinations |
| Diagonal highlight per sum | varies | FadeIn/FadeOut per n value |
| Dice row slide | per sum value | animate shift |
| Graph ShowCreation | 4s | rate_func=linear with GlowDot tracking |
| Total video | ~20 min | Many scenes |

## Patterns

### Pattern: Dice Probability Distribution via Grid Diagonals

**What**: Creates a 6x6 grid of mini dice pairs, then iterates through sum values (2-12), highlighting diagonals where dice pairs sum to the target. Each diagonal gets a probability label showing count/36. The grid makes the combinatorial structure visible.

**When to use**: Probability distributions from combining discrete random variables, sum distributions, any combinatorial enumeration where a 2D grid reveals the pattern.

```python
# Source: projects/videos/_2022/convolutions/discrete.py:415-445
for n in range(2, 13):
    to_highlight = VGroup()
    for die in mini_dice:
        if die.sum == n:
            to_highlight.add(die)
    pairs = VGroup(*(VGroup(m1, m2) for m1, m2 in zip(to_highlight[::2], to_highlight[1::2])))
    prob_label = self.get_p_sum_expr(n, Rf"\frac{{{len(pairs)}}}{{36}}")
    self.play(
        to_highlight.animate.set_opacity(1),
        to_fade.animate.set_opacity(0.2),
    )
```

### Pattern: Sliding Row Convolution Visualization

**What**: Reverses one row of dice, then slides it across the other row. For each alignment, SurroundingRectangles highlight which pairs line up, physically demonstrating convolution as the sum of aligned products.

**When to use**: Discrete convolution demonstrations, cross-correlation, any sliding-window operation on sequences. The reversal step is crucial for distinguishing convolution from correlation.

```python
# Source: projects/videos/_2022/convolutions/discrete.py:459-481
self.play(Rotate(red_dice, PI))  # Reverse one row
for n in range(2, 13):
    pairs = self.get_aligned_pairs(blue_dice, red_dice, n)
    self.play(self.get_dice_shift(blue_dice, red_dice, n))
    rects = get_pair_rects(pairs)
    self.play(LaggedStartMap(ShowCreation, rects, lag_ratio=0.2))
```

### Pattern: Distribution Bars from Data Array

**What**: Converts a probability distribution array into a VGroup of Rectangle bars with heights proportional to values, colored by a gradient. Each bar stores its index for later alignment operations. Labels can be added above bars.

**When to use**: Histogram displays, probability mass functions, frequency distributions, any discrete data that needs bar-chart representation.

```python
# Source: projects/videos/_2022/convolutions/discrete.py:50-60
def dist_to_bars(dist, bar_width=0.5, height=2.0, bar_colors=(BLUE_D, GREEN_D)):
    bars = Rectangle(width=bar_width).get_grid(1, len(dist), buff=0)
    bars.set_color_by_gradient(*bar_colors)
    bars.set_fill(opacity=1)
    bars.set_stroke(WHITE, 1)
    for bar, value, index in zip(bars, dist, it.count()):
        bar.set_height(value, stretch=True, about_edge=DOWN)
        bar.index = index
    bars.set_height(height, stretch=True)
    return bars
```

### Pattern: Lagrange Polynomial Interpolation

**What**: Computes the Lagrange interpolating polynomial from a set of data points, returning a callable function. Used to create smooth curves through discrete distribution values.

**When to use**: Fitting smooth curves through discrete data points, polynomial interpolation demonstrations, connecting discrete bar charts to continuous distributions.

```python
# Source: projects/videos/_2022/convolutions/discrete.py:90-101
def get_lagrange_polynomial(data):
    def poly(x):
        return sum(
            y0 * prod((x - x1) for x1, y1 in data if x1 != x0)
            / prod((x0 - x1) for x1, y1 in data if x1 != x0)
            for x0, y0 in data
        )
    return poly
```

## Scene Flow

1. **WaysToCombine** (0-90s): Left panel shows sequences a, b. Right panel shows function graphs f, g. Three operations compared: addition (pointwise), multiplication (pointwise), convolution (sliding sum of products). Mystery box with question marks revealed as convolution.
2. **DiceExample** (90-300s): Blue and red dice introduced. 6x6 grid shows all 36 outcomes. Diagonals highlighted for each sum (2-12) with probability fractions. Grid fades. One row reversed and slid across the other to show convolution. Implicit uniform 1/6 probabilities shown, then generalized to non-uniform.
3. **SimpleExample** (300-360s): Simpler discrete convolution example with smaller sequences.
4. **MovingAverageExample** (360-420s): Continuous version of convolution as sliding window average.
5. **ImageConvolution** (420-540s): Pixel grids with kernels. Box blur, Gaussian blur, Sobel edge detection, and sharpening filters demonstrated on real images.
