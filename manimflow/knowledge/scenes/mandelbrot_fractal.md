---
source: https://github.com/vivek3141/videos/blob/main/mandelbrot.py
project: vivek3141_videos
domain: [mathematics, complex_analysis, fractal, number_theory, calculus]
elements: [complex_plane, dot, label, equation, line, axes, function_plot, dashed_line]
animations: [write, fade_in, fade_out, transform, animate_parameter, indicate]
layouts: [centered, side_by_side, dual_panel]
techniques: [shader_custom, value_tracker, add_updater, custom_mobject, progressive_disclosure]
purpose: [exploration, demonstration, derivation, step_by_step]
mobjects: [ComplexPlane, MandelbrotSet, Dot, VGroup, Tex, TexText, ValueTracker, Line, Axes, ParametricFunction, Brace, ScreenRectangle, Polygon, Arrow]
manim_animations: [Write, FadeIn, FadeOut, Transform, TransformFromCopy, TransformMatchingTex, ShowCreation, Uncreate, FocusOn, Indicate]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 908
scene_classes: [MandelbrotTest, Intro, MandelbrotIntro, ExpIntro, Exp2, TitleScene, TitleU, TitleC, TitleW, TitleA, Thumb]
---

## Summary

Visualizes the Mandelbrot set using GPU shaders via a custom Mobject that renders the fractal directly on the complex plane. The core innovation is a `MandelbrotSet` class that passes iteration parameters (num_steps, max_arg, color_style) as shader uniforms, enabling real-time parameter animation. Scenes demonstrate the iterative process z -> z^2 + c by tracing orbit paths on the complex plane, building a table linking epsilon values to pi digits, and showing cobweb diagrams on parabolas to explain fixed-point behavior near the boundary.

## Design Decisions

- **GPU shader rendering for the fractal**: The Mandelbrot set is rendered entirely on the GPU via custom GLSL shaders, not as a pixel grid of Dots. This enables smooth zooming and real-time parameter changes without Python-side recomputation. The shader folder is `shaders/mandelbrot`.
- **ValueTracker-driven iteration count**: The number of iteration steps is animated via a ValueTracker, so the fractal "grows" from coarse (1 step) to detailed (100 steps). This reveals the fractal structure progressively.
- **Split-screen layout for equation + fractal**: The complex plane with the Mandelbrot set occupies the left side, while equations and iteration tables occupy the right. A black Polygon masks the dividing line cleanly.
- **Orbit visualization with lines and dots**: For a given c value, the orbit z_0, z_1, z_2... is shown as orange dots connected by semi-transparent lines on the complex plane. This makes the divergence/convergence behavior tangible.
- **Cobweb diagram on parabola**: The fixed-point behavior near c=0.25 is visualized using a cobweb (staircase) diagram: vertical line to parabola, horizontal line to y=x, repeat. Blue lines on red parabola. This is the standard dynamical systems visualization.
- **Epsilon-to-pi table**: A table correlating epsilon values with iteration counts reveals that the number of steps follows pi (3, 33, 315, 3143...). The table builds incrementally, with the first entries animated individually and later entries fading in together.
- **Pastel color palette**: Uses a distinctive pastel palette (A_AQUA, A_YELLOW, A_LAVENDER, A_RED, A_BLUE, A_ORANGE, A_GREEN, A_PINK) consistently across all equations via tex_to_color_map.

## Composition

