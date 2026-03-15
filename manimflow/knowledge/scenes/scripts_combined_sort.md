---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/combined_sort_visualization.py
project: manim-scripts
domain: [computer_science, algorithms, sorting]
elements: [array, bar_chart, label, highlight_rect]
animations: [swap, highlight, color_change, fade_in, write]
layouts: [split_screen, horizontal_row, edge_anchored]
techniques: [color_state_machine, helper_function, data_driven]
purpose: [comparison, step_by_step, demonstration]
mobjects: [VGroup, Rectangle, Text]
manim_animations: [Write, FadeIn, Create]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 143
scene_classes: [CombinedSortScene]
---

## Summary

Side-by-side comparison of bubble sort and insertion sort on the same 8-element dataset. Uses split-screen layout with algorithm-specific color palettes: blue/yellow/orange for bubble sort, green/yellow/purple for insertion sort. Each algorithm runs sequentially with comparison highlighting, swap animations, and sorted-element marking. Class constants define the full color scheme for easy palette swaps.

## Design Decisions

- **Split-screen layout**: Bubble sort on the left, insertion sort on the right. Direct visual comparison is the entire point — the viewer can see how the same data gets sorted differently.
- **Class-level color constants**: `BUBBLE_SORT_COLOR`, `INSERTION_SORT_HIGHLIGHT_COMPARE`, etc. are class attributes. This makes the color scheme declarative, easy to modify, and self-documenting.
- **Three-state color system per algorithm**: Each algorithm has default, highlight, and sorted colors. Bubble: BLUE_D → YELLOW_C (comparing) → ORANGE_C (sorted). Insertion: GREEN_D → YELLOW_C (key) / RED_C (comparing) → PURPLE_C (sorted).
- **Sequential not simultaneous**: Bubble sort runs first, then insertion sort. Running them simultaneously would be more impressive but much harder to follow. Sequential lets the viewer focus on one algorithm at a time.
- **Sorted color sweep at end**: After each algorithm finishes, any bar not already in the sorted color gets swept to sorted color. This handles edge cases (early termination, already-sorted bars).

## Composition

- **Screen regions**:
  - Scene title: to_edge(UP), font_size=40
  - Bubble sort title: next_to(scene_title, DOWN, buff=0.5), to_edge(LEFT, buff=0.7), font_size=32
  - Insertion sort title: align_to(bubble_title, UP), to_edge(RIGHT, buff=0.7), font_size=32
  - Bars: scale=0.75, next_to(title, DOWN, buff=0.3)
  - Status text: next_to(bars, DOWN, buff=0.3), font_size=24
- **Data**: [7, 2, 8, 1, 4, 5, 9, 3] — fixed for consistent testing

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Bubble sort default | BLUE_D | opacity=0.8 |
| Bubble sort comparing | YELLOW_C | opacity=1 |
| Bubble sort sorted | ORANGE_C | opacity=0.8 |
| Insertion sort default | GREEN_D | opacity=0.8 |
| Insertion sort key | YELLOW_C | opacity=1 |
| Insertion sort comparing | RED_C | opacity=1 |
| Insertion sort sorted | PURPLE_C | opacity=0.8 |
| Status text | WHITE | font_size=24 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Comparison highlight | run_time=0.2 | Per bar pair |
| Bar swap | run_time=0.4 | Via animate_bar_swap |
| Unhighlight | run_time=0.2 | Reset to default color |
| Mark sorted | run_time=0.1 | After each pass |
| Final sorted sweep | run_time=0.3 | All remaining bars |
| Wait between algorithms | 0.5s | After bubble sort completes |
| End wait | 3s | Final state |
| Total video | ~60-90s | Depends on swaps needed |

## Patterns

### Pattern: Class-Level Color Palette Constants

**What**: Define all algorithm-specific colors as class attributes. Each algorithm gets its own namespace of colors (default, highlight, sorted). This makes the color scheme readable, modifiable, and prevents magic color values scattered through the code.
**When to use**: Any side-by-side algorithm comparison, multi-category visualization, or any scene with more than 3 distinct color-coded states. Also useful when the same scene class might be themed differently.

```python
# Source: projects/manim-scripts/scenes/combined_sort_visualization.py:12-19
class CombinedSortScene(Scene):
    BUBBLE_SORT_COLOR = BLUE_D
    BUBBLE_SORT_HIGHLIGHT_COMPARE = YELLOW_C
    BUBBLE_SORT_SORTED_COLOR = ORANGE_C

    INSERTION_SORT_COLOR = GREEN_D
    INSERTION_SORT_HIGHLIGHT_KEY = YELLOW_C
    INSERTION_SORT_HIGHLIGHT_COMPARE = RED_C
    INSERTION_SORT_SORTED_COLOR = PURPLE_C
```

### Pattern: Insertion Sort with Key Element Tracking

**What**: The current element being inserted is highlighted as KEY (YELLOW_C). As it shifts left through the sorted portion, each compared element briefly turns RED_C. After each swap, the displaced element turns PURPLE_C (sorted) and the key element retains its yellow highlight. This four-state color machine (default → key → comparing → sorted) makes the insertion process visible.
**When to use**: Insertion sort visualization, or any algorithm where a single element "bubbles" through an ordered portion — priority queue insertion, sorted linked list insertion.

```python
# Source: projects/manim-scripts/scenes/combined_sort_visualization.py:103-129
def insertion_sort_animation(self, bars):
    n = len(bars)
    self.play(bars[0].animate.set_fill(self.INSERTION_SORT_SORTED_COLOR, opacity=0.8), run_time=0.1)
    for i in range(1, n):
        self.play(bars[i].animate.set_fill(self.INSERTION_SORT_HIGHLIGHT_KEY, opacity=1), run_time=0.2)
        j = i
        while j > 0 and bars[j].height < bars[j-1].height:
            self.play(bars[j-1].animate.set_fill(self.INSERTION_SORT_HIGHLIGHT_COMPARE, opacity=1), run_time=0.2)
            animate_bar_swap(self, bars, j-1, j, run_time=0.4)
            self.play(bars[j].animate.set_fill(self.INSERTION_SORT_SORTED_COLOR, opacity=0.8), run_time=0.2)
            self.play(bars[j-1].animate.set_fill(self.INSERTION_SORT_HIGHLIGHT_KEY, opacity=1), run_time=0.1)
            j -= 1
        self.play(bars[j].animate.set_fill(self.INSERTION_SORT_SORTED_COLOR, opacity=0.8), run_time=0.2)
```

## Scene Flow

1. **Setup** (0-5s): Title "Comparing Sorting Algorithms" writes. Bubble sort bars and title on left. Insertion sort bars and title on right. Empty status text below each.
2. **Bubble Sort** (5-35s): Status shows "Sorting...". Bars highlighted YELLOW_C during comparison, swapped with run_time=0.4, sorted bars turn ORANGE_C. After final pass, status becomes "Sorted!" in ORANGE_C.
3. **Insertion Sort** (35-65s): Status shows "Sorting...". Key element in YELLOW_C shifts left through sorted portion. Compared elements flash RED_C. Sorted elements accumulate in PURPLE_C. Status becomes "Sorted!" in PURPLE_C.
4. **End** (65-68s): Both arrays sorted, both statuses colored. Wait 3s.

> Full file: `projects/manim-scripts/scenes/combined_sort_visualization.py` (143 lines)
