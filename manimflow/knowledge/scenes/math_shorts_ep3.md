---
source: https://github.com/tharun0x/manim-projects/blob/main/2025/shorts/Nov25/episode3.py
project: manim-projects
domain: [mathematics, geometry]
elements: [title, label, equation, formula, brace, line, dot, arrow]
animations: [write, fade_in, fade_out, transform, replacement_transform, draw, indicate, grow_from_center, rotate]
layouts: [centered, vertical_stack, edge_anchored]
techniques: [custom_animation]
purpose: [derivation, step_by_step, demonstration]
mobjects: [Text, Tex, Polygon, VGroup, Brace, DashedLine, Square, Line]
manim_animations: [Write, FadeIn, FadeOut, DrawBorderThenFill, ShowCreation, TransformFromCopy, ReplacementTransform, MoveToTarget, Rotate]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 420
scene_classes: [Episode3]
---

## Summary

Derives the triangle area formula (1/2 x b x h) from first principles using a geometric proof. A triangle is duplicated and rotated 180 degrees around an edge midpoint to form a parallelogram, proving that the triangle is half the parallelogram's area. The derivation builds step-by-step from "parallelogram area = b x h" through algebraic rearrangement to the final formula. Includes a worked example (base=8, height=5) and a timed challenge (base=12, height=7).

## Design Decisions

- **Geometric proof via rotation**: The copy of the triangle rotates PI radians about the hypotenuse midpoint to form a parallelogram, making the "half" relationship visually obvious.
- **TransformFromCopy for equation derivation**: Each algebraic step copies relevant parts from previous lines and transforms them into the next step, showing where each piece comes from. This creates a visual audit trail.
- **DashedLine for height**: The perpendicular height uses DashedLine to distinguish it from the triangle edges. A small Square marker at the foot shows the right angle.
- **TEAL for triangles, WHITE for annotations**: The triangle fill uses TEAL at low opacity (0.3-0.5), while measurement labels and formulas stay white for readability.
- **Manual fraction construction**: Rather than using MathTex fractions directly for the derivation, constructs the fraction visually with a Line separator, numerator above, and denominator below, so each piece can be independently animated from its source.

## Composition

- **Hook**: Title Text(font_size=30, fill_color=RED) at `to_edge(UP, buff=1.5)`. Formula Tex(font_size=30, fill_color=BLUE) next_to title DOWN, buff=0.2.
- **Triangle**: Polygon with vertices at LEFT*0.75+DOWN*1, RIGHT*0.75+DOWN*1, UP*0.5+RIGHT*0.5. fill_opacity=0.3, color=TEAL.
- **Base brace**: Brace along bottom edge, DOWN, buff=0.1. Label Tex("b", font_size=40, fill_color=TEAL).
- **Height line**: DashedLine from apex straight down to base level, stroke_width=3. Label Tex("h", font_size=40) to LEFT, buff=0.15.
- **Right angle marker**: Square(side_length=0.15) at foot of perpendicular.
- **Parallelogram group**: Shifted UP * 1.5 after formation.
- **Equation lines**: Each at font_size=30, stacked DOWN with buff=0.3-0.8 below the geometry.
- **Example triangle**: Larger polygon at ORIGIN, shifted UP * 0.5.
- **Clock**: Circle(radius=0.5, stroke_color=TEAL) at next_to(triangle, DOWN, buff=1.2).

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Triangle fill | TEAL | fill_opacity=0.3 |
| Triangle copy | TEAL_C | stroke_opacity=0.7 |
| Base label "b" | TEAL | font_size=40 |
| Height label "h" | WHITE | font_size=40 |
| Height line | WHITE | DashedLine, stroke_width=3 |
| Right angle marker | WHITE | Square, stroke_width=2 |
| Parallelogram symbol | WHITE | stroke_width=2 |
| Area equations | WHITE | font_size=30 |
| Final formula | RED | fill_color |
| Faint background triangle | TEAL | fill_opacity=0.5, stroke_opacity=0.3 |
| Title/prompts | RED | fill_color |
| Clock face | TEAL | stroke_color |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + formula write | run_time=1.5 each | |
| DrawBorderThenFill triangle | run_time=1 | |
| Base brace + label | run_time=0.5 | |
| Height line ShowCreation | run_time=1 | |
| TransformFromCopy duplicate | run_time=1 | |
| Rotate copy PI | run_time=1.5 | about_point=midpoint_edge |
| MoveToTarget center | run_time=1 | |
| Each equation TransformFromCopy | run_time=0.6-0.8 | |
| ReplacementTransform to final | run_time=1.5 | |
| Example solve steps | 0.3-1.0s each | |
| Clock timer | run_time=5 | |
| Total video | ~90 seconds | |

