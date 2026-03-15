---
source: https://github.com/KainaniD/manim-videos/blob/main/matrix.py
project: manim-videos
domain: [computer_science, data_structures, mathematics, linear_algebra]
elements: [matrix, array, rectangle_node, label, highlight_rect]
animations: [write, fade_in, fade_out, color_change, transform]
layouts: [grid, side_by_side]
techniques: [color_state_machine, status_text, helper_function, factory_pattern]
purpose: [definition, demonstration, step_by_step]
mobjects: [VGroup, Text, Square, Rectangle, Circle]
manim_animations: [Write, FadeIn, FadeOut, FadeToColor, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 117
scene_classes: [Matrix]
---

## Summary

Visualizes a 4x5 matrix of random integers arranged as a 2D grid. Row indices appear on the left, column indices on the bottom, and "Array 1-4" labels on the right show that each row is an array. The animation demonstrates two-level indexing: first `matrix[3]` highlights an entire row RED while dimming others GREY, then `matrix[3][2]` highlights a specific element BLUE within that row. A color-coded access expression on the right shows the code syntax with row index in RED and column index in BLUE.

## Design Decisions

- **4x5 grid layout**: 20 elements in a grid matches how 2D arrays are visualized in textbooks. 4 rows and 5 columns give enough structure to demonstrate two-level indexing without being overwhelming.
- **Two-step access highlighting**: First highlights the entire row (RED), then narrows to a specific element (BLUE). This teaches two-level indexing progressively -- `matrix[3]` selects a row, `[2]` selects within that row.
- **RED for row, BLUE for column**: RED draws attention to the first-level access (row selection). BLUE contrasts for the second-level access (column selection). The t2c coloring in the access expression text uses the same colors.
- **GREY for dimmed elements**: Non-selected rows/columns turn GREY to create contrast. The selected row pops against the dimmed background.
- **"Array 1-4" labels on right**: Explicitly shows that each matrix row IS an array. This label group fades out after introduction to reduce clutter during the access demonstration.
- **Row indices on left, column indices on bottom**: Matches standard matrix notation where rows are on the side and columns are across the bottom.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Matrix: `LEFT * 2 + UP * 2` (top-left corner), 5 columns x 4 rows
  - Row indices: `LEFT * 3.5`, aligned with each row (`UP * 2 + DOWN * i * 1.2`)
  - Column indices: `LEFT * 2 + RIGHT * j`, at `DOWN * 3`
  - Array labels: `RIGHT * 4.5`, aligned with each row (`UP * 2 + DOWN * i * 1.2`)
  - Access expression: `RIGHT * 4.5 + UP`, scale=0.8
- **Element sizing**: Square(side_length=1), inner Text scale=0.8
- **Grid spacing**: 1 unit horizontal (RIGHT * j), 1.2 units vertical (DOWN * i * 1.2)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Matrix squares | stroke=WHITE | fill=WHITE opacity=0 |
| Matrix text | WHITE | Default, scale=0.8 |
| Selected row | RED | FadeToColor on all elements in row |
| Selected element | BLUE | FadeToColor on specific element |
| Dimmed elements | GREY | Non-selected rows/columns |
| Row index (selected) | RED | FadeToColor |
| Column index (selected) | BLUE | FadeToColor |
| Access text `[row]` | RED | Via t2c parameter |
| Access text `[col]` | BLUE | Via t2c parameter |
| Array labels | WHITE | scale implied default |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=1 | Solo |
| Matrix FadeIn | run_time=1 | After title |
| Array labels FadeIn | run_time=1 | Shows row=array concept |
| Row/column indices Write | run_time=1 | Simultaneous |
| Array labels FadeOut | run_time=1 | Clear clutter |
| Row highlight | run_time=1 | RED row + GREY others + access text |
| Element highlight | run_time=1 | BLUE element + access text update |
| Reset colors | run_time=1 | Back to WHITE |
| Second access demo | run_time=1 per step | Row 0, then element [0][1] |
| Total video | ~22 seconds | 2 full access demonstrations |

## Patterns

### Pattern: 2D Grid Layout with Nested Loops

**What**: Creates a 4x5 grid of Square elements by iterating with nested loops. The outer loop controls rows (DOWN * i * 1.2), the inner loop controls columns (RIGHT * j). The entire grid is then shifted as a VGroup. The 1.2 vertical spacing (vs 1.0 horizontal) gives rows slight visual separation.
**When to use**: Matrix visualization, 2D array indexing demos, pixel grids, game boards, truth tables, any rectangular arrangement of uniform cells.

```python
# Source: projects/manim-videos/matrix.py:58-72
matrix = []
matrixGroup = VGroup()

for i in range(20):
    currentData = createData(rand.randint(0, 99))
    matrixGroup.add(currentData)
    matrix.append(currentData)

index = 0
for i in range(4):
    for j in range(5):
        matrix[index].shift(DOWN * i * 1.2 + RIGHT * j)
        index += 1

matrixGroup.shift(LEFT * 2 + UP * 2)
```

### Pattern: Two-Level Access Highlighting with Row-Then-Element

**What**: First highlights an entire row RED and dims everything else GREY to show first-level indexing (`matrix[3]`). Then a ReplacementTransform updates the access expression to include the column index, and a single element within the row turns BLUE. This two-step process teaches that 2D array access is "select row, then select element."
**When to use**: 2D array/matrix indexing tutorials, spreadsheet cell selection, any two-dimensional data access where you need to show the hierarchical nature of the indexing.

```python
# Source: projects/manim-videos/matrix.py:96-104
# Step 1: Highlight entire row
index_text = Text("Accessing:\n\nmatrix[3]", t2c={"[3]": RED})
index_text.shift(RIGHT * 4.5 + UP).scale(0.8)
self.play(Write(index_text), FadeToColor(matrixGroup[15:20], RED),
          FadeToColor(matrixGroup[0:15], GREY), FadeToColor(side_key[3], RED),
          FadeToColor(side_key[0:3], GREY))

# Step 2: Narrow to specific element
index_text1 = Text("Accessing:\n\nmatrix[3][2]", t2c={"[3]": RED, "[2]": BLUE})
index_text1.shift(RIGHT * 4.5 + UP).scale(0.8)
self.play(ReplacementTransform(index_text, index_text1),
          FadeToColor(matrixGroup[17], BLUE),
          FadeToColor(bottom_key, GREY), FadeToColor(bottom_key[2], BLUE))
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a matrix?" writes. 4x5 grid of random numbers fades in.
2. **Array labels** (2-4s): "Array 1" through "Array 4" labels appear on the right, showing each row is an array. Then indices appear on left and bottom.
3. **Clear labels** (4-5s): Array labels fade out to reduce clutter.
4. **First access: matrix[3]** (5-8s): Row 3 turns RED, others turn GREY. Row index 3 turns RED. Access expression "matrix[3]" writes on the right.
5. **First access: matrix[3][2]** (8-10s): Element at [3][2] turns BLUE. Column index 2 turns BLUE. Access expression updates to "matrix[3][2]".
6. **Reset** (10-12s): All colors return to WHITE. Access expression fades out.
7. **Second access: matrix[0]** (12-14s): Row 0 turns RED, others GREY. Access expression "matrix[0]" writes.
8. **Second access: matrix[0][1]** (14-17s): Element at [0][1] turns BLUE. Access expression updates to "matrix[0][1]". Wait 2s.

> Full file: `projects/manim-videos/matrix.py` (117 lines)
