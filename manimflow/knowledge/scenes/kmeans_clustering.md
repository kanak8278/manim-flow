---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/kmeans.py
project: manim-animations
domain: [machine_learning, clustering, statistics, algorithms]
elements: [scatter_plot, axes, dot, label]
animations: [fade_in, color_change, move, write, stagger]
layouts: [centered, edge_anchored]
techniques: [algorithm_class_separation, history_replay, data_driven, color_state_machine]
purpose: [step_by_step, classification, demonstration, progression]
mobjects: [Axes, Dot, Text, VGroup]
manim_animations: [Write, Create, FadeIn, AnimationGroup]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 118
scene_classes: [KMeansAnimation]
---

## Summary

Visualizes K-Means clustering on 30 synthetic data points with 3 clusters. Data points start as gray dots, then iteratively change color (BLUE/GREEN/ORANGE) based on nearest centroid assignment. Red centroid dots smoothly move to cluster centers each iteration. Uses the algorithm+scene separation pattern — KMeans class runs to completion first, then the scene replays the history. Uses sklearn's make_blobs for realistic cluster distribution.

## Design Decisions

- **Algorithm class separate from scene**: Same pattern as linear_regression — the KMeans class runs fully, stores centroid positions per iteration in history list. Scene replays recorded states. Keeps algorithm logic clean and testable.
- **Gray initial state for data points**: All 30 dots start GRAY (unclassified). As the algorithm assigns clusters, dots change to BLUE/GREEN/ORANGE. The color change IS the classification — the viewer sees clusters form in real-time.
- **RED centroids, larger radius (0.10 vs 0.05)**: Centroids are visually distinct from data points — bigger and red. The viewer can always tell "these 3 are the centroids, everything else is data." Red signals "active/important."
- **Individual dot color change (run_time=0.025)**: Each dot's color change is animated separately at 0.025s. This creates a rapid-fire "assigning" effect. Batching all 30 into one self.play() would be cleaner code but loses the visual sense of "the algorithm is processing each point."
- **Centroid movement is one batch animation**: All 3 centroids move simultaneously with run_time=1. This contrasts with the rapid-fire point assignment — first a burst of assignments, then a smooth centroid adjustment. The rhythm teaches the algorithm: assign → update → assign → update.
- **No axes numbers or ticks**: axis_config has include_numbers=False and include_ticks=False. The exact coordinates don't matter for understanding clustering — only the spatial relationships matter. Removing chart junk follows Tufte's principles.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "KMeans Clustering"
  - Axes: centered, x_length=6, y_length=6
  - Data points: positioned via `axes.coords_to_point(x, y)`, 30 dots
  - Centroids: same positioning, larger radius
- **Axes configuration**: x_range=[-15, 15, 5], y_range=[-15, 15, 5], x_length=6, y_length=6. No numbers, no ticks — clean scatter plot.
- **Data generation**: `make_blobs(n_samples=30, centers=3, cluster_std=1.5, random_state=42)` — 3 well-separated clusters with moderate spread.
- **Point sizing**: Data dots radius=0.05 (small), centroid dots radius=0.10 (2x larger).

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Data points (initial) | GRAY | radius=0.05, unclassified state |
| Cluster 0 points | BLUE | After assignment |
| Cluster 1 points | GREEN | After assignment |
| Cluster 2 points | ORANGE | After assignment |
| Centroids | RED | radius=0.10, always visible |
| Title text | WHITE | Default |
| Axes | WHITE | No numbers, no ticks |

Color strategy: Three maximally distinguishable colors (BLUE/GREEN/ORANGE) for clusters. These are well-separated in color space — a colorblind-friendly choice (blue vs green vs orange has good luminance contrast). RED reserved exclusively for centroids so they never blend with cluster colors.

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Title + Axes | run_time=2 | Write + Create simultaneous |
| Data points FadeIn | Default (~1s) | All 30 at once |
| Centroids FadeIn | Default (~1s) | All 3 at once |
| Per-point color change | run_time=0.025 | 30 points × 0.025s = 0.75s per iteration |
| Centroid movement | run_time=1 | All 3 move simultaneously |
| Wait between iterations | 1s | Pause to observe clusters |
| Total per iteration | ~2.75s | Color burst + wait + centroid move |
| Total video | ~20 seconds | ~5-6 iterations to convergence |

## Patterns

### Pattern: Iterative Algorithm Replay

