---
source: https://github.com/far1din/manim/blob/main/cubic_formula/3d_animations.py
project: manim_far1din
domain: [mathematics, algebra, geometry]
elements: [cube, prism, brace, label, equation, formula, rectangle_node]
animations: [write, fade_in, fade_out, transform, indicate, rotate]
layouts: [centered]
techniques: [three_d_camera, value_tracker, always_redraw, custom_animation]
purpose: [demonstration, exploration, derivation, decomposition]
mobjects: [Cube, Prism, Brace, MathTex, VGroup, Rectangle, Line, BraceBetweenPoints]
manim_animations: [Write, FadeIn, FadeOut, Create, Indicate, ShowPassingFlash, Rotating, SurroundingRectangle]
scene_type: ThreeDScene
manim_version: manim_community
complexity: advanced
lines: 792
scene_classes: [A1, A1_FIX, A2, A3]
---

## Summary

Four ThreeDScene classes that visualize the "completing the cube" technique for solving cubic equations. A yellow Cube represents x^3, and three blue Prisms represent the mx term, sliced into three equal pieces that rotate into position on three faces of the cube. The A1/A2 scenes use ValueTracker with always_redraw to dynamically resize the prism cross-section (showing that the cross-sectional area is fixed at m regardless of shape). A3 adds detailed braces labeling each dimension (x, t, u/3) and reveals the small cube that must be subtracted to "complete" the larger cube. Camera is set at phi=65, theta=45 degrees throughout.

## Design Decisions

- **Yellow cube + blue prisms color scheme**: YELLOW_D for the main cube (x^3 term) and BLUE for the three prisms (mx term). This matches the color-coded algebra in the 2D derivation scenes, maintaining consistency across the project.
- **ValueTracker-driven prism reshaping**: The prism width is controlled by a ValueTracker, and always_redraw recalculates prism dimensions maintaining constant cross-sectional area. This dynamically shows that only the area matters, not the aspect ratio.
- **Three prisms instead of one**: The mx term splits into 3 identical prisms that attach to 3 faces of the cube. Each rotates differently (90 deg around X, Y, or no-axis) to fit its face. This geometric decomposition is the visual heart of the completing-the-cube proof.
- **Camera at phi=65, theta=45**: Provides a good isometric-like view where all three faces of the cube are visible, critical for seeing how the prisms attach.
- **BraceBetweenPoints for precise 3D labeling**: Since standard Brace doesn't work well in 3D after rotations, BraceBetweenPoints is used for precise placement of dimension labels on rotated prisms.
- **Rotating animation for overview**: After attaching all prisms, the entire assembly rotates as a unit so the viewer can see the structure from all angles.

## Composition

- **Camera**: phi=65 degrees, theta=45 degrees, gamma=0, zoom=0.8.
- **Cube**: side_length=3, fill_opacity=1, fill_color=YELLOW_D, centered at ORIGIN.
- **Prism dimensions**: width=ValueTracker(0.5), depth=area/width (area=3.5*0.5=1.75), height=cube_dim=3.
- **Prism positioning (pre-rotation)**: next_to(cube, LEFT, buff=1.5), shifted UP*4.5. Three prisms stacked LEFT with buff=0.
- **Prism positioning (post-rotation)**:
  - Prism 1: rotate 90 deg axis=RIGHT, next_to cube RIGHT, buff=0, shift 0.5*ttt*OUT
  - Prism 2: rotate 90 deg (default), next_to cube UP, buff=0, shift 0.5*ttt*RIGHT
  - Prism 3: rotate 90 deg axis=UP, next_to cube OUT, buff=0, shift 0.5*ttt*UP
- **Braces**: Standard Brace for cube edges, rotated into 3D orientation. Brace labels ("x", "t", "u/3") use MathTex rotated to face camera.
- **Subtracted corner cube**: Cube(side_length=0.5), positioned next_to prism1 UP, shifted OUT*1.5.
- **Blue bottom indicator**: Rectangle with fill_opacity=1, fill_color=BLUE, stroke_opacity=0, shifted 0.5*cube_dim*IN (to the bottom face of prisms).

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Main cube | YELLOW_D | fill_opacity=1 |
| Prisms (pre-attach) | BLUE | fill_opacity=0.3-0.5 via ValueTracker |
| Prisms (attached) | BLUE | fill_opacity=0.4 |
| Blue bottom area | BLUE | Rectangle, fill_opacity=1, stroke_opacity=0 |
| Area text "m" | BLACK | On blue bottom surface |
| Braces | default WHITE | |
| Dimension label "x" | default | MathTex, rotated for 3D |
| Dimension label "t" | default | |
| Dimension label "u/3" | default | MathTex fraction |
| Corner cube (subtract) | RED_E | fill_opacity=0.5 initially, set_opacity toggled |
| Indicate emphasis | RED | On braces and labels |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Cube FadeIn | default | |
| Brace Create | default | 3 braces for x dimensions |
| Prism FadeIn | default | With area rectangle and label |
| ValueTracker reshape | run_time=1.5 | linear rate_func |
| Prism opacity animate | default | bp*_opacity ValueTrackers |
| Prism rotation and attach | default | 3 simultaneous rotations |
| Rotating full assembly | default | Full rotation about center |
| Corner cube reveal | default | Opacity 0 to 1 |
| Total per scene | ~30-45 seconds each | 4 scenes = ~2-3 minutes total |

## Patterns

### Pattern: ValueTracker-Driven 3D Prism Reshaping

**What**: Uses a ValueTracker for prism width and always_redraw to continuously rebuild Prism objects with dimensions [width, area/width, height], maintaining constant cross-sectional area while the shape changes. Opacity is also controlled via separate ValueTrackers for each prism.

