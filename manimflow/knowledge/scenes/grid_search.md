---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/grid_search.py
project: manim-animations
domain: [machine_learning, optimization]
elements: [axes, dot, surface_3d, label]
animations: [write, fade_in, fade_out, draw, rotate, zoom_in]
layouts: [centered]
techniques: [three_d_camera, color_gradient]
purpose: [exploration, demonstration, step_by_step]
mobjects: [ThreeDAxes, Dot3D, Surface, Line3D, Text, MathTex, VGroup]
manim_animations: [Write, Create, FadeOut, FadeIn, LaggedStart, Unwrite]
scene_type: ThreeDScene
manim_version: manim_community
complexity: intermediate
lines: 166
scene_classes: [GridSearch3D]
---

## Summary

Visualizes grid search hyperparameter tuning using a 3D surface plot. Starts with a top-down 2D view of a 4x4 hyperparameter grid, then rotates the camera to reveal a 3D accuracy surface (sum of three Gaussians). The surface is color-mapped from RED (low) to BLUE (high) by z-value. After ambient camera rotation for exploration, the optimal point is marked. Camera returns to top-down view with reference lines showing the best hyperparameter combination.

## Design Decisions

- **Top-down start, then 3D reveal**: The scene starts with phi=0, theta=-90 (looking straight down) showing only the 2D grid. The z-axis is hidden (opacity=0). This builds curiosity — "which combination is best?" — before the 3D surface reveals the answer. The dimensional reveal is the key dramatic moment.
- **Hidden z-axis initially**: z_axis and its label start at opacity=0 and animate to opacity=1 after the camera rotation. This prevents visual confusion during the 2D phase.
- **Multi-Gaussian surface**: Three Gaussian peaks at different positions create an accuracy landscape with a clear global maximum (at 2.5, 2.5) and secondary peaks. This is more realistic than a single peak — it shows why grid search matters (local optima exist).
- **Color mapping by z-value**: `set_fill_by_value(axes_3d, colorscale=[RED, BLUE], axis=2)` maps low accuracy to RED and high to BLUE. The viewer instantly sees which regions perform well.
- **Ambient camera rotation**: 7 seconds of slow rotation (rate=0.35) lets the viewer see the surface from all angles. This is essential for 3D scenes — a single viewpoint can hide features.
- **Return to 2D for final answer**: After 3D exploration, camera returns to top-down. Green reference lines project the optimal 3D point onto the 2D parameter axes. This connects the 3D insight back to actionable 2D coordinates.

## Composition

- **Screen regions**:
  - Title: centered (default for 3D scenes)
  - Intro text: `shift(LEFT * 3)`, font_size=32
  - 3D axes: centered, default ThreeDAxes position
  - Question text: `next_to(axes_3d, LEFT, buff=0.3)`, font_size=22
  - Best combination text: `shift(RIGHT * 3 + UP * 2)`, font_size=42
- **Axes configuration**: x_range=[0, 5, 0.05], y_range=[0, 5, 0.05], z_range=[0, 1, 0.1], blue axis color, no ticks
- **Grid points**: 4x4 grid at integer positions [1,2,3,4] x [1,2,3,4]
- **Surface**: u_range=[0.2, 5], v_range=[0.2, 5], resolution=15, fill_opacity=0.7
- **Camera**: Initial phi=0, theta=-90, zoom=0.5. Rotated to phi=75, theta=-45
- **Optimal point**: Dot3D at (2.5, 2.5, gaussian(2.5, 2.5)), radius=0.25

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Axes | BLUE | axis_config color |
| Grid points | WHITE | Dot3D, default |
| Surface (low accuracy) | RED | set_fill_by_value colorscale |
| Surface (high accuracy) | BLUE | set_fill_by_value colorscale |
| Surface | fill_opacity=0.7 | Semi-transparent |
| Optimal point | WHITE | Dot3D, radius=0.25 |
| Reference lines | GREEN | Line3D |
| "best" keyword | BLUE | t2c={"best": BLUE} in question text |
| Best combination text | WHITE | font_size=42 |

Color strategy: BLUE = good/high accuracy, RED = bad/low accuracy. This inverts the usual "red=danger" convention but matches the "cool=calm=good" intuition for performance metrics. GREEN for reference/projection lines.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write + FadeOut | ~2s | + 1s wait |
| Intro text Write | ~2s | + 3s wait, then Unwrite |
| Axes + labels Create | ~1s | |
| Grid points LaggedStart | ~2s | lag_ratio=0.1 |
| Question text Write | ~1s | + 2s wait |
| Camera rotation to 3D | run_time=2 | phi=75, theta=-45 |
| Z-axis reveal | ~1s | Animate opacity 0->1 |
| Surface Create | ~1s | + 2s wait |
| Ambient rotation | 7s | rate=0.35 |
| Optimal point Create | ~1s | + 2s wait |
| Return to top-down | run_time=2 | phi=0, theta=-90 |
| Reference lines + text | run_time=2 | + 3s wait |
| Total video | ~38 seconds | |

