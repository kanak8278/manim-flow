---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/normalization.py
project: manim-animations
domain: [statistics, machine_learning]
elements: [axes, scatter_plot, dot]
animations: [grow_from_center, move, stagger]
layouts: [centered]
techniques: [data_driven]
purpose: [transformation, before_after, step_by_step]
mobjects: [Axes, Dot, VGroup]
manim_animations: [AnimationGroup, GrowFromCenter]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 62
scene_classes: [Normalization]
---

## Summary

Visualizes data centering and normalization as a two-step transformation of 15 2D data points. Points start at their original positions (normal distribution with means 5 and 10), then animate to centered positions (subtract mean), then to normalized positions (divide by std). Each transition uses staggered AnimationGroup with `lag_ratio=0.1` so the viewer sees the dots "ripple" to their new locations. The axes remain static while dots move, showing the data shifting toward the origin and then compressing.

## Design Decisions

- **Two-step transformation (center then normalize)**: Instead of jumping directly to normalized, the scene shows the intermediate centered state. This matches how normalization is taught: first subtract mean, then divide by standard deviation. Each step is a separate concept.
- **Staggered dot movement (lag_ratio=0.1)**: Dots don't all move at once — they ripple with 0.1s delay between each. This makes the transformation visible as a process rather than an instantaneous change. The viewer can track individual dots.
- **Static axes with no labels**: The axes stay fixed while data moves. This provides a spatial reference frame so the viewer can see the centering (shift toward origin) and normalization (compression toward origin). No numbers or ticks keep focus on the relative positions.
- **Pre-computed target positions**: Centered and normalized dot positions are computed upfront as separate VGroups. The animation moves existing dots to new VGroup positions using `dot.animate.move_to(new_dot.get_center())`. This is simpler than ValueTracker for discrete transformations.
- **Axes added without animation**: `self.add(axes)` places axes immediately without Create animation. The focus is entirely on the data transformation, not the axes setup.

## Composition

- **Screen regions**:
  - Axes: centered, x_length=10, y_length=7
  - Data points: positioned via `axes.c2p(x, y)`, 15 dots
- **Axes configuration**: x_range=[-10, max+2, 1], y_range=[-10, max+2, 1], no numbers, no ticks, with tips
- **Data generation**: np.random.normal, means=[5.0, 10.0], stds=[2.0, 3.0], 15 samples
- **Transformations**: centered_data = data - mean, normalized_data = centered / std

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| All data points | BLUE | Dot, default radius |
| Axes | WHITE | include_tip=True, no numbers, no ticks |
| Axis labels | WHITE | "x" and "y" |

Color strategy: All points are the same BLUE color. The transformation is communicated purely through position changes, not color. This keeps the visual clean and focuses attention on spatial movement.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Axes added (no animation) | instant | self.add() + 2s wait |
| Points GrowFromCenter | ~2s | AnimationGroup, lag_ratio=0.1, + 1s wait |
| Center transformation | ~2s | AnimationGroup, lag_ratio=0.1, + 1s wait |
| Normalize transformation | ~2s | AnimationGroup, lag_ratio=0.1, + 1s wait |
| Total video | ~10 seconds | |

## Patterns

### Pattern: Staggered Dot Position Transform

**What**: Compute target positions as a separate VGroup of Dots. Then animate existing dots to the target positions using `dot.animate.move_to(new_dot.get_center())` inside an AnimationGroup with lag_ratio. The dots ripple to their new positions one by one.
**When to use**: Data normalization, standardization, centering, any point cloud transformation where individual dots should visually travel to new positions. Also works for sorting, clustering reassignment, or layout changes.

```python
# Source: projects/manim-animations/src/normalization.py:33-52
centered_dots = VGroup(*[
    Dot(axes.c2p(x, y), color=BLUE) for x, y in centered_data
])

# Animate dots moving to centered positions
self.play(
    AnimationGroup(
        *[dot.animate.move_to(new_dot.get_center()) for dot, new_dot in zip(dots, centered_dots)],
        lag_ratio=0.1
    )
)

# Then to normalized positions
normalized_dots = VGroup(*[
    Dot(axes.c2p(x, y), color=BLUE) for x, y in normalized_data
])

self.play(
    AnimationGroup(
        *[dot.animate.move_to(new_dot.get_center()) for dot, new_dot in zip(dots, normalized_dots)],
        lag_ratio=0.1
    )
)
```

## Scene Flow

1. **Setup** (0-2s): Axes appear instantly (self.add). 2s pause.
2. **Original data** (2-5s): 15 blue dots grow from center with staggered timing. Points cluster around (5, 10) in the upper right quadrant.
3. **Centering** (5-8s): All dots animate to centered positions (subtract mean). The cluster shifts to near the origin. Staggered ripple effect.
4. **Normalization** (8-11s): All dots animate to normalized positions (divide by std). The cluster compresses tighter around the origin. Staggered ripple effect.

> Full file: `projects/manim-animations/src/normalization.py` (62 lines)
