---
source: https://github.com/KainaniD/manim-videos/blob/main/depth-search.py
project: manim-videos
domain: [computer_science, algorithms, graph_theory, searching, data_structures]
elements: [tree, circle_node, rectangle_node, arrow, line, label]
animations: [highlight, color_change, fade_in, fade_out, write]
layouts: [hierarchy, dual_panel, vertical_stack]
techniques: [color_state_machine, dual_track_visualization, helper_function, factory_pattern]
purpose: [step_by_step, demonstration, process]
mobjects: [Circle, Rectangle, VGroup, Text, Line]
manim_animations: [Write, FadeToColor, FadeInFromPoint, FadeOutToPoint]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 167
scene_classes: [DepthSearch]
---

## Summary

Visualizes depth-first search on a tree with 11 nodes (a-k). The tree is displayed on the left half of the screen, and a stack data structure is shown on the right. As DFS explores each node, it turns RED (currently visiting) then GREY (visited). The stack grows when DFS descends deeper and shrinks when it backtracks. This dual-track visualization (tree + stack side by side) shows WHY DFS goes deep before going wide -- the stack's LIFO behavior drives the traversal order.

## Design Decisions

- **Dual-track visualization (tree + stack)**: Mirrors the BFS + queue pattern but with a stack instead. The stack on the right explains the mechanism -- "DFS uses a stack, that's why it goes deep before wide." The stack grows tall during descent and shrinks during backtracking, making the depth-first pattern visceral.
- **Tree on LEFT, stack on RIGHT**: Consistent with the BFS visualization layout. The viewer sees the tree (problem) on the left and the stack (mechanism) on the right.
- **Three-color state system (WHITE -> RED -> GREY)**: Same CLRS-standard coloring as BFS. WHITE = unvisited, RED = currently processing, GREY = already visited. Consistency across BFS and DFS helps the viewer compare the two algorithms.
- **Stack shown as vertical pile growing upward**: New elements fade in from above (FadeInFromPoint from UP*2). Removed elements fade out upward (FadeOutToPoint to UP). The stack grows upward as DFS descends, creating a visual correlation between tree depth and stack height.
- **Explicit backtracking shown**: When DFS reaches a leaf, the stack shrinks as it backtracks. The viewer sees the stack pop multiple times in sequence, which teaches that DFS must unwind before exploring siblings.
- **Same helper functions as BFS**: createNode, createRectangleNode, highlight, addToStack, removeFromStack are identical to the BFS codebase. This consistency lets the viewer (and the LLM) transfer patterns between the two.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2 -- "What is Depth First Search?"
  - Tree: `UP * 2 + LEFT * 2` (root node), children offset DOWN and LEFT/RIGHT
  - Stack: `RIGHT * 5 + DOWN * 3` (starting position), grows upward
- **Tree layout**:
  - Root "a" at `UP * 2 + LEFT * 2`
  - Level 1: x_offset=+-2, y_offset=1, buffer=0.35
  - Level 2+: x_offset=+-1, y_offset=2, buffer=0.31
  - Edges are Lines with arrow tips
- **Stack layout**:
  - Starts at `RIGHT * 5 + DOWN * 3`
  - Each new element appears at `stack[-1].get_center() + UP`
  - Rectangle width=3, height=1
- **Node sizing**: Circle radius=0.5 for tree nodes, Rectangle(3, 1) for stack elements

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Unvisited nodes | WHITE | stroke_color=WHITE, default |
| Currently visiting | RED | Via FadeToColor highlight |
| Already visited | GREY | Dimmed, no longer active |
| Stack rectangles | WHITE | stroke_color=WHITE, fill=WHITE opacity=0 |
| Stack text | WHITE | scale=0.8 |
| Tree edges | WHITE | Line with arrow tip, buff=0.31-0.35 |
| Title | WHITE | scale=1.2 |

Color strategy: Identical to BFS -- 3 states, 3 colors (WHITE -> RED -> GREY). Matches CLRS textbook coloring.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + Tree Write | Default (~1s) | Simultaneous |
| Node highlight (color change) | run_time=0.75 | RED active, GREY previous |
| Stack add (FadeInFromPoint) | Default (~1s) | Enters from above |
| Stack remove (FadeOutToPoint) | Default (~1s) | Exits upward |
| Backtrack wait | wait=0.5 | Before each stack pop sequence |
| Total video | ~80 seconds | 11 nodes, deeper paths = more time |

