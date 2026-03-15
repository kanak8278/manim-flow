---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/euclidian.py
project: manim-animations
domain: [mathematics, geometry, linear_algebra]
elements: [axes, dot, line, dashed_line, label, equation]
animations: [write, fade_in, draw]
layouts: [split_screen, edge_anchored]
techniques: [progressive_disclosure]
purpose: [derivation, demonstration, step_by_step]
mobjects: [Axes, Dot, Line, DashedLine, MathTex, Text, VGroup]
manim_animations: [Write, Create, FadeIn]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 91
scene_classes: [EuclideanDistance]
---

## Summary

Visualizes the Euclidean distance formula between two points on a 2D coordinate plane. Two colored dots (BLUE and RED) are connected by a YELLOW hypotenuse line, with GREEN dashed lines showing the horizontal and vertical components forming a right triangle. A step-by-step derivation on the right side walks through the formula substitution from general form to the final sqrt(10) result.

## Design Decisions

- **Split-screen layout**: Axes shifted LEFT*4 with equation derivation at RIGHT*4. This separates the geometric visualization from the algebraic derivation, letting the viewer see both simultaneously. Mirrors the textbook convention of "diagram on left, work on right."
- **Color-coded points (BLUE vs RED)**: Two distinct colors make the points immediately distinguishable. The labels (x1,y1) and (x2,y2) reinforce which is which.
- **YELLOW hypotenuse, GREEN components**: The hypotenuse (the distance being computed) stands out in YELLOW against the GREEN dashed component lines. Dashed lines signal "construction lines" — auxiliary visual aids, not the main result.
- **Step-by-step equation chain**: Five equations stack vertically, each Write'd sequentially. This progressive disclosure matches how a teacher would write the derivation on a whiteboard.
- **Custom tick labels (x1, x2, y1, y2)**: Instead of numeric axis ticks, the tick positions show the symbolic coordinates. This connects the geometric positions to the algebraic variables.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Euclidean Distance"
  - Axes: `shift(LEFT * 4)`, x_length=5, y_length=5, tips=True
  - Equation derivation: starts at `RIGHT * 4 + UP * 2`, each step `next_to(prev, DOWN)`
  - Point labels: `next_to(dot, LEFT/RIGHT)`
- **Axes configuration**: x_range=[0, 6, 1], y_range=[0, 6, 1], x_length=5, y_length=5
- **Points**: dot1 at (2, 3), dot2 at (5, 4)
- **Custom ticks**: x_ticks at x=2 ("x_1") and x=5 ("x_2"), y_ticks at y=3 ("y_1") and y=4 ("y_2"), offset by TICKS_AXES_GAP=0.5
- **Component lines**: h_line from (2,3) to (5,3), v_line from (5,3) to (5,4)
- **Equation font sizes**: FONT_SIZE=28 for labels, EQ_FONT_SIZE=32 for derivation

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Point 1 | BLUE | Dot at (2, 3) |
| Point 2 | RED | Dot at (5, 4) |
| Hypotenuse line | YELLOW | Solid Line, buff=0.1 |
| Horizontal component | GREEN | DashedLine |
| Vertical component | GREEN | DashedLine |
| Component labels | GREEN | "x_2 - x_1", "y_2 - y_1" |
| Distance label | YELLOW | "sqrt(10)" on the hypotenuse |
| Equations | WHITE | font_size=32 |
| Axes | WHITE | With tips |
| Custom tick labels | WHITE | font_size=28 |

Color strategy: Three-color system — BLUE/RED for the two points (input), YELLOW for the distance (output), GREEN for the construction (intermediate computation). Each color maps to a conceptual role.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=2 | + 1s wait |
| Axes + labels Create | run_time=2 | + 1s wait |
| Tick labels FadeIn | ~1s | + 1s wait |
| Dots + labels FadeIn | ~1s | + 1s wait |
| Hypotenuse Create | ~1s | + 1s wait |
| Component lines Create | ~1s | Simultaneous h_line + v_line |
| Component labels Write | ~1s | + 1s wait |
| Each equation step Write | ~1s | 5 steps sequential |
| Distance label Write | ~1s | |
| Total video | ~22 seconds | |

## Patterns

### Pattern: Right Triangle Decomposition

