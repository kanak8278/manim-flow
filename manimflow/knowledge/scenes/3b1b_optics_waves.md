---
source: https://github.com/3b1b/videos/blob/main/_2023/optics_puzzles/slowing_waves.py
project: videos
domain: [optics, waves, physics, electromagnetism]
elements: [wave, oscillator, line, label, equation, arrow, vector]
animations: [write, fade_in, fade_out, draw, animate_parameter, lagged_start, grow, move]
layouts: [centered, side_by_side]
techniques: [value_tracker, add_updater, custom_mobject, progressive_disclosure, always_redraw]
purpose: [demonstration, step_by_step, simulation, exploration]
mobjects: [ThreeDAxes, VGroup, Line, Vector, Text, Tex, DecimalNumber, FullScreenRectangle, BackgroundRectangle, SurroundingRectangle]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, FadeTransform, GrowFromCenter, LaggedStart, ChangeDecimalToValue, ReplacementTransform]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 977
scene_classes: [SpeedInMediumFastPart, SpeedInMediumSlower, VectorOverMedia, VioletWaveFast, VioletWaveSlow, GreenWaveFast, GreenWaveSlow, OrangeWaveFast, OrangeWaveSlow, RedWaveFast, RedWaveSlow, PhaseKickBacks, RevertToOneLayerAtATime]
---

## Summary

Visualizes how light waves slow down in a medium (like glass) through the concept of "phase kick-backs" — each thin layer of material kicks back the phase of the wave by a small amount. Uses a custom SlicedWave group that wraps an OscillatingWave with per-layer phase and amplitude trackers. The progressive reveal starts with many dense layers, collapses to one layer showing a large phase kick, then builds back up with smaller kicks to show how the continuous limit reproduces the apparent speed reduction.

## Design Decisions

- **SlicedWave custom group**: Wraps OscillatingWave with arrays of ValueTrackers for per-layer phase kick and absorption. The xt_to_yz method modifies the wave equation based on which layers the x-coordinate has passed, giving a physically accurate piecewise wave.
- **Phase kick-back as the core mechanism**: Instead of abstractly saying "light slows down," the visualization shows each layer literally kicking back the phase by a small delta. This is the actual physics — the medium's response shifts the wave phase.
- **Colored medium rectangle**: Right half of screen filled with BLUE at low opacity (0.25-0.35) to represent glass. Simple but immediately legible.
- **Spectral colors**: Different wavelength scenes use get_spectral_color() to show actual visible light colors (violet=0.95, green=0.65, orange=0.3, red=0.05). Each has matching wavelength and speed in medium.
- **Progressive layer reveal**: Start with 2^11 layers packed tightly (practically continuous), then collapse to 1 layer with exaggerated phase kick, then rebuild with 2, 4, 8, ... layers with proportionally smaller kicks. This builds intuition for the continuous limit.
- **Phase kick formula display**: Shows A*sin(kx) on the left side and A*sin(kx + delta) on the right. The delta value is a live DecimalNumber that updates with the phase kick tracker.

## Composition

- **Wave axes**: ThreeDAxes x_range=(-12,12), y_range=(-4,4). z and y axes at opacity=0.
- **Medium rectangle**: FullScreenRectangle stretched 0.5 horizontally about_edge=RIGHT. Fill BLUE at medium_opacity.
- **Material label**: Text, font_size=60, next_to rect top edge DOWN.
- **Layer lines**: Line(DOWN, UP) height=4-5, stroke_width=2 at opacity=1 for visible, 1 at 0.25 for dense packing.
- **Phase kick label**: Text("Phase kick = ") at font_size=36, GREY_B. DecimalNumber in RED next to it. Upper left area.
- **Number of layers label**: TexText("Num. layers = N"), font_size=36. GREY_B with BLUE decimal. Above phase kick label.
- **Kick arrow and text**: Vector(1.0*LEFT, stroke_width=6) + "Kick back the phase" in RED.
- **Phase formula**: Tex(R"A\sin(kx)") left, Tex(R"A\sin(kx + 1.00)") right. DecimalNumber changeable in RED.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Fast wave | YELLOW | Default wave color |
| Medium (glass) | BLUE | fill opacity 0.25-0.35 |
| Phase kick value | RED | DecimalNumber in formulas |
| Kick arrow/text | RED | Vector + Text |
| Layers (dense) | BLUE_B | stroke_width=1, opacity=0.25 |
| Layers (sparse) | WHITE | stroke_width=2, opacity=1 |
| Layer count label | BLUE | Integer decimal |
| Phase kick label | GREY_B | Text body |
| Violet wave | spectral 0.95 | wave_len=1.2, y_amplitude=0.5 |
| Green wave | spectral 0.65 | wave_len=1.5 |
| Orange wave | spectral 0.3 | wave_len=2.0 |
| Red wave | spectral 0.05 | wave_len=2.5 |
| Vector field arrows | default | OscillatingFieldWave, opacity=0.5 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Basic wave propagation | run_time=30 | self.wait(30) continuous |
| Layer collapse | run_time=2 | arrange RIGHT buff=0.3 |
| Single layer emerge | run_time=5 | LaggedStart layer fadeouts |
| Phase kick adjust | run_time=2-4 | ChangeDecimalToValue |
| Layer doubling | run_time=3 each | lag_ratio=0.1 GrowFromCenter |
| Layer filling cycles | 6 iterations | Each halves spacing, halves kick |
| Clock stop/start | instant | wave.stop_clock() / start_clock() |

