---
source: https://github.com/3b1b/videos/blob/main/_2018/uncertainty.py
project: videos
domain: [signal_processing, physics, waves, probability, quantum_mechanics]
elements: [axes, function_plot, vector, dot, arrow, label, equation, brace, pi_creature, wave]
animations: [write, transform, fade_in, fade_out, draw, animate_parameter, update_value]
layouts: [vertical_stack, side_by_side, centered]
techniques: [value_tracker, always_redraw, add_updater, custom_mobject, scipy_integration, progressive_disclosure, helper_function]
purpose: [demonstration, exploration, analogy, step_by_step]
mobjects: [Axes, FunctionGraph, VGroup, OldTex, OldTexText, Line, DashedLine, Arrow, Vector, Circle, Arc, Dot, DecimalNumber, SVGMobject, ExponentialValueTracker, Brace]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write, GrowFromCenter, GrowArrow, ReplacementTransform, UpdateFromFunc, Transform, ChangeDecimalToValue]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 4739
scene_classes: [MentionUncertaintyPrinciple, FourierTradeoff, ShowPlan, ShowDopplerRadar]
---

## Summary

Visualizes the Heisenberg uncertainty principle as a consequence of the Fourier transform tradeoff — a narrow time-domain signal has a wide frequency spread, and vice versa. Uses ProbabalisticDotCloud and ProbabalisticVectorCloud (Gaussian-distributed point clouds driven by GaussianDistributionWrapper) to show position and momentum uncertainty. The FourierTradeoff scene uses ExponentialValueTracker to smoothly morph a wave packet between narrow and wide, with the Fourier transform updating in real-time. Imports from fourier.py for FFT computation.

## Design Decisions

- **Gaussian clouds for uncertainty**: Position is shown as a cloud of dots (ProbabalisticDotCloud), momentum as a cloud of vectors (ProbabalisticVectorCloud). Each cloud's spread is controlled by a GaussianDistributionWrapper (a Line whose length encodes sigma). When one shrinks, the other grows — the uncertainty tradeoff is physically visible.
- **ExponentialValueTracker for wave packet width**: Since width spans orders of magnitude (0.02 to 6), an ExponentialValueTracker provides perceptually uniform animation speed. Linear tracking would rush through small values.
- **Radar/Doppler analogy before quantum**: The video builds from concrete (radar pulses, Doppler effect) to abstract (quantum uncertainty). Each level uses the same Fourier tradeoff visual but in a different context.
- **GaussianDistributionWrapper as invisible Line**: The distribution parameters (mu, sigma) are encoded as a Line's center and radial vector. This makes it a Mobject that can be interpolated during animations — the distribution smoothly morphs.
- **ContinualAnimation for clouds**: ProbabalisticMobjectCloud extends ContinualAnimation (deprecated, now use updaters) to continuously resample point positions from the Gaussian distribution every frame.
- **Dual axes layout**: Time-domain signal on top (Axes with YELLOW graph), frequency-domain on bottom (TEAL Axes with RED graph). Arrow connecting them labeled "Fourier Transform."

## Composition

- **Time axes**: x_min=0, x_max=8 (2*time_mean), x_axis unit_size=1.5. y_min=-2, y_max=2, y_axis unit_size=0.5. Centered, to_edge(UP).
- **Frequency axes**: x_min=0, x_max=8, x_axis unit_size=1.5. y_min=-0.025, y_max=0.075, y_axis unit_size=30. TEAL colored. Aligned LEFT with time axes, to_edge(DOWN, buff=LARGE_BUFF).
- **Wave packet**: Gaussian envelope * cos(4*TAU*t). YELLOW color. 200 graph points.
- **Fourier graph**: RED colored. Computed via get_fourier_graph with 17*2*time_radius samples.
- **Cloud layout**: dot_cloud and vector_cloud next to title, separated by 3*RIGHT. Braces below/above with sigma labels.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Wave packet | YELLOW | Time-domain signal |
| Frequency graph | RED | FREQUENCY_COLOR constant |
| Frequency axes | TEAL | Axes color config |
| Position cloud dots | BLUE | ProbabalisticDotCloud default |
| Momentum cloud vectors | RED | ProbabalisticVectorCloud default |
| Sub-words | BLUE | "(To be explained shortly)" |
| Fourier arrow | RED (FREQUENCY_COLOR) | Arrow connecting domains |
| Radar dish | GREY_B | SVG fill |
| Radar pulse | BLUE to YELLOW | color_gradient across pulses |
| Pulse stroke | WHITE | stroke_width=3 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Wave packet morph | run_time=3 per width change | ExponentialValueTracker |
| Fourier transform display | run_time=1 | ReplacementTransform |
| Cloud sigma change | run_time=2-3 | Smooth Gaussian reshape |
| Radar pulse | speed=3.0 units/s | ContinualAnimation |
| Graph creation | run_time=2 | ShowCreation with double_smooth |
| Width cycle (3 values) | ~12s total | 3x run_time=3 + waits |

## Patterns

