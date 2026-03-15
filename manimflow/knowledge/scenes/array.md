---
source: https://github.com/KainaniD/manim-videos/blob/main/array.py
project: manim-videos
domain: [computer_science, data_structures, algorithms]
elements: [array, rectangle_node, label, pointer, highlight_rect]
animations: [fade_in, write, transform, color_change, slide]
layouts: [horizontal_row, edge_anchored]
techniques: [labeled_pointer, color_state_machine, helper_function, factory_pattern, status_text]
purpose: [demonstration, step_by_step, definition]
mobjects: [VGroup, Text, Square, Circle, Line, Rectangle]
manim_animations: [Write, FadeIn, FadeOut, Transform, FadeToColor]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 101
scene_classes: [Array]
---

## Summary

Visualizes array indexing on a 9-element horizontal array of random integers. A BLUE highlight square and labeled pointer slide across each element one-by-one, while a center-top text shows the access expression (e.g., `array[3]==42`) with color-coded index (BLUE) and value (RED). The animation teaches the mapping between an index variable and the element it points to.

## Design Decisions

- **Horizontal row of 9 squares**: Left-to-right layout mirrors how arrays are drawn in textbooks and how memory is visualized as contiguous cells.
- **BLUE highlight square per index**: A colored border square overlays the current element to draw the viewer's eye. BLUE is used for the index because it is informational, not alarming.
- **RED for accessed value**: The data text inside the accessed element turns RED to separate it visually from the index highlight (BLUE). RED grabs attention at the value the viewer should read.
- **Center-top access expression**: `array[i]==value` text with t2c color coding ties the code syntax to the visual. The viewer learns that `array[3]` means "the element at index 3" by seeing both simultaneously.
- **Transform-based sliding**: Instead of destroying and recreating the highlight/label, Transform morphs one state into the next. This creates a smooth sliding effect that visually tracks the pointer moving right.
- **"index" label with arrow**: Briefly shown at the start to explain what the pointer represents, then faded out to reduce clutter during the main loop.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Array: 9 elements starting at `LEFT * 4 + DOWN * 1`, each shifted `RIGHT * i`
  - Index labels: `LEFT * 4 + RIGHT * i + UP`, scale=0.8
  - Access expression: `UP * 2`, scale=0.8
- **Element sizing**: Square(side_length=1), inner Text scale=0.8
- **Array spacing**: 1 unit between elements (each element at `LEFT * 4 + RIGHT * i`)
- **Highlight sizing**: Square(side_length=1, color=BLUE) at same position as element
- **Pointer lines**: Line from label to element, scale=0.8, with arrow tip

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Array squares | stroke=WHITE | fill=WHITE opacity=0 (transparent) |
| Array text | WHITE | Default, scale=0.8 |
| Index highlight | BLUE | Square(side_length=1, color=BLUE) |
| Index number in label | BLUE | Via `t2c={"[i]": BLUE}` |
| Accessed value text | RED | Via FadeToColor on element text |
| Access expression value | RED | Via `t2c={"value": RED}` |
| Circle nodes (unused helper) | stroke=RED | fill=RED opacity=0.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + array FadeIn | run_time=1 | Simultaneous |
| First index label Write | Default (~1s) | Single element |
| "index" label FadeIn/FadeOut | Default + wait=0.5 | Brief explanation |
| Per-element Transform | Default (~1s) + wait=1 | Loop through 8 remaining elements |
| Total video | ~20 seconds | 9 elements at ~2s each |

## Patterns

### Pattern: Indexed Array Element Factory

**What**: Creates a data element as a VGroup of Text + Square. Two variants: `createData` uses a square that auto-sizes, `createDataFixedWidth` uses a fixed-width Rectangle. Both center the text inside the shape.
**When to use**: Any array, list, or sequential data structure visualization where elements need uniform sizing. Use `createDataFixedWidth` when elements have varying text widths but you want consistent cell sizes.

```python
# Source: projects/manim-videos/array.py:21-39
def createData(data):
    data = str(data)
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_square = Square(side_length=1, stroke_color=WHITE)
    node_square.set_fill(WHITE, opacity=0)
    node.add(node_data, node_square)
    return node

def createDataFixedWidth(data, width):
    data = str(data)
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_rectangle = Rectangle(width=width, height=1, stroke_color=WHITE)
    node_rectangle.set_fill(WHITE, opacity=0)
    node.add(node_data, node_rectangle)
    return node
```

### Pattern: Transform-Based Index Pointer Slide

**What**: A highlight group (label + arrow + colored square) is created for each index position upfront. Transform morphs the first group into each subsequent one, creating a smooth sliding effect. The center text expression also transforms in sync. This avoids FadeOut/FadeIn flicker.
**When to use**: Array traversal, linear scan, sequential access demonstrations where a pointer/cursor moves through elements one at a time. Also works for sliding window visualizations.

```python
# Source: projects/manim-videos/array.py:70-80
# Pre-create all index label groups and center texts
for i in range(9):
    index_label = Text(f"array[{i}]", t2c={f"[{i}]": BLUE}).shift(LEFT * 4 + RIGHT * i + UP).scale(0.8)
    index_label_arrow = Line(index_label, array_group[i]).scale(0.8).add_tip()
    index_label_highlight = Square(side_length=1, color=BLUE).shift(LEFT * 4 + RIGHT * i + DOWN)
    index_label_group.add(index_label).add(index_label_arrow).add(index_label_highlight)

# Slide by transforming one group into the next
for i in range(1, 9):
    self.play(
        Transform(index_label_group_array[0], index_label_group_array[i]),
        Transform(center_text_array[0], center_text_array[i]),
        FadeToColor(array_group[i-1][0], WHITE),
        FadeToColor(array_group[i][0], RED)
    )
```

### Pattern: Color-Coded Access Expression with t2c

**What**: A Text mobject displays the code expression `array[i]==value` with the index colored BLUE and the value colored RED using the `t2c` (text-to-color) parameter. This visually links the syntax to the highlighted elements on screen.
**When to use**: Teaching array/matrix indexing, dictionary lookups, any code expression where you want to highlight which part is the key and which part is the value.

```python
# Source: projects/manim-videos/array.py:80
center_text = Text(
    f"array[{i}]=={array_data_values[i]}",
    t2c={f"[{i}]": BLUE, f"{array_data_values[i]}": RED}
).shift(UP * 2).scale(0.8)
```

## Scene Flow

1. **Setup** (0-2s): Title "What is an Array?" writes at top. Array of 9 random-value squares fades in horizontally.
2. **Index introduction** (2-4s): First index label `array[0]` with arrow and BLUE highlight writes on element 0. An "index" label briefly appears and fades to explain the concept.
3. **Value access** (4-5s): Center text `array[0]==value` writes. Element 0's text turns RED.
4. **Traversal** (5-20s): Highlight, arrow, and center text Transform to each subsequent index (1 through 8). Previous element text returns to WHITE, current turns RED. 1-second wait between each step.
5. **Done** (20-22s): Final element highlighted. Wait 2s.

> Full file: `projects/manim-videos/array.py` (101 lines)