## Patterns

### Pattern: SlicedWave with Per-Layer Phase Trackers

**What**: A custom Group wrapping an OscillatingWave that adds phase kick and damping at discrete layer positions. Each layer has its own ValueTracker for phase_kick and absorption. The wave's xt_to_yz method is overridden to apply cumulative phase shifts for x > layer_x.

**When to use**: Light propagation through layered media, wave refraction visualization, index of refraction explanation, any wave passing through discrete interfaces.

```python
# Source: projects/videos/_2023/optics_puzzles/slowing_waves.py:5-76
class SlicedWave(Group):
    def __init__(self, axes, layer_xs, phase_kick_back=0,
                 layer_height=4.0, damping_per_layer=1.0, **kwargs):
        self.wave = OscillatingWave(axes, **wave_kw)
        self.vect_wave = OscillatingFieldWave(axes, self.wave)
        self.phase_kick_trackers = [ValueTracker(phase_kick_back) for x in layer_xs]
        self.absorbtion_trackers = [ValueTracker(damping_per_layer) for x in layer_xs]
        self.layers = VGroup(
            Line(DOWN, UP).set_height(layer_height).move_to(axes.c2p(x, 0))
            for x in layer_xs
        )
        self.wave.xt_to_yz = self.xt_to_yz  # Override wave equation

    def xt_to_yz(self, x, t):
        phase = TAU * t * self.wave.speed / self.wave.wave_len * np.ones_like(x)
        amplitudes = self.wave.y_amplitude * np.ones_like(x)
        for layer_x, pkt, at in zip(self.layer_xs, self.phase_kick_trackers,
                                     self.absorbtion_trackers):
            phase[x > layer_x] += pkt.get_value()
            amplitudes[x > layer_x] *= at.get_value()
        y = amplitudes * np.sin(TAU * x / self.wave.wave_len - phase)
        return y, np.zeros_like(x)
```

### Pattern: Progressive Layer Doubling with Phase Kick Halving

**What**: Start with N layers and a phase kick delta. Double the number of layers while halving the kick per layer. Repeat until the layers are nearly continuous. This demonstrates that many small phase kicks approximate a continuous speed change. Layer opacity and stroke width scale down to prevent visual clutter.

**When to use**: Continuous limit demonstrations, Riemann sum -> integral analogy, any discrete-to-continuous approximation where you want to show convergence.

```python
# Source: projects/videos/_2023/optics_puzzles/slowing_waves.py:454-500
nls = self.n_layers_skipped  # Start at 64
while nls > 1:
    nls //= 2
    opacity = 0.25 + 0.5 * (opacity - 0.25)
    stroke_width = 1.0 + 0.5 * (stroke_width - 1.0)
    phase_kick /= 2

    new_layers = layers[nls::2 * nls]
    old_layers = layers[0::2 * nls]

    self.play(
        LaggedStart(*(GrowFromCenter(l) for l in new_layers),
                     lag_ratio=0.1, run_time=3),
        old_layers.animate.set_stroke(width=stroke_width, opacity=opacity),
        LaggedStart(*(pkt.animate.set_value(phase_kick)
                       for pkt in pkts[::nls]),
                     lag_ratio=0.1, run_time=3),
    )
```

### Pattern: Spectral Wave Color Variants via Class Inheritance

**What**: A base class defines wave parameters (color, wave_len, speed, amplitude). Subclasses override only the parameters that differ for each spectral color. A "slow" variant halves both wavelength and speed (keeping frequency constant) for the in-medium version.

**When to use**: Showing multiple wavelengths of light, dispersion visualization, any wave property comparison where you need the same scene structure with different parameters.

```python
# Source: projects/videos/_2023/optics_puzzles/slowing_waves.py:150-193
class VioletWaveFast(SpeedInMediumFastPart):
    color = get_spectral_color(0.95)
    wave_len = 1.2
    y_amplitude = 0.5
    speed = 1.5

class VioletWaveSlow(VioletWaveFast):
    wave_len = 1.2 * 0.5
    speed = 1.5 * 0.5

class GreenWaveFast(VioletWaveFast):
    color = get_spectral_color(0.65)
    wave_len = 1.5
```

## Scene Flow

1. **Basic wave in medium** (0-30s): Yellow wave propagates left to right. Right half is blue medium. Wave continues at reduced speed/wavelength inside medium.
2. **Phase velocity label** (30-35s): Vector tracking phase velocity annotated.
3. **Spectral variants** (35-60s): Violet, green, orange, red waves each shown in fast (vacuum) and slow (medium) versions. Different spectral colors from get_spectral_color.
4. **Phase kick mechanism** (60-120s): Dense layers shown, then collapsed to one. Clock paused. Phase kicked back visually with red arrow. Formula A*sin(kx) -> A*sin(kx+delta) displayed. Then rebuilt with more layers.
5. **Continuous limit** (120-180s): Layer count doubles repeatedly (N, 2N, 4N, ...) while kick halves. Layers become nearly invisible. The discrete kicks converge to smooth apparent speed reduction.
