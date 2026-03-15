---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/moving_dots.py
project: ragibson_manim-videos
domain: [mathematics, geometry]
elements: [dot, line]
animations: [animate_parameter]
layouts: [centered]
techniques: [value_tracker, add_updater]
purpose: [demonstration]
mobjects: [Dot, Line, VGroup, ValueTracker]
manim_animations: []
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 22
scene_classes: [MovingDots]
---

## Summary

Minimal example of ValueTracker-driven animation with two dots connected by a line. A blue dot moves along the x-axis and a green dot moves along the y-axis, each controlled by a separate ValueTracker. The connecting line rebuilds every frame via add_updater with become(). Demonstrates the fundamental pattern of using ValueTrackers to drive mobject positions while keeping dependent objects (the line) synchronized.

## Design Decisions

- **Two independent ValueTrackers for x and y**: Rather than a single tracker or direct position animation, using separate x and y trackers makes each axis independently controllable. This is the minimal example of multi-tracker coordination.
- **Line rebuilds via become()**: The line's updater creates a fresh Line object from the current dot centers and calls become(). This is simpler than updating start/end points directly and avoids issues with Line's internal path representation.
- **set_x and set_y updaters**: The dots use set_x/set_y rather than move_to, which only affects one axis and leaves the other axis position unchanged. This is important when you want constrained motion.

## Composition

- **Dots**: d1 (BLUE) and d2 (GREEN), arranged RIGHT buff=1
- **Line**: RED, from d1 center to d2 center
- **Motion**: x tracker moves d1 horizontally, y tracker moves d2 vertically

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Dot 1 | BLUE | Moves horizontally |
| Dot 2 | GREEN | Moves vertically |
| Connecting line | RED | Rebuilds every frame |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| x to 5 | default | d1 moves right |
| y to 4 | default | d2 moves up |
| x to 2, y to 3 | default | Both move simultaneously |
| Total | ~4s | |

## Patterns

### Pattern: ValueTracker-Driven Dots with Connected Line

**What**: Two dots have add_updater calls that set their x or y position from ValueTracker values. A connecting line has an updater that rebuilds itself from the current dot positions using become(). Animating the ValueTrackers smoothly moves the dots and the line follows automatically.
**When to use**: Any two-point connection that needs to stay linked (endpoints of a segment, nodes in a graph), constrained motion along one axis, demonstrating ValueTracker basics, interactive geometry where points drive dependent constructions.

```python
# Source: projects/ragibson_manim-videos/manim_examples/moving_dots.py:4-21
d1, d2 = Dot(color=BLUE), Dot(color=GREEN)
dg = VGroup(d1, d2).arrange(RIGHT, buff=1)
l1 = Line(d1.get_center(), d2.get_center()).set_color(RED)

x, y = ValueTracker(0), ValueTracker(0)

d1.add_updater(lambda z: z.set_x(x.get_value()))
d2.add_updater(lambda z: z.set_y(y.get_value()))
l1.add_updater(lambda z: z.become(Line(d1.get_center(), d2.get_center())))

self.add(d1, d2, l1)
self.play(x.animate.set_value(5))
self.play(y.animate.set_value(4))
self.play(x.animate.set_value(2), y.animate.set_value(3))
```

## Scene Flow

1. **Setup** (0s): Blue and green dots appear 1 unit apart, connected by red line.
2. **Move x** (0-1s): Blue dot slides right to x=5, line stretches.
3. **Move y** (1-2s): Green dot slides up to y=4, line rotates.
4. **Move both** (2-3s): Blue dot to x=2, green dot to y=3 simultaneously.

> Full file: `projects/ragibson_manim-videos/manim_examples/moving_dots.py` (22 lines)
