---
source: https://github.com/3b1b/videos/blob/main/_2023/convolutions2/continuous.py
project: videos
domain: [probability, statistics, calculus, signal_processing, mathematics]
elements: [axes, function_plot, area_under_curve, riemann_rectangles, dot, label, equation, number_line, line, arrow]
animations: [write, fade_in, fade_out, transform, replacement_transform, transform_from_copy, animate_parameter, lagged_start, trace_path, indicate]
layouts: [side_by_side, vertical_stack, centered, grid]
techniques: [value_tracker, always_redraw, add_updater, data_driven, progressive_disclosure, custom_animation, helper_function]
purpose: [derivation, demonstration, step_by_step, comparison, exploration]
mobjects: [Axes, VGroup, VMobject, GlowDot, DecimalNumber, Tex, TexText, Text, Cross, SurroundingRectangle, Line, Arrow, FullScreenFadeRectangle, Randolph, ImageMobject]
manim_animations: [FadeIn, FadeOut, FadeTransform, TransformMatchingTex, TransformMatchingStrings, ShowCreation, Write, ShowSubmobjectsOneByOne, VFadeIn, Blink]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 2332
scene_classes: [TransitionToContinuousProbability, CompareFormulas, RepeatedSamplesFromContinuousDistributions, SampleTwoNormals, AddTwoGammaDistributions, SampleWedgePlusDoubleLump, Convolutions, ProbConvolutions, ConvolveTwoUniforms, MovingAverageAsConvolution, RepeatedConvolution, RectConvolutionFacts]
---

## Summary

Visualizes continuous convolutions as the sum of two independent random variables, transitioning from discrete (dice) to continuous probability distributions. Features a reusable RepeatedSamplesFromContinuousDistributions base class that animates random sampling from two distributions with GlowDots, live decimal labels, and vertical graph lines. The convolution itself is shown as a sliding inner product: one function is reflected and slid across the other, with the area of overlap plotted as the output. Repeated self-convolution demonstrates convergence to a Gaussian (central limit theorem).

## Design Decisions

- **Discrete to continuous transition**: Starts with dice bar charts (Riemann rectangles), then ShowSubmobjectsOneByOne through progressively finer rectangles until they become a smooth curve. The probability -> density relabeling happens mid-scene.
- **Three-axes layout for X, Y, X+Y**: Left axes stacked vertically for the two input distributions, right axes for their sum. This makes the additive relationship physically visible — sample X, sample Y, add them, see where X+Y lands.
- **GlowDot sampling with TrackingDots-style fade**: Each sample places a GlowDot on each axis, then fades to small radius and low opacity. Over many samples, the distribution emerges as a density of dots.
- **Sliding convolution animation**: For the integral visualization, g(s-x) slides across f(x). The overlapping area (product of the two functions) is filled and its integral plotted in real time on a third axes. This is the most intuitive explanation of the convolution integral.
- **Discrete-continuous formula comparison**: Left half shows discrete P_X * P_Y with sum, right half shows continuous f * g with integral. TransformMatchingTex morphs one into the other.
- **Repeated convolution -> CLT**: Self-convolving a distribution multiple times. After 5-10 convolutions, any reasonable starting distribution approaches a Gaussian, visualizing the central limit theorem.

## Composition

- **Sampling layout**:
  - Left two Axes: width=5.5, height=2, x_range (-5,5), y_range (0, 0.5, 0.25). Arranged DOWN buff=1.5, to_edge LEFT.
  - Right Axes: same but centered to_edge RIGHT.
  - X axis numbers font_size=16, y axis stroke_opacity=0.5.
  - Labels: "X", "Y", "X + Y" at corner UR of each axes.
- **Formula comparison**:
  - Screen split by vertical Line. "Discrete case" and "Continuous case" titles with Underline.
  - Discrete diagram from image. Continuous: three Axes with wedge, double_lump, and convolution graphs.
