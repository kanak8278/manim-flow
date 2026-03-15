---
source: https://github.com/vivek3141/videos/blob/main/gaussian.py
project: vivek3141_videos
domain: [mathematics, calculus, geometry, statistics]
elements: [axes, function_plot, parametric_curve, surface_3d, area_under_curve, equation, label, dashed_line, line]
animations: [write, transform, draw, camera_rotate]
layouts: [centered, vertical_stack]
techniques: [three_d_camera, ambient_camera_rotation, custom_mobject, progressive_disclosure]
purpose: [derivation, step_by_step, proof, demonstration]
mobjects: [Axes, ParametricFunction, ParametricSurface, ThreeDAxes, Cylinder, Rectangle, VGroup, TexMobject, TextMobject, Brace, Line, Dot, Circle]
manim_animations: [Write, Transform, ShowCreation, FadeIn, Uncreate, ApplyMethod, ReplacementTransform, FadeInFrom]
scene_type: ThreeDScene
manim_version: manimlib
complexity: advanced
lines: 729
scene_classes: [Cylinder, UnwrappedCylinder, Intro, DefiniteIntegral, Nonelem, Gaussian, ThreeFunc, GaussianVisualOld, GaussianScene, GaussianVisual, Volume, Erf, Thumb]
---

## Summary

Derives the Gaussian integral (integral of e^{-x^2} = sqrt(pi)) using the cylindrical shell method in 3D. The core visual trick is showing the 2D Gaussian surface e^{-(x^2+y^2)}, placing a Cylinder shell on it, then unwrapping the cylinder into a flat rectangle whose dimensions are 2*pi*r (width) and e^{-r^2} (height). Custom Cylinder and UnwrappedCylinder Mobject classes extend Sphere for the 3D geometry. The volume integral 2*pi*r*e^{-r^2} is then evaluated via u-substitution to get pi, proving I^2 = pi, so I = sqrt(pi).

## Design Decisions

- **Custom Cylinder as Sphere subclass**: Since manimlib's Sphere handles ParametricSurface rendering, Cylinder overrides `func(u, v)` to map (u,v) -> (cos(u), sin(u), v). UnwrappedCylinder maps to a flat rectangle. ReplacementTransform morphs one into the other.
- **Shell method visualization**: Instead of abstract double integral, show a physical cylindrical shell sitting on the Gaussian surface, then unwrap it. The viewer sees the 2D*pi*r*height formula directly.
- **I^2 trick shown algebraically**: The integral I is squared to get I^2 = double integral over R^2. Shown as a chain of 7 equation transforms, with Brace annotations labeling each single integral as "I".
- **Riemann sums for area**: Custom thin-rectangle Riemann sums (dx=0.01) with low opacity (0.3) to show area under the Gaussian curve without occluding it.
- **SpecialThreeDScene base for 3D**: GaussianScene extends SpecialThreeDScene for better 3D defaults (lighting, camera). Uses `get_axes()` and `default_angled_camera_position`.

## Composition

- **Gaussian curve**: ParametricFunction t -> (t, e^{-t^2}), t in [-3,3], scaled 2x, shifted 2*DOWN
- **Gaussian surface**: ParametricSurface (u,v) -> (u, v, e^{-(u^2+v^2)}), u/v in [-2,2] or [-3,3], scaled 2x
- **Cylinder shell**: radius=0.75, u in [0, 2*PI], v in [0, const], ORANGE/RED checkerboard, scaled 2x
- **Unwrapped rectangle**: Width = 2*pi*radius, height = e^{-r^2}, with dimension labels
- **Equation chain**: Each equation scale=2, centered at ORIGIN
- **Dimension labels**: top_line YELLOW (stroke_width=5), side_line GREEN (stroke_width=5), rotated 90 degrees for 3D

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Gaussian curve | BLUE | ParametricFunction |
| Gaussian surface | Default | ParametricSurface default shading |
| Cylinder shell | ORANGE/RED | checkerboard_colors, fill_opacity=1 |
| Unwrapped cylinder | ORANGE/RED | Same checkerboard |
| Riemann sums | RED | fill_opacity=0.3, stroke_opacity=0.3 |
| Top dimension line | YELLOW | stroke_width=5, label "2*pi*r" |
| Side dimension line | GREEN | stroke_width=5, label "e^{-r^2}" |
| Variable r | YELLOW | tex_to_color_map |
| Variable e | RED | tex_to_color_map |
| Integral bounds | GREEN | tex_to_color_map |
| Variable u | YELLOW | Substitution variable |
| Variable I | YELLOW | The integral value |
| Error function | GREEN | FunctionGraph of erf(x) |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Surface write | ~2s | Write(surface) |
| Ambient rotation | 5-15s | begin_ambient_camera_rotation() |
| Cylinder write | run_time=3 | Write(cylinder) |
| Cylinder unwrap | run_time=3 | ReplacementTransform |
| Camera move | ~2s | move_camera() |
| Dimension labels | ~1s each | ShowCreation + FadeInFrom |
| Equation transforms | ~1s each | 7 steps for I^2 derivation |
| Volume derivation | ~1s each | 5 steps (substitution) |
| Total | ~3-4 minutes | Multiple scenes |

