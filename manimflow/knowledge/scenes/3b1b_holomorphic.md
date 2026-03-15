---
source: https://github.com/3b1b/videos/blob/main/_2021/holomorphic_dynamics.py
project: 3blue1brown
domain: [complex_analysis, fractal, calculus, mathematics]
elements: [complex_plane, function_plot, dot, arrow, label, equation, formula, image]
animations: [write, fade_in, fade_out, draw, transform, replacement_transform, animate_parameter, trace_path, move]
layouts: [centered, side_by_side, edge_anchored]
techniques: [shader_custom, custom_mobject, value_tracker, always_redraw, moving_camera, color_gradient, traced_path, progressive_disclosure]
purpose: [exploration, demonstration, definition, overview]
mobjects: [ComplexPlane, Dot, OldTex, OldTexText, Text, VGroup, DecimalNumber, Line, Arrow, VMobject, TracedPath, Square, Underline, SurroundingRectangle, Vector]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, FadeTransform, LaggedStartMap, LaggedStart, TransformFromCopy, FadeInFromPoint, Transform, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 3644
scene_classes: [MandelbrotFractal, JuliaFractal, MandelbrotSetPreview, HolomorphicDynamics, HolomorphicPreview, AmbientRepetition, AmbientRepetitionLimitPoint, AmbientRepetitionInfty, AmbientRepetitionChaos, Recap, RepeatedNewtonPlain, RationalFunctions, ShowFatouAndJulia, IveSeenThis, MandelbrotIntro, BenSparksVideoWrapper, AckoNet, ParameterSpaceVsSeedSpace, MandelbrotStill, JuliaStill, ClassicJuliaSetDemo, AskAboutGeneralTheory, NewtonRuleLabel, FixedPoints, UseNewton, DescribeDerivative, DescribeDerivativeInnerFrame, DescribeDerivativeIExample, DescribeDerivativeIExampleInnerFrame, LooksLikeTwoMult]
---

## Summary

Explores holomorphic dynamics -- the study of iterated complex functions -- connecting Newton's fractal to Mandelbrot and Julia sets. Implements `MandelbrotFractal` and `JuliaFractal` as shader-based Mobjects (extending the NewtonFractal class). Visualizes repeated function application on the complex plane with TracedPath orbits, shows the Mandelbrot set as a parameter space, Julia sets as seed spaces, and builds toward a unified theory of complex dynamical systems.

## Design Decisions

- **Mandelbrot color palette (9 colors)**: Deep blues to warm earth tones (`"#00065c"` through `"#573706"`), creating the classic Mandelbrot escape-time aesthetic with smooth gradients.
- **Shader-based fractal rendering**: Both MandelbrotFractal and JuliaFractal use GPU shaders for real-time rendering, with n_steps=300 for Mandelbrot (high detail) and n_steps=100 for Julia sets.
- **Parameter c displayed as dynamic label**: A yellow `c = ` label with DecimalNumber follows a draggable dot, updating in real-time to show the complex parameter value.
- **Iterated function as arrow chain**: In AmbientRepetition, each iteration step is shown as an arrow from z to f(z) with labeled points, making the iteration sequence tangible before introducing the fractal.
- **Color-coded iteration labels**: z_0 through z_3 use a blue-to-green gradient in tex_to_color_map, showing progression visually even in the formula.
- **Two-panel input/output for holomorphic functions**: HolomorphicPreview shows a tiny neighborhood in the input plane being mapped to the output plane, revealing that holomorphic functions locally look like scaling + rotation.

## Composition

- **MandelbrotSetPreview**: ComplexPlane `(-2, 1), (-2, 2)`, width=0.7*FRAME_WIDTH, with coordinate labels font_size=18
- **AmbientRepetition**: ComplexPlane `(-2, 2), (-2, 2)`, height=6, to_corner(DR, buff=SMALL_BUFF)
- **HolomorphicPreview**: Two ComplexPlanes `(-2, 2), (-2, 2)`, height=5, width=5, one to_corner(DL), one to_corner(DR)
- **Tiny neighborhood**: ComplexPlane height=0.5, width=0.5, moved to in_plane.c2p(1, 1)
- **HolomorphicDynamics title**: font_size=60, to_edge(UP), with variable-width underline

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Mandelbrot palette | #00065c to #573706 | 9-color escape-time gradient |
| z dot | BLUE | Starting point |
| f(z) dot | YELLOW | Iteration result |
| Arrow (iteration) | default | Between z and f(z) |
| c label | YELLOW | DecimalNumber with include_sign |
| TracedPath | default | stroke_width=1 |
| Title underline | YELLOW | Variable width: [1, *5*[3], 1] |
| f : C -> C | BLUE for C | tex_to_color_map |
| z variable | YELLOW | tex_to_color_map |
| Iteration labels | BLUE_C -> GREEN_D | z_0 blue, z_2 green |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Mandelbrot n_steps animation | 10s | rate_func=a^3, 0 to 300 steps |
| Iteration arrow + dot | 0.5s wait | Per step in AmbientRepetition |
| FadeOut previous iteration | default | Arrows and temp dots |
| Title underline ShowCreation | default | Single play |
| HolomorphicPreview mapping | 2s | TransformFromCopy of tiny_plane |
| Total video | ~20 min | Many scenes |

## Patterns

