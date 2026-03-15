---
source: https://github.com/3b1b/videos/blob/main/once_useful_constructs/graph_scene.py
project: videos
domain: [mathematics, calculus, geometry]
elements: [axes, function_plot, line, label, formula]
animations: [write, transform, draw, animate_parameter]
layouts: [edge_anchored]
techniques: [value_tracker, add_updater, helper_function]
purpose: [demonstration, step_by_step, exploration, definition]
mobjects: [NumberLine, ParametricCurve, Rectangle, VGroup, Line, RegularPolygon]
manim_animations: [Write, Transform, UpdateFromAlphaFunc, DrawBorderThenFill, ShowCreation]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 564
scene_classes: [GraphScene]
---

## Summary

A legacy scene base class for function graphing with built-in axes setup, graph plotting, Riemann sum rectangles, derivative computation, secant line groups, and integral bound animation. While deprecated in favor of the modern Axes mobject, the patterns here show how to build a complete calculus visualization toolkit at the scene level: coordinate transforms, labeled axes, color-graded Riemann rectangles, and animated secant-slope convergence to derivatives.

## Design Decisions

- **Scene-level graphing (deprecated pattern)**: All coordinate transforms live on the scene object rather than on an Axes mobject. This couples graph logic to the scene, making reuse harder. Modern manimlib uses Axes directly, but these patterns show the foundational techniques.
- **Color-graded Riemann rectangles**: Start/end colors create a visual gradient across the integration interval, making it clear where the approximation is coarse vs fine. Signed area uses inverted colors below x-axis.
- **Secant slope group as VGroup with kwargs**: The group stores its construction parameters in `group.kwargs`, enabling `animate_secant_slope_group_change` to smoothly interpolate dx toward 0 (derivative visualization).
- **Graph origin offset**: graph_origin = 2.5*DOWN + 4*LEFT positions axes in bottom-left, leaving room for annotations above and to the right.

## Composition

- **Axes positioning**: graph_origin at 2.5*DOWN + 4*LEFT. X-axis width=9, Y-axis height=6.
- **Default ranges**: x: [-1, 10], y: [-1, 10], tick_frequency=1 for both.
- **Axes color**: GREY.
- **Graph colors cycle**: [BLUE, GREEN, YELLOW] for successive graphs.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Axes | GREY | Default axes_color |
| Graph (1st) | BLUE | Cycles through default_graph_colors |
| Graph (2nd) | GREEN | Next in cycle |
| Derivative | GREEN | default_derivative_color |
| Input marker | YELLOW | default_input_color |
| Riemann start | BLUE | default_riemann_start_color |
| Riemann end | GREEN | default_riemann_end_color |
| Riemann rectangles | Color gradient | stroke_color=BLACK, stroke_width=1, fill_opacity=1 |
| Area fill | 0.8 opacity | area_opacity |

## Patterns

### Pattern: Riemann Sum Rectangles with Color Gradient

**What**: Creates a VGroup of rectangles under a graph curve, with colors grading from start_color to end_color across the interval. Supports left/right/center sampling, signed area (inverted colors below x-axis), and progressive refinement via `get_riemann_rectangles_list` which generates increasingly fine approximations.

**When to use**: Integral visualization, area-under-curve approximation, Riemann sum convergence demonstration. The color gradient makes the dx spacing visually apparent. The refinement list enables animated convergence to the true integral.

```python
# Source: projects/videos/once_useful_constructs/graph_scene.py:219-268
def get_riemann_rectangles(self, graph, x_min=None, x_max=None, dx=0.1,
    input_sample_type="left", stroke_width=1, stroke_color=BLACK,
    fill_opacity=1, start_color=None, end_color=None, show_signed_area=True):
    rectangles = VGroup()
    x_range = np.arange(x_min, x_max, dx)
    colors = color_gradient([start_color, end_color], len(x_range))
    for x, color in zip(x_range, colors):
        graph_point = self.input_to_graph_point(sample_input, graph)
        rect = Rectangle()
        rect.replace(points, stretch=True)
        if graph_point[1] < self.graph_origin[1] and show_signed_area:
            fill_color = invert_color(color)
        else:
            fill_color = color
        rect.set_fill(fill_color, opacity=fill_opacity)
        rect.set_stroke(stroke_color, width=stroke_width)
        rectangles.add(rect)
    return rectangles
```

### Pattern: Animated Secant Slope Convergence

**What**: Creates a secant line group (dx_line, df_line, optional labels, secant line) that stores its construction kwargs. An animation function smoothly interpolates dx toward 0 and/or moves x along the curve, visually demonstrating the derivative as the limit of the secant slope.

**When to use**: Teaching derivatives, showing tangent line as limit of secant lines, visualizing instantaneous rate of change. The stored kwargs pattern enables smooth UpdateFromAlphaFunc interpolation.

```python
# Source: projects/videos/once_useful_constructs/graph_scene.py:524-563
def animate_secant_slope_group_change(self, secant_slope_group,
    target_dx=None, target_x=None, run_time=3, added_anims=None):
    start_dx = secant_slope_group.kwargs["dx"]
    start_x = secant_slope_group.kwargs["x"]
    if target_dx is None: target_dx = start_dx
    if target_x is None: target_x = start_x

    def update_func(group, alpha):
        dx = interpolate(start_dx, target_dx, alpha)
        x = interpolate(start_x, target_x, alpha)
        kwargs = dict(secant_slope_group.kwargs)
        kwargs["dx"] = dx
        kwargs["x"] = x
        new_group = self.get_secant_slope_group(**kwargs)
        group.become(new_group)
        return group

    self.play(UpdateFromAlphaFunc(secant_slope_group, update_func, run_time=run_time))
```

### Pattern: Animated Integral Bounds

**What**: Smoothly animates the bounds of an integral region (Riemann rectangles + vertical lines + labels) using UpdateFromAlphaFunc. The update function rebuilds the area, vertical lines, and repositions labels at each alpha step.

**When to use**: Showing how integral value changes as bounds shift, demonstrating the fundamental theorem of calculus, variable upper/lower bound integrals. The simultaneous update of area + markers + labels keeps everything synchronized.

```python
# Source: projects/videos/once_useful_constructs/graph_scene.py:471-522
def get_animation_integral_bounds_change(self, graph, new_t_min, new_t_max, run_time=1.0):
    def update_group(group, alpha):
        area, left_v_line, left_T_label, right_v_line, right_T_label = group
        t_min = interpolate(curr_t_min, new_t_min, alpha)
        t_max = interpolate(curr_t_max, new_t_max, alpha)
        new_area = self.get_area(graph, t_min, t_max)
        Transform(area, new_area).update(1)
        # ... repositions lines and labels ...
    return UpdateFromAlphaFunc(group, update_group, run_time=run_time)
```

## Scene Flow

1. **Axes setup** (0-2s): setup_axes() creates x/y NumberLines with labels.
2. **Graph drawing** (2-5s): get_graph() plots parametric curve from function.
3. **Riemann sum** (5-15s): Rectangles appear, then transform_between_riemann_rects refines dx.
4. **Derivative** (15-25s): Secant slope group appears, dx shrinks toward 0.
5. **Integral bounds** (25-35s): Area region animates as bounds change.

## manimlib Notes

- Uses legacy `OldTex`/`OldTexText` for labels (pre-refactor manimlib)
- `digest_config` pattern for class attributes (legacy CONFIG dict style)
- Modern equivalent: use `Axes` mobject directly with `axes.get_graph()`, `axes.get_riemann_rectangles()`
