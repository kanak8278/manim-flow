---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/graph_area_plot.py
project: ragibson_manim-videos
domain: [mathematics, calculus]
elements: [axes, function_plot, area_under_curve, line]
animations: []
layouts: [centered]
techniques: []
purpose: [demonstration]
mobjects: [Axes, Line]
manim_animations: []
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 28
scene_classes: [GraphAreaPlot]
---

## Summary

Static reference showing how to use Axes methods for shaded areas and vertical lines. Two curves (a parabola and a quadratic) are plotted on the same axes. Riemann rectangles fill a narrow band under the first curve with BLUE. A bounded area between the two curves from x=2 to x=3 is filled with GREY. Vertical yellow lines mark the integration bounds. Everything is added with self.add() (no animations).

## Design Decisions

- **Riemann rectangles for integration visualization**: `get_riemann_rectangles()` with dx=0.03 on a narrow x-range [0.3, 0.6] shows a fine-grained approximation. The small dx makes the rectangles nearly smooth, demonstrating both the concept and the API.
- **Bounded area between two curves**: `get_area(curve2, [2, 3], bounded_graph=curve1)` fills the region between two functions over a specific interval. The bounded_graph parameter is key -- without it, the area extends down to the x-axis.
- **Vertical lines from get_vertical_line**: `ax.get_vertical_line(ax.i2gp(x, curve))` creates a line from the x-axis to the curve at a given x-value. The `i2gp` (input-to-graph-point) method converts an x-value to the corresponding point on the graph.
- **No animations**: Everything uses self.add(), making this a single-frame reference card for the various area-filling APIs.

## Composition

- **Axes**: x_range=[0, 5], y_range=[0, 6], numbers at x=2 and x=3 only, no tips
- **Curve 1**: 4x - x^2, x_range=[0, 4], BLUE_C
- **Curve 2**: 0.8x^2 - 3x + 4, x_range=[0, 4], GREEN_B
- **Vertical lines**: at x=2 and x=3, YELLOW
- **Riemann rectangles**: x_range=[0.3, 0.6], dx=0.03, BLUE, fill_opacity=0.5
- **Bounded area**: between curve2 and curve1, x=[2, 3], GREY, opacity=0.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Axes | WHITE | Default |
| Curve 1 (4x-x^2) | BLUE_C | |
| Curve 2 (0.8x^2-3x+4) | GREEN_B | |
| Vertical lines | YELLOW | At x=2, x=3 |
| Riemann rectangles | BLUE | fill_opacity=0.5, dx=0.03 |
| Bounded area | GREY | opacity=0.5 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Static frame | N/A | self.add(), no animations |

## Patterns

### Pattern: Riemann Rectangles and Bounded Area Between Curves

**What**: Demonstrates three Axes area methods in one scene: `get_riemann_rectangles()` for rectangular approximation of integrals, `get_area()` with `bounded_graph` for filling between two curves, and `get_vertical_line()` with `i2gp()` for marking integration bounds. These are the core tools for visualizing integrals in Manim.
**When to use**: Integral visualization, area between curves, Riemann sum demonstrations, marking specific x-values on a graph, any calculus visualization involving definite integrals or bounded regions.

```python
# Source: projects/ragibson_manim-videos/manim_examples/graph_area_plot.py:5-27
ax = Axes(x_range=[0, 5], y_range=[0, 6],
          x_axis_config={"numbers_to_include": [2, 3]}, tips=False)
curve1 = ax.plot(lambda x: 4 * x - x ** 2, x_range=[0, 4], color=BLUE_C)
curve2 = ax.plot(lambda x: 0.8 * x ** 2 - 3 * x + 4, x_range=[0, 4], color=GREEN_B)

line1 = ax.get_vertical_line(ax.i2gp(2, curve1), color=YELLOW)
line2 = ax.get_vertical_line(ax.i2gp(3, curve1), color=YELLOW)

riemann_area = ax.get_riemann_rectangles(curve1, x_range=[0.3, 0.6], dx=0.03,
                                         color=BLUE, fill_opacity=0.5)
area = ax.get_area(curve2, [2, 3], bounded_graph=curve1, color=GREY, opacity=0.5)
```

**Critical**: `get_area()` with `bounded_graph` fills BETWEEN the two curves. Without `bounded_graph`, it fills from the curve down to the x-axis. The `i2gp()` method (input-to-graph-point) is essential for converting x-values to on-curve points.

## Scene Flow

1. **Static** (single frame): All elements appear at once. Two curves intersect. Riemann rectangles fill a narrow band. Vertical yellow lines mark x=2 and x=3. Grey area fills between the curves in [2, 3].

> Full file: `projects/ragibson_manim-videos/manim_examples/graph_area_plot.py` (28 lines)
