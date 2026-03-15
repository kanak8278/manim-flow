---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/following_graph_camera.py
project: ragibson_manim-videos
domain: [mathematics, trigonometry]
elements: [axes, function_plot, dot]
animations: [zoom_in, zoom_out, camera_follow]
layouts: [centered]
techniques: [moving_camera, add_updater]
purpose: [demonstration, exploration]
mobjects: [Axes, Dot]
manim_animations: [MoveAlongPath, Restore]
scene_type: MovingCameraScene
manim_version: manim_community
complexity: intermediate
lines: 27
scene_classes: [FollowingGraphCamera]
---

## Summary

Demonstrates MovingCameraScene with a camera that tracks a dot moving along a sine curve. The camera saves its initial state, zooms in to 0.5x scale at the dot's starting position, then follows the dot via an updater as it traverses the graph using MoveAlongPath. After the traversal, the camera restores to its original wide view. This is the canonical pattern for camera-following animations in Manim CE.

## Design Decisions

- **save_state() + Restore() pattern**: The camera frame saves its initial state at the start, allowing a clean Restore() at the end. This is cleaner than manually tracking the original position/scale and avoids drift from accumulated transforms.
- **Updater on camera frame, not on the dot**: The camera follows the dot (not the other way around). The updater calls `move_to(moving_dot.get_center())` every frame, keeping the dot centered regardless of the curve's direction.
- **MoveAlongPath for smooth traversal**: Rather than animating x and computing y, MoveAlongPath follows the actual graph geometry. This handles the non-linear relationship between x-position and arc-length automatically, giving uniform visual speed.
- **Start and end dots as reference**: Static dots at t_min and t_max mark the endpoints. When the camera zooms out at the end, these provide context for the full traversal.

## Composition

- **Axes**: x_range=[-1, 10], y_range=[-1, 10]
- **Graph**: sin(x), x_range=[0, 3*PI], color=BLUE
- **Moving dot**: starts at i2gp(graph.t_min, graph), ORANGE
- **Static dots**: at t_min and t_max, default color
- **Camera zoom**: scale(0.5), centered on moving_dot

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Sine graph | BLUE | |
| Moving dot | ORANGE | Follows the curve |
| Endpoint dots | WHITE | Static at start/end |
| Axes | WHITE | Default |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Camera zoom in | default | scale(0.5) + move_to |
| Dot traversal | default | MoveAlongPath, rate_func=linear |
| Camera restore | default | Restore to saved state |
| Total | ~5s | |

## Patterns

### Pattern: Camera-Following Dot Along Graph

**What**: A MovingCameraScene where the camera frame has an updater that continuously moves to a dot's position. The dot traverses a graph via MoveAlongPath. The camera saves state before zooming in, and Restore() returns to the original view afterward. The updater is removed between the traversal and the restore to prevent conflicts.
**When to use**: Following a point along a curve (function exploration, particle on a trajectory), zoomed-in traversal of a long graph, any animation where the viewer needs to see local detail of a path being traced, guided tours along mathematical curves.

```python
# Source: projects/ragibson_manim-videos/manim_examples/following_graph_camera.py:4-26
class FollowingGraphCamera(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        ax = Axes(x_range=[-1, 10], y_range=[-1, 10])
        graph = ax.plot(lambda x: np.sin(x), color=BLUE, x_range=[0, 3 * PI])
        moving_dot = Dot(ax.i2gp(graph.t_min, graph), color=ORANGE)

        self.add(ax, graph, moving_dot)
        self.play(self.camera.frame.animate.scale(0.5).move_to(moving_dot))

        def update_curve(mob):
            mob.move_to(moving_dot.get_center())

        self.camera.frame.add_updater(update_curve)
        self.play(MoveAlongPath(moving_dot, graph, rate_func=linear))
        self.camera.frame.remove_updater(update_curve)

        self.play(Restore(self.camera.frame))
```

**Critical**: Remove the updater BEFORE calling Restore(), otherwise the updater fights the restore animation and the camera won't zoom out properly.

## Scene Flow

1. **Setup** (0-1s): Axes, sine graph, three dots (moving + two static) added instantly.
2. **Zoom in** (1-2s): Camera scales to 0.5x and centers on the orange dot at the graph start.
3. **Traversal** (2-4s): Orange dot moves along the sine curve with the camera following. The viewer sees a zoomed-in view of the local curve as the dot passes through peaks and troughs.
4. **Zoom out** (4-5s): Camera updater removed. Camera restores to original state, revealing the full graph with the dot at the end.

> Full file: `projects/ragibson_manim-videos/manim_examples/following_graph_camera.py` (27 lines)
