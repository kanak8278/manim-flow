---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/normal.py
project: manim-animations
domain: [probability, statistics, mathematics]
elements: [axes, function_plot, riemann_rectangles, label, equation]
animations: [write, draw, fade_in, animate_parameter, update_value]
layouts: [centered, edge_anchored]
techniques: [value_tracker, always_redraw, add_updater, helper_function]
purpose: [exploration, demonstration, distribution]
mobjects: [Axes, ValueTracker, MathTex, Text, VGroup, Line]
manim_animations: [Write, Create, FadeIn]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 115
scene_classes: [NormalDistribution]
---

## Summary

Visualizes a normal (Gaussian) distribution with interactive parameter exploration. The bell curve, Riemann rectangles (shaded area for 1-sigma), and percentage annotations (68%, 95%, 99.7%) all update dynamically via ValueTracker + always_redraw as the mean and standard deviation are animated. The mean slides from 0 to 3 and back, then sigma increases from 1 to 3, demonstrating how parameters reshape the distribution. Custom helper methods compute the PDF and build bracket-style percentage annotations.

## Design Decisions

- **ValueTracker for mean and std**: Both parameters are ValueTrackers so the entire visualization — curve, rectangles, annotations, info text — redraws automatically when either changes. This allows smooth continuous animation without rebuilding objects.
- **always_redraw for curve, rectangles, and annotations**: Every dynamic element uses always_redraw. The curve recomputes the PDF, Riemann rectangles recompute the shaded region, and annotations reposition their brackets. This is the cleanest approach for multiple interdependent dynamic elements.
- **Riemann rectangles for 1-sigma area**: Yellow rectangles fill the area between mu-sigma and mu+sigma. This visually communicates "68% of the data falls within one standard deviation" more concretely than just drawing the area.
- **Three percentage annotations (68%, 95%, 99.7%)**: The 68-95-99.7 rule is the most important property of the normal distribution. Showing all three simultaneously with bracket-style annotations stacked below the curve makes the rule visually memorable.
- **Bracket-style annotations with lines and text**: The `get_percentage_annotation()` helper returns a VGroup of left_line + text + right_line. Lines extend from the text to the axis positions. This creates a clean bracket that visually spans the interval. The pattern is reusable for any interval annotation.
- **Animate mean first, then std**: Moving the mean shows the curve sliding left/right without changing shape. Then changing std shows the curve widening/narrowing. This isolates each parameter's effect — a pedagogically sound approach.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Normal Distribution"
  - Axes: `next_to(title, DOWN, buff=0.3)`, x_length=8, y_length=4
  - Info text: `next_to(axes, LEFT, buff=0.5)` — "mu = ... sigma = ..."
  - Annotations: stacked below the x-axis, shifted DOWN*0.7 from axes
- **Axes configuration**: x_range=[-10, 10, 1], y_range=[0, 0.5, 0.1], x_length=8, y_length=4, tips=False, include_numbers=True, font_size=28
- **Axis labels**: "x" and "P(x)", font_size=28
- **Riemann rectangles**: dx=0.25, stroke_width=0.5, fill_opacity=0.6
- **Annotation stacking**: 68% at DOWN*0.7, 95% next_to(68%, DOWN, buff=0.2), 99.7% next_to(95%, DOWN, buff=0.2)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Bell curve | BLUE | always_redraw plot |
| Riemann rectangles | YELLOW | fill_opacity=0.6, stroke_width=0.5 |
| Axes | WHITE | include_numbers=True, font_size=28 |
| Info text | WHITE | MathTex, font_size=28 |
| Annotation text | WHITE | font_size=20 |
| Annotation lines | WHITE | stroke_width=2 |

Color strategy: Minimal — BLUE for the distribution curve (the star of the show), YELLOW for the shaded area (draws attention to the probability mass). Everything else WHITE. The simplicity keeps focus on the dynamic parameter changes.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| Axes + labels Create/Write | ~1s | + 1s wait |
| Info text Write | ~1s | + 1s wait |
| Curve Create | run_time=2 | + 1s wait |
| Rectangles + annotations | ~1s | Create + three FadeIns simultaneously, + 2s wait |
| Mean to 3 | run_time=2 | + 1s wait |
| Mean back to 0 | run_time=2 | + 1s wait |
| Std to 2 | run_time=2 | + 1s wait |
| Std to 3 | run_time=2 | + 1s wait |
| Total video | ~22 seconds | |

