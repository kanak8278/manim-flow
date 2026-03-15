---
source: https://github.com/3b1b/videos/blob/main/_2024/puzzles/max_rand.py
project: videos
domain: [probability, statistics, mathematics, calculus]
elements: [axes, function_plot, number_line, dot, arrow, label, equation, surrounding_rect, area_under_curve]
animations: [write, fade_in, fade_out, transform, animate_parameter, trace_path, zoom_out, camera_rotate]
layouts: [vertical_stack, centered, side_by_side]
techniques: [value_tracker, always_redraw, add_updater, custom_animation, three_d_camera, progressive_disclosure]
purpose: [exploration, demonstration, derivation, comparison]
mobjects: [UnitInterval, Axes, ThreeDAxes, ValueTracker, ArrowTip, Tex, Text, DecimalNumber, Vector, Square, SurroundingRectangle, DashedLine, Line, Dot, GlowDot, Randolph, VGroup]
manim_animations: [FadeIn, FadeOut, FadeTransform, TransformMatchingStrings, ShowCreation, Write, Randomize, TrackingDots, GrowArrow, Blink]
scene_type: InteractiveScene
manim_version: manimlib
complexity: intermediate
lines: 575
scene_classes: [MaxProcess, SqrtProcess, SquareAndSquareRoot, GawkAtEquivalence, VisualizeMaxOfPairCDF]
---

## Summary

Explores the surprising equivalence between max(rand(), rand()) and sqrt(rand()) through interactive probability visualizations. Custom animations Randomize (drives a ValueTracker through random values at a set frequency) and TrackingDots (leaves a fading trail of GlowDots) make random sampling viscerally visible. The proof builds through CDF analysis on a 2D unit square: the region where max(x1,x2) <= R is a square of side R, so P = R^2, matching the CDF of sqrt(uniform). Extends to 3D for max of three variables.

## Design Decisions

- **Randomize custom animation**: Drives a ValueTracker to random values at a configurable frequency. Unlike smooth interpolation, it jumps discretely, making randomness look random. A final_value parameter ensures the animation ends at a known state.
- **TrackingDots trail**: Each frame appends a GlowDot at the current position and fades all previous dots by fade_factor=0.95. This builds up a visual probability density — more dots accumulate where values are common.
- **Three stacked UnitIntervals**: x1 (BLUE), x2 (YELLOW), max (GREEN) arranged vertically with connecting lines. The max interval auto-updates via updater on its tracker. A DashedLine connects the winning input to the max output.
- **2D unit square for CDF proof**: Axes(0,1)x(0,1) with x1 on horizontal, x2 on vertical. A GREEN inner square shows the region where max <= R. Scaling this square demonstrates P(max <= R) = R^2.
- **Color semantics**: BLUE = x1, YELLOW = x2, GREEN = max/result, TEAL = sqrt operation. Consistent across all scenes.
- **Randy's confusion**: Randolph reacts to the equivalence max(rand(),rand()) <=> sqrt(rand()), making the surprise explicit.

## Composition

- **MaxProcess layout**:
  - Three UnitIntervals, width=3, arranged DOWN buff=2.5, shifted 2*LEFT
  - Labels with Tex and make_number_changeable to RIGHT, buff=0.5
  - SurroundingRectangle around top two intervals, WHITE stroke width=2, GREY_E fill
  - Arrow: Vector(1.5*DOWN, thickness=5) below rectangle
- **CDF visualization**:
  - Axes (0,1,0.1)x(0,1,0.1), width=6, height=6
  - Big square: GREY_E fill, GREY_D stroke width=1
  - Inner square: GREEN fill opacity=0.35, stroke=0
  - Max lines: GREEN stroke width=3
- **3D extension**: ThreeDAxes (0,1)^3. Camera ambient rotation -1 DEG.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| x1 variable | BLUE | Tip, tracking dots, labels |
| x2 variable | YELLOW | Tip, tracking dots, labels |
| max result | GREEN | Tip, tracking dots, inner square |
| sqrt result | TEAL | In sqrt variant |
| Unit square background | GREY_E | fill=1, stroke GREY_D width=1 |
| Max region fill | GREEN | opacity=0.35 |
| Max boundary lines | GREEN | stroke_width=3 |
| "Not helpful" | RED | Annotation text |
| Connecting lines | GREY | DashedLine, stroke_width=2, opacity=0.5 |
| Arrow tips | matched color | ArrowTip at 90 deg, height=0.15 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Randomize sampling | run_time=30 | frequency=4, continuous sampling |
| TrackingDots | run_time=30 | Concurrent with Randomize |
| CDF square scaling | run_time=3 | there_and_back rate_func |
| Move tracker to boundary | run_time=3 | Per axis |
| Total MaxProcess | ~35s | Long ambient sampling |
| 3D camera rotation | -1 DEG continuous | Ambient |

## Patterns

### Pattern: Randomize Animation for ValueTracker

**What**: A custom Animation that sets a ValueTracker to random values at a configurable frequency (jumps per second). Uses a running tally to determine when to update, ensuring consistent visual frequency regardless of frame rate. A final_value parameter controls where the animation lands.

**When to use**: Random sampling visualization, Monte Carlo demonstrations, any animation where you need a ValueTracker to jump through random values at a steady rate.

