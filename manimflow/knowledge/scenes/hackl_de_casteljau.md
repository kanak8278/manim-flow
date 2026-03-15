---
source: https://github.com/behackl/manim-with-ease/blob/main/e06_math-and-updaters.py
project: manim-with-ease
domain: [geometry, mathematics, calculus]
elements: [dot, line, parametric_curve]
animations: [fade_out, animate_parameter, trace_path]
layouts: [centered]
techniques: [value_tracker, add_updater, always_redraw, traced_path, lambda_capture_i]
purpose: [demonstration, derivation, step_by_step]
mobjects: [Dot, Cross, Line, VGroup, ValueTracker, TracedPath]
manim_animations: [FadeOut]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 65
scene_classes: [DeCasteljau]
---

## Summary

Animates de Casteljau's algorithm for constructing a cubic Bezier curve. Four control points (two anchors marked as crosses, two handles as orange dots) are connected by lines. As a ValueTracker sweeps from 0 to 1, intermediate interpolation dots at each level move along their parent segments, with the final red dot tracing out the Bezier curve via TracedPath. After the curve is drawn, all construction scaffolding fades out, leaving only the anchors and the traced curve.

## Design Decisions

- **ValueTracker as the single driver**: One `t` parameter from 0 to 1 drives ALL intermediate dots via chained updaters. This mirrors the mathematical algorithm exactly — every point is a function of t.
- **Hierarchical dot dependencies**: Level-1 dots interpolate between level-0 (control points), level-2 between level-1, level-3 between level-2. Each dot's updater references the dots above it, creating a dependency tree that auto-resolves every frame.
- **Cross markers for anchors, Dot for handles**: Visual distinction between on-curve anchor points (Cross, not movable conceptually) and off-curve control handles (Dot, ORANGE). This matches standard Bezier editing UIs.
- **always_redraw for dynamic lines**: Lines between intermediate dots are wrapped in `always_redraw` so they update every frame. Static lines connect the control points and don't need updating.
- **TracedPath for the curve**: Instead of plotting the Bezier formula directly, the curve emerges from the red dot's traced path. This shows the curve being CONSTRUCTED, not just displayed.
- **Custom background color #455D3E**: A muted olive-green background gives a chalkboard feel and provides good contrast with ORANGE, RED, GRAY, and LIGHT_GRAY elements.
- **Lambda capture with default argument**: `lambda a=a, b=b: Line(...)` in the list comprehension correctly captures loop variables. Without `a=a, b=b`, all lambdas would reference the last values of a and b.

## Composition

- **Screen regions**:
  - Control points: a1=[-3,-2,0], h1=[-3,0,0], h2=[3,0,0], a2=[3,2,0]
  - All construction elements centered in frame
- **Element sizing**: Dot default radius, Cross scale_factor=0.2
- **Control point layout**: Anchors at bottom-left and top-right, handles directly above/below anchors creating an S-shaped control polygon

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | #455D3E | Olive-green, chalkboard feel |
| Anchor points | WHITE | Cross(scale_factor=0.2) |
| Handle points | ORANGE | Dot |
| Level-1 interpolation dots | GRAY | Dot |
| Level-2 interpolation dots | GRAY | Dot |
| Final curve point | RED | Dot |
| Static control polygon lines | ORANGE (endpoints), WHITE (middle) | Line |
| Dynamic interpolation lines | LIGHT_GRAY | always_redraw Line |
| Traced Bezier curve | RED | TracedPath, stroke_color=RED |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Initial wait | 0.5s | Let viewer see control points |
| t sweep 0→1 | run_time=5 | Main animation |
| Post-sweep wait | 0.5s | Pause on completed curve |
| Scaffold fade out | default (~1s) | FadeOut construction lines and intermediate dots |
| Final wait | default (~1s) | Show clean curve |
| Total video | ~8 seconds | |

## Patterns

### Pattern: ValueTracker-Driven Hierarchical Interpolation

**What**: A single ValueTracker parameter `t` drives a tree of dependent dots, each computing `(1-t)*A + t*B` between its parent dots. The dependency chain auto-resolves because Manim evaluates updaters in add-order. This is the textbook de Casteljau algorithm expressed directly as Manim updaters.

