---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/3d_surface_plot.py
project: ragibson_manim-videos
domain: [mathematics, geometry, statistics]
elements: [surface_3d, axes, coordinate_system]
animations: []
layouts: [centered]
techniques: [three_d_camera]
purpose: [demonstration]
mobjects: [ThreeDAxes, Surface]
manim_animations: []
scene_type: ThreeDScene
manim_version: manim_community
complexity: beginner
lines: 23
scene_classes: [ThreeDSurfacePlot]
---

## Summary

Renders a 3D Gaussian surface (bell curve in two dimensions) on ThreeDAxes with a checkerboard fill pattern of ORANGE and BLUE at 50% opacity. The camera is set at phi=75 degrees, theta=-30 degrees. The surface is defined parametrically and scaled 2x about the origin. This is a minimal example showing the Surface mobject for 3D function visualization.

## Design Decisions

- **Parametric function returning [x, y, z] array**: The Surface mobject requires a function that takes (u, v) and returns a 3D numpy array. This is different from 2D plotting where you just return y. The Gaussian formula uses sigma=0.4, mu=[0,0] for a tight peak.
- **Checkerboard fill**: `set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)` creates an alternating color pattern that helps the viewer perceive the 3D curvature. Without it, a single-color surface looks flat under certain camera angles.
- **Scale 2x about ORIGIN**: The default u_range/v_range of [-2, 2] produces a small surface. Scaling by 2 makes it fill the screen while keeping the parametric function clean.
- **Static scene (no animations)**: Uses self.add() instead of self.play(), making this a single-frame render. Useful as a reference for surface setup without animation overhead.

## Composition

- **Camera**: phi=75 degrees (elevation from top), theta=-30 degrees (horizontal rotation)
- **Surface**: u_range=[-2, 2], v_range=[-2, 2], resolution=(24, 24), scaled 2x
- **Axes**: ThreeDAxes() with default ranges

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Surface fill (even) | ORANGE | opacity=0.5, checkerboard |
| Surface fill (odd) | BLUE | opacity=0.5, checkerboard |
| Surface stroke | GREEN | stroke_color |
| Axes | WHITE | Default ThreeDAxes |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Static frame | N/A | self.add(), no animations |

## Patterns

### Pattern: Parametric 3D Surface with Checkerboard Fill

**What**: Defines a parametric function that maps (x, y) to [x, y, z] and passes it to the Surface mobject. The checkerboard fill uses two alternating colors to enhance depth perception. Resolution controls the mesh density (higher = smoother but slower).
**When to use**: Visualizing 2D probability distributions (Gaussian, bivariate), optimization landscapes (loss surfaces), any function z=f(x,y) that benefits from 3D rendering, topographic representations.

```python
# Source: projects/ragibson_manim-videos/manim_examples/3d_surface_plot.py:4-19
class ThreeDSurfacePlot(ThreeDScene):
    def construct(self):
        resolution_fa = 24
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)

        def param_gauss(x, y):
            sigma, mu = 0.4, [0.0, 0.0]
            d = np.linalg.norm(np.array([x - mu[0], y - mu[1]]))
            z = np.exp(-(d ** 2 / (2.0 * sigma ** 2)))
            return np.array([x, y, z])

        gauss_plane = Surface(param_gauss, resolution=(resolution_fa, resolution_fa),
                              v_range=[-2, 2], u_range=[-2, 2])
        gauss_plane.scale(2, about_point=ORIGIN)
        gauss_plane.set_style(fill_opacity=1, stroke_color=GREEN)
        gauss_plane.set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)
```

## Scene Flow

1. **Static** (single frame): ThreeDAxes and Gaussian surface appear immediately. No animation. Camera positioned for standard 3D viewing angle.

> Full file: `projects/ragibson_manim-videos/manim_examples/3d_surface_plot.py` (23 lines)
