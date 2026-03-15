---
source: https://github.com/3b1b/videos/blob/main/_2017/efvgt.py
project: videos
domain: [algebra, geometry, complex_analysis, mathematics]
elements: [axes, vector, arrow, circle_node, label, equation, pi_creature, complex_plane, number_line, surrounding_rect]
animations: [write, rotate, transform, replacement_transform, fade_in, fade_out, draw, indicate]
layouts: [centered, side_by_side, horizontal_row]
techniques: [three_d_camera, custom_mobject, helper_function, progressive_disclosure, teacher_students_scene]
purpose: [definition, demonstration, exploration, analogy]
mobjects: [VGroup, OldTex, OldTexText, Circle, Square, Line, Arrow, Vector, NumberPlane, ComplexPlane, Dot, Brace, Rectangle, FunctionGraph, Randolph, SVGMobject, PartyHat]
manim_animations: [Write, FadeIn, FadeOut, ShowCreation, GrowFromCenter, GrowArrow, DrawBorderThenFill, Blink, Rotating, ReplacementTransform, ApplyMethod, Succession, LaggedStartMap, Rotate, Indicate]
scene_type: TeacherStudentsScene
manim_version: manimlib
complexity: intermediate
lines: 3370
scene_classes: [Anniversary, SymmetriesOfSquare, QuickExplanation, LetsStudyTheBasics, WatchingScreen]
---

## Summary

Introduces group theory through the symmetries of a square (dihedral group of order 8). A blue square with face labels (Randolph character) demonstrates all 8 symmetry actions — 4 rotations and 4 reflections — arranged in a horizontal grid. The e^{it} explanation connects complex multiplication to rotation: the velocity vector is always a 90-degree rotation of the position vector, and Rotating animation traces the unit circle. TeacherStudentsScene framing with party hats celebrates the channel anniversary while introducing the math.

## Design Decisions

- **Square with Randolph face for orientation**: A plain blue square looks the same after rotation — you can't tell if anything happened. Adding Randolph's face makes the orientation visible, so each symmetry action produces a visibly different result.
- **8 symmetries in a grid**: 4 rotations (top row, with arc indicators) + 4 reflections (bottom row, with axis lines). Arranged with LARGE_BUFF between. Each miniature square (scale=0.5) is independently animated to show its action.
- **Complex exponential as rotation**: The equation d(e^{it})/dt = i*e^{it} is shown with a position vector (YELLOW) and velocity vector (RED) rotating together. The key insight: the velocity is always perpendicular to position, which means circular motion.
- **ConfettiSpiril for celebration**: Custom Animation that spirals colored squares downward while rotating — a visual celebration effect. Uses squish_rate_func for staggered starts.
- **Dashed line symmetry axes**: Reflection axes are drawn as DashedLine or Line through the square's center. Each axis (horizontal, vertical, two diagonals) is paired with a flip demonstration.
- **get_composite_rotation_angle_and_axis**: Pure math function computing the combined effect of sequential 3D rotations via quaternion-like algebra, enabling composition of group elements.

## Composition

- **Square**: side_length=2, BLUE fill at 0.75 opacity, stroke_width=0. Centered.
- **8 symmetries grid**: Each square at scale=0.5. 4+4 layout (top_squares, bottom_squares). All squares within FRAME_WIDTH-2*LARGE_BUFF total width. Centered, to_edge DOWN with LARGE_BUFF.
- **Rotation arcs**: Small arcs (MED_SMALL_BUFF) showing rotation angles (90, 180, -90 degrees). Added as children of the square.
- **Reflection axes**: Lines through center, extending to square edges. For axes UP, UP+RIGHT, RIGHT+UP, UP+LEFT.
- **Complex plane vectors**: s_vector (YELLOW, position) and v_vector (RED, velocity). Unit circle radius = z_to_point(1)[0]. Rotating about ORIGIN.
- **Equation**: d(e^{it})/dt = i*e^{it}. Velocity term in RED, position in YELLOW. Background rectangle for readability.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Square | BLUE | fill_opacity=0.75, stroke_width=0 |
| Position vector | YELLOW | position_color config |
| Velocity vector | RED | velocity_color config |
| Unit circle | YELLOW | Circle matching position color |
| Adder | GREEN | ADDER_COLOR constant |
| Multiplier | YELLOW | MULTIPLIER_COLOR constant |
| Confetti | RED, YELLOW, GREEN, BLUE, PURPLE | Random selection |
| Party hats | Various | Random rotation about bottom |
| Background labels | WHITE | add_background_rectangle |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Square rotation | run_time=2 | With arcs |
| Square flip | run_time=2 | 3D rotation about axis |
| Circle tracing | run_time=5, rate_func=None | Continuous Rotating |
| Confetti spiral | run_time=10 | 50 squares with staggered starts |
| All 8 symmetries demo | run_time=3 each | there_and_back rate_func |
| Title write | run_time=2 | Write("Groups <-> Symmetry") |
| Student reactions | run_time=1-2 | change_mode calls |

