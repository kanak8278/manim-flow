---
source: https://github.com/KainaniD/manim-videos/blob/main/stack.py
project: manim-videos
domain: [computer_science, data_structures]
elements: [array, rectangle_node, label, pointer, arrow]
animations: [fade_in, fade_out, slide, write]
layouts: [vertical_stack, edge_anchored]
techniques: [labeled_pointer, helper_function, factory_pattern]
purpose: [definition, demonstration, process]
mobjects: [VGroup, Text, Rectangle, Line]
manim_animations: [Write, FadeInFromPoint, FadeOutToPoint, MoveToTarget]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 94
scene_classes: [Stack]
---

## Summary

Visualizes a stack data structure using a vertical column of 4 wide rectangle elements (20, 29, 10, 35). Elements push from the top (FadeInFromPoint) and pop from the top (FadeOutToPoint). An "accessing" label with an arrow tracks the top element, sliding up with each push and down with each pop. The animation demonstrates LIFO: last element pushed (35) is the first popped.

## Design Decisions

- **Vertical layout**: The stack is shown as a vertical column, matching the common "stack of plates" mental model. Items are added on top and removed from the top. Gravity metaphor reinforces LIFO.
- **Wide rectangles (width=4)**: Rectangle(width=4, height=1) gives elements a wide, flat shape that looks like "plates" stacking. The width also accommodates larger numbers without overflow.
- **FadeInFromPoint from above**: New elements appear by fading in from a point above their final position (get_top() + UP). This creates a "dropping from above" effect that matches the push operation.
- **FadeOutToPoint upward**: Popped elements fade out toward a point above (get_top() + UP), visually "lifting off" the stack. Same direction as entry reinforces top-only access.
- **"accessing" label tracks the top**: The accessing pointer shifts UP with each push and DOWN with each pop via MoveToTarget. This teaches that stack access is always at the top -- you cannot access elements below without popping.
- **Simultaneous push + pointer move**: The FadeInFromPoint and MoveToTarget(accessing) happen in the same play() call, keeping the pointer synchronized with the stack state.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Stack: centered vertically (DOWN*2 to UP), elements 1 unit apart
  - "accessing" label: `LEFT * 4 + DOWN * 2` (initial), scale=0.9
- **Element sizing**: Rectangle(width=4, height=1), inner Text scale=0.8
- **Stack spacing**: 1 unit between elements vertically (DOWN*2, DOWN, center, UP)
- **Pointer movement**: Shifts UP by 1 unit per push, DOWN by 1 unit per pop
- **Arrow**: Line from label to element, scale=0.7, with tip

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Stack rectangles | WHITE | stroke=WHITE, fill=WHITE opacity=0 |
| Stack text | WHITE | scale=0.8 |
| "accessing" label | WHITE | scale=0.9 |
| Accessing arrow | WHITE | Line with add_tip(), scale=0.7 |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + first element | run_time=1 | Simultaneous |
| "accessing" label Write | run_time=1 | With arrow |
| Each push FadeIn + pointer move | run_time=1 | Simultaneous, + wait=0.2 |
| Each pop FadeOut + pointer move | run_time=1 | Simultaneous, + wait=0.2 |
| Post-push wait | wait=1 | After all 4 pushed |
| Final wait | wait=8 | Long hold |
| Total video | ~18 seconds | 4 pushes + 2 pops + hold |

## Patterns

### Pattern: Stack Push with Top Pointer Tracking

**What**: A new element fades in from above via FadeInFromPoint. Simultaneously, the "accessing" pointer group shifts UP by 1 unit via MoveToTarget. This keeps the pointer always aimed at the current top of the stack.
**When to use**: Stack push visualization, function call stack growth, undo history accumulation, any LIFO structure where new items arrive at the top and the access point must track the top.

```python
# Source: projects/manim-videos/stack.py:79-83
for i in range(1, len(stack_group_add)):
    accessing.generate_target()
    accessing.target.shift(UP)
    self.play(FadeInFromPoint(stack_group_add[i], stack_group_add[i].get_top() + UP),
              MoveToTarget(accessing), run_time=1)
    self.wait(0.2)
```

### Pattern: Stack Pop with Top Pointer Tracking

**What**: The top element fades out upward via FadeOutToPoint. Simultaneously, the "accessing" pointer shifts DOWN by 1 unit. This shows the stack shrinking and the access point dropping to the new top. Elements are popped in reverse order (LIFO).
**When to use**: Stack pop visualization, function return (call stack unwinding), undo operations, any LIFO removal where the top element leaves and the pointer must adjust.

```python
# Source: projects/manim-videos/stack.py:85-89
for i in range(len(stack_group_subtract)):
    accessing.generate_target()
    accessing.target.shift(DOWN)
    self.play(FadeOutToPoint(stack_group_subtract[i], stack_group_subtract[i].get_top() + UP),
              MoveToTarget(accessing), run_time=1)
    self.wait(0.2)
```

### Pattern: Wide Fixed-Width Rectangle for Stack Elements

**What**: Stack elements use Rectangle(width=4, height=1) -- wider than the typical width=1 array cell. The extra width creates a "plate" aesthetic that reinforces the stack-of-plates metaphor. Text is scaled to 0.8 to fit within.
**When to use**: Stack visualization, any vertical data structure where elements should look like flat, wide items stacking on top of each other. The wide shape also works for horizontal timelines or progress bars.

```python
# Source: projects/manim-videos/stack.py:32-39
def createDataFixedWidth(data):
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_rectangle = Rectangle(width=4, height=1, stroke_color=WHITE)
    node_rectangle.set_fill(WHITE, opacity=0)
    node.add(node_data, node_rectangle)
    return node
```

## Scene Flow

1. **Setup** (0-1s): Title "What is a stack?" writes. First element (20) fades in from above at bottom of stack area.
2. **Accessing pointer** (1-2s): "accessing" label with arrow pointing to element 20 writes at left.
3. **Push** (2-6s): Elements 29, 10, 35 push onto stack one by one. Each fades in from above while accessing pointer slides up. Stack grows upward.
4. **Pause** (6-7s): Wait 1s with full 4-element stack.
5. **Pop** (7-10s): Top elements 35 then 10 pop off. Each fades out upward while accessing pointer slides down.
6. **Done** (10-18s): Stack has 2 elements (20, 29). Wait 8s.

> Full file: `projects/manim-videos/stack.py` (94 lines)
