---
source: https://github.com/3b1b/videos/blob/main/_2018/div_curl.py
project: videos
domain: [calculus, electromagnetism, fluid_dynamics, physics]
elements: [vector_field, axes, arrow, dot, circle_node, label, equation, complex_plane, grid, pi_creature]
animations: [write, draw, transform, replacement_transform, fade_in, fade_out, lagged_start, passing_flash]
layouts: [centered, grid, side_by_side]
techniques: [custom_mobject, helper_function, add_updater, moving_camera]
purpose: [demonstration, exploration, definition, analogy]
mobjects: [VectorField, StreamLines, AnimatedStreamLines, ComplexPlane, Circle, Line, VGroup, OldTex, OldTexText, Dot, Arrow, Vector, DecimalNumber, Square]
manim_animations: [ShowCreation, ShowPassingFlash, FadeIn, FadeOut, Write, GrowArrow, ReplacementTransform, LaggedStartMap, UpdateFromFunc, UpdateFromAlphaFunc, Rotate]
scene_type: MovingCameraScene
manim_version: manimlib
complexity: advanced
lines: 4616
scene_classes: [Introduction, TestVectorField, CylinderModel, ShowDivergenceFormula, ShowCurlFormula, PredatorPreyFields]
---

## Summary

Visualizes divergence and curl of 2D vector fields using VectorField for static arrows and StreamLines/AnimatedStreamLines for dynamic flow. The introduction scene smoothly transitions between a divergence field (radial outflow) and a curl field (rotational flow) by transforming one VectorField into another. Includes the Joukowski map for aerodynamic cylinder flow, predator-prey systems, and electromagnetic force fields. Helper functions compute divergence and curl numerically via finite differences.

## Design Decisions

