---
source: https://github.com/nipunramk/Reducible/blob/main/2021/Collision/collision.py
project: Reducible
domain: [computer_science, algorithms, physics, mechanics]
elements: [circle_node, box, dot, arrow, line, grid, label, surrounding_rect, code_block, tree]
animations: [fade_in, fade_out, write, draw, move, color_change, update_value, animate_parameter]
layouts: [centered, grid, side_by_side, hierarchy]
techniques: [custom_mobject, data_driven, zoomed_scene, progressive_disclosure]
purpose: [simulation, step_by_step, demonstration, comparison, process]
mobjects: [Circle, Rectangle, Dot, Arrow, Line, VGroup, Text, Tex, DecimalNumber, Square]
manim_animations: [FadeIn, FadeOut, Write, ShowCreation, Transform, GrowFromCenter, Rotate]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 5106
scene_classes: [Ball, Box, BouncingBall, ParticleSimulation, ParticleSimulationOptimized, LargeParticleSimulationOptimized250, AnimationIntro, FrameByFrame, FPS15Anim, ParticleInBox, ParticleInBoxDescription, UpdaterCode, TunnelingIssue, CCDLast, TwoParticleSim, TwoParticleDescription, IntroHandlingSeveralParticles, HundredParticleIssue, CollisionDetectionFramework, SortAndSweep, UniformGrid, KDTree, BVH]
---

## Summary

Comprehensive particle collision detection and response tutorial. Covers the full pipeline: frame-by-frame animation model, particle physics (position/velocity/acceleration updaters), elastic collision response using Wikipedia's formula, tunneling issues solved by continuous collision detection (CCD), and spatial partitioning for performance (sort-and-sweep, uniform grids, KD-trees, BVH). Features real-time simulations of 30-256 bouncing particles using Manim updaters.

## Design Decisions

- **Ball as Circle subclass**: Custom Ball class adds velocity vector, mass (proportional to area), and edge accessor methods. CONFIG dict pattern from manimlib. Mass = PI * radius^2 for physically realistic elastic collisions.
- **Box as Rectangle subclass**: Bounding container with edge accessors. Configurable height/width. GREEN_C or COBALT_BLUE stroke.
- **Updater-based physics**: `ball.add_updater(update_ball)` runs every frame. Each updater applies acceleration, integrates velocity, shifts position, and checks collisions. This is the core real-time simulation pattern.
- **Elastic collision formula**: Response velocities computed from Wikipedia's elastic collision equations using mass, velocity, and position vectors. Separated into `compute_velocity()` helper.
- **Sort-and-sweep broad phase**: Particles sorted by x-coordinate left edge. Sweep line maintains active list, only checking overlapping x-ranges for collisions. Reduces O(n^2) to near O(n log n).
- **Progressive simulation complexity**: Starts with 1 ball, then 2 (collision response), then 30 (naive), then 100 (optimized with sort-and-sweep), then 256 (full demo). Each step motivates the next optimization.
- **Frame decomposition visualization**: Shows 15 FPS vs 60 FPS ghost trail of a moving circle to explain discrete time steps.

## Composition

- **Box**: height=5.5-6, width=FRAME_WIDTH-1 or 5.5, centered or shifted RIGHT*4
- **Ball**: radius=0.04-0.2, positioned on grid with step spacing
- **Particle grid**: np.arange(-2.5, 2.5, step) for x and y positions
- **Physics vectors**: Arrow from ball center for velocity, Arrow from ball bottom for acceleration
- **Labels**: DecimalNumber for position/velocity values, scale 0.6
- **KD-tree visualization**: Recursive space partitioning with alternating horizontal/vertical Lines
- **BVH**: Bounding rectangles around particle groups in hierarchy

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Box boundary | GREEN_C or COBALT_BLUE | Rectangle stroke |
| Particles (default) | BLUE | Circle fill_opacity=1 |
| Multi-color particles | [BLUE, YELLOW, GREEN_SCREEN, ORANGE] | Cycling per ball |
| Large sim particles | [LIGHT_VIOLET, SEAFOAM_GREEN, PERIWINKLE_BLUE] | i%3 color cycling |
| Velocity arrow | BRIGHT_ORANGE | Arrow from ball center |
| Acceleration arrow | BLUE | Arrow from ball bottom |
| Position dot | YELLOW | Dot at ball center |
| Position label | YELLOW | DecimalNumber scale=0.6 |
| Velocity label | BRIGHT_ORANGE | DecimalNumber scale=0.6 |
| Acceleration label | BLUE | TexMobject scale=0.6 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Bouncing ball sim | 30s | self.wait(bouncing_time) |
| Particle sim (100) | 10s | simulation_time CONFIG |
| Large sim (256) | 120s | 2 minutes of real-time physics |
| Optimized sim (100) | 70s | With sort-and-sweep |
| Frame decomposition | ~4s | 15 FPS and 60 FPS ghost trails |
| Physics vector display | ~2s | Write arrows and labels |

## Patterns

### Pattern: Physics Updater with Collision Detection

**What**: Ball objects with velocity/acceleration updated every frame via `add_updater()`. Each frame: apply acceleration to velocity, shift ball by velocity*dt, check boundary collisions (reflect velocity component), check inter-particle collisions (elastic response). This creates real-time physics simulations.

