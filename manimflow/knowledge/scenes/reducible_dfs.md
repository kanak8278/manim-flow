---
source: https://github.com/nipunramk/Reducible/blob/main/2020/DFS/dfs.py
project: Reducible
domain: [computer_science, algorithms, graph_theory, searching, recursion]
elements: [graph, node, circle_node, line, arrow, label]
animations: [fade_in, fade_out, write, draw, transform, transform_from_copy, highlight, indicate, color_change]
layouts: [centered, scattered]
techniques: [custom_mobject, algorithm_class_separation, color_state_machine, progressive_disclosure]
purpose: [step_by_step, demonstration, comparison, exploration]
mobjects: [Circle, Line, ArcBetweenPoints, Arrow, VGroup, TextMobject]
manim_animations: [FadeIn, FadeOut, ShowCreation, Transform, TransformFromCopy, CircleIndicate]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 3399
scene_classes: [GraphNode, GraphAnimationUtils, ThumbnailYoutube, Introduction, Transition, GraphTraversal, DFSImplementation, DFSIteratitiveImplementation, ImplementationComparison, PostOrder, DFSApplications, MazeGeneration]
---

## Summary

Visualizes Depth-First Search with the same GraphNode/GraphAnimationUtils infrastructure as BFS, extended with backtracking visualization. When DFS hits a dead end, the surround circle turns BRIGHT_RED to indicate backtracking, and CircleIndicate in BLUE highlights the parent being returned to. Covers recursive DFS, iterative DFS with stack, post-order traversal, and DFS applications including topological sort, cycle detection, and maze generation via randomized DFS.

## Design Decisions

- **Backtracking color state**: Visited-and-exploring nodes are GREEN_SCREEN. When backtracking (no unvisited neighbors), the surround circle color changes to BRIGHT_RED. Parent node gets BLUE CircleIndicate to show where control returns.
- **Two traversal orderings**: Same graph, two different DFS orderings shown (dependent on neighbor visit order). Order 1 and Order 2 displayed simultaneously to demonstrate DFS non-uniqueness.
- **Directed graph variant**: connect_arrow() creates one-way edges for directed graph DFS demonstrations.
- **Shared code with BFS**: GraphNode, highlight_node, sharpie_edge, find_angle_of_intersection are identical to bfs.py. The same visual language (green surround + green thick edge) is reused.
- **Maze generation**: Randomized DFS used to carve maze paths. Demonstrates DFS as a constructive algorithm, not just a search.

## Composition

- **Same as BFS**: Node radius=0.4, scale=0.9, stroke_width=8 surround, stroke_width=12 sharpie edges
- **Graph layout**: 10 nodes at explicit positions spanning LEFT*5 to RIGHT*5, UP*2 to DOWN*2
- **Order text**: Two lines for Order 1 and Order 2, positioned below graph
- **Directed edges**: Arrow with buff=radius/2 for arrowhead clearance

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Exploring node | GREEN_SCREEN | Surround circle |
| Backtracked node | BRIGHT_RED | surround_circle.set_color(BRIGHT_RED) |
| Return-to parent | BLUE | CircleIndicate animation |
| Traversed edge | GREEN_SCREEN | Sharpie edge, stroke_width=12 |
| Default node | DARK_BLUE_B fill, BLUE stroke | Same as BFS |
| Default edge | GRAY | stroke_width=7 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| DFS node highlight | run_time=1 | Same as BFS |
| Backtrack color change | instant | set_color(BRIGHT_RED) |
| CircleIndicate parent | run_time=2 | Shows return-to node |
| Neighbor indication | run_time=2 | All neighbors simultaneously |
| Wait times per node | variable | 2-26s for narration |

## Patterns

### Pattern: Backtracking Color State Machine

**What**: Three visual states for DFS nodes: (1) GREEN_SCREEN surround when first visited, (2) BRIGHT_RED surround when all children explored (backtracking), (3) BLUE CircleIndicate on parent when returning. This three-state system makes the recursive call stack visible.

**When to use**: DFS visualization, recursive algorithm animation, any algorithm with forward exploration and backtracking phases. Also useful for constraint satisfaction, game tree search.

```python
# Source: projects/Reducible/2020/DFS/dfs.py:118-206
# After visiting all children of node 2:
graph[2].surround_circle.set_color(BRIGHT_RED)
self.wait(3)
# Return to parent node 1:
self.play(CircleIndicate(graph[1].circle, color=BLUE), run_time=2)
self.indicate_neighbors(graph, 1, wait_time_dict)
# Continue DFS from node 1's next unvisited neighbor
```

### Pattern: Dual DFS Ordering Comparison

**What**: Runs DFS twice on graphs with different neighbor orderings. Shows Order 1 and Order 2 text simultaneously to demonstrate that DFS traversal order depends on which neighbor is visited first. Same graph structure, different results.

**When to use**: Explaining algorithm non-determinism, comparing different tie-breaking strategies, any scenario where the same algorithm can produce different valid outputs.

```python
# Source: projects/Reducible/2020/DFS/dfs.py:236-261
order_1 = TextMobject("Order 1: 0 1 2 3 5 6 7 8 9 4")
order_1.move_to(order.get_center())
self.play(ReplacementTransform(order, order_1))

order_2 = TextMobject("Order 2: 0 2 1 4 3 5 8 9 7 6")
order_2.next_to(order, DOWN)
self.play(Write(order_2[:7]))
# Run second DFS with different neighbor order
dfs_second_full_order = dfs(graph, 0)
new_highlights = self.show_second_dfs_preorder(graph, edge_dict,
    dfs_second_full_order, order_2[7:], wait_times)
```

## Scene Flow

1. **DFS Intuition** (0-10min): 10-node graph with full step-by-step DFS. GREEN_SCREEN for exploring, BRIGHT_RED for backtracking, BLUE CircleIndicate for parent return. Two different orderings compared.
2. **DFS Implementation** (10-16min): Recursive code walkthrough with graph animation.
3. **Iterative DFS** (16-22min): Stack-based implementation, comparison with recursive.
4. **Post-Order** (22-26min): Post-order traversal visualization.
5. **Applications** (26-30min): Topological sort, cycle detection, maze generation.

> Note: Uses manimlib. GraphNode/GraphAnimationUtils pattern shared with bfs.py and fft.py.
