---
source: https://github.com/3b1b/videos/blob/main/_2021/newton_fractal.py
project: 3blue1brown
domain: [complex_analysis, fractal, calculus, number_theory, algorithms, mathematics]
elements: [complex_plane, dot, function_plot, axes, label, equation, formula, pixel_grid, image, arrow]
animations: [write, fade_in, fade_out, draw, transform, replacement_transform, highlight, color_change, animate_parameter, zoom_in, camera_rotate]
layouts: [centered, side_by_side, edge_anchored]
techniques: [shader_custom, custom_mobject, value_tracker, three_d_camera, moving_camera, helper_function, color_gradient, progressive_disclosure]
purpose: [exploration, demonstration, derivation, step_by_step]
mobjects: [Mobject, NumberPlane, ComplexPlane, Axes, VGroup, OldTex, OldTexText, Text, Dot, GlowDot, DecimalNumber, ImageMobject, SurroundingRectangle, SVGMobject, VMobject, DotCloud, Line, Arrow, ParametricCurve, Sphere, SurfaceMesh, ThreeDAxes, Mortimer, Randolph]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, FadeTransform, GrowArrow, LaggedStartMap, LaggedStart, ShowIncreasingSubsets, ShowSubmobjectsOneByOne, ShowCreationThenDestruction, TransformFromCopy, ChangeDecimalToValue, VFadeInThenOut, Rotate, UpdateFromAlphaFunc, ApplyMethod, MoveAlongPath]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 5119
scene_classes: [NewtonFractal, MetaNewtonFractal, AmbientRootFinding, PragmaticOrigins, SeekingRoots, AskAboutComplexity, WhoCares, SphereExample, ExamplePixels, CurvesDefiningFonts, RasterizingBezier, WriteThisIsPolynomial, DontWorryAboutDetails, ShowManyGraphs, ComingVideoWrapper, QuinticAppletPlay, AskAboutFractals, RealNewtonsMethod, FasterNewtonExample, AssumingItsGood, PauseAndPonder, AltPauseAndPonder, WhatIsThis, GutCheckFormula, HistoryWithNewton, CalcHomework, RealNewtonsMethodHigherGraph, FactorPolynomial, TransitionToComplexPlane]
---

## Summary

