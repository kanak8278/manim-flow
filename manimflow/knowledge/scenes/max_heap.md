---
source: https://github.com/KainaniD/manim-videos/blob/main/max-heap.py
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
lines: 140
scene_classes: [MaxHeap]
---

## Summary

Visualizes max-heap insertion by adding 6 nodes one at a time (21, 19, 49, 71, 12, 67) to both a tree view (left) and an array view (right) simultaneously. After each insertion, if the new node violates the max-heap property (child > parent), it bubbles up via synchronized tree+array swaps. Settled nodes turn BLUE to signal they are in a valid position. The dual representation shows that the tree's parent-child relationships map to specific array index positions.

## Design Decisions

- **Dual-track visualization (tree + array)**: The tree shows the structural heap property (parent >= children). The array shows the underlying storage. Synchronized swaps prove they are the same data structure.
- **Incremental insertion**: Nodes are added one at a time rather than showing a pre-built heap. This teaches the insertion algorithm: add at bottom, then bubble up. The viewer sees each swap decision.
- **BLUE color for settled nodes**: After a node reaches its valid position (no more swaps needed), its circle turns BLUE. This signals "this node is done" and creates a growing set of validated nodes.
- **RED-filled circles with opacity=0.2**: Nodes start with a subtle RED fill to distinguish the tree from plain circles. The RED is light enough (opacity=0.2) that it doesn't compete with the BLUE "settled" state.
- **Manual tree layout with explicit coordinates**: Each node is positioned with hardcoded shifts (LEFT*2 + UP*2 for root, LEFT*4 for left child, etc.). Edges are plain Lines scaled to 1.2-1.7x to span between nodes.
- **Array as vertical column on right**: Array elements stack vertically at `RIGHT * 5`, each 1 unit apart (UP*2, UP, center, DOWN, DOWN*2, DOWN*3). The vertical layout saves horizontal space for the tree.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Tree: root at `LEFT * 2 + UP * 2`, children at LEFT*4, center, RIGHT positions
  - Array: `RIGHT * 5` column, elements at UP*2 through DOWN*3 (1 unit spacing)
- **Tree layout**:
  - Root: `LEFT * 2 + UP * 2`
  - Left child: `LEFT * 4` (center-y)
  - Right child: center (ORIGIN)
  - Level 2: `LEFT * 5 + DOWN * 2`, `LEFT * 3 + DOWN * 2`, `LEFT * 1 + DOWN * 2`
- **Edge scaling**: Lines scaled 1.2-1.7x to bridge gaps between nodes
- **Node sizing**: Circle radius=0.7, stroke=RED, fill=RED opacity=0.2
- **Array sizing**: Rectangle width=3, height=1

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Tree node circles | RED | stroke=RED, fill=RED opacity=0.2 |
| Tree node text | WHITE | Default |
| Settled node circles | BLUE | FadeToColor after valid position reached |
| Array rectangles | WHITE | stroke=WHITE, fill=WHITE opacity=0 |
| Array text | WHITE | scale=0.8 |
| Tree edges | WHITE | Line, scaled 1.2-1.7x |
| Title | WHITE | scale=1.2 |

Color strategy: RED (default/unsettled) -> BLUE (valid position). The RED start state creates urgency ("this node needs to find its place"), BLUE creates calm ("settled").

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=1 | Solo |
| Node + array element Write | run_time=1 | Simultaneous pair |
| Settle color (BLUE) | Default (~1s) | FadeToColor |
| Swap (tree + array) | run_time=1 | play_swap with 4 elements |
| Wait between insertions | wait=0.4 | Brief pause |
| Total video | ~35 seconds | 6 insertions, varying swap counts |

## Patterns

### Pattern: Synchronized Tree-Array Swap for Heap Operations

**What**: When a node needs to bubble up, swap() is called twice (once for tree pair, once for array pair), then play_swap() animates all four MoveToTarget animations simultaneously. This keeps the tree and array in perfect visual sync.
**When to use**: Max-heap insertion (bubble up), min-heap insertion, heap extract operations. Any heap visualization where tree and array must mirror each other.

```python
# Source: projects/manim-videos/max-heap.py:41-48
def swap(first, second):
    first.generate_target()
    second.generate_target()
    first.target.shift(second.get_center() - first.get_center())
    second.target.shift(first.get_center() - second.get_center())

def play_swap(self, first, second, third, fourth):
    self.play(MoveToTarget(first), MoveToTarget(second),
              MoveToTarget(third), MoveToTarget(fourth), run_time=1)

# Usage: bubble up node 49 past root 21
swap(tree1, tree3)    # tree nodes
swap(array1, array3)  # array elements
play_swap(self, tree1, array1, tree3, array3)
```

### Pattern: Incremental Heap Insertion with Bubble-Up

**What**: Each new node is added at the next available position in both the tree and array. If the new value is greater than its parent (max-heap violation), repeated swaps bubble it up. Multiple swap calls chain to move a node up multiple levels (e.g., node 71 swaps with parent 19, then with grandparent 49).
**When to use**: Teaching heap insertion, priority queue operations, any visualization where elements must find their correct position in a hierarchy by comparing with ancestors.

```python
# Source: projects/manim-videos/max-heap.py:94-112
# Insert 71 at left-left position
tree4 = createNode(71)
tree4.shift(LEFT * 5 + DOWN * 2)
array4 = createDataFixedWidth(71, 3)
array4.shift(RIGHT * 5 + DOWN)
self.play(Write(tree4), Write(array4), Write(tree2_tree4), run_time=1)

# 71 > 19 (parent) -> swap up
swap(tree4, tree2)
swap(array4, array2)
play_swap(self, tree2, array2, tree4, array4)

# 71 > 49 (new parent) -> swap up again
swap(tree4, tree3)
swap(array4, array3)
play_swap(self, tree3, array3, tree4, array4)
# 71 is now root -> settled
self.play(FadeToColor(tree4[1], BLUE))
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a max-heap?" writes.
2. **Insert 21** (2-4s): Root node 21 appears in tree and array. Turns BLUE (only node, trivially valid).
3. **Insert 19** (4-7s): Left child 19 added. 19 < 21, no swap needed. Turns BLUE.
4. **Insert 49** (7-11s): Right child 49 added. 49 > 21 (parent), swap up. 49 becomes root. Turns BLUE.
5. **Insert 71** (11-17s): Left-left grandchild 71 added. 71 > 19 (parent), swap. 71 > 49 (new parent), swap again. 71 becomes root. Turns BLUE.
6. **Insert 12** (17-20s): 12 added under 19. 12 < 19, no swap. Turns BLUE.
7. **Insert 67** (20-25s): 67 added under 21. 67 > 21 (parent), swap. 67 is now under 71, 67 < 71, stop. Turns BLUE.
8. **Done** (25-26s): Wait 1s. Full max-heap displayed.

> Full file: `projects/manim-videos/max-heap.py` (140 lines)
