---
source: https://github.com/3b1b/videos/blob/main/_2025/cosmic_distance/paralax.py
project: videos
domain: [astronomy, geometry, trigonometry, optics]
elements: [dot, line, dashed_line, arrow, circle, sphere, label, brace, surrounding_rect]
animations: [fade_in, fade_out, write, grow, rotate, camera_rotate, zoom_in, zoom_out, move]
layouts: [centered, side_by_side, layered]
techniques: [three_d_camera, moving_camera, add_updater, value_tracker, custom_mobject]
purpose: [demonstration, step_by_step, exploration, analogy]
mobjects: [GlowDots, GlowDot, DotCloud, Circle, Line, DashedLine, VGroup, Text, Tex, Randolph, Mortimer, LineBrace, Arc, SVGMobject, TrueDot]
manim_animations: [ShowCreation, FadeIn, FadeOut, FadeTransform, LaggedStartMap, MoveToTarget, Rotate, MaintainPositionRelativeTo, GrowFromCenter, Write, Blink, VFadeIn, Restore]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 917
scene_classes: [SimpleDotsParalax, SimpleDotsFromPerspective, ParalxInSolarSystem, ShowConstellationsDuringOrbit, ParalaxMeasurmentFromEarth]
---

## Summary

Visualizes stellar parallax — the technique astronomers use to measure distances to nearby stars by observing apparent position shifts from different viewpoints. Starts with a 3D star field demonstrating parallax from camera movement, then scales up to Earth's orbit around the Sun with realistic orbital mechanics. The main measurement scene shows two observers on Earth with sight lines to a distant object, angle labels, and progressive zoom-outs to the Moon, Venus, and Jupiter orbit scales.

## Design Decisions

- **3D star field with GlowDots**: Random points in a cube create a starfield. Moving the observer (Randy) in the z-direction while looking from the side shows nearby stars shifting more than distant ones — the parallax effect is immediately visible.
- **Pi creatures as observers**: Randy and Morty stand on Earth's surface at different angles (45 and -55 degrees). This anthropomorphizes the measurement, making the geometry of two-point observation intuitive.
- **DashedLine for sight lines with updaters**: Observation lines dynamically track both observer positions and the target object. Updaters ensure geometry stays consistent as the object moves.
- **Progressive scale reveal**: Moon orbit -> Venus orbit -> Jupiter orbit. Each zoom-out reveals how tiny Earth's baseline is compared to cosmic distances, driving home why parallax is limited.
- **Angle color coding**: alpha=BLUE, beta=RED. Consistent throughout for the two observer angles.
- **Eye analogy**: The two Earth observers are replaced with Randy's eyes briefly, making the binocular vision analogy explicit before returning to the astronomical context.

## Composition

- **3D star scene**:
  - VCube height=4, stars=200 GlowDots in [-1,1]^3 scaled to cube
  - Randy height=1, next_to cube LEFT with buff=1
  - Camera: reorient(-40, -26, 0) for side view, (-89, -4, 0) for perspective
- **Earth measurement scene**:
  - Earth: Circle radius=3, BLUE_B fill at 0.5 opacity, to_edge(LEFT)
  - Observers at 45 and -55 degree positions on circle
  - Pi creature height=0.25 (after MoveToTarget shrink)
  - Target: GlowDot at 12*RIGHT, color=TEAL
  - Frame width expands to 20 for sight lines
- **Orbit scales**:
  - Moon orbit radius based on conversion_factor = 3/EARTH_RADIUS
  - Sun: get_sun with big_glow_ratio=20
  - All orbits use Circle with stroke=(0,3) gradient

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Stars | WHITE | GlowDots, glow_factor=2, random radii 0-0.075 |
| Earth circle | BLUE_B | fill_opacity=0.5, stroke WHITE width=3 |
| Observer angle alpha | BLUE | Arc + label |
| Observer angle beta | RED | Arc + label |
| Target object | TEAL | GlowDot |
| Sight lines | WHITE | DashedLine, stroke_width=2 |
| Baseline between observers | YELLOW | Line, stroke_width=3 |
| Orbit lines | BLUE/TEAL | stroke=(0,3) gradient, anti_alias_width=5 |
| Earth back fill | BLACK | opacity=1, hides circle interior |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Star field creation | run_time=4 | ShowCreation |
| Randy parallax movement | run_time=5 each | 5 up/down movements |
| Observer placement | run_time=3 | LaggedStart MoveToTarget |
| Object movement | run_time=3 each | 4 directions with save/restore |
| Rotation around Earth | run_time=8 | there_and_back rate_func |
| Zoom to Moon | run_time=5 | Frame + object animate |
| Zoom to Venus | run_time=8 | Frame + orbit fade-ins |
| Frame ambient phi update | continuous | interpolate toward -90 deg |

