---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/draw.py
project: manim-scripts
domain: [mathematics, geometry, calculus]
elements: [function_plot, parametric_curve, axes, coordinate_system, number_line, area_under_curve, dot, arrow, circle_node, label, grid]
animations: [draw, draw_then_fill, fade_in, fade_out, transform, replacement_transform, indicate, move, shift, rotate]
layouts: [centered, horizontal_row, vertical_stack, grid]
techniques: [value_tracker, add_updater, always_redraw, moving_camera, custom_animation, custom_mobject]
purpose: [demonstration, exploration, definition]
mobjects: [Axes, ThreeDAxes, NumberPlane, ParametricFunction, Dot, Circle, Square, Star, Arrow, Vector, Line, NumberLine, VGroup, Text, Tex, MathTex, DecimalNumber, ValueTracker]
manim_animations: [Create, Write, FadeIn, FadeOut, DrawBorderThenFill, ReplacementTransform, Indicate, MoveToTarget, Restore, MoveAlongPath, Rotate, UpdateFromAlphaFunc, Disperse]
scene_type: [Scene, ThreeDScene]
manim_version: manim_community
complexity: intermediate
lines: 312
scene_classes: [plotSmooth, SquareToCircle, ComplexExp, Positioning, CriticalPoints, UsefulUnits, Grouping, AnimateSyntax, AnimateProblem, AnimationMechanisms, SimpleCustomAnimation, CustomAnimationExample, MovingLabel, AllUpdaterTypes, UpdaterAndAnimation, ValueTrackerMove, ValueTrackerPlot]
---

## Summary

A comprehensive Manim tutorial file covering 17 scene classes that demonstrate core Manim patterns: plotting with area fills, 3D parametric curves with camera movement, positioning/alignment, grouping, animate syntax, generate_target/MoveToTarget, save_state/Restore, custom animations via UpdateFromAlphaFunc, a full custom Animation subclass (Disperse), updater types (mobject updater, dt-based updater, scene updater), and ValueTracker with always_redraw for dynamic plots. This is the single best reference for fundamental Manim patterns.

## Design Decisions

- **One concept per scene class**: Each scene demonstrates exactly one Manim pattern. This makes the file a reference catalog rather than a narrative.
- **ComplexExp uses ThreeDScene**: e^(i*pi*t) naturally lives in 3D. Camera rotates to reveal the helix from multiple angles — the same projection tricks used for any 3D function visualization.
- **Disperse as custom Animation subclass**: Shows the full Animation lifecycle: `begin()` to create dots, `interpolate_mobject(alpha)` to control per-frame state, `clean_up_from_scene()` to remove temporary mobjects. This is the definitive pattern for custom animations.
- **Three updater types side by side**: AllUpdaterTypes shows mobject updater (position), dt-based updater (velocity), and scene updater (global scaling) in one scene. Critical for understanding when to use which.
- **ValueTrackerPlot with DecimalNumber**: The parabola y=ax^2 redraws every frame via `mob.become(...)` updater, while a DecimalNumber tracks the a value. This is the standard pattern for interactive parameter exploration.

## Composition

- **plotSmooth axes**: x_range=(-3,3), y_range=(-3,3)
- **ComplexExp axes**: ThreeDAxes x_range=(-0.1, 4.25), y_range=(-1.5, 1.5), z_range=(-1.5, 1.5), y_length=5, z_length=5
- **ValueTrackerPlot axes**: x_range=[-2,2,1], y_range=[-8.5,8.5,1], x_length=4, y_length=6
- **NumberLine (ValueTrackerMove)**: x_range=[-5,5]
- **Stars grid**: 4x5, buff=0.2
- **Circles column**: 10 circles, arranged UP, buff=0.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| plotSmooth curve | RED | ax.plot |
| plotSmooth area | Default (blue) | ax.get_area |
| ComplexExp curve | Default (white) | ParametricFunction |
| Green square | GREEN | fill_opacity=0.5 |
| Blue circle | BLUE | fill_opacity=0.5 |
| Stars | YELLOW | fill_opacity=1, scale=0.5 |
| Spiral dot | YELLOW→hue cycle | Color changes with t |
| Disperse star | YELLOW | fill_opacity=1, scale=3 |
| ValueTracker parabola | RED | ax.plot |
| DecimalNumber | RED | num_decimal_places=3 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| plotSmooth curve Create | run_time=5 | Slow draw |
| Axes Create | run_time=2 | plotSmooth |
| ComplexExp camera moves | Default | Multiple self.move_camera calls |
| Spiral out | run_time=3 | UpdateFromAlphaFunc |
| Disperse | run_time=4 | Custom Animation |
| AllUpdaterTypes | 5s | self.wait(5) |
| ValueTracker animations | Default | 3 set_value plays |