## Patterns

### Pattern: Duplicate-and-Rotate Geometric Proof

**What**: Creates a copy of a polygon, computes the midpoint of a shared edge, then rotates the copy 180 degrees about that midpoint to form a larger shape (parallelogram from two triangles). Visually proves area relationships.

**When to use**: Geometric proofs involving area doubling/halving, showing that two congruent shapes tile into a known shape. Triangle-to-parallelogram, parallelogram-to-rectangle proofs. Any derivation where duplicating and rearranging a shape reveals a simpler formula.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode3.py:58-78
triangle_copy = triangle.copy()
triangle_copy.set_color(TEAL_C)
triangle_copy.set_style(stroke_opacity=0.7)

verts = triangle.get_vertices()
v1, v2, v3 = verts[0], verts[1], verts[2]
midpoint_edge = np.array([(v2[0] + v3[0]) / 2, (v2[1] + v3[1]) / 2, 0])

self.play(TransformFromCopy(triangle, triangle_copy), run_time=1)
self.play(
    Rotate(triangle_copy, PI, about_point=midpoint_edge),
    run_time=1.5
)
```

### Pattern: Step-by-Step Equation Derivation with TransformFromCopy

**What**: Builds an algebraic derivation line by line, where each new equation element is a TransformFromCopy from the relevant part of the previous line. This shows the viewer exactly which pieces map to which in each step.

**When to use**: Any algebraic derivation or proof, formula manipulation, step-by-step equation solving. Especially effective when you want to show where each term comes from during simplification or rearrangement.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode3.py:124-148
# Line: b x h = 2 x triangle Area
bxh_copy = Tex(r"b \times h", font_size=30, fill_color=WHITE)
bxh_copy.move_to(eq_pos + LEFT * 1)
self.play(TransformFromCopy(para_area_text, bxh_copy), run_time=0.8)

equals_sign = Tex(r"=", font_size=30)
equals_sign.next_to(bxh_copy, RIGHT, buff=0.15)
self.play(Write(equals_sign), run_time=0.3)

tri_area_copy = Tex(r"2 \times \triangle \ Area", font_size=30)
tri_area_copy.next_to(equals_sign, RIGHT, buff=0.15)
self.play(TransformFromCopy(para_area_text2, tri_area_copy), run_time=0.8)
```

### Pattern: Perpendicular Height with Right Angle Marker

**What**: Draws a DashedLine from a triangle's apex vertically down to the base line, then places a small Square at the foot to indicate a right angle. The foot position is computed by projecting the apex x-coordinate onto the base y-coordinate.

**When to use**: Any triangle area visualization, perpendicular distance indicators, altitude construction. Geometry proofs where the height must be explicitly shown and labeled.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode3.py:29-54
vertices = triangle.get_vertices()
apex_pos = vertices[2]
base_y = vertices[0][1]
foot = np.array([apex_pos[0], base_y, 0])

height_line = DashedLine(apex_pos, foot, color=WHITE, stroke_width=3)
height_label = Tex("h", font_size=40, fill_color=WHITE)
height_label.next_to(height_line, LEFT, buff=0.15)

right_angle = Square(side_length=0.15, color=WHITE, stroke_width=2)
right_angle.move_to(foot + UP * 0.075 + LEFT * 0.075)
```

## Scene Flow

1. **Hook** (0-3s): "Why area of any triangle is 1/2 x b x h?" title and formula write in.
2. **Triangle setup** (3-8s): Triangle draws with TEAL fill. Base brace with "b", height DashedLine with "h", right angle marker appear.
3. **Parallelogram proof** (8-16s): Triangle duplicates via TransformFromCopy. Copy rotates PI around edge midpoint. Group centers upward.
4. **Area derivation** (16-28s): "Parallelogram Area = b x h" appears. Then "= 2 x Triangle Area". Then "b x h = 2 x Triangle Area". Then "Triangle Area = (b x h) / 2". Final formula "Triangle Area = 1/2 x b x h" in RED via ReplacementTransform.
5. **Worked example** (28-42s): New triangle (base=8, height=5). Formula recalled. Values plugged in step-by-step via TransformFromCopy. "= 40/2 = 20 units^2".
6. **Challenge** (42-52s): "TRY THIS!" with triangle (base=12, height=7). Clock timer 5 seconds.
7. **CTA** (52-56s): LIKE/SHARE/SUBSCRIBE cascade, staggered exit.