## Patterns

### Pattern: Custom Cylinder and Unwrapped Cylinder Mobjects

**What**: Cylinder extends Sphere by overriding `func(u,v)` to produce a cylindrical surface. UnwrappedCylinder maps the same parametric space to a flat rectangle. Using ReplacementTransform between them creates a smooth "unwrapping" animation that reveals the cylinder's surface area as a rectangle.

**When to use**: Shell method for volumes of revolution, surface area computation, any transformation where a curved surface needs to flatten for analysis. Also applicable for sphere-to-Mercator projection demonstrations.

```python
# Source: projects/vivek3141_videos/gaussian.py:4-20
class Cylinder(Sphere):
    def func(self, u, v):
        return np.array([
            np.cos(u),
            np.sin(u),
            v
        ])

class UnwrappedCylinder(Cylinder):
    def func(self, u, v):
        return np.array([
            v - PI,
            -self.radius,
            np.abs(np.cos(u))
        ])
```

### Pattern: SpecialThreeDScene with Ghost Surface

**What**: A GaussianScene base class extending SpecialThreeDScene with helper methods for 3D visualization: `get_cylinder()` creates cylinders with sphere_config, `get_ghost_surface()` creates semi-transparent copies for overlay, `project_point()` projects points onto a cylinder surface. This provides reusable 3D infrastructure.

**When to use**: Any 3D mathematical visualization needing cylinder shells, ghost overlays, or point projection -- volumes of revolution, surface integrals, solid geometry.

```python
# Source: projects/vivek3141_videos/gaussian.py:389-434
class GaussianScene(SpecialThreeDScene):
    CONFIG = {
        "cap_config": {
            "stroke_width": 1, "stroke_color": WHITE,
            "fill_color": BLUE_D, "fill_opacity": 1,
        }
    }

    def get_ghost_surface(self, surface):
        result = surface.copy()
        result.set_fill(BLUE_E, opacity=0.5)
        result.set_stroke(WHITE, width=0.5, opacity=0.5)
        return result

    def project_point(self, point):
        radius = self.sphere_config["radius"]
        result = np.array(point)
        result[:2] = normalize(result[:2]) * radius
        return result
```

### Pattern: I-Squared Trick via Equation Chain with Brace Labels

**What**: Shows that I^2 = (integral e^{-x^2} dx)^2 = double integral e^{-(x^2+y^2)} dxdy by factoring e^{-x^2} * e^{-y^2}. The two single integrals are labeled with Brace -> "I" in yellow. Then I^2 = pi is derived, giving I = sqrt(pi). Seven Transform steps, each equation at scale=2.

**When to use**: The Gaussian integral proof specifically, but the pattern of labeling sub-expressions with Brace and then combining them applies to any algebraic factoring or product derivation.

```python
# Source: projects/vivek3141_videos/gaussian.py:151-246
eq6 = TexMobject(
    r"\int_{-\infty}^{\infty}e^{-x^2} \ dx",
    r"\int_{-\infty}^{\infty} e^{-y^2} \ dy")
eq6.shift(ORIGIN).scale(2)

br1 = Brace(eq6[0])
t1 = br1.get_text("I").scale(2).set_color(YELLOW)
b1 = VGroup(br1, t1)

br2 = Brace(eq6[1])
t2 = br2.get_text("I").scale(2).set_color(YELLOW)
b2 = VGroup(br2, t2)

self.play(Transform(eq2, eq6))
self.play(Write(b1), Write(b2))
# Then: Uncreate braces, Transform to I^2 = pi
```

## Scene Flow

1. **Intro** (0-10s): Gaussian curve e^{-x^2} with Riemann sum shading. Equation transforms from f(x) to integral = sqrt(pi).
2. **DefiniteIntegral** (10-20s): Contrast with a normal definite integral (x^2 from 1 to 2 = 7/3) that has a closed form.
3. **Nonelem** (20-25s): Brace under integral e^{-x^2} dx labeled "Nonelementary" -- no closed antiderivative.
4. **Gaussian** (25-50s): I^2 trick. Seven equation transforms: I -> double integral -> factor -> separate -> Brace label -> I^2 = integral -> I = sqrt(integral).
5. **ThreeFunc** (50-60s): 3D Gaussian surface with ambient rotation.
6. **GaussianVisual** (60-80s): Cylinder shell on surface. Surface fades to 0.75 opacity. Cylinder unwraps to rectangle. Dimension labels: 2*pi*r (YELLOW), e^{-r^2} (GREEN).
7. **Volume** (80-100s): Integrate 2*pi*r*e^{-r^2} dr via u=r^2 substitution. Result = pi. Therefore I = sqrt(pi).
8. **Erf** (100-110s): Error function erf(x) = (1/sqrt(pi)) * integral_{-x}^{x} e^{-t^2} dt plotted in GREEN.

> Full file: `projects/vivek3141_videos/gaussian.py` (729 lines)