## Patterns

### Pattern: Plot with Area Under Curve

**What**: Create axes, plot a function, then shade the area under the curve between two x-values using `ax.get_area()`. The area fill makes integration concepts visually concrete.
**When to use**: Integral visualization, probability density functions, cumulative distribution shading, or any area-between-curves demonstration.

```python
# Source: projects/manim-scripts/scenes/draw.py:4-10
ax = Axes(x_range=(-3, 3), y_range=(-3, 3))
curve = ax.plot(lambda x: (x+2)*x*(x-2)/2, color=RED)
area = ax.get_area(curve, x_range=(-2, 0))
self.play(Create(ax, run_time=2), Create(curve, run_time=5))
self.play(FadeIn(area))
```

### Pattern: 3D Parametric Curve with Camera Movement

**What**: Use ThreeDAxes and ParametricFunction to plot a 3D curve (e^{i*pi*t} helix). Multiple `self.move_camera()` calls show the curve from different angles — front view, 3/4 view, top-down, side view.
**When to use**: Complex number visualization, 3D function plots, helical paths, any 3D curve where different viewpoints reveal different structure.

```python
# Source: projects/manim-scripts/scenes/draw.py:21-53
axes = ThreeDAxes(x_range=(-0.1, 4.25), y_range=(-1.5, 1.5), z_range=(-1.5, 1.5))
curve = ParametricFunction(
    lambda p: axes.coords_to_point(p, np.exp(complex(0, PI*p)).real, np.exp(complex(0, PI*p)).imag),
    t_range=(0, 2, 0.1)
)
self.set_camera_orientation(phi=90*DEGREES, theta=0, focal_distance=10000)
self.play(Create(curve, run_time=2), Write(t))
self.move_camera(phi=75*DEGREES, theta=-30*DEGREES)
```

### Pattern: generate_target + MoveToTarget for Planned Animation

**What**: Call `generate_target()` to create a copy of the mobject's future state. Modify the target (color, position, scale), then animate with `MoveToTarget()`. Alternatively, `save_state()` + modifications + `Restore()` for undo.
**When to use**: When you need to specify the end state explicitly before animating (complex multi-property changes), or when you need an "undo" capability (save_state/Restore).

```python
# Source: projects/manim-scripts/scenes/draw.py:143-163
c = Circle()
c.generate_target()
c.target.set_fill(color=GREEN, opacity=0.5)
c.target.shift(2*RIGHT + UP).scale(0.5)
self.play(MoveToTarget(c))

s = Square()
s.save_state()
self.play(s.animate.set_color(PURPLE).set_opacity(0.5).shift(2*LEFT).scale(3))
self.play(s.animate.shift(5*DOWN).rotate(PI/4))
self.play(Restore(s), run_time=2)  # Undo all changes
```

### Pattern: Custom Animation Subclass

**What**: Subclass `Animation` to create a particle disperse effect. Override `begin()` to create particle dots along the mobject's boundary, `interpolate_mobject(alpha)` for per-frame logic (fade original, expand particles), and `clean_up_from_scene()` to remove temporary objects.
**When to use**: Any animation effect not achievable with built-in animations — particle explosions, custom morphs, physics-based transitions, procedural animations.