```python
# Source: projects/videos/_2024/puzzles/max_rand.py:4-29
class Randomize(Animation):
    def __init__(self, value_tracker, frequency=8, rand_func=random.random,
                 final_value=None, **kwargs):
        self.frequency = frequency
        self.final_value = final_value if final_value is not None else rand_func()
        self.running_tally = 0
        super().__init__(value_tracker, **kwargs)

    def interpolate_mobject(self, alpha):
        if not self.new_step(alpha):
            return
        value = self.rand_func() if alpha < 1 else self.final_value
        self.value_tracker.set_value(value)

    def new_step(self, alpha):
        d_alpha = alpha - self.last_alpha
        self.last_alpha = alpha
        self.running_tally += self.frequency * d_alpha * self.run_time
        if self.running_tally > 1:
            self.running_tally %= 1
            return True
        return False
```

### Pattern: TrackingDots Trailing GlowDot Path

**What**: An Animation that tracks a point_func each frame, appending a new GlowDot and fading all previous dots by fade_factor. Over time, this builds a visual density estimate — areas visited more often have brighter clusters. The remover=True flag cleans up after the animation ends.

**When to use**: Probability density estimation, random walk traces, Monte Carlo path visualization, any moving point where you want to show visit frequency.

```python
# Source: projects/videos/_2024/puzzles/max_rand.py:32-47
class TrackingDots(Animation):
    def __init__(self, point_func, fade_factor=0.95, radius=0.25,
                 color=YELLOW, **kwargs):
        self.point_func = point_func
        self.dots = GlowDot(point_func(), color=color, radius=radius)
        kwargs.update(remover=True)
        super().__init__(self.dots, **kwargs)

    def interpolate_mobject(self, alpha):
        opacities = self.dots.get_opacities()
        point = self.point_func()
        if not np.isclose(self.dots.get_end(), point).all():
            self.dots.add_point(point)
            opacities = np.hstack([opacities, [1]])
        opacities *= self.fade_factor
        self.dots.set_opacity(opacities)
```

### Pattern: Random Variable Label Group

**What**: A factory function that creates a ValueTracker + ArrowTip + label bundle for a random variable on a number line. The tip auto-positions on the axis via updater. Used for both input variables and derived quantities like max or sqrt.

**When to use**: Any number line with a moving indicator — random variables, sliders, parameter displays, value annotations on axes.

```python
# Source: projects/videos/_2024/puzzles/max_rand.py:50-66
def get_random_var_label_group(axis, label_name, color=GREY,
                                initial_value=None, font_size=36, direction=None):
    tracker = ValueTracker(initial_value or random.uniform(*axis.x_range[:2]))
    tip = ArrowTip(angle=90 * DEGREES)
    tip.set_height(0.15).set_fill(color)
    if direction is None:
        direction = np.round(rotate_vector(UP, -axis.get_angle()), 1)
    tip.add_updater(lambda m: m.move_to(axis.n2p(tracker.get_value()), direction))
    label = Tex(label_name, font_size=font_size).set_color(color)
    label.set_backstroke(BLACK, 5)
    label.always.next_to(tip, -direction, buff=0.1)
    return Group(tracker, tip, label)
```

### Pattern: CDF Proof via 2D Region

**What**: On a unit square Axes, show that P(max(x1,x2) <= R) equals the area of a square of side R. An inner square with GREEN fill and boundary lines visually represents the CDF. Scaling the square demonstrates the R^2 relationship.

**When to use**: CDF derivation for order statistics, geometric probability proofs, any argument where probability equals an area in a multi-variable space.

```python
# Source: projects/videos/_2024/puzzles/max_rand.py:347-448
# Max boundary lines at (R, R)
max_lines = VGroup(
    Line(axes.c2p(0.7, 0.7), axes.c2p(0.7, 0)),
    Line(axes.c2p(0.7, 0.7), axes.c2p(0, 0.7)),
)
max_lines.set_stroke(GREEN, 3)

# Inner square = P(max <= R)
inner_square = Square()
inner_square.set_fill(GREEN, 0.35).set_stroke(GREEN, 0)
inner_square.replace(max_lines)

# Animate scaling to show R^2 relationship
self.play(
    VGroup(inner_square, max_lines).animate.scale(0.5, about_edge=DL)
        .set_anim_args(rate_func=there_and_back),
    run_time=3
)
```

## Scene Flow

1. **Max process** (0-35s): Three UnitIntervals. x1 and x2 randomize for 30 seconds. max updates via updater. TrackingDots show distributions building up. max(rand,rand) clusters toward 1.
2. **Sqrt process** (35-65s): Two UnitIntervals. x randomizes, sqrt(x) follows. TrackingDots show identical distribution to max.
3. **Gawk at equivalence** (65-75s): Side-by-side text comparison. Randy is confused.
4. **CDF proof** (75-180s): Unit square. x1 on x-axis, x2 on y-axis. Random dots fill square. Green region shows max <= R. Area = R^2. Compare to P(sqrt(x) <= R) = P(x <= R^2) = R^2. QED.
5. **3D extension** (180s+): ThreeDAxes cube for max of three variables. Camera rotates to show the cube region.
