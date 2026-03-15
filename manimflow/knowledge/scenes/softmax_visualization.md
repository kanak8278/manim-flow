---
source: https://github.com/mashaan14/manim/blob/main/manim_visualizeSoftmax.ipynb
project: manim_mashaan14
domain: [deep_learning, machine_learning, mathematics, linear_algebra]
elements: [matrix, table, code_block, label, title]
animations: [write, fade_in, fade_out, indicate]
layouts: [horizontal_row, arranged_grid, edge_anchored]
techniques: [data_driven]
purpose: [demonstration, comparison, step_by_step]
mobjects: [MathTable, VGroup, Code, Text]
manim_animations: [Write, FadeIn, FadeOut, Indicate]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 55
scene_classes: [visualizeSoftmax]
---

## Summary

Visualizes PyTorch's `F.softmax` applied along different dimensions of a 4x3 matrix. Three matrices are shown side by side: the raw MLP output, the result of `softmax(dim=0)` where columns sum to 1, and `softmax(dim=1)` where rows sum to 1. Each softmax result is annotated with its Python code and a text explanation. The `Indicate` animation highlights each column or row in sequence to show which elements sum to 1 under each dimension setting.

## Design Decisions

- **Side-by-side comparison of dim=0 vs dim=1**: Placing all three matrices in a single row makes the difference between dimension axes immediately visible. The viewer can compare corresponding cells across matrices.
- **Indicate animation on columns/rows**: Instead of just stating "columns sum to 1", the animation physically highlights each column one at a time. This forces the viewer to see the grouping and understand which axis `dim=0` operates on. Same for rows with `dim=1`.
- **Code snippets above each result matrix**: The Python code `F.softmax(A, dim=0)` is shown directly above its result, creating a direct visual link between code and output. The viewer learns the API and sees its effect simultaneously.
- **Real computed softmax values**: Values are computed via PyTorch's `F.softmax` and rounded to 4 decimal places. This ensures mathematical accuracy and gives the viewer actual numbers to verify.
- **Sequential reveal**: Input matrix appears first, then dim=0 result with its explanation, then dim=1 result. This progressive disclosure prevents information overload.
- **arrange_in_grid with row_alignments='d'**: Aligns all three matrix groups at their bottom edge (descender), keeping the layout clean despite different heights from code blocks.

## Composition

- **Screen regions**:
  - Three matrix groups: `arrange_in_grid(1, 3, row_alignments='d')` — horizontal row
  - Explanation text: `to_edge(UP + LEFT)`, scale=0.5
  - Attribution: `to_edge(DOWN + LEFT)`, scale=0.4
- **Element sizing**: MathTable height=4, then entire group scaled to 0.6
- **Code blocks**: Code with tab_width=1, background="rectangle", font="Monospace", scaled as part of 0.6 group
- **Labels**: "MLP output" text above first matrix, code snippets above result matrices

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| All matrices | BLUE_B | MathTable with include_outer_lines=True |
| "MLP output" label | BLUE_B | Text above input matrix |
| Code blocks | Default | Code with background="rectangle" |
| Explanation text | WHITE | scale=0.5 |
| "dim=0" in explanation | YELLOW | Via t2c={"dim=0": YELLOW} |
| "dim=1" in explanation | YELLOW | Via t2c={"dim=1": YELLOW} |
| Indicate highlight | YELLOW | Default Indicate color |
| Attribution | WHITE | scale=0.4 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Attribution write | default (~1s) | |
| Input matrix write | default (~1s) | |
| dim=0 result write | default (~1s) | |
| Explanation text fade in | default (~1s) | |
| Column indicates | default (~1s) each | 3 columns = ~3s |
| Explanation fade out | default (~1s) | |
| dim=1 result write | default (~1s) | |
| Row indicates | default (~1s) each | 4 rows = ~4s |
| Final fade out + wait | default (~2s) | |
| Total video | ~16 seconds | |

## Patterns

### Pattern: MathTable Column/Row Indication

**What**: Use `matrixB.get_columns()[i]` or `matrixC.get_rows()[i]` to get submobject groups, then animate each with `Indicate` in a loop. This physically highlights which elements belong to the same group under a given operation (sum, softmax, normalization).

**When to use**: Softmax dim explanation, matrix operations that act along an axis (column-wise normalization, row-wise attention), any visualization where you need to show "these elements are grouped together" within a table or matrix.

```python
# Source: projects/manim_mashaan14/manim_visualizeSoftmax.ipynb (cell 3)
# Highlight each column for dim=0 (columns sum to 1)
for i in range(len(matrixB.get_columns())):
    self.play(Indicate(matrixB.get_columns()[i]))

# Highlight each row for dim=1 (rows sum to 1)
for i in range(len(matrixC.get_rows())):
    self.play(Indicate(matrixC.get_rows()[i]))
```

### Pattern: Code + Result Paired VGroup

**What**: Create a VGroup containing a Code block positioned above a MathTable, then treat the pair as a single unit for layout. The code shows the operation, the table shows the result. Scale the entire group uniformly.

**When to use**: Any code-to-output demonstration — showing function calls alongside their results, API documentation with live examples, comparing different function parameters (dim=0 vs dim=1, different hyperparameters).

```python
# Source: projects/manim_mashaan14/manim_visualizeSoftmax.ipynb (cell 3)
matrixB = MathTable(B, include_outer_lines=True)
matrixB.color = BLUE_B
code = '''
      import torch.nn.functional as F
      F.softmax(A,dim=0)
        '''
CodeB = Code(code=code, tab_width=1, background="rectangle",
             language="Python", font="Monospace")
matrixB_group = VGroup(matrixB, CodeB.next_to(matrixB, UP)).scale(0.6)
```

### Pattern: t2c (Text-to-Color) for Parameter Highlighting

**What**: Use the `t2c` parameter in `Text()` to color specific substrings differently from the rest. This draws the viewer's attention to the key parameter being discussed — in this case, the dimension argument.

**When to use**: Highlighting function parameters, variable names, keywords in explanatory text. Especially useful when comparing different parameter values (dim=0 vs dim=1, learning_rate, batch_size) across visualizations.

```python
# Source: projects/manim_mashaan14/manim_visualizeSoftmax.ipynb (cell 3)
textB = Text('When dim=0 all columns sum to 1', t2c={"dim=0": YELLOW}).scale(0.5)
textB.to_edge(UP + LEFT)
```

## Scene Flow

1. **Attribution** (0-1s): Watermark URL writes at bottom-left.
2. **Input matrix** (1-2s): 4x3 matrix labeled "MLP output" appears at left.
3. **dim=0 result** (2-3s): Second matrix with `F.softmax(A,dim=0)` code appears in center.
4. **Column explanation** (3-7s): Text "When dim=0 all columns sum to 1" appears at top-left with "dim=0" highlighted in yellow. Each of the 3 columns is indicated in sequence.
5. **Clear explanation** (7-8s): dim=0 text fades out.
6. **dim=1 result** (8-9s): Third matrix with `F.softmax(A,dim=1)` code appears at right.
7. **Row explanation** (9-14s): Text "When dim=1 all rows sum to 1" with "dim=1" in yellow. Each of the 4 rows is indicated in sequence.
8. **Cleanup** (14-16s): Explanation fades out. Final wait.

> Source: `projects/manim_mashaan14/manim_visualizeSoftmax.ipynb` (cell 3)
