---
source: https://github.com/3b1b/videos/blob/main/_2025/grover/state_vectors.py
project: videos
domain: [quantum_mechanics, computer_science, algorithms, linear_algebra]
elements: [vector, sphere, grid, label, equation, surrounding_rect, dot, line, arrow, circle_node]
animations: [fade_in, fade_out, write, transform, replacement_transform, transform_from_copy, grow, rotate, camera_rotate, indicate, flash, lagged_start]
layouts: [side_by_side, centered, vertical_stack, grid]
techniques: [value_tracker, three_d_camera, ambient_camera_rotation, custom_mobject, custom_animation, progressive_disclosure]
purpose: [demonstration, comparison, step_by_step, exploration]
mobjects: [VGroup, Group, Vector, Sphere, SurfaceMesh, NumberPlane, ThreeDAxes, Integer, Tex, TexText, Text, Randolph, Mortimer, Square, Line, SurroundingRectangle, GlowDot, DotCloud, Rectangle]
manim_animations: [FadeIn, FadeOut, FadeTransform, TransformFromCopy, ReplacementTransform, ShowCreation, Write, GrowArrow, LaggedStartMap, FlashAround, VFadeIn, VShowPassingFlash, Blink, Rotate]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 3186
scene_classes: [ContrstClassicalAndQuantum, AmbientStateVector, RotatingStateVector, FlipsToCertainDirection, DisectAQuantumComputer, Qubit, ShowAFewFlips, ExponentiallyGrowingState, InvisibleStateValues, ThreeDSample, GroversAlgorithm, TwoFlipsEqualsRotation, ComplexComponents]
---

## Summary

Comprehensive visualization of Grover's quantum search algorithm, building from classical vs quantum computing fundamentals through qubit state vectors to the full Grover iteration. Custom mobjects include BitString (binary display), Ket (Dirac notation wrapper), and RandomSampling (animation that randomly cycles through quantum measurement outcomes). The visual progression moves from classical bits in boxes to quantum state vectors on the Bloch sphere, then to Grover's geometric rotation in 2D state space.

## Design Decisions

- **Classical vs quantum side-by-side**: Screen split by a vertical line. Classical bits on the left with boxed integer display, quantum qubits on the right with ket notation. This direct comparison is the pedagogical backbone.
- **Layers of abstraction**: Three stacked rectangles (Hardware, Bits, Data types) filled with BLUE_E->BLUE_C gradient. Same layering shown for both classical and quantum, emphasizing structural parallels.
- **BitString custom mobject**: A VGroup of Integer(0) copies that can set_value(n) to display any binary number. Clean, box-aligned display that maps directly to the trapped ion visualization above it.
- **Ket notation wrapper**: Custom Ket class wraps any mobject in Dirac bra-ket notation by placing | and > symbols around it with height scaling. Reused throughout the file.
- **RandomSampling animation**: Cycles through pre-computed qubit states randomly during playback, visually demonstrating quantum measurement randomness. Uses random.choices with optional weights for biased sampling.
- **3D state vector on Bloch sphere**: Vector in ThreeDAxes with ambient camera rotation (3 deg/frame). Sphere + mesh overlay shows the space of possible states. Vector always perpendicular to camera for readability.
- **State = not what you see**: The key conceptual beat uses != (red) between state and measurement, contrasted with = for classical. State vector is TEAL, measurement outcomes cycle randomly.

## Composition

- **Split screen**: v_line at center, classical LEFT, quantum RIGHT. FRAME_WIDTH/4 spacing.
- **Boxed bits**: Square().get_grid(1, length, buff=0), height=0.5, stroke WHITE width=2.
- **Layers**: Rectangle(8.0, 1.5).replicate(3), arranged UP buff=0. BLUE_E to BLUE_C gradient.
- **Trapped ions**: GlowDot(RED, radius=0.5) + Dot(radius=0.1) + Tex("+", font_size=14), spaced evenly across 4 units.
- **3D state vector scene**: ThreeDAxes(-1,1)^3 scaled 2x. Sphere radius=2. Mesh resolution (41,21). Camera starts at (14, 76, 0).
- **Morty for ket explanation**: height=5, position (13, -6, 0). Big ket notation with font_size=96 "ket" label.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Classical bits | WHITE | stroke_width=2 boxes |
| Quantum state vector | TEAL | Vector thickness=5, border_width=2 |
| Ket notation | WHITE | set_fill(border_width=3) |
| Layers of abstraction | BLUE_E to BLUE_C | fill_opacity=0.5, gradient |
| Trapped ions (|1>) | RED | GlowDot visible |
| Trapped ions (|0>) | RED | GlowDot opacity=0 |
| Ion lasers | RED | stroke [1,3,3,3,1] width profile |
| State != measurement | RED | ne symbol |
| Random measurement label | TEAL | for quantum side |
| Deterministic label | YELLOW | for classical side |
| Sphere | BLUE | opacity=0.25 |
| Sphere mesh | WHITE | stroke 0.5 width, 0.5 opacity |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Ion laser measurement | run_time=2 | VShowPassingFlash with time_width=2 |
| RandomSampling cycles | run_time=1 each | 8 repetitions |
| State vector rotation | varies | Random axis/angle, 16 iterations |
| Sphere reveal | run_time=2 | ShowCreation + Write mesh |
| Ambient camera rotation | 3 DEG continuous | On Bloch sphere scenes |
| Layer expansion | run_time=2 | Mid layer stretches to height=7 |