**What**: Show the distance between two points by drawing the hypotenuse (solid, colored) and then the horizontal and vertical components (dashed, different color). This decomposes the diagonal distance into orthogonal components, setting up the Pythagorean theorem visually.
**When to use**: Euclidean distance derivation, Pythagorean theorem, vector decomposition into components, any situation where a diagonal measurement should be broken into horizontal and vertical parts.

```python
# Source: projects/manim-animations/src/euclidian.py:35-46
line = Line(dot1.get_center(), dot2.get_center(), color=YELLOW, buff=0.1)

h_line = DashedLine(start=dot1.get_center(), end=axes.c2p(5, 3), color=GREEN)
h_line_text = MathTex(
    "x_2 - x_1", font_size=FONT_SIZE, color=GREEN
).next_to(h_line, DOWN, buff=0.2)

v_line = DashedLine(start=axes.c2p(5, 3), end=dot2.get_center(), color=GREEN)
v_line_text = MathTex(
    "y_2 - y_1", font_size=FONT_SIZE, color=GREEN
).next_to(v_line, RIGHT, buff=0.2)
```

### Pattern: Sequential Equation Derivation

**What**: Stack equations vertically, each positioned `next_to(previous, DOWN)`. Write them one at a time to show the derivation step by step. Each equation simplifies from the previous one.
**When to use**: Any mathematical derivation, proof steps, formula substitution walkthrough. Works for distance formulas, calculus derivations, algebraic simplifications.

```python
# Source: projects/manim-animations/src/euclidian.py:48-67
step1 = MathTex(
    "d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}", font_size=EQ_FONT_SIZE
).shift(RIGHT * 4 + UP * 2)

step2 = MathTex(
    "d = \sqrt{(5 - 2)^2 + (4 - 3)^2}", font_size=EQ_FONT_SIZE
).next_to(step1, DOWN)

step3 = MathTex("d = \sqrt{3^2 + 1^2}", font_size=EQ_FONT_SIZE).next_to(step2, DOWN)
step4 = MathTex("d = \sqrt{9 + 1}", font_size=EQ_FONT_SIZE).next_to(step3, DOWN)
step5 = MathTex("d = \sqrt{10}", font_size=EQ_FONT_SIZE).next_to(step4, DOWN)
```

### Pattern: Custom Symbolic Axis Ticks

**What**: Instead of numeric tick marks, place symbolic labels (x_1, x_2, y_1, y_2) at specific axis positions. Uses MathTex positioned via axes.c2p() with a small gap offset. This connects the plotted points to the algebraic variables.
**When to use**: When exact numeric values matter less than the symbolic relationship. Useful for geometry proofs, generic formula demonstrations, or any diagram where variables rather than numbers should label the axes.

```python
# Source: projects/manim-animations/src/euclidian.py:20-27
x_ticks = VGroup(
    MathTex("x_1", font_size=FONT_SIZE).move_to(axes.c2p(2, TICKS_AXES_GAP)),
    MathTex("x_2", font_size=FONT_SIZE).move_to(axes.c2p(5, TICKS_AXES_GAP)),
)
y_ticks = VGroup(
    MathTex("y_1", font_size=FONT_SIZE).move_to(axes.c2p(TICKS_AXES_GAP, 3)),
    MathTex("y_2", font_size=FONT_SIZE).move_to(axes.c2p(TICKS_AXES_GAP, 4)),
)
```

## Scene Flow

1. **Setup** (0-4s): Title "Euclidean Distance" writes. Axes with tips create on the left side.
2. **Points and labels** (4-7s): Custom tick labels (x1, x2, y1, y2) fade in. Blue dot at (2,3) and red dot at (5,4) fade in with coordinate labels.
3. **Hypotenuse** (7-9s): Yellow line connects the two dots.
4. **Right triangle** (9-11s): Green dashed horizontal and vertical lines create, forming a right triangle. Component difference labels write.
5. **Derivation** (11-18s): Five equation steps write sequentially on the right: general formula, substitution, simplification, arithmetic, final result sqrt(10).
6. **Result** (18-22s): Distance label "sqrt(10)" writes on the hypotenuse. Hold 2s.

> Full file: `projects/manim-animations/src/euclidian.py` (91 lines)
