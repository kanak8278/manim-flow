---
source: https://github.com/3b1b/videos/blob/main/_2018/fourier.py
project: videos
domain: [signal_processing, mathematics, waves, calculus]
elements: [axes, function_plot, label, arrow, pi_creature, dashed_line, brace, surrounding_rect]
animations: [write, draw, transform, replacement_transform, fade_in, fade_out, grow, lagged_start]
layouts: [vertical_stack, side_by_side, centered]
techniques: [helper_function, custom_mobject, scipy_integration, progressive_disclosure, data_driven]
purpose: [decomposition, demonstration, step_by_step, exploration]
mobjects: [Axes, FunctionGraph, VMobject, VGroup, OldTex, OldTexText, Line, DashedLine, Rectangle, Arrow, SVGMobject, Brace, DecimalNumber, Circle]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write, GrowFromCenter, GrowArrow, ReplacementTransform, LaggedStartMap]
scene_type: PiCreatureScene
manim_version: manimlib
complexity: advanced
lines: 4309
scene_classes: [Introduction, AddingPureFrequencies, FourierTradeoff, WrapCosineAroundCircle, DrawFrequencyPlot]
---

## Summary

Visualizes the Fourier transform as "winding a signal around a circle" — a time-domain signal is literally wrapped around the origin at different frequencies, and the center of mass of the wound-up graph reveals the frequency content. Uses FunctionGraph for time-domain signals, custom VMobject for the wound graph, and scipy/numpy FFT for the frequency-domain plot. Multiple pure frequency components (A440, D294, F349, C523) are shown stacking vertically, then combined into a sum signal.

## Design Decisions

- **Winding around a circle metaphor**: Instead of the abstract integral definition, the Fourier transform is shown as wrapping a 1D signal around the complex plane. The center of mass of the resulting curve is the transform value. This is Grant's signature visual explanation.
- **Color per frequency**: A=YELLOW, D=PINK, F=TEAL, C=RED, sum=GREEN. Each frequency gets a unique color that persists across time-domain, frequency-domain, and wound-up views.
- **Vertical stacking of component signals**: Individual frequency components are shown on separate axes stacked vertically, with the sum on the top axes. This makes additive composition physically visible.
- **scipy.integrate.quad for Fourier transform**: The get_fourier_transform function uses numerical integration rather than FFT for the "almost Fourier" transform (scalar = 1/(t_max-t_min)), giving smooth frequency-domain curves.
- **Speaker + broadcast animation**: A speaker SVG emits expanding arcs (broadcast animation) to give sound a visual presence. This grounds the abstract math in the physical context of audio.
- **Pi creature reactions**: Students react with confusion, then understanding. Teacher guides the narrative. The PiCreatureScene structure provides built-in pedagogical scaffolding.

## Composition

- **Time-domain axes**: y_min=-2, y_max=2, x_min=0, x_max=10. Stretched to height=2. Positioned at top, shifted UP. Equilibrium line as DashedLine at height=1.5.
- **Frequency axes**: Separate Axes below time axes. frequency_label colored RED, time_label default.
- **Component signal layout**: After separation, A_axes and D_axes are deepcopied and stacked with MED_LARGE_BUFF. Additional F and C axes appended below.
- **Brace**: On one period of the wave, positioned UP, with "Imagine 440 per second" text scaled 0.8.
- **Speaker**: SVGMobject at bottom edge. Broadcast arcs emanate from it.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| A440 signal | YELLOW | A_color config |
| D294 signal | PINK | D_color config |
| F349 signal | TEAL | F_color config |
| C523 signal | RED | C_color config |
| Sum signal | GREEN | sum_color config |
| Equilibrium line | GREY_B | DashedLine, stroke_width=2 |
| Frequency label | RED | FREQUENCY_COLOR constant |
| Highlight rect | YELLOW | fill_opacity=0.4, stroke_width=0 |
| Axes labels | WHITE | scale=0.8 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Wave drawing | run_time=4, rate_func=linear | ShowCreation of graph |
| Broadcast arcs | run_time=1 per ring | Expanding circles |
| Sum graph construction | run_time=15, rate_func=linear | Simultaneous line sweep across all graphs |
| Component separation | run_time=1 per MoveToTarget | Stacking animation |
| Frequency graph | run_time=4 | ReplacementTransform from time to freq |

