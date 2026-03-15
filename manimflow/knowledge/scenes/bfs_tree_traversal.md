---
source: https://github.com/KainaniD/manim-videos/blob/main/breadth-search.py
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
lines: 186
scene_classes: [BreadthSearch]
---

## Summary

Visualizes breadth-first search on a tree with 11 nodes (a-k). The tree is displayed on the left half of the screen, and a queue data structure is shown on the right. As BFS explores each node, it turns RED (currently visiting) then GREY (visited). The queue grows and shrinks in sync — nodes are enqueued as discovered and dequeued as processed. This dual-track visualization (tree + queue side by side) is the key pedagogical technique: the viewer sees BOTH the traversal and the data structure driving it.

## Design Decisions

- **Dual-track visualization (tree + queue)**: The tree alone doesn't explain WHY BFS visits nodes in breadth-first order. The queue on the right shows the mechanism — "BFS uses a queue, that's why it goes level by level." Showing both simultaneously creates the "aha" connection.
- **Tree on LEFT, queue on RIGHT**: Natural reading order — the viewer looks at the tree (the problem), then looks right at the queue (the mechanism). The tree is the "what", the queue is the "how."
- **Three-color state system (WHITE → RED → GREY)**: WHITE = unvisited (default). RED = currently being processed (attention). GREY = already visited (dimmed, no longer active). This maps to the standard algorithm coloring used in CLRS textbook.
- **Queue shown as vertical stack of rectangles**: Each rectangle contains the node label. New nodes enter from the bottom (FadeInFromPoint from below), processed nodes exit from the top (FadeOutToPoint upward). The queue shifts up as items are removed, maintaining visual continuity.
- **Highlight with simultaneous color changes**: When visiting node X, the highlight function colors X red and simultaneously colors the previous node grey. This two-at-a-time color change creates a visual "moving pointer" effect — attention transfers from old node to new node.
- **Manual tree construction (not Graph mobject)**: The tree is built node-by-node using createNode() + addNodeToGraph() with explicit x/y offsets. This gives precise control over layout but requires manual positioning. Each edge is a Line with an arrow tip.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2 — "What is Breadth First Search?"
  - Tree: `UP * 2 + LEFT * 2` (root node), children offset DOWN and LEFT/RIGHT
  - Queue: `RIGHT * 5 + DOWN * 3` (starting position), grows upward
- **Tree layout**:
  - Root "a" at `UP * 2 + LEFT * 2`
  - Level 1: x_offset=±2, y_offset=1, buffer=0.35
  - Level 2+: x_offset=±1, y_offset=2, buffer=0.31
  - Edges are Lines with arrow tips, buff determines gap between node and arrow
- **Queue layout**:
  - Starts at `RIGHT * 5 + DOWN * 3`
  - Each new element shifts existing queue UP by 1 unit
  - Rectangle width=3, height=1 (wide enough for node labels)
- **Node sizing**: Circle radius=0.5 for tree nodes, Rectangle(3, 1) for queue elements

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Unvisited nodes | WHITE | stroke_color=WHITE, default |
| Currently visiting | RED | Via FadeToColor highlight |
| Already visited | GREY | Dimmed, no longer active |
| Queue rectangles | WHITE | stroke_color=WHITE, fill=WHITE opacity=0 |
| Queue text | WHITE | scale=0.8 |
| Tree edges | WHITE | Line with arrow tip, buff=0.31-0.35 |
| Title | WHITE | scale=1.2 |

Color strategy: Only 3 states, only 3 colors. WHITE (default/unvisited) → RED (active/current) → GREY (done/visited). This maps exactly to the textbook BFS coloring from CLRS Introduction to Algorithms. The viewer who knows BFS from a textbook will immediately recognize the pattern.

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Title + Tree Write | Default (~1s) | Simultaneous |
| Node highlight (color change) | run_time=0.75 | RED active, GREY previous |
| Queue add (FadeInFromPoint) | Default (~1s) | Enters from below |
| Queue remove (FadeOutToPoint) | Default (~1s) | Exits upward |
| Queue shift up (MoveToTarget) | Implicit | Bundled with add |
| Total video | ~60 seconds | 11 nodes, ~5s per node average |

## Patterns

### Pattern: Dual-Track Algorithm Visualization

**What**: Show the algorithm's data structure (queue/stack) alongside the data it operates on (tree/graph). Both update in sync — when BFS dequeues a node, the queue visually shrinks AND the tree node changes color. The viewer sees the cause (queue operation) and effect (node visit) simultaneously.
**When to use**: BFS (tree + queue), DFS (tree + stack), Dijkstra (graph + priority queue), any algorithm where an auxiliary data structure drives the traversal. This is the most effective pattern for teaching graph algorithms — the data structure IS the explanation.

