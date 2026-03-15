---
source: https://github.com/vivek3141/videos/blob/main/navier.py
project: vivek3141_videos
domain: [mathematics, physics, fluid_dynamics, calculus]
elements: [vector_field, axes, equation, label, number_line, function_plot, surrounding_rect, arrow, line]
animations: [write, transform, fade_in, animate_parameter]
layouts: [centered, dual_panel, vertical_stack]
techniques: [value_tracker, add_updater, custom_mobject, progressive_disclosure]
purpose: [derivation, step_by_step, definition, demonstration, decomposition]
mobjects: [VectorField, NumberPlane, Axes, FunctionGraph, Polygon, Rectangle, TexMobject, Text, VGroup, Vector, Line, BulletedList, BackgroundRectangle, ScreenRectangle, Brace, Dot, Arrow]
manim_animations: [Write, Transform, FadeInFromDown, ShowCreation, Uncreate, ApplyMethod, FadeOut]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 548
scene_classes: [NumberedList, Intro, Equations, MilleniumPrize, ApplicationsOne, Assumptions, Newtonian, Incompressible, Isothermal, Divergence, VectorFieldDemo, DivergenceDemo, DivergenceEq, SecondEq, Smooth]
---

## Summary

Explains the Navier-Stokes equations through progressive decomposition. Each term in the momentum equation (pressure, friction, external force) is highlighted with a colored BackgroundRectangle and labeled. The incompressibility condition (divergence of velocity = 0) is explained using Manim's built-in VectorField with positive and negative divergence demos. Physical concepts (Newtonian fluid, incompressible, isothermal) are introduced via Assumptions bulleted list. A custom NumberedList mobject extends BulletedList for ordered items. The smoothness question is visualized with a ValueTracker-driven tangent line approaching a point.

## Design Decisions

- **Color-coded equation terms**: Each variable gets a consistent color: u (velocity) = BLUE, rho (density) = YELLOW, p (pressure) = RED, mu (viscosity) = GOLD, g (gravity) = GOLD. A shared `color_map` dict is reused across scenes.
- **Term-by-term decomposition**: The momentum equation is broken apart by highlighting each term with a TEAL BackgroundRectangle (fill_opacity=0, stroke_width=4) and labeling it ("Pressure", "Friction", "External"). The viewer learns what each piece contributes.
- **Built-in VectorField for divergence**: Uses Manim's VectorField class with lambda functions for positive divergence (t/3) and negative divergence (-t/3). Title overlay with background rectangle for readability.
- **Newtonian fluid via viscosity plot**: Constant viscosity (TEAL horizontal line) vs shear-thinning (RED x^{-0.5} curve) side by side, with a ScreenRectangle placeholder for animation.
- **Incompressible fluid animation**: Polygon water with ValueTracker height. Piston (Rectangle + Line) moves with updater, water level changes with `there_and_back` rate function.

## Composition

- **Intro field**: Grid of Vector arrows, x in [-9,8] step 0.75, y in [-4,4] step 1.5, color=PURPLE
- **Navier-Stokes display**: eq1 (continuity) at 1*UP, eq2 (momentum) at 1*DOWN, title at 3*UP
- **Millenium Prize list**: NumberedList scaled 0.75, shifted 0.5*DOWN, `fade_all_but(3)` highlights NS entry
- **Newtonian plot**: Axes x=[0,6], y=[0,5], shifted left by 2.75 with ScreenRectangle at 3.75*RIGHT
- **Incompressible**: Container Lines at x=+/-2, bottom at y=-2, piston at y=1 with Rectangle handle
- **VectorField demos**: Full-screen with NumberPlane at 0.5 opacity, title with background_rectangle at top edge

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Velocity u | BLUE | Shared color_map |
| Density rho | YELLOW | Shared color_map |
| Pressure p | RED | Shared color_map |
| Viscosity mu | GOLD | Shared color_map |
| Gravity g | GOLD | Shared color_map |
| Title | GREEN | Text("Navier-Stokes Equations") |
| Term highlight | TEAL | BackgroundRectangle, stroke_width=4 |
| Term labels | TEAL | Text objects |
| Divergence title | YELLOW | tex_to_color_map for "div" |
| Vector field | Default | VectorField auto-colors |
| Intro vectors | PURPLE | Vector grid |
| Newtonian line | TEAL | FunctionGraph |
| Non-Newtonian | RED | FunctionGraph |
| Water | BLUE_E | Polygon fill_opacity=1 |
| Piston handle | YELLOW | Rectangle fill_opacity=1 |
| Smooth function | GOLD | FunctionGraph stroke_opacity=0.8 |
| Tangent dots | YELLOW | Dot(fill_opacity=1) |
| Number list | BLUE | num_color in NumberedList |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Write equations | ~1s each | Standard |
| fade_all_but | ~1s | BulletedList highlight |
| Water piston | there_and_back | ValueTracker animation |
| Tangent approach | run_time=3, linear | ValueTracker converges |
| VectorField creation | ShowCreation ~2s | Full field |
| Total | ~3 minutes | 15 scenes |

## Patterns

### Pattern: Custom NumberedList Mobject

