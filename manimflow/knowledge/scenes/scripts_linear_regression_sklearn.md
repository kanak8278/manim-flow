---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/manim-scripts/linear_regression_script.py
project: manim-scripts
domain: [machine_learning, regression, statistics]
elements: [axes, scatter_plot, dot, line, dashed_line, label, number_line]
animations: [write, draw, fade_in, flash, lagged_start]
layouts: [centered, edge_anchored]
techniques: [value_tracker, always_redraw, data_driven]
purpose: [demonstration, step_by_step, exploration]
mobjects: [Axes, Dot, DashedLine, Text, VGroup, ValueTracker]
manim_animations: [Write, Create, FadeIn, Flash, LaggedStart]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 121
scene_classes: [LinearRegressionScene]
---

## Summary

Visualizes linear regression from data to forecast using sklearn's LinearRegression. Scatter plot of 8 data points appears. A regression line starts with an initial slope (from first two points) and animates to the sklearn-fitted line via ValueTracker. Then a forecast point is shown at x=10 with dashed guide lines and a Flash highlight. The ValueTracker + always_redraw pattern makes the line fitting animation smooth and physically intuitive.

## Design Decisions

- **sklearn for actual regression**: Uses `LinearRegression().fit()` for real coefficients rather than hardcoded values. This means the visualization accurately represents the model.
- **ValueTracker for slope/intercept animation**: The regression line animates from an initial guess (slope from first two points) to the actual fitted values. This shows the "fitting" process visually, even though sklearn computes it instantly.
- **always_redraw for dynamic line**: The regression line rebuilds every frame based on current slope/intercept tracker values. This is the correct pattern for any line that depends on animated parameters.
- **Dashed guide lines for forecast**: Horizontal and vertical dashed lines from the axes to the forecast point create a visual "lookup" — trace from x-axis up to the line, then across to y-axis. Standard for showing how to read a prediction.
- **Flash on forecast point**: The Flash animation (10 lines, 0.2 radius, 1.5s) creates a "discovery" moment for the prediction.
- **Labeled sections**: "Historical Data", "Regression Line", "Forecasted Value" labels appear sequentially, building the narrative.

## Composition

- **Axes**: x_range=[0,12,2], y_range=[0,40,5], x_length=10, y_length=6. Scaled 0.8, to_edge(DOWN, buff=1).
- **Axis labels**: "Time" (x), "Contribution Amount" (y, rotated 90 degrees)
- **Data points**: 8 dots at various (x,y) positions, radius=0.08, color=BLUE
- **Forecast dot**: radius=0.1, color=RED, at x=10
- **Dashed guide lines**: color=GREY, from axes to forecast point
- **Section labels**: font_size=24, positioned next_to each other at top

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Axes | WHITE | include_numbers=True |
| Data points | BLUE | radius=0.08 |
| Regression line | YELLOW | ax.plot |
| Forecast point | RED | radius=0.1 |
| Guide lines | GREY | DashedLine |
| Flash | WHITE | line_length=0.2, 10 lines |
| Labels | WHITE | font_size=24 |
| Title | WHITE | Default |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Axes creation | Default | Create |
| Data points | lag_ratio=0.2 | LaggedStart Create |
| Line creation | Default | Create |
| Slope/intercept animation | run_time=2 | ValueTracker animate |
| Guide lines Create | Default | Simultaneous |
| Forecast dot + label | Default | Create + Write |
| Flash | run_time=1.5 | 10 lines, radius=0.2 |
| End wait | 3s | Final state |
| Total | ~18s | Setup + animation + forecast |

## Patterns

### Pattern: ValueTracker Line Fitting Animation

**What**: Two ValueTrackers (slope, intercept) drive a regression line via `always_redraw`. The line starts at an initial guess and animates to the sklearn-fitted values. The viewer sees the line "settle" into its optimal position.
**When to use**: Linear regression visualization, gradient descent animation, any optimization where parameters converge to optimal values. Also useful for showing how changing slope/intercept affects a line.

```python
# Source: projects/manim-scripts/manim-scripts/linear_regression_script.py:68-88
slope_tracker = ValueTracker(initial_slope)
intercept_tracker = ValueTracker(initial_intercept)

line_graph = always_redraw(
    lambda: ax.plot(
        lambda x: slope_tracker.get_value() * x + intercept_tracker.get_value(),
        x_range=[float(ax.x_range[0]), float(ax.x_range[1])],
        color=line_color
    )
)
self.play(Create(line_graph))
self.play(
    slope_tracker.animate.set_value(model.coef_[0]),
    intercept_tracker.animate.set_value(model.intercept_),
    run_time=2
)
```

### Pattern: Forecast Point with Dashed Guide Lines

**What**: Show a prediction by creating dashed horizontal and vertical lines from the axes to the forecast point. The dashed lines create a visual "crosshair" that shows how to read the prediction from the chart. Flash animation on the point draws attention.
**When to use**: Any prediction or forecast visualization — regression predictions, interpolation, extrapolation. Also useful for showing specific values on any chart (percentiles, thresholds).

```python
# Source: projects/manim-scripts/manim-scripts/linear_regression_script.py:96-118
forecast_dot = Dot(ax.coords_to_point(forecast_x, forecast_y), color=prediction_point_color, radius=0.1)
forecast_dot_label = Text(f"Pred: ({forecast_x}, {forecast_y:.1f})", font_size=20)
forecast_dot_label.next_to(forecast_dot, RIGHT, buff=0.2)

h_line = DashedLine(
    ax.coords_to_point(ax.x_range[0], forecast_y),
    ax.coords_to_point(forecast_x, forecast_y), color=GREY
)
v_line = DashedLine(
    ax.coords_to_point(forecast_x, ax.y_range[0]),
    ax.coords_to_point(forecast_x, forecast_y), color=GREY
)
self.play(Create(h_line), Create(v_line))
self.play(Create(forecast_dot), Write(forecast_dot_label))
self.play(Flash(forecast_dot, color=WHITE, line_length=0.2, num_lines=10, flash_radius=0.2))
```

## Scene Flow

1. **Setup** (0-4s): Title writes. Axes with labels create. "Historical Data" label.
2. **Data points** (4-6s): 8 blue dots create with LaggedStart.
3. **Regression line** (6-10s): "Regression Line" label. Line appears at initial slope, animates to fitted slope over 2s.
4. **Forecast** (10-16s): "Forecasted Value" label. Dashed guide lines create. Red forecast dot with label appears. Flash effect.
5. **End** (16-19s): Wait 3s on final state.

> Full file: `projects/manim-scripts/manim-scripts/linear_regression_script.py` (121 lines)
