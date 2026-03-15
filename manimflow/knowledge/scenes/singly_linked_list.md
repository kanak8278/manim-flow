---
source: https://github.com/KainaniD/manim-videos/blob/main/singly-linked-list.py
project: manim-videos
domain: [computer_science, data_structures]
elements: [circle_node, arrow, label, pointer]
animations: [write, slide, color_change, highlight]
layouts: [horizontal_row]
techniques: [labeled_pointer, color_state_machine, helper_function, factory_pattern]
purpose: [definition, demonstration, step_by_step]
mobjects: [VGroup, Integer, Circle, Text, Line]
manim_animations: [Write, ShowCreation, MoveToTarget, ReplacementTransform, FadeToColor]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 92
scene_classes: [LinkedList]
---

## Summary

Visualizes a singly linked list with 3 nodes (2 -> 3 -> 9) connected by arrow-tipped lines. The head node starts large and centered, then shrinks and shifts left to make room for the chain. A "head" label with a connecting line identifies the first node. After building the list, a "current" label slides right along the chain, highlighting each node RED in sequence (then returning it to BLUE) to demonstrate traversal.

## Design Decisions

- **Horizontal chain layout**: Nodes are arranged left-to-right with arrows between them, matching the standard linked list diagram. The linear flow shows that each node "points to" the next one.
- **BLUE-filled circles**: Nodes use BLUE fill (opacity=0.5) to give them visual weight and make the chain stand out. BLUE is neutral/informational.
- **Head starts large, then shrinks**: The head node begins at scale=2 to introduce it as the starting point. It then shrinks to scale=1 and shifts left using MoveToTarget, similar to the binary tree root pattern. This progressive disclosure teaches "this is where the list begins."
- **Arrows (Line + add_tip) between nodes**: Each arrow is a Line with buff=0 (touching the node edge) and an arrow tip. The arrow visually represents the "next" pointer in the linked list node.
- **"current" label slides with MoveToTarget**: The traversal is shown by a "current" label that slides RIGHT * 3 at each step. Simultaneously, the previous node returns to BLUE and the current node turns RED. This teaches that traversal means "follow the pointers one at a time."
- **RED for current traversal position**: RED signals "this is where we are now." The node returns to BLUE (its default) when the cursor moves on.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Head label: `LEFT * 4 + UP`, scale=0.9 (shifts UP later)
  - Head node: initially at `UP`, scale=2, then shifts to `LEFT * 3 + DOWN * 1`, scale=1
  - Child nodes: 3 units apart horizontally (center, RIGHT*3)
  - "current" label: starts at `LEFT * 3 + DOWN * 1`, slides RIGHT*3 per step
- **Node sizing**: Circle with surround(buff=0.5), auto-sized to Integer content
- **Arrow lines**: Line(start=node1, end=node2, buff=0) with add_tip()
- **Node spacing**: 3 units between nodes horizontally

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Node circles | BLUE | stroke=BLUE, fill=BLUE opacity=0.5 |
| Node data | WHITE | Integer mobject |
| Currently traversed | RED | FadeToColor on circle [1] |
| Head label | WHITE | scale=0.9 |
| Current label | WHITE | scale=0.9 |
| Arrows | WHITE | Line with add_tip(), buff=0 |
| Head label line | WHITE | Line with buff=0.2 |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + head Write | run_time=1 | Simultaneous |
| Head label line | run_time=0.5 | ShowCreation |
| Head shrink + shift | run_time=0.5 | MoveToTarget + ReplacementTransform |
| Arrow Write | run_time=0.5 | Per edge |
| Child node Write | run_time=0.5 | Per node |
| Current label + highlight | run_time=0.4 | Per traversal step |
| Traversal wait | wait=0.5 | Between steps |
| Final wait | wait=6 | Long hold |
| Total video | ~15 seconds | Build + 3-step traversal + hold |

## Patterns

### Pattern: Linked List Node Chain Construction

**What**: Build a linked list by creating circle nodes and connecting them with arrow-tipped lines. Each child node is positioned 3 units to the right. The arrow is drawn first (Write), then the node appears (Write + ShowCreation). This order shows "the pointer exists, then the node it points to appears."
**When to use**: Singly linked list, doubly linked list, chain-of-responsibility visualization, sequential node connections, any data structure where nodes point to the next element.

```python
# Source: projects/manim-videos/singly-linked-list.py:65-77
child1_node = createNode(3)
head_node_to_child1_node = Line(start=head_node, end=child1_node, buff=0)
head_node_to_child1_node.add_tip()
self.play(Write(head_node_to_child1_node), run_time=0.5)
self.play(Write(child1_node[0]), ShowCreation(child1_node[1]), run_time=0.5)

child2_node = createNode(9)
child2_node.shift(RIGHT * 3)
child1_node_to_child2_node = Line(start=child1_node, end=child2_node, buff=0)
child1_node_to_child2_node.add_tip()
self.play(Write(child1_node_to_child2_node), run_time=0.5)
self.play(Write(child2_node[0]), ShowCreation(child2_node[1]), run_time=0.5)
```

### Pattern: Sliding Traversal Label with Color Cursor

**What**: A "current" text label slides along the linked list using generate_target/MoveToTarget (shifting RIGHT*3 per step). Simultaneously, the current node turns RED and the previous node returns to BLUE via FadeToColor. This creates a visual "cursor" that walks the list.
**When to use**: Linked list traversal, iterator visualization, sequential scan of any chain structure, teaching how to walk a linked list with a pointer variable.

```python
# Source: projects/manim-videos/singly-linked-list.py:81-89
self.play(Write(current_label), FadeToColor(head_node[1], color=RED), run_time=0.4)
current_label.generate_target()
current_label.target.shift(RIGHT * 3)
self.wait(0.5)
self.play(MoveToTarget(current_label),
          FadeToColor(head_node[1], color=BLUE),
          FadeToColor(child1_node[1], color=RED), run_time=0.4)
current_label.generate_target()
current_label.target.shift(RIGHT * 3)
self.wait(0.5)
self.play(MoveToTarget(current_label),
          FadeToColor(child1_node[1], color=BLUE),
          FadeToColor(child2_node[1], color=RED), run_time=0.4)
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a linked list?" writes. Head node (2) appears large and centered. "head" label with connecting line appears.
2. **Head repositioning** (2-3s): Head node shrinks to half and shifts left. Label follows via MoveToTarget + ReplacementTransform on line.
3. **Build chain** (3-5s): Arrow from head writes, then node 3 appears. Arrow from 3 writes, then node 9 appears. Chain is now 2 -> 3 -> 9.
4. **Traversal start** (5-6s): "current" label appears below head. Head node turns RED.
5. **Step to node 3** (6-7s): "current" slides right. Head returns to BLUE, node 3 turns RED.
6. **Step to node 9** (7-8s): "current" slides right again. Node 3 returns to BLUE, node 9 turns RED.
7. **Done** (8-14s): Wait 6s on final state with current at last node.

> Full file: `projects/manim-videos/singly-linked-list.py` (92 lines)
