---
source: https://github.com/tharun0x/manim-projects/blob/main/2026/feb/episode4.py
project: manim-projects
domain: [mathematics, algebra, geometry]
elements: [title, label, equation, formula, brace, line, rectangle_node, grid]
animations: [write, fade_in, fade_out, transform, replacement_transform, indicate, grow_from_center, rotate]
layouts: [centered, vertical_stack, edge_anchored, grid, side_by_side]
techniques: [custom_animation]
purpose: [derivation, step_by_step, demonstration, exploration]
mobjects: [Text, Tex, VGroup, Square, Rectangle, Cross, DashedLine, Brace, Circle, Line]
manim_animations: [Write, FadeIn, FadeOut, ShowCreation, Transform, ReplacementTransform, TransformFromCopy, Indicate, GrowFromCenter, Rotate]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 292
scene_classes: [Episode4]
---

## Summary

Derives the (a+b)^2 expansion using a geometric square decomposition. Starts by crossing out the common misconception "(a+b)^2 = a^2 + b^2", then builds a square of side (a+b), splits it with dashed lines into a 2x2 grid, and color-fills each region (a^2 in TEAL, b^2 in GOLD, two ab rectangles in GREEN_C). The formula assembles from the geometry via TransformFromCopy. Includes a numerical example (13^2 = (10+3)^2 = 169) with the same grid approach, plus a timed challenge (21^2).

## Design Decisions

- **Cross out wrong formula first**: Opens with the common mistake "(a+b)^2 = a^2 + b^2" then draws a Cross over it. This hooks the viewer by challenging a misconception before revealing the correct answer.
- **Line-to-Square transformation**: A horizontal line segment representing (a+b) Transforms into the full square, showing that squaring literally means making a square from the length.
- **Color-coded regions**: TEAL for a^2, GOLD for b^2, GREEN_C for both ab rectangles. The formula terms inherit these colors, creating a direct visual mapping between geometry and algebra.
- **Numerical grid reuses the same layout**: The 13^2 example uses identical colored squares and rectangles (2.0 and 1.2 side lengths mapping to 10 and 3), reinforcing the pattern.
- **Braces with labeled dimensions**: Every segment of the square's edge gets a Brace with its variable name, so the viewer can trace dimensions to area terms.

## Composition

- **Square dimensions**: a_val=2.0, b_val=1.2, total=3.2. Square centered at ORIGIN.
- **Split lines**: DashedLine vertical at x = sq_left + a_val, horizontal at y = sq_top - a_val. stroke_width=2.
- **a^2 square**: Square(side_length=2.0), fill_color=TEAL, fill_opacity=0.7, stroke_width=0. Top-left region.
- **b^2 square**: Square(side_length=1.2), fill_color=GOLD, fill_opacity=0.7, stroke_width=0. Bottom-right region.
- **ab rectangles**: Rectangle(width=1.2, height=2.0) and Rectangle(width=2.0, height=1.2), fill_color=GREEN_C, fill_opacity=0.7.
- **Braces**: "a" brace under left segment, "b" brace under right segment, buff=0.1. Labels Tex(font_size=45).
- **Formula row**: Arranged RIGHT, buff=0.15, at next_to(geometry, DOWN, buff=0.8).
- **Numerical grid center**: DOWN * 0.5.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Wrong equation | RED | fill_color |
| Cross | RED | stroke_width=8 |
| Main square outline | WHITE | stroke_width=3 |
| Split lines | WHITE | DashedLine, stroke_width=2 |
| a^2 region | TEAL | fill_opacity=0.7, stroke_width=0 |
| b^2 region | GOLD | fill_opacity=0.7, stroke_width=0 |
| ab rectangles | GREEN_C | fill_opacity=0.7, stroke_width=0 |
| ab rect outline | GREEN | stroke_width=2 |
| "a" label | TEAL | font_size=45 |
| "b" label | GOLD | font_size=45 |
| Formula a^2 | TEAL | font_size=50 |
| Formula 2ab | GREEN_C | font_size=50 |
| Formula b^2 | GOLD | font_size=50 |
| Line segment | BLUE | stroke_width=6 |
| "Try this!" | BLUE | fill_color |
| Clock face | TEAL | stroke_color |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Wrong eq Write | run_time=1.5 | |
| Cross ShowCreation | run_time=1.0 | |
| ReplacementTransform to question | run_time=1.0 | |
| Line ShowCreation | run_time=1.0 | |
| Braces GrowFromCenter | run_time=1.0 | |
| Line to Square Transform | run_time=2.0 | |
| Vertical split line | run_time=1.0 | |
| Horizontal split line | run_time=1.0 | |
| a^2 FadeIn + label | run_time=1.5 | |
| b^2 FadeIn + label | run_time=1.5 | |
| ab Indicate + label | run_time=1.0 each | |
| Formula assembly | 0.2-0.6s per piece | TransformFromCopy |
| Full formula Write | run_time=1.0 | |
| Numerical example total | ~12s | |
| Clock timer | run_time=5 | |
| Total video | ~75 seconds | |

## Patterns

### Pattern: Misconception Hook with Cross

**What**: Opens by writing a commonly believed but incorrect equation, then draws a Cross over it, and ReplacementTransforms to the correct question form. Immediately engages the viewer by challenging what they think they know.

**When to use**: Educational content debunking common mistakes, any "most people get this wrong" hook for math shorts. Opening scenes that need to establish the problem by showing what NOT to do.