## Patterns

### Pattern: FFT-based Frequency Domain Graph

**What**: Computes FFT of a time-domain function and plots the result as a VMobject. Uses np.fft.fft on sampled points, then creates a smooth curve through the frequency bins using set_points_smoothly. The underlying_function attribute allows later point queries.

**When to use**: Any Fourier analysis visualization, spectrum display, frequency content reveal. Also useful for any scenario where a computed transform needs to be plotted as a smooth curve.

```python
# Source: projects/videos/_2018/fourier.py:11-42
def get_fourier_graph(axes, time_func, t_min, t_max,
                      n_samples=1000, complex_to_real_func=lambda z: z.real,
                      color=RED):
    time_range = float(t_max - t_min)
    time_samples = np.vectorize(time_func)(np.linspace(t_min, t_max, n_samples))
    fft_output = np.fft.fft(time_samples)
    frequencies = np.linspace(0.0, n_samples / (2.0 * time_range), n_samples // 2)
    graph = VMobject()
    graph.set_points_smoothly([
        axes.coords_to_point(x, complex_to_real_func(y) / n_samples)
        for x, y in zip(frequencies, fft_output[:n_samples // 2])
    ])
    graph.set_color(color)
    return graph
```

### Pattern: Numerical Fourier Transform via scipy Integration

**What**: Computes the continuous Fourier transform using scipy.integrate.quad. Returns a callable function f -> transform_value. The "almost Fourier" variant divides by (t_max - t_min) for normalization. This gives smoother results than FFT for visualization.

**When to use**: When you need a continuous frequency-domain function rather than discrete bins. Useful for interactive exploration where the user adjusts parameters and the transform updates smoothly.

```python
# Source: projects/videos/_2018/fourier.py:44-57
def get_fourier_transform(func, t_min, t_max,
                          complex_to_real_func=lambda z: z.real,
                          use_almost_fourier=True):
    scalar = 1. / (t_max - t_min) if use_almost_fourier else 1.0
    def fourier_transform(f):
        z = scalar * scipy.integrate.quad(
            lambda t: func(t) * np.exp(complex(0, -TAU * f * t)),
            t_min, t_max
        )[0]
        return complex_to_real_func(z)
    return fourier_transform
```

### Pattern: Simultaneous Multi-Graph Line Sweep

**What**: A vertical highlight rectangle sweeps across multiple stacked axes simultaneously. For each axes/graph pair, a get_graph_line_animation creates a synchronized sweep. All animations run with rate_func=linear at the same run_time, creating a visual scan that reveals how components add up at each time point.

**When to use**: Showing superposition of signals, comparing multiple time series at the same time instant, any "vertical slice" analysis across stacked plots.

```python
# Source: projects/videos/_2018/fourier.py:406-414
# Simultaneous sweep across all component graphs + sum
kwargs = {"rate_func": None, "run_time": 10}
self.play(ShowCreation(new_sum_graph.copy(), **kwargs), *[
    self.get_graph_line_animation(curr_axes, graph, **kwargs)
    for curr_axes, graph in [
        (self.A_axes, self.A_graph),
        (self.D_axes, self.D_graph),
        (F_axes, F_graph),
        (C_axes, C_graph),
        (axes, new_sum_graph),
    ]
])
```

## Scene Flow

1. **Introduction** (0-15s): TeacherStudentsScene with "Fourier Transform" title. FunctionGraph of cos(2*TAU*t)+cos(3*TAU*t) on left, its Fourier transform on right, connected by arrow. Student reactions.
2. **A440 Sound** (15-60s): Speaker SVG with broadcast animation. Pressure vs time graph appears. A440 sine wave drawn with ShowCreation over 4s. Brace shows "440 per second."
3. **Add Lower Pitch** (60-90s): D294 wave added. Both graphs visible on same axes. Labels show note names.
4. **Separate and Stack** (90-120s): A and D graphs move to separate stacked axes. Sum drawn on original axes with vertical sweep animation.
5. **Four Notes Combined** (120-180s): F and C added. All four components stacked. New more complex sum drawn with 10s sweep. Highlight rectangles show specific time points.
6. **Fourier Transform** (180-240s): Arrow from time to frequency domain. Frequency graph constructed. Width tracker controls wave packet width, showing the time-frequency tradeoff.
