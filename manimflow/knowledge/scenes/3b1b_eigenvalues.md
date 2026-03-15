---
source: https://github.com/3b1b/videos/blob/main/_2024/linalg/eigenlecture.py
project: videos
domain: [linear_algebra, differential_equations, mathematics]
elements: [axes, vector, vector_field, label, equation, matrix, number_line, coordinate_system]
animations: [write, transform, fade_in, fade_out, animate_parameter]
layouts: [centered, side_by_side]
techniques: [value_tracker, add_updater, scipy_integration, data_driven]
purpose: [demonstration, derivation, exploration, step_by_step]
mobjects: [NumberPlane, VectorField, StreamLines, AnimatedStreamLines, Vector, VGroup, Tex, Line]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write]
scene_type: InteractiveScene
manim_version: manimlib
complexity: intermediate
lines: 370
scene_classes: [TexScratchPad, VectorFieldSolution, Transformation]
---

## Summary

Visualizes eigenvalues and eigenvectors through two complementary approaches: a vector field showing the flow of a linear ODE system dx/dt = Ax with animated streamlines, and a direct matrix transformation that stretches/rotates the coordinate plane. Eigenlines (lines through the origin along eigenvectors) are highlighted in TEAL to show which directions are merely scaled (not rotated) by the transformation. The Fibonacci connection is explored via the matrix [[0,1],[1,1]] and its eigendecomposition.

## Design Decisions

- **Vector field + streamlines**: The matrix A = [[1,2],[3,1]] defines a linear ODE. VectorField shows instantaneous directions, AnimatedStreamLines show the flow over time. Together they make the dynamics viscerally visible.
- **Eigenlines as TEAL lines through origin**: After the flow is established, lines along eigenvectors are drawn. These are the only lines where flow is purely outward/inward, not rotating. The contrast with the swirling nearby flow makes eigenvalues click.
- **Ghost plane for transformation**: A grey ghost plane stays fixed while the main colored plane deforms under A. The viewer can see how the transformation distorts space by comparing to the static reference.
- **Eigenbasis transformation**: Same matrix applied to a plane aligned with eigenvectors (TEAL and YELLOW). The transformation becomes pure scaling along these axes — the diagonal matrix visible physically.
- **Color-coded basis vectors**: Standard basis i-hat=GREEN, j-hat=RED. Eigenbasis v1=TEAL, v2=YELLOW. Same colors used in all TeX expressions throughout.

## Composition

- **Vector field scene**: NumberPlane fills FRAME_HEIGHT, range (-4,4)x(-2,2). Background lines BLUE width=1, faded BLUE width=0.5 opacity=0.5. Coordinate labels font_size=36.
- **Eigenlines**: Line(-v, v).set_length(10) for each eigenvector. TEAL stroke_width=5.
- **Transformation scene**: ghost_plane with GREY stroke_width=1. Main plane default coloring. Basis vectors use get_updated_vector with updaters to track coord_system.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Standard basis i-hat | GREEN | Vector thickness=4 |
| Standard basis j-hat | RED | Vector thickness=4 |
| Eigenvector v1 | TEAL | In Tex and vector |
| Eigenvector v2 | YELLOW | In Tex and vector |
| Eigenvalues lambda_1 | TEAL | In all Tex t2c maps |
| Eigenvalues lambda_2 | YELLOW | In all Tex t2c maps |
| Vector field | default | stroke_opacity=0.5 |
| Streamlines | WHITE | width=3, opacity=1.0 |
| Eigenlines | TEAL | stroke_width=5 |
| Ghost plane | GREY | stroke_width=1 |
| Background lines | BLUE | width=1 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Vector field appearance | instant | Added, then opacity animated |
| Streamlines flow | 10s wait | AnimatedStreamLines continuous |
| Eigenline reveal | ShowCreation | After 10s of flow |
| Matrix transformation | run_time=4 | plane.animate.apply_matrix(mat) |
| Post-eigenline wait | 10s | Watch flow along eigenlines |

## Patterns

### Pattern: Vector Field with Animated Streamlines

**What**: A VectorField shows arrows at grid points, while AnimatedStreamLines overlay flowing curves that trace the ODE solution. The vector field fades to 50% opacity so streamlines are prominent. The combined view shows both instantaneous direction and long-term dynamics.

**When to use**: ODE phase portraits, dynamical systems, fluid flow visualization, any vector field where you want to show both local direction and global flow structure.

```python
# Source: projects/videos/_2024/linalg/eigenlecture.py:239-281
def func(v):
    return 0.5 * np.dot(v, mat.T)

vector_field = VectorField(func, axes, density=4,
    stroke_width=5, stroke_opacity=0.5)
stream_lines = StreamLines(func, axes, density=5,
    n_samples_per_line=10, solution_time=1,
    color_by_magnitude=False, stroke_color=WHITE,
    stroke_width=3, stroke_opacity=1.0)
animated_lines = AnimatedStreamLines(stream_lines,
    line_anim_config=dict(time_width=0.5), rate_multiple=0.25)

self.add(vector_field, animated_lines)
self.play(vector_field.animate.set_stroke(opacity=0.5))
self.wait(10)
self.play(ShowCreation(eigenlines))
```

### Pattern: Updated Vector Tracking Coordinate System

**What**: A Vector with an updater that always points from the origin of a coordinate system to a specific coordinate point. When the coordinate system is deformed (apply_matrix), the vector follows — visually showing how basis vectors transform.

**When to use**: Linear transformation visualization, basis change, coordinate system animation, any transformation where you want vectors to track the deforming space.

```python
# Source: projects/videos/_2024/linalg/eigenlecture.py:364-370
def get_updated_vector(self, coords, coord_system, color=YELLOW, thickness=4):
    vect = Vector(RIGHT, fill_color=color, thickness=thickness)
    vect.add_updater(lambda m: m.put_start_and_end_on(
        coord_system.get_origin(),
        coord_system.c2p(*coords),
    ))
    return vect

# Usage: basis vectors that follow the plane
basis = VGroup(
    self.get_updated_vector((1, 0), plane, GREEN),
    self.get_updated_vector((0, 1), plane, RED),
)
self.play(plane.animate.apply_matrix(mat), run_time=4)
```

## Scene Flow

1. **Vector field** (0-10s): NumberPlane with coordinate labels. Vector field arrows appear. Streamlines begin flowing.
2. **Eigenlines reveal** (10-15s): TEAL lines along eigenvectors drawn. Flow clearly follows these lines without rotation.
3. **Standard transformation** (15-25s): Ghost plane stays fixed. Main plane deforms under A=[[1,2],[3,1]]. Green i-hat and red j-hat stretch and rotate. FadeOut.
4. **Eigenbasis transformation** (25-35s): Plane aligned with eigenvectors. TEAL v1 and YELLOW v2 as basis. Same matrix applied — vectors only scale, no rotation. The physical meaning of diagonalization.