**When to use**: Particle simulations, bouncing ball demos, physics demonstrations, any animation where objects move according to physical laws and interact with boundaries or each other.

```python
# Source: projects/Reducible/2021/Collision/collision.py:68-150
def update_ball(ball, dt):
    ball.acceleration = np.array((0, 0, 0))
    ball.velocity = ball.velocity + ball.acceleration * dt
    ball.shift(ball.velocity * dt)
    handle_collision_with_box(ball, box)
    handle_ball_collisions(ball)

def handle_collision_with_box(ball, box):
    if ball.get_bottom() <= box.get_bottom() * BOX_THRESHOLD or \
            ball.get_top() >= box.get_top() * BOX_THRESHOLD:
        ball.velocity[1] = -ball.velocity[1]
    if ball.get_left_edge() <= box.get_left_edge() or \
            ball.get_right_edge() >= box.get_right_edge():
        ball.velocity[0] = -ball.velocity[0]

def compute_velocity(v1, v2, m1, m2, x1, x2):
    return v1 - (2 * m2 / (m1 + m2)) * np.dot(v1 - v2, x1 - x2) / \
           np.linalg.norm(x1 - x2) ** 2 * (x1 - x2)

for ball in balls:
    ball.add_updater(update_ball)
```

### Pattern: Optimized VGroup Updater for Many Particles

**What**: Instead of per-ball updaters (O(n) updater calls per frame), wrap all particles in a VGroup and attach a single updater that iterates. This avoids Manim's overhead of managing hundreds of individual updaters.

**When to use**: Any simulation with 50+ independently moving objects. Critical for performance when particle count exceeds ~30.

```python
# Source: projects/Reducible/2021/Collision/collision.py:274-363
def update_particles(particles, dt):
    for i in range(len(particles)):
        particle = particles[i]
        particle.acceleration = np.array((0, 0, 0))
        particle.velocity = particle.velocity + particle.acceleration * dt
        particle.shift(particle.velocity * dt)
        handle_collision_with_box(particle, box, dt)
    handle_particle_collisions_opt(particles, dt)

particles = VGroup(*particles)
particles.add_updater(update_particles)
self.add(particles)
self.wait(self.simulation_time)
```

### Pattern: Sort-and-Sweep Broad Phase Collision

**What**: Sorts particles by their left x-coordinate, then sweeps through maintaining an active list. Only particles with overlapping x-ranges are checked for actual collision. Dramatically reduces collision checks from O(n^2) to near-linear for uniformly distributed particles.

**When to use**: Any simulation needing pairwise collision detection among many objects. Standard technique in game physics engines.

```python
# Source: projects/Reducible/2021/Collision/collision.py:322-337
def find_possible_collisions(particles):
    axis_list = sorted(particles, key=lambda x: x.get_left()[0])
    active_list = []
    possible_collisions = set()
    for particle in axis_list:
        to_remove = [p for p in active_list if particle.get_left()[0] > p.get_right()[0]]
        for r in to_remove:
            active_list.remove(r)
        for other_particle in active_list:
            possible_collisions.add((particle, other_particle))
        active_list.append(particle)
    return possible_collisions
```

### Pattern: Frame-by-Frame Ghost Trail Comparison

**What**: Shows a moving circle at different frame rates by creating transparent copies at each interpolated position. 15 FPS gets widely-spaced ghosts, 60 FPS gets dense ghosts. Both trails visible simultaneously to compare temporal resolution.

**When to use**: Explaining frame rate concepts, animation smoothness, temporal aliasing, any educational content about discrete time steps in simulation or animation.

```python
# Source: projects/Reducible/2021/Collision/collision.py:536-665
frame_circle = circle.copy()
frame_circle.set_stroke(opacity=0.1).set_fill(opacity=0.1)
FPS = self.camera.frame_rate
interp = smooth
for i in range(FPS + 1):
    t = 1 / FPS * i
    position = (1 - interp(t)) * start + interp(t) * end
    frames.append(frame_circle.copy().move_to(position + DOWN * 1.5))
# 15 FPS version with wider spacing
for i in range(16):
    t = 1 / 15 * i
    position = (1 - interp(t)) * start_15 + interp(t) * end_15
    frames_15.append(frame_circle.copy().move_to(position + UP * 1.5))
```

## Scene Flow

1. **Animation Basics** (0-4min): Frame-by-frame perspective. 15 FPS vs 60 FPS ghost trails. Smooth interpolation.
2. **Single Particle** (4-8min): Ball in box with gravity. Show position, velocity, acceleration vectors with live-updating labels. Updater code explanation.
3. **Tunneling Issue** (8-12min): Fast particles pass through walls. CCD (continuous collision detection) as solution. ZoomedScene for detail.
4. **Two Particle Collision** (12-18min): Elastic collision response formula. Vector decomposition. Debug visualization.
5. **Many Particles** (18-22min): 100-particle simulation. O(n^2) problem. Sort-and-sweep optimization.
6. **Spatial Partitioning** (22-30min): Uniform grid, KD-tree, BVH (bounding volume hierarchy). Framework comparison.

> Note: Uses manimlib (not Community Edition). CONFIG dict pattern, TextMobject, ShowCreation.
