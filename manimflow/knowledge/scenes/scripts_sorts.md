---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/sorts.py
project: manim-scripts
domain: [computer_science, algorithms, sorting]
elements: [array, bar_chart, rectangle_node, highlight_rect]
animations: [swap, highlight, color_change, fade_in, grow]
layouts: [horizontal_row, centered]
techniques: [helper_function, color_state_machine, data_driven]
purpose: [step_by_step, demonstration, comparison]
mobjects: [VGroup, Rectangle, Square, Text]
manim_animations: [Create, Swap, FadeIn]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 135
scene_classes: [InsertionSortScene, SelectionSortScene, SelectionSortScene2, BubbleSortBoxes]
---

## Summary

Demonstrates three sorting algorithms (insertion sort, selection sort, bubble sort) using height-proportional rectangular bars. InsertionSort and SelectionSort use shared utility functions (`create_sortable_bars`, `animate_bar_swap`) from `manim_utils.py`, while BubbleSortBoxes builds bars inline using `stretch_to_fit_height`. SelectionSortScene2 adds comparison highlighting with RED/ORANGE color states during the scan phase.

## Design Decisions

- **Height-proportional bars**: Each bar's height equals its data value, giving an immediate visual encoding of magnitude. This is the standard approach for sorting visualizations.
- **Shared utility functions**: `create_sortable_bars` and `animate_bar_swap` are factored out so multiple sorting algorithms reuse the same visual primitives. Reduces code duplication across scenes.
- **Color state for comparison tracking (SelectionSortScene2)**: RED marks the current minimum candidate, ORANGE marks the element being scanned. After each pass, all bars reset to BLUE. This three-state color system makes the scan-and-select logic visible.
- **Manim's built-in Swap (BubbleSortBoxes)**: Uses Manim's `Swap` animation rather than manual position swaps. Simpler code but less control over the arc path.
- **stretch_to_fit_height for variable bar heights**: Instead of creating rectangles with different heights directly, BubbleSortBoxes creates uniform squares then stretches them — an alternative approach.

## Composition

- **Screen regions**:
  - Bars: centered horizontally, shifted down by `config.frame_y_radius * 0.5` (utility function default)
  - BubbleSortBoxes: arranged with `RIGHT, buff=0.2`, centered at ORIGIN
- **Element sizing**: Rectangle(width=0.5, height=value) for utility-based scenes; Square(side_length=1) stretched to height for BubbleSortBoxes
- **Bar spacing**: buff=0.3 (utility default), buff=0.2 (BubbleSortBoxes)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Default bars | BLUE | opacity=0.75 (InsertionSort/SelectionSort), opacity=0.8 (BubbleSortBoxes) |
| Current minimum (SelectionSortScene2) | RED | opacity=0.75 |
| Scanning element (SelectionSortScene2) | ORANGE | opacity=0.75 |
| BubbleSortBoxes fill | BLUE | opacity=0.8 |
| BubbleSortBoxes stroke | WHITE | stroke_width=2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Bar swap (utility) | run_time=0.5 | Default in animate_bar_swap |
| Comparison highlight wait | 0.5s | self.wait(0.5) per comparison |
| Swap (BubbleSortBoxes) | Default (~1s) | Manim Swap default |
| Total video | ~15-30s | Depends on data size and algorithm |

## Patterns

### Pattern: Shared Bar Creation Utility

**What**: A factory function that creates a VGroup of height-proportional rectangles arranged horizontally. Centralizes bar creation so multiple sorting scene classes share the same visual style.
**When to use**: Any sorting visualization, histogram builder, or bar chart where bars represent comparable values and need consistent spacing and sizing.

```python
# Source: projects/manim-scripts/src/manim_utils.py:47-63
def create_sortable_bars(data, bar_width=0.5, bar_buff=0.3, initial_color=None, initial_opacity=None):
    bars = VGroup(*[
        Rectangle(width=bar_width, height=value) for value in data
    ]).arrange(RIGHT, buff=bar_buff)
    if initial_color:
        for bar in bars:
            bar.set_fill(color=initial_color, opacity=initial_opacity if initial_opacity is not None else 1.0)
    bars.shift(DOWN * (config.frame_y_radius * 0.5))
    return bars
```

### Pattern: In-Place Bar Swap with Position Exchange

**What**: Swaps two bars by animating each to the other's position simultaneously, then swaps references in the VGroup list. The VGroup index swap is critical — without it, subsequent comparisons reference wrong elements.
**When to use**: Any sorting algorithm visualization where elements exchange positions. Also useful for reordering sequences, shuffling decks, or any pairwise position exchange.

```python
# Source: projects/manim-scripts/src/manim_utils.py:65-75
def animate_bar_swap(scene, bars, i, j, run_time=0.5):
    scene.play(bars[i].animate.move_to(bars[j].get_center()),
               bars[j].animate.move_to(bars[i].get_center()),
               run_time=run_time)
    bars[i], bars[j] = bars[j], bars[i]  # CRITICAL: update VGroup references
```

### Pattern: Scan Highlight with Color Reset

**What**: During selection sort's inner loop, each scanned element temporarily turns ORANGE, then resets to BLUE after the pass. The current minimum stays RED. After each pass, all unsorted bars reset to BLUE.
**When to use**: Any algorithm with a scan-and-select phase — finding minimum/maximum, linear search, sequential comparison where you want to show "looking at this element now."

```python
# Source: projects/manim-scripts/scenes/sorts.py:77-94
def selection_sort(self, bars):
    n = len(bars)
    for i in range(n - 1):
        min_idx = i
        bars[i].set_fill(color=RED, opacity=0.75)  # Current minimum
        for j in range(i + 1, n):
            bars[j].set_fill(color=ORANGE, opacity=0.75)  # Scanning
            self.wait(0.5)
            if bars[j].get_height() < bars[min_idx].get_height():
                min_idx = j
        if min_idx != i:
            animate_bar_swap(self, bars, i, min_idx)
        bars[i].set_fill(color=BLUE, opacity=0.75)
        for k in range(i + 1, n):
            bars[k].set_fill(color=BLUE, opacity=0.75)
```

## Scene Flow

1. **Setup** (0-2s): Bars appear on screen, arranged horizontally, each height proportional to its data value.
2. **Sorting passes** (2-25s): Algorithm-specific comparisons and swaps. SelectionSortScene2 shows RED/ORANGE highlighting. BubbleSortBoxes uses Manim's Swap animation.
3. **Completion** (25-30s): All bars in sorted order. No explicit "sorted" celebration in these scenes.

> Full file: `projects/manim-scripts/scenes/sorts.py` (135 lines)
