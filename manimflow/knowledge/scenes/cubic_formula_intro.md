---
source: https://github.com/far1din/manim/blob/main/cubic_formula/introduction.py, https://github.com/far1din/manim/blob/main/cubic_formula/example.py, https://github.com/far1din/manim/blob/main/cubic_formula/functions.py, https://github.com/far1din/manim/blob/main/cubic_formula/dtpa.py
project: manim_far1din
domain: [mathematics, algebra, calculus]
elements: [title, equation, formula, label, axes, function_plot, dot, arrow, brace, number_line, cube, prism, svg_icon]
animations: [write, fade_in, fade_out, transform, replacement_transform, indicate, draw, rotate, zoom_in, camera_rotate]
layouts: [centered, edge_anchored, vertical_stack, side_by_side]
techniques: [moving_camera, camera_save_restore, svg_integration, traced_path, add_updater, value_tracker, always_redraw, progressive_disclosure]
purpose: [derivation, step_by_step, exploration, demonstration, overview]
mobjects: [MathTex, Text, Tex, VGroup, Axes, Dot, Arrow, Brace, SVGMobject, Square, NumberLine, SurroundingRectangle, Cross]
manim_animations: [Write, FadeIn, FadeOut, Create, Uncreate, ShowCreation, Transform, ReplacementTransform, Indicate, ShowPassingFlash, Unwrite, Flash, Rotate, Rotating, TransformFromCopy, MoveToTarget]
scene_type: MovingCameraScene
manim_version: manim_community
complexity: advanced
lines: 1760
scene_classes: [Intro, I2, EX1, EX2, F1, F2, DTPA1, DTPA2, DTPA3, DTPA4, DTPA5]
---

## Summary

A multi-scene derivation of the cubic formula, spanning introduction (Fibonacci spiral with SVG integration, general cubic equation to 3D cube visualization), worked example (depressed cubic x^3+6x=20 solved step-by-step with number line verification), algebraic derivation in 2D (complete-the-cube technique reducing to quadratic formula), and the depressed-to-polynomial-association showing how to translate any cubic ax^3+bx^2+cx+d=0 to x^3+mx=n form. Uses MovingCameraScene extensively for zooming into equation details and ThreeDScene for the 3D cube teaser.

## Design Decisions

- **Fibonacci spiral opening**: The Intro scene builds Fibonacci squares with TracedPath and camera updaters that zoom out as the spiral grows, creating a visually impressive opening that connects to mathematical beauty before diving into the cubic formula.
- **Color-coded coefficients throughout**: YELLOW for a (leading coefficient), RED/BLUE for b, GREEN_B for c, ORANGE for d, BLUE for m, PURPLE for n. These colors persist across ALL scenes so the viewer can track terms through every transformation.
- **ShowPassingFlash + SurroundingRectangle for emphasis**: Used repeatedly to draw momentary attention to specific terms in equations. The flash sweeps across the rectangle and disappears, less disruptive than persistent highlighting.
- **MovingCameraScene for equation zoom**: When equations get complex, the camera zooms to focus on the relevant portion (e.g., zooming into the quadratic formula application, then back out to see the full context).
- **Progressive equation transformation**: Each algebraic step is a ReplacementTransform from the previous equation, showing exact morphing between forms. This is critical for the cubic derivation where 10+ algebraic manipulations happen sequentially.
- **camera.frame.save_state / restore**: The EX2 and F2 scenes save camera state at the start, zoom in for detailed work, then restore to show the full picture. This pattern is used 4+ times across scenes.

## Composition

