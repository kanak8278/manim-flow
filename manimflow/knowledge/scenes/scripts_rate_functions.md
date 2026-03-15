---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/rate.py
project: manim-scripts
domain: [mathematics]
elements: [function_plot, parametric_curve, surrounding_rect, label, dot, line]
animations: [draw, move, rotate]
layouts: [grid, horizontal_row]
techniques: [data_driven, factory_pattern]
purpose: [overview, comparison, demonstration]
mobjects: [ParametricFunction, SurroundingRectangle, Text, Dot, Line, VGroup]
manim_animations: [DrawBorderThenFill, FadeIn, Write, MoveAlongPath]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 69
scene_classes: [RateFuncExample, RateFunctions1Example]
---

## Summary

Two scenes demonstrating Manim's rate functions (easing curves). RateFuncExample generates a visual catalog of ALL available rate functions by introspecting `rate_functions.__dict__`, plotting each as a parametric curve with a labeled background rectangle, then arranging them in an 8-column grid. RateFunctions1Example compares ease_in_sine, ease_out_sine, and ease_in_out_sine side by side with dots moving along parallel lines.

## Design Decisions

- **Introspection-based catalog**: RateFuncExample dynamically discovers all rate functions from `rate_functions.__dict__` rather than hardcoding them. This automatically captures any new rate functions added to Manim.
- **Parametric plot for rate functions**: Each rate function f is plotted as ParametricFunction `[x, f(x), 0]` over t_range=[0,1]. Stretched to fixed width/height for consistent grid cells.
- **Grid layout for comparison**: 8-column grid fills the entire frame. All rate functions visible simultaneously for easy comparison — the viewer scans the grid to find the easing they want.
- **Parallel line race (RateFunctions1Example)**: Three dots move along parallel colored lines with different rate functions. The visual "race" makes timing differences viscerally obvious — ease_in starts slow, ease_out ends slow.

## Composition

- **Grid cells**: Each cell = SurroundingRectangle (WHITE) + ParametricFunction (YELLOW, stretched to 1.5w x 1h) + Text title (BOLD, scale=0.5)
- **Grid arrangement**: arrange_in_grid(cols=8), scaled to fill frame
- **Parallel lines**: 3*LEFT to 3*RIGHT, separated by 1 unit (UP, ORIGIN, DOWN)
- **Labels**: "Ease In", "Ease out", "Ease In Out" next_to lines, RIGHT

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Rate function plots | YELLOW | ParametricFunction |
| Plot background | WHITE | SurroundingRectangle |
| Plot title | WHITE | BOLD, scale=0.5 |
| Line 1 (ease in) | RED | Line |
| Line 2 (ease out) | GREEN | Line |
| Line 3 (ease in out) | BLUE | Line |
| Dots | WHITE | Default Dot |
| Labels | WHITE | Tex |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Grid FadeIn | run_time=0 | Static scene (self.add) |
| Dot race | run_time=7 | All three dots simultaneously |
| Line FadeIn | Default | All lines at once |
| Total (RateFuncExample) | 0s | Static catalog |
| Total (RateFunctions1Example) | ~10s | Setup + race + wait |

## Patterns

### Pattern: Introspective Rate Function Catalog

**What**: Dynamically discover all rate functions from Manim's module, plot each as a parametric curve in a labeled cell, arrange in a grid. Fully automatic — no hardcoded function names.
**When to use**: Generating visual catalogs of any Manim module's contents — rate functions, color palettes, mobject types. Also useful as a reference sheet for choosing the right easing.

```python
# Source: projects/manim-scripts/scenes/rate.py:3-38
for k, v in rate_functions.__dict__.items():
    if "function" in str(v):
        if not k.startswith("__") and not k.startswith("sqrt") and not k.startswith("bezier"):
            rate_func = v
            plot = (
                ParametricFunction(
                    lambda x: [x, rate_func(x), 0],
                    t_range=[0, 1, .01],
                    use_smoothing=False, color=YELLOW,
                )
                .stretch_to_fit_width(1.5)
                .stretch_to_fit_height(1)
            )
            plot_bg = SurroundingRectangle(plot).set_color(WHITE)
            plot_title = Text(rate_func.__name__, weight=BOLD).scale(0.5).next_to(plot_bg, UP, buff=0.1)
            x.add(VGroup(plot_bg, plot, plot_title))
x.arrange_in_grid(cols=8)
```

### Pattern: Parallel Dot Race for Timing Comparison

**What**: Three dots move along parallel lines using MoveAlongPath with different rate functions. Running simultaneously makes timing differences immediately visible — which starts faster, which decelerates, which is smooth.
**When to use**: Comparing easing functions, demonstrating rate_func parameter effect, or any scenario where timing differences between parallel processes need to be shown.

```python
# Source: projects/manim-scripts/scenes/rate.py:42-67
line1 = Line(3*LEFT, 3*RIGHT).shift(UP).set_color(RED)
dot1 = Dot().move_to(line1.get_left())
self.play(
    MoveAlongPath(dot1, line1, rate_func=rate_functions.ease_in_sine),
    MoveAlongPath(dot2, line2, rate_func=rate_functions.ease_out_sine),
    MoveAlongPath(dot3, line3, rate_func=rate_functions.ease_in_out_sine),
    run_time=7
)
```

## Scene Flow

1. **RateFuncExample**: Static catalog — all rate function plots appear in an 8-column grid. No animation.
2. **RateFunctions1Example** (0-10s): Three colored lines with labels appear. Dots start at left. All three race to the right simultaneously with different easing. 7s race reveals timing differences.

> Full file: `projects/manim-scripts/scenes/rate.py` (69 lines)
