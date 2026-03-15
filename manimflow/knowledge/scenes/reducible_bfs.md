---
source: https://github.com/nipunramk/Reducible/blob/main/2020/BFS/bfs.py
project: Reducible
domain: [computer_science, algorithms, graph_theory, searching]
elements: [graph, node, circle_node, line, arrow, label, surrounding_rect, grid, pixel_grid]
animations: [fade_in, fade_out, write, draw, transform, transform_from_copy, highlight, indicate, color_change, grow, lagged_start]
layouts: [centered, scattered, grid, hierarchy]
techniques: [custom_mobject, algorithm_class_separation, color_state_machine, progressive_disclosure, dual_track_visualization]
purpose: [step_by_step, demonstration, exploration, process]
mobjects: [Circle, Line, VGroup, TextMobject, ArcBetweenPoints, Arrow]
manim_animations: [FadeIn, FadeOut, ShowCreation, Transform, TransformFromCopy, GrowFromCenter, CircleIndicate, LaggedStartMap, ShowCreationThenDestruction]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 2696
scene_classes: [GraphNode, GraphAnimationUtils, Introduction, Transition, BFSIntuitionPart1, BFSIntuitionPart2, BFSImplementation, FloodFill, FloodFillImplementation]
---

## Summary

Visualizes Breadth-First Search on custom graph structures. Features a reusable GraphNode class with Circle+Text mobjects, neighbor/edge tracking, and multiple connection types (Line, Arrow, ArcBetweenPoints). The GraphAnimationUtils base class provides highlight_node (colored surround circle), sharpie_edge (thick colored edge overlay), and full BFS animation orchestration. Includes a FloodFill application on grid structures. Used as the foundation pattern for DFS and FFT files.

## Design Decisions

- **GraphNode as data+visual class**: Each node stores position, radius, neighbors list, edges list, and its Circle+Text mobjects. The `connect()` method creates edges as Lines between circle boundaries (not centers), handles both directions, and updates both nodes' neighbor/edge lists.
- **Surround circle for highlighting**: Instead of changing node fill, a separate colored Circle (GREEN_SCREEN, stroke_width=8) is drawn on top. StartAngle rotates to meet the incoming edge direction, creating a smooth visual flow.
- **Sharpie edge**: A new thick Line (stroke_width=12) drawn on top of the existing thin edge. Color GREEN_SCREEN by default. This preserves the original edge while showing the BFS tree.
- **Angle-of-intersection calculation**: For each highlighted node, the surround circle's start_angle is computed by finding the closest point on the circle circumference to the last edge's endpoint. This creates a seamless "flowing into" animation.
- **Order display**: TransformFromCopy from node data text to an order text at bottom, showing BFS traversal sequence being built.
- **Huge graph for intro**: 72-node hex-grid graph for dramatic intro, with LaggedStartMap ShowCreationThenDestruction flashes before the actual BFS.

## Composition

- **Node sizing**: Circle radius=0.4, text scale=0.9, positioned at explicit coordinates
- **Graph layout**: Manually positioned using LEFT/RIGHT/UP/DOWN * integer values, spanning ~10 units wide
- **Highlight circle**: Same radius as node circle, stroke_width=8, no fill
- **Sharpie edge**: stroke_width=12 * scale_factor, on top of original edge (stroke_width=7)
- **Edge color**: GRAY default, GREEN_SCREEN when traversed
- **Node fill**: DARK_BLUE_B fill_opacity=0.5, BLUE stroke
- **Huge graph**: 72 nodes in hex grid, radius=0.2, scale=0.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Node fill | DARK_BLUE_B | opacity=0.5 |
| Node stroke | BLUE | Circle |
| Node text | WHITE | data_color |
| Edge default | GRAY | stroke_width=7 |
| Highlighted edge | GREEN_SCREEN | stroke_width=12 (sharpie) |
| Highlighted node | GREEN_SCREEN | Surround circle, stroke_width=8 |
| Neighbor indicate | default (YELLOW) | CircleIndicate animation |
| Intro flashes | GREEN_SCREEN | ShowCreationThenDestruction |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Node highlight | run_time=1 | ShowCreation of surround circle |
| Edge sharpie | run_time=1 | ShowCreation of thick line |
| CircleIndicate neighbors | run_time=2 | All neighbors simultaneously |
| TransformFromCopy to order | default | Node text copies to order text |
| Intro huge graph BFS | run_time=3 | LaggedStartMap for flash effect |
| Total video | ~15 minutes | BFS intuition + implementation + FloodFill |

## Patterns