### Pattern: Mandelbrot/Julia Shader Fractals

**What**: Extends the NewtonFractal shader Mobject for escape-time fractals. MandelbrotFractal colors pixels by iteration count before escape, JuliaFractal fixes c and varies z_0. Both pass parameters as shader uniforms for real-time rendering and animation.

**When to use**: Any escape-time fractal visualization, parameter space exploration, Julia set families, any complex dynamical system where per-pixel iteration is needed.

```python
# Source: projects/videos/_2021/holomorphic_dynamics.py:66-110
class MandelbrotFractal(NewtonFractal):
    CONFIG = {
        "shader_folder": "mandelbrot_fractal",
        "colors": MANDELBROT_COLORS,
        "n_colors": 9,
        "parameter": complex(0, 0),
        "n_steps": 300,
        "mandelbrot": True,
    }

    def set_parameter(self, c):
        self.uniforms["parameter"] = np.array([c.real, c.imag])

class JuliaFractal(MandelbrotFractal):
    CONFIG = {"n_steps": 100, "mandelbrot": False}
    def set_c(self, c):
        self.set_parameter(c)
```

### Pattern: Iteration Visualization with Arrow Chain

**What**: Visualizes repeated function application on the complex plane. Each step shows an Arrow from current z to f(z), a TransformFromCopy of the dot, and labels. Previous steps fade out to keep focus on the current iteration. TracedPath records the orbit.

**When to use**: Fixed-point iteration, orbit diagrams, dynamical systems exploration, any iterative algorithm visualization on the complex plane or 2D space.

```python
# Source: projects/videos/_2021/holomorphic_dynamics.py:434-464
for n in range(self.n_steps):
    new_point = plane.n2p(func(plane.p2n(dot.get_center())))
    arrow = Arrow(dot.get_center(), new_point, buff=dot.get_height() / 2)
    dot_copy = dot.copy().move_to(new_point).set_color(YELLOW)
    fz_label = OldTex("f(z)", font_size=font_size)
    fz_label.next_to(dot_copy, normalize(new_point - dot.get_center()))

    self.play(
        ShowCreation(arrow),
        TransformFromCopy(dot, dot_copy),
        FadeInFromPoint(fz_label, z_label.get_center()),
    )
    # Fade old, update position
    dot.move_to(dot_copy)
    self.play(*map(FadeOut, to_fade), FadeIn(z_label))
```

### Pattern: Dynamic Parameter Label Following Dot

**What**: A `c = <value>` label that follows a movable dot and updates its DecimalNumber in real-time. Uses two updaters: one for positioning (`next_to`), one for value (`set_value`). Yellow color and black backstroke ensure readability over fractal backgrounds.

**When to use**: Any interactive parameter exploration, sliders, draggable points on complex planes, real-time function parameter display.

```python
# Source: projects/videos/_2021/holomorphic_dynamics.py:18-28
def get_c_dot_label(dot, get_c, font_size=24, direction=UP):
    c_label = VGroup(
        OldTex("c = ", font_size=font_size),
        DecimalNumber(get_c(), font_size=font_size, include_sign=True)
    ).arrange(RIGHT, buff=0.075)
    c_label.set_color(YELLOW)
    c_label.set_stroke(BLACK, 5, background=True)
    c_label.add_updater(lambda m: m.next_to(dot, direction, SMALL_BUFF))
    c_label.add_updater(lambda m: m[1].set_value(get_c()))
    return c_label
```

### Pattern: Holomorphic Function as Local Scale+Rotate

**What**: Shows a tiny grid neighborhood in an input complex plane, applies the function, and displays the result in an output plane. The nonlinear transform is applied via `apply_function`, revealing that locally it looks like scaling + rotation (the derivative as a complex number).

**When to use**: Complex function visualization, conformal mapping demonstrations, derivative interpretation in complex analysis, any explanation of why holomorphic = angle-preserving.

```python
# Source: projects/videos/_2021/holomorphic_dynamics.py:366-397
tiny_plane = ComplexPlane((-2, 2), (-2, 2), height=0.5, width=0.5)
tiny_plane.move_to(in_plane.c2p(1, 1))

tiny_plane_image = tiny_plane.copy()
tiny_plane_image.apply_function(
    lambda p: out_plane.n2p(f(in_plane.p2n(p)))
)
self.play(TransformFromCopy(tiny_plane, tiny_plane_image))
```

## Scene Flow

1. **HolomorphicDynamics** (0-120s): Title "Holomorphic Dynamics" with underline. Goals: Mandelbrot occurrences + tie up loose ends. Definition: f: C->C with f'(z) exists. Examples: z^2+1, e^z, sin(z). "Dynamics" = repeated application. Iteration chain z_0 -> z_1 -> ... shown. Three fractal types previewed: Newton, Mandelbrot, exponential.
2. **MandelbrotSetPreview** (120-150s): Mandelbrot fractal rendered by animating n_steps from 0 to 300.
3. **AmbientRepetition** (150-240s): Step-by-step iteration on complex plane. Arrow chain shows orbit converging, diverging, or cycling depending on c value.
4. **FixedPoints** (240-360s): Fixed point theory. Attracting vs repelling. Derivative magnitude determines behavior.
5. **ClassicJuliaSetDemo** (360-420s): Julia set shown for specific c values, connected to Mandelbrot parameter space.