- **VectorField + StreamLines dual representation**: Static arrows show the field direction/magnitude at grid points. StreamLines (animated via ShowPassingFlash or AnimatedStreamLines) show how particles would flow. Together they give both instantaneous and trajectory understanding.
- **Transition between div and curl via ReplacementTransform**: The two concepts are introduced by morphing one vector field into another. The div field p/3 (radial) transforms into the curl field rotate(p/3, 90deg). The VectorField arrows smoothly rotate, making the conceptual difference visually concrete.
- **Numerical derivatives via finite differences**: divergence() and two_d_curl() compute partial derivatives with dt=1e-7. This makes any Python function differentiable for visualization purposes — no symbolic math needed.
- **Complex plane for cylinder flow**: The Joukowski map (z + 1/z) creates airfoil flow patterns from uniform flow. Using ComplexPlane with complex arithmetic enables elegant flow field definitions.
- **FOX_COLOR (#DF7F20) and RABBIT_COLOR (#C6D6EF)**: Custom predator-prey colors for ecological modeling scenes. The earthy orange fox and cool blue rabbit are intuitively associated with their roles.
- **JigglingSubmobjects for particle movement**: A VGroup updater that randomly oscillates each submobject, creating a "thermal" particle effect. Phase and direction are randomized per submobject.

## Composition

- **VectorField**: Default grid covering the screen. Arrows colored by magnitude.
- **StreamLines config**: delta_x=1/8, delta_y=1/8 for production quality (increase for faster dev). y_min=-8.5, y_max=8.5.
- **Introduction titles**: Scale=2, to_edge(UP), add_background_rectangle().
- **CylinderModel**: ComplexPlane with coordinates. Unit circle at center (fill=BLACK when closed). Contour lines via warped grid.
- **Charged particles**: Circle radius=0.1, stroke_width=0.5. Proton=RED with "+", Electron=BLUE with "-".
- **Force field**: get_force_field_func with inverse-cube law, radius=0.5 cutoff.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Divergence title | WHITE | Scale=2, background_rectangle |
| Curl title | WHITE | Scale=2, background_rectangle |
| Fox (predator) | #DF7F20 | FOX_COLOR custom hex |
| Rabbit (prey) | #C6D6EF | RABBIT_COLOR custom hex |
| Proton | RED | fill_opacity=0.8, "+" label |
| Electron | BLUE | fill_opacity=0.8, "-" label |
| Unit circle | YELLOW | CylinderModel |
| StreamLines | gradient | Colored by velocity magnitude |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| StreamLines flash | run_time=3 | ShowPassingFlash |
| VectorField transform | run_time=2 | ReplacementTransform between fields |
| AnimatedStreamLines | continuous | line_anim_class=ShowPassingFlash |
| Unit circle creation | run_time=5 | With DecimalNumber tracking |
| Flow application | run_time=15 | Full production AnimatedStreamLines |
| Joukowski map | run_time=5 | apply_complex_function |

## Patterns

### Pattern: Vector Field with Animated Stream Lines

**What**: VectorField creates a grid of arrows showing field direction/magnitude. StreamLines generates particle trajectories that can be animated with ShowPassingFlash (quick flash) or AnimatedStreamLines (continuous flow). The combination provides both static and dynamic views of the same field.

**When to use**: Any vector field visualization — fluid flow, electromagnetic fields, gradient fields, phase portraits. StreamLines are particularly effective for showing flow topology (sources, sinks, saddles, vortices).

```python
# Source: projects/videos/_2018/div_curl.py:188-244
class Introduction(MovingCameraScene):
    def construct(self):
        # Divergence field: radial outflow
        def div_func(p):
            return p / 3
        div_vector_field = VectorField(div_func)
        stream_lines = StreamLines(div_func,
            start_points_generator_config={"delta_x": 1./8, "delta_y": 1./8})
        stream_lines.shuffle()

        self.add(div_vector_field)
        self.play(LaggedStartMap(ShowPassingFlash, stream_lines), ...)

        # Curl field: rotational flow
        def curl_func(p):
            return rotate_vector(p / 3, 90 * DEGREES)
        curl_vector_field = VectorField(curl_func)
        self.play(ReplacementTransform(div_vector_field, curl_vector_field))
```

### Pattern: Numerical Divergence and Curl

**What**: Compute divergence and 2D curl of any Python vector function using finite differences (dt=1e-7). No symbolic computation needed. Returns scalar-valued functions suitable for coloring or labeling. The divergence sums partial derivatives; the 2D curl takes the cross-partial difference.

**When to use**: Any vector calculus visualization where you need to compute div or curl from an arbitrary function. Works with lambda functions, interpolated data, or complex transformations.

```python
# Source: projects/videos/_2018/div_curl.py:55-72
def divergence(vector_func, dt=1e-7):
    def result(point):
        value = vector_func(point)
        return sum([
            (vector_func(point + dt * RIGHT) - value)[i] / dt
            for i, vect in enumerate([RIGHT, UP, OUT])
        ])
    return result

def two_d_curl(vector_func, dt=1e-7):
    def result(point):
        value = vector_func(point)
        return op.add(
            (vector_func(point + dt * RIGHT) - value)[1] / dt,
            -(vector_func(point + dt * UP) - value)[0] / dt,
        )
    return result
```

### Pattern: Force Field from Point Charges

**What**: Creates an inverse-cube-law force field from a list of (center, strength) pairs. Positive strength = repulsion, negative = attraction. A radius parameter prevents singularity at the center by capping the force inside a small ball. Returns a function compatible with VectorField and StreamLines.

**When to use**: Electromagnetic field visualization, gravitational fields, any multi-source potential field. The strength parameter allows mixing sources and sinks.

```python
# Source: projects/videos/_2018/div_curl.py:100-117
def get_force_field_func(*point_strength_pairs, **kwargs):
    radius = kwargs.get("radius", 0.5)
    def func(point):
        result = np.array(ORIGIN)
        for center, strength in point_strength_pairs:
            to_center = center - point
            norm = get_norm(to_center)
            if norm < radius:
                to_center /= radius**3
            else:
                to_center /= norm**3
            to_center *= -strength
            result += to_center
        return result
    return func
```

## Scene Flow

1. **Introduction** (0-15s): Divergence VectorField (radial) with StreamLines flash. Title "Divergence" with background rect. Then transforms to curl field with title "Curl."
2. **Cylinder Flow Model** (15-60s): ComplexPlane with unit circle. Numbers labeled on plane. Contour lines appear. Joukowski map applied for airfoil flow. AnimatedStreamLines show flow around cylinder.
3. **Divergence Definition** (60-120s): Formal definition with partial derivatives. Color-coded regions show positive/negative divergence. Expanding/contracting rectangle demonstrations.
4. **Curl Definition** (120-180s): Curl formula shown. Paddle wheel analogy — a tiny paddle at each point would spin with angular velocity = curl. Animated demonstration.
5. **Predator-Prey** (180-240s): Lotka-Volterra equations as vector field. Fox and rabbit populations as axes. Orbital trajectories in phase space.
6. **Electromagnetic Fields** (240-300s): Proton and electron charges. Inverse-cube force field. StreamLines show field lines. Connection to Maxwell's equations.