## Patterns

### Pattern: Group Actions Grid (Dihedral Group)

**What**: All symmetry actions of a group displayed as a grid of small copies of the object. Top row: rotations with arc indicators. Bottom row: reflections with axis lines. Each copy independently demonstrates its action. The identity (do-nothing) is explicitly included as the first element.

**When to use**: Visualizing any finite group's elements, symmetry catalogs, group tables. The grid layout makes the group structure visible. Works for dihedral groups, permutation groups, or any finite symmetry group.

```python
# Source: projects/videos/_2017/efvgt.py:426-466
all_squares = VGroup(*[self.square.copy().scale(0.5) for x in range(8)])
top_squares = VGroup(*all_squares[:4])
bottom_squares = VGroup(*all_squares[4:])
bottom_squares.next_to(top_squares, DOWN, buff=LARGE_BUFF)
all_squares.set_width(FRAME_WIDTH - 2*LARGE_BUFF)
all_squares.center().to_edge(DOWN, buff=LARGE_BUFF)

# Rotations with arcs
for square, angle in zip(all_squares[1:4], [PI/2, PI, -PI/2]):
    arcs = self.get_rotation_arcs(square, angle, MED_SMALL_BUFF)
    self.play(*list(map(FadeIn, [square, arcs])))
    self.rotate_square(square=square, angle=angle)
    square.add(arcs)

# Reflections with axis lines
for square, axis in zip(bottom_squares, [RIGHT, RIGHT+UP, UP, UP+LEFT]):
    axis_line = self.get_axis_line(square, axis)
    self.rotate_square(square=square, angle=PI, axis=axis)
```

### Pattern: e^{it} as Perpendicular Vectors on Unit Circle

**What**: A position vector (YELLOW) and velocity vector (RED) on the complex plane. The velocity is created as a 90-degree rotation of the position vector. Both rotate together via Rotating animation, tracing the unit circle. The equation d(e^{it})/dt = i*e^{it} is displayed with matching colors.

**When to use**: Complex exponential visualization, circular motion explanation, harmonic oscillator phase space, any scenario connecting rotation to perpendicularity.

```python
# Source: projects/videos/_2017/efvgt.py:296-332
s_vector = Arrow(ORIGIN, right, tip_length=0.2, buff=0, color=self.position_color)
v_vector = s_vector.copy().rotate(PI/2)
v_vector.set_color(self.velocity_color)
circle = Circle(radius=self.z_to_point(1)[0], color=self.position_color)

self.play(ShowCreation(s_vector))
self.play(ReplacementTransform(s_vector.copy(), v_vector, path_arc=PI/2))
self.play(v_vector.shift, right)
# Rotate both together
self.vectors = VGroup(s_vector, v_vector)
rotation = Rotating(self.vectors, about_point=ORIGIN, run_time=5, rate_func=None)
self.play(ShowCreation(circle, run_time=5, rate_func=None), rotation)
```

## Scene Flow

1. **Anniversary Celebration** (0-20s): Title "2 year Anniversary!" PartyHats on pi creatures. Confetti spirals. Formula e^{pi*i}=-1 in first_video rectangle.
2. **Groups and Symmetry** (20-40s): Title "Groups <-> Symmetry." Blue square appears. DrawBorderThenFill. Question marks with brace.
3. **90-Degree Rotation** (40-60s): Arcs show rotation. Square rotates. Then vertical flip demonstrated.
4. **Confusion Without Labels** (60-80s): Randolph confused — can't tell rotations apart. Face added to square to track orientation.
5. **Full Group Display** (80-120s): 8 symmetries in grid. Rotations demonstrated with there_and_back. Reflections demonstrated similarly. "Dihedral group of order 8" named.
6. **e^{it} Quick Explanation** (120-160s): Equation displayed. Position and velocity vectors. 90-degree relationship shown. Rotating animation traces unit circle three times. Words explain: "only a walk at rate 1 satisfies both e^0=1 and this derivative property."
