---
source: https://github.com/nipunramk/Reducible/blob/main/2020/DynamicProgramming/dp.py
project: Reducible
domain: [computer_science, algorithms, dynamic_programming, graph_theory, data_structures]
elements: [graph, node, circle_node, array, grid, box, arrow, curved_arrow, label, surrounding_rect, formula]
animations: [fade_in, fade_out, write, draw, transform, replacement_transform, transform_from_copy, highlight, indicate, color_change, grow]
layouts: [centered, hierarchy, grid, side_by_side, vertical_stack]
techniques: [custom_mobject, algorithm_class_separation, progressive_disclosure, data_driven, color_state_machine]
purpose: [step_by_step, demonstration, decomposition, comparison, process]
mobjects: [Circle, Square, Rectangle, Prism, Line, Arrow, CurvedArrow, VGroup, TextMobject, TexMobject, BulletedList, ScreenRectangle]
manim_animations: [FadeIn, FadeOut, ShowCreation, Write, Transform, TransformFromCopy, Indicate, GrowFromCenter]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 3491
scene_classes: [GraphNode, IntroDP, MakeGrids, BoxProblem, LIS, BoxProblemPart2, DPConclusion]
---

## Summary

Visualizes dynamic programming through two problems: Box Stacking (3D boxes with strict dimension constraints) and Longest Increasing Subsequence (LIS). Uses the GraphNode class to construct DAGs representing subproblem dependencies, with CurvedArrow edges showing valid transitions. LIS array elements transform into graph nodes, with GREEN_SCREEN highlights tracing the longest path. Box Stacking uses 3D Prism mobjects that stack vertically. Follows a 5-step DP framework: visualize, find subproblems, find relationships, generalize, implement.

## Design Decisions

- **DAG for subproblem structure**: Both problems visualized as directed acyclic graphs where edges represent valid transitions (box i can sit on box j, or element i < element j). Longest path in DAG = optimal DP solution.
- **3D Prism for boxes**: Prism(dimensions=[l, w, h]) with color coding and dimension labels. Stacking shown by next_to(UP, buff=0) with vertical offset correction.
- **CurvedArrow for subsequence**: LIS transitions shown as curved arrows between array elements, GREEN_SCREEN colored to highlight the optimal subsequence.
- **Grid subproblem visualization**: MakeGrids creates colored square grids of increasing sizes (1x1 through 6x6) that slide and stack to show subproblem growth.
- **5-step framework**: Structured around "1. Visualize Examples" through "5. Implement", with step labels appearing at DOWN*3.5.
- **Array to graph transform**: TransformFromCopy takes array element text and creates corresponding graph nodes, visually connecting the input representation to the DAG representation.

## Composition

- **Box Prisms**: scale_factor=0.3, construct_box(l, w, h, color), label_direction=RIGHT
- **LIS array**: TexMobject elements, scale=0.8, positioned next to problem statement
- **Graph nodes**: radius=0.4, scale=0.9, positioned via create_graph(array)
- **CurvedArrow tips**: tip_length=0.1 for clean small arrows
- **Grid squares**: side_length=0.5, filled with color opacity=0.3
- **Step labels**: scale=0.8, positioned DOWN*3.5
- **Problem text**: scale=0.6-0.8, next_to(h_line, DOWN)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Box 1 | RED | Prism fill |
| Box 2 | GREEN_SCREEN | Prism fill |
| Box 3 | BLUE | Prism fill |
| More boxes | [RED, ORANGE, YELLOW, GREEN_SCREEN, BLUE, VIOLET] | 6-color cycle |
| LIS highlight | GREEN_SCREEN | CurvedArrow + element color |
| Graph node | DARK_BLUE_B fill, BLUE stroke | Same as BFS/DFS |
| Grid fill | [RED, ORANGE, YELLOW, GREEN_SCREEN, BLUE, VIOLET] | opacity=0.3 |
| Step highlight | YELLOW | Indicate or set_color |
| DP function labels | MONOKAI_BLUE, MONOKAI_PURPLE | Code coloring |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Problem statement write | default | Sequential Write per line |
| Box FadeIn | default | *[FadeIn(box) for box in boxes] |
| Box stacking | run_time=2 | TransformFromCopy to stack position |
| LIS arrow creation | default | ShowCreation per CurvedArrow |
| Array to graph transform | run_time=2 | TransformFromCopy per element |
| Graph edge creation | run_time=6 | ShowCreation(edges), rate_func=linear |
| Grid sliding | default | shift with smooth rate_func |
| Total video | ~25 minutes | DP tutorial with two problems |

