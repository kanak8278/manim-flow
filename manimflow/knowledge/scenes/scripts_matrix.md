---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/matrix.py
project: manim-scripts
domain: [mathematics, linear_algebra]
elements: [matrix, surrounding_rect, label]
animations: [fade_in, transform, draw]
layouts: [horizontal_row, edge_anchored]
techniques: [helper_function, color_state_machine]
purpose: [demonstration, step_by_step, transformation]
mobjects: [Matrix, Text, Tex, VGroup, SurroundingRectangle]
manim_animations: [FadeIn, Write, Transform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 183
scene_classes: [MatrixMultiplication, MatrixMultiplication2, MatrixMultiplication3, MatrixMultiplication4]
---

## Summary

Four progressive matrix multiplication scenes. MatrixMultiplication shows basic A*B. MatrixMultiplication2 uses a `get_matrix()` helper with preset basis-like matrices and animates Transform between different multiplications. MatrixMultiplication3-4 add SurroundingRectangle highlights on specific rows and columns to show which parts contribute to the result — the key pedagogical pattern for teaching matrix multiplication mechanics.

## Design Decisions

- **Preset matrix bank via get_matrix()**: Six hardcoded 3x3 matrices (sparse, identity-like, basis-like) allow quick switching between multiplications without recalculating. Useful for showing how different right-hand matrices select/combine columns.
- **SurroundingRectangle on rows/columns**: Yellow rectangles wrap specific rows or columns to visually connect input row * input column = output element. This is the standard way to teach matrix multiplication — highlight what contributes to what.
- **Transform between multiplications**: Changing the right-hand matrix via Transform (not replacement) shows the viewer the transition. Combined with rectangle transforms on the result, this creates a "what if we change B?" narrative.
- **get_mob_matrix() for element access**: Manim's Matrix.get_mob_matrix() returns a 2D array of mobject elements, enabling per-element color changes and per-row/column rectangle wrapping.

## Composition

- **Matrix A**: to_edge(UL), default scale
- **Matrix B**: next_to(Matrix_A, RIGHT)
- **Equals sign**: Text(" = "), next_to(Matrix_B, RIGHT)
- **Result matrix**: next_to(equals, RIGHT)
- **Second row (MatrixMultiplication4)**: Matrix_B at to_edge(DL)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Matrix entries | WHITE | Default |
| Row highlight (color_row) | RED | opacity=0.5 |
| Column highlight (color_column) | GREEN | opacity=0.5 |
| SurroundingRectangle | YELLOW | stroke_width=2 |
| Element highlight | YELLOW | Single-element rectangle |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| FadeIn matrices | Default | All at once |
| Transform to new multiplication | Default (~1s) | Matrix and result |
| Wait between steps | 2s | Standard |
| Total (MatrixMultiplication4) | ~12s | 2 transformations + waits |

## Patterns

### Pattern: Row/Column SurroundingRectangle for Matrix Highlighting

**What**: Wrap a SurroundingRectangle around all elements in a specific row or column of a Manim Matrix. Uses `get_mob_matrix()` to access the internal element grid, then creates a VGroup of the target elements for the rectangle.
**When to use**: Teaching matrix multiplication (highlight contributing row and column), matrix operations (row reduction, column operations), or any per-row/column focus in tabular data.

```python
# Source: projects/manim-scripts/scenes/matrix.py:78-88
def surround_row_or_column(matrix, row=None, column=None, color=YELLOW):
    if row is not None:
        elements = matrix.get_mob_matrix()[row]
    elif column is not None:
        num_rows = len(matrix.get_mob_matrix())
        elements = [matrix.get_mob_matrix()[i][column] for i in range(num_rows)]
    else:
        raise ValueError("Either row or column must be specified.")
    rectangle = SurroundingRectangle(VGroup(*elements), color=color, stroke_width=2)
    return rectangle
```

### Pattern: Transform Between Matrix Multiplications

**What**: Change the right-hand matrix and result simultaneously via Transform, keeping the left-hand matrix fixed. Combined with transforming SurroundingRectangles on the result, this shows how changing B affects the output.
**When to use**: Exploring matrix properties (identity, projection, rotation), showing column interpretation of matrix multiplication, or any "what happens when we change this input" scenario.

```python
# Source: projects/manim-scripts/scenes/matrix.py:46-51
matrix_2 = get_matrix(2)
matrix_2_mn = Matrix(matrix_2).to_edge(UL).next_to(matrix_A_mn, RIGHT)
result_2 = Matrix(np.dot(matrix_A, matrix_2)).next_to(text_eq, RIGHT)
self.play(Transform(matrix_1_mn, matrix_2_mn), Transform(result_1, result_2))
```

### Pattern: Per-Element Access in Manim Matrix

**What**: Access individual matrix elements for highlighting or manipulation using `get_mob_matrix()[row][col]`. Returns the actual MathTex mobject for that entry, which can be colored, surrounded, or animated independently.
**When to use**: Highlighting specific matrix entries during multiplication walkthrough, Gaussian elimination pivot highlighting, or any entry-level matrix operation visualization.

```python
# Source: projects/manim-scripts/scenes/matrix.py:63-66
def get_element_position(matrix, row, col):
    element = matrix.get_mob_matrix()[row][col]
    return element.get_center()

def color_row(matrix, row_index, color=RED, opacity=0.5):
    elements = matrix.get_mob_matrix()[row_index]
    for element in elements:
        element.set_fill(color, opacity=opacity)
```

## Scene Flow

1. **MatrixMultiplication** (0-5s): A, B, and C = A*B all appear.
2. **MatrixMultiplication2** (0-8s): A and basis matrix appear, result shown. Transforms to different basis matrix with updated result.
3. **MatrixMultiplication3** (0-5s): Same multiplication with SurroundingRectangles on a single element, a column, and a row.
4. **MatrixMultiplication4** (0-12s): Column rectangles on input and output. Transforms to new matrix. Second row shows different column highlighted. Transforms again.

> Full file: `projects/manim-scripts/scenes/matrix.py` (183 lines)
