---
source: https://github.com/3b1b/videos/blob/main/_2018/lost_lecture.py
project: videos
domain: [physics, mechanics, geometry, astronomy]
elements: [circle_node, line, dashed_line, dot, arrow, label, equation, image, pi_creature]
animations: [write, draw, rotate, transform, fade_in, fade_out, lagged_start, move, orbit]
layouts: [centered, side_by_side, radial, grid]
techniques: [custom_mobject, add_updater, helper_function, progressive_disclosure]
purpose: [proof, demonstration, step_by_step, exploration]
mobjects: [Circle, Ellipse, Line, VGroup, OldTex, OldTexText, Dot, Arrow, Vector, ImageMobject, SVGMobject, Rectangle, SurroundingRectangle, Square, BackgroundRectangle]
manim_animations: [ShowCreation, FadeIn, FadeOut, FadeInFromDown, Write, GrowFromCenter, LaggedStartMap, MoveToTarget, MaintainPositionRelativeTo, VFadeOut, DrawBorderThenFill, Rotating]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 4298
scene_classes: [ShowEmergingEllipse, ShowFullStory, FeynmanFame, FeynmanAndOrbitingPlannetOnEllipseDiagram, TakeOver]
---

## Summary

Recreates Feynman's lost lecture on why planets orbit in ellipses. The key visual: lines drawn from an eccentric point inside a circle, each rotated 90 degrees about its midpoint, have their midpoints trace out a perfect ellipse. The ShowEmergingEllipse scene constructs this step-by-step with 150 lines, ghost lines for reference, and a highlighted single-line demonstration with elbow marker. The Orbiting class creates a continuously orbiting planet with Kepler's second law (speed varies inversely with distance).

## Design Decisions