## Patterns

### Pattern: BitString Custom Mobject

**What**: A VGroup of Integer mobjects that displays a binary number. set_value(n) converts n to binary and updates each digit. Used alongside boxed grids (Square().get_grid) for classical bit visualization.

**When to use**: Binary number display, computer memory visualization, classical computing explanation, bit manipulation demonstrations.

```python
# Source: projects/videos/_2025/grover/state_vectors.py:5-16
class BitString(VGroup):
    def __init__(self, value, length=4, buff=SMALL_BUFF):
        self.length = length
        bit_mob = Integer(0)
        super().__init__(bit_mob.copy() for n in range(length))
        self.arrange(RIGHT, buff=buff)
        self.set_value(value)

    def set_value(self, value):
        bits = bin(value)[2:].zfill(self.length)
        for mob, bit in zip(self, bits):
            mob.set_value(int(bit))
```

### Pattern: RandomSampling Animation for Quantum Measurement

**What**: An Animation subclass that randomly selects from pre-computed sample states each frame, simulating quantum measurement randomness. Optionally accepts weights for biased sampling (post-Grover amplification).

**When to use**: Quantum measurement visualization, probabilistic state collapse, Monte Carlo sampling displays, any random selection animation.

```python
# Source: projects/videos/_2025/grover/state_vectors.py:33-50
class RandomSampling(Animation):
    def __init__(self, mobject, samples, weights=None, **kwargs):
        self.samples = samples
        self.weights = weights
        super().__init__(mobject, **kwargs)

    def interpolate(self, alpha):
        if self.weights is None:
            target = random.choice(self.samples)
        else:
            target = random.choices(self.samples, self.weights)[0]
        self.mobject.set_submobjects(target.submobjects)

# Usage: pre-compute all 2^8 possible measurement outcomes
qubit_samples = [qubits.copy().set_value(n) for n in range(2**8)]
self.play(RandomSampling(qubits, qubit_samples))
```

### Pattern: Ket Notation Wrapper

**What**: A Tex mobject that wraps any existing mobject in Dirac ket notation (| >). Automatically scales to match the wrapped object's height with a configurable scale factor. KetGroup bundles both into a VGroup for easy manipulation.

**When to use**: Quantum state notation, Dirac formalism, any physics visualization using bra-ket notation.

```python
# Source: projects/videos/_2025/grover/state_vectors.py:19-31
class Ket(Tex):
    def __init__(self, mobject, height_scale_factor=1.25, buff=SMALL_BUFF):
        super().__init__(R"| \rangle")
        self.set_height(height_scale_factor * mobject.get_height())
        self[0].next_to(mobject, LEFT, buff)
        self[1].next_to(mobject, RIGHT, buff)

class KetGroup(VGroup):
    def __init__(self, mobject, **kwargs):
        ket = Ket(mobject, **kwargs)
        super().__init__(ket, mobject)
```

### Pattern: 3D State Vector with Ambient Rotation

**What**: A Vector in ThreeDAxes with ambient camera rotation for depth perception. The vector uses set_perpendicular_to_camera to always face the viewer. A transparent Sphere with SurfaceMesh overlays to show the Bloch sphere of possible states.

**When to use**: Bloch sphere visualization, quantum state space, any 3D vector that needs to maintain readability while the camera rotates.

```python
# Source: projects/videos/_2025/grover/state_vectors.py:422-462
plane, axes = self.get_plane_and_axes()
frame.reorient(14, 76, 0)
frame.add_ambient_rotation(3 * DEG)

vector = Vector(2 * normalize([1, 1, 2]), thickness=5)
vector.set_fill(border_width=2)
vector.set_color(TEAL)
vector.always.set_perpendicular_to_camera(frame)

sphere = Sphere(radius=2)
sphere.always_sort_to_camera(self.camera)
sphere.set_color(BLUE, 0.25)
sphere_mesh = SurfaceMesh(sphere, resolution=(41, 21))
sphere_mesh.set_stroke(WHITE, 0.5, 0.5)
```

## Scene Flow

1. **Classical vs quantum split** (0-30s): Side-by-side comparison. Classical: boxed bits -> integer -> character. Quantum: trapped ions -> qubits in kets -> quantum integer.
2. **Layers of abstraction** (30-50s): Three layers expand to show hardware, bits, data types on both sides.
3. **Measurement** (50-80s): Laser pulses measure trapped ions. Qubit values change randomly. Morty explains ket notation.
4. **State != what you see** (80-120s): Classical side shows state = measurement. Quantum side shows state != measurement with RED inequality. RandomSampling demonstrates measurement randomness.
5. **Bloch sphere** (120-160s): 3D state vector with ambient rotation. Sphere and mesh reveal. Random rotations show state space.
6. **Grover's algorithm** (later scenes): 2D geometric visualization of the Grover iteration as reflection operations in the plane spanned by |target> and |uniform>.
