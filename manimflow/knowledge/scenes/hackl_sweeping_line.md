---
source: https://github.com/behackl/manim-with-ease/blob/main/e06_math-and-updaters.py
project: manim-with-ease
domain: [geometry, mathematics, algorithms]
elements: [dot, line]
animations: [draw, color_change, animate_parameter]
layouts: [centered]
techniques: [add_updater, custom_animation]
purpose: [demonstration, exploration]
mobjects: [Circle, Dot, Line]
manim_animations: [Create]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 56
scene_classes: [SweepingLine]
---

## Summary

Visualizes a sweeping line classifier on randomly placed dots. A growing circle reveals 30 dots by switching them from transparent to opaque blue, then a vertical line sweeps left-to-right across the screen, recoloring dots to BLUE or YELLOW based on which side of the line they fall on. Uses chained updaters — each dot starts with an opacity updater that self-destructs and replaces itself with a color updater once triggered.

## Design Decisions

- **Growing circle as reveal mechanism**: Instead of fading in all dots at once, an expanding circle "discovers" them, creating a radar-sweep feel. This makes the initial phase feel like exploration rather than static setup.
- **Updater chaining (clear + re-attach)**: Each dot starts with `opacity_updater` which calls `clear_updaters()` then `add_updater(color_updater)` once triggered. This is a state machine pattern — the dot transitions from "hidden" state to "classifiable" state.
- **Normal vector for half-plane test**: The line's normal vector is computed once via `.copy().rotate(90*DEGREES).get_vector()`. The dot product against this normal determines which side of the line a point is on — a standard computational geometry technique.
- **Random dot placement**: `random.uniform(-6, 6)` for x, `(-4, 4)` for y ensures dots fill the visible frame without overlapping edges.
- **BLUE/YELLOW binary classification**: Two high-contrast colors on opposite sides of the color wheel make the partition instantly readable.
- **Sound on state change**: `self.add_sound("assets/click.wav")` fires only when a dot changes color, creating an auditory connection to the visual event.

## Composition

- **Screen regions**:
  - Dots: randomly placed in range x=[-6, 6], y=[-4, 4]
  - Growing circle: starts at ORIGIN with radius=0.001, scales to 1.5x frame width
  - Moving line: starts at [-7, -5, 0] to [-6, 5, 0] (off-screen left), sweeps 14 units RIGHT then 14 units LEFT
- **Element sizing**: Dot default radius, fill_opacity=0.6 initially
- **Dot count**: 30 dots

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Dots (hidden) | WHITE | fill_opacity=0.6, default color |
| Dots (revealed) | BLUE | opacity=1, set by opacity_updater |
| Dots (right of line) | BLUE | Set by color_updater |
| Dots (left of line) | YELLOW | Set by color_updater |
| Moving line | WHITE | Default Line color |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Circle grow | run_time=5 | Reveals all dots |
| Line creation | default (~1s) | Create(moving_line) |
| Line sweep right | run_time=5 | 14 units RIGHT |
| Line sweep left | run_time=5 | 14 units LEFT |
| Total video | ~16 seconds | |

## Patterns

### Pattern: Updater Chaining (State Machine)

**What**: Attach an initial updater to a mobject that, upon meeting a condition, removes itself and attaches a different updater. This creates a two-state machine: the dot transitions from "waiting to be revealed" to "actively classified" without any external orchestration.

**When to use**: Any visualization where objects need to change behavior mid-scene — particles that activate when reached by a wavefront, nodes that switch from passive to active in a graph traversal, elements that unlock new interactions after a trigger.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:15-26
def opacity_updater(obj):
    if (  # check whether dot is inside circle
        sum((growing_circle.points[0] - growing_circle.get_center())**2)
        >= sum((obj.get_center() - growing_circle.get_center())**2)
    ):
        obj.set_fill(BLUE, opacity=1)
        obj.clear_updaters()  # removes opacity_updater
        obj.add_updater(color_updater)  # attaches the color_updater

def color_updater(obj):
    if (np.dot(obj.get_center(), moving_line.normal_vector)
        < np.dot(moving_line.get_start(), moving_line.normal_vector)):
        if obj.color != Color(BLUE):
            obj.set_color(BLUE)
    else:
        if obj.color != Color(YELLOW):
            obj.set_color(YELLOW)
```

> Gotcha: `clear_updaters()` removes ALL updaters. If you need to keep some, remove only the specific one.

### Pattern: Half-Plane Classification via Normal Vector

**What**: Compute a line's normal vector once, then use `np.dot(point, normal)` vs `np.dot(line_start, normal)` to determine which side of the line a point lies on. This is the standard half-plane test from computational geometry, implemented as a per-frame updater.

**When to use**: Sweepline algorithms, binary spatial partitioning, any visualization where a line divides the plane into two regions and objects need to react to which side they are on — e.g., decision boundaries in ML, geometric proofs about half-planes.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:13-14
moving_line = Line([-7, -5, 0], [-6, 5, 0])
moving_line.normal_vector = moving_line.copy().rotate(90*DEGREES).get_vector()

# Then in the updater:
# np.dot(obj.get_center(), moving_line.normal_vector) < np.dot(moving_line.get_start(), moving_line.normal_vector)
```

### Pattern: Circle Containment Test

**What**: Check whether a point is inside a growing circle by comparing squared distances — `sum((circle.points[0] - center)**2) >= sum((point - center)**2)`. Uses the first Bezier control point of the circle path as the radius reference. No sqrt needed since comparing squared values preserves ordering.

**When to use**: Reveal animations driven by expanding regions, proximity-based triggers, wavefront simulations, radar-sweep effects where objects activate when "reached" by a growing boundary.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:16-19
if (
    sum((growing_circle.points[0] - growing_circle.get_center())**2)
    >= sum((obj.get_center() - growing_circle.get_center())**2)
):
    # point is inside circle
```

## Scene Flow

1. **Setup** (0s): 30 dots placed randomly, all at fill_opacity=0.6. Growing circle added at origin with radius=0.001.
2. **Reveal phase** (0-5s): Circle expands to 1.5x frame width. As it passes each dot, the dot snaps to BLUE opacity=1 and gains a color_updater.
3. **Line appears** (5-6s): Moving line created at far left via `Create`.
4. **Sweep right** (6-11s): Line moves 14 units right. Dots flip between BLUE and YELLOW as the line crosses them.
5. **Sweep left** (11-16s): Line returns 14 units left, re-classifying dots in reverse.

> Full file: `projects/manim-with-ease/e06_math-and-updaters.py` (56 lines)