**When to use**: Showing that a geometric constraint (constant area) allows different shapes, demonstrating volume decomposition in 3D, any 3D visualization where dimensions must maintain a mathematical relationship while one parameter varies.

```python
# Source: projects/manim_far1din/cubic_formula/3d_animations.py:58-84
area = 3.5 * 0.5
blue_width = ValueTracker(0.5)
bp1_opacity = ValueTracker(0)

bluep1 = always_redraw(
    lambda: Prism(
        dimensions=[blue_width.get_value(), area/blue_width.get_value(), cube_dim],
        fill_opacity=1,
        fill_color=BLUE
    ).next_to(cube, LEFT, buff=1.5).shift(UP*4.5).set_opacity(bp1_opacity.get_value())
)

# Animate reshape
self.play(
    blue_width.animate.set_value(1),
    rate_func=linear,
    run_time=1.5
)
```

### Pattern: Three-Face Prism Attachment with Rotation

**What**: Three prisms (representing the 3mx term split into thirds) each rotate by 90 degrees around different axes and attach to different faces of a cube. The gap offset (ttt) accounts for the dimensional mismatch between cube side and prism depth.

**When to use**: Completing-the-cube visualization, any 3D decomposition where auxiliary volumes attach to faces of a primary solid. Geometric proofs involving volume addition in three dimensions.

```python
# Source: projects/manim_far1din/cubic_formula/3d_animations.py:191-207
ttt = abs(cube_dim - area/blue_width.get_value())

bluep1_copy = copy.deepcopy(bluep1)
bluep2_copy = copy.deepcopy(bluep2)
bluep3_copy = copy.deepcopy(bluep3)

self.play(
    bluep1_copy.animate.rotate(90*DEGREES, axis=RIGHT).next_to(cube, RIGHT, buff=0).shift(0.5*ttt*OUT),
    bp1_opacity.animate.set_value(0),

    bluep2_copy.animate.rotate(90*DEGREES).next_to(cube, UP, buff=0).shift(0.5*ttt*RIGHT),
    bp2_opacity.animate.set_value(0),

    bluep3_copy.animate.rotate(90*DEGREES, axis=UP).next_to(cube, OUT, buff=0).shift(0.5*ttt*UP),
    bp3_opacity.animate.set_value(0),
    FadeOut(BG4)
)
```

### Pattern: 3D Brace Labeling with Rotation

**What**: Creates Brace objects for cube edges, then rotates them into the correct 3D orientation using chained rotations (e.g., rotate 90 deg axis=LEFT, then shift). MathTex labels are similarly rotated (180 deg, 90 deg axis=RIGHT, etc.) to face the camera from the chosen viewpoint.

**When to use**: Labeling dimensions on 3D objects, annotating ThreeDScene geometry with text, any 3D visualization requiring readable dimension indicators on edges or faces.

```python
# Source: projects/manim_far1din/cubic_formula/3d_animations.py:40-52
b1 = Brace(cube, RIGHT)
t1 = MathTex("x").next_to(b1, RIGHT).rotate(180*DEGREES)
BG1 = VGroup(b1, t1).rotate(90*DEGREES, axis=LEFT).shift(DOWN * (cube_dim*.5 + .05))

b2 = Brace(cube, RIGHT)
t2 = MathTex("x").next_to(b2, RIGHT).rotate(90*DEGREES)
BG2 = VGroup(b2, t2).shift(IN * (cube_dim*.5 + .1))

b3 = Brace(cube, IN)
t3 = MathTex("x").next_to(b3, UP).rotate(180*DEGREES)
BG3 = VGroup(b3, t3).shift(IN * (cube_dim*.5 + .1))
```

### Pattern: Subtracted Corner Cube Reveal

**What**: A small Cube (side_length matching the prism width) is placed at the corner where all three prisms meet. Its opacity toggles between 0 and 1 to show/hide the volume that must be subtracted when completing the cube. Dimension labels switch between (x, u/3) and (t) representations to show both decompositions.

**When to use**: Volume subtraction or addition proofs in 3D, completing-the-cube visualization, any geometric construction where a correction term has a clear spatial interpretation.

```python
# Source: projects/manim_far1din/cubic_formula/3d_animations.py:723-739
cube_to_subtract = Cube(.5, fill_opacity=0, fill_color=BLUE).next_to(
    bluep1_copy, UP, buff=0
).shift(OUT*1.5)
self.add(cube_to_subtract)

self.play(
    cube_to_subtract.animate.set_opacity(1),
    bluep1_copy.animate.set_opacity(1),
    bluep2_copy.animate.set_opacity(1),
    bluep3_copy.animate.set_opacity(1),
    FadeOut(x_labels),
    FadeIn(t_labels),
)
```

## Scene Flow

1. **A1: Dynamic prism reshaping** (0-30s): Yellow cube with x braces appears. Blue prism block with area label fades in. ValueTracker reshapes the prism cross-section while maintaining area=m. Area text flashes to emphasize constancy. Prisms split into 3 pieces.
2. **A1: Prism attachment** (30-50s): Three prisms rotate onto three cube faces simultaneously. Assembly rotates for overview.
3. **A1_FIX: Alternative take** (same content): Refined version with corrected prism opacity and label sequencing.
4. **A2: Extended labeling** (0-50s): Full cube+prism setup with t and u dimension braces. ValueTracker reshapes with visible t and u labels updating. Area relationship demonstrated. Variables renamed from numeric to symbolic (t, u).
5. **A3: Completing the cube** (0-80s): Full setup with sliced prisms showing u/3 labels. Each prism rotated individually with step-by-step labeling (x brace, t brace, u/3 brace). Assembly rotates. Dimension labels switch between (x, u/3) and (t) views. Corner cube revealed in RED_E, then hidden. Assembly rotates again.