```python
# Source: projects/manim-videos/breadth-search.py:80-120
# Tree on left
tree = createGraph(createNode("a")).shift(UP * 2 + LEFT * 2)
addNodeToGraph(tree, tree[0], createNode("b"), -2, 1, buffer_1)
addNodeToGraph(tree, tree[0], createNode("c"), 2, 1, buffer_1)

# Queue on right
queue = createQueue(createRectangleNode("a", 3, 1)).shift(RIGHT * 5 + DOWN * 3)

# Visit node: highlight tree + update queue in sequence
highlight(self, RED, tree[2], GREY, tree[0])    # Color tree node
highlight(self, RED, tree[1], GREY, tree[2])    # Move to neighbor
addToQueue(self, queue, createRectangleNode("b", 3, 1))  # Enqueue
```

### Pattern: Three-State Color Machine for Graph Traversal

**What**: Nodes transition through exactly 3 states via color: WHITE (unvisited) → RED (currently processing) → GREY (visited/done). The highlight() function changes the current node to RED and the previous node to GREY in one animation call. This creates a visual "cursor" moving through the graph.
**When to use**: Any graph/tree traversal algorithm (BFS, DFS, topological sort, Dijkstra). Also works for state machine visualization, workflow progress tracking, or any sequential process where items move through states.

```python
# Source: projects/manim-videos/breadth-search.py:41-45
def highlight(self, color, item, color2=WHITE, *items):
    item_group = VGroup()
    for i in items:
        item_group.add(i)
    self.play(FadeToColor(item, color), FadeToColor(item_group, color2), run_time=0.75)

# Usage: color current RED, previous GREY simultaneously
highlight(self, RED, tree[2], GREY, tree[0])
```

### Pattern: Animated Queue (Add from Bottom, Remove from Top)

**What**: A visual queue implemented as a vertical stack of rectangles. New items fade in from below the queue. When an item is removed, it fades out upward. The remaining queue shifts up to fill the gap. This mirrors FIFO behavior visually — first in at the bottom, first out from the top.
**When to use**: BFS visualization, task scheduling, message queues, any FIFO process. Pair with a tree/graph for dual-track visualization.

```python
# Source: projects/manim-videos/breadth-search.py:66-78
def addToQueue(self, queue, new_element):
    new_element.shift(queue[-1].get_center())
    queue.generate_target()
    queue.target.shift(UP)
    self.play(FadeInFromPoint(new_element, queue[-1].get_center() + DOWN), MoveToTarget(queue))
    queue.add(new_element)

def removeFromQueue(self, queue):
    self.play(FadeOutToPoint(queue[0], queue[0].get_center() + UP))
    queue.remove(queue[0])
```

### Pattern: Manual Tree Construction with Edges

**What**: Build a tree node-by-node using helper functions. Each node is a Circle + Text VGroup. Edges are Lines with arrow tips. addNodeToGraph() positions the new node relative to its parent using x/y offsets and adds a connecting edge. The buffer parameter controls the gap between node circle and arrow tip.
**When to use**: Tree visualizations where you need precise control over layout. Also works for any directed graph, org charts, family trees, or hierarchical diagrams. For simple trees, this manual approach gives more control than Manim's Graph mobject.

```python
# Source: projects/manim-videos/breadth-search.py:12-19, 47-52
def createNode(data, radius=0.5):
    data = str(data)
    node = VGroup()
    node_data = Text(data)
    node_circle = Circle(radius=radius, stroke_color=WHITE)
    node.add(node_data, node_circle)
    return node

def addNodeToGraph(graph, graph_node, new_node, x_offset, y_offset, buffer):
    new_node = new_node.shift(graph_node.get_center() + RIGHT * x_offset + DOWN * y_offset)
    graph.add(new_node).add(Line(start=graph_node[0], end=new_node[0], buff=buffer).add_tip())

# Build tree: root, then children with offsets
tree = createGraph(createNode("a")).shift(UP * 2 + LEFT * 2)
addNodeToGraph(tree, tree[0], createNode("b"), -2, 1, 0.35)  # left child
addNodeToGraph(tree, tree[0], createNode("c"), 2, 1, 0.35)   # right child
```

## Scene Flow

1. **Setup** (0-2s): Title "What is Breadth First Search?" writes at top. Full tree with 11 nodes (a-k) and directed edges writes on the left half. Queue starts empty on the right.
2. **Root visit** (2-4s): Node "a" turns RED. Queue rectangle "a" fades in on the right.
3. **Level 1** (4-12s): BFS visits "b" and "c" (children of "a"). Each visit: node turns RED, parent turns GREY, child added to queue. After processing "a"'s children, "a" is dequeued.
4. **Level 2** (12-25s): BFS visits "d", "e", "f", "g". Same pattern: RED current, GREY previous, enqueue children, dequeue processed. Queue grows and shrinks, showing the FIFO order.
5. **Level 3** (25-40s): Visits "h", "i", "j". Fewer children to add. Queue is shrinking.
6. **Level 4** (40-55s): Visits "k" (deepest leaf). Queue empties rapidly as remaining nodes have no children.
7. **Done** (55-60s): All nodes are GREY. Queue is empty. Wait 1s.

> Full file: `projects/manim-videos/breadth-search.py` (186 lines)
