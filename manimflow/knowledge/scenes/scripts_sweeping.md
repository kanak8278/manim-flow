---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/sweeping.py
project: manim-scripts
domain: [geometry, mathematics, computer_science, algorithms]
elements: [dot, line, parametric_curve, label]
animations: [move, shift, fade_out, draw, grow]
layouts: [centered]
techniques: [value_tracker, always_redraw, add_updater, traced_path, color_state_machine]
purpose: [demonstration, simulation, exploration]
mobjects: [Dot, Line, Circle, Cross, ValueTracker, TracedPath]
manim_animations: [Create, FadeOut]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 112
scene_classes: [SweepingLine, DeCasteljau]
---

## Summary

Two computational geometry scenes. SweepingLine demonstrates a growing circle that reveals random dots, followed by a sweeping line that partitions them into two colors based on which side they fall on — implemented entirely via updater functions. DeCasteljau visualizes the De Casteljau algorithm for cubic Bezier curves using ValueTracker-driven interpolation dots, always_redraw dynamic lines, and TracedPath to draw the final curve. The combination of updaters, always_redraw, and TracedPath makes this a rich reference for dynamic Manim patterns.

## Design Decisions

- **Updater-based dot coloring (SweepingLine)**: Each dot has an updater that checks its position relative to the growing circle and sweeping line. No animation calls needed — the updater fires every frame. This is the right approach for continuous state changes driven by moving geometry.
- **Two-phase updater swap**: Dots start with `opacity_updater` (checks if inside circle). Once inside, the updater is swapped to `color_updater` (checks which side of line). `clear_updaters()` + `add_updater()` implements a clean state machine.
- **ValueTracker for De Casteljau parameter**: t ranges from 0 to 1, driving all interpolation dots via updater lambdas. Single parameter controls the entire algorithm state.
- **always_redraw for dynamic construction lines**: Lines between interpolation points are `always_redraw` lambdas — they reconstruct every frame based on current dot positions. This is cleaner than updaters on Line objects.
- **TracedPath for curve output**: The final interpolation point (d31) leaves a red traced path as it moves. No explicit curve construction needed — the path emerges from the algorithm.
- **Dark green background (#455D3E)**: Unusual choice that makes the orange control points and red curve stand out. Geometric visualization benefits from non-black backgrounds.

## Composition

- **SweepingLine**:
  - Growing circle: starts at radius=0.001, scales to 1.5*frame_width
  - Moving line: from [-7,-5,0] to [-6,5,0], sweeps 14 units RIGHT then LEFT
  - Random dots: 30 dots, uniform in [-6,6] x [-4,4], fill_opacity=0.6
- **DeCasteljau**:
  - Control points: a1=[-3,-2,0], h1=[-3,0,0], h2=[3,0,0], a2=[3,2,0]
  - Anchor points (Cross): scale_factor=0.2
  - Handle points (Dot): color=ORANGE
  - Interpolation dots: GRAY (intermediate), RED (final)
  - Background: #455D3E

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background (DeCasteljau) | #455D3E | Dark green |
| Anchor points | WHITE | Cross, scale_factor=0.2 |
| Handle/control points | ORANGE | Dot |
| Static construction lines | ORANGE (outer), WHITE (inner) | Line |
| Dynamic construction lines | LIGHT_GRAY | always_redraw |
| Intermediate interpolation dots | GRAY | Dot |
| Final interpolation dot | RED | Dot |
| Traced curve | RED | TracedPath stroke |
| Dots (inside circle) | BLUE | opacity=1 |
| Dots (right of line) | BLUE | via color_updater |
| Dots (left of line) | YELLOW | via color_updater |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Circle grow | run_time=5 | scale_to_fit_width(1.5*frame_width) |
| Line sweep right | run_time=5 | 14 units RIGHT |
| Line sweep left | run_time=5 | 14 units LEFT |
| ValueTracker 0→1 | run_time=5 | De Casteljau parameter |
| FadeOut construction lines | Default | Clean up |
| Total (SweepingLine) | ~18s | Circle + line sweeps |
| Total (DeCasteljau) | ~12s | Animation + cleanup |

## Patterns

### Pattern: Updater-Based State Machine for Dot Coloring

**What**: Each dot has an updater function that checks geometric conditions (inside circle? which side of line?) and sets color accordingly. When a dot transitions state, `clear_updaters()` swaps the updater function — implementing a state machine without any play() calls.
**When to use**: Sweep line algorithms, Voronoi diagrams, point-in-polygon checks, any computational geometry visualization where point states change based on moving geometry. Also useful for particle simulations, field visualizations.

```python
# Source: projects/manim-scripts/scenes/sweeping.py:10-31
def opacity_updater(obj):
    if (sum((growing_circle.points[0] - growing_circle.get_center())**2)
        >= sum((obj.get_center() - growing_circle.get_center())**2)):
        obj.set_fill(BLUE, opacity=1)
        obj.clear_updaters()
        obj.add_updater(color_updater)

def color_updater(obj):
    if (np.dot(obj.get_center(), moving_line.normal_vector)
        < np.dot(moving_line.get_start(), moving_line.normal_vector)):
        if obj.color != BLUE:
            obj.set_color(BLUE)
    else:
        if obj.color != YELLOW:
            obj.set_color(YELLOW)
```

### Pattern: ValueTracker + Updater Lambdas for De Casteljau

**What**: A single ValueTracker parameter `t` drives all interpolation dots via updater lambdas. Each dot computes `(1-t)*A + t*B` from its two parent dots. The hierarchy of dots (d01-d04 → d11-d13 → d21-d22 → d31) mirrors the algorithm's recursive structure.
**When to use**: Any recursive subdivision algorithm — De Casteljau, binary search tree traversal, fractal generation. Also useful for any parametric animation where multiple elements depend on a single parameter.

```python
# Source: projects/manim-scripts/scenes/sweeping.py:50-79
t = ValueTracker(0.001)
d11 = Dot(color=GRAY).add_updater(
    lambda mob: mob.move_to(
        (1 - t.get_value()) * d01.get_center() + t.get_value() * d02.get_center()
    )
)
# ... d12, d13, d21, d22 follow same pattern ...
d31 = Dot(color=RED).add_updater(
    lambda mob: mob.move_to(
        (1 - t.get_value()) * d21.get_center() + t.get_value() * d22.get_center()
    )
)
```

### Pattern: always_redraw + TracedPath for Dynamic Geometry

**What**: Construction lines between moving dots use `always_redraw` to reconstruct every frame. The final point uses `TracedPath` to accumulate its trajectory as a visible curve. Together, they show both the algorithm's construction (lines) and its output (curve) dynamically.
**When to use**: Any algorithm where intermediate construction and final output coexist — Bezier curves, convex hull construction, Delaunay triangulation, or any progressive geometric construction.

```python
# Source: projects/manim-scripts/scenes/sweeping.py:87-96
dynamic_lines = [
    always_redraw(lambda a=a, b=b: Line(a.get_center(), b.get_center(), color=LIGHT_GRAY))
    for a, b in [(d11, d12), (d12, d13), (d21, d22)]
]
self.add(*dynamic_lines, *static_lines, d01, d02, d03, d04, d11, d12, d13, d21, d22, d31)
self.add(TracedPath(lambda: d31.get_center(), stroke_color=RED))
self.play(t.animate(run_time=5).set_value(0.999))
```

> **Gotcha**: In the list comprehension for `dynamic_lines`, the `lambda a=a, b=b:` default argument pattern is critical. Without it, all lambdas would capture the same loop variable.

## Scene Flow

1. **SweepingLine** (0-18s): 30 random dots placed. Growing circle reveals dots (they turn BLUE). Line appears. Sweeps right — dots on left turn YELLOW, right stay BLUE. Sweeps back left.
2. **DeCasteljau** (0-12s): Control points and construction lines appear. t animates 0→1 over 5s — interpolation dots slide, construction lines update, red dot traces the Bezier curve. Construction lines fade out, leaving only anchors and curve.

> Full file: `projects/manim-scripts/scenes/sweeping.py` (112 lines)