### Pattern: ExponentialValueTracker for Fourier Tradeoff

**What**: An ExponentialValueTracker controls the width of a Gaussian wave packet. Two UpdateFromFunc animations keep the time-domain graph and frequency-domain graph synchronized: as the tracker changes, both graphs regenerate via Transform. The exponential tracker ensures smooth animation across orders-of-magnitude width changes (0.02 to 6).

**When to use**: Any paired visualization where one parameter controls two linked displays (time/frequency, position/momentum, spatial/spectral). The ExponentialValueTracker is essential when the parameter spans orders of magnitude.

```python
# Source: projects/videos/_2018/uncertainty.py:363-493
width_tracker = ExponentialValueTracker(0.5)
get_width = width_tracker.get_value

def get_wave_packet_function():
    factor = 1. / get_width()
    return lambda t: (factor**0.25) * np.cos(4*TAU*t) * np.exp(-factor*(t-time_mean)**2)

wave_packet = get_wave_packet()
wave_packet_update = UpdateFromFunc(
    wave_packet, lambda g: Transform(g, get_wave_packet()).update(1)
)
fourier_graph_update = UpdateFromFunc(
    fourier_graph, lambda g: Transform(g, get_wave_packet_fourier_transform()).update(1)
)

for width in self.widths:  # [6, 0.02, 1]
    self.play(
        width_tracker.set_value, width,
        wave_packet_update,
        fourier_graph_update,
        run_time=3
    )
```

### Pattern: Gaussian Distribution as Animated Mobject (GaussianDistributionWrapper)

**What**: Encodes a 2D Gaussian distribution (mu, sigma) as an invisible Line. The center is mu, the direction vector is sigma. This makes the distribution a Mobject that can be animated with Transform or ApplyMethod. Point clouds sample from it every frame, creating a living probability visualization.

**When to use**: Probability distributions that need to morph over time, uncertainty visualization, any scenario where distribution parameters should be animated as continuous quantities.

```python
# Source: projects/videos/_2018/uncertainty.py:17-54
class GaussianDistributionWrapper(Line):
    CONFIG = {"stroke_width": 0, "mu": ORIGIN, "sigma": RIGHT}

    def change_parameters(self, mu=None, sigma=None):
        curr_mu, curr_sigma = self.get_parameters()
        mu = mu if mu is not None else curr_mu
        sigma = sigma if sigma is not None else curr_sigma
        self.put_start_and_end_on(mu - sigma, mu + sigma)

    def get_random_points(self, size=1):
        mu, sigma = self.get_parameters()
        return np.array([
            [np.random.normal(mu_coord, sigma_coord)
             for mu_coord, sigma_coord in zip(mu, sigma)]
            for x in range(size)
        ])
```

### Pattern: Radar Pulse as ContinualAnimation

**What**: An expanding arc (60-degree arc) propagates outward from a radar dish, reflects off a target, and returns. The pulse tracks distance via internal_time * speed, and uses point manipulation to create the reflection effect (clipping points past the target distance). Multiple pulses with color gradient create a visually rich radar beam.

**When to use**: Wave propagation, sonar, radar, any expanding wavefront that reflects. The reflection geometry via point manipulation is reusable for any bouncing-wave visualization.

```python
# Source: projects/videos/_2018/uncertainty.py:157-241
class RadarPulseSingleton(ContinualAnimation):
    CONFIG = {"speed": 3.0, "direction": RIGHT, "color": WHITE, "stroke_width": 3}

    def update_mobject(self, dt):
        arc = self.arc
        total_distance = self.speed * self.internal_time
        arc.set_points(self.start_points)
        arc.shift(total_distance * self.direction)
        # Reflection: flip points past the target
        if self.reflection_distance is not None:
            diffs = point_distances - self.reflection_distance
            shift_vals = np.outer(-2 * np.maximum(diffs, 0), self.direction)
            arc.set_points(arc.get_points() + shift_vals)
```

## Scene Flow

1. **Uncertainty Principle Statement** (0-30s): TeacherStudentsScene. Title "Heisenberg Uncertainty Principle." Dot cloud (position) and vector cloud (momentum) appear. As one cloud narrows, the other widens. Braces show 2*sigma labels.
2. **Fourier Tradeoff** (30-90s): Time axes (top) and frequency axes (bottom). Yellow wave packet drawn. Arrow + "Fourier Transform" label. ExponentialValueTracker morphs width through [6, 0.02, 1] — narrow pulse = wide spectrum, broad pulse = narrow spectrum.
3. **Sound Context** (90-150s): Speaker SVG broadcasting. Sound waves decomposed into frequencies. Connection to hearing different pitches.
4. **Doppler Radar** (150-210s): Radar dish SVG. Pulse arcs propagate, reflect off target. Short pulse = good position but poor velocity. Long pulse = good velocity (Doppler) but poor position. Same Fourier tradeoff.
5. **Quantum Connection** (210-270s): The position/momentum clouds return. The Fourier relationship between position and momentum wavefunctions IS the uncertainty principle. Not a measurement limitation — a mathematical identity.
