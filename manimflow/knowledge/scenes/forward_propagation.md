---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/forward_prop.py
project: manim-animations
domain: [machine_learning, neural_networks, deep_learning]
elements: [neuron, layer, weight_connection, surrounding_rect, label]
animations: [fade_in, write, draw, passing_flash, fade_out]
layouts: [layered, horizontal_row]
techniques: [passing_flash_signal]
purpose: [process, step_by_step, demonstration]
mobjects: [Circle, Line, Text, MathTex, VGroup, SurroundingRectangle]
manim_animations: [FadeIn, FadeOut, Write, Create, ShowPassingFlash]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 77
scene_classes: [ForwardPropagation]
---

## Summary

Visualizes forward propagation through a 3-layer neural network (4 input, 3 hidden, 2 output nodes). Neurons are colored circles (BLUE input, GREEN hidden, RED output) connected by lines. Signal flow is shown via ShowPassingFlash traveling along connections in YELLOW, with semi-transparent node fills indicating which layer is currently active. The output layer displays numeric predictions (0.85, 0.30) with a SurroundingRectangle highlighting the top prediction.

## Design Decisions

- **Color per layer (BLUE/GREEN/RED)**: Each layer gets a distinct color so the viewer instantly knows which layer is which. This is the standard neural network color convention — input, hidden, output.
- **ShowPassingFlash for signal propagation**: Instead of moving dots along connections, ShowPassingFlash creates a YELLOW pulse that travels along each line simultaneously. This shows all connections firing at once, which is how forward propagation actually works — all weights in a layer compute in parallel.
- **Semi-transparent fills for activation**: `set_opacity(0.4)` copies of node circles fade in/out to show which layer is "active." Input layer fills first, then hidden, then output. The low opacity keeps the node borders visible.
- **Fully-connected topology**: Every input connects to every hidden node (4x3=12 lines), every hidden to every output (3x2=6 lines). All connections are created simultaneously — the viewer sees the full network before the signal flows.
- **SurroundingRectangle for prediction highlight**: The output node with the highest value (0.85) gets a YELLOW rectangle, drawing attention to the "winner."

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Forward Propagation"
  - Input layer: `shift(LEFT * 3)`, 4 nodes arranged DOWN with buff=1
  - Hidden layer: centered (default), 3 nodes arranged DOWN with buff=1
  - Output layer: `shift(RIGHT * 3)`, 2 nodes arranged DOWN with buff=1
  - Output values: `next_to(output_node, RIGHT, buff=0.2)`
- **Node sizing**: Circle(radius=0.3) for all nodes
- **Labels**: Input labels x_1-x_4 next_to LEFT, hidden h_1-h_3 next_to UP, output y_1-y_2 next_to UP, all font_size=24
- **Connections**: Line from node.get_right() to node.get_left()

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Input nodes | BLUE | Circle radius=0.3 |
| Hidden nodes | GREEN | Circle radius=0.3 |
| Output nodes | RED | Circle radius=0.3 |
| Node labels | WHITE | font_size=24 |
| Connections | WHITE | Line, default stroke |
| Signal flash | YELLOW | ShowPassingFlash, time_width=0.5 |
| Active layer fill | BLUE/GREEN/RED | opacity=0.4 |
| Output values | WHITE | font_size=28, "0.85" and "0.30" |
| Prediction highlight | YELLOW | SurroundingRectangle |

Color strategy: Layer colors (BLUE/GREEN/RED) provide immediate spatial identification. YELLOW is reserved for dynamic signal and attention — the flash and the prediction highlight.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| All nodes FadeIn | ~1s | Simultaneous |
| All labels Write | ~1s | Simultaneous, + 2s wait |
| All connections Create | ~1s | Simultaneous, + 2s wait |
| Input layer fill FadeIn | run_time=0.3 | Quick activation |
| Input-to-hidden flash | run_time=1 | All 12 connections flash |
| Input fill out, hidden fill in | run_time=0.3 | + 1s wait |
| Hidden-to-output flash | run_time=1 | All 6 connections flash |
| Hidden fill out, output fill in | run_time=0.3 | |
| Output fill out, values Write | ~1s | + 1s wait |
| Prediction highlight | ~1s | Create + FadeOut |
| Total video | ~16 seconds | |

## Patterns

### Pattern: ShowPassingFlash for Signal Propagation

**What**: Create a colored copy of each connection line, then use ShowPassingFlash to animate a pulse traveling along it. All flashes play simultaneously, simulating parallel computation. The time_width parameter controls how wide the flash "tail" is — 0.5 gives a short bright pulse.
**When to use**: Neural network forward/backward propagation, data flow through pipelines, signal transmission in networks, any visualization where information travels along edges simultaneously.

```python
# Source: projects/manim-animations/src/forward_prop.py:50-58
flashes_ih = [
    ShowPassingFlash(
        conn.copy().set_color(YELLOW),
        time_width=0.5
    ) for conn in connections_input_to_hidden
]

self.play(FadeIn(filled_input), run_time=0.3)
self.play(*flashes_ih, run_time=1)
self.play(FadeOut(filled_input), FadeIn(filled_hidden), run_time=0.3)
```

### Pattern: Layer Activation via Semi-Transparent Fill

**What**: Create a copy of the node group with `set_opacity(0.4)`. FadeIn the copy when the layer is "active," FadeOut when propagation moves to the next layer. This gives a subtle glow effect without obscuring the node structure.
**When to use**: Showing which layer/component is currently processing in neural networks, pipeline stages, or any multi-stage system where "current step" needs visual emphasis.

```python
# Source: projects/manim-animations/src/forward_prop.py:10-11
filled_input = input_nodes.copy().set_opacity(0.4)

# Later in animation:
self.play(FadeIn(filled_input), run_time=0.3)
# ... signal flows ...
self.play(FadeOut(filled_input), FadeIn(filled_hidden), run_time=0.3)
```

### Pattern: Fully Connected Layer Construction

**What**: Generate all connections between two layers using a nested list comprehension. Every node in layer A connects to every node in layer B via a Line from get_right() to get_left(). All connections are created in one self.play() call.
**When to use**: Neural network architecture visualization, bipartite graph construction, any fully connected layer-to-layer wiring.

```python
# Source: projects/manim-animations/src/forward_prop.py:26-36
connections_input_to_hidden = [
    Line(input_nodes[i].get_right(), hidden_nodes[j].get_left())
    for i in range(4)
    for j in range(3)
]

connections_hidden_to_output = [
    Line(hidden_nodes[i].get_right(), output_nodes[j].get_left())
    for i in range(3)
    for j in range(2)
]
```

## Scene Flow

1. **Structure** (0-6s): Title writes. All 9 nodes fade in simultaneously. Labels (x1-x4, h1-h3, y1-y2) write. 18 connection lines create.
2. **Forward pass: input to hidden** (6-9s): Input nodes glow (opacity=0.4 fill). YELLOW flashes travel along all 12 input-to-hidden connections simultaneously. Input glow fades, hidden glow appears.
3. **Forward pass: hidden to output** (9-12s): YELLOW flashes travel along all 6 hidden-to-output connections. Hidden glow fades, output glow appears.
4. **Result** (12-16s): Output glow fades. Values "0.85" and "0.30" write next to output nodes. YELLOW SurroundingRectangle highlights the top output (0.85), then fades out.

> Full file: `projects/manim-animations/src/forward_prop.py` (77 lines)
