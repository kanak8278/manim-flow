---
source: https://github.com/vivek3141/videos/blob/main/domino.py
project: vivek3141_videos
domain: [mathematics, combinatorics, number_theory, algorithms]
elements: [grid, label, equation, line, surrounding_rect, formula]
animations: [write, transform, draw, fade_in]
layouts: [centered, grid, side_by_side]
techniques: [custom_mobject, progressive_disclosure]
purpose: [demonstration, exploration, derivation, step_by_step]
mobjects: [VGroup, Line, Rectangle, Polygon, TexMobject, TextMobject, BackgroundRectangle, Circle]
manim_animations: [Write, ShowCreation, Transform, TransformFromCopy, FadeInFromDown, Uncreate]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 1355
scene_classes: [Grid, Chessboard, DominoGrid, Tilings, Recursion, TwoByNExample, Tmn, TwoByN, TreeMobject]
---

## Summary

Visualizes domino tiling of rectangular grids, progressing from concrete examples to the Fibonacci sequence connection. Three custom Grid mobjects (Grid, Chessboard, DominoGrid) build the visual foundation. DominoGrid extends Grid to overlay colored domino rectangles based on a permutation encoding. Tilings are shown by generating permutation arrays and calling `get_perm()` to produce VGroups of colored Polygon dominoes. The 2xN case is proven to follow the Fibonacci recurrence T(2,n) = T(2,n-1) + T(2,n-2) using visual decomposition with colored rectangles showing the two cases.

## Design Decisions

- **Custom Grid hierarchy**: Grid (base lines), Chessboard (alternating filled squares), DominoGrid (grid + domino placement from permutation). This separation lets the same grid underlie different visualizations.
- **Permutation-based domino encoding**: Each tiling is encoded as a permutation array. Entry i maps to the partner cell. `get_rect(pos1, pos2)` determines horizontal or vertical orientation from cell positions. Colors cycle through [TEAL, MAROON, GREEN].
- **Cross overlay for invalid tilings**: Two diagonal red Lines (stroke_width=8) form an X to mark tilings that are not valid. This is a clear "wrong" indicator.
- **Fibonacci visual proof**: The 2xN grid is split into two cases: last column has one vertical domino (leaving 2x(n-1)) or two horizontal dominoes (leaving 2x(n-2)). Gray Rectangles represent the "remaining" subproblem. Purple Rectangles represent the placed dominoes.
- **TreeMobject for binary trees**: A tree of Circle nodes connected by Lines, used to show the branching structure of combinatorial problems.

## Composition

- **DominoGrid**: m=4, n=4, s_width=1.5, s_length=1.5 (scaled grid)
- **Grid lines**: From `s_width * (x - m/2)` to `s_width * (x + n/2)`, creating centered grid
- **Domino rectangles**: Polygon with 4 corners, inset by dt=0.5 from cell boundaries, fill_opacity=1
- **2xN grid**: m=5, n=2, s_width=1.5, s_length=1.5
- **Case rectangles**: PURPLE for placed dominoes, GRAY for remaining subproblem
- **M and N labels**: TexMobject at 4*LEFT and 3.5*DOWN
- **Fibonacci equation**: scale=2.5, centered

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Domino colors | TEAL, MAROON, GREEN | Cycling via `pos1 % len(colors)` |
| Grid lines | WHITE | Default Line |
| Chessboard fills | WHITE | fill_opacity=0.6 |
| Invalid cross | RED | stroke_width=8 |
| Condition text | BLUE | M*N tex_to_color_map |
| Placed domino | PURPLE | Rectangle fill_opacity=1 |
| Remaining subproblem | GRAY | Rectangle fill_opacity=1 |
| T(2,n) result | TEAL | Fibonacci connection label |
| Variable n | GREEN | tex_to_color_map |
| Variable -1, -2 | RED | tex_to_color_map |
| Boxed result | YELLOW | BackgroundRectangle stroke_width=6 |
| Tree nodes | BLUE stroke, GREEN fill | Circle, fill_opacity=0 |
| Tree edges | LIGHT_GREY | Line, stroke_width=2 |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Grid creation | ShowCreation ~1s | Grid lines |
| Tiling write | Write ~1s | Domino rectangles |
| Tiling transform | Transform ~1s | Between permutations |
| Cross overlay | ShowCreation ~1s | Invalid mark |
| Fibonacci numbers | Write ~0.5s each | Sequential |
| Total | ~3-4 minutes | Multiple scenes |

## Patterns

### Pattern: Grid and DominoGrid Custom Mobjects

**What**: A hierarchy of grid mobjects. Grid draws m+1 vertical and n+1 horizontal Lines centered at origin, with configurable s_width and s_length. DominoGrid extends Grid to overlay colored domino Polygons based on a permutation array. `get_perm(perm)` returns a VGroup of domino rectangles. `get_rect(pos1, pos2)` creates horizontal or vertical Polygons based on whether cells share a row or column, inset by dt=0.5.

**When to use**: Domino tiling problems, grid-based combinatorics (polyomino packing), chessboard coloring, maze visualization, any grid where cells need to be paired or grouped.

