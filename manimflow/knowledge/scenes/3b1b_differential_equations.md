---
source: https://github.com/3b1b/videos/blob/main/_2019/diffyq/part1/pendulum.py
project: videos
domain: [differential_equations, physics, mechanics, calculus]
elements: [axes, function_plot, parametric_curve, vector, dot, dashed_line, arrow, label, equation, number_line, coordinate_system, circle_node]
animations: [write, draw, transform, fade_in, fade_out, rotate, animate_parameter, update_value, trace_path]
layouts: [centered, side_by_side, grid]
techniques: [value_tracker, always_redraw, add_updater, custom_mobject, progressive_disclosure, helper_function, moving_camera]
purpose: [simulation, step_by_step, exploration, derivation]
mobjects: [Pendulum, ThetaVsTAxes, GravityVector, Axes, NumberPlane, VGroup, OldTex, OldTexText, Line, DashedLine, Arc, Dot, Vector, Circle, VMobject, Rectangle, VectorizedPoint]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write, GrowFromPoint, ShowCreationThenFadeAround, ShowCreationThenFadeOut, UpdateFromFunc, Rotating, ApplyMethod, ShowIncreasingSubsets, TransformFromCopy, LaggedStart, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 3936
scene_classes: [Pendulum, IntroducePendulum, VisualizeStates, ThetaVsTAxes, GravityVector]
---

## Summary

Visualizes the differential equation of a pendulum through a custom Pendulum mobject that simulates gravity via Euler integration, a ThetaVsTAxes that draws theta(t) live as the pendulum swings, and a phase space visualization (VisualizeStates) that collapses a grid of pendulum states into dots on a theta-vs-omega plane. The Pendulum class handles rod, weight, angle arc, theta label, and velocity vector — all auto-updating via always_redraw. Phase space trajectories are traced in real-time by tying dot position to pendulum state.

## Design Decisions

- **Pendulum as self-contained physics Mobject**: The Pendulum VGroup contains rod (Line), weight (Circle), dashed_line (rest position), angle_arc, theta_label, and velocity_vector. All are created with always_redraw so they track the pendulum state. The physics (start_swinging/end_swinging) is an updater that can be toggled.
- **Euler integration with sub-stepping**: update_by_gravity uses n_steps_per_frame=100 sub-steps per frame to maintain numerical stability. Each sub-step computes d_theta=omega*dt/nspf and d_omega=(-damping*omega - g/L*sin(theta))*dt/nspf.
- **Grid-of-states to phase-space collapse**: A grid of small pendulums (each with different initial theta and omega) is shown running simultaneously, then collapsed into dots on a NumberPlane where x=theta, y=omega. This physically demonstrates what "phase space" means.
- **Live-drawn graph**: ThetaVsTAxes.get_live_drawn_graph creates a VMobject that extends in real-time as the pendulum swings, using an updater that appends new (time, theta) coordinates at each frame.
- **GravityVector with component decomposition**: A Vector attached to the pendulum weight, with dashed component lines showing tangential and radial decomposition that update via always_redraw.
- **Rod with sheen**: The rod uses sheen_direction=UP, sheen_factor=1 for a metallic look. Weight uses sheen_direction=UL for 3D feel on a 2D object.

## Composition

- **Pendulum**: length=3 default, weight_diameter=0.5. Rod: Line(UP, DOWN), GREY_B stroke_width=3. Weight: Circle, GREY_BROWN fill. Top point at 2*UP.
- **Angle arc**: radius=1, stroke_width=2, WHITE. From -90deg to theta.
- **Theta label**: OldTex("\\theta"), height=0.25. Positioned midway along arc, nudged outward.
- **Velocity vector**: RED, tangent to swing direction. Length clipped to max_velocity_vector_length_to_length_ratio=0.5 of rod length.
- **ThetaVsTAxes**: x_min=0, x_max=8 (time). y_min=-PI/2, y_max=PI/2. y_axis tick_frequency=PI/8, unit_size=1.5. Graph: GREEN stroke_width=3.
- **Phase space plane**: NumberPlane with y_line_frequency=PI/2. Theta axis with pi-labeled ticks. Omega axis with numeric labels.
- **State grid**: n_thetas=11, n_omegas=7 pendulums in Rectangle cells (height=3, width=3). Total grid fills FRAME_HEIGHT.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Rod | GREY_B | stroke_width=3, sheen_factor=1, sheen_direction=UP |
| Weight | GREY_BROWN | fill_opacity=1, sheen_factor=0.5, background_stroke: BLACK, width=3 |
| Dashed rest line | WHITE | stroke_width=2, num_dashes=25 |
| Angle arc | WHITE | stroke_width=2 |
| Velocity vector | RED | velocity_vector_config |
| Gravity vector | YELLOW | GravityVector color |
| Theta(t) graph | GREEN | stroke_width=3 |
| State dots | YELLOW | radius=0.05, background_stroke: BLACK, width=3 |
| Phase plane axis labels | YELLOW | omega (dot-theta) label |
| State grid cells | GREY_E | fill_opacity=1, stroke: WHITE, width=2 |
| Trajectory | varies | Traced path during evolution |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Pendulum swinging | continuous | Updater, n_steps_per_frame=100 |
| Live graph drawing | continuous | Frame-by-frame point addition |
| Grid display | 15s | initial_grid_wait_time |
| Grid creation | run_time=2 | ShowIncreasingSubsets per row |
| Grid collapse to dots | run_time=4 | LaggedStart TransformFromCopy |
| State dot trajectory | 20+ seconds | Continuous trace |
| Dot manual movement | run_time=1.5 per shift | Exploring phase space |

