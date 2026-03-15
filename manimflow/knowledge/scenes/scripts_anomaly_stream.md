---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/manim-scripts/anomaly_detection_script.py
project: manim-scripts
domain: [machine_learning, statistics]
elements: [dot, surrounding_rect, label]
animations: [draw, fade_in, shift, flash, lagged_start, replacement_transform]
layouts: [horizontal_row, centered]
techniques: [data_driven, color_state_machine]
purpose: [simulation, demonstration, classification]
mobjects: [Dot, Text, SurroundingRectangle, VGroup]
manim_animations: [Create, Write, ReplacementTransform, Flash, LaggedStart]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 89
scene_classes: [AnomalyScene]
---

## Summary

Visualizes anomaly detection as a data stream. First, 20 normal green dots stream across the screen left-to-right. Then a mixed stream with 3 randomly placed red anomaly dots (larger radius) flows across. After the stream passes, anomalies are detected via color check and highlighted with Flash animations and yellow SurroundingRectangles. The streaming metaphor makes the temporal nature of anomaly detection intuitive.

## Design Decisions

- **Streaming motion (shift RIGHT*14)**: Data points move as a group from left to right with `rate_func=linear`, simulating a real-time data stream. The linear rate function prevents easing — data arrives at constant speed.
- **Size differentiation for anomalies**: Anomalies have radius=0.2 vs normal radius=0.1. Even before color detection, the size difference provides a visual hint.
- **Post-stream detection**: Highlighting happens AFTER the stream passes, simulating batch detection on accumulated data. This matches how many real anomaly detection systems work.
- **Color-based anomaly identification**: Detection loop checks `point.get_color() == anomaly_color`. This is a simplified but effective way to identify which dots are anomalies without maintaining a separate data structure.

## Composition

- **Data stream**: 20 dots at x=-7 to x=7, y=0, spaced 0.7 units apart
- **Stream shift**: RIGHT*14 (full screen width)
- **Flash highlight**: line_length=0.3, num_lines=12, flash_radius=0.3
- **SurroundingRectangle**: buff=0.1, color=YELLOW

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Normal points | GREEN | radius=0.1 |
| Anomaly points | RED | radius=0.2 |
| Detection highlight | YELLOW | Flash + SurroundingRectangle |
| Labels | WHITE | font_size=30 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Normal stream | run_time=5 | rate_func=linear |
| Mixed stream | run_time=5 | rate_func=linear |
| Flash highlights | run_time=1.5 | LaggedStart, lag_ratio=0.2 |
| Label transitions | Default | ReplacementTransform |
| End wait | 2s | Final state |
| Total | ~18s | Two streams + detection |

## Patterns

### Pattern: Data Stream Animation

**What**: Create a row of dots, animate the entire group shifting across the screen with `rate_func=linear`. After the stream passes, remove the group. This simulates real-time data arrival.
**When to use**: Time-series visualization, network packet flow, sensor data streams, any scenario where data arrives sequentially over time.

```python
# Source: projects/manim-scripts/manim-scripts/anomaly_detection_script.py:22-32
normal_points_group = VGroup()
for i in range(n_normal_points):
    point = Dot(radius=0.1, color=normal_color)
    point.move_to(np.array([-7 + 0.7 * i, 0, 0]))
    normal_points_group.add(point)
self.play(LaggedStart(*[Create(p) for p in normal_points_group], lag_ratio=0.1))
self.play(normal_points_group.animate.shift(RIGHT * 14), run_time=animation_run_time, rate_func=linear)
self.remove(*normal_points_group)
```

### Pattern: Post-Hoc Anomaly Flash Detection

**What**: After data points are displayed, iterate through them checking a property (color). Anomalies get Flash + SurroundingRectangle simultaneously via LaggedStart. The flash provides a dramatic "detection" moment.
**When to use**: Anomaly detection results, test pass/fail highlighting, any batch classification result display where flagged items need visual emphasis.

```python
# Source: projects/manim-scripts/manim-scripts/anomaly_detection_script.py:72-83
for point in data_points_mixed:
    if point.get_color() == anomaly_color:
        flash_animations.append(Flash(point, color=YELLOW, line_length=0.3,
            num_lines=12, flash_radius=0.3, time_width=0.3, run_time=1.5))
        box = SurroundingRectangle(point, color=detection_color, buff=0.1)
        box_animations.append(Create(box))
self.play(LaggedStart(*flash_animations, lag_ratio=0.2),
          LaggedStart(*box_animations, lag_ratio=0.2))
```

## Scene Flow

1. **Normal stream** (0-8s): Title writes. "Normal Data Stream" label. 20 green dots create and stream right. Removed after passing.
2. **Mixed stream** (8-16s): "Introducing Anomalies..." label. 20 dots (17 green, 3 red) create and stream right.
3. **Detection** (16-20s): "Highlighting Anomalies" label. Flash + rectangle on each anomaly via LaggedStart.
4. **End** (20-22s): Wait 2s on final state.

> Full file: `projects/manim-scripts/manim-scripts/anomaly_detection_script.py` (89 lines)