```python
# Source: projects/manim-scripts/scenes/draw.py:178-210
class Disperse(Animation):
    def __init__(self, mobject, dot_radius=0.05, dot_number=100, **kwargs):
        super().__init__(mobject, **kwargs)
        self.dot_radius = dot_radius
        self.dot_number = dot_number

    def begin(self):
        dots = VGroup(*[Dot(radius=self.dot_radius).move_to(
            self.mobject.point_from_proportion(p))
            for p in np.linspace(0, 1, self.dot_number)])
        for dot in dots:
            dot.initial_position = dot.get_center()
            dot.shift_vector = 2*(dot.get_center() - self.mobject.get_center())
        dots.set_opacity(0)
        self.mobject.add(dots)
        self.dots = dots
        super().begin()

    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)
        if alpha <= 0.5:
            self.mobject.set_opacity(1 - 2*alpha, family=False)
            self.dots.set_opacity(2*alpha)
        else:
            self.mobject.set_opacity(0)
            self.dots.set_opacity(2*(1 - alpha))
            for dot in self.dots:
                dot.move_to(dot.initial_position + 2*(alpha-0.5)*dot.shift_vector)
```

### Pattern: ValueTracker + always_redraw for Dynamic Plot

**What**: A ValueTracker parameter drives a plot that redraws every frame. The parabola `y = a*x^2` changes shape as `a` animates. A DecimalNumber updater displays the current value. This is the standard pattern for parameter exploration.
**When to use**: Interactive parameter visualization — regression line fitting, function family exploration, slider-driven demonstrations, any scenario where a single parameter changes a visual.

```python
# Source: projects/manim-scripts/scenes/draw.py:292-312
a = ValueTracker(1)
ax = Axes(x_range=[-2, 2, 1], y_range=[-8.5, 8.5, 1], x_length=4, y_length=6)
parabola = ax.plot(lambda x: a.get_value() * x**2, color=RED)
parabola.add_updater(
    lambda mob: mob.become(ax.plot(lambda x: a.get_value() * x**2, color=RED))
)
a_number = DecimalNumber(a.get_value(), color=RED, num_decimal_places=3, show_ellipsis=True)
a_number.add_updater(
    lambda mob: mob.set_value(a.get_value()).next_to(parabola, RIGHT)
)
self.add(ax, parabola, a_number)
self.play(a.animate.set_value(2))
self.play(a.animate.set_value(-2))
```

### Pattern: Three Updater Types

**What**: Demonstrates all three updater types in one scene: (1) mobject updater `lambda mob:` for relative positioning, (2) dt-based updater `def f(mob, dt):` for velocity/physics, (3) scene updater `def f(dt):` for global effects. Shows `suspend_updating()` to pause.
**When to use**: Choose mobject updater for relative positioning (label follows dot), dt-based for continuous motion (constant velocity, physics), scene updater for global effects (scaling all mobjects based on distance).

```python
# Source: projects/manim-scripts/scenes/draw.py:233-254
pointer.add_updater(lambda mob: mob.next_to(red_dot, LEFT))  # Mobject updater

def shifter(mob, dt):  # dt-based updater: 2 units RIGHT/sec
    mob.shift(2*dt*RIGHT)
red_dot.add_updater(shifter)

def scene_scaler(dt):  # Scene updater: scale by distance to origin
    for mob in self.mobjects:
        mob.set(width=2/(1 + np.linalg.norm(mob.get_center())))
self.add_updater(scene_scaler)
```

## Scene Flow

This file is a catalog — each scene class is independent and self-contained. Key scenes:
1. **plotSmooth**: Axes draw (2s), curve draws (5s), area fades in.
2. **ComplexExp**: 3D helix draws, camera orbits through 5 viewpoints.
3. **AnimationMechanisms**: Circle target animation, square save/restore.
4. **SimpleCustomAnimation**: Yellow dot spirals outward with color cycling (3s).
5. **CustomAnimationExample**: Star disperses into 200 particles (4s).
6. **ValueTrackerPlot**: Parabola shape-shifts as parameter a goes 1→2→-2→1.

> Full file: `projects/manim-scripts/scenes/draw.py` (312 lines)