Comprehensive visualization of Newton's method and Newton fractals. Implements a custom shader-based `NewtonFractal` Mobject that renders the fractal in real-time on the GPU by coloring each pixel based on which polynomial root Newton's method converges to. Covers the progression from real root-finding (graphical Newton's method on polynomial curves) to complex plane fractals, including interactive root dragging and the meta-Newton fractal (parameter space). Also includes Bezier curve rasterization and font rendering as practical polynomial applications.

## Design Decisions

- **Custom shader Mobject for fractal rendering**: The `NewtonFractal` class passes polynomial coefficients and root positions as uniforms to a GPU shader, avoiding per-pixel Python computation. This enables real-time interaction and smooth animations of root positions.
- **Five root colors (viridis-like)**: `ROOT_COLORS_DEEP = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]` chosen for perceptual distinctness and aesthetics. Bright variants used for UI elements.
- **GlowDot for root markers**: Custom `glow_dot` function creates concentric fading dots (n=20 layers) for a soft, luminous root indicator on the complex plane.
- **Real Newton's method first**: The video starts with familiar 1D calculus (graph + tangent line) before transitioning to the complex plane, building conceptual scaffolding.
- **Rasterization digression**: Shows Bezier curves defining fonts and rasterization to pixels, connecting polynomial root-finding to everyday computer graphics.
- **CONFIG dict pattern**: Uses manimlib's CONFIG class attribute for shader configuration, with methods like `set_coefs`, `set_roots`, `set_n_steps` for animation.

## Composition

- **PragmaticOrigins**: NumberPlane `(-3,3), (-4,4)`, width=6, height=8, set_height(5.0), to_corner(DL). Root equations to the RIGHT of axes.
- **RealNewtonsMethod**: Full-width axes with graph, tangent line, and root approximation dots.
- **NewtonFractal**: Replaces a ComplexPlane, stretching to fill the plane bounds.
- **CurvesDefiningFonts**: Camera zooms from full text to individual Bezier curve on a single letter.
- **RasterizingBezier**: Pixel grid 90x160 (halved), overlaid on SVG curve.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Root colors (deep) | #440154, #3b528b, #21908c, #5dc963, #29abca | Viridis-inspired for fractal regions |
| Root colors (bright) | RED, GREEN, BLUE, YELLOW, MAROON_B | For UI elements and root labels |
| Cubic colors | RED_E, TEAL_E, BLUE_E | Three-root polynomials |
| GlowDot | YELLOW | 20 concentric dots, opacity = 1/n |
| Graph | BLUE | stroke_width varies: [0, *50*[4], 0] for tapered ends |
| Root decimal values | YELLOW | DecimalNumber, 3 decimal places |
| Bezier control points | BLUE | Dot, radius=0.005 |
| Bezier control lines | YELLOW | stroke_width=0.25 |
| Rasterized pixels | YELLOW | fill_opacity based on distance to curve |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Graph ShowCreation | 4s | rate_func=linear, with root FadeIn synced to alphas |
| ShowCreation underline | default | Styled with variable stroke width |
| Fractal n_steps animation | 10s | Animates from 0 to 300 steps, rate_func=a^3 |
| Camera zoom on font | 5s | From full text to single character |
| Rasterization sweep | 4s | ShowCreation with lag_ratio=10/len(pixels) |
| Font curve trace | 2s | ShowCreationThenDestruction |

## Patterns

### Pattern: Custom Shader Fractal Mobject

**What**: A Mobject subclass that renders Newton's fractal via GPU shaders. Polynomial coefficients, root positions, iteration count, and per-root colors are passed as uniforms. The fractal updates in real-time when roots are animated.

**When to use**: Any pixel-level mathematical visualization requiring GPU acceleration: Julia sets, Mandelbrot sets, distance fields, domain coloring of complex functions. Any scenario where per-pixel computation makes Python-side rendering impractical.

```python
# Source: projects/videos/_2021/newton_fractal.py:72-172
class NewtonFractal(Mobject):
    CONFIG = {
        "shader_folder": "newton_fractal",
        "colors": ROOT_COLORS_DEEP,
        "coefs": [1.0, -1.0, 1.0, 0.0, 0.0, 1.0],
        "n_steps": 30,
        "max_degree": 5,
    }

    def __init__(self, plane, **kwargs):
        super().__init__(
            scale_factor=plane.get_x_unit_size(),
            offset=plane.n2p(0),
            **kwargs,
        )
        self.replace(plane, stretch=True)

    def set_coefs(self, coefs, reset_roots=True):
        full_coefs = [*coefs] + [0] * (self.max_degree - len(coefs) + 1)
        self.uniforms.update({
            f"coef{n}": np.array([coef.real, coef.imag], dtype=np.float64)
            for n, coef in enumerate(map(complex, full_coefs))
        })
        if reset_roots:
            self.set_roots(coefficients_to_roots(coefs), False)
```

### Pattern: GlowDot with Concentric Fading Layers

**What**: Creates a soft-glowing dot effect using n concentric Dot objects with linearly interpolated radii and uniformly distributed opacity (total opacity = opacity_mult).

**When to use**: Marking special points on complex planes, highlighting roots or critical points, any scenario where a standard dot is too harsh and you want a luminous/ethereal marker.

```python
# Source: projects/videos/_2021/newton_fractal.py:14-20
def glow_dot(point, r_min=0.05, r_max=0.15, color=YELLOW, n=20, opacity_mult=1.0):
    result = VGroup(*(
        Dot(point, radius=interpolate(r_min, r_max, a))
        for a in np.linspace(0, 1, n)
    ))
    result.set_fill(color, opacity=opacity_mult / n)
    return result
```

### Pattern: Synced Graph Creation with Root Emergence

**What**: A polynomial graph is drawn with ShowCreation while root dots FadeIn at the exact moment the graph passes each root, using `squish_rate_func(rush_from, alpha, alpha+0.2)` keyed to each root's x-position along the curve.

**When to use**: Any function graph where special points (roots, extrema, intersections) should appear precisely when the drawing reaches them, creating a discovery narrative.

```python
# Source: projects/videos/_2021/newton_fractal.py:293-304
alphas = [inverse_interpolate(*graph_x_range, root) for root in roots]
self.play(
    ShowCreation(graph, rate_func=linear),
    *(
        FadeIn(rg, rate_func=squish_rate_func(rush_from, a, min(a + 0.2, 1)))
        for rg, a in zip(root_groups, alphas)
    ),
    run_time=4,
)
```

### Pattern: Pixel Distance-Based Rasterization

**What**: Fills a grid of pixel squares with opacity proportional to their distance from a parametric curve, simulating rasterization. Each pixel precomputes its minimum distance to curve samples, then a ValueTracker controls the "stroke width" threshold.

**When to use**: Font rendering demonstrations, anti-aliasing explanations, signed distance field visualizations, showing how continuous curves become discrete pixels.

```python
# Source: projects/videos/_2021/newton_fractal.py:669-688
samples = np.array([curve.pfp(x) for x in np.linspace(0, 1, 100)])
for pixel in pixels:
    diffs = samples - pixel.get_center()
    dists = np.apply_along_axis(lambda p: np.dot(p, p), 1, diffs)
    pixel.dist = dists[np.argmin(dists)]

def update_pixels(pixels):
    for pixel in pixels:
        pixel.set_fill(YELLOW, 0.5 * clip(10 * (get_sw() - pixel.dist), 0, 1))
```

## Scene Flow

1. **PragmaticOrigins** (0-30s): Polynomial graph on axes with title "Pragmatic origins". Graph created with ShowCreation, roots emerge as yellow GlowDots synced to graph drawing.
2. **CurvesDefiningFonts** (30-90s): Text "When a computer renders text..." appears. Camera zooms to single letter, showing Bezier control points and lines. Quadratic Bezier equation shown.
3. **RasterizingBezier** (90-150s): Pixel grid overlaid on Bezier curve. Distance-based rasterization shown. Stroke width animated via ValueTracker.
4. **RealNewtonsMethod** (150-300s): 1D Newton's method on polynomial graph. Tangent lines, convergence dots, step-by-step iteration.
5. **TransitionToComplexPlane**: Newton's method extended to complex numbers. NewtonFractal Mobject renders the fractal. Roots can be dragged interactively. n_steps animated from 0 to 300.
