---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/openg.py
project: manim-scripts
domain: [mathematics, geometry]
elements: [function_plot, parametric_curve, dot, circle_node, line, axes, coordinate_system]
animations: [write, fade_in, fade_out, draw, transform, rotate]
layouts: [centered]
techniques: [add_updater, always_redraw, moving_camera]
purpose: [exploration, demonstration]
mobjects: [Tex, NumberPlane, Dot, Circle, Line]
manim_animations: [Write, FadeIn, FadeOut, Create, FadeTransform]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 114
scene_classes: [OpenGLIntro, InteractiveRadius, NewtonIteration]
---

## Summary

Three scenes using Manim's OpenGL renderer. OpenGLIntro shows a "Hello World" with 3D camera rotation, then an OpenGL parametric surface with mesh and lighting. InteractiveRadius creates an interactive scene where a circle's radius tracks cursor distance from origin via an updater. NewtonIteration implements interactive Newton's method — click to place a point on a curve, press a key to iterate toward a root with tangent line visualization.

## Design Decisions

- **OpenGL renderer for 3D surfaces**: OpenGLSurface provides GPU-accelerated rendering for parametric surfaces. The mesh-to-surface FadeTransform shows wireframe before solid — a common 3D viz pattern.
- **Camera light manipulation**: Moving the light source demonstrates how surface appearance changes with lighting — useful for any 3D visualization where surface curvature matters.
- **Updater for interactive radius**: The circle rebuilds itself every frame via `mob.become(Circle(radius=...))`. This always_redraw-via-become pattern is the standard for geometry that depends on dynamic input.
- **Newton's method with tangent visualization**: Each iteration draws the tangent line at the current point, moves the dot to the x-intercept, then to the curve. The tangent line fades out after use. This makes the geometric interpretation of Newton's method concrete.
- **interactive_embed() for real interaction**: These scenes use Manim's interactive mode where keyboard input drives the animation. Not usable in batch rendering but demonstrates Manim's interactive capabilities.

## Composition

- **OpenGL surface**: u_range=(-3,3), v_range=(-3,3), function u*sin(v) + v*cos(u)
- **Interactive circle**: NumberPlane background, cursor_dot at 3*RIGHT + 2*UP initially
- **Newton axes**: default Axes, function = (x+6)(x+3)x(x-3)(x-6)/300

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Hello World | WHITE | Tex, scale=3 |
| OpenGL surface | Default | GPU-rendered |
| Surface mesh | Default | OpenGLSurfaceMesh |
| Interactive circle | RED | Dynamic radius |
| Cursor dot | Default | Dot |
| Newton curve | RED | Axes plot |
| Newton cursor dot | YELLOW | Dot |
| Tangent line | YELLOW | stroke_width=2 |
| NumberPlane | Default | Grid background |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Camera euler rotation | Default | theta=-10, phi=50 |
| Surface mesh Create | Default | OpenGLSurfaceMesh |
| FadeTransform mesh→surface | Default | Wireframe to solid |
| Light shift | Default | 2 moves |
| Newton tangent Create | Default | Per iteration |
| Total | Interactive | User-driven |

## Patterns

### Pattern: Updater-Based Interactive Geometry

**What**: A mobject rebuilds itself every frame based on another mobject's position. The circle uses `mob.become(Circle(radius=...))` where the radius is computed from the cursor dot's distance to origin. This creates responsive geometry without animation calls.
**When to use**: Interactive demonstrations, geometry that depends on user input or another moving element, dynamic constraints (e.g., circle through a point, tangent to a curve).

```python
# Source: projects/manim-scripts/scenes/openg.py:52-63
red_circle = Circle(radius=np.linalg.norm(cursor_dot.get_center()), color=RED)
red_circle.add_updater(
    lambda mob: mob.become(
        Circle(radius=np.linalg.norm(cursor_dot.get_center()), color=RED)
    )
)
```

### Pattern: Newton's Method with Tangent Line Visualization

**What**: Interactive Newton's method iteration. On keypress: compute tangent at current point, draw tangent line (extended beyond intersection), move cursor to x-intercept, then up to curve. Tangent fades out. Each step makes the geometric intuition of Newton's method visible.
**When to use**: Root-finding visualization, optimization demonstrations, any iterative numerical method where the geometric interpretation involves tangent lines or gradients.

```python
# Source: projects/manim-scripts/scenes/openg.py:86-113
if symbol == pyglet_key.I:
    x, y = self.axes.point_to_coords(self.cursor_dot.get_center())
    x_new = x - self.f(x) / derivative(self.f, x, dx=0.01)
    curve_point = self.cursor_dot.get_center()
    axes_point = self.axes.c2p(x_new, 0)
    tangent = Line(
        curve_point + (curve_point - axes_point)*0.25,
        axes_point + (axes_point - curve_point)*0.25,
        color=YELLOW, stroke_width=2,
    )
    self.play(Create(tangent))
    self.play(self.cursor_dot.animate.move_to(self.axes.c2p(x_new, 0)))
    self.play(self.cursor_dot.animate.move_to(self.axes.c2p(x_new, self.f(x_new))), FadeOut(tangent))
```

## Scene Flow

1. **OpenGLIntro**: "Hello World" writes, camera rotates to 3D view, text fades out. Surface mesh creates, transforms to solid surface. Light moves. Camera rotates further.
2. **InteractiveRadius**: Number plane and red circle appear. User moves cursor dot with 'G' key. Circle radius updates in real-time.
3. **NewtonIteration**: Axes and curve appear. User clicks 'P' to place point on curve. 'I' to iterate — tangent draws, cursor moves to root approximation.

> Full file: `projects/manim-scripts/scenes/openg.py` (114 lines)
> Note: Requires `--renderer=opengl` flag. Interactive scenes need `interactive_embed()` support (not available in batch/online rendering).