## Patterns

### Pattern: Array Elements to DAG Nodes via TransformFromCopy

**What**: Takes individual array element text mobjects and transforms copies of them into corresponding graph nodes positioned in a DAG layout. Then draws directed edges between nodes that satisfy the subproblem relationship. Visually bridges the input (array) to the computational structure (DAG).

**When to use**: Any DP visualization where the subproblem graph derives from the input data structure. LIS, edit distance, coin change, any problem where you want to show how input elements become nodes in a dependency graph.

```python
# Source: projects/Reducible/2020/DynamicProgramming/dp.py:1216-1237
graph, edge_dict = self.construct_graph([3, 1, 8, 2, 5])
nodes, edges = self.make_graph_mobject(graph, edge_dict)
transforms = []
for i in range(5, 10):  # indices of array elements in text
    transform = TransformFromCopy(ex1[0][i], nodes[i - 5])
    transforms.append(transform)
self.play(*transforms, run_time=2)
self.wait(3)
self.play(ShowCreation(edges), rate_func=linear, run_time=6)
```

### Pattern: CurvedArrow Subsequence Indicators

**What**: CurvedArrow connecting consecutive elements of a subsequence within an array display. tip_length=0.1 for clean small arrows. GREEN_SCREEN color for the selected subsequence. Source points offset by DOWN*0.2 to avoid overlapping the text.

**When to use**: Subsequence visualization in arrays, demonstrating LIS/LCS solutions, showing which elements are selected in a DP trace-back, any sequential selection from a list.

```python
# Source: projects/Reducible/2020/DynamicProgramming/dp.py:1074-1098
arrow_1 = CurvedArrow(
    ex1[0][6].get_center() + DOWN * 0.2 + RIGHT * SMALL_BUFF,
    ex1[0][8].get_center() + DOWN * 0.2 + LEFT * SMALL_BUFF,
    tip_length=0.1
)
arrow_1.set_color(GREEN_SCREEN)
ex1[0][6].set_color(GREEN_SCREEN)
self.play(ShowCreation(arrow_1))
ex1[0][8].set_color(GREEN_SCREEN)
```

### Pattern: 3D Box Stacking Visualization

**What**: Prism mobjects represent boxes with (l, w, h) dimensions. Stack by placing each box on top of the previous using next_to(UP, buff=0) with a height-dependent vertical correction. Dimension labels placed next to each box.

**When to use**: 3D packing problems, any visualization involving stacking or layering of differently-sized objects.

```python
# Source: projects/Reducible/2020/DynamicProgramming/dp.py:951-994
def construct_box(self, l=3, w=2, h=1, color=BLUE, label=True):
    box = Prism(dimensions=[l, w, h]).set_color(color).set_stroke(WHITE, 2)
    box.pose_at_angle()
    if label:
        label_text = TextMobject("({0}, {1}, {2})".format(...)).scale(1.8)
        label_text.next_to(box, RIGHT)
        box = VGroup(box, label_text)
    return box

def put_box_on_top(self, top, bottom):
    display_length = bottom[0].dimensions[2]
    top[0].next_to(bottom[0], UP, buff=0)
    top[0].shift(DOWN * 0.25 * display_length)
    top[1].next_to(top[0], RIGHT)
```

## Scene Flow

1. **Introduction** (0-3min): Dynamic programming defined. 5 steps + 2 problems overview. Screen rectangles for fundamental vs challenging.
2. **Box Stacking** (3-12min): Problem statement. 3D box visualization. Examples with 3 and 6 boxes. Stack construction via TransformFromCopy. Step 1: Visualize.
3. **LIS** (12-22min): Problem statement with constraints. Array examples with CurvedArrow subsequences. Array to DAG transformation. Graph traversal to find longest path. DP implementation.
4. **Box Stacking Part 2** (22-28min): Sorting by dimensions. DAG construction. DP solution building on LIS framework.
5. **Conclusion** (28-30min): Guide to finding subproblems. Generalization of the 5-step approach.

> Note: Uses manimlib. GraphNode pattern shared with BFS/DFS/FFT. Prism is a manimlib 3D mobject.