## Patterns

### Pattern: ValueTracker-Driven Distribution Exploration

**What**: Use ValueTrackers for distribution parameters (mean, std) and always_redraw for the curve. When the tracker animates, the curve, shaded area, and annotations all update in real-time. This creates a "slider" effect where the viewer sees how parameters affect the shape.
**When to use**: Any parameterized distribution visualization — normal, Poisson, exponential, chi-squared. Also works for any function with tunable parameters — activation functions with temperature, loss functions with regularization weight.

```python
# Source: projects/manim-animations/src/normal.py:7-36
mean_tracker = ValueTracker(0)
std_tracker = ValueTracker(1)

curve = always_redraw(
    lambda: axes.plot(
        lambda x: self.normal_pdf(x, mean_tracker.get_value(), std_tracker.get_value()),
        x_range=[-10, 10],
        color=BLUE,
    )
)

riemann_rectangles = always_redraw(
    lambda: axes.get_riemann_rectangles(
        graph=curve,
        x_range=[
            mean_tracker.get_value() - std_tracker.get_value(),
            mean_tracker.get_value() + std_tracker.get_value(),
        ],
        dx=0.25,
        stroke_width=0.5,
        fill_opacity=0.6,
        color=YELLOW,
    )
)
```

### Pattern: Bracket-Style Percentage Annotation

**What**: A reusable helper method that creates a horizontal bracket annotation: left_line + centered text + right_line. The lines extend from the text edges to axis positions (mean - std, mean + std). The VGroup repositions automatically via always_redraw. Useful for showing "this percentage of data falls in this range."
**When to use**: Normal distribution 68-95-99.7 rule, confidence intervals, any interval annotation on a number line or axis. Works for showing ranges in box plots, tolerance bands, or percentile markers.

```python
# Source: projects/manim-animations/src/normal.py:101-115
def get_percentage_annotation(self, axes, mean, std, percentage):
    start_x = mean - std
    end_x = mean + std

    text = Text(percentage, font_size=20)
    text.move_to(axes.c2p(mean, 0))

    left_line = Line(
        axes.c2p(start_x, 0), text.get_left() + LEFT*0.05, color=WHITE, stroke_width=2
    )
    right_line = Line(
        text.get_right() + RIGHT*0.05, axes.c2p(end_x, 0), color=WHITE, stroke_width=2
    )

    return VGroup(left_line, text, right_line)
```

### Pattern: Self-Updating Parameter Display with add_updater

**What**: A MathTex that shows current parameter values (mu and sigma), rebuilt every frame via add_updater + become(). The new text is repositioned next_to a reference element to stay anchored. This keeps the displayed values in sync with the ValueTrackers.
**When to use**: Live parameter displays, updating labels, any text that must reflect changing numeric values — training metrics, slider values, simulation counters.

```python
# Source: projects/manim-animations/src/normal.py:23-28
info = (
    MathTex(f"\mu = {mean_tracker.get_value():.1f} \ \sigma = {std_tracker.get_value():.1f}", font_size=28)
    .next_to(axes, LEFT, buff=0.5)
    .add_updater(lambda m: m.become(MathTex(f"\mu = {mean_tracker.get_value():.1f} \ \sigma = {std_tracker.get_value():.1f}", font_size=28)
    .next_to(axes, LEFT, buff=0.5)))
)
```

## Scene Flow

1. **Setup** (0-4s): Title "Normal Distribution" writes. Axes with numbers create. "mu = 0.0 sigma = 1.0" info text writes.
2. **Initial curve** (4-7s): Blue bell curve creates (2s).
3. **Annotations** (7-10s): Yellow Riemann rectangles for 1-sigma region create. Three percentage annotations (68%, 95%, 99.7%) fade in simultaneously below the x-axis.
4. **Mean exploration** (10-15s): Mean animates from 0 to 3 (curve slides right, annotations follow). Mean returns to 0.
5. **Std exploration** (15-22s): Std animates from 1 to 2 (curve widens, rectangles widen). Std continues to 3 (even wider). All annotations stretch to match.

> Full file: `projects/manim-animations/src/normal.py` (115 lines)
