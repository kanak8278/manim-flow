---
source: https://github.com/3b1b/videos/blob/main/_2024/manim_demo/lorenz.py
project: videos
domain: [differential_equations, physics, mathematics]
elements: [axes, parametric_curve, dot, label, equation]
animations: [write, draw, trace_path, camera_rotate]
layouts: [centered]
techniques: [three_d_camera, scipy_integration, data_driven, add_updater, color_gradient]
purpose: [simulation, exploration, demonstration]
mobjects: [ThreeDAxes, VMobject, GlowDot, VGroup, Tex, TracingTail]
manim_animations: [ShowCreation, Write]
scene_type: InteractiveScene
manim_version: manimlib
complexity: intermediate
lines: 114
scene_classes: [LorenzAttractor, EndScreen]
---

## Summary

Visualizes the Lorenz attractor with multiple trajectories starting from nearly identical initial conditions (epsilon=1e-5 apart), demonstrating sensitive dependence on initial conditions (chaos). Uses scipy.integrate.solve_ivp to compute 30-second ODE solutions, then animates GlowDots moving along these trajectories with TracingTail for fading colored trails. The 3D camera rotates continuously at 3 degrees/second. Equations are fixed in frame at the upper-left corner.

## Design Decisions

- **Multiple nearby initial conditions**: 10 trajectories starting at (10, 10, 10+n*epsilon) with epsilon=1e-5. They start indistinguishable and dramatically diverge — the essence of chaos becomes visually obvious without explanation.
- **Color gradient BLUE_E to BLUE_A**: Nearby trajectories get similar blues, so the initial cluster is coherent and the divergence is visible as colors separate.
- **GlowDot + TracingTail**: GlowDots (radius=0.25) show current position with a soft halo. TracingTail (time_traced=3) leaves a fading trail matching the dot's color. This creates the classic attractor wing pattern.
- **Continuous camera rotation**: frame.add_updater rotating at 3 DEG/second. Keeps the 3D structure visible and prevents flat-looking views. Starting orientation (43, 76, 1) gives a slightly tilted perspective.
- **Equations fixed in frame**: Lorenz equations in upper-left, fix_in_frame() ensures they stay on screen during camera rotation. Backstroke for readability against the dark trajectories.
- **Linear rate_func for ShowCreation**: Trajectories are revealed at constant speed (not ease-in-out), matching the constant dt of the ODE solver. The dots appear to "trace" the curves in real time.

## Composition

- **ThreeDAxes**: x_range=(-50,50,5), y_range=(-50,50,5), z_range=(0,50,5). Width=height=16, depth=8. Set to FRAME_WIDTH and centered.
- **Camera**: Initial orientation (43, 76, 1), center at IN. Continuous rotation at 3 DEG/sec.
- **Equations**: Tex with t2c {x: RED, y: GREEN, z: BLUE}, font_size=30. fix_in_frame(), to_corner(UL), backstroke.
- **Curves**: VMobject.set_points_smoothly from scipy solution points mapped through axes.c2p.
- **Dots**: GlowDot radius=0.25, color from BLUE_E->BLUE_A gradient. 10 dots total.
- **Tails**: TracingTail per dot, time_traced=3, color matched.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Trajectories | BLUE_E to BLUE_A | Gradient across 10 curves |
| Dots | matched gradient | GlowDot radius=0.25 |
| Tails | matched gradient | TracingTail time_traced=3 |
| Equation x | RED | In Tex t2c |
| Equation y | GREEN | In Tex t2c |
| Equation z | BLUE | In Tex t2c |
| Curve stroke | matched | width=2, opacity=1 (initial 0) |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Equation write | default | Write(equations) |
| Trajectory reveal | run_time=30 | ShowCreation, rate_func=linear |
| Camera rotation | continuous | 3 DEG/second |
| Total video | ~32s | Equation + 30s evolution |

## Patterns

### Pattern: ODE Solution to Animated 3D Curve

**What**: Use scipy.integrate.solve_ivp to compute an ODE solution, convert the result points to screen coordinates via axes.c2p, and create a VMobject with set_points_smoothly. Animate with ShowCreation at linear rate for real-time playback. GlowDots with updaters track curve endpoints, and TracingTail leaves fading trails.

**When to use**: Any dynamical system visualization — Lorenz, double pendulum, three-body problem, Rossler attractor, any ODE where you want to show trajectories evolving over time.

```python
# Source: projects/videos/_2024/manim_demo/lorenz.py:5-111
def lorenz_system(t, state, sigma=10, rho=28, beta=8/3):
    x, y, z = state
    return [sigma*(y-x), x*(rho-z)-y, x*y-beta*z]

def ode_solution_points(function, state0, time, dt=0.01):
    solution = solve_ivp(function, t_span=(0, time), y0=state0,
                         t_eval=np.arange(0, time, dt))
    return solution.y.T

# Compute curves
states = [[10, 10, 10 + n * 1e-5] for n in range(10)]
colors = color_gradient([BLUE_E, BLUE_A], len(states))
curves = VGroup()
for state, color in zip(states, colors):
    points = ode_solution_points(lorenz_system, state, 30)
    curve = VMobject().set_points_smoothly(axes.c2p(*points.T))
    curve.set_stroke(color, 2, opacity=1)
    curves.add(curve)

# Dots tracking curve ends with tails
dots = Group(GlowDot(color=color, radius=0.25) for color in colors)
dots.add_updater(lambda d: [dot.move_to(c.get_end()) for dot, c in zip(d, curves)])
tail = VGroup(TracingTail(dot, time_traced=3).match_color(dot) for dot in dots)

# Animate all curves simultaneously
self.play(*(ShowCreation(c, rate_func=linear) for c in curves), run_time=30)
```

### Pattern: Fixed-in-Frame Equations with 3D Camera

**What**: Mathematical equations displayed in the corner of the screen using fix_in_frame() so they remain stationary while the 3D camera rotates. set_backstroke() ensures readability against any background. Color-coded variables match the visualization.

**When to use**: Any 3D scene that needs persistent mathematical notation — equations, labels, legends that should not rotate with the camera.

```python
# Source: projects/videos/_2024/manim_demo/lorenz.py:49-67
equations = Tex(R"""
    \begin{aligned}
    \frac{\mathrm{d} x}{\mathrm{~d} t} &= \sigma(y-x) \\
    \frac{\mathrm{d} y}{\mathrm{~d} t} &= x(\rho-z)-y \\
    \frac{\mathrm{d} z}{\mathrm{~d} t} &= xy-\beta z
    \end{aligned}
""", t2c={"x": RED, "y": GREEN, "z": BLUE}, font_size=30)
equations.fix_in_frame()
equations.to_corner(UL)
equations.set_backstroke()
```

## Scene Flow

1. **Setup** (0-2s): ThreeDAxes appear. Camera at (43, 76, 1) with continuous rotation. Lorenz equations write in upper-left.
2. **Evolution** (2-32s): 10 curves simultaneously revealed via ShowCreation at linear rate. GlowDots move along endpoints. TracingTails leave fading trails. Initially, all trajectories overlap. Around t=15s, they begin to separate. By t=25s, they are fully diverged across the two wings of the attractor.
