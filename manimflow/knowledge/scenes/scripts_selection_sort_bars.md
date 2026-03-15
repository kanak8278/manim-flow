---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/sort2.py
project: manim-scripts
domain: [computer_science, algorithms, sorting]
elements: [array, rectangle_node]
animations: [highlight, color_change, swap]
layouts: [horizontal_row, centered]
techniques: [color_state_machine, helper_function]
purpose: [step_by_step, demonstration]
mobjects: [VGroup, Rectangle]
manim_animations: [Create]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 50
scene_classes: [SelectionSortAnimation]
---

## Summary

A minimal selection sort visualization using height-proportional bars created inline (no utility import). The scan phase highlights the current element in YELLOW, unhighlights to WHITE after checking. Swaps are done by exchanging widths rather than positions — an unusual approach. Sorted elements turn GREEN after each pass.

## Design Decisions

- **Width-swap instead of position-swap**: `swap_bars` animates `set_width` on both bars rather than exchanging positions. This is technically incorrect for a visual sort — it changes bar widths rather than moving bars. Included here as a cautionary example of what NOT to do when the visual metaphor breaks.
- **YELLOW scan highlight**: Each scanned element briefly turns YELLOW (0.2s), then reverts to WHITE (0.1s). Fast enough to show scanning without slowing the video.
- **GREEN for sorted**: After each outer loop pass, all bars up to the current index turn GREEN simultaneously.
- **Self-contained bar creation**: `create_bars` builds VGroup of Rectangles inline, arranged with buff=0.2, shifted DOWN. No utility dependency.

## Composition

- **Bar sizing**: Rectangle(width=0.5, height=value) — height equals data value
- **Bar arrangement**: arrange(buff=0.2), shift(DOWN)
- **Data**: [8, 3, 5, 1, 6, 4]

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Default bars | WHITE | Default Rectangle |
| Scanning element | YELLOW | During inner loop |
| Sorted bars | GREEN | After each pass |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Scan highlight | 0.2s wait | set_color YELLOW |
| Unhighlight | 0.1s wait | set_color WHITE |
| Width swap | run_time=0.5 | rate_func=linear |
| Mark sorted | run_time=0.5 | All bars up to index |
| Total | ~15s | 5 passes |

## Patterns

### Pattern: Inline Bar Creation for Sorting

**What**: Create height-proportional bars as a VGroup of Rectangles, arranged horizontally. No factory function — bars are created directly in construct(). Simplest possible setup for a sorting visualization.
**When to use**: Quick sorting prototype, minimal sorting demo where utility imports are not available. For production, prefer the shared `create_sortable_bars` factory.

```python
# Source: projects/manim-scripts/scenes/sort2.py:21-27
def create_bars(self, array):
    bars = VGroup(*[
        Rectangle(width=0.5, height=value)
        for value in array
    ]).arrange(buff=0.2)
    bars.shift(DOWN)
    return bars
```

## Scene Flow

1. **Setup** (0-1s): Bars appear arranged horizontally.
2. **Selection passes** (1-14s): For each position, scan remaining bars (YELLOW flash). After finding minimum, swap widths. Mark sorted prefix GREEN.
3. **End** (14-15s): All bars green. Wait.

> Full file: `projects/manim-scripts/scenes/sort2.py` (50 lines)
