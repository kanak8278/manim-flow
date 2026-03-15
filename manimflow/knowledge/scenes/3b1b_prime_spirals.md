---
source: https://github.com/3b1b/videos/blob/main/_2019/spirals.py
project: videos
domain: [number_theory, mathematics, geometry]
elements: [axes, dot, label, number_line, coordinate_system, grid, pi_creature]
animations: [write, fade_in, fade_out, transform, replacement_transform, lagged_start, zoom_out, indicate]
layouts: [centered, radial, grid]
techniques: [custom_mobject, data_driven, progressive_disclosure, helper_function, moving_camera]
purpose: [exploration, demonstration, step_by_step, progression]
mobjects: [Axes, NumberPlane, VGroup, Square, PMobject, Dot, Integer, DecimalNumber, Line, Circle, OldTex, OldTexText, IntegerMatrix, Brace, Arc]
manim_animations: [FadeIn, FadeOut, ShowCreation, Write, LaggedStartMap, LaggedStart, ChangeDecimalToValue, ReplacementTransform, FadeInFromDown, ApplyFunction, Rotate]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 4931
scene_classes: [SpiralScene, AltTitle, RefresherOnPolarCoordinates, PrimesAndPi, CountSpirals, HighlightGapsInSpirals]
---

## Summary

Visualizes prime numbers plotted in polar coordinates (n, n) — each integer n is placed at angle n radians and distance n from origin, forming a striking spiral pattern. Uses tiny squares (VGroup of filled Squares) or point clouds (PMobject) depending on zoom level. The SpiralScene base class provides reusable methods for polar point conversion, scale animation, and label generation. Reveals how residue classes modulo various numbers create the observed spiral arms through progressive zoom and coloring.

## Design Decisions

- **Polar coordinate encoding (r=n, theta=n)**: Both distance and angle equal n. This dual encoding creates the spiral structure — the pattern emerges from the relationship between integers and radian angle wrapping. Using the same value for both coordinates is the key insight.
- **Squares instead of Dots for VGroup spiral**: Each point is a tiny filled Square (side_length ~0.2) rather than a Dot. Squares are more GPU-efficient at small sizes and create a more uniform texture when thousands are rendered.
- **PMobject for large N**: When plotting millions of points, switches from VGroup of Squares to PMobject (point-based rendering). This is a critical performance pattern — VGroup breaks down past ~10K elements.
- **Progressive zoom with custom rate_func**: The set_scale method scales axes + spiral + extras together about ORIGIN. Uses a custom rate function `lambda t: interpolate(smooth(t), smooth(t)**(sf**0.5), t)` to feel natural at different zoom levels.
- **TEAL as default dot color**: Primes rendered in TEAL against black background. Non-primes either absent or shown in low-contrast. This creates the "galaxy" aesthetic.
- **Color-by-residue-class**: Spiral arms are color-coded by `n mod k` to reveal the pattern — points in the same residue class share a color, making the spiral structure visually obvious.

## Composition

- **Axes**: Default Axes with stroke_width=1.5 on axis config. Centered at origin.
- **Spiral points**: Squares at side_length ~0.2 (auto-scaled by zoom), fill_color=TEAL, fill_opacity=1, stroke_width=0.
- **PMobject spiral**: stroke_width=6 (p_spiral_width config), color=TEAL.
- **Labels**: Integer labels next to points, scaled by sqrt(n), positioned UP with buff=0.5*label_height. Background stroke for legibility.
- **Polar coordinate demo**: NumberPlane for Cartesian, polar_grid for polar. Dot for traced point, DecimalNumber for live coordinate display.
- **Screen**: FRAME_WIDTH layout, all elements scale about ORIGIN.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Default spiral points | TEAL | fill_opacity=1, stroke_width=0 |
| Background | BLACK | Default |
| Coordinate x | GREEN | Cartesian x coordinate |
| Coordinate y | RED | Cartesian y coordinate |
| Radius r | YELLOW | Polar radius |
| Angle theta | LIGHT_PINK | Polar angle |
| Primes highlight | TEAL | ApplyFunction to scale(1.2) |
| Non-primes | 25% opacity | set_opacity(0.25) |
| Rational approximations pi | YELLOW | Pi-related values |
| Image background | 25% overlay | FullScreenFadeRectangle(fill_opacity=0.25) |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Polar zoom out | run_time=3 | set_scale with custom rate_func |
| Coordinate drawing | run_time=2 | ShowCreation of x_line, y_line |
| DecimalNumber update | run_time=2 | ChangeDecimalToValue for coords |
| Prime highlight | run_time=2 | LaggedStart with ApplyFunction |
| Label word-by-word | run_time=0.05*len(word) | Per-word FadeIn with lag_ratio=0.4 |
| Grid transition | run_time=2 | FadeOut/ShowCreation of grids |

## Patterns

### Pattern: Polar Spiral Point Generation