```python
# Source: projects/manim-projects/2026/feb/episode4.py:13-27
wrong_eq = Tex("(a + b)^2 = a^2 + b^2", font_size=50, fill_color=RED)
wrong_eq.move_to(ORIGIN)
self.play(Write(wrong_eq), run_time=1.5)

cross = Cross(wrong_eq, stroke_color=RED, stroke_width=8)
self.play(ShowCreation(cross), run_time=1.0)

question = Tex("(a + b)^2 =\ ?", font_size=50, fill_color=WHITE)
question.move_to(ORIGIN)
self.play(
    FadeOut(cross),
    ReplacementTransform(wrong_eq, question),
    run_time=1.0
)
```

### Pattern: Color-Coded Square Decomposition Grid

**What**: Builds a square of side (a+b), splits it with dashed lines into 4 regions, and fills each with a distinct color matching the algebraic term it represents. Labels go inside each region. The formula is assembled by TransformFromCopy from each label.

**When to use**: Algebraic identity proofs via geometry ((a+b)^2, (a-b)^2, difference of squares), area decomposition visualizations, any scenario where a square or rectangle is partitioned into labeled sub-regions.

```python
# Source: projects/manim-projects/2026/feb/episode4.py:63-106
# Split with dashed lines
v_line = DashedLine(
    np.array([split_x, sq_top, 0]),
    np.array([split_x, sq_bottom, 0]),
    stroke_color=WHITE, stroke_width=2
)
h_line = DashedLine(
    np.array([sq_left, split_y, 0]),
    np.array([sq_right, split_y, 0]),
    stroke_color=WHITE, stroke_width=2
)

# Fill regions with color
a_sq = Square(side_length=a_val, fill_color=TEAL, fill_opacity=0.7, stroke_width=0)
a_sq.move_to(np.array([sq_left + a_val/2, sq_top - a_val/2, 0]))
a_sq_label = Tex("a^2", font_size=45, fill_color=WHITE).move_to(a_sq)

b_sq = Square(side_length=b_val, fill_color=GOLD, fill_opacity=0.7, stroke_width=0)
b_sq.move_to(np.array([sq_right - b_val/2, sq_bottom + b_val/2, 0]))

ab_rect1 = Rectangle(width=b_val, height=a_val, stroke_color=GREEN, stroke_width=2)
ab_rect1.move_to(np.array([sq_right - b_val/2, sq_top - a_val/2, 0]))
```

### Pattern: Formula Assembly from Geometry Labels

**What**: Each term in the final algebraic formula is created by TransformFromCopy from the corresponding label in the geometric figure. Plus signs are written between terms. Then all terms ReplacementTransform into the full formatted equation with the left-hand side added.

**When to use**: Any derivation where you want to show the geometric-to-algebraic mapping explicitly. Building formulas piece by piece from visual evidence. Connecting spatial intuition to symbolic representation.

```python
# Source: projects/manim-projects/2026/feb/episode4.py:116-141
eq_parts = VGroup(
    Tex("a^2", font_size=50, fill_color=TEAL),
    Tex("+", font_size=50),
    Tex("2ab", font_size=50, fill_color=GREEN_C),
    Tex("+", font_size=50),
    Tex("b^2", font_size=50, fill_color=GOLD)
).arrange(RIGHT, buff=0.15)
eq_parts.next_to(geometry, DOWN, buff=0.8)

self.play(TransformFromCopy(a_sq_label, eq_parts[0]), run_time=0.6)
self.play(Write(eq_parts[1]), run_time=0.2)
self.play(TransformFromCopy(VGroup(ab_label1, ab_label2), eq_parts[2]), run_time=0.6)
self.play(Write(eq_parts[3]), run_time=0.2)
self.play(TransformFromCopy(b_sq_label, eq_parts[4]), run_time=0.6)

full_formula = Tex("(a + b)^2", "=", "a^2", "+", "2ab", "+", "b^2", font_size=40)
full_formula[2].set_color(TEAL)
full_formula[4].set_color(GREEN_C)
full_formula[6].set_color(GOLD)
self.play(
    ReplacementTransform(eq_parts, full_formula[2:]),
    Write(full_formula[:2]),
)
```

## Scene Flow

1. **Hook** (0-5s): Wrong formula "(a+b)^2 = a^2 + b^2" writes in RED. Cross drawn over it. Transforms to "(a+b)^2 = ?".
2. **Line to Square** (5-12s): Horizontal line appears with "a" and "b" braces. Line Transforms into a square.
3. **Grid split** (12-16s): Vertical and horizontal DashedLines split the square into 4 regions.
4. **Fill regions** (16-24s): a^2 (TEAL) and b^2 (GOLD) squares FadeIn with labels. Two ab rectangles (GREEN_C) Indicated and filled.
5. **Formula assembly** (24-30s): Geometry shifts up. a^2 + 2ab + b^2 built from TransformFromCopy. Full "(a+b)^2 = a^2 + 2ab + b^2" formed.
6. **Numerical example** (30-48s): "13^2 = (10+3)^2" with same grid approach. 100 + 2(30) + 9 = 169 shown, then mapped back to a^2 + 2ab + b^2.
7. **Challenge** (48-56s): "21^2 = (20+1)^2" with clock timer.
8. **CTA** (56-60s): LIKE/SHARE/SUBSCRIBE cascade exit.
