---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/log_transform.py
project: manim-animations
domain: [statistics, mathematics, calculus]
elements: [axes, histogram, arrow, equation, label]
animations: [write, draw, grow_arrow, transform]
layouts: [split_screen, edge_anchored]
techniques: [data_driven, before_after_comparison]
purpose: [transformation, before_after, demonstration]
mobjects: [Axes, Rectangle, Arrow, MathTex, Text, VGroup]
manim_animations: [Write, Create, GrowArrow, Transform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 107
scene_classes: [LogTransform]
---

## Summary

Visualizes log transformation of exponential data by showing a histogram morphing from a right-skewed distribution (BLUE bars) to a more symmetric shape (GREEN bars). The original exponential PDF and its log-transformed form are shown as equations on the right with an arrow connecting them. The histogram, axes, and labels all Transform simultaneously from original to log-transformed versions, creating a smooth before-after transition. Uses numpy for data generation and histogram computation.

## Design Decisions

- **Data-driven histograms from numpy**: 1000 random exponential samples generate the histogram via `np.histogram(bins=30, density=True)`. This produces realistic, noisy distributions rather than idealized curves. The viewer sees actual data behavior.
- **Manual Rectangle construction for histogram bars**: Instead of Manim's BarChart, rectangles are positioned individually using `axes.c2p()` for coordinate conversion. This gives exact control over sizing and allows the Transform between original and log-transformed histograms.
- **BLUE for original, GREEN for transformed**: The color change during the Transform reinforces "something changed." BLUE = raw data, GREEN = processed/improved data. The viewer sees both the shape change and the color change.
- **Equation + arrow annotation on the right**: The mathematical transformation is shown alongside the visual one. The arrow with "Applying log" text makes the operation explicit. This connects the algebraic operation to the visual effect.
- **Simultaneous triple Transform**: Axes, labels, and rectangles all transform at once (run_time=3). This shows that the log transform affects the entire distribution — scale, shape, and axis labels all change together.
- **No tips on axes**: `tips=False` for both axes sets. The focus is on the data distribution, not the axis structure. Numbers are included (include_numbers=True) because the scale change is important to see.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Log Transformation"
  - Axes: `to_edge(LEFT)`, x_length=8, y_length=4
  - Original equation: `RIGHT * 3 + UP * 2`
  - Log equation: `next_to(original_eq, DOWN, buff=2)`
  - Arrow: between equation tops/bottoms, buff=0.3, stroke_width=4
  - Arrow text: `next_to(arrow, RIGHT, buff=0.3)`
- **Original axes**: x_range=[0, max(data)+1, 10], y_range=[0, max(hist)+0.1, 0.1], font_size=20
- **Log axes**: x_range=[0, max(log_data)+1, 1], y_range=[0, max(log_hist)+0.1, 0.1], font_size=20
- **Histogram bars**: 30 bins, fill_opacity=0.6, widths computed via c2p coordinate conversion

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Original histogram | BLUE | Rectangle, fill_opacity=0.6 |
| Log histogram | GREEN | Rectangle, fill_opacity=0.6 |
| Axes | WHITE | tips=False, include_numbers=True, font_size=20 |
| Original equation | WHITE | font_size=32 |
| Log equation | WHITE | font_size=32 |
| Arrow | WHITE | stroke_width=4 |
| Arrow text | WHITE | font_size=32, "Applying log" |
| Axis labels | WHITE | font_size=24 |

Color strategy: BLUE = raw/original data, GREEN = transformed/improved data. The color shift during Transform provides an additional visual cue that the data has been processed.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 2s wait |
| Axes + labels Create/Write | run_time=2 | |
| Histogram bars Create | run_time=2 | + 2s wait |
| Original equation Write | ~1s | + default wait |
| Arrow GrowArrow + text | ~1s | + default wait |
| Log equation Write | ~1s | + default wait |
| Triple Transform | run_time=3 | Axes + labels + rectangles |
| Final hold | 2s | |
| Total video | ~18 seconds | |

## Patterns

### Pattern: Data-Driven Histogram with Manual Rectangles

**What**: Generate histogram data with `np.histogram(bins=30, density=True)`, then construct individual Rectangle mobjects for each bin. Width and height are computed via `axes.c2p()` coordinate conversion. Each rectangle is positioned with `move_to(center, aligned_edge=DOWN)` so bars sit on the x-axis.
**When to use**: Any histogram or bar chart where you need per-bar control — coloring individual bars, animating bar-by-bar, or transforming between two different distributions. Manim's built-in BarChart is less flexible for these cases.

```python
# Source: projects/manim-animations/src/log_transform.py:48-61
original_rectangles = VGroup()
for height, left_edge, right_edge in zip(
    og_hist, og_bin_edges[:-1], og_bin_edges[1:]
):
    rect = Rectangle(
        width=original_axes.c2p(right_edge, 0)[0]
        - original_axes.c2p(left_edge, 0)[0],
        height=original_axes.c2p(0, height)[1] - original_axes.c2p(0, 0)[1],
        color=BLUE,
        fill_opacity=0.6,
    ).move_to(
        original_axes.c2p((left_edge + right_edge) / 2, 0), aligned_edge=DOWN
    )
    original_rectangles.add(rect)
```

### Pattern: Simultaneous Axes + Data Transform

**What**: Transform the original axes, axis labels, and histogram rectangles simultaneously into their log-transformed counterparts. All three transforms play in one `self.play()` call with run_time=3. This creates a smooth morphing effect where the entire chart changes at once.
**When to use**: Before-after comparison of the same data under different transformations — log transform, normalization, standardization, any data preprocessing step. Also works for switching between coordinate systems.

```python
# Source: projects/manim-animations/src/log_transform.py:101-106
self.play(
    Transform(original_axes, log_axes),
    Transform(original_labels, log_labels),
    Transform(original_rectangles, log_rectangles),
    run_time=3,
)
```

## Scene Flow

1. **Setup** (0-3s): Title "Log Transformation" writes.
2. **Original distribution** (3-9s): Axes create on the left with x/density labels. 30 BLUE histogram bars create, showing a right-skewed exponential distribution.
3. **Math annotation** (9-14s): Exponential PDF equation writes on the right. Arrow with "Applying log" label grows. Log-transformed equation writes below.
4. **Transformation** (14-19s): Axes, labels, and histogram all Transform simultaneously (3s). Bars morph from BLUE skewed shape to GREEN symmetric shape. Axes rescale. x-label changes from "x" to "log(x+1)".

> Full file: `projects/manim-animations/src/log_transform.py` (107 lines)
