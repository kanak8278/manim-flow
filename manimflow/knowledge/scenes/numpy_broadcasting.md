---
source: https://github.com/mashaan14/manim/blob/main/manim_numpyBroadcasting.ipynb
project: manim_mashaan14
domain: [linear_algebra, mathematics, machine_learning]
elements: [matrix, table, code_block, label]
animations: [write, fade_in, transform]
layouts: [side_by_side, edge_anchored]
techniques: [data_driven]
purpose: [demonstration, step_by_step, transformation]
mobjects: [MathTable, VGroup, Code, Text]
manim_animations: [Write, FadeIn, TransformMatchingShapes]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 60
scene_classes: [numpyBroadcasting]
---

## Summary

Visualizes NumPy broadcasting by showing how a pairwise Euclidean distance computation `C = np.sqrt(np.square(A[:, None, :] - B[None, :, :]).sum(axis=-1))` works. Two matrices A (3x2) and B (3x2) are displayed, then transformed into their broadcast-compatible shapes — A becomes a column slice (3x1) and B becomes a row slice (1x3) — which slide into position around the resulting distance matrix C (3x3). Uses MathTable with actual computed NumPy values and a Code block showing the source expression.

## Design Decisions

- **Real computed data, not placeholders**: A, B, and C are computed with actual NumPy/PyTorch operations, then displayed. This ensures the numbers are mathematically correct and the viewer can verify them.
- **TransformMatchingShapes for reshape visualization**: The transformation from full matrix to sliced/broadcast shape uses `TransformMatchingShapes`, which morphs matching elements and creates/destroys non-matching ones. This visually communicates "the data is being reshaped."
- **Stacked duplicate tables for broadcast shape**: The broadcast form (e.g., A1 column repeated) is shown as two slightly offset copies of the slice, conveying "this column is conceptually repeated across columns." The offset (0.2 DOWN, 0.15 LEFT) creates a shadow/stack effect.
- **Code block at top-left**: The NumPy expression is always visible as context, anchoring the visual to the code the viewer is trying to understand.
- **Attribution text at bottom-left**: Small watermark-style URL that stays out of the way.

## Composition

- **Screen regions**:
  - Code block: `to_edge(UP + LEFT)`, scale=0.8
  - Matrix A: `to_edge(LEFT)`, scale=0.7
  - Matrix B: `to_edge(RIGHT)`, scale=0.7
  - Matrix C: centered (default)
  - Reshaped A1: animates to `next_to(matrixC, LEFT)`
  - Reshaped B1: animates to `next_to(matrixC, UP)`
  - Attribution: `to_edge(DOWN + LEFT)`, scale=0.4
- **Element sizing**: All MathTable scaled to 0.7, Code scaled to 0.8
- **Stacked offset for broadcast shape**: 0.2 DOWN + 0.15 LEFT (for A), 0.2 UP + 0.1 RIGHT (for B)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| All matrices | BLUE_B | MathTable with include_outer_lines=True |
| Code block | Default | Code with background="rectangle", font="Monospace" |
| Attribution text | WHITE | scale=0.4 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Attribution write | default (~1s) | First element |
| Matrix A + B write | default (~1s) | Simultaneous |
| Code fade in | default (~1s) | |
| Wait | 2s | Let viewer read |
| TransformMatchingShapes | default (~1s) | Reshape both matrices |
| A1 slide to position | default (~1s) | next_to(C, LEFT) |
| B1 slide to position | default (~1s) | next_to(C, UP) |
| Matrix C write | default (~1s) | Result appears |
| Final wait | 5s | |
| Total video | ~14 seconds | |

## Patterns

### Pattern: Data-Driven MathTable from NumPy Array

**What**: Create a MathTable directly from a NumPy array, with `include_outer_lines=True` for a bordered grid look. The array values are computed programmatically, so the table always shows correct data. Scale uniformly for consistent sizing.

**When to use**: Matrix operations, linear algebra demonstrations, displaying computed results from NumPy/PyTorch operations, any visualization where you want to show real numeric data in a grid format.

```python
# Source: projects/manim_mashaan14/manim_numpyBroadcasting.ipynb (cell 3)
A = np.round(np.array([[1,1],[2,2],[3,3]], dtype=np.float32), 2)
matrixA = MathTable(A, include_outer_lines=True)
matrixA.color = BLUE_B
matrixA.scale(0.7)
```

### Pattern: TransformMatchingShapes for Matrix Reshaping

**What**: Use `TransformMatchingShapes` to morph a full matrix into a reshaped/sliced version. Matching elements animate smoothly while extras appear or disappear. This visually communicates array slicing and broadcasting better than a simple replacement.

**When to use**: NumPy broadcasting visualizations, tensor reshaping, matrix decomposition, any operation where the same data appears in a different shape — slicing, transposing, expanding dimensions.

```python
# Source: projects/manim_mashaan14/manim_numpyBroadcasting.ipynb (cell 3)
self.play(
    TransformMatchingShapes(matrixA, matrixA1_group),
    TransformMatchingShapes(matrixB, matrixB1_group)
)
```

### Pattern: Stacked Duplicate Tables for Broadcast Semantics

**What**: Show a broadcast axis by creating two slightly offset copies of a slice, visually suggesting "this is repeated." One copy shifts slightly (0.2 units) to create a depth/stack effect. Group both in a VGroup for unified animation.

**When to use**: NumPy broadcasting, tensor expansion, any operation where a lower-dimensional object is conceptually repeated/tiled to match a higher-dimensional shape.

```python
# Source: projects/manim_mashaan14/manim_numpyBroadcasting.ipynb (cell 3)
matrixA1 = MathTable(A1, include_outer_lines=True)
matrixA1.color = BLUE_B
matrixA1_1 = MathTable(A1, include_outer_lines=True)
matrixA1_1.color = BLUE_B
matrixA1_1.shift(0.2 * DOWN)
matrixA1_1.shift(0.15 * LEFT)
matrixA1_group = VGroup(matrixA1, matrixA1_1).scale(0.7)
```

## Scene Flow

1. **Attribution** (0-1s): Watermark URL writes at bottom-left.
2. **Input matrices** (1-2s): Matrix A (3x2) appears at left edge, Matrix B (3x2) at right edge.
3. **Code context** (2-3s): NumPy expression fades in at top-left.
4. **Pause** (3-5s): Viewer reads the matrices and code.
5. **Reshape** (5-6s): Both matrices morph via TransformMatchingShapes into broadcast-compatible shapes — A becomes a stacked column (3x1), B becomes a stacked row (1x3).
6. **Position** (6-8s): Reshaped A slides to left of center, reshaped B slides to top of center.
7. **Result** (8-9s): Distance matrix C (3x3) writes at center, flanked by its input shapes.
8. **Hold** (9-14s): Final layout held for 5 seconds.

> Source: `projects/manim_mashaan14/manim_numpyBroadcasting.ipynb` (cell 3)
