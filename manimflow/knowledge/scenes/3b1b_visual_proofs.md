---
source: https://github.com/3b1b/videos/blob/main/_2022/visual_proofs/lies.py
project: 3blue1brown
domain: [geometry, calculus, topology, mathematics]
elements: [surface_3d, sphere, label, equation, formula, line, dashed_line, arrow, surrounding_rect, brace, dot]
animations: [write, transform, fade_in, fade_out, draw, rotate, zoom_in, flash, highlight, replacement_transform, transform_from_copy, camera_rotate]
layouts: [centered, side_by_side, vertical_stack]
techniques: [three_d_camera, value_tracker, always_redraw, moving_camera, custom_mobject, progressive_disclosure, helper_function]
purpose: [proof, demonstration, step_by_step, exploration, analogy]
mobjects: [ParametricSurface, Circle, Polygon, Triangle, Rectangle, Square, VGroup, Group, OldTex, OldTexText, Text, Line, Arc, NumberLine, SurroundingRectangle, Brace, Underline, Dot, VMobject, TexturedSurface, Sphere, SurfaceMesh, Mortimer, Randolph]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, DrawBorderThenFill, LaggedStartMap, ReplacementTransform, FadeTransform, FadeTransformPieces, TransformFromCopy, WiggleOutThenIn, VShowPassingFlash, ShowCreationThenFadeOut, Rotate, GrowFromCenter]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 2368
scene_classes: [PreviewThreeExamples, Intro, SimpleSphereQuestion, SphereExample, SphereExample50, SphereExample100, CallOutSphereExampleAsWrong, SomethingSomethingLimits, PiEqualsFourOverlay, Proof2Slide, CircleExample, SideBySide, SphereSectorAnalysis, FalseVsTrueSurfaceAreaOverlay, FakeAreaManipulation, ContrastSphericalGeometry, GiveItAGo, SquareCircleExample, ObviouslyWrong, UpshotOfLimitExample, WhyWeNeedProofs, Proof3Slide, SpeakingOfLimits, IntegralExample, IntegralError, DefiningTheLengthOfACurve, FalseEuclidProofAnnotation, FalseEuclidFollowup, TryToFindFault, SideSumTruthiness, PythagoreanProofSketch, LastSideBySide, ByTheWay]
---

## Summary

Explores three famous false visual proofs of increasing subtlety: the sphere surface area "proof" that pi^2*R^2, the staircase "proof" that pi=4, and the Euclidean "proof" that all triangles are isosceles. Uses 3D sphere slicing with ParametricSurface objects that flatten into 2D, circle rolling on a number line with real-time circumference tracking, and detailed geometric constructions. The core visual technique is showing plausible-looking manipulations where the error is hard to spot.

## Design Decisions

- **Three examples of increasing subtlety**: Arranged left-to-right with an "Increasingly subtle" arrow, priming the viewer that each proof hides its flaw better.
- **3D sphere slicing into flattened triangles**: Sphere is cut into longitudinal wedges (ParametricSurface) that animate to flat 2D triangular strips, making the false area calculation feel convincing.
- **ValueTracker-driven width line**: A red line sweeps down each flattened slice, showing the sinusoidal width variation that the false proof ignores.
- **Circle rolling on number line**: Real-time circumference measurement via a yellow arc that unrolls as the circle translates, with a radial line tracking rotation.
- **Color-coded sphere components**: BLUE_D/BLUE_E alternating for hemisphere slices, TEAL for equator, RED for edge measurements, YELLOW for highlighting.
- **Pi creature reactions**: Mortimer and Randolph react to the proofs, grounding abstract math in character-driven storytelling.

## Composition

- **PreviewThreeExamples**: 3 rectangles (3.5 x 4.5) arranged RIGHT with buff=0.75, to_edge(DOWN, buff=0.25). Titles above.
- **SphereExample**: 3D scene with focal_distance=100, light at [-10, 2, 5]. Sphere radius=2.5 with textured surface.
- **Flattened slices**: Centered, with equator as Line at bottom.
- **Proof2Slide**: Circle radius=1.25, number line (0, 4) with width = 4 * circle width, positioned at 2*DOWN.
- **CircleExample**: Circle radius=2.0, centered.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Sphere slices (even) | BLUE_D | Alternating |
| Sphere slices (odd) | BLUE_E | Alternating |
| Equator | TEAL | stroke_width=2 |
| Width measurement line | RED | stroke_width=3 |
| Edge/arc measurement | PINK | stroke_width=2 |
| Circumference formula | default | OldTex |
| Circle (pi=4) | BLUE_E | fill_opacity=1, stroke_width=0 |
| Circumference tracker | YELLOW | stroke_width=2 |
| Highlight rects | YELLOW | SurroundingRectangle, stroke_width=2 |
| "Increasingly subtle" text | YELLOW | font_size=72 |
| Arrow gradient | YELLOW | stroke_opacity=(0.5, 0.9, 1) |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| DrawBorderThenFill rects | lag_ratio=0.3 | LaggedStartMap |
| Sphere unfold | 2s | Transform for each hemisphere |
| Width line sweep | 3s each way | ValueTracker 0->1 and 1->0 |
| Circle roll | 4s | rate_func=linear |
| VShowPassingFlash | 1.5s | time_width=1.5 for equator highlight |
| Total video | ~15 min | Many scenes |