- **Eccentric point construction**: A point inside a circle (offset by eccentricity_vector=2*RIGHT from center) connected to 150 points on the circle by lines. Each line rotated 90 degrees about its center. The envelope of perpendicular bisectors forms the ellipse. This is Feynman's geometric proof.
- **Ghost lines for before/after**: When lines rotate, ghost copies (GREY_B, stroke_width=0.5) remain at original positions so the viewer can see both states. This dual-display technique prevents the viewer from losing track of the construction.
- **Orbiting with inverse-square speed**: The Orbiting updater moves a planet along an ellipse with speed proportional to 1/r (Kepler's second law). Uses d_prop/ds * rate * dt for proportional traversal, where ds is the local arc length.
- **Image-heavy biographical scenes**: Feynman photos, book covers, and diagrams are loaded as ImageMobject with SurroundingRectangle borders. The biographical context establishes why this proof matters.
- **Elbow marker for right angle**: A small VGroup of two perpendicular lines (scale 0.2) marks the 90-degree rotation. Rotated to match the line's angle and positioned at the line's center.
- **PINK ellipse on BLUE circle**: High contrast between the constructed ellipse (PINK) and the generating circle (BLUE). The eccentric point is YELLOW.

## Composition

- **Circle**: radius=3, color=BLUE. Centered.
- **Eccentric point**: circle center + 2*RIGHT (eccentricity_vector). YELLOW dot.
- **Lines**: 150 lines from eccentric point to circle circumference. stroke_width=1.
- **Ghost lines**: Same as lines but GREY_B, stroke_width=0.5.
- **Ellipse**: Computed from circle radius and eccentricity. a=radius/2, c=distance/2, b=sqrt(a^2-c^2). PINK color.
- **Elbow**: Two lines (UP->UL, UL->LEFT) at scale=0.2, stroke_width=1.
- **Feynman image**: height=6, next_to ORIGIN LEFT, to_edge UP.
- **Scene overview grid**: 16 scene thumbnails in 4x4 grid, each with SurroundingRectangle.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Circle | BLUE | circle_color config, radius=3 |
| Eccentric point | YELLOW | Dot |
| Construction lines | WHITE | stroke_width=1 |
| Ghost lines | GREY_B | stroke_width=0.5 |
| Ellipse | PINK | ellipse_color config |
| Elbow marker | WHITE | stroke_width=1, scale=0.2 |
| Highlighted line dot | YELLOW | scale=0.5 |
| Fade rect | BLACK | FullScreenFadeRectangle for focus |
| Rotation words | WHITE | background_stroke: BLACK, width=5 |
| COBALT | #0047AB | Custom color constant |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Circle creation | run_time=1 | ShowCreation |
| Lines creation | run_time=2 | LaggedStartMap(ShowCreation, shuffled) |
| Single line rotation | run_time=1 | MoveToTarget with path_arc=90deg |
| All lines rotation | run_time=4 | LaggedStartMap(MoveToTarget) |
| Ellipse drawing | run_time=1 | ShowCreation |
| Orbiting planet | continuous | Updater, speed varies with 1/r |
| Feynman intro | run_time=2 | restore + VFadeOut of background rect |

## Patterns

### Pattern: Ellipse from Eccentric Point Construction

**What**: Lines from an eccentric point inside a circle to N circumference points. Each line has a target that is the same line rotated 90 degrees about its midpoint. When animated with MoveToTarget(path_arc=90*DEGREES), the lines pivot to reveal the ellipse. Ghost copies preserve the original configuration for reference.

**When to use**: Geometric proofs involving envelopes of lines, conic section constructions, any demonstration where rotating elements reveal a hidden curve. Also useful for the dual construction in projective geometry.

```python
# Source: projects/videos/_2018/lost_lecture.py:256-303
def get_lines(self):
    e_point = self.get_eccentricity_point()
    lines = VGroup(*[
        Line(e_point, center + rotate_vector(radius * RIGHT, angle))
        for angle in np.linspace(0, TAU, self.num_lines)
    ])
    lines.set_stroke(width=self.lines_stroke_width)
    for line in lines:
        line.generate_target()
        line.target.rotate(90 * DEGREES)  # About center of line
    return lines

# Animate: ghost lines stay, originals rotate
self.add(ghost_lines)
self.play(LaggedStartMap(MoveToTarget, lines, run_time=4))
self.play(ShowCreation(ellipse), FadeInFromDown(ellipse_words))
```

### Pattern: Kepler Orbiting with Variable Speed

**What**: An Orbiting updater moves a planet along an ellipse with speed inversely proportional to distance from the focus (Kepler's second law). Uses point_from_proportion for smooth traversal and computes local arc length ds to convert between proportion-space and physical-space velocity.

**When to use**: Planetary orbits, Kepler's laws, any animation where an object must move along a closed curve with varying speed. The proportion-based approach works for any parametric curve.

```python
# Source: projects/videos/_2018/lost_lecture.py:17-57
class Orbiting(VGroup):
    CONFIG = {"rate": 7.5}

    def __init__(self, planet, star, ellipse, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.add(planet)
        self.proportion = 0
        planet.move_to(ellipse.point_from_proportion(0))
        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt):
        rate = self.rate
        radius_vector = self.planet.get_center() - self.star.get_center()
        rate *= 1.0 / get_norm(radius_vector)  # Kepler's 2nd law
        d_prop = 0.001
        ds = get_norm(
            self.ellipse.point_from_proportion((self.proportion + d_prop) % 1)
            - self.ellipse.point_from_proportion(self.proportion)
        )
        delta_prop = (d_prop / ds) * rate * dt
        self.proportion = (self.proportion + delta_prop) % 1
        self.planet.move_to(self.ellipse.point_from_proportion(self.proportion))
```

## Scene Flow

1. **Circle and Eccentric Point** (0-15s): Blue circle drawn. Yellow "eccentric point" appears with label. 150 lines drawn from point to circle via LaggedStartMap.
2. **Single Line Demo** (15-30s): FullScreenFadeRectangle isolates one line. Yellow dot at center. "Rotate 90deg about center" text. Line rotates with elbow marker showing right angle.
3. **All Lines Rotate** (30-45s): Fade rect removed. All 150 lines rotate simultaneously via LaggedStartMap(MoveToTarget). Ellipse emerges from the rotated midpoints.
4. **Ellipse Revealed** (45-55s): Pink ellipse drawn with ShowCreation. "Perfect ellipse" label.
5. **Orbiting Planet** (55-90s): Earth image orbits along the ellipse with Kepler speed variation. Feynman's photo appears alongside.
6. **Story Overview** (90-120s): Grid of 16 scene thumbnails from the full video. Zooms into specific steps to preview the proof structure.