## Patterns

### Pattern: Animated Stack (Push from Top, Pop from Top)

**What**: A visual stack implemented as a vertical pile of rectangles. New items fade in from above the stack top. When an item is removed, it fades out upward. This mirrors LIFO behavior visually -- last in (top) is first out (top). Contrast with the queue pattern where items enter from below and exit from above.
**When to use**: DFS visualization, function call stack, undo/redo operations, any LIFO process. Pair with a tree/graph for dual-track visualization.

```python
# Source: projects/manim-videos/depth-search.py:54-64
def createStack(element):
    return VGroup().add(element)

def addToStack(self, stack, new_element):
    new_element.shift(stack[-1].get_center() + UP)
    self.play(FadeInFromPoint(new_element, stack[-1].get_center() + UP * 2))
    stack.add(new_element)

def removeFromStack(self, stack):
    self.play(FadeOutToPoint(stack[-1], stack[-1].get_center() + UP))
    stack.remove(stack[-1])
```

### Pattern: DFS Backtracking Sequence

**What**: When DFS reaches a leaf node, the visualization shows multiple stack pops in sequence as the algorithm backtracks up the tree. Each pop is accompanied by a highlight change on the tree (the current node returns to the parent). The viewer sees the stack shrink rapidly during backtracking, which contrasts with the slow growth during descent.
**When to use**: DFS traversal, recursive algorithm unwinding, any process where a stack unwinds multiple levels. The rapid successive pops create a visual "snapping back" effect.

```python
# Source: projects/manim-videos/depth-search.py:108-136
# DFS reaches leaf "h" -- backtrack to root
self.wait(0.5)
removeFromStack(self, stack)              # pop "h"
highlight(self, RED, tree[5], GREY, tree[13])   # back to "d"
removeFromStack(self, stack)              # pop "d"
highlight(self, RED, tree[1], GREY, tree[5])    # back to "b"
# ... continues popping back to "a"
removeFromStack(self, stack)              # pop "b"
highlight(self, RED, tree[0], GREY, tree[1])    # back to root "a"
```

### Pattern: Three-State Color Machine for Graph Traversal

**What**: Nodes transition through exactly 3 states via color: WHITE (unvisited) -> RED (currently processing) -> GREY (visited/done). The highlight() function changes the current node to RED and the previous node to GREY in one animation call.
**When to use**: Any graph/tree traversal algorithm (BFS, DFS, topological sort, Dijkstra). Also works for state machine visualization, workflow progress tracking, or any sequential process where items move through states.

```python
# Source: projects/manim-videos/depth-search.py:41-45
def highlight(self, color, item, color2=WHITE, *items):
    item_group = VGroup()
    for i in items:
        item_group.add(i)
    self.play(FadeToColor(item, color), FadeToColor(item_group, color2), run_time=0.75)
```

## Scene Flow

1. **Setup** (0-2s): Title "What is Depth First Search?" writes at top. Full tree with 11 nodes (a-k) and directed edges writes on the left half.
2. **Root visit** (2-4s): Node "a" turns RED. Stack with "a" fades in on the right.
3. **Left subtree descent** (4-20s): DFS goes deep: a -> c -> b -> d -> h. Each step: node turns RED, parent turns GREY, child pushed to stack. Stack grows taller with each descent.
4. **First backtrack** (20-28s): "h" is a leaf. Stack pops "h", "d", back to "b". Then DFS explores "e" subtree: e -> i (leaf, pop), j (leaf, pop). More backtracking pops.
5. **Right subtree** (28-50s): DFS returns to root "a", then explores right: c -> f (leaf, pop), g -> k (leaf, pop). Stack grows and shrinks with each branch.
6. **Final backtrack** (50-75s): All remaining nodes visited. Stack pops all the way back to empty. Root "a" turns GREY.
7. **Done** (75-80s): All nodes GREY. Stack empty. Wait 1s.

> Full file: `projects/manim-videos/depth-search.py` (167 lines)
