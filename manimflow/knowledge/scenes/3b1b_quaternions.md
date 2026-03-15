---
source: https://github.com/3b1b/videos/blob/main/_2018/quaternions.py
project: videos
domain: [complex_analysis, algebra, geometry, topology]
elements: [sphere, circle_node, vector, arrow, label, equation, complex_plane, number_line, pi_creature, cube]
animations: [rotate, transform, fade_in, fade_out, write, draw, lagged_start, camera_rotate]
layouts: [centered, side_by_side, radial]
techniques: [three_d_camera, custom_mobject, helper_function, progressive_disclosure]
purpose: [exploration, demonstration, analogy, step_by_step]
mobjects: [Sphere, ParametricSurface, Circle, Line, VGroup, OldTex, OldTexText, NumberPlane, ComplexPlane, NumberLine, Dot, Arrow, Square, SVGMobject, CheckedCircle, RubiksCube]
manim_animations: [FadeIn, FadeOut, FadeInFromLarge, ShowCreation, Write, GrowFromCenter, LaggedStartMap, Rotating, DrawBorderThenFill, Blink, ReplacementTransform, ApplyMethod, CounterclockwiseTransform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 6427
scene_classes: [ManyNumberSystems, SymmetriesOfSquare, QuaternionTracker, StereoProjectedSphere, RubiksCube]
---

## Summary

Visualizes quaternions and their relationship to 3D rotations through stereographic projection. Custom mobjects project the 4D hypersphere onto 3D space: StereoProjectedSphere renders the quaternion sphere, StereoProjectedCircleFromHypersphere shows how quaternion multiplication maps great circles. A QuaternionTracker (extending ValueTracker to 4D) enables smooth quaternion interpolation. The Linus character (a 1D being) provides narrative contrast. RubiksCube demonstrates 3D rotation actions.

## Design Decisions

- **Stereographic projection for 4D visualization**: Since quaternions live on S3 (a 3-sphere in 4D), stereographic projection maps them to 3D space where they can be rendered. The projection formula `point * r / (point[axis] + r)` maps through one pole, creating the characteristic circle-preserving distortion.
- **CheckeredCircle for great circles**: Great circles on the hypersphere are rendered with alternating colors (BLUE_E, BLUE_C) in 48 pieces. This makes rotation direction visible — you can see which way the circle moves by watching the checker pattern.
- **QuaternionTracker as 4D ValueTracker**: Extends ValueTracker to store 4-component vectors. The force_unit option auto-normalizes to keep quaternions on the unit sphere. This enables smooth interpolation between rotations.
- **Linus character (1D being)**: A custom VGroup with a body line and Eyes. Can become a squiggle for emotions. Represents a 1D creature's perspective on higher dimensions — the pedagogical framing.
- **RubiksCube for tangible 3D rotations**: A VGroup of colored squares arranged in 3D on 6 faces. The viewer sees rotation as something familiar before the abstract quaternion math.
- **q_mult function for quaternion multiplication**: Pure Python quaternion algebra (no libraries), making the code self-contained and the multiplication rule visible.

## Composition

- **Number systems layout**: Reals at [-4,2], Complex at [4,0], Quaternions at [0,2], Rationals at [3,-2]. NumberLine for reals (x_min=-3, x_max=3), ComplexPlane (x_radius=3.5, y_radius=2.5). Systems shift left as focus narrows.
- **RubiksCube**: 6 faces, each 3x3 grid of squares (side_length=1). Colors: Yellow, Red, Green, Orange, Blue, White. stroke_width=3, stroke_color=BLACK.
- **StereoProjectedSphere**: radius=1, projected through axis=2 (z-axis). Max rendered radius=32 to handle projection distortion.
- **Linus**: body stroke_width=15, GREY_B with sheen=0.4. Height=2. Eyes on top.
- **SymmetriesOfSquare**: square side_length=2, BLUE fill at 0.75 opacity. 8 symmetries arranged in 4+4 grid with LARGE_BUFF.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Reals | YELLOW | NumberLine example |
| Complex numbers | BLUE | ComplexPlane example |
| Quaternions | PINK | Title and examples |
| Rationals | RED | Number system label |
| p-adic | GREEN | Number system label |
| Octonions | GREY_B | Number system label |
| RubiksCube faces | #FFD500, #C41E3A, #009E60, #FF5800, #0051BA, #FFFFFF | Y, O, G, R, B, W |
| CheckeredCircle | BLUE_E, BLUE_C | Alternating, stroke_width=5 |
| Linus body | GREY_B | stroke_width=15, sheen=0.4 |
| Square symmetry | BLUE | fill_opacity=0.75 |
| Adder color | GREEN | ADDER_COLOR constant |
| Multiplier color | YELLOW | MULTIPLIER_COLOR constant |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Cube rotation | run_time=5 | radians=PI/3 |
| Number system intro | run_time=1 per FadeInFromLarge | Staggered |
| Square symmetry rotation | run_time=2 | With arcs |
| Square flip | run_time=2 | About axis |
| Stereographic projection | continuous | Updated per frame |
| Linus expression change | run_time=1 | Body becomes squiggle |

## Patterns

### Pattern: Stereographic Projection of Hypersphere

**What**: Projects a 4D quaternion sphere onto 3D space via stereographic projection. The StereoProjectedSphereFromHypersphere takes a quaternion and a null_axis, multiplies every point on S2 by the quaternion, then projects via `point * r / (point[axis] + r)`. Points near the projection pole are faded to avoid infinity artifacts.

**When to use**: Quaternion visualization, higher-dimensional geometry, Hopf fibration, any 4D-to-3D projection. Also useful for visualizing group actions on spheres.

```python
# Source: projects/videos/_2018/quaternions.py:12-54
def stereo_project_point(point, axis=0, r=1, max_norm=10000):
    point = fdiv(point * r, point[axis] + r)
    point[axis] = 0
    norm = get_norm(point)
    if norm > max_norm:
        point *= max_norm / norm
    return point

def stereo_project(mobject, axis=0, r=1, outer_r=10, **kwargs):
    for submob in mobject.family_members_with_points():
        # Handle pole singularity by nudging
        points = submob.get_points()
        for i in range(len(points)):
            if points[i, axis] == -r:
                # Find nearest non-pole point and nudge toward it
                ...
        submob.apply_function(
            lambda p: stereo_project_point(p, axis, r, **kwargs)
        )
```

### Pattern: QuaternionTracker (4D ValueTracker)

**What**: Extends ValueTracker to store and interpolate 4-component quaternion vectors. Auto-normalizes to unit quaternions via an updater. get_value/set_value work with 4D arrays stored as points. Enables smooth quaternion animation by interpolating the tracker value.

**When to use**: Any animation involving quaternion rotation, SLERP interpolation, orientation tracking. Also a pattern for extending ValueTracker to arbitrary-dimension state.

```python
# Source: projects/videos/_2018/quaternions.py:332-358
class QuaternionTracker(ValueTracker):
    CONFIG = {"force_unit": True, "dim": 4}

    def __init__(self, four_vector=None, **kwargs):
        Mobject.__init__(self, **kwargs)
        if four_vector is None:
            four_vector = np.array([1, 0, 0, 0])
        self.set_value(four_vector)
        if self.force_unit:
            self.add_updater(lambda q: q.normalize())

    def set_value(self, vector):
        self.set_points(np.array(vector).reshape((1, 4)))

    def get_value(self):
        return self.get_points()[0]

    def normalize(self):
        self.set_value(normalize(self.get_value(), fall_back=np.array([1, 0, 0, 0])))
```

### Pattern: Custom Character (Linus 1D Being)

**What**: A VGroup representing a 1D creature with a body (Line with thick stroke and sheen) and Eyes. Can change_mode to become a squiggle (FunctionGraph of sin) for "sad" or "confused" states. The character provides narrative personality to abstract concepts.

**When to use**: Any video with a character-driven narrative explaining higher dimensions. The pattern of a minimal custom character with mode changes is reusable for any explanatory animation needing personality.

```python
# Source: projects/videos/_2018/quaternions.py:57-131
class Linus(VGroup):
    CONFIG = {
        "body_config": {"stroke_width": 15, "stroke_color": GREY_B, "sheen": 0.4},
        "height": 2,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.body = self.get_body_line()
        self.eyes = Eyes(self.body)
        self.add(self.body, self.eyes)

    def change_mode(self, mode, thing_to_look_at=None):
        self.eyes.change_mode(mode, thing_to_look_at)
        if mode == "sad":
            self.become_squiggle()
        else:
            self.become_line()
```

## Scene Flow

1. **Number Systems Overview** (0-30s): Title "Number systems." Reals, Complex, Quaternions, Rationals, p-adics, Octonions arranged spatially. NumberLine and ComplexPlane appear for reals and complex. Quaternions positioned prominently.
2. **Square Symmetries** (30-120s): Title "Groups <-> Symmetry." A blue square (fill_opacity=0.75). Rotations shown with arcs, flips shown with axis lines. 8 symmetries arranged in grid. Labels added with Randolph character.
3. **Linus Introduction** (120-180s): The 1D character explains his perspective. Body line with eyes. Mode changes for reactions.
4. **Complex Multiplication as Rotation** (180-240s): Unit circle on ComplexPlane. Velocity vector perpendicular to position vector. Rotating animation shows e^{it} tracing the circle.
5. **Stereographic Projection** (240-360s): 3D sphere projected to 2D plane. Then hypersphere (4D) projected to 3D. Quaternion multiplication visualized as transforming great circles.
6. **RubiksCube Rotations** (360-420s): 3D cube with colored faces. Rotations applied to show quaternion actions on physical objects.