## Patterns

### Pattern: 2D-to-3D Camera Reveal

**What**: Start the scene with a top-down camera (phi=0, theta=-90) showing a flat 2D grid. Hide the z-axis. After introducing the problem, rotate the camera to a 3D perspective (phi=75, theta=-45) and reveal the z-axis. This creates a dramatic "there's a hidden dimension" moment.
**When to use**: Any 3D visualization where the third dimension adds insight — loss landscapes, hyperparameter surfaces, function plots. Also works in reverse (3D to 2D projection).

```python
# Source: projects/manim-animations/src/grid_search.py:43-81
# Hide z initially
axes_3d.z_axis.set_opacity(0)
axes_3d_labels[2].set_opacity(0)

# Start top-down
self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.5)

# ... show 2D grid ...

# Reveal 3D
self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES, run_time=2)
self.play(
    axes_3d.z_axis.animate.set_opacity(1),
    axes_3d_labels[2].animate.set_opacity(1),
)
```

### Pattern: Color-Mapped 3D Surface

**What**: Create a Surface from a parametric function and color it by z-value using `set_fill_by_value()`. The colorscale maps low z to one color and high z to another. Combined with semi-transparency (fill_opacity=0.7), underlying features remain visible.
**When to use**: Optimization landscapes, loss surfaces, accuracy heatmaps, any function of two variables where the z-value represents a metric. The color gradient provides instant visual ranking without reading axis numbers.

```python
# Source: projects/manim-animations/src/grid_search.py:103-110
surface = Surface(
    lambda u, v: axes_3d.c2p(u, v, gaussian_function(u, v)),
    u_range=[0.2, 5],
    v_range=[0.2, 5],
    resolution=15,
    fill_opacity=0.7,
)
surface.set_fill_by_value(axes_3d, colorscale=[RED, BLUE], axis=2)
```

### Pattern: Ambient Camera Rotation for 3D Exploration

**What**: Use `begin_ambient_camera_rotation(rate=0.35)` to slowly rotate the viewpoint around a 3D scene. Wait for a duration, then `stop_ambient_camera_rotation()`. This lets the viewer see the 3D object from all angles without manual camera keyframes.
**When to use**: Any ThreeDScene where a single viewpoint is insufficient — 3D surfaces, volumes, complex geometry. The slow rotation (rate 0.2-0.5) prevents motion sickness.

```python
# Source: projects/manim-animations/src/grid_search.py:115-124
self.begin_ambient_camera_rotation(rate=0.35)
self.wait(7)

max_point = Dot3D(
    axes_3d.c2p(2.5, 2.5, gaussian_function(2.5, 2.5)), radius=0.25
)
self.play(Create(max_point))
self.wait(2)

self.stop_ambient_camera_rotation()
```

### Pattern: 3D-to-2D Projection with Reference Lines

**What**: After 3D exploration, return the camera to top-down view and draw Line3D projections from the optimal 3D point onto the 2D parameter axes. This shows the viewer "here are the actual hyperparameter values to use."
**When to use**: Extracting 2D coordinates from a 3D result — optimal hyperparameters from a surface, projecting a 3D point onto axes, connecting a 3D insight to actionable 2D values.

```python
# Source: projects/manim-animations/src/grid_search.py:130-149
self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=2)
self.play(
    axes_3d.z_axis.animate.set_opacity(0),
    axes_3d_labels[2].animate.set_opacity(0),
)

line_x = Line3D(
    start=axes_3d.c2p(2.5, 0, 0), end=axes_3d.c2p(2.5, 2.5, 0), color=GREEN
)
line_y = Line3D(
    start=axes_3d.c2p(0, 2.5, 0), end=axes_3d.c2p(2.5, 2.5, 0), color=GREEN
)
best_x = MathTex("x").move_to(axes_3d.c2p(2.5, -0.25, 0))
best_y = MathTex("y").move_to(axes_3d.c2p(-0.25, 2.5, 0))
```

## Scene Flow

1. **Title** (0-3s): "Grid Search for Hyperparameter Tuning" writes, then fades out.
2. **Problem introduction** (3-10s): Explanatory text about two hyperparameters appears left, then unwrites.
3. **2D grid** (10-16s): Top-down view. 3D axes create (z hidden). 16 grid points appear with LaggedStart. Question text asks "which combination yields the best performance?"
4. **3D reveal** (16-22s): Points and question fade out. Camera rotates to 3D perspective. Z-axis and "Accuracy" label appear.
5. **Surface exploration** (22-33s): Color-mapped Gaussian surface creates. Camera rotates slowly for 7 seconds. White dot marks the global maximum at (2.5, 2.5).
6. **Return to 2D** (33-38s): Surface fades out. Camera returns to top-down. Z-axis hides. Green reference lines project optimal point onto parameter axes. "Best combination" text with hyperparameter values appears.

> Full file: `projects/manim-animations/src/grid_search.py` (166 lines)