### Pattern: GraphNode with Edge-Aware Connections

**What**: GraphNode stores Circle+Text at a position, with a neighbors list and edges list. The `connect()` method creates a Line from one circle boundary to another (not center-to-center), using unit vectors and radius offsets. Both nodes get updated neighbor and edge references.

**When to use**: Any custom graph visualization where you need manual control over node positions, edge connections, and traversal state. BFS, DFS, shortest path, any graph algorithm.

```python
# Source: projects/Reducible/2020/BFS/bfs.py:5-56
class GraphNode:
    def __init__(self, data, position=ORIGIN, radius=0.5, neighbors=[], scale=1):
        self.char = data
        self.data = TextMobject(str(data)).scale(scale)
        self.neighbors = []
        self.circle = Circle(radius=radius).move_to(position)
        self.data.move_to(position)
        self.edges = []

    def connect(self, other):
        line_center = Line(self.center, other.center)
        unit_vector = line_center.get_unit_vector()
        new_start = self.center + unit_vector * self.radius
        new_end = other.center - unit_vector * other.radius
        line = Line(new_start, new_end)
        self.neighbors.append(other)
        other.neighbors.append(self)
        self.edges.append(line)
        other.edges.append(line)
        return line
```

### Pattern: Node Highlight with Direction-Aware Surround Circle

**What**: Highlights a node by drawing a colored Circle on top that starts from the angle where the incoming edge arrives. The angle is computed by testing all 360 degree positions on the circle circumference and finding the closest to the edge endpoint.

**When to use**: Graph traversal visualizations (BFS, DFS, Dijkstra) where you want the highlight to "flow" from the edge into the node, creating directional continuity.

```python
# Source: projects/Reducible/2020/BFS/bfs.py:262-311
def find_angle_of_intersection(self, graph, last_point, node_index):
    node = graph[node_index]
    distances = []
    for angle in range(360):
        respective_line = Line(node.circle.get_center(),
            node.circle.get_center() + RIGHT * node.circle.radius)
        respective_line.rotate(angle / 360 * TAU, about_point=node.circle.get_center())
        distances.append(np.linalg.norm(respective_line.get_end() - last_point))
    return np.argmin(np.array(distances))

def highlight_node(self, graph, index, color=GREEN_SCREEN,
                   start_angle=TAU/2, scale_factor=1, run_time=1):
    node = graph[index]
    surround_circle = Circle(radius=node.circle.radius * scale_factor,
                             start_angle=start_angle, TAU=-TAU)
    surround_circle.set_stroke(width=8 * scale_factor).set_color(color)
    surround_circle.set_fill(opacity=0)
    surround_circle.move_to(node.circle.get_center())
    self.play(ShowCreation(surround_circle), run_time=run_time)
    return surround_circle
```

### Pattern: BFS Animation Orchestration

**What**: Full BFS animation driven by a pre-computed traversal order (list of node IDs and edge tuples). Each element is either an int (highlight node) or a tuple (sharpie edge). The order text builds up via TransformFromCopy as nodes are visited. Neighbor indication via CircleIndicate.

**When to use**: Any graph traversal where you want to animate the discovery order with edge highlighting, node highlighting, and a running record of visited nodes.

```python
# Source: projects/Reducible/2020/BFS/bfs.py:84-101
def show_bfs(self, graph, edge_dict, full_order, wait_times, scale_factor=1):
    angle = 180
    for element in full_order:
        if isinstance(element, int):
            surround_circle = self.highlight_node(graph, element,
                start_angle=angle/360 * TAU, scale_factor=scale_factor)
        else:
            last_edge = self.sharpie_edge(edge_dict, element[0], element[1],
                scale_factor=scale_factor)
            angle = self.find_angle_of_intersection(graph, last_edge.get_end(), element[1])
```

## Scene Flow

1. **Introduction** (0-2min): 72-node hex graph with dramatic flash sequence (ShowCreationThenDestruction), then full BFS traversal.
2. **BFS Intuition Part 1** (2-6min): Small 5-node graph. String edges (visual metaphor for connections). Layer-by-layer exploration.
3. **BFS Intuition Part 2** (6-10min): 10-node graph. Full BFS with order tracking, neighbor indication at each step.
4. **BFS Implementation** (10-14min): Code walkthrough with graph animation.
5. **FloodFill** (14-18min): BFS applied to grid-based pixel filling. Grid cells colored as BFS expands.

> Note: Uses manimlib (not Community Edition). TextMobject, ShowCreation, CONFIG dict, positional animation syntax.
