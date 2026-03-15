---
source: https://github.com/3b1b/videos/blob/main/_2025/spheres/volumes.py
project: videos
domain: [geometry, calculus, mathematics, topology]
elements: [sphere, circle, axes, formula, equation, label, grid, surrounding_rect, brace, arrow, line]
animations: [write, transform, replacement_transform, transform_from_copy, fade_in, fade_out, highlight, indicate, rotate, camera_rotate, grow]
layouts: [grid, centered, vertical_stack]
techniques: [three_d_camera, custom_mobject, progressive_disclosure, always_redraw, helper_function]
purpose: [derivation, step_by_step, demonstration, progression]
mobjects: [Sphere, SurfaceMesh, Circle, Square, Line, VGroup, Tex, Text, Integer, SurroundingRectangle, Arrow, Polygon]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, FadeTransform, TransformMatchingTex, TransformFromCopy, ReplacementTransform, Rotate]
scene_type: InteractiveScene
manim_version: manimlib
complexity: intermediate
lines: 1210
scene_classes: [CircumferenceToArea, SurfaceAreaToVolume, VolumeGrid, ShowCircleAreaDerivative, CircleDerivativeFormula, BuildCircleWithCombinedAnnulusses, ShowSphereVolumeDerivative, SphereDerivativeFormula, SimpleLineWithEndPoints, ZAxisWithCircle, SeparateRingsOfLatitude, CrossLineWithCircle, CrossDiskWithCircle, CrossBallWithCircle, ShowNumericalValues, WriteB100Volume, SphereEquator, Distributions, UnitCircleAndSquare, UniSphereAndSquare]
---

## Summary

Explores the volume of n-dimensional spheres, building from the familiar circle (circumference -> area via nested rings) and 3D sphere (surface area -> volume via nested shells) to the general formula V(B^n) = pi^(n/2) / (n/2)! * r^n. Uses a dimension grid showing boundary and volume formulas for dimensions 0-9, a "knight's move" recursion pattern (b_n = 2*pi/n * b_{n-2}), and 3D visualizations of sphere slicing. The recursion is demonstrated step by step with animated arrows between even-indexed columns.

## Design Decisions