## Patterns

### Pattern: Self-Simulating Pendulum Mobject

**What**: A VGroup containing rod, weight, angle arc, theta label, and velocity vector. Physics is toggled via start_swinging() (adds gravity updater) and end_swinging() (removes it). The updater uses Euler integration with 100 sub-steps per frame. All visual elements use always_redraw to track the current theta and omega.

**When to use**: Any physical system simulation embedded as a Manim mobject — spring-mass, double pendulum, projectile, orbital mechanics. The pattern of separating visual construction (always_redraw) from physics (togglable updater) is broadly reusable.

```python
# Source: projects/videos/_2019/diffyq/part1/pendulum.py:5-198
class Pendulum(VGroup):
    CONFIG = {"length": 3, "gravity": 9.8, "damping": 0.1, "n_steps_per_frame": 100}

    def create_angle_arc(self):
        self.angle_arc = always_redraw(lambda: Arc(
            arc_center=self.get_fixed_point(),
            start_angle=-90 * DEGREES,
            angle=self.get_theta(),
        ))

    def start_swinging(self):
        self.add_updater(Pendulum.update_by_gravity)

    def update_by_gravity(self, dt):
        theta, omega = self.get_theta(), self.get_omega()
        for x in range(self.n_steps_per_frame):
            d_theta = omega * dt / self.n_steps_per_frame
            d_omega = (-self.damping * omega - (self.gravity / self.length) * np.sin(theta)) * dt / self.n_steps_per_frame
            theta += d_theta
            omega += d_omega
        self.set_theta(theta)
        self.set_omega(omega)
```

### Pattern: Live-Drawn Graph Tracking a Simulation

**What**: A VMobject that extends in real-time as a simulation runs. An updater appends (time, value) coordinates at each frame, then regenerates the path via set_points_smoothly. The graph has a configurable t_step for point density and self-removes the updater when t_max is reached.

**When to use**: Real-time plotting during any simulation — pendulum theta(t), population dynamics, stock price, any time series generated frame-by-frame.

```python
# Source: projects/videos/_2019/diffyq/part1/pendulum.py:322-353
def get_live_drawn_graph(self, pendulum, t_max=None, t_step=1./60, **style):
    graph = VMobject()
    graph.set_style(**style)
    graph.all_coords = [(0, pendulum.get_theta())]
    graph.time = 0

    def update_graph(graph, dt):
        graph.time += dt
        if graph.time > t_max:
            graph.remove_updater(update_graph)
            return
        new_coords = (graph.time, pendulum.get_theta())
        if graph.time - graph.time_of_last_addition >= t_step:
            graph.all_coords.append(new_coords)
        points = [self.coords_to_point(*c) for c in [*graph.all_coords, new_coords]]
        graph.set_points_smoothly(points)

    graph.add_updater(update_graph)
    return graph
```

### Pattern: Grid-of-States to Phase-Space Collapse

**What**: A grid of small pendulums (each initialized with different theta and omega) runs simultaneously. Then each pendulum's state (theta, omega) is mapped to a dot on a NumberPlane, and the grid cells are TransformFromCopy'd into the dots. This physically demonstrates the abstraction of phase space — each configuration corresponds to a point.

**When to use**: Introducing phase space for any dynamical system. The grid-to-dots collapse makes the abstraction concrete. Useful for oscillators, population models, or any system with 2+ state variables.

```python
# Source: projects/videos/_2019/diffyq/part1/phase_space.py:218-252
def collapse_grid_into_points(self):
    dots = VGroup()
    for row in self.state_grid:
        for state in row:
            dot = Dot(
                self.get_state_point(state.pendulum),
                radius=0.05, color=YELLOW,
                background_stroke_width=3, background_stroke_color=BLACK,
            )
            dots.add(dot)
    self.play(
        ShowCreation(plane),
        LaggedStart(*[TransformFromCopy(m1, m2) for m1, m2 in zip(flat_state_group, flat_dot_group)],
                    lag_ratio=0.1, run_time=4)
    )
```

## Scene Flow

1. **Pendulum Introduction** (0-30s): Pendulum appears at top_point=4*RIGHT. Theta label and arc shown. Velocity vector appears as RED arrow tangent to motion. Pi creatures watch.
2. **Theta vs Time Graph** (30-60s): ThetaVsTAxes to the left. Pendulum starts swinging. Graph draws live in GREEN, showing damped oscillation. Period and amplitude visible.
3. **State Grid** (60-90s): 11x7 grid of small pendulums with different initial conditions fills the screen. All swing simultaneously for 15 seconds. Dramatic visual of diverse trajectories.
4. **Phase Space Collapse** (90-120s): NumberPlane appears. Grid cells collapse into YELLOW dots via LaggedStart TransformFromCopy. Each dot represents one (theta, omega) state.
5. **State Evolution** (120-180s): A single state dot is controlled interactively. Horizontal/vertical lines track theta and omega axes. The dot traces a trajectory in phase space as the pendulum swings. Abstract (phase space) vs physical (pendulum) views shown side by side.
6. **ODE Connection** (180-210s): The differential equation shown. Acceleration depends on angle. The vector field in phase space encodes the ODE — every point has a direction.