## Patterns

### Pattern: Sphere Slice to Flat Strip Transformation

**What**: Creates longitudinal sphere slices as ParametricSurface objects, then transforms them into flat 2D triangular strips. Uses helper functions to generate both 3D and flat versions with matching coloring, then animates the Transform between them.

**When to use**: Any 3D-to-2D unfolding visualization: sphere projections, map projections, surface area derivations, paper folding/unfolding, manifold flattening demonstrations.

```python
# Source: projects/videos/_2022/visual_proofs/lies.py:7-52
def get_sphere_slices(radius=1.0, n_slices=20):
    delta_theta = TAU / n_slices
    north_slices = Group(*(
        ParametricSurface(
            uv_func=lambda u, v: [
                radius * math.sin(v) * math.cos(u),
                radius * math.sin(v) * math.sin(u),
                radius * math.cos(v),
            ],
            u_range=[theta, theta + delta_theta],
            v_range=[0, PI / 2],
            resolution=(4, 25),
        )
        for theta in np.arange(0, TAU, delta_theta)
    ))
    # ... returns Group(north_slices, south_slices, equator)

def get_flattened_slices(radius=1.0, n_slices=20):
    slc = ParametricSurface(
        lambda u, v: [u * math.sin(v * PI / 2), 1 - v, 0],
        u_range=[-1, 1], v_range=[0, 1],
    )
    # Grid of n_slices, colored alternating BLUE_D/BLUE_E
```

### Pattern: Rolling Circle with Real-Time Arc Decomposition

**What**: A circle translates along a number line while a ValueTracker drives both its position and a dynamic arc/line that shows the circumference unrolling. A radial line tracks rotation angle. The arc decomposes into already-unrolled line + remaining arc.

**When to use**: Circumference measurement, cycloid generation, rolling-without-slipping physics, any visualization connecting circular motion to linear distance.

```python
# Source: projects/videos/_2022/visual_proofs/lies.py:453-457
def update_circum(circum):
    line = Line(nl.n2p(0), nl.n2p(get_t() * 4))
    arc = Arc(start_angle=-TAU / 4, angle=TAU * (1 - get_t()), radius=radius)
    arc.shift(circle.get_bottom() - arc.get_start())
    circum.set_points(np.vstack([line.get_points(), arc.get_points()]))
circum.add_updater(update_circum)
```

### Pattern: ValueTracker Width Line Sweep

**What**: A horizontal line whose width follows a sinusoidal profile as it sweeps vertically across a flattened slice, driven by a ValueTracker from 0 to 1. Shows how slice width varies with latitude.

**When to use**: Demonstrating cross-sectional variation in geometric objects, showing how a function's value changes along a parameter, sweeping measurements across shapes.

```python
# Source: projects/videos/_2022/visual_proofs/lies.py:247-256
v_tracker = ValueTracker(0)
width_line = Line(LEFT, RIGHT).set_stroke(RED, 3)

def update_width_line(width_line, slc=slc, v_tracker=v_tracker):
    v = v_tracker.get_value()
    width_line.set_width(1.2 * slc.get_width() * math.sin(v) + 1e-2)
    width_line.move_to(interpolate(slc.get_top(), slc.get_bottom(), v))

width_line.add_updater(update_width_line)
self.play(v_tracker.animate.set_value(1), run_time=3)
```

## Scene Flow

1. **PreviewThreeExamples** (0-10s): Three preview rectangles appear with titles. "Increasingly subtle" arrow and label.
2. **SphereExample** (10-120s): Textured sphere shown, mesh drawn, sliced longitudinally. Slices flattened to 2D strips. Width line sweeps. Interlinked triangles shown. Equator = 2piR, arc height = pi/2 R. Area = pi^2 R^2 (wrong!).
3. **Proof2Slide** (120-180s): Circle on number line. Rolls from 0 to 4, circumference unrolls showing 2piR. Dashed vertical lines mark integer positions.
4. **CircleExample** (180-240s): Circle sliced into sectors that rearrange into approximate rectangle, deriving pi*r^2.
5. **FalseEuclidProofAnnotation** (later): Detailed geometric construction showing the subtle error in the "all triangles are isosceles" proof.