- **Circumference -> area by nested circles**: 100 concentric circles of decreasing radius, yellow with low opacity, show how integrating circumferences gives area. Same pattern repeated for sphere surface -> volume with nested transparent shells.
- **Dimension grid (2 rows x 10 cols)**: Top row = boundary formula (surface), bottom row = volume formula. This tabular layout makes the recursion pattern (knight's move from column n-2) visually obvious.
- **Knight's move recursion**: An L-shaped arrow group jumps from column n-2 to column n, mirroring the b_n = 2*pi/n * b_{n-2} recurrence. The chess metaphor makes an abstract recursion physically intuitive.
- **Color coding b_n in YELLOW**: Volume constants b_n are consistently YELLOW throughout equations and grid highlights. The radius r is always BLUE.
- **Progressive formula derivation**: Start with specific cases (d=2,3), show derivative/integral relationship, add more dimensions one at a time, then derive general formula. Never shows the final formula without building to it.
- **3D sphere with clip_plane**: Inner spheres (50 concentric) clipped by a moving plane to show the cross-section. set_clip_plane(IN, z) reveals the internal structure.

## Composition

- **Grid layout**: Square().get_grid(2, n_cols) for the dimension table. 10 columns, 2 rows.
  - Row labels: Tex(R"\partial B^n") and Tex(R"B^n") to the LEFT
  - Column labels: Integer(n) above each column
  - "Dimension" title above column labels, to_edge(UP, buff=MED_SMALL_BUFF)
- **Sphere scene**: Sphere radius=3, BLUE at 0.5 opacity. Mesh resolution (51,26), WHITE stroke width=2 opacity=0.2. Camera at (44, 56, 0).
- **Circle scene**: Circle radius=3, YELLOW stroke width=5. Radius line WHITE width=3. r label BLUE font_size=72.
- **Formula positions**: gen_formula and recursion at bottom corners. Final formula next_to grid DOWN buff=2.25.
- **Recursion arrows**: path_arc=120 DEG, between every-other column bottom edges.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Circle/sphere boundary | YELLOW | stroke_width=5 (circle), 3 (sphere grid) |
| Radius r | BLUE | In all equations via t2c |
| Volume constants b_n | YELLOW | In all equations via t2c |
| Grid cell highlight | TEAL_E | fill_opacity=0.5, temporary |
| Question marks | YELLOW | font_size=72, for unknown cells |
| Knight's move source cell | RED | fill_opacity=0.35 |
| Inner spheres | BLUE | opacity=0.2, clipped |
| Sphere mesh | WHITE | stroke 2 width, 0.2 opacity |
| Recursion arrows | default | path_arc=120 DEG |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Circle creation with rotation | run_time=3 | ShowCreation + Rotate simultaneously |
| Nested circles reveal | run_time=3 | ReplacementTransform with lag_ratio=0.1 |
| Sphere ShowCreation + mesh | run_time=2 | Simultaneous |
| Inner sphere creation | run_time=3 | lag_ratio=0.5 |
| Cell highlight | run_time=3 | there_and_back_with_pause rate_func |
| Grid question marks | lag_ratio=0.05 | Write with grid columns |
| Knight's move step | varies | FadeIn + TransformMatchingTex pairs |
| Recursion example stages | run_time=1 each | TransformMatchingTex with key_map |

## Patterns

### Pattern: Nested Shapes Integration (Circumference -> Area)

**What**: Generate many concentric copies of a shape at decreasing scales, then reveal them in sequence. This physically demonstrates that integrating the boundary formula gives the volume formula (e.g., integrating 2*pi*r gives pi*r^2).

**When to use**: Calculus derivations, showing how area/volume builds from boundary, integration as accumulation, any "sum of shells/rings" argument.

```python
# Source: projects/videos/_2025/spheres/volumes.py:60-73
circles = VGroup(
    circle.copy().set_width(a * circle.get_width())
    for a in np.linspace(1, 0, 100)
)
circles.set_stroke(YELLOW, 3, 0.25)
self.play(
    ReplacementTransform(
        circle.replicate(len(circles)).set_stroke(width=0, opacity=0),
        circles,
        lag_ratio=0.1
    ),
    run_time=3
)
```

### Pattern: Dimension Grid with Progressive Reveal

**What**: A 2-row x N-column grid (Square().get_grid) with boundary formulas in the top row and volume formulas in the bottom row. Cells are revealed progressively with highlighting (TEAL_E fill), and a knight's-move arrow shows the recursion relationship between columns n-2 and n.

**When to use**: Tabular mathematical relationships, recursion visualization, dimension-indexed formulas, any pattern that emerges across a series of related quantities.

```python
# Source: projects/videos/_2025/spheres/volumes.py:113-157
grid = self.get_grid(n_cols)  # Square().get_grid(2, n_cols)

# Highlight a cell temporarily
def highlight_cell(row, col, run_time=3, fill_color=TEAL_E, fill_opacity=0.5):
    kw = dict(rate_func=there_and_back_with_pause, run_time=run_time)
    cell = grid[col][row]
    return cell.animate.set_fill(fill_color, fill_opacity).set_anim_args(**kw)

# Knight's move group shows recursion
knight_group = self.get_knights_move_group(grid, 3)
self.play(FadeIn(knight_group))
```

### Pattern: TransformMatchingTex for Step-by-Step Recursion

**What**: A sequence of Tex equations where each step substitutes one term, animated with TransformMatchingTex using key_map to specify which symbols correspond across equations. Demonstrates recursive unrolling (b_8 -> b_6 -> b_4 -> b_2 -> b_0).

**When to use**: Recursive formula derivation, algebraic simplification steps, any chain of substitutions where you want the viewer to track which parts change.

```python
# Source: projects/videos/_2025/spheres/volumes.py:346-416
stages = VGroup(
    Tex(R"b_8 = {\pi \over 4} b_6"),
    Tex(R"b_8 = {\pi \over 4} {\pi \over 3} b_4"),
    Tex(R"b_8 = {\pi \over 4} {\pi \over 3} {\pi \over 2} b_2"),
    Tex(R"b_8 = {\pi \over 4} {\pi \over 3} {\pi \over 2} {\pi \over 1} b_0"),
)
# Each stage highlights b_n in YELLOW
for stage in stages:
    stage[re.compile(r"b_.")].set_color(YELLOW)

self.play(TransformMatchingTex(
    stages[0], stages[1],
    key_map={"b_6": "b_4"},
    run_time=1
))
```

### Pattern: 3D Sphere with Clip Plane for Cross-Section

**What**: Multiple concentric transparent spheres with a movable clip plane that reveals internal structure. set_clip_plane(IN, z) cuts away everything behind the plane. Animating z from 0 to radius reveals or hides the cross-section.

**When to use**: Sphere slicing, 3D cross-section visualization, internal structure revelation, any solid of revolution where you need to show internal geometry.

```python
# Source: projects/videos/_2025/spheres/volumes.py:96-110
inner_spheres = Group(
    sphere.copy().set_width(a * sphere.get_width())
    for a in np.linspace(0, 1, 50)
)
inner_spheres.set_color(BLUE, 0.2)
inner_spheres.set_clip_plane(IN, 0)

self.play(ShowCreation(inner_spheres, lag_ratio=0.5, run_time=3))
self.play(inner_spheres.animate.set_clip_plane(IN, radius), run_time=2)
```

## Scene Flow

1. **Circle: circumference -> area** (0-10s): Circle drawn with rotating radius. 100 nested circles appear, filling the interior. Shows 2*pi*r integrates to pi*r^2.
2. **Sphere: surface -> volume** (10-20s): 3D sphere with mesh. 50 nested shells revealed, then clip plane slices to show cross-section.
3. **Dimension grid** (20-120s): 2x10 grid built progressively. d=2,3 filled first. Derivative/integral relationship shown. Knight's move reveals recursion. Question marks for d>=4. Each dimension filled using the recursion.
4. **Volume constants** (120-180s): General formula V(B^n) = b_n * r^n. Individual b_n values highlighted. Recursion b_n = 2*pi/n * b_{n-2}.
5. **Recursion unrolling** (180-220s): b_8 expanded step by step to pi^4/4!. General formula b_n = pi^(n/2)/(n/2)! derived.
6. **Final formula** (220-240s): V(B^n) = pi^(n/2)/(n/2)! * r^n displayed with SurroundingRectangle.
