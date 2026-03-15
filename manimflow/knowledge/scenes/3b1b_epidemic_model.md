---
source: https://github.com/3b1b/videos/blob/main/_2020/sir.py
project: videos
domain: [epidemiology, probability, statistics, biology]
elements: [dot, circle_node, axes, function_plot, surrounding_rect, label, grid, pi_creature]
animations: [animate_parameter, update_value, fade_in, fade_out, color_change, move]
layouts: [grid, side_by_side, centered]
techniques: [add_updater, custom_mobject, data_driven, value_tracker, simulation]
purpose: [simulation, exploration, comparison, progression]
mobjects: [VGroup, Dot, Circle, Square, Axes, VMobject, SVGMobject, Line, VectorizedPoint]
manim_animations: [UpdateFromAlphaFunc, Transform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 3358
scene_classes: [Person, DotPerson, PiPerson, SIRSimulation, SIRGraph]
---

## Summary

Implements a full agent-based SIR (Susceptible-Infected-Recovered) epidemic simulation as Manim mobjects. Each Person is a VGroup with physics (velocity, gravity wells, wall bouncing, social distancing via repulsion forces), infection mechanics (radius-based transmission, infection timer, symptomatic status), and visual state (color transitions S=BLUE, I=RED, R=GREY_D). The SIRSimulation manages populations in bounded boxes with real-time infection spreading, and SIRGraph plots cumulative S/I/R proportions as stacked area charts that update live. PiPerson variant uses Randolph with mode changes for emotional reactions to infection.

## Design Decisions

- **Agent-based simulation as Mobject tree**: Each Person is a self-contained VGroup with updaters for position, infection ring animation, and state transitions. This means the simulation runs via Manim's standard animation loop — no external simulation needed.
- **Color = status**: S=BLUE (healthy), I=RED (infected), R=GREY_D (recovered). The color transition is animated via UpdateFromAlphaFunc with interpolate_color, creating a smooth shift rather than an abrupt change.
- **Infection ring pulse**: An expanding circle pulses from body radius to infection_radius with period=2s. stroke_width oscillates via there_and_back, creating a visual "danger zone" around infected individuals.
- **Physics-based movement**: Each person has velocity, gravity wells (wander targets), wall bouncing (velocity reflection at boundaries), and optional social distance repulsion (inverse-cube force from neighbors). This creates realistic crowd dynamics.
- **Bounded boxes**: Populations live in Square containers. Multiple boxes enable travel-between-cities simulation via path_along_arc transfers.
- **SIRGraph as stacked area chart**: Three filled VMobjects (S, I, R regions) stacked vertically using cumulative proportions. Updates every 0.5s by appending new data points and regenerating the polygons.

## Composition

- **Person**: height=0.2 (tiny). SVGMobject body + infection_ring Circle. Infection radius=0.5 (from center).
- **SIRSimulation box**: Square side_length=7, stroke=WHITE width=3. Population 100 per box.
- **SIRGraph**: Axes with y_min=0, y_max=1, x_min=0, x_max=1. height=7, width=5. Stacked areas for S (top), I (middle), R (bottom).
- **Person position**: Random initial position within box bounds. Wall buffer=1 for repulsion zone.
- **Social distance visualization**: Body stroke in YELLOW, width proportional to nearest-neighbor proximity.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Susceptible (S) | BLUE | Person body fill |
| Infected (I) | RED | Person body fill, infection_ring stroke |
| Recovered (R) | GREY_D | Person body fill |
| Infection ring | RED | stroke_opacity=0.8, pulsing stroke_width 0-5 |
| Asymptomatic | YELLOW | Alternative infection ring + body color |
| Social distance stroke | YELLOW | Background stroke, width proportional to proximity |
| Box boundary | WHITE | stroke_width=3 |
| SIR graph S region | BLUE | Filled area |
| SIR graph I region | RED | Filled area |
| SIR graph R region | GREY_D | Filled area |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Infection color transition | run_time=1 | UpdateFromAlphaFunc with interpolate_color |
| Infection ring pulse | period=2s | Continuous, smooth alpha |
| Graph update | every 0.5s | update_frequency config |
| Simulation step | per frame | Physics + infection check per dt |
| Travel transfer | run_time=1 | path_along_arc(45*DEGREES) |
| Full simulation | 30-60s typical | Until most recover |

## Patterns

### Pattern: Agent-Based Simulation as Mobject

**What**: Each agent (Person) is a VGroup with multiple updaters: position physics (gravity + repulsion + wall bouncing), infection mechanics (proximity-based transmission), and visual state (color interpolation, ring animation). The simulation container (SIRSimulation) manages inter-agent interactions in its own updater. Everything runs inside Manim's animation loop — no external engine needed.

**When to use**: Any particle simulation, crowd dynamics, cellular automata, predator-prey, or agent-based model. The pattern of encoding simulation state in Mobject properties and using updaters for dynamics is broadly applicable.

```python
# Source: projects/videos/_2020/sir.py:16-68
class Person(VGroup):
    CONFIG = {
        "status": "S", "height": 0.2,
        "color_map": {"S": BLUE, "I": RED, "R": GREY_D},
        "infection_radius": 0.5, "max_speed": 1,
        "social_distance_factor": 0,
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = np.zeros(3)
        self.add_updater(update_time)
        self.add_updater(lambda m, dt: m.update_position(dt))
        self.add_updater(lambda m, dt: m.update_infection_ring(dt))
        self.add_updater(lambda m: m.progress_through_change_anims())
```

### Pattern: Smooth State Transition with Color Interpolation

**What**: When a Person changes status (S->I, I->R), the body color smoothly transitions via UpdateFromAlphaFunc + interpolate_color. The animation is pushed to a queue (change_anims) and progressed by the Person's own updater, allowing state changes to happen asynchronously during the simulation.

**When to use**: Any simulation where agents change state and the transition should be visually smooth. Useful for status indicators, health systems, traffic light changes, or any multi-state system.

```python
# Source: projects/videos/_2020/sir.py:81-116
def set_status(self, status, run_time=1):
    start_color = self.color_map[self.status]
    end_color = self.color_map[status]
    anims = [UpdateFromAlphaFunc(
        self.body,
        lambda m, a: m.set_color(interpolate_color(start_color, end_color, a)),
        run_time=run_time,
    )]
    for anim in anims:
        self.push_anim(anim)
    self.status = status

def progress_through_change_anims(self):
    for anim in self.change_anims:
        alpha = (self.time - anim.start_time) / anim.run_time
        anim.interpolate(alpha)
        if alpha >= 1:
            self.pop_anim(anim)
```

### Pattern: Live-Updating Stacked Area Chart (SIRGraph)

**What**: A VGroup containing Axes and three filled VMobjects representing cumulative S, I, R proportions. Updates every update_frequency seconds by appending simulation.get_status_proportions() to its data array and regenerating the polygon points. Each region is computed as a cumulative stack so they fill the full y-axis.

**When to use**: Any time-series visualization of proportions that must update in real-time during a simulation. Useful for population dynamics, market share, resource allocation, or any partition-of-unity over time.

```python
# Source: projects/videos/_2020/sir.py:422-500
class SIRGraph(VGroup):
    CONFIG = {"color_map": COLOR_MAP, "height": 7, "width": 5, "update_frequency": 0.5}

    def __init__(self, simulation, **kwargs):
        super().__init__(**kwargs)
        self.data = [simulation.get_status_proportions()] * 2
        self.add_axes()
        self.add_graph()
        self.add_updater(lambda m: m.update_graph())

    def get_graph(self, data):
        # Build stacked polygon points for S, I, R regions
        for x, props in zip(np.linspace(0, 1, len(data)), data):
            i_point = axes.c2p(x, props[1])
            s_point = axes.c2p(x, sum(props[:2]))
        # Create closed polygons for each region
```

## Scene Flow

1. **Simulation Setup**: Square box appears. 100 Person dots populate it randomly. One turns RED (patient zero). All start wandering.
2. **Infection Spread** (0-20s): Red infection rings pulse. When susceptible (BLUE) enters radius of infected (RED), probability-based transmission occurs. Smooth BLUE->RED color transition.
3. **Recovery Phase** (20-40s): After infection_time=5s, RED persons turn GREY_D (recovered). The population gradually shifts from BLUE to RED to GREY.
4. **SIR Curve** (concurrent): SIRGraph to the side shows stacked area chart updating live. The I curve rises then falls. S decreases monotonically. R increases monotonically.
5. **Parameter Exploration**: Social distancing (repulsion force) turns on — YELLOW stroke appears on bodies. Infection rate drops visibly. Travel between boxes introduces new dynamics.