- **Intro Fibonacci squares**: VGroup of squares with Tex labels, arranged in spiral pattern using `next_to(squares, direction, buff=0)` with rotating directions [RIGHT, UP, LEFT, DOWN].
- **General cubic equation**: MathTex at ORIGIN, individual characters color-coded by coefficient index.
- **Axes (multiple scenes)**: x_range=[-7, 7], y_range=[-12, 12, 2], include_numbers=True, font_size=27, tips=False.
- **Zero point dots**: Dot(color=RED, radius=0.1) at intersection points, set_z_index(2).
- **Equation layout**: Primary equation at ORIGIN or `to_edge(UP)`. Supporting equations stack DOWN with buff=0.5-1.0. Helper identities at `to_edge(LEFT + UP)`.
- **Number line (EX2)**: x_range=[-3, 3, 1], length=10, include_numbers=True. Scaled 0.9, opacity 0.7.
- **Camera zoom widths**: Typically `set_width(target.width * 1.5)` or `set_height(target.height * 1.7)`.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Leading coefficient a | YELLOW / PINK | Varies by scene context |
| Coefficient b | RED / BLUE | |
| Coefficient c | GREEN_B | |
| Constant d | ORANGE | |
| Depressed m | BLUE | In x^3 + mx = n |
| Depressed n | PURPLE | In x^3 + mx = n |
| Cubic plot | YELLOW_C | |
| Zero points | RED | Dot, radius=0.1, z_index=2 |
| Inflection point | BLUE / BLUE_D | |
| Translated plot g(x) | RED / RED_C | |
| x solution formula | YELLOW_A | Main color |
| Complete-cube subtracted term | RED / RED_E | |
| k substitution | RED | |
| Quadratic formula a,b,c | YELLOW, BLUE, GREEN | |
| SurroundingRectangle flash | RED / WHITE / YELLOW_E | ShowPassingFlash |
| Fibonacci squares | DARK_GRAY | set_color |
| Egypt/Greece SVGs | default | |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Equation Write | default or run_time=1-2 | |
| ReplacementTransform | default | Between equation forms |
| ShowPassingFlash | time_width=0.5-1.0 | Emphasis flash |
| Indicate | default | scale_factor=1 (no size change) |
| Camera zoom | default | Combined with equation transforms |
| ValueTracker cubic morph | run_time=1.5 each | DTPA3 coefficient animation |
| Fibonacci spiral rotation | default per step | PI/2 rotation, camera zooms by phi*0.9 |
| 3D cube Rotating | run_time=2.5 | About UP+RIGHT axis |
| Total video | ~10-15 minutes | Full cubic formula derivation |

## Patterns

### Pattern: ShowPassingFlash Emphasis on Equation Terms

**What**: Wraps a SurroundingRectangle around a specific MathTex submobject and applies ShowPassingFlash with time_width=0.5, creating a brief sweep highlight that draws attention without persisting. Often paired with Indicate at scale_factor=1 for a subtle color pulse.

**When to use**: Drawing attention to specific terms in long equations during algebraic derivations, highlighting the relevant variable before a substitution step, emphasizing a term that will change in the next transformation.

```python
# Source: projects/manim_far1din/cubic_formula/functions.py:48-49
self.play(
    Indicate(f[3], scale_factor=1),
    Indicate(f[6], scale_factor=1),
    ShowPassingFlash(SurroundingRectangle(f[3], color=BLUE), time_width=.5),
    ShowPassingFlash(SurroundingRectangle(f[6], color=PURPLE), time_width=.5),
)
```

### Pattern: MovingCameraScene Zoom for Equation Detail

**What**: Saves camera state at scene start, zooms into specific equation portions by animating camera.frame to match a target's center and width (with multiplier), does detailed work, then restores to show full context. The zoom animation happens simultaneously with equation transforms.

**When to use**: Long algebraic derivations where individual steps have small but important details, any scene where the working area grows beyond comfortable viewing, presentations that need to alternate between overview and detail views.

```python
# Source: projects/manim_far1din/cubic_formula/example.py:112-113
self.camera.frame.save_state()

# Later, zoom in:
self.play(
    Write(x_solution),
    self.camera.frame.animate.move_to(arrow_2.get_center()).shift(DOWN)
)

# Zoom to specific equation:
self.play(
    self.camera.frame.animate.move_to(cc_eq_2.get_center()).set_width(cc_eq_2.width * 2)
)

# Restore:
self.play(self.camera.frame.animate.restore())
```

### Pattern: Fibonacci Spiral with Camera Tracking Updaters

**What**: Builds Fibonacci squares arranged in a spiral pattern, uses TracedPath on a Dot that rotates PI/2 about each square's corner. Camera follows the dot via updater, and the stroke width scales with camera zoom. The camera zooms out by the golden ratio each step.

**When to use**: Mathematical beauty introductions, golden ratio visualizations, any opening sequence that needs visual wow factor while remaining mathematically rigorous. Spiral growth animations.

```python
# Source: projects/manim_far1din/cubic_formula/introduction.py:100-146
path = TracedPath(dot.get_center)

def update_camera_position(camera):
    camera.move_to(dot.get_center())

def update_spiral(path):
    path.set_stroke_width(self.camera.frame.height / 1.5)

def update_dot(dot):
    dot.set_height(center_dot.height * (self.camera.frame.height / starting_frame_height))

self.add(path)
path.add_updater(update_spiral)
self.camera.frame.add_updater(update_camera_position)
dot.add_updater(update_dot)

phi = (1 + 5 ** (1 / 2)) / 2
for i in range(n + 1):
    direction = directions[i % 4] + directions[(i + 1) % 4]
    self.play(
        Rotate(dot, about_point=squares[i].get_corner(direction), angle=PI / 2),
        self.camera.frame.animate.scale(phi * 0.9),
        rate_func=linear,
    )
```

