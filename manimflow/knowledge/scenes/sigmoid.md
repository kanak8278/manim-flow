---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/sigmoid.py
project: manim-animations
domain: [machine_learning, neural_networks, activation_functions, classification]
elements: [axes, function_plot, dot, dashed_line, label, paragraph]
animations: [write, draw, stagger]
layouts: [split_screen, edge_anchored]
techniques: []
purpose: [definition, demonstration]
mobjects: [Axes, Dot, DashedLine, Text, MathTex, VGroup]
manim_animations: [Write, Create, FadeOut, LaggedStart]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 67
scene_classes: [Sigmoid]
---

## Summary

Visualizes the sigmoid activation function with a YELLOW S-curve plotted on BLUE axes with numbered ticks. An explanation text describes the 0-to-1 mapping and binary classification use case. Three evaluation points at x = -4, 0, 4 are shown with GREEN dashed vertical lines connecting each point on the curve to the x-axis, demonstrating how extreme inputs saturate near 0 or 1 while x=0 maps to 0.5. Uses a MathTex graph label for the formula.

## Design Decisions

- **Dashed lines from axis to curve points**: Unlike the ReLU visualization (dots only), sigmoid adds GREEN dashed vertical lines from the x-axis up to each evaluation point. This visually traces "input x maps to output sigma(x)" and shows the saturation behavior for extreme values.
- **MathTex for graph label**: Uses LaTeX formula `\sigma(x) = \frac{1}{1 + e^{-x}}` instead of plain Text. The proper mathematical notation is important for an audience that will use this formula.
- **Include numbers on axes**: `include_numbers=True` because the specific output values (0, 0.5, 1) matter for understanding sigmoid behavior. This contrasts with ReLU where exact values are less important.
- **Explanation positioned LEFT*3.5 + UP*1.5**: The text is pushed up and left to avoid overlapping with the sigmoid curve's midpoint area and the dashed lines.

## Composition

- **Screen regions**:
  - Title: centered, font_size=40, then faded out
  - Axes: centered, default axis length
  - Graph label: `get_graph_label()`, direction=UP
  - Explanation: `shift(LEFT * 3.5 + UP * 1.5)`, font_size=22, line_spacing=1.5
- **Axes configuration**: x_range=[-5, 5, 1], y_range=[-0.5, 1.5, 0.5], axis_config={"color": BLUE, "include_numbers": True}
- **Evaluation points**: x = -4 (y near 0.018), x = 0 (y = 0.5), x = 4 (y near 0.982)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Axes | BLUE | include_numbers=True |
| Sigmoid graph | YELLOW | S-curve |
| Graph label | WHITE | MathTex, LaTeX fraction |
| Explanation text | WHITE | font_size=22, line_spacing=1.5 |
| Evaluation dots | WHITE | Default Dot |
| Evaluation dashed lines | GREEN | DashedLine from (x,0) to (x,y) |

Color strategy: Same as ReLU — YELLOW graph on BLUE axes. GREEN dashed lines are added for the evaluation trace, matching the "construction line" convention used in euclidean_distance.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write + FadeOut | ~2s | + 1s wait between |
| Axes + labels Create/Write | ~1s | |
| Graph + label Create/Write | run_time=2 | + 1s wait |
| Explanation Write | ~2s | + 2s wait |
| Dots + dashed lines LaggedStart | ~2s | lag_ratio=0.5 |
| Final hold | 3s | |
| Total video | ~15 seconds | |

## Patterns

### Pattern: Evaluation Point with Vertical Trace

**What**: For each evaluation x-value, create a Dot at the function value and a DashedLine from the x-axis (x, 0) to the point (x, f(x)). Group dot + line into a VGroup and animate them together via LaggedStart. The dashed line visually traces the function evaluation.
**When to use**: Sigmoid, tanh, or any bounded activation function where showing the mapping from input to bounded output is important. Also useful for CDF evaluation, probability lookups, or any function where vertical projections aid understanding.

```python
# Source: projects/manim-animations/src/sigmoid.py:48-65
input_values = [-4, 0, 4]
dots = VGroup()
dashed_lines = VGroup()
for x in input_values:
    y = 1 / (1 + np.exp(-x))
    dot = Dot().move_to(axes.c2p(x, y))
    dashed_line = DashedLine(
        start=axes.c2p(x, 0), end=axes.c2p(x, y), color=GREEN
    )
    dots.add(dot)
    dashed_lines.add(dashed_line)

self.play(
    LaggedStart(
        *[Create(VGroup(dot, line)) for dot, line in zip(dots, dashed_lines)],
        lag_ratio=0.5
    )
)
```

## Scene Flow

1. **Title** (0-2s): "Sigmoid Activation Function" writes, then fades out.
2. **Graph** (2-6s): Blue axes with numbers create. Yellow sigmoid S-curve draws. LaTeX formula label appears above curve.
3. **Explanation** (6-10s): Multi-line text writes on the upper left describing sigmoid properties and binary classification use.
4. **Evaluation** (10-15s): Three (dot + dashed line) pairs appear with LaggedStart at x=-4, 0, 4. The dashed lines show how -4 maps near 0, 0 maps to 0.5, and 4 maps near 1. Hold 3s.

> Full file: `projects/manim-animations/src/sigmoid.py` (67 lines)
