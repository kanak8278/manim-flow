---
source: https://github.com/3b1b/videos/blob/main/_2018/cramer.py
project: videos
domain: [linear_algebra, algebra, mathematics]
elements: [matrix, vector, label, equation, axes, arrow, surrounding_rect, brace, pi_creature]
animations: [write, transform, replacement_transform, transform_from_copy, fade_in, fade_out, grow, indicate]
layouts: [centered, horizontal_row, side_by_side]
techniques: [progressive_disclosure, helper_function, custom_mobject]
purpose: [derivation, step_by_step, demonstration, definition]
mobjects: [Matrix, IntegerMatrix, VGroup, OldTex, OldTexText, Line, Brace, SurroundingRectangle, Rectangle, Circle, Arrow, Dot, Laptop]
manim_animations: [Write, FadeIn, FadeOut, ShowCreation, GrowFromCenter, ReplacementTransform, LaggedStartMap, LaggedStart, DrawBorderThenFill, PiCreatureSays, RemovePiCreatureBubble, Indicate, MoveToTarget]
scene_type: TeacherStudentsScene
manim_version: manimlib
complexity: intermediate
lines: 2280
scene_classes: [LeaveItToComputers, ShowComputer, PrerequisiteKnowledge, SetupSimpleSystemOfEquations, WhyLearnIt, NotTheMostComputationallyEfficient]
---

## Summary

Visualizes Cramer's rule for solving systems of linear equations using determinant ratios. The LinearSystem custom mobject creates a formatted Ax=b display with color-coded variables (x=GREEN, y=RED, z=BLUE, output=YELLOW). The get_cramer_matrix helper replaces one column of the coefficient matrix with the output vector. Pi creature scenes frame the topic pedagogically — the teacher builds Cramer's rule step by step while students react. Transitions from system-of-equations notation to matrix notation to geometric interpretation via LinearTransformationScene.

## Design Decisions

- **Color-coded variables**: x=GREEN, y=RED, z=BLUE throughout all representations. output=YELLOW, input=MAROON_B. This consistent mapping persists from equations to matrices to geometric vectors.
- **LinearSystem as VGroup**: A reusable custom mobject that packages the coefficient Matrix, input vector (xyz), equals sign, and output vector. Arranges them horizontally with SMALL_BUFF. Handles both 2D and 3D systems.
- **get_cramer_matrix helper**: Takes a Matrix mobject and replaces column i with the output vector. Uses mob_matrix (the grid of entry mobjects) for surgical column replacement. Creates a new Matrix with element_to_mobject=lambda m: m.copy() to avoid mutation.
- **TeacherStudentsScene framing**: "Let the computer handle it" -> "But what IS Cramer's rule?" -> formula reveal. The teacher-student dynamic makes the abstract rule feel like a conversation.
- **Determinant notation**: get_det_text wraps a matrix with vertical bars and "det" label. initial_scale_factor=3 for legibility. The fraction (numer/denom) layout uses a horizontal Line.
- **System -> Matrix -> Geometry pipeline**: The same problem shown in three representations, with ReplacementTransform connecting each pair.

## Composition

- **LinearSystem**: height=4 (configurable). Matrix, input_vect_mob, equals, output_vect_mob arranged RIGHT with SMALL_BUFF.
- **Cramer fraction**: Numerator matrix (with replaced column) over denominator matrix (original). Line separator matching numer width. Total height=2.25. Positioned at hold_up_spot, to_edge RIGHT with LARGE_BUFF.
- **Variable labels**: x, y, z as Matrix elements with gradient coloring GREEN->RED->BLUE.
- **Prerequisites display**: Three ImageMobject thumbnails (eola chapters 5, 7, 6) arranged RIGHT with LARGE_BUFF, next to h_line below title.
- **Corner rect**: SurroundingRectangle with BLACK fill at 0.8 opacity, height=2, to_corner UL.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Variable x | GREEN | X_COLOR constant |
| Variable y | RED | Y_COLOR constant |
| Variable z | BLUE | Z_COLOR constant |
| Output vector | YELLOW | OUTPUT_COLOR constant |
| Input vector | MAROON_B | INPUT_COLOR constant |
| Cramer column highlight | YELLOW | set_color + set_stroke(YELLOW, 1) |
| Unknown circles | YELLOW | stroke_width=2, scale=1.5 |
| Row rectangles | BLUE | SurroundingRectangle, stroke_width=2 |
| "Not efficient" text | RED | set_stroke(WHITE, 1) |
| Brace | WHITE | GrowFromCenter |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| System write | run_time=2 | Write(system) |
| Matrix transform | run_time=1 | ReplacementTransform columns |
| Cramer formula reveal | run_time=1 per piece | Sequential line, denom, numer |
| Student reaction | run_time=1 | change_students("horrified") |
| Big system compare | run_time=2 | Transform 2D -> 7D -> back |
| Unknown circles | run_time=1 | LaggedStartMap with lag_ratio=0.7 |

