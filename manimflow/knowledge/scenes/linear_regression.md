---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/linreg.py
project: manim-animations
domain: [machine_learning, statistics, regression, optimization]
elements: [scatter_plot, axes, function_plot, dashed_line, label, dot]
animations: [update_value, animate_parameter, grow_from_center, stagger, write, fade_in]
layouts: [centered, edge_anchored]
techniques: [value_tracker, always_redraw, add_updater, algorithm_class_separation, history_replay, lambda_capture_i]
purpose: [progression, demonstration, step_by_step]
mobjects: [Axes, Dot, DashedLine, Text, VGroup]
manim_animations: [Write, Create, GrowFromCenter, GrowFromPoint, AnimationGroup]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 112
scene_classes: [LinearRegressionAnimation]
---

## Summary

Visualizes linear regression training via gradient descent. A scatter plot of 8 data points appears, then a regression line starts flat and animates through 40 training epochs. Dashed lines from each point to the line show prediction errors shrinking in real-time. Weight and bias values update live. The key technique is ValueTracker + always_redraw — the line and error lines recompute every frame as parameters change.

## Design Decisions

- **Algorithm class separate from scene class**: The LinearRegression class runs gradient descent to completion first, storing the full history of (weight, bias) pairs. Then the scene replays that history as animation. This separation means the algorithm logic is clean, testable, and reusable — the visualization just iterates over recorded states.
- **ValueTracker for parameters, not manual repositioning**: Instead of creating a new line object each epoch, we use ValueTrackers for weight and bias. The line is `always_redraw` — it recomputes from tracker values every frame. This gives smooth interpolation between epochs instead of discrete jumps.
- **DashedLine for errors, not solid**: Dashed lines visually communicate "measurement" or "distance" — a convention from statistics diagrams. Solid lines would compete visually with the regression line itself.
- **Staggered dot entrance**: Data points appear one-by-one with GrowFromCenter and lag_ratio=0.1, not all at once. This draws attention to the data itself before the algorithm starts, and creates a natural build-up.
- **Fast epoch animation (0.1s each)**: 40 epochs at 0.1s = 4 seconds of training animation. Fast enough to feel like "training is happening" without boring the viewer. The smooth ValueTracker interpolation makes it feel continuous.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Linear Regression"
  - Parameter text: `next_to(title_text, DOWN, buff=0.2)` — "Weight: 0.00 Bias: 0.00"
  - Axes: centered, x_length=7, y_length=5
  - Data points: positioned via `axes.coords_to_point(x, y)`
  - Regression line: full width of axes, redrawn every frame
  - Error lines: vertical DashedLine from each point to the line
- **Axes configuration**: x_range=[0, 7, 1], y_range=[0, 20, 2], include_numbers=True
- **Data**: 8 points, X in [0.5, 6.0], y = 2.5x + 2 + noise

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Data points | BLUE | Dot mobject, default radius |
| Regression line | RED | Plotted via axes.plot() |
| Error lines | RED | DashedLine, stroke_width=1.5 |
| Title text | WHITE | Default |
| Parameter text | WHITE | font_size=24 |
| Axes | WHITE | include_numbers=True |
| Axis labels | WHITE | "x" and "y" |

The color scheme is minimal: BLUE for data (input), RED for model (output/prediction). This two-color system keeps the visual clean and lets the viewer immediately distinguish "what we have" (blue) from "what the model thinks" (red).

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | Default + 1s wait |
| Axes Create | ~1s | Default + 1s wait |
| Parameter text Write | ~1s | + 1s wait |
| Data points entrance | ~1.5s | GrowFromCenter, lag_ratio=0.1 |
| Initial line appear | ~1s | GrowFromPoint from origin |
| Error lines appear | ~1s | GrowFromPoint from each dot |
| Training (40 epochs) | ~4s | 0.1s per epoch |
| Final hold | 1s | |
| Total video | ~12 seconds | |

## Patterns

### Pattern: Algorithm + Scene Separation

**What**: Keep the algorithm logic in a pure Python class with a history list. Run it to completion first, then the scene replays the history as animation. This cleanly separates "what happens" from "how it looks."
**When to use**: Any ML training visualization, algorithm simulation, or iterative process. Run the algorithm, record states, then animate the recorded states.

```python
# Source: projects/manim-animations/src/linreg.py:4-34
class LinearRegression:
    def __init__(self):
        self.weight = 0.0
        self.bias = 0.0
        self.history = []

    def predict(self, X):
        return self.weight * X + self.bias

    def fit(self, X, y, learning_rate=0.01, epochs=100):
        n = len(X)
        for _ in range(epochs):
            y_pred = self.predict(X)
            d_weight = (-2 / n) * np.sum(X * (y - y_pred))
            d_bias = (-2 / n) * np.sum(y - y_pred)
            self.weight -= learning_rate * d_weight
            self.bias -= learning_rate * d_bias
            self.history.append((self.weight, self.bias))

# In scene: run first, then animate
model = LinearRegression()
model.fit(X, y, learning_rate=0.01, epochs=40)
```