**What**: Extends BulletedList to use numbered bullets ("1)", "2)") instead of dots. Each number is colored via `num_color` config. Items are split by newline and formatted with "\\\\". The numbers are positioned with `next_to(part[0], LEFT, MED_SMALL_BUFF)`.

**When to use**: Ordered lists in educational videos, enumerating steps in a process, Millenium Prize Problems, ranking items, any numbered enumeration.

```python
# Source: projects/vivek3141_videos/navier.py:12-31
class NumberedList(BulletedList):
    CONFIG = {
        "dot_scale_factor": 1,
        "num_color": BLUE,
    }
    def __init__(self, *items, **kwargs):
        line_separated_items = [s + "\\\\" for s in items]
        TextMobject.__init__(self, *line_separated_items, **kwargs)
        for num, part in enumerate(self):
            dot = TexMobject(f"{num+1})", color=self.dot_color,
                tex_to_color_map={f"{num+1}": self.num_color})
            dot.scale(self.dot_scale_factor)
            dot.next_to(part[0], LEFT, MED_SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange(DOWN, aligned_edge=LEFT, buff=self.buff)
```

### Pattern: Equation Term Decomposition with BackgroundRectangle

**What**: Break a complex equation into terms by wrapping each term in a BackgroundRectangle (no fill, colored stroke) and adding a text label below. Animate sequentially: highlight term, show label, shift surrounding terms to make room for the next annotation. Uses a shared config dict for consistent rectangle styling.

**When to use**: Explaining multi-term equations in physics (force balance, energy conservation), decomposing loss functions in ML, breaking down any formula where each term has a distinct physical meaning.

```python
# Source: projects/vivek3141_videos/navier.py:448-488
br_config = {
    "buff": 0.1875, "fill_opacity": 0,
    "stroke_opacity": 1, "stroke_width": 4, "color": TEAL
}
r1 = BackgroundRectangle(eq2[4:6], **br_config)
t1 = Text("Pressure", color=TEAL)
t1.move_to(r1, aligned_edge=DOWN).shift(0.7 * DOWN)

self.play(Write(r1))
self.play(FadeInFromDown(t1))
# Move external force term right to make room
self.play(ApplyMethod(eq3[3:].shift, 2.5 * RIGHT),
          TransformFromCopy(eq2[4:7], eq2cp[5:8]))

# Repeat for "Friction" and "External" terms
r2 = BackgroundRectangle(eq2[7:10], **br_config)
t2 = Text("Friction", color=TEAL)
self.play(Transform(r1, r2), Transform(t1, t2))
```

### Pattern: Fluid Simulation with ValueTracker Polygon

**What**: A water surface represented as a Polygon whose top edge height is driven by a ValueTracker. The updater rebuilds the Polygon each frame. A piston group (Line + Rectangle) uses a separate updater to track the water surface position. `there_and_back` rate function makes the piston compress and release.

**When to use**: Fluid level animations, piston/cylinder diagrams, any container with changing volume, hydraulic press demonstrations, incompressible fluid concepts.

```python
# Source: projects/vivek3141_videos/navier.py:236-266
t = ValueTracker(1)
water = Polygon(
    [-2, t.get_value(), 0], [2, t.get_value(), 0],
    [2, -2, 0], [-2, -2, 0],
    color=BLUE_E, fill_opacity=1)

def update_func_water(water):
    water2 = Polygon(
        [-2, t.get_value(), 0], [2, t.get_value(), 0],
        [2, -2, 0], [-2, -2, 0],
        color=BLUE_E, fill_opacity=1)
    water.become(water2)
water.add_updater(update_func_water)

obj2 = VGroup(...)  # Piston
obj2.add_updater(lambda grp: grp.move_to(water, UP).shift(1.125 * UP))

self.play(t.increment_value, -1, rate_func=there_and_back)
```

## Scene Flow

1. **Intro** (0-5s): Grid of purple vectors fills screen. Sets the "fluid flow" visual tone.
2. **Equations** (5-15s): Both Navier-Stokes equations displayed. Green title.
3. **MilleniumPrize** (15-25s): Numbered list of 7 problems. Highlight #4 (Navier-Stokes).
4. **Assumptions** (25-35s): BulletedList: Newtonian, Incompressible, Isothermal. Each highlighted in turn.
5. **Newtonian** (35-50s): Constant viscosity plot (TEAL) vs Non-Newtonian (RED). ScreenRectangle for honey video.
6. **Incompressible** (50-60s): Water in container with piston. Height oscillates via ValueTracker.
7. **Divergence** (60-75s): Continuity equation decomposed: nabla (Divergence) + u (Velocity Vector Field) via Braces.
8. **VectorFieldDemo + DivergenceDemo** (75-90s): VectorField with cos/sin. Then positive/negative divergence demos.
9. **SecondEq** (90-115s): Momentum equation decomposed term by term: F=ma analogy, pressure, friction, external force. Material derivative note in Rectangle.
10. **Smooth** (115-125s): Function with tangent line approaching a point via ValueTracker. "Smooth Solution" title.

> Full file: `projects/vivek3141_videos/navier.py` (548 lines)
