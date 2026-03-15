---
source: https://github.com/KainaniD/manim-videos/blob/main/binary-tree.py
project: manim-videos
domain: [computer_science, data_structures, graph_theory]
elements: [binary_tree, circle_node, arrow, line, label]
animations: [write, highlight, color_change, fade_in]
layouts: [hierarchy]
techniques: [color_state_machine, helper_function, factory_pattern]
purpose: [definition, demonstration, step_by_step]
mobjects: [VGroup, Integer, Circle, Text, Line]
manim_animations: [Write, ShowCreation, MoveToTarget, ReplacementTransform, FadeToColor]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 96
scene_classes: [BinaryTree]
---

## Summary

Visualizes a binary search tree with 6 nodes (values 5, 3, 8, 1, 4, 9). The root node starts large and centered, then shrinks and shifts up to make room for children. Nodes are BLUE-filled circles with integer labels. Directed edges connect parent to child with arrow tips. After the tree is built, a brief traversal demo highlights nodes RED one at a time (root to left child to left-right grandchild) to show path navigation.

## Design Decisions

- **BLUE filled circles for nodes**: BLUE fill at opacity=0.5 gives nodes visual weight and makes them stand out against the black background. The fill makes nodes look like "containers" holding data.
- **Root starts large, then shrinks**: The root is initially scale=2 to introduce it as the focus. It then shrinks to scale=1 and shifts up using generate_target/MoveToTarget. This progressive disclosure teaches "this is the root" before adding complexity.
- **"root" label with connecting line**: An explicit text label connected by a line teaches the viewer the vocabulary. The label shifts up with the root during the resize animation using ReplacementTransform on the connecting line.
- **surround() for circle sizing**: Instead of fixed radius, `node_circle.surround(node_data, buff=0.5)` auto-sizes the circle to fit the data. This handles multi-digit numbers gracefully.
- **RED highlight for traversal**: After building the tree, nodes turn RED one at a time (root -> left child -> left-right grandchild) to demo how you navigate a BST. The previous node returns to BLUE, creating a visual cursor.
- **Manual node positioning**: Each child is placed with explicit coordinate shifts (LEFT*2, RIGHT*2, DOWN*2) rather than auto-layout, giving precise control over the tree shape.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Root label: `LEFT * 4 + UP`, scale=0.9 (shifts to `LEFT * 2 + UP * 2` later)
  - Root node: centered at `UP * 1`, scale=2 initially, then scale=1 at `UP * 2`
  - Level 1 children: `LEFT * 2` and `RIGHT * 2` from center
  - Level 2 children: `LEFT * 3 + DOWN * 2`, `LEFT * 1 + DOWN * 2`, `RIGHT * 3 + DOWN * 2`
- **Node sizing**: Circle with surround(buff=0.5), auto-sized to Integer content
- **Edge lines**: Line(start=parent, end=child, buff=0.5) with arrow tip

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Node circles | BLUE | stroke_color=BLUE, fill=BLUE, opacity=0.5 |
| Node data | WHITE | Integer mobject, default color |
| Highlighted node | RED | FadeToColor on circle only |
| Root label | WHITE | scale=0.9 |
| Edges | WHITE | Line with add_tip() |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + root Write | run_time=1 | Simultaneous |
| Root label line ShowCreation | run_time=0.5 | Quick |
| Root shrink + shift | run_time=0.5 | MoveToTarget + ReplacementTransform |
| Level 1 children Write | run_time=0.5 | Both simultaneously |
| Level 1 edges Write | run_time=0.5 | Both simultaneously |
| Level 2 children Write | run_time=0.5 | Three simultaneously |
| Level 2 edges Write | run_time=0.5 | Three simultaneously |
| Each highlight step | run_time=0.4 + wait=0.5 | 3 steps |
| Total video | ~15 seconds | Build + brief traversal |

## Patterns

### Pattern: Auto-Sized Circle Node with surround()

**What**: Creates a circle node where the circle automatically sizes itself to fit the data using `surround(node_data, buff=0.5)`. Unlike fixed-radius circles, this handles varying content widths (single digit vs multi-digit numbers, short vs long strings).
**When to use**: Tree nodes, graph nodes, network diagrams, any node-based visualization where data content varies in width and you want consistent padding around the content.

```python
# Source: projects/manim-videos/binary-tree.py:13-20
def createNode(data):
    node = VGroup()
    node_data = Integer(data)
    node_circle = Circle(stroke_color=BLUE)
    node_circle.set_fill(BLUE, opacity=0.5)
    node_circle.surround(node_data, buff=0.5)
    node.add(node_data, node_circle)
    return node
```

### Pattern: Progressive Root Disclosure with Scale and Shift

**What**: The root node starts large (scale=2) and centered to introduce itself as the focal point. Then it shrinks (scale=1/2 of current) and shifts up via generate_target/MoveToTarget to make room for children. An attached label and connecting line move in sync using ReplacementTransform on the line.
**When to use**: Any tree or hierarchy visualization where you want to introduce the root/parent concept before revealing the full structure. Also works for org charts, family trees, or any top-down diagram.

```python
# Source: projects/manim-videos/binary-tree.py:40-55
root_node = createNode(5)
root_node.scale(2)
root_node.shift(UP)

# Later: shrink and shift up
root_label.generate_target()
root_label.target.shift(RIGHT * 2 + UP)
root_node.generate_target()
root_node.target.shift(UP)
root_node.target.scale(1/2)
root_label_to_root_node1 = Line(start=root_label.target, end=root_node.target, buff=0.2)
self.play(MoveToTarget(root_node), MoveToTarget(root_label),
          ReplacementTransform(root_label_to_root_node0, root_label_to_root_node1))
```

### Pattern: Sequential Node Highlight for Tree Traversal

**What**: After building the tree, nodes are highlighted RED one at a time. The previous node returns to BLUE in the same animation call. This creates a visual cursor that shows a path through the tree (root -> left -> left-right).
**When to use**: Demonstrating BST lookup, tree path traversal, showing how to navigate from root to a specific node. Brief traversal demo at the end of a tree-building visualization.

```python
# Source: projects/manim-videos/binary-tree.py:89-93
self.play(FadeToColor(root_node[1], color=RED), run_time=0.4)
self.wait(0.5)
self.play(FadeToColor(root_node[1], color=BLUE), FadeToColor(left_node[1], color=RED), run_time=0.4)
self.wait(0.5)
self.play(FadeToColor(left_node[1], color=BLUE), FadeToColor(left_right_node[1], color=RED), run_time=0.4)
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a binary tree?" writes. Root node (5) appears large and centered. "root" label with connecting line appears.
2. **Root repositioning** (2-3s): Root shrinks to half size and shifts upward. Label and line follow via MoveToTarget and ReplacementTransform.
3. **Level 1** (3-4s): Left child (3) and right child (8) write simultaneously. Edges from root to both children write.
4. **Level 2** (4-5s): Three grandchildren (1, 4, 9) write simultaneously. Their edges write.
5. **Pause** (5-8s): Wait 3s to let viewer absorb the full tree structure.
6. **Traversal demo** (8-12s): Root highlights RED. Then left child (3) highlights RED while root returns to BLUE. Then left-right grandchild (4) highlights RED while left child returns to BLUE.
7. **Done** (12-18s): Wait 6s on final state.

> Full file: `projects/manim-videos/binary-tree.py` (96 lines)