- **Convolution sliding**:
  - Two Axes with function graphs. One function reflected and animated sliding via ValueTracker s.
  - Product area filled below min(f, g_reflected). Output graph builds on third axes.
- **Probability transition**: Axes (0,12)x(0,1,0.2), width=14, height=5. to_edge LEFT LARGE_BUFF, DOWN buff=1.25.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Function f | BLUE | Graph stroke_width=2 |
| Function g | RED | Graph stroke_width=2 |
| Convolution f*g | TEAL | Graph stroke_width=2 |
| X distribution | BLUE | In t2c and graph |
| Y distribution | YELLOW/RED | In t2c and graph |
| X+Y distribution | TEAL | In t2c and graph |
| Riemann rectangles | default | Decreasing stroke from 3 to 0 |
| Probability label | default | "Probability" then crossed out in RED |
| Density label | default | "Probability density" |
| Sub-area | TEAL | fill_opacity via tracker |
| v_lines | GREY_A | stroke_width=1 |
| Sample dots | GlowDot | Color matched to distribution |
| Short name "pdf" | default | TransformMatchingStrings from long name |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Discrete -> continuous bars | run_time=5 | ShowSubmobjectsOneByOne with bezier curve |
| X value sweep | run_time=6 | ValueTracker 0 to 12 |
| Range tracking | run_time=2-3 per | Animate range_tracker pairs |
| Formula comparison | run_time=2 | TransformMatchingTex with path_arc |
| Single sample cycle | ~2s | time_between=0.25, fade=1.0 |
| Repeated sampling | 30+ cycles | Automated loop |
| GlowDot fade | run_time=0.25 | Radius shrink + opacity reduction |
| Sliding convolution | continuous | ValueTracker s drives reflection position |

## Patterns

### Pattern: Discrete-to-Continuous Distribution Transition

**What**: Start with coarse Riemann rectangles (bars) under a curve. Generate progressively finer rectangles and display them one at a time via ShowSubmobjectsOneByOne. The final set has stroke_width=0, appearing as a solid area. Then overlay the continuous curve with ShowCreation.

**When to use**: Transitioning from discrete to continuous probability, Riemann sum -> integral visualization, histogram -> density curve, any discrete-to-smooth limit.

```python
# Source: projects/videos/_2023/convolutions2/continuous.py:70-92
all_rects = VGroup(*(
    axes.get_riemann_rectangles(
        graph, x_range=(0, min(6 + n, 12)), dx=(1/n),
        input_sample_type="right",
    ).set_stroke(WHITE, width=(2.0/n), opacity=(2.0/n), behind=False)
    for n in (*range(1, 10), *range(10, 20, 2), *range(20, 100, 5))
))
area = all_rects[-1]
area.set_stroke(width=0)

self.play(
    ShowSubmobjectsOneByOne(all_rects,
        rate_func=bezier([0, 0, 0, 0, 1, 1])),
    run_time=5
)
self.remove(all_rects)
self.add(area, graph)
self.play(ShowCreation(graph))
```

### Pattern: Repeated Random Sampling with GlowDot Accumulation

**What**: A base class RepeatedSamplesFromContinuousDistributions handles the sampling loop. Each iteration: draw random values for X and Y, place GlowDots on respective axes, show vertical graph lines, display decimal labels with the sum, then fade dots to small/transparent. Over many iterations, the dot density approximates the PDF.

**When to use**: Monte Carlo visualization, demonstrating the distribution of a statistic, showing how the sum of random variables builds up a new distribution, any repeated-trial visualization.

```python
# Source: projects/videos/_2023/convolutions2/continuous.py:430-500
def animate_samples(self, plots, time_between_samples=0.25, **kwargs):
    xy_samples = np.round(self.get_samples(), 2)
    sample_sum = sum(xy_samples)
    samples = [*xy_samples[:2], sample_sum]
    dots = Group()
    for sample, plot in zip(samples, plots):
        axes, graph, sym_label = plot
        dot = GlowDot(axes.c2p(sample, 0))
        line = axes.get_v_line_to_graph(sample, graph, line_func=Line)
        line.set_stroke(YELLOW, 2)
        dots.add(dot)
    # Show and fade
    self.play(LaggedStart(*(
        dot.animate.set_radius(0.1).set_opacity(self.dot_fade_factor)
        for dot in dots
    ), run_time=0.25))
```

