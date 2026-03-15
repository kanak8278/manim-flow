---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/manim1.py
project: manim-scripts
domain: [mathematics, geometry]
elements: [circle_node, label]
animations: [fade_in, move, write]
layouts: [side_by_side, vertical_stack]
techniques: [factory_pattern]
purpose: [definition, demonstration]
mobjects: [Ellipse, Intersection, Union, Exclusion, Difference, Text, MarkupText, Group]
manim_animations: [FadeIn, Write]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 37
scene_classes: [BooleanOperations]
---

## Summary

Demonstrates Manim's boolean set operations on two overlapping ellipses: Intersection (green), Union (orange), Exclusion (yellow), and Difference (pink). Each result is scaled down and positioned to the right of the source ellipses with a text label. Uses Manim's built-in CSG (Constructive Solid Geometry) mobjects for clean boolean geometry.

## Design Decisions

- **Overlapping ellipses as input**: Two colored ellipses (BLUE, RED) with partial overlap make the boolean regions visually obvious. The thick stroke_width=10 makes boundaries clear.
- **Scale and reposition results**: Each boolean result animates to a small version next to the source, creating a catalog of operations. The viewer sees source on left, results on right.
- **MarkupText with underline**: Uses HTML-style markup `<u>Boolean Operation</u>` for the title — demonstrates Manim's MarkupText capability.

## Composition

- **Source ellipses**: width=4.0, height=5.0, fill_opacity=0.5, stroke_width=10. Left ellipse at LEFT, right at RIGHT. Group moved to LEFT*3.
- **Result positions**: Intersection scaled 0.25 at RIGHT*5 + UP*2.5. Union scaled 0.3 below intersection. Exclusion scaled 0.3 below union. Difference scaled 0.3 left of union.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Ellipse 1 | BLUE | fill_opacity=0.5, stroke_width=10 |
| Ellipse 2 | RED | fill_opacity=0.5, stroke_width=10 |
| Intersection | GREEN | fill_opacity=0.5 |
| Union | ORANGE | fill_opacity=0.5 |
| Exclusion | YELLOW | fill_opacity=0.5 |
| Difference | PINK | fill_opacity=0.5 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Ellipse group FadeIn | Default | All at once |
| Each boolean result | Default | animate.scale + move_to |
| Label FadeIn | Default | Per operation |
| Total | ~15s | 4 operations + waits |

## Patterns

### Pattern: Boolean Geometry Operations

**What**: Use Manim's CSG mobjects (Intersection, Union, Exclusion, Difference) to compute and display boolean operations on overlapping shapes. Results are new mobjects that can be independently styled and animated.
**When to use**: Set theory visualization (Venn diagrams), computational geometry demonstrations, area calculation visualizations, or any scenario involving overlapping regions.

```python
# Source: projects/manim-scripts/scenes/manim1.py:13-34
i = Intersection(ellipse1, ellipse2, color=GREEN, fill_opacity=0.5)
self.play(i.animate.scale(0.25).move_to(RIGHT * 5 + UP * 2.5))

u = Union(ellipse1, ellipse2, color=ORANGE, fill_opacity=0.5)
self.play(u.animate.scale(0.3).next_to(i, DOWN, buff=union_text.height * 3))

e = Exclusion(ellipse1, ellipse2, color=YELLOW, fill_opacity=0.5)
d = Difference(ellipse1, ellipse2, color=PINK, fill_opacity=0.5)
```

## Scene Flow

1. **Setup** (0-2s): Two overlapping ellipses with "Boolean Operation" title fade in.
2. **Intersection** (2-5s): Green intersection region scales down and moves to upper right. Label appears.
3. **Union** (5-8s): Orange union scales down below intersection.
4. **Exclusion** (8-11s): Yellow exclusion below union.
5. **Difference** (11-14s): Pink difference to the left of union.

> Full file: `projects/manim-scripts/scenes/manim1.py` (37 lines)
