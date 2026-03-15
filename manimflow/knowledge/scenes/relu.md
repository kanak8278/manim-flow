---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/relu.py
project: manim-animations
domain: [machine_learning, neural_networks, activation_functions]
elements: [axes, function_plot, dot, label, paragraph]
animations: [write, draw, stagger]
layouts: [split_screen, edge_anchored]
techniques: []
purpose: [definition, demonstration]
mobjects: [Axes, Dot, Text, VGroup]
manim_animations: [Write, Create, FadeOut, LaggedStart]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 57
scene_classes: [ReLU]
---

## Summary

Visualizes the ReLU activation function with a plot of max(0, x) on blue axes. The YELLOW graph shows the characteristic "hockey stick" shape. An explanation text block on the left describes the function behavior. Three dots at x = -2, 0, 2 highlight key points on the curve. Simple and clean — primarily a definition/reference animation.

## Design Decisions

- **Title shown then removed**: Title "ReLU Activation Function" writes then fades out, freeing screen space for the graph and explanation. This is a common pattern for short educational clips.
- **YELLOW graph on BLUE axes**: High contrast pairing. YELLOW is the most visible color against a dark background, making the function shape immediately clear. BLUE axes recede into the background.
- **Explanation text on the left**: Multi-line text block with line_spacing=1.5 provides readable description alongside the graph. Shifted LEFT*3.5 to avoid overlapping the plot.
- **Key point dots at -2, 0, 2**: These three points demonstrate the three regimes: negative input (output=0), zero (inflection point), positive input (output=x). LaggedStart with lag_ratio=0.5 gives each dot a moment of attention.

## Composition

- **Screen regions**:
  - Title: centered (default), font_size=40, then faded out
  - Axes: centered (default), default axis length
  - Graph label: `get_graph_label()`, x_val=1, buff=1
  - Explanation: `shift(LEFT * 3.5)`, font_size=22, line_spacing=1.5
- **Axes configuration**: x_range=[-3, 3, 1], y_range=[-1, 4, 1], axis_config={"color": BLUE}
- **Key dots**: at x = -2 (y=0), x = 0 (y=0), x = 2 (y=2)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Axes | BLUE | axis_config color |
| ReLU graph | YELLOW | axes.plot(lambda x: max(0, x)) |
| Graph label | WHITE | "ReLU(x) = max(0, x)", font_size=24 |
| Explanation text | WHITE | font_size=22, line_spacing=1.5 |
| Key dots | WHITE | Default Dot |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write + FadeOut | ~2s | + 1s wait between |
| Axes + labels Create/Write | ~1s | |
| Graph + label Create/Write | run_time=2 | + 1s wait |
| Explanation Write | ~2s | |
| Key dots LaggedStart | ~2s | lag_ratio=0.5 |
| Final hold | 3s | |
| Total video | ~13 seconds | |

## Patterns

### Pattern: Activation Function Visualization

**What**: Plot an activation function using `axes.plot(lambda x: ...)` with a graph label from `axes.get_graph_label()`. Add key evaluation points as Dots at critical x-values. Pair with a multi-line text explanation on one side.
**When to use**: Visualizing ReLU, sigmoid, tanh, leaky ReLU, or any activation function. The key points should highlight the function's characteristic behavior (zero crossing, saturation, inflection).

```python
# Source: projects/manim-animations/src/relu.py:21-30
relu_graph = axes.plot(
    lambda x: max(0, x),
    color=YELLOW,
)
relu_label = axes.get_graph_label(
    relu_graph,
    label=Text("ReLU(x) = max(0, x)", font_size=24),
    x_val=1,
    buff=1,
)
```

## Scene Flow

1. **Title** (0-2s): "ReLU Activation Function" writes, then fades out.
2. **Graph** (2-6s): Blue axes create with labels. Yellow ReLU curve draws with graph label.
3. **Explanation** (6-9s): Multi-line text writes on the left describing ReLU behavior.
4. **Key points** (9-13s): Three dots appear at x=-2, 0, 2 with LaggedStart. Hold 3s.

> Full file: `projects/manim-animations/src/relu.py` (57 lines)