### Pattern: ValueTracker-Driven Dynamic Cubic Plot

**What**: Uses ValueTrackers for coefficients a, b, c, d of a cubic function, with always_redraw on the plot and inflection point Dot. Animating the ValueTrackers morphs the cubic curve and moves the inflection point in real time, showing how different cubics relate.

**When to use**: Exploring how parameter changes affect function shape, comparing multiple function instances, demonstrating that all cubics of a family share structural properties. Interactive-feeling coefficient exploration.

```python
# Source: projects/manim_far1din/cubic_formula/dtpa.py:220-265
a = ValueTracker(1)
b = ValueTracker(0)
c = ValueTracker(-5)
d = ValueTracker(3)

plot = always_redraw(lambda: axes.plot(
    lambda x: cubic(x, a.get_value(), b.get_value(), c.get_value(), d.get_value()),
    color=YELLOW_C
))
ip = always_redraw(lambda: Dot(color=BLUE, radius=.1).move_to(
    axes.coords_to_point(0, d.get_value(), 0)
).set_z_index(2))

self.play(
    a.animate.set_value(3),
    c.animate.set_value(-3),
    d.animate.set_value(1),
    ReplacementTransform(ft1, ft2),
    run_time=1.5
)
```

### Pattern: Depressed Cubic Translation via Graph Shift

**What**: Shows f(x) as a cubic plot, then creates g(x) = f(x - b/3a) as a shifted copy of the plot, demonstrating visually that translating the cubic eliminates the x^2 term and moves the inflection point to the y-axis.

**When to use**: Polynomial depression (eliminating second-highest degree term), Tschirnhaus transformation visualization, any coordinate translation that simplifies an equation. Showing the geometric meaning of algebraic substitution.

```python
# Source: projects/manim_far1din/cubic_formula/dtpa.py:163-197
g = MathTex("g(x) = f(x - \\frac{b}{3a})").scale(.8)
plot_g = copy.deepcopy(plot).shift(axes.coords_to_point(1, 0, 0)).set_color(RED)
g_zero_points = copy.deepcopy(VGroup(zp1, ip, zp2)).shift(axes.coords_to_point(1, 0, 0)).set_color(YELLOW)

self.play(FadeIn(plot_g, shift=RIGHT))
self.play(Write(g))
self.play(Create(g_zero_points))
```

## Scene Flow

1. **Intro: Fibonacci spiral** (0-30s): Egypt and Greece SVGs fade in/out. Fibonacci squares build. Dot traces spiral with camera tracking and zoom-out updaters. Spiral undraws with Flash.
2. **Intro: General cubic** (30-50s): ax^3+bx^2+cx+d=0 writes with colored coefficients. Axes and cubic plot create. Zero points appear as RED dots. Transforms to 3D cube + prisms. Cube rotates. Transforms to x solution formula.
3. **Example: Setup** (50-90s): x^3+9x^2+33x+25=0 with colored coefficients. Translation arrow and "Translate by b/3a" label. Substituted form writes out. Simplifies to x^3+6x=20 (depressed cubic).
4. **Example: Solution** (90-140s): Camera zooms to show cubic formula. Values substituted (n=20, m=6). Number line with solution dot at x=2. Camera zooms back. "Translate by -3" reverses to get x=-1 for original equation.
5. **Functions: Derivation part 1** (140-240s): x^3+mx=n written and analyzed. t*u=m and t=x+u/3 established. Complete cube equation t^3-(u/3)^3=n derived. Three unknowns (t, u, x) identified.
6. **Functions: Derivation part 2** (240-360s): Algebraic manipulation through 8+ ReplacementTransforms. Multiply by 27, substitute u=m/t, multiply by t^3, rearrange to quadratic in k=t^3. Apply quadratic formula. Simplify through 6 steps to k = n/2 +/- sqrt(n^2/4 + m^3/27). Back-substitute to get t and u expressions, combine into x solution.
7. **DTPA: Translation theory** (360-450s): General cubic plotted with zero points. f''(x)=0 gives inflection point. Translation by -b/3a shifts plot to center inflection at y-axis. Eliminates b term.
8. **DTPA: Full general form** (450-500s): General cubic with translation substituted. Simplified to x^3+mx=n with m,n braces. Solution formula applied. Zero points on axes. Translation reversed to original equation.
