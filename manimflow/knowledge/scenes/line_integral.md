---
source: https://github.com/vivek3141/videos/blob/main/line_integral.py
project: vivek3141_videos
domain: [mathematics, calculus, geometry, physics]
elements: [axes, parametric_curve, surface_3d, arrow, label, equation, area_under_curve, dashed_line, dot]
animations: [write, draw, transform, camera_rotate]
layouts: [centered, vertical_stack]
techniques: [three_d_camera, ambient_camera_rotation, custom_mobject, progressive_disclosure]
purpose: [derivation, step_by_step, demonstration, definition]
mobjects: [ThreeDAxes, ParametricSurface, ParametricFunction, Axes, FunctionGraph, TexMobject, TextMobject, VGroup, Line, Brace, Rectangle, Dot, Circle, BulletedList]
manim_animations: [Write, ShowCreation, Transform, Uncreate, ApplyMethod, FadeInFromDown]
scene_type: ThreeDScene
manim_version: manimlib
complexity: intermediate
lines: 1061
scene_classes: [Positron, Intro, ScalarField, Equation, ArcLength, ArcExp, LineIntegralScalar]
---

## Summary

Visualizes line integrals over scalar fields and vector fields, progressing from arc length to the full line integral formula. The key visual technique is a 3D parametric surface with a curve traced on it, then camera rotation to project the curve down to 2D where the area under it becomes visible. Custom Riemann sum rectangles approximate the integral area. A custom Positron mobject (red circle with "+") represents charges. The arc length derivation builds the formula in 5 algebraic steps using Transform chains.

## Design Decisions

- **3D surface with curve overlay**: The scalar field f(x,y) is shown as a ParametricSurface with the line integral path traced as a ParametricFunction on the surface. Camera rotation reveals the "curtain" of area between the curve and the base.
- **Camera projection trick**: Start in 3D angled view, then move camera to side view (pi/2, -pi/2) to collapse the surface into a 2D curve. This shows that the 3D line integral projects to an area under a curve.
- **Riemann sums as thin rectangles**: Custom `get_riemann_sums()` builds VGroup of thin Rectangle mobjects (dx=0.005) to approximate the area. Each rectangle has height = f(point) and width = dx.
- **Custom Positron mobject**: Circle subclass with CONFIG dict, red fill at 0.5 opacity, "+" symbol inside. Shows how to create labeled circular nodes.
- **5-step arc length derivation**: Delta_s -> sum -> limit -> multiply/divide by dt -> integral. Each step is Transform of the previous.

## Composition

- **3D surface**: ParametricSurface with u_min/v_min=-1, u_max/v_max=1, resolution=(16,24), scaled 2x
- **ThreeDAxes**: Matching range [-1,1] for x,y,z, scaled 2 or 2.5x
- **Camera angles**: Initial position `0.8*pi/2, -0.45*pi`, then side view `pi/2, -pi/2`, then front `0, -pi/2`
- **Arc length diagram**: Triangle with dx (GREEN), dy (RED), ds (YELLOW) sides, with Brace labels
- **Equation sizing**: scale=1.5 for main equations, scale=2 for section headings
- **Riemann sums**: dx=0.005 for smooth fill, rectangles centered at grid points

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Scalar field surface | YELLOW/ORANGE | checkerboard_colors |
| Line integral surface | RED/ORANGE | checkerboard_colors |
| Parametric curve | BLUE or WHITE | Default ParametricFunction |
| dx segment | GREEN | Line, Brace labeled |
| dy segment | RED | Line, Brace labeled |
| ds segment | YELLOW | Line, Brace labeled |
| Riemann rectangles | RED | fill_opacity=0.3, stroke_opacity=0.3 |
| Section headings | BLUE/YELLOW/ORANGE | Vary by topic |
| Positron | RED | Circle fill_opacity=0.5, stroke_width=3 |
| Integral text | WHITE | Default |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Surface creation | ShowCreation ~2s | Full surface appears |
| Ambient rotation | 6-30s | begin_ambient_camera_rotation() |
| Camera move | ~2s | move_camera() transition |
| Transform chain (5 steps) | ~1s each | Arc length derivation |
| Riemann sums | ShowCreation ~2s | All rectangles at once |
| Total per scene | ~30-60s | Varies |

## Patterns

### Pattern: 3D Surface with Curve Projection