```python
# Source: projects/vivek3141_videos/domino.py:4-81
class Grid(VGroup):
    def __init__(self, m, n, s_width=1, s_length=1, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.m, self.n, self.s_width = m, n, s_width
        for x in range(0, m + 1):
            self.add(Line(
                s_width * np.array([x - m/2, -n/2, 0]),
                s_width * np.array([x - m/2, n/2, 0])))
        for y in range(0, n + 1):
            self.add(Line(
                s_length * np.array([-m/2, y - n/2, 0]),
                s_length * np.array([m/2, y - n/2, 0])))

class DominoGrid(Grid):
    def __init__(self, m, n, s_width=1, s_length=1,
                 dt=0.5, perm=None, **kwargs):
        Grid.__init__(self, m, n, s_width=s_width,
                      s_length=s_length, **kwargs)
        self.colors = [TEAL, MAROON, GREEN]
        self.dt = dt

    def get_rect(self, pos1, pos2):
        if pos1 // self.m == pos2 // self.m:  # Same row
            rect = Polygon(
                self.get_point(pos1) + np.array([-self.dt, self.dt, 0]),
                self.get_point(pos2) + np.array([self.dt, self.dt, 0]),
                self.get_point(pos2) - np.array([-self.dt, self.dt, 0]),
                self.get_point(pos1) - np.array([self.dt, self.dt, 0]),
                fill_opacity=1, stroke_color=WHITE,
                color=self.colors[pos1 % len(self.colors)])
        else:  # Same column
            rect = Polygon(...)  # Vertical domino
        return rect
```

### Pattern: Fibonacci Recurrence via Visual Decomposition

**What**: The 2xN tiling count is proven to follow T(2,n) = T(2,n-1) + T(2,n-2) by showing two cases visually. Case 1: place one vertical domino (PURPLE, width=1) in the last column, leaving a GRAY rectangle labeled T(2,n-1). Case 2: place two horizontal dominoes (PURPLE, width=2.5, height=1) in the last two columns, leaving a GRAY rectangle labeled T(2,n-2). The equation builds incrementally as each case is shown.

**When to use**: Combinatorial recurrence proofs, tiling problems, dynamic programming visualizations, any problem where a solution decomposes into subproblems at the boundary.

```python
# Source: projects/vivek3141_videos/domino.py:239-326
eq = TexMobject(r"T(2, n)", r"= T(2, n-1)", r"+ T(2, n-2)",
                tex_to_color_map={r"-2": RED, r"-1": RED, r"n": GREEN})
eq.scale(1.5).shift(3 * UP)
grid = DominoGrid(5, 2, s_width=1.5, s_length=1.5)

# Case 1: vertical domino
rect = Rectangle(width=1, height=2.5, fill_opacity=1,
                 stroke_color=WHITE, color=PURPLE).shift(3 * RIGHT)
rect2 = Rectangle(width=5.5, height=2.5, fill_opacity=1,
                   stroke_color=WHITE, color=GRAY).shift(0.75 * LEFT)
text1 = TexMobject("T(2, n-1)").scale(1.5).shift(0.75 * LEFT)

# Case 2: two horizontal dominoes
rects = VGroup(
    Rectangle(width=2.5, height=1, ..., color=PURPLE).shift(2.25*RIGHT+0.75*UP),
    Rectangle(width=2.5, height=1, ..., color=PURPLE).shift(2.25*RIGHT-0.75*UP))
rect3 = Rectangle(width=4, height=2.5, ..., color=GRAY).shift(1.5 * LEFT)
text2 = TexMobject("T(2, n-2)").scale(1.5).shift(1.5 * LEFT)

# Final result
fib = TexMobject(r"T(2, n) = F_{n + 1}",
                 tex_to_color_map={r"n": GREEN, r"F": TEAL})
rect_box = BackgroundRectangle(fib, ..., color=YELLOW, stroke_width=6)
```

### Pattern: TreeMobject for Binary Decision Trees

**What**: A VGroup-based tree of Circle neurons arranged in layers, connected by Lines. Each layer has a configurable number of nodes. Nodes are arranged vertically within layers, layers arranged horizontally. Edges connect all nodes in adjacent layers. Supports labels and branch labels. Based on the NeuralNetworkMobject pattern but with tree-specific edge routing.

**When to use**: Decision trees, binary trees, game trees, probability trees, recursion visualization, any hierarchical branching structure.

```python
# Source: projects/vivek3141_videos/domino.py:329-400
class TreeMobject(VGroup):
    CONFIG = {
        "neuron_radius": 0.15,
        "neuron_to_neuron_buff": MED_SMALL_BUFF,
        "layer_to_layer_buff": LARGE_BUFF,
        "neuron_stroke_color": BLUE,
        "neuron_stroke_width": 3,
        "neuron_fill_color": GREEN,
        "edge_color": LIGHT_GREY,
        "edge_stroke_width": 2,
    }

    def __init__(self, neural_network, size=0.15):
        VGroup.__init__(self)
        self.layer_sizes = neural_network
        self.neuron_radius = size
        self.add_neurons()
        self.add_edges()
```

## Scene Flow

1. **Tilings** (0-20s): 4x4 grid with domino tiling. Transform between 5 different tilings. Red cross marks invalid tiling. M and N labels. "M*N is even" constraint shown.
2. **Recursion** (20-35s): Fibonacci sequence (1, 1, 2, 3, 5) shown as large numbers sliding left. Recurrence equation F_n = F_{n-1} + F_{n-2}.
3. **TwoByNExample** (35-40s): 5x2 grid with vertical purple domino rectangles.
4. **TwoByN** (40-60s): Visual decomposition. Case 1: vertical domino + T(2,n-1). Case 2: two horizontals + T(2,n-2). Equation builds incrementally. Boxed result: T(2,n) = F_{n+1}.

> Full file: `projects/vivek3141_videos/domino.py` (1355 lines, first 400 documented)
