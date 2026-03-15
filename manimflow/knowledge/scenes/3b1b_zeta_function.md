---
source: https://github.com/3b1b/videos/blob/main/_2025/zeta/play.py
project: videos
domain: [complex_analysis, number_theory, mathematics]
elements: [complex_plane, vector, label, equation, dot, function_plot]
animations: [write, grow, animate_parameter, trace_path]
layouts: [side_by_side, centered]
techniques: [value_tracker, always_redraw, add_updater, custom_animation, data_driven]
purpose: [exploration, demonstration, step_by_step]
mobjects: [ComplexPlane, VMobject, Vector, VGroup, Tex, ComplexValueTracker, TrueDot, GlowDot]
manim_animations: [Write, FadeIn, ShowCreation]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 191
scene_classes: [ZetaSum, ZetaLogDerivSum]
---

## Summary

Visualizes the Riemann zeta function and its logarithmic derivative as partial sums in the complex plane. Two complex planes side by side: the left is the s-plane (input), the right is the output plane where partial sums are drawn as chains of vectors. A draggable dot on the s-plane controls the value of s, and the output updates in real-time via updaters. The exponential damping constant c smoothly regularizes divergent sums.

## Design Decisions

- **Dual complex plane layout**: Left plane shows the input s (narrow range, tall imaginary axis), right plane shows the output sum (square, symmetric). This separation makes the function mapping physically visible.
- **ComplexValueTracker for s**: Allows dragging s through the complex plane interactively. The partial sum path and vector chain update in real time via updaters.
- **Vector chain for partial sums**: Each term 1/n^s becomes a vector. Chaining them tip-to-tail shows how the sum spirals and converges. Alternating TEAL/GREEN colors distinguish adjacent terms.
- **Exponential damping e^(-cn)**: A ValueTracker for c lets you smoothly regularize the sum. At c=0 you see the raw zeta, increasing c dampens high-frequency oscillations. This makes analytic continuation intuitive.
- **Separate ZetaLogDerivSum class**: The log derivative -zeta'/zeta sums only over prime powers, with log(p) weights. Reuses the same visual framework by overriding generate_sample_ns() and get_summands().
- **GlowDot + TrueDot for s indicator**: GlowDot provides a soft halo for visibility, TrueDot gives a precise center. Combined in a Group with YELLOW color.

## Composition

- **Screen regions**:
  - s-plane (left): width=4, range (-1,3) x (-40,40), shifted LEFT with y=-0.5
  - Output plane (right): width=6, range (-3,3) x (-3,3), arranged RIGHT of s-plane with buff=2.0
  - Sum label: above output plane, aligned to its left edge
- **Element sizing**: Coordinate labels font_size=16, sum formula font_size=42
- **s-dot**: YELLOW, GlowDot + TrueDot group, label "s" at UR with SMALL_BUFF

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| s parameter | YELLOW | TrueDot + GlowDot + label |
| Partial sum path | TEAL | stroke_width=1 |
| Vector chain | TEAL, GREEN | Alternating, thickness=3 |
| Exponential constant c | RED | In Tex t2c and decimal display |
| Coordinate labels | default | font_size=16 on both planes |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Move s to zeta zero | run_time=3 | Smooth interpolation |
| Change exp constant | run_time=3 | Gradual regularization |
| Move s across values | run_time=3-5 | Various targets |

## Patterns

### Pattern: ComplexValueTracker with Live Partial Sum Path

**What**: A ComplexValueTracker holds a complex number s. A VMobject path updates every frame by computing the cumulative sum of n^(-s) terms and drawing the result as corners in the output plane. The vector sum overlays individual term vectors on the same path.

**When to use**: Any complex function visualization where you want to show how a sum or product builds up term by term. Dirichlet series, Fourier series partial sums, Taylor series in the complex plane.

```python
# Source: projects/videos/_2025/zeta/play.py:67-129
s_tracker = ComplexValueTracker(1)
get_s = s_tracker.get_value

# Partial sum path that auto-updates
path = VMobject()
def update_path(path):
    summands = weights * (sample_ns ** (-get_s()))
    partial_sums = np.hstack([[0], np.cumsum(summands)])
    points = out_plane.n2p(partial_sums)
    path.set_points_as_corners(points)
path.add_updater(update_path)
path.set_stroke(TEAL, 1)

# Vector chain on top of the path
vects = VGroup(
    Vector(RIGHT, thickness=3, fill_color=color)
    for n, color in zip(range(n_vects), it.cycle([TEAL, GREEN]))
)
def update_vects(vects):
    points = path.get_anchors()
    for vect, p0, p1 in zip(vects, points, points[1:]):
        vect.put_start_and_end_on(p0, p1)
vects.add_updater(update_vects)
```

### Pattern: Exponential Damping Regularization

**What**: A ValueTracker for an exponential constant c multiplies each summand by e^(-cn). Animating c from 0 to a positive value smoothly regularizes a divergent or slowly converging sum, visually taming wild oscillations.

**When to use**: Visualizing analytic continuation, regularization of divergent series, smoothing summation methods, Abel summation.

```python
# Source: projects/videos/_2025/zeta/play.py:30-31,111-114
exp_const_tracker = ValueTracker(0)

def get_summands(self, s):
    exp_const = self.exp_const_tracker.get_value()
    weights = np.exp(-exp_const * self.sample_ns)
    return weights * (self.sample_ns ** (-s))

# Animate regularization
self.play(exp_const_tracker.animate.set_value(0.01), run_time=3)
```

## Scene Flow

1. **Setup** (0-3s): Dual complex planes appear with coordinate labels. Yellow s-dot on s-plane. Sum formula above output plane.
2. **Partial sum appears** (3-5s): Vector chain and path materialize on output plane at current s value.
3. **Navigate to zeta zero** (5-8s): s-dot moves to first nontrivial zero. Vectors spiral to near-origin.
4. **Regularize** (8-11s): c increases from 0 to 0.01, smoothing the spiral.
5. **Log derivative variant**: Same visual framework but summing over prime powers with log(p) weights. Frame zooms out. s navigates to various zeros and off-critical-line points.