**What**: Render a 3D scalar field as a ParametricSurface, trace a parametric curve on the surface, then rotate the camera to project everything to a 2D side view. This visually demonstrates that a line integral over a scalar field equals the area under a projected curve. The camera moves from angled 3D to flat 2D using `move_camera()`.

**When to use**: Line integrals, surface integrals, contour integrals, any concept where a 3D object projects meaningfully to 2D. Also works for showing cross-sections of solids of revolution.

```python
# Source: projects/vivek3141_videos/line_integral.py:282-375
surface = ParametricSurface(
    self.func, resulution=(16, 24),
    u_min=-1, u_max=1, v_min=-1, v_max=1,
    fill_color=RED, checkerboard_colors=[RED, ORANGE]
)
curve = ParametricFunction(self.c, t_min=-1, t_max=1)
curve_p = ParametricFunction(self.c_project, t_min=-1, t_max=1)

surface.scale(2)
axes = ThreeDAxes(**t_config).scale(2.5)

self.play(ShowCreation(axes), ShowCreation(surface), ShowCreation(curve))
self.move_camera(0.8 * np.pi / 2, -0.45 * np.pi)
self.begin_ambient_camera_rotation()
self.wait(6)

# Project to 2D
self.stop_ambient_camera_rotation()
self.move_camera(np.pi / 2, -np.pi / 2)
self.play(Transform(curve, curve_p), Uncreate(surface))
area = self.get_riemann_sums(self.c_project, dx=0.005)
self.play(ShowCreation(area))
```

### Pattern: Custom Riemann Sum Rectangles

**What**: Generates a VGroup of thin colored rectangles to approximate the area under a parametric curve. Each rectangle has height from the function value and width=dx. For 3D use, the rectangles are positioned in the xz-plane (y=0). The color parameter controls the fill.

**When to use**: Riemann integration visualization, area under curve, probability density shading, any numerical integration approximation display.

```python
# Source: projects/vivek3141_videos/line_integral.py:399-412
@staticmethod
def get_riemann_sums(func, dx=0.2, x=(-1, 1), color=RED):
    rects = VGroup()
    for i in np.arange(x[0], x[1], dx):
        point = func(i)
        h = point[2]  # z-value for 3D
        rect = Rectangle(
            height=abs(h), width=dx, color=color,
            stroke_opacity=0.3, fill_opacity=0.3)
        rect.shift(i * RIGHT + (h / 2) * UP)
        rects.add(rect)
    return rects
```

### Pattern: Custom Labeled Circle Mobject (Positron)

**What**: A Circle subclass using CONFIG dict to set radius, stroke, fill color, and fill opacity. A TeX label ("+") is centered inside. This creates a reusable labeled node that can represent charges, particles, or any labeled circular entity.

**When to use**: Particle physics diagrams, circuit elements, graph nodes with labels, any scenario needing a filled circle with a centered symbol.

```python
# Source: projects/vivek3141_videos/line_integral.py:4-18
class Positron(Circle):
    CONFIG = {
        "radius": 0.2,
        "stroke_width": 3,
        "color": RED,
        "fill_color": RED,
        "fill_opacity": 0.5,
    }
    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        plus = TexMobject("+")
        plus.scale(0.7)
        plus.move_to(self)
        self.add(plus)
```

## Scene Flow

1. **Intro** (0-10s): "Line Integral" title. Three integral notations shown in sequence via Transform. BulletedList of applications (Work, Center of mass, Faraday's Law, Ampere's Law).
2. **ScalarField** (10-25s): 3D surface f(x,y)=x^2+y^2 with checkerboard YELLOW/ORANGE. Camera rotates to angled view. Ambient rotation for 30 seconds.
3. **ArcLength** (25-50s): 2D parametric curve. Zoom in. Triangle showing dx, dy, ds with Braces. Leads into algebraic derivation.
4. **ArcExp** (50-70s): 5-step Transform chain: Delta_s -> sum -> limit -> integral -> ds. Final equation shown with equals sign.
5. **LineIntegralScalar** (70-110s): 3D surface with curve on it. Ambient rotation. Camera rotates to side view. Surface removed, Riemann sums appear. Camera moves to front. Final formula displayed.

> Full file: `projects/vivek3141_videos/line_integral.py` (1061 lines, first 400 documented)