### Pattern: ValueTracker + always_redraw for Dynamic Line

**What**: A function plot that recomputes automatically when ValueTracker parameters change. The line is never manually updated — always_redraw rebuilds it from scratch every frame using the current tracker values. This gives smooth interpolation between discrete parameter updates.
**When to use**: Any visualization where a curve, line, or shape should respond to changing parameters — regression lines, distribution curves, optimization landscapes, function exploration.

```python
# Source: projects/manim-animations/src/linreg.py:44-67
weight_tracker = ValueTracker(0.)
bias_tracker = ValueTracker(0.)

# Line redraws every frame based on current tracker values
line = always_redraw(lambda: axes.plot(
    lambda x: weight_tracker.get_value() * x + bias_tracker.get_value(),
    color=RED
))

# Animate parameter changes — line follows automatically
for epoch, (weight, bias) in enumerate(model.history):
    self.play(
        weight_tracker.animate.set_value(weight),
        bias_tracker.animate.set_value(bias),
        run_time=0.1,
    )
```

### Pattern: Dynamic Error Lines (always_redraw DashedLine)

**What**: Dashed lines from each data point to the regression line, showing prediction residuals. Each line is always_redraw so it updates in real-time as the regression line moves. The critical detail is `lambda i=i:` which captures the loop variable by value — without this, all lambdas would reference the last value of i.
**When to use**: Residual visualization, error measurement, distance display, or any "gap" between two things that changes over time.

```python
# Source: projects/manim-animations/src/linreg.py:69-76
dashed_lines = VGroup(*[
    always_redraw(lambda i=i: DashedLine(
        start=axes.coords_to_point(X[i], y[i]),
        end=axes.coords_to_point(X[i], weight_tracker.get_value() * X[i] + bias_tracker.get_value()),
        color=RED,
        stroke_width=1.5,
    )) for i in range(len(X))
])
```

**Critical**: `lambda i=i:` captures the loop variable by value. Without this, all 8 lambdas would use i=7 (the last value) and all error lines would point to the same data point.

### Pattern: Self-Updating Text Display

**What**: Text that rebuilds itself every frame to show current parameter values. Uses add_updater with t.become() to replace the entire Text object. The new Text is repositioned with next_to() to stay anchored to the title.
**When to use**: Live counters, parameter displays, score trackers, any numeric value that changes during animation.

```python
# Source: projects/manim-animations/src/linreg.py:78-87
info_text = (
    Text(f"Weight: {weight_tracker.get_value():.2f} Bias: {bias_tracker.get_value():.2f}",
         font_size=24)
    .next_to(title_text, DOWN, buff=0.2)
    .add_updater(
        lambda t: t.become(
            Text(f"Weight: {weight_tracker.get_value():.2f} Bias: {bias_tracker.get_value():.2f}",
                 font_size=24)
            .next_to(title_text, DOWN, buff=0.2)
        )
    )
)
```

### Pattern: Staggered Data Point Entrance

**What**: Data points appear one by one using AnimationGroup with lag_ratio. Each dot grows from its center with GrowFromCenter. The lag_ratio=0.1 means each dot starts 0.1s after the previous one, creating a ripple effect.
**When to use**: Revealing a dataset, showing multiple items appearing in sequence, any situation where "one by one" entrance is more engaging than "all at once."

```python
# Source: projects/manim-animations/src/linreg.py:98
self.play(AnimationGroup(*[GrowFromCenter(dot) for dot in points], lag_ratio=0.1))
```

## Scene Flow

1. **Title** (0-1s): "Linear Regression" writes at top edge.
2. **Axes** (1-3s): Coordinate system with x=[0,7] y=[0,20] and numbered ticks creates. Axis labels "x" and "y" appear.
3. **Parameters** (3-4s): "Weight: 0.00 Bias: 0.00" text writes below title. This text will auto-update during training.
4. **Data points** (4-5.5s): 8 blue dots grow in one-by-one with staggered timing. This builds anticipation — "here's what we need to fit."
5. **Initial line** (5.5-6.5s): Flat red line (weight=0, bias=0) grows from the axes origin. Visually wrong — clearly doesn't fit the data.
6. **Error lines** (6.5-7.5s): 8 dashed red lines grow from each dot down/up to the line. Shows how far off the predictions are.
7. **Training** (7.5-11.5s): 40 epochs at 0.1s each. The red line rotates and shifts to fit the data. Error lines shrink in real-time. Parameter text updates continuously. The viewer sees the model "learning."
8. **Hold** (11.5-12.5s): Final fitted state. Error lines are short. Line fits the data.

> Full file: `projects/manim-animations/src/linreg.py` (112 lines)
