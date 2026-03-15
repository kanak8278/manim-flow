---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/color_ex.py
project: manim-scripts
domain: [mathematics]
elements: [grid, box]
animations: [draw_then_fill, rotate, fade_in, fade_out, move, stagger, lagged_start]
layouts: [grid, horizontal_row]
techniques: [data_driven, factory_pattern]
purpose: [demonstration, overview]
mobjects: [VGroup, Square, RegularPolygon, VMobject]
manim_animations: [DrawBorderThenFill, Rotate, FadeIn, FadeOut, MoveToTarget, AnimationGroup]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 80
scene_classes: [BasicAnimations, ConflictingAnimations, LaggingGroup, NewColors]
---

## Summary

Four scenes demonstrating animation techniques: BasicAnimations shows 5 pentagons rotating with different rate functions side by side. LaggingGroup shows 20 squares fading in with lag_ratio=0.15. NewColors is the standout — it introspects all XKCD colors from Manim, displays them in a 23x41 grid, then animates each square to its hue-sorted position using MoveToTarget with low lag_ratio for a wave-like sorting effect.

## Design Decisions

- **Rate function comparison via parallel rotation**: Five identical pentagons rotate simultaneously, each with a different rate_func. Side-by-side makes the difference viscerally obvious — same visual setup as the rate function race but applied to rotation.
- **XKCD color introspection**: Dynamically discovers all ManimColor objects in the XKCD module using `inspect.getmembers`. This auto-captures the full palette without hardcoding.
- **HSV sorting for visual coherence**: Colors are sorted by (hue, value) using `to_hsv()`. The MoveToTarget animation creates a visual "sorting" where each square migrates to its correct position in hue-space — a meta-visualization of sorting itself.
- **Low lag_ratio (0.001) for wave effect**: 900+ squares with lag_ratio=0.001 creates a cascading wave. Higher lag_ratio would be too sequential; lower would be simultaneous.

## Composition

- **Pentagon row**: 5 RegularPolygon(5), radius=1, arranged RIGHT
- **LaggingGroup grid**: 20 squares in 4x5, scale=0.75
- **Color grid**: 23 rows x 41 columns, width=config.frame_width

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Pentagons | RED | fill_opacity=0.5 |
| Lagging squares | RED | fill_opacity=0.05*j (gradient) |
| Color grid squares | All XKCD colors | fill_opacity=1, stroke_opacity=0 |
| Background (NewColors) | #000000 | Explicit black |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Pentagon rotation | run_time=2 | 5 simultaneous rotations |
| Lagging grid FadeIn | lag_ratio=0.15 | 20 squares |
| Color grid FadeIn | run_time=5 | lag_ratio=0.001 |
| Color sorting MoveToTarget | run_time=5 | lag_ratio=0.001 |
| Color grid FadeOut | run_time=5 | lag_ratio=0.001 |
| Total (NewColors) | ~16s | FadeIn + sort + FadeOut |

## Patterns

### Pattern: Introspective Color Palette Grid with Hue Sort

**What**: Discover all colors from a Manim color module, display as filled squares in a grid, then animate each square to its hue-sorted position using generate_target/MoveToTarget. The sorting animation itself is beautiful — a visual metaphor for the concept of sorting.
**When to use**: Color palette visualization, demonstrating sorting algorithms on non-numeric data, or creating visual catalogs of any ordered collection.

```python
# Source: projects/manim-scripts/scenes/color_ex.py:33-77
xkcd_colors = [color for _, color in inspect.getmembers(XKCD, lambda obj: isinstance(obj, ManimColor))]
for color in xkcd_colors:
    col_square = Square()
    col_square.set_fill(color, opacity=1)
    col_square.set_stroke(opacity=0)
    xkcd_color_mobjects.add(col_square)

xkcd_sorted_ind = sorted(range(len(xkcd_colors)), key=lambda ind: xkcd_colors[ind].to_hsv())
xkcd_color_mobjects.arrange_in_grid(23, 41)

for ind, col_square in enumerate(xkcd_color_mobjects):
    col_square.generate_target()
    target_ind = xkcd_sorted_ind.index(ind)
    col_square.target.move_to(xkcd_color_mobjects[target_ind])

move_squares = AnimationGroup(*[MoveToTarget(s) for s in xkcd_color_mobjects], lag_ratio=0.001, run_time=5)
self.play(move_squares)
```

### Pattern: Rate Function Comparison via Parallel Animation

**What**: Apply different rate functions to the same animation (Rotate) on identical mobjects arranged side by side. The simultaneous execution makes timing differences immediately visible.
**When to use**: Demonstrating rate_func/easing differences, comparing animation styles, or any A/B/C comparison of animation parameters.

```python
# Source: projects/manim-scripts/scenes/color_ex.py:3-18
polys = VGroup(*[RegularPolygon(5, radius=1, color=RED, fill_opacity=0.5) for j in range(5)]).arrange(RIGHT)
self.play(
    Rotate(polys[0], PI, rate_func=lambda t: t),
    Rotate(polys[1], PI, rate_func=smooth),
    Rotate(polys[2], PI, rate_func=lambda t: np.sin(t*PI)),
    Rotate(polys[3], PI, rate_func=there_and_back),
    Rotate(polys[4], PI, rate_func=lambda t: 1 - abs(1-2*t)),
    run_time=2
)
```

## Scene Flow

1. **BasicAnimations** (0-5s): 5 pentagons draw, then rotate with different easing.
2. **ConflictingAnimations** (0-3s): Square rotates PI and -PI simultaneously (demonstrates conflict).
3. **LaggingGroup** (0-3s): 20 squares cascade in with lag_ratio=0.15.
4. **NewColors** (0-16s): ~900 color squares FadeIn as wave, sort by hue with MoveToTarget wave, FadeOut as wave.

> Full file: `projects/manim-scripts/scenes/color_ex.py` (80 lines)