**What**: Run algorithm to completion, store state history, then replay each state as animation. Each iteration has two phases: (1) rapid-fire point assignments via color change, (2) smooth centroid movement. The two-phase rhythm matches the actual algorithm structure (E-step → M-step in EM terms).
**When to use**: K-means, EM algorithm, any iterative optimization with assign-then-update structure. Also works for gradient descent, simulated annealing, or any algorithm where you want to show "before state → computation → after state" per iteration.

```python
# Source: projects/manim-animations/src/kmeans.py:100-116
for iteration, centroids in enumerate(history[1:], start=1):
    distances = kmeans.compute_distances(X, centroids)
    labels = kmeans.assign_clusters(distances)

    # Phase 1: Rapid-fire point color assignment
    for i, dot in enumerate(points_group):
        color = [BLUE, GREEN, ORANGE][labels[i]]
        self.play(dot.animate.set_color(color), run_time=0.025)

    self.wait(1)

    # Phase 2: Smooth centroid movement
    self.play(
        *[
            centroid.animate.move_to(axes.coords_to_point(x, y))
            for centroid, (x, y) in zip(centroid_dots, centroids)
        ],
        run_time=1
    )
```

### Pattern: Scatter Plot with Axes (No Chart Junk)

**What**: Clean scatter plot using Axes with all decorations removed (no numbers, no ticks). Data points as small Dots positioned via coords_to_point(). The axes provide spatial reference without visual noise.
**When to use**: Any 2D data visualization where exact values don't matter — clustering, classification boundaries, dimensionality reduction results, spatial distributions. Follow Tufte: maximize data-ink ratio.

```python
# Source: projects/manim-animations/src/kmeans.py:67-80
axes = Axes(
    x_range=[-15, 15, 5],
    y_range=[-15, 15, 5],
    x_length=6,
    y_length=6,
    axis_config={"include_numbers": False, "include_ticks": False},
)

points_group = VGroup(
    *[
        Dot(axes.coords_to_point(x, y), color=GRAY, radius=0.05)
        for x, y in X
    ]
)
```

### Pattern: Color-Based Classification State

**What**: Use dot color to represent cluster/class membership. Points start in a neutral color (GRAY = unclassified) and change to a cluster color when assigned. Each cluster gets a maximally distinguishable color. The color change itself IS the animation — no labels or annotations needed.
**When to use**: Clustering results, classification visualization, any assignment where each item belongs to one of N categories. Also works for state machines, graph coloring, or region labeling.

```python
# Source: projects/manim-animations/src/kmeans.py:104-107
# Color map: cluster index → color
for i, dot in enumerate(points_group):
    color = [BLUE, GREEN, ORANGE][labels[i]]
    self.play(dot.animate.set_color(color), run_time=0.025)
```

### Pattern: Simultaneous Multi-Object Movement

**What**: Move multiple objects at once by unpacking a list comprehension into self.play(). All centroids move simultaneously to their new positions. Uses `centroid.animate.move_to()` which creates a smooth interpolation.
**When to use**: When multiple objects need to reposition simultaneously — centroids updating, nodes rearranging, elements sliding into new layout positions.

```python
# Source: projects/manim-animations/src/kmeans.py:110-116
self.play(
    *[
        centroid.animate.move_to(axes.coords_to_point(x, y))
        for centroid, (x, y) in zip(centroid_dots, centroids)
    ],
    run_time=1
)
```

## Scene Flow

1. **Setup** (0-4s): Title "KMeans Clustering" writes at top while axes create simultaneously (run_time=2). Wait 1s. 30 gray data dots fade in. Wait 1s. 3 red centroid dots fade in at random initial positions. Wait 1s.
2. **Iteration 1** (4-7s): Each of the 30 gray dots rapidly changes to BLUE, GREEN, or ORANGE based on nearest centroid (0.025s each = 0.75s total). Wait 1s. All 3 centroids smoothly move to the mean of their assigned points (run_time=1).
3. **Iterations 2-5** (7-18s): Same pattern repeats. Each iteration: rapid color reassignment (some dots change color between clusters), pause, centroid adjustment. Centroid movements get smaller as algorithm converges.
4. **Convergence** (18-20s): Final iteration — no dots change color (centroids barely move). Wait 2s to let viewer observe the final stable clustering.

> Full file: `projects/manim-animations/src/kmeans.py` (118 lines)
