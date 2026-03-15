---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/sine_curve_unit_circle.py
project: ragibson_manim-videos
domain: [mathematics, trigonometry, geometry]
elements: [dot, line, function_plot, coordinate_system]
animations: [draw]
layouts: [side_by_side]
techniques: [add_updater, always_redraw]
purpose: [demonstration, exploration]
mobjects: [Circle, Dot, Line, VGroup, MathTex]
manim_animations: []
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 73
scene_classes: [SineCurveUnitCircle]
---

## Summary

Classic demonstration linking the unit circle to the sine curve. A yellow dot orbits a circle on the left while a sine curve is traced on the right in real-time. A blue radius line connects the circle center to the dot, and a yellow horizontal line connects the dot to the curve's current point. The curve is built incrementally by appending Line segments every frame using a dt-based updater. This is the canonical "why sine is a wave" visualization.

## Design Decisions

- **dt-based updater instead of ValueTracker**: The dot's angular position advances by `dt * rate` each frame using add_updater with the dt parameter. This gives frame-rate-independent motion and avoids needing a ValueTracker for the angle. The instance variable `self.t_offset` tracks cumulative progress.
- **Curve built by appending Line segments**: Rather than using a parametric plot, the curve is constructed by appending a new Line segment from the last endpoint to the current position each frame. This creates the "drawing in real-time" effect where the curve grows from left to right.
- **Circle and curve on same y-axis**: The circle is positioned at x=-4 and the curve starts at x=-3, so the dot's y-coordinate directly maps to the curve's y-coordinate. The horizontal connecting line makes this correspondence explicit.
- **point_from_proportion for circular motion**: The dot uses Circle's `point_from_proportion(t % 1)` to get its position, where t is the cumulative offset. This handles the modular arithmetic of circular motion cleanly.
- **Manual axis construction**: Uses raw Line objects for axes instead of Axes mobject, with manually positioned MathTex labels for pi multiples. This gives full control over placement without axis ticks or numbers.

## Composition

- **X-axis**: Line from (-6, 0, 0) to (6, 0, 0)
- **Y-axis**: Line from (-4, -2, 0) to (-4, 2, 0)
- **Circle**: radius=1, centered at (-4, 0, 0)
- **X labels**: pi, 2pi, 3pi, 4pi at x = -1, 1, 3, 5 (spacing = 2 units per pi)
- **Curve start**: (-3, 0, 0) — 1 unit right of circle center
- **Dot**: radius=0.08, YELLOW
- **Radius line**: BLUE, from circle center to dot
- **Connecting line**: YELLOW_A, stroke_width=2, from dot to curve point
- **Curve segments**: YELLOW_D, appended incrementally

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Axes | WHITE | Raw Line objects |
| Circle | WHITE | radius=1 |
| Orbiting dot | YELLOW | radius=0.08 |
| Radius line | BLUE | always_redraw |
| Connecting line | YELLOW_A | stroke_width=2, always_redraw |
| Sine curve | YELLOW_D | Incrementally appended Lines |
| Pi labels | WHITE | MathTex |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Setup (axes, circle) | instant | self.add() |
| Dot orbit + curve trace | 8.5s | self.wait(8.5) with updaters |
| Orbit rate | 0.25 | ~2 full cycles in 8.5s |
| Total | ~8.5s | |

## Patterns

### Pattern: Real-Time Curve Tracing from Circular Motion

**What**: A dot orbits a circle using a dt-based updater. Each frame, a new Line segment is appended to a VGroup to trace out the sine curve. The dot's y-coordinate maps directly to the curve's y-value, while the x-position advances linearly with time (4 units per full orbit). Three always_redraw objects keep the radius line and connecting line synchronized.
**When to use**: Unit circle to trig function demonstrations, Lissajous figures, Fourier series visualization, any animation where circular motion needs to be decomposed into a waveform, parametric curve tracing.

```python
# Source: projects/ragibson_manim-videos/manim_examples/sine_curve_unit_circle.py:32-72
def move_dot_and_draw_curve(self):
    dot = Dot(radius=0.08, color=YELLOW)
    dot.move_to(orbit.point_from_proportion(0))
    self.t_offset = 0

    def go_around_circle(mob, dt, rate=0.25):
        self.t_offset += dt * rate
        mob.move_to(orbit.point_from_proportion(self.t_offset % 1))

    def get_line_to_curve():
        x = self.curve_start[0] + self.t_offset * 4
        y = dot.get_center()[1]
        return Line(dot.get_center(), np.array([x, y, 0]), color=YELLOW_A, stroke_width=2)

    self.curve = VGroup(Line(self.curve_start, self.curve_start))

    def get_curve():
        last_line = self.curve[-1]
        x = self.curve_start[0] + self.t_offset * 4
        y = dot.get_center()[1]
        self.curve.add(Line(last_line.get_end(), np.array([x, y, 0]), color=YELLOW_D))
        return self.curve

    dot.add_updater(go_around_circle)
    origin_to_circle_line = always_redraw(get_line_to_circle)
    dot_to_curve_line = always_redraw(get_line_to_curve)
    sine_curve_line = always_redraw(get_curve)
```

**Critical**: The `get_curve` function mutates `self.curve` by appending segments AND returns it. This means the VGroup grows every frame. For long animations, this accumulates thousands of Line objects which can slow rendering.

## Scene Flow

1. **Setup** (instant): X and Y axes drawn as raw lines. Pi labels placed. Unit circle added at (-4, 0).
2. **Orbit + trace** (0-8.5s): Yellow dot begins orbiting the circle. Blue radius line rotates with the dot. Yellow connecting line stretches horizontally to the growing curve. Sine wave traces out from left to right in YELLOW_D segments. After ~2 full orbits, the curve covers 0 to ~4pi.

> Full file: `projects/ragibson_manim-videos/manim_examples/sine_curve_unit_circle.py` (73 lines)
