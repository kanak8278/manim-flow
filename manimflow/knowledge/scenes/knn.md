---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/knn.py
project: manim-animations
domain: [machine_learning, classification, algorithms]
elements: [scatter_plot, axes, dot, table, dashed_line, surrounding_rect, label]
animations: [write, draw, fade_out, color_change, stagger]
layouts: [split_screen, edge_anchored]
techniques: [data_driven, progressive_disclosure]
purpose: [classification, comparison, step_by_step, demonstration]
mobjects: [Axes, Dot, Table, DashedLine, DashedVMobject, Circle, SurroundingRectangle, Text, MathTex, VGroup]
manim_animations: [Write, Create, FadeIn, FadeOut, Transform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 132
scene_classes: [KNN]
---

## Summary

Visualizes K-nearest neighbors classification with 6 labeled data points (RED and BLUE classes) and a GREEN query point. A scatter plot on the left shows the points, while a distance table on the right lists computed distances to the query. The algorithm is demonstrated for K=1 and K=3: dashed circles expand to enclose the K nearest neighbors, table rows are highlighted with SurroundingRectangles, and the query point changes color to the majority class. Uses DashedVMobject circles for the neighborhood radius.

## Design Decisions

- **Split-screen: plot left, table right**: The scatter plot shows spatial relationships while the table shows exact distances. Having both visible simultaneously lets the viewer verify "the closest point in the plot IS the smallest distance in the table." This dual representation is how KNN is taught in textbooks.
- **GREEN for unclassified query point**: The new point starts GREEN — neutral, belonging to no class. After classification, it changes to the winning class color (RED or BLUE). The color change IS the classification result.
- **DashedVMobject circle for K-neighborhood**: A dashed circle centered on the query shows the decision boundary. For K=1, it encloses 1 point; for K=3, it expands to enclose 3. Dashed rather than solid signals "this is a boundary, not a data element."
- **Sequential distance highlighting**: Before showing K results, each data point gets a DashedLine from the query and a corresponding table row highlight. This teaches the viewer that KNN computes ALL distances first, then selects the K smallest.
- **K=1 to K=3 comparison**: Showing both values demonstrates how K affects the result — the query might be classified differently depending on K. Transform(k_1, k_3) morphs the K label smoothly.
- **Programmatic distance computation**: The `calculate_distance` static method computes actual Euclidean distances, which populate the table. This ensures the visualization is data-consistent — the table values match the visual positions.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "K-nearest neighbors"
  - Axes: `shift(LEFT * 3)`, x_length=5, y_length=5, tips=True
  - Table: `next_to(axes, RIGHT, buff=2)`, scale=0.5
  - K label: `next_to(table, DOWN, buff=0.4)`, font_size=28
- **Axes configuration**: x_range=[-2, 3, 1], y_range=[0, 4, 1]
- **Data points**: 6 points at (-1,3), (2,1), (-2,2), (-1,2), (-1,0), (1,1) with DOT_SIZE=0.1
- **Query point**: (1, 2), GREEN, same radius
- **Neighborhood circles**: DashedVMobject(Circle(radius=sorted_dist + 2*DOT_SIZE)), num_dashes=15

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Class 0 points | RED | Dot radius=0.1 |
| Class 1 points | BLUE | Dot radius=0.1 |
| Query point | GREEN (then RED or BLUE) | Changes on classification |
| Distance lines | YELLOW | DashedLine, buff=0.1 |
| Neighborhood circle | WHITE | DashedVMobject, num_dashes=15 |
| Table headers | WHITE | font_size=32 |
| Table class column | RED/BLUE | Colored per class label |
| SurroundingRectangle | WHITE | Default |
| K label | WHITE | font_size=28 |
| Axes | WHITE | With tips |

Color strategy: RED and BLUE for the two classes — maximally distinguishable. GREEN for the unclassified query (neutral, not yet belonging to either class). YELLOW for measurement lines (temporary). The class column in the table is colored to match dot colors, reinforcing the visual-to-tabular mapping.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| Axes Create | run_time=2 | + 1s wait |
| Dots Create | ~1s | + 1s wait |
| Query dot Create | ~1s | + 2s wait |
| Table Create | run_time=3 | + 2s wait |
| Per-point distance highlight | ~1.75s each | Line 0.25s + rect 0.5s + FadeOut + 1s wait |
| All 6 highlights | ~10.5s | Sequential |
| K=1 demo | ~5s | Circle + rect + color change |
| K=3 demo | ~6s | Transform K, circle + rects + color |
| Total video | ~38 seconds | |

## Patterns

### Pattern: Distance Table with Color-Coded Class Column

**What**: Create a Table from computed distance data. The class column entries are colored to match their class color by accessing table entries and checking the text content. Headers use plain font, data rows use computed distance values formatted to 2 decimal places.
**When to use**: KNN visualization, distance-based classification, any algorithm where you need to show computed distances alongside class labels. Also useful for sorted ranking displays.

```python
# Source: projects/manim-animations/src/knn.py:49-63
headers = ["i", "Distance", "Class"]
table_rows = [
    [str(idx), f"{dist:.2f}", cls]
    for idx, dist, cls in distances
]
table = Table(
    table_rows,
    col_labels=[Text(h, font_size=32) for h in headers],
    include_outer_lines=False
).scale(0.5).next_to(axes, RIGHT, buff=2)

for i in range(2, len(points)+2):
    ent = table.get_entries((i, 3))
    ent.set_color(classes_to_color[ent.lines_text.original_text])
```

### Pattern: DashedVMobject Neighborhood Circle

**What**: Create a dashed circle to show the K-nearest neighborhood boundary. Use `DashedVMobject(Circle(radius=...))` with `num_dashes=15`. The radius is computed from the K-th sorted distance plus a small padding (2*DOT_SIZE). Center the circle on the query point.
**When to use**: KNN neighborhood visualization, radius-based search areas, proximity boundaries, any "within distance r" region display.

```python
# Source: projects/manim-animations/src/knn.py:68-70
sorted_distances = sorted([dist[1] for dist in distances])
circle_k_1 = DashedVMobject(Circle(radius=sorted_distances[0] + 2 * DOT_SIZE, color=WHITE), num_dashes=15).move_to(new_dot)
circle_k_3 = DashedVMobject(Circle(radius=sorted_distances[2] + 2 * DOT_SIZE, color=WHITE), num_dashes=15).move_to(new_dot)
```

### Pattern: Sequential Distance Line Highlighting

**What**: For each data point, draw a DashedLine from the query to the point and simultaneously highlight the corresponding table row with a SurroundingRectangle. Then fade both out. This creates a one-by-one "measuring" effect that teaches the distance computation step.
**When to use**: KNN distance computation, pairwise comparisons, any algorithm where each element is processed individually and the result appears in a table or list.

```python
# Source: projects/manim-animations/src/knn.py:96-103
for i, dot in enumerate(dots):
    line = DashedLine(start=new_dot, end=dot, buff=0.1, color=YELLOW)
    rect = SurroundingRectangle(table.get_rows()[i+1])

    self.play(Create(line), run_time=0.25)
    self.play(Create(rect), run_time=0.5)
    self.play(FadeOut(line, rect))
    self.wait(1)
```

## Scene Flow

1. **Setup** (0-5s): Title writes. Axes create on left. 6 colored data points (RED/BLUE) create. Green query point creates.
2. **Distance table** (5-10s): Table with index, distance, and class columns creates on the right side.
3. **Distance measurement** (10-21s): For each of the 6 points, a YELLOW dashed line draws from query to point while corresponding table row highlights. Both fade out before the next point.
4. **K=1 classification** (21-27s): "K = 1" writes below table. Small dashed circle encloses the nearest point. Table row highlights. Query point changes to the class color of the nearest neighbor.
5. **K=3 classification** (27-35s): K label transforms to "K = 3". Larger dashed circle encloses 3 nearest points. Three table rows highlight. Query point changes to majority class color.

> Full file: `projects/manim-animations/src/knn.py` (132 lines)
