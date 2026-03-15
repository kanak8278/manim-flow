---
source: https://github.com/3b1b/videos/blob/main/_2021/shadows.py
project: 3blue1brown
domain: [geometry, probability, linear_algebra, calculus, mathematics]
elements: [surface_3d, cube, sphere, dot, line, dashed_line, arrow, label, equation, formula, number_line]
animations: [write, fade_in, fade_out, draw, transform, rotate, camera_rotate, highlight, flash, update_value, animate_parameter]
layouts: [centered, edge_anchored]
techniques: [three_d_camera, add_updater, ambient_camera_rotation, custom_mobject, value_tracker, scipy_integration, data_driven, helper_function]
purpose: [proof, demonstration, exploration, derivation, simulation]
mobjects: [VCube, Group, NumberPlane, Rectangle, OldTex, OldTexText, Text, DecimalNumber, Integer, DashedLine, Line, DotCloud, TrueDot, Dot, Brace, SurroundingRectangle, Underline]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, DrawBorderThenFill, LaggedStartMap, LaggedStart, Rotate, ChangeDecimalToValue, VFadeInThenOut, ShowCreationThenFadeOut, UpdateFromAlphaFunc, UpdateFromFunc]
scene_type: ThreeDScene
manim_version: manimlib
complexity: advanced
lines: 6626
scene_classes: [ShadowScene, SimpleWriting, AliceName, BobName, BobWords, AliceWords, AskAboutConditions, IntroduceShadow, AskAboutAveraging, MeanCalculation, DescribeSO3, PauseAndPonder, StartSimple, FocusOnOneFace, NotQuiteRight, DiscussLinearity, Matrices, DefineDeterminant, AmbientShapeRotationPreimage, AmbientShapeRotationFull3d, AmbientShapeRotationShadowOnly, IsntThatObvious, StretchLabel, WonderAboutAverage, SingleFaceRandomRotation, RandomRotations1, RandomRotations2, RandomRotations3, RandomRotations4, AverageFaceShadow]
---

## Summary

Explores the problem of finding the average shadow area of a 3D cube (and other convex solids) across all orientations. Builds a `ShadowScene` base class providing 3D infrastructure: a ground plane, light source with glow, real-time shadow projection via updaters, convex hull outline tracking, and random tossing/rotation utilities. The mathematical payoff is that average shadow area = (1/2) * c * surface_area, connecting to the determinant of projection matrices. Features Alice/Bob character framing (embraces calculations vs seeks generality).

## Design Decisions

- **Real-time shadow projection via updater**: Shadow mobjects are deepcopies of the solid, with each point projected either flat (infinite light) or perspectively via `project_to_xy_plane`. The shadow updates every frame, making rotations visually immediate.
- **Convex hull for shadow outline**: Uses `scipy.spatial.ConvexHull` on the shadow's 2D points to compute the outline, avoiding rendering artifacts from overlapping projected faces.
- **Random toss with rotating axis**: Instead of simple rotation, `random_toss` uses a meta-rotation that slowly rotates the rotation axis itself, creating more natural-looking tumbling.
- **Depth-sorted face rendering**: `sort_to_camera` ensures faces closest to the camera render last, preventing z-fighting in the 3D scene.
- **Ground plane as NumberPlane**: A 20x20 grid with subtle background lines gives spatial grounding without visual clutter. Plane style: fill=GREY_A at opacity=0.5.
- **GlowDot for light source**: `TrueDot` with radius=10 and glow_factor=10, interpolated between YELLOW and WHITE, creates a visible light point in the 3D scene.
- **Area label with live DecimalNumber**: Continuously updates to show the shadow area divided by unit_size^2, providing real-time numerical feedback during rotations.

## Composition

- **Object center**: `[0, 0, 3]` (3 units above ground)
- **Frame center**: `[0, 0, 2]`, camera reoriented to (-30, 75)
- **Plane dims**: (20, 20), with background lines stroke=GREY_B, width=1
- **Cube**: VCube, height=2, then scaled 0.945 to make area exactly 1
- **Area label**: Fixed in frame, positioned at `[-2, -1.5, 0]`
- **Light source**: Default at high Z, movable. Glow radius=10, glow_factor=10
- **Shadow outline**: White stroke, width=1, tracks convex hull

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Cube fill | BLUE_E | fill_opacity=0.7, reflectiveness=0.3, gloss=0.1, shadow=0.5 |
| Cube stroke | WHITE | stroke_width=0.5 |
| Ground plane | GREY_A | fill_opacity=0.5, gloss=0.5, shadow=0.2 |
| Grid lines | GREY_B | stroke_width=1 |
| Shadow | darkened original | Opacity=0.7 of original color interpolated toward BLACK |
| Light glow | YELLOW-WHITE | interpolated, glow_factor=10 |
| Light lines | YELLOW | stroke_width=0.5, opacity=0.1 |
| Shadow outline | WHITE | stroke_width=1 |
| Edge labels | RED | for s (edge length) measurements |
| Hexagonal shadow | RED | outline copied with stroke_width=5 |
| Area equation | varies | tex_to_color_map for Shadow, Solid terms |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Random toss | 2-3s | `UpdateFromAlphaFunc` with rotating axis |
| Light movement | 3-8s | Various paths and durations |
| Frame rotation | 0.01 dt | Ambient slow rotation updater |
| Ambient cube rotation | 0.2 dt | `begin_ambient_rotation` |
| DrawBorderThenFill (cube + shadow) | 3s | lag_ratio=0.1 |
| Total video | ~25 min | Very long, many scenes |