- **Complex plane**: `ComplexPlane(x_range=(-3, 2), y_range=(-1, 1))`, scaled 4x for full-screen display
- **Mandelbrot overlay**: `MandelbrotSet(plane, opacity=0.75)` stretches to fill the plane
- **Split layout**: Black masking Polygon from x=0.77 to FRAME_WIDTH/2, creating left (fractal) and right (equations) panels
- **Equation positioning**: Equations at `3 * UP + 3.93 * RIGHT` (center of right panel)
- **Iteration steps**: Spaced vertically at `1.25 * DOWN` intervals from equation
- **Cobweb diagram**: Axes with x_range=(-1, 1, 0.5), y_range=(0, 1, 0.5), scaled 0.95, shifted 0.3 * DOWN
- **Epsilon table**: Two columns (epsilon, num_steps) with 0.65 unit vertical spacing, positioned under header labels

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Mandelbrot set | GPU-rendered | color_style=0 or 1 (two palettes) |
| Function f | A_GREEN (#b3de69) | In tex_to_color_map |
| Variable z | A_PINK (#fccde5) | In tex_to_color_map |
| Constants/numbers | A_YELLOW (#ffffb3) | In tex_to_color_map |
| Epsilon | A_LAVENDER (#bebada) | In tex_to_color_map |
| Orbit dots | A_ORANGE (#fdb462) | Dot radius=0.1 |
| Orbit lines | WHITE | stroke_opacity=0.5 |
| Cobweb lines | A_BLUE (#80b1d3) | stroke_width=6 |
| Parabola | A_RED (#fb8072) | stroke_width=6 |
| Selected point | A_RED (#fb8072) | Dot with label |
| Tangent highlight | A_AQUA (#8dd3c7) | Partial curve tracing |
| Y=x line | WHITE | Default graph color |

Color strategy: Pastel palette assigns semantic roles consistently. Green=function, pink=variable, yellow=constants, lavender=parameters. This mapping persists across all scenes in the file.

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Mandelbrot iteration growth | run_time=5 | ValueTracker 1->100 |
| Orbit animation per step | ~1s each | First 10 steps individually |
| Remaining orbit steps | 1/(num_steps-10) each | Accelerates after step 10 |
| Epsilon sweep | run_time=7.5 | ValueTracker 0->1 for imaginary part |
| Cobweb trace | run_time=10 | ValueTracker 0->arctan(4) |
| Table entries (first 3) | ~2s each | Individual animation |
| Table entries (remaining) | FadeIn batch | All at once |
| Total per main scene | ~60-90s | MandelbrotIntro is longest |

## Patterns

### Pattern: Custom Shader Mobject for GPU Rendering

**What**: A Mobject subclass that renders via custom GLSL shaders. The `MandelbrotSet` class passes parameters (scale_factor, offset, num_steps, max_arg, color_style) as shader uniforms. The shader folder contains vertex/fragment shaders that compute the fractal per-pixel on the GPU. The Mobject stretches to fill a ComplexPlane using `self.replace(plane, stretch=True)`.

**When to use**: Any visualization requiring per-pixel computation that would be too slow in Python -- fractals (Julia sets, Burning Ship), complex function coloring, domain coloring, heat maps, ray marching. Also useful for real-time parameter animation of computationally expensive visuals.

```python
# Source: projects/vivek3141_videos/mandelbrot.py:32-64
class MandelbrotSet(Mobject):
    CONFIG = {
        "shader_folder": "shaders/mandelbrot",
        "num_steps": 100,
        "max_arg": 2.0,
        "color_style": 0
    }

    def __init__(self, plane, **kwargs):
        super().__init__(
            scale_factor=plane.get_x_unit_size(),
            offset=plane.n2p(0),
            **kwargs,
        )
        self.replace(plane, stretch=True)

    def init_uniforms(self):
        super().init_uniforms()
        self.uniforms["scale_factor"] = self.scale_factor
        self.uniforms["opacity"] = self.opacity
        self.uniforms["num_steps"] = float(self.num_steps)
        self.uniforms["max_arg"] = float(self.max_arg)
        self.uniforms["offset"] = self.offset
        self.uniforms["color_style"] = float(self.color_style)

    def init_data(self):
        super().init_data()
        self.data["points"] = np.array([UL, DL, UR, DR])
```

### Pattern: Animated Shader Parameters via ValueTracker + Updater

**What**: Animate a shader Mobject's parameters by attaching an updater that reconstructs the Mobject each frame with new uniform values from a ValueTracker. Since shader uniforms cannot be directly animated, the updater creates a fresh MandelbrotSet and calls `become()` on each frame.

**When to use**: Animating any custom shader parameter -- iteration count, zoom level, color palette, threshold values. Also works for any Mobject where you need to reconstruct it each frame based on a changing parameter.

```python
# Source: projects/vivek3141_videos/mandelbrot.py:79-89
c = ComplexPlane(x_range=(-3, 2), y_range=(-1, 1))
c.scale(4)
m = MandelbrotSet(c, opacity=0.75)
v = ValueTracker(1)

def m_updater(m, v=v, c=c):
    m_ = MandelbrotSet(c, opacity=0.75, num_steps=v.get_value())
    m.become(m_)
m.add_updater(m_updater)

self.add(c, m)
self.play(v.increment_value, 100, run_time=5)
```

### Pattern: Cobweb (Staircase) Diagram for Iteration Visualization

**What**: Draws a cobweb diagram showing the iteration of f(z) = z^2 + c. From a starting point, draw a vertical line to the parabola, then a horizontal line to y=x, then vertical to parabola again. The resulting staircase pattern shows convergence (spiral inward) or divergence (spiral outward). Lines are stored as a VGroup and animated with updaters.

**When to use**: Fixed-point iteration visualization, dynamical systems, Newton's method convergence, logistic map analysis, any iterative process where you want to show convergence/divergence graphically.

```python
# Source: projects/vivek3141_videos/mandelbrot.py:594-613
def get_bounce_lines(self, axes, num_steps=20, offset=0.25,
                     start_coord=(0, 0), max_arg=1.0):
    curr, f = 0, lambda z: z**2 + offset
    x, y = start_coord
    path = VGroup()
    for _ in range(num_steps):
        if curr > max_arg:
            break
        path.add(Line(
            axes.c2p(x + curr, y + curr),
            axes.c2p(x + curr, y + f(curr)),
            color=A_BLUE, stroke_width=6))
        path.add(Line(
            axes.c2p(x + curr, y + f(curr)),
            axes.c2p(x + f(curr), y + f(curr)),
            color=A_BLUE, stroke_width=6))
        curr = f(curr)
    return path
```

### Pattern: Orbit Trace on Complex Plane

**What**: Shows the iteration orbit of z -> z^2 + c as connected dots on a ComplexPlane. Orange dots mark each z_n value, semi-transparent lines connect consecutive iterates. A helper function generates the full orbit VGroup given a starting point and plane. The dot at position z is labeled with its complex value using a background rectangle for readability.

**When to use**: Complex dynamics visualization, iteration sequences on the complex plane, orbit analysis for Julia sets or Mandelbrot set, any iterative map where you want to trace the sequence of values.

```python
# Source: projects/vivek3141_videos/mandelbrot.py:363-376
def get_mandel_lines(self, point, c, steps=15, max_arg=10000):
    curr, prev = point, 0
    grp = VGroup()
    for i in range(steps):
        grp.add_to_back(
            Line(c.n2p(curr), c.n2p(prev), stroke_opacity=0.5))
        grp.add(Dot(c.n2p(prev), color=A_ORANGE))
        if abs(curr) < max_arg:
            curr, prev = (lambda z: z**2 + point)(curr), curr
        else:
            break
    return grp

def get_dot_grp(self, z, c, conv=int, color=A_ORANGE, radius=0.1):
    d_ = Dot(c.n2p(z), color=color, radius=radius)
    return VGroup(
        d_,
        Tex(c_to_str(z, conv)).next_to(d_, DOWN)
            .add_background_rectangle(buff=0.075),
    )
```

## Scene Flow

1. **Intro** (0-8s): ComplexPlane appears with Mandelbrot set at opacity 0.75. ValueTracker animates iteration count from 1 to 100 over 5 seconds, revealing fractal detail progressively.
2. **MandelbrotIntro** (8-90s): Split-screen layout. Left: complex plane with Mandelbrot set. Right: equation f(z) = z^2 + c. Iterates shown for c = -1+i (diverges). Then c = -0.25+0.25i (converges). Orbit dots and connecting lines trace the iteration path. Table reveals epsilon-to-pi connection with incrementally building rows.
3. **ExpIntro** (90-150s): Cobweb diagram on parabola y = x^2 + 0.25. Dot traces the staircase pattern. ValueTracker animates epsilon perturbation, showing how the cobweb behavior changes near the bifurcation point. Brace labels the period as pi/sqrt(epsilon).
4. **Exp2** (150-200s): Algebraic derivation from discrete to continuous. Integral dz/(z^2+epsilon) = dn leads to arctan solution. Tangent function plotted on axes, partial curve traced with ValueTracker.

> Full file: `projects/vivek3141_videos/mandelbrot.py` (908 lines)