### Pattern: Convolution as Sliding Reflected Function

**What**: For computing [f*g](s), reflect g to get g(-x), then shift by s to get g(s-x). A ValueTracker for s slides the reflected function across f. The product f(x)*g(s-x) is filled as an area. The integral of this area is plotted on a separate axes as the convolution output.

**When to use**: Convolution integral visualization, cross-correlation, matched filtering, any "slide and multiply" operation.

```python
# Source: projects/videos/_2023/convolutions2/continuous.py:20-32
def get_conv_graph(axes, f, g, dx=0.1):
    x_samples = np.arange(x_min, x_max + dx, dx)
    f_samples = np.array([f(x) for x in x_samples])
    g_samples = np.array([g(x) for x in x_samples])
    full_conv = np.convolve(f_samples, g_samples)
    x0 = len(x_samples) // 2 - 1
    conv_samples = full_conv[x0:x0 + len(x_samples)]
    conv_graph = VMobject()
    conv_graph.set_stroke(TEAL, 2)
    conv_graph.set_points_smoothly(axes.c2p(x_samples, conv_samples * dx))
    return conv_graph
```

### Pattern: Dynamic Probability Region with always_redraw

**What**: A range_tracker ValueTracker holds [a, b]. An always_redraw function generates the area under the PDF between a and b, with fill opacity controlled by a separate tracker. Vertical lines at a and b update via updater. Moving the range smoothly reshapes the highlighted area.

**When to use**: Interactive probability region visualization, P(a < X < b) demonstrations, confidence intervals, any "area under curve between bounds" display.

```python
# Source: projects/videos/_2023/convolutions2/continuous.py:154-204
range_tracker = ValueTracker([0, 12])
sub_area_opacity_tracker = ValueTracker(0)

def get_subarea():
    result = axes.get_area_under_graph(graph, range_tracker.get_value())
    result.set_fill(TEAL, sub_area_opacity_tracker.get_value())
    return result

sub_area = always_redraw(get_subarea)

v_lines = Line(DOWN, UP).replicate(2)
v_lines.set_stroke(GREY_A, 1).set_height(FRAME_HEIGHT)
v_lines.add_updater(lambda m: [
    line.move_to(axes.c2p(val, 0), DOWN)
    for val, line in zip(range_tracker.get_value(), m)
])

# Animate range changes
for pair in [(5, 6), (1, 3), (2.5, 3), (4, 7)]:
    self.play(range_tracker.animate.set_value(pair), run_time=2)
```

## Scene Flow

1. **Discrete -> continuous** (0-30s): Dice bars on axes. Progressively finer Riemann rectangles. Smooth curve emerges. "Probability" crossed out, replaced with "Probability density."
2. **PDF interpretation** (30-60s): Shaded sub-area between a and b. v_lines at bounds. P(a<x<b) = integral formula. Range slides around.
3. **Formula comparison** (60-80s): Split screen. Discrete sum on left, continuous integral on right. TransformMatchingTex morphs one into the other. Randy confused, then pondering.
4. **Repeated sampling** (80-150s): X and Y distributions with GlowDot sampling. Dots accumulate to show sum distribution. Sum label with live arithmetic.
5. **Sliding convolution** (150-250s): f in BLUE, g(s-x) in RED sliding across. Product area in TEAL. Output builds on third axes.
6. **Moving average** (250-300s): Rectangular function convolved = moving average. Shows smoothing effect.
7. **Repeated convolution -> Gaussian** (300-360s): Self-convolving a distribution multiple times. Shape converges to normal curve. CLT demonstrated visually.
