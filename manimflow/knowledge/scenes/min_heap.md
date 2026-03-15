---
source: https://github.com/KainaniD/manim-videos/blob/main/min-heap.py
project: manim-videos
domain: [computer_science, data_structures, algorithms]
elements: [tree, circle_node, rectangle_node, line, label]
animations: [write, swap, color_change]
layouts: [dual_panel, hierarchy, vertical_stack]
techniques: [dual_track_visualization, color_state_machine, helper_function, factory_pattern]
purpose: [definition, demonstration, step_by_step]
mobjects: [VGroup, Text, Circle, Rectangle, Line]
manim_animations: [Write, MoveToTarget, FadeToColor]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 144
scene_classes: [MinHeap]
---

## Summary

Visualizes min-heap insertion by adding 6 nodes one at a time (12, 8, 10, 6, 7, 2) to both a tree view (left) and an array view (right). After each insertion, if the new node violates the min-heap property (child < parent), it bubbles up via synchronized tree+array swaps. Settled nodes turn BLUE. Structurally identical to the max-heap visualization but with the comparison reversed -- smaller values bubble up instead of larger ones.

## Design Decisions

- **Mirror of max-heap visualization**: Uses the exact same layout, helpers, color scheme, and dual-track approach as max-heap.py. This consistency lets the viewer (or LLM) compare the two directly. The ONLY difference is the comparison direction: min-heap bubbles up smaller values.
- **Dual-track visualization (tree + array)**: Same rationale as max-heap. The tree shows the structural property (parent <= children), the array shows underlying storage.
- **BLUE for settled nodes**: Same as max-heap. After a node reaches its valid position, it turns BLUE.
- **RED-filled circles**: Same RED stroke and fill (opacity=0.2) as max-heap for unsettled nodes.
- **Multi-level bubble-up**: Node 6 bubbles up twice (past 12, past 8). Node 2 bubbles up twice (past 10, past 6). This shows that insertion can require O(log n) swaps.
- **Manual coordinate positioning**: Same explicit positioning as max-heap, identical tree shape.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Tree: root at `LEFT * 2 + UP * 2`, children at LEFT*4, center
  - Array: `RIGHT * 5` column, elements at UP*2 through DOWN*3
- **Tree layout**: Identical to max-heap.py
  - Root: `LEFT * 2 + UP * 2`
  - Level 1: `LEFT * 4`, center
  - Level 2: `LEFT * 5 + DOWN * 2`, `LEFT * 3 + DOWN * 2`, `LEFT * 1 + DOWN * 2`
- **Edge scaling**: Lines scaled 1.2-1.7x
- **Node sizing**: Circle radius=0.7, Rectangle width=3 height=1

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Tree node circles | RED | stroke=RED, fill=RED opacity=0.2 |
| Settled node circles | BLUE | FadeToColor after valid position |
| Array rectangles | WHITE | stroke=WHITE, fill=WHITE opacity=0 |
| Array text | WHITE | scale=0.8 |
| Tree edges | WHITE | Line, scaled 1.2-1.7x |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=1 | Solo |
| Node + array Write | run_time=1 | Simultaneous pair |
| Swap | run_time=1 | play_swap with 4 elements |
| Settle (BLUE) | Default (~1s) | FadeToColor |
| Wait between inserts | wait=0.4 | Brief pause |
| Total video | ~35 seconds | 6 insertions |

## Patterns

### Pattern: Min-Heap Bubble-Up with Synchronized Dual Swap

**What**: Same pattern as max-heap but comparison is reversed. When a newly inserted node is smaller than its parent, swap() is called for both tree and array pairs, then play_swap() animates all four simultaneously. Multiple rounds of swaps move the node up to its correct position.
**When to use**: Min-heap insertion, priority queue with smallest-first ordering, Dijkstra's algorithm priority queue operations, Huffman coding tree construction.

```python
# Source: projects/manim-videos/min-heap.py:91-107
# Insert 6 at left-left position
tree4 = createNode(6)
tree4.shift(LEFT * 5 + DOWN * 2)
array4 = createDataFixedWidth(6, 3)
array4.shift(RIGHT * 5 + DOWN)
self.play(Write(tree4), Write(array4), Write(tree1_tree4), run_time=1)

# 6 < 12 (parent) -> swap up
swap(tree4, tree1)
swap(array4, array1)
play_swap(self, tree1, array1, tree4, array4)

# 6 < 8 (new parent, which was original root) -> swap up again
swap(tree4, tree2)
swap(array4, array2)
play_swap(self, tree2, array2, tree4, array4)
# 6 is now root -> settled
self.play(FadeToColor(tree4[1], BLUE))
```

### Pattern: Consistent Heap Visualization Template

**What**: Max-heap and min-heap use identical code structure: same createNode, createDataFixedWidth, swap, play_swap helpers, same layout, same color scheme. Only the insertion values and swap conditions differ. This makes the two files a reusable template for any heap variant.
**When to use**: When you need to create heap visualizations and want a proven layout. Copy either file and change only the values and comparison logic.

```python
# Source: projects/manim-videos/min-heap.py:11-47
# These helpers are identical to max-heap.py
def createNode(data):
    data = str(data)
    node = VGroup()
    node_data = Text(data)
    node_circle = Circle(radius=0.7, stroke_color=RED)
    node_circle.set_fill(RED, opacity=0.2)
    node.add(node_data, node_circle)
    return node

def swap(first, second):
    first.generate_target()
    second.generate_target()
    first.target.shift(second.get_center() - first.get_center())
    second.target.shift(first.get_center() - second.get_center())
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a min-heap?" writes.
2. **Insert 12** (2-4s): Root node 12 in tree and array. Turns BLUE.
3. **Insert 8** (4-7s): Left child 8 added. 8 < 12, swap up. 8 becomes root. Both turn BLUE.
4. **Insert 10** (7-10s): Right child 10 added under original root position (now 12). 10 < 12, no swap needed (10 is right child of 8, 10 > 8). Turns BLUE.
5. **Insert 6** (10-15s): Left-left grandchild 6 added. 6 < 12, swap. 6 < 8, swap again. 6 becomes root. Turns BLUE.
6. **Insert 7** (15-19s): 7 added under 12. 7 < 12, swap. 7 under 8, 7 < 8, stop. Turns BLUE.
7. **Insert 2** (19-25s): 2 added under 10. 2 < 10, swap. 2 < 6, swap. 2 becomes root. Turns BLUE.
8. **Done** (25s): Final min-heap state displayed.

> Full file: `projects/manim-videos/min-heap.py` (144 lines)