## Patterns

### Pattern: LinearSystem Custom Mobject

**What**: A VGroup that creates a complete Ax=b matrix equation with color-coded variables. Generates random integer matrices if none provided. The input vector shows variable names (x, y, z) colored by gradient. Output vector elements are YELLOW. All parts are accessible as named attributes for targeted animation.

**When to use**: Any linear algebra scene showing systems of equations, matrix equations, or Ax=b form. Reusable for Gaussian elimination, LU decomposition, or any matrix method.

```python
# Source: projects/videos/_2018/cramer.py:25-71
class LinearSystem(VGroup):
    CONFIG = {"matrix_config": {"element_to_mobject": Integer}, "dimensions": 3, "height": 4}

    def __init__(self, matrix=None, output_vect=None, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.matrix_mobject = Matrix(matrix, **self.matrix_config)
        self.equals = OldTex("=").scale(1.5)
        colors = [X_COLOR, Y_COLOR, Z_COLOR][:dim]
        self.input_vect_mob = Matrix(np.array(["x", "y", "z"][:dim]))
        self.input_vect_mob.elements.set_color_by_gradient(*colors)
        self.output_vect_mob = IntegerMatrix(output_vect)
        self.output_vect_mob.elements.set_color(OUTPUT_COLOR)
        self.add(self.matrix_mobject, self.input_vect_mob, self.equals, self.output_vect_mob)
        self.arrange(RIGHT, buff=SMALL_BUFF)
```

### Pattern: Cramer Matrix Column Replacement

**What**: Takes a Matrix mobject and creates a new matrix where column `index` is replaced with the output vector entries. Uses mob_matrix (the internal grid of entry mobjects) to surgically swap columns. Returns a new Matrix with copied entries to avoid mutating the original.

**When to use**: Cramer's rule visualization, any matrix method where a specific column is substituted (like cofactor expansion along a column).

```python
# Source: projects/videos/_2018/cramer.py:13-22
def get_cramer_matrix(matrix, output_vect, index=0):
    new_matrix = np.array(matrix.mob_matrix)
    new_matrix[:, index] = output_vect.mob_matrix[:, 0]
    result = Matrix(new_matrix, element_to_mobject=lambda m: m.copy())
    result.match_height(matrix)
    return result
```

## Scene Flow

1. **System Introduction** (0-20s): 3x3 LinearSystem appears. Yellow circles highlight unknowns. Blue rectangles highlight rows (equations). Transform to 7x7 system and back to show scale.
2. **Matrix Form** (20-40s): System-of-equations transforms into Ax=b matrix notation. Corner rect holds the matrix equation as geometric view appears.
3. **"Leave it to Computers"** (40-60s): Teacher says "Let the computer handle it" via PiCreatureSays. Students confused. 3D Laptop rotates.
4. **Cramer's Rule** (60-120s): Fraction structure: det(modified matrix) / det(original matrix). Column replacement highlighted in YELLOW. Three fractions for x, y, z arranged horizontally.
5. **"Not Efficient"** (120-140s): Big red text overlay. Comparison to Gaussian elimination. But the formula has conceptual value.
6. **Geometric View** (140-200s): LinearTransformationScene shows the matrix transformation. Basis vectors grown. Input space mapped to output space. Cramer's rule as area/volume ratios.
