---
source: https://github.com/KainaniD/manim-videos/blob/main/queue.py
project: manim-videos
domain: [computer_science, data_structures]
elements: [array, rectangle_node, label, pointer, arrow]
animations: [fade_in, fade_out, slide, write]
layouts: [horizontal_row, edge_anchored]
techniques: [labeled_pointer, helper_function, factory_pattern]
purpose: [definition, demonstration, process]
mobjects: [VGroup, Text, Rectangle, Line]
manim_animations: [Write, FadeInFromPoint, FadeOutToPoint, MoveToTarget]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 95
scene_classes: [Queue]
---

## Summary

Visualizes a queue data structure using a horizontal row of 5 scaled-up rectangle elements (17, 45, 4, 33, 26). Elements enqueue from the left (FadeInFromPoint) and dequeue from the right (FadeOutToPoint), with the remaining elements sliding right to fill gaps. An "accessing" label with an arrow always points to the front element (rightmost). The animation demonstrates FIFO: first element added (17) is the first removed.

## Design Decisions

- **Horizontal layout**: The queue is shown as a horizontal row, which matches the common "line of people" mental model. Elements enter from the left and exit from the right, creating a left-to-right flow.
- **Scale=1.5 on the queue group**: Elements are scaled up to 1.5x for visual prominence. This makes the queue the dominant visual element on screen.
- **FadeInFromPoint for enqueue**: New elements appear by fading in from a point above-left of their position (DOWN*(1/2) + LEFT offset). This creates a "dropping in from above-left" effect that suggests arrival.
- **FadeOutToPoint for dequeue**: Removed elements fade out toward a point above-right (DOWN*(1/2) + RIGHT). This exit direction is opposite to the entry direction, reinforcing the FIFO flow.
- **Remaining elements slide right**: After a dequeue, the group shifts RIGHT*(3/2) via MoveToTarget to fill the gap. This keeps the queue compact and centered.
- **"accessing" pointer stays at front**: The accessing label with arrow always points to the rightmost element (the front of the queue), showing that you can only access the front in a queue.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Queue: centered, scale=1.5 (5 elements from LEFT*2 to RIGHT*2)
  - "accessing" label: `RIGHT * 4 + UP * 2`, scale=0.9
- **Element sizing**: Rectangle(width=1, height=1), scale=1.5 applied to group
- **Queue spacing**: Elements at LEFT*2, LEFT, center, RIGHT, RIGHT*2 (1 unit apart)
- **Slide amount**: RIGHT*(3/2) per dequeue (accounts for 1.5x scale)
- **Arrow**: Line from label to first element, scale=0.7, with tip

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Queue rectangles | WHITE | stroke=WHITE, fill=WHITE opacity=0 |
| Queue text | WHITE | scale=0.8 |
| "accessing" label | WHITE | scale=0.9 |
| Accessing arrow | WHITE | Line with add_tip(), scale=0.7 |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + first element | run_time=1 | Simultaneous |
| "accessing" label Write | run_time=1 | With arrow |
| Each enqueue FadeIn | run_time=1 | Per element, + wait=0.2 |
| Each dequeue FadeOut + slide | run_time=1 | Simultaneous remove + shift |
| Post-enqueue wait | wait=1 | After all 5 added |
| Final wait | wait=8 | Long hold |
| Total video | ~20 seconds | 5 enqueues + 4 dequeues + hold |

## Patterns

### Pattern: Queue Enqueue with FadeInFromPoint

**What**: New elements enter the queue by fading in from a point offset above-left of their final position. The FadeInFromPoint animation creates a smooth "arrival" effect. Elements are added one at a time with a 0.2s pause between each.
**When to use**: Queue visualizations, task scheduling, message queue animations, any FIFO data structure where new items enter at the back.

```python
# Source: projects/manim-videos/queue.py:81-86
self.play(FadeInFromPoint(first, first.get_top() + DOWN * (1/2) + LEFT), run_time=1)

for i in range(1, len(queue_group_add)):
    self.play(FadeInFromPoint(queue_group_add[i],
              queue_group_add[i].get_top() + DOWN * (1/2) + LEFT), run_time=1)
    self.wait(0.2)
```

### Pattern: Queue Dequeue with Shift-to-Fill

**What**: The front element (rightmost) fades out upward-right via FadeOutToPoint. Simultaneously, the remaining elements slide RIGHT*(3/2) via generate_target/MoveToTarget to fill the gap and keep the queue compact. The removed element is also removed from the VGroup to maintain correct indexing.
**When to use**: Queue dequeue operations, conveyor belt simulations, any FIFO process where removing the front item causes remaining items to shift forward.

```python
# Source: projects/manim-videos/queue.py:88-93
for i in range(len(queue_group_subtract)):
    queue_group_add.remove(queue_group_subtract[i])
    queue_group_add.generate_target()
    queue_group_add.target.shift(RIGHT * (3/2))
    self.play(
        FadeOutToPoint(queue_group_subtract[i],
                       queue_group_subtract[i].get_top() + DOWN * (1/2) + RIGHT),
        MoveToTarget(queue_group_add), run_time=1)
    self.wait(0.2)
```

## Scene Flow

1. **Setup** (0-1s): Title "What is a queue?" writes. First element (17) fades in from above-left.
2. **Accessing pointer** (1-2s): "accessing" label with arrow pointing to element 17 writes.
3. **Enqueue** (2-7s): Elements 45, 4, 33, 26 fade in one by one from above-left, each entering to the left of the previous (back of queue).
4. **Pause** (7-8s): Wait 1s with full 5-element queue.
5. **Dequeue** (8-14s): Front elements (17, then 45, 4, 33) dequeue one by one. Each dequeue: front fades out to above-right, remaining elements slide right to fill gap.
6. **Done** (14-22s): Only element 26 remains. Wait 8s.

> Full file: `projects/manim-videos/queue.py` (95 lines)