**When to use**: Bezier curve construction, any recursive subdivision algorithm, interpolation demonstrations, parametric animations where multiple objects depend on the same parameter at different levels of a computation hierarchy.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:68-97
t = ValueTracker(0.001)

# Level 0: static control points (d01, d02, d03, d04)
# Level 1: interpolate between level-0 pairs
d11 = Dot(color=GRAY).add_updater(
    lambda mob: mob.move_to(
        (1 - t.get_value()) * d01.get_center() + t.get_value() * d02.get_center()
    )
)
# Level 2: interpolate between level-1 pairs
d21 = Dot(color=GRAY).add_updater(
    lambda mob: mob.move_to(
        (1 - t.get_value()) * d11.get_center() + t.get_value() * d12.get_center()
    )
)
# Level 3: the point on the curve
d31 = Dot(color=RED).add_updater(
    lambda mob: mob.move_to(
        (1 - t.get_value()) * d21.get_center() + t.get_value() * d22.get_center()
    )
)
```

### Pattern: always_redraw with Lambda Capture for Dynamic Lines

**What**: Wrap `Line` in `always_redraw` inside a list comprehension, using default-argument capture (`lambda a=a, b=b:`) to bind the correct pair of dots to each lambda. Without the capture, all lambdas would reference the last loop iteration's values.

**When to use**: Any situation where you need multiple dynamic lines (or other mobjects) created in a loop, each tracking different pairs of objects — graph edges, tree connections, polygon edges in deformable shapes.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:105-110
dynamic_lines = [
    always_redraw(lambda a=a, b=b: Line(a.get_center(), b.get_center(), color=LIGHT_GRAY))
    for a, b in [
        (d11, d12), (d12, d13), (d21, d22)
    ]
]
```

> Gotcha: Without `a=a, b=b`, all three lambdas would use `a=d21, b=d22` (the last pair). This is Python's late-binding closure behavior. The default-argument trick forces early binding.

### Pattern: TracedPath for Emergent Curves

**What**: Attach a `TracedPath` to a moving dot's center to draw a curve as the dot moves, rather than computing and plotting the curve equation directly. The curve "emerges" from the construction, which is pedagogically powerful.

**When to use**: Bezier curves, Lissajous figures, spirographs, any parametric curve where you want the viewer to see the curve being DRAWN by a moving point rather than appearing all at once. Also useful for showing the trajectory of any dynamic system.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:112-114
self.add(
    TracedPath(lambda: d31.get_center(), stroke_color=RED)
)
# Then animate the parameter:
self.play(t.animate(run_time=5).set_value(0.999))
```

### Pattern: Scaffold Fadeout (Reveal the Result)

**What**: After the construction animation completes, fade out all intermediate construction elements (lines, helper dots) to leave only the final result (anchors + curve). This transitions from "how it's built" to "what it produces."

**When to use**: Any derivation or construction visualization where you want a clean final frame — mathematical proofs that reduce to a result, algorithm visualizations that end with the output, progressive disclosure that strips away scaffolding.

```python
# Source: projects/manim-with-ease/e06_math-and-updaters.py:119-121
self.play(FadeOut(VGroup(
    *dynamic_lines, *static_lines, d02, d03, d11, d12, d13, d21, d22
)))
```

## Scene Flow

1. **Setup** (0-0.5s): All control points, static lines, dynamic lines, and intermediate dots appear. ValueTracker at t=0.001 (near zero). Brief pause.
2. **Construction sweep** (0.5-5.5s): t animates from 0.001 to 0.999. All intermediate dots glide along their segments. The red dot traces the Bezier curve.
3. **Pause** (5.5-6s): Completed curve visible with all construction scaffolding.
4. **Cleanup** (6-7s): All construction elements (dynamic lines, static lines, handle dots, intermediate dots) fade out simultaneously.
5. **Final** (7-8s): Only anchor crosses and the red traced curve remain.

> Full file: `projects/manim-with-ease/e06_math-and-updaters.py` (65 lines, DeCasteljau class starts at line 60)
