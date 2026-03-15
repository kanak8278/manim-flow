---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/manim-scripts/classification_script.py
project: manim-scripts
domain: [machine_learning, classification]
elements: [circle_node, box, rectangle_node, label, grid]
animations: [draw, fade_in, write, move, lagged_start, replacement_transform]
layouts: [horizontal_row, grid, centered]
techniques: [data_driven, color_state_machine]
purpose: [classification, demonstration, step_by_step]
mobjects: [Circle, Square, Triangle, Rectangle, Text, VGroup]
manim_animations: [Create, Write, LaggedStart, ReplacementTransform]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 119
scene_classes: [ClassificationScene]
---

## Summary

Visualizes classification by sorting shape-based items into labeled bins. Creates 12 items (4 each of circles, squares, triangles) in random positions, then animates each moving to the correct category bin. Items are classified by their Python type (isinstance check), making the classification rule concrete and visual. Bins are labeled rectangles arranged horizontally at the bottom.

## Design Decisions

- **Shape-as-class metaphor**: Using different Manim shape types (Circle, Square, Triangle) with distinct colors (BLUE, GREEN, YELLOW) makes classification tangible. The "rule" is the shape type — no abstract decision boundary needed.
- **Random initial positioning**: Items start randomly clustered in the center, then sort into bins. The visual transition from disorder to order is the core message.
- **Grid positioning within bins**: Items are placed in a grid layout inside each bin using row/col calculations. This prevents overlap and shows that each bin can hold multiple items.
- **isinstance for classification**: The classification "model" is just `isinstance(item, Circle)`. This makes the code self-documenting — the classification rule IS the shape type.

## Composition

- **Unsorted area**: ORIGIN + DOWN*0.5, items randomly within [-1,1] x [-0.5,0.5]
- **Bin dimensions**: width=3, height=2, spacing=0.5 between bins
- **Bin positions**: Centered horizontally, y=-2.5
- **Items**: scale=0.5 per shape
- **Grid within bins**: items_per_row based on bin_width / (item_scale * 2 + padding)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Circles (Category A) | BLUE | scale=0.5 |
| Squares (Category B) | GREEN | scale=0.5 |
| Triangles (Category C) | YELLOW | scale=0.5 |
| Bin borders | WHITE | Rectangle |
| Bin labels | WHITE | font_size=20 |
| Status labels | WHITE | font_size=24 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Item creation | lag_ratio=0.1 | LaggedStart Create |
| Bin creation | Default | Create + Write |
| Item sorting | lag_ratio=0.1 | LaggedStart animate.move_to |
| Label transitions | Default | ReplacementTransform |
| End wait | 3s | Final state |
| Total | ~15s | Setup + sorting |

## Patterns

### Pattern: Shape-Based Classification into Bins

**What**: Create items of different shape types, then animate each moving to its corresponding labeled bin. Classification is done by checking the Manim shape type (isinstance). Grid positioning within bins prevents overlap.
**When to use**: Classification demonstrations, sorting/categorization visualizations, any scenario where items need to move from an unsorted collection into labeled categories.

```python
# Source: projects/manim-scripts/manim-scripts/classification_script.py:83-113
classified_items_for_bins = {key: [] for key in category_keys}
for item in unsorted_items_group:
    if isinstance(item, Circle):
        classified_items_for_bins["Category A (Circles)"].append(item)
    elif isinstance(item, Square):
        classified_items_for_bins["Category B (Squares)"].append(item)
    elif isinstance(item, Triangle):
        classified_items_for_bins["Category C (Triangles)"].append(item)

for cat_key, items_in_cat in classified_items_for_bins.items():
    bin_c = categories[cat_key]["bin_center"]
    for i, item_to_move in enumerate(items_in_cat):
        row = i // items_per_row_in_bin
        col = i % items_per_row_in_bin
        x_offset = (col - (items_per_row_in_bin - 1) / 2.0) * (item_scale * 2 + item_padding)
        y_offset = (bin_height / 2.0 - item_scale - item_padding / 2.0) - (row * (item_scale * 2 + item_padding))
        target_pos = bin_c + np.array([x_offset, y_offset, 0])
        animations.append(item_to_move.animate.move_to(target_pos))
self.play(LaggedStart(*animations, lag_ratio=0.1))
```

## Scene Flow

1. **Setup** (0-4s): Title "Classification Demonstration" writes. "Unsorted Items" label. 12 randomly positioned items create with LaggedStart.
2. **Bins appear** (4-6s): Three labeled bins create at bottom.
3. **Classification** (6-12s): "Categorizing Items..." label. All items animate to their bins in a LaggedStart wave.
4. **End** (12-15s): "Items Categorized" label. Wait 3s.

> Full file: `projects/manim-scripts/manim-scripts/classification_script.py` (119 lines)