**What**: Maps integers to polar coordinates where both r and theta equal n. Creates either a VGroup of tiny squares (for interactive zoom) or a PMobject (for large N rendering). The get_polar_point method converts (r, theta) to Cartesian via axes.c2p.

**When to use**: Visualizing number-theoretic patterns in polar form, Ulam spiral variants, any data where angular and radial position both encode the same index. Also useful for phi-spiral (golden angle) patterns.

```python
# Source: projects/videos/_2019/spirals.py:58-118
class SpiralScene(Scene):
    CONFIG = {
        "axes_config": {"axis_config": {"stroke_width": 1.5}},
        "default_dot_color": TEAL,
        "p_spiral_width": 6,
    }

    def get_polar_point(self, r, theta, axes=None):
        if axes is None:
            axes = self.axes
        return axes.c2p(r * np.cos(theta), r * np.sin(theta))

    def get_v_spiral(self, sequence, axes=None, box_width=None):
        # VGroup approach — good for < 10K points
        return VGroup(*[
            Square(side_length=box_width, fill_color=self.default_dot_color,
                   fill_opacity=1, stroke_width=0,
            ).move_to(self.get_polar_point(n, n, axes))
            for n in sequence
        ])

    def get_p_spiral(self, sequence, axes=None):
        # PMobject approach — good for millions of points
        result = PMobject(color=self.default_dot_color, stroke_width=self.p_spiral_width)
        result.add_points([self.get_polar_point(n, n, axes) for n in sequence])
        return result
```

### Pattern: Progressive Zoom with Scale Factor

**What**: Scales axes, spiral, and supplementary mobjects together about ORIGIN. Calculates scale factor from current unit size vs target. Uses a custom rate function that adapts based on the magnitude of the zoom. Handles both VGroup (resize individual squares) and PMobject (adjust stroke width).

**When to use**: Any scene needing to zoom from local to global view, number theory explorations where patterns emerge at different scales, fractal-like self-similarity reveals.

```python
# Source: projects/videos/_2019/spirals.py:120-168
def set_scale(self, scale, axes=None, spiral=None, to_shrink=None,
              min_box_width=0.05, target_p_spiral_width=None,
              added_anims=[], run_time=3):
    sf = self.get_scale_factor(scale, axes)
    anims = []
    for mob in [axes, spiral, to_shrink]:
        if mob is None:
            continue
        mob.generate_target()
        mob.target.scale(sf, about_point=ORIGIN)
        if mob is spiral and isinstance(mob, VMobject):
            for submob in mob.target:
                submob.set_width(max(old_width * sf, min_box_width))
        anims.append(MoveToTarget(mob))
    self.play(*anims, run_time=run_time,
              rate_func=lambda t: interpolate(smooth(t), smooth(t)**(sf**0.5), t))
```

### Pattern: Refresher Scene with Coordinate System Transition

**What**: Teaches polar coordinates by starting with Cartesian (NumberPlane with x/y lines and braces), then transitioning to polar (custom polar grid with r/theta). Uses live-updating DecimalNumbers bound to a moving Dot, with add_updater for label positioning. The transition uses FadeOut of Cartesian elements and ShowCreation of polar grid.

**When to use**: Any video that needs to establish a coordinate system before the main content. Useful for transitioning between representations (Cartesian to polar, real to complex, etc.).

```python
# Source: projects/videos/_2019/spirals.py:326-500
# Cartesian phase
coord_label.add_updater(lambda m: m.next_to(dot, UR, SMALL_BUFF))
self.play(
    ShowCreation(x_line),
    ChangeDecimalToValue(x_coord, x),
    UpdateFromFunc(dot, lambda d: d.move_to(x_line.get_end())),
    run_time=2,
)
# Transition to polar
self.play(
    FadeOut(self.xy_coord_mobjects),
    FadeOut(self.plane),
    ShowCreation(self.polar_grid, run_time=2),
)
```

## Scene Flow

1. **Title** (0-10s): Alliterative title over prime spiral background image. Words appear one at a time with per-word FadeIn lag.
2. **Primes in Grid** (10-30s): 10x10 integer matrix. Primes highlighted in TEAL at scale=1.2, non-primes dimmed to 25% opacity. Shows primes are "special" but seem random.
3. **Polar Coordinate Refresher** (30-90s): NumberPlane with (x,y) demo, transition to polar grid with (r,theta). Moving dot with live DecimalNumber coordinates. Establishes the encoding before the spiral.
4. **First Spiral** (90-120s): All integers plotted at (n, n) in polar. Initial small view shows individual points. Progressive zoom reveals spiral arms emerging.
5. **Prime Filtering** (120-180s): Same spiral but only primes. The spiral arms persist — primes avoid certain residue classes. Color-coding by n mod 6 reveals the structure.
6. **Rational Approximations** (180-240s): Connection to pi approximations (22/7, 355/113). The number of spiral arms relates to denominators of good rational approximations of 2*pi.