## Patterns

### Pattern: 3D Parallax Star Field

**What**: Random GlowDots distributed in a cube. Moving an observer along one axis while viewing from the side demonstrates parallax — nearby dots shift more than distant ones. Camera can switch between side view and observer's perspective.

**When to use**: Parallax demonstrations, depth perception visualization, stereoscopic vision explanation, any concept where relative motion reveals distance.

```python
# Source: projects/videos/_2025/cosmic_distance/paralax.py:9-52
n_stars = 200
stars = GlowDots(np.random.uniform(-1, 1, (n_stars, 3)))
stars.scale(height / 2)
stars.set_color(WHITE)
stars.set_glow_factor(2)
stars.set_radii(np.random.uniform(0, 0.075, n_stars))

# Move observer to show parallax
for dy in [1, -2, 2, -2, 1]:
    self.play(randy.animate.shift(dy * 1.5 * IN), run_time=5)
```

### Pattern: Dynamic Sight Lines with Updaters

**What**: DashedLines connecting observer positions to a target object, with updaters that recompute endpoints every frame. When the target moves, the lines and angle labels update automatically.

**When to use**: Geometric measurement visualization, triangulation, surveying, any two-point observation geometry where the target or observers move.

```python
# Source: projects/videos/_2025/cosmic_distance/paralax.py:234-266
obs_lines = VGroup(
    DashedLine(obs_points[0], obj.get_center()),
    DashedLine(obs_points[1], obj.get_center()),
)
obs_lines.set_stroke(WHITE, 2)

for line, dot in zip(obs_lines, obs_dots):
    line.dot = dot
    line.add_updater(lambda m: m.put_start_and_end_on(
        m.dot.get_center(), obj.get_center()
    ))
```

### Pattern: Progressive Scale Zoom-Out

**What**: Start at a human-scale view, then zoom out through Moon orbit, Venus orbit, and Jupiter orbit scales. Each transition uses frame.animate with new height/center targets and fade-in of the next orbit circle. A conversion_factor maps real astronomical distances to screen coordinates.

**When to use**: Astronomical scale comparisons, powers-of-ten zooms, any visualization that needs to show the same geometry at progressively larger scales.

```python
# Source: projects/videos/_2025/cosmic_distance/paralax.py:417-454
conversion_factor = radius / EARTH_RADIUS
moon_orbit = Circle(radius=MOON_ORBIT_RADIUS * conversion_factor)
moon_orbit.set_stroke(GREY_B, width=(0, 3))

self.play(
    obj.animate.move_to(moon),
    frame.animate.set_height(1.5 * moon_orbit.get_width())
        .move_to(moon_orbit.get_right())
        .set_field_of_view(35 * DEG),
    FadeIn(moon_orbit),
    run_time=5
)
```

## Scene Flow

1. **Star field parallax** (0-30s): 200 stars in a 3D cube. Randy moves up/down, side view shows nearby stars shifting more. Then camera switches to Randy's perspective.
2. **Solar system parallax** (30-60s): Sun at center, Earth orbiting. Camera follows Earth, stars appear to shift. Zoom out reveals star distribution.
3. **Earth measurement** (60-180s): Two observers on a 2D Earth circle. Sight lines to a TEAL target object. Eye analogy. Angle labels alpha (BLUE) and beta (RED). Baseline highlighted in YELLOW. Triangle geometry explained.
4. **Scale zoom-outs** (180-240s): Progressive reveal of Moon orbit, Venus orbit, Jupiter orbit. Each zoom shows how tiny the Earth baseline is. Observer positions rotate for orbital baseline.