## Patterns

### Pattern: Real-Time Shadow Projection Updater

**What**: Creates a shadow mobject as a deepcopy with darkened colors, then adds an updater that projects every point either flat to xy-plane or perspectively from a light source. Handles both VMobject and non-VMobject families, with normal-vector flipping for correct fill rendering.

**When to use**: Any 3D projection visualization, shadow studies, orthographic/perspective projection demonstrations, light-source geometry.

```python
# Source: projects/videos/_2021/shadows.py:44-66
def update_shadow(shadow, mobject, light_source):
    lp = light_source.get_center() if light_source is not None else None
    def project(point):
        if lp is None:
            return flat_project(point)
        else:
            return project_to_xy_plane(lp, point)
    for sm, mm in zip(shadow.family_members_with_points(), mobject.family_members_with_points()):
        sm.set_points(np.apply_along_axis(project, 1, mm.get_points()))
        if isinstance(sm, VMobject) and sm.get_unit_normal()[2] < 0:
            sm.reverse_points()

def get_shadow(mobject, light_source=None, opacity=0.7):
    shadow = get_pre_shadow(mobject, opacity)
    shadow.add_updater(lambda s: update_shadow(s, mobject, light_source))
    return shadow
```

### Pattern: Random Toss with Meta-Rotating Axis

**What**: Simulates a natural-looking random tumble by rotating the object around an axis that itself slowly rotates. Uses `UpdateFromAlphaFunc` with time-based dt tracking inside the update function. The meta-rotation uses `normalize(np.random.random(3))` for a random target direction.

**When to use**: Physical simulations, dice rolls, random sampling visualizations, any scenario where a rigid body needs to look naturally tumbled rather than mechanically rotated.

```python
# Source: projects/videos/_2021/shadows.py:289-305
def random_toss(self, mobject=None, angle=TAU, about_point=None, meta_speed=5, **kwargs):
    mobject.rot_axis = normalize(np.random.random(3))
    mobject.rot_time = 0
    def update(mob, time):
        dt = time - mob.rot_time
        mob.rot_time = time
        mob.rot_axis = rotate_vector(mob.rot_axis, meta_speed * dt, normalize(np.random.random(3)))
        mob.rotate(angle * dt, mob.rot_axis, about_point=about_point)
    self.play(UpdateFromAlphaFunc(mobject, update), **kwargs)
```

### Pattern: Convex Hull Shadow Outline

**What**: Computes the convex hull of the shadow's 2D points using `scipy.spatial.ConvexHull` and draws it as a VMobject outline that updates every frame. Avoids the visual noise of overlapping projected face edges.

**When to use**: Clean outline rendering of projected 3D shapes, convex hull demonstrations, any scenario where you need the outer boundary of a complex shape's projection.

```python
# Source: projects/videos/_2021/shadows.py:76-79, 261-264
def get_convex_hull(mobject):
    points = mobject.get_all_points()
    hull = scipy.spatial.ConvexHull(points[:, :2])
    return points[hull.vertices]

def get_shadow_outline(self, stroke_width=1):
    outline = VMobject().set_stroke(WHITE, stroke_width)
    outline.add_updater(lambda m: m.set_points_as_corners(
        get_convex_hull(self.shadow)
    ).close_path())
    return outline
```

### Pattern: Live Area Measurement with DecimalNumber

**What**: A fixed-in-frame label with a DecimalNumber that continuously computes the shadow's area by summing `get_area_vector()` norms across all submobjects, divided by unit_size^2 for display. Uses `set_backstroke()` for readability over the 3D scene.

**When to use**: Real-time measurement displays during 3D rotations, numerical feedback during parameter animations, any quantitative readout that should update continuously.

```python
# Source: projects/videos/_2021/shadows.py:237-249
def get_shadow_area_label(self):
    text = OldTexText("Shadow area: ")
    decimal = DecimalNumber(100)
    label = VGroup(text, decimal)
    label.arrange(RIGHT)
    label.fix_in_frame()
    label.set_backstroke()
    decimal.add_updater(lambda d: d.set_value(
        get_area(self.shadow) / (self.unit_size**2)
    ).set_backstroke())
    return label
```

## Scene Flow

1. **IntroduceShadow** (0-120s): Cube appears with shadow. Question "Find the average area of a cube's shadow" posed. Shadow area label shown with live updates. Light source explored: moved around, lines from light to shadow outline demonstrated. Light moved to infinity (orthographic projection).
2. **Flat projection** (120-180s): Top-down view shown. Vertex dots projected to xy-plane with dashed lines. Square shadow at axis-aligned orientation (area=1). Hexagonal shadow at diagonal orientation (area=sqrt(3)).
3. **Random sampling** (180-240s): Cube randomly tossed, area samples collected in column. Mean calculation framed.
4. **DescribeSO3** (240-360s): Rotation group SO(3) introduced. Single face analysis begins.
5. **FocusOnOneFace** (360-480s): One face tracked through random rotations. Connection to projection matrix determinant. Linearity argument for averaging.
6. **AverageFaceShadow** (480-600s): Final result: average shadow = (1/2) * surface area for any convex solid.
