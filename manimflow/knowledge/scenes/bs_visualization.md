---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/visualization_conclusion.py
project: ragibson_manim-videos
domain: [finance, probability, statistics, economics]
elements: [axes, function_plot, area_under_curve, dashed_line, dot, label, title, equation]
animations: [fade_in, fade_out, write, draw, animate_parameter]
layouts: [side_by_side, edge_anchored]
techniques: [value_tracker, add_updater, always_redraw, scipy_integration]
purpose: [exploration, demonstration, comparison]
mobjects: [Text, MathTex, Axes, VGroup, ValueTracker, DashedLine, Dot, DashedVMobject, Surface]
manim_animations: [Write, FadeIn, FadeOut, Create, BulletedList]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 247
scene_classes: [BlackScholesVisualization, FinalTakeaways]
---

## Summary

Interactive visualization of the Black-Scholes formula with five ValueTrackers (S0, sigma, t, K, r) driving two synchronized panels. The left panel shows the lognormal price distribution with a strike line and shaded area above strike. The right panel shows the option price curve (from `black_scholes_price()`) against intrinsic value (dashed hockey-stick), with a dot marking the current S(0) position. All elements rebuild via updaters as each parameter sweeps through a range. The scene performs three rounds of parameter sweeps with increasing visual complexity, ending with a delta-sensitivity demonstration.

## Design Decisions

- **Five ValueTrackers initialized in __init__**: All Black-Scholes parameters (S0=300, sigma=0.10, t=0.25, K=310, r=0.04) are ValueTrackers created in the constructor, not in construct(). This allows helper methods to access them cleanly and keeps the animation code focused on sequencing.
- **Fixed variable positions to prevent text jitter**: When parameter values change, the LaTeX width changes (e.g., "$300" vs "$280"). Without intervention, `arrange()` would shift all labels. The hack stores initial positions on first render and overrides `arrange()` on subsequent renders by using `move_to(stored_position, aligned_edge=LEFT)`.
- **Three-phase sweep sequence**: First sweep with only the distribution (left panel), second sweep after adding the payoff diagram (right panel), third sweep including the risk-free rate. This progressive disclosure prevents overwhelming the viewer with two complex panels at once.
- **Intrinsic value as DashedVMobject**: The hockey-stick payoff max(S-K, 0) is rendered as a dashed line (DashedVMobject with num_dashes=50), visually distinguishing it from the smooth Black-Scholes curve. This matches the finance convention where intrinsic value is shown as a reference line.
- **Dot on option price curve**: A white Dot follows the current S(0) position on the Black-Scholes curve, making it easy to track the option price as S(0) sweeps. The dot rebuilds every frame via updater.
- **Delta sensitivity hint at end**: The final sweep sequence oscillates S(0) through [260, 280, 260, 340, 320, 340, 300], showing how the option price changes faster when in-the-money vs out-of-the-money. This hints at the concept of delta (the option's sensitivity to stock price) without naming it.
- **BulletedList for final takeaways**: FinalTakeaways uses Manim's BulletedList with manual color hack for the third bullet. The hack indexes into the BulletedList to color "General problem-solving technique" BLUE.

## Composition

- **Variable text bar**: arranged RIGHT buff=0.75, to_edge(UP, buff=0.5). Five MathTex objects showing S(0), sigma, t, K, r.
- **Left panel (price distribution)**:
  - Axes: x_range=[250, 350.1, 25], y_range=[0, 0.05], x_length=5.25, y_length=4, to_edge(LEFT, buff=0.5)
  - X-axis label: centered below x-axis, DOWN buff=0.75
  - Strike line: DashedLine full y-range at K
  - Shaded area: get_area() from K to x_max, BLUE opacity=0.5
- **Right panel (payoff diagram)**:
  - Axes: x_range=[250, 350.1, 25], y_range=[0, 50.1, 10], x_length=5.25, y_length=4, to_edge(RIGHT, buff=0.5)
  - Intrinsic value: DashedVMobject, WHITE, num_dashes=50
  - Option price curve: BLUE, z_index=2
  - Current price dot: WHITE, radius=0.1, z_index=3
- **Dollar-sign labels**: Manual add_labels hack on both panels' x and y axes

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Variable text (default) | WHITE | font_size=MATH_SIZE_MEDIUM |
| Active variable | YELLOW | Highlighted during its sweep |
| Price distribution curve | BLUE | z_index=1 |
| Strike line | WHITE | DashedLine |
| Area above strike | BLUE | opacity=0.5 |
| Intrinsic value line | WHITE | DashedVMobject, num_dashes=50 |
| Option price curve | BLUE | z_index=2 |
| Current price dot | WHITE | radius=0.1, z_index=3 |
| "General problem-solving" | BLUE | Manual BulletedList color hack |
| "What We Learned" header | YELLOW | font_size=TEXT_SIZE_MEDIUM |

Color strategy: Minimal palette. BLUE for all computed/theoretical elements (distribution, option price, shaded area). WHITE for reference elements (intrinsic value, strike line, dot). YELLOW for the currently active parameter being swept.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Variable text Write | 2.0s | All five at once |
| First variable highlight sweep | ~5s | Just cycling through names |
| Left panel Create | 2.0s | Axes + labels |
| Distribution Create | default | rate_func=linear |
| Each parameter sweep value | 2.0s | ValueTracker animate |
| 0.5s wait between sweep values | | 0.25s wait between variables |
| Right panel Create | 2.0s | Axes + labels |
| Intrinsic value Create | default | rate_func=linear |
| Full sweep (5 variables, 3 values each) | ~45s | Per round |
| Delta sensitivity sweep | ~30s | 7 values for S0 only |
| Total (BlackScholesVisualization) | ~3 minutes | |
| Total (FinalTakeaways) | ~15s | |

## Patterns

### Pattern: Multi-ValueTracker Interactive Parameter Dashboard

**What**: Five ValueTrackers drive a full parameter dashboard. Helper methods (create_price_distribution, create_payoff_diagram, create_text) rebuild all visual elements from current tracker values. Each element has add_updater calling the appropriate helper. A sweep_variables method takes a sequence of target values per parameter and animates through them, highlighting the active variable in YELLOW.
**When to use**: Any multi-parameter formula visualization where the viewer needs to see the effect of each variable independently, Black-Scholes greeks exploration, sensitivity analysis dashboards, physics simulations with multiple controls.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/visualization_conclusion.py:37-39
self.S0, self.sigma, self.t, self.K, self.r = (ValueTracker(x) for x in (300.0, 0.10, 0.25, 310.0, 0.04))

# Source: projects/ragibson_manim-videos/black_scholes_derivation/visualization_conclusion.py:127-142
def sweep_variables(self, sweep_sequence):
    assert len(sweep_sequence) == 5
    self.variable_highlight_idx = 0
    for variable, values in zip((self.S0, self.sigma, self.t, self.K, self.r), sweep_sequence):
        self.wait(0.25)
        for v in values:
            self.play(variable.animate.set_value(v), run_time=2.0)
            self.wait(0.5)
        self.variable_highlight_idx += 1
    self.variable_highlight_idx = None
```

### Pattern: Fixed-Position Text Labels Preventing Jitter

**What**: When ValueTracker-driven text is arranged in a row, changing values (e.g., "$300" to "$280") causes width changes that shift all labels. The fix: on first render, store each label's left-anchor position. On subsequent renders, override arrange() by using move_to(stored_position, aligned_edge=LEFT).
**When to use**: Any row of updating numeric labels, parameter dashboards, live scoreboards, any situation where multiple text elements in a row change width independently.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/visualization_conclusion.py:79-98
def create_text(self):
    variables = VGroup(
        MathTex(rf"S(0) = \${self.S0.get_value():.0f}", font_size=MATH_SIZE_MEDIUM),
        MathTex(rf"\sigma = {100 * self.sigma.get_value():.1f}\%", font_size=MATH_SIZE_MEDIUM),
        # ... more variables ...
    ).arrange(RIGHT, buff=0.75).to_edge(UP, buff=0.5)

    if self.variable_highlight_idx is not None:
        variables[self.variable_highlight_idx].set_color(YELLOW)

    if self.variable_positions:
        for i, v in enumerate(variables):
            v.move_to(self.variable_positions[i], aligned_edge=LEFT)
    else:
        self.variable_positions = [x.get_left() for x in variables]
    return variables
```

### Pattern: DashedVMobject for Reference Curves

**What**: Converts a solid plot_line_graph output into a dashed line using DashedVMobject(line['line_graph'], num_dashes=50). This is used for reference/comparison curves (like intrinsic value) that should be visually distinct from the main computed curve. The dashed line also has its own updater to rebuild when parameters change.
**When to use**: Showing theoretical vs empirical curves, reference lines vs computed results, intrinsic value vs option price, any overlay where two curves share the same axes but represent different concepts.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/visualization_conclusion.py:104-109
intrinsic_price = self.payoff_ax.plot_line_graph(
    x_values=plot_xs,
    y_values=np.maximum(plot_xs - self.K.get_value(), 0.0),
    line_color=WHITE, add_vertex_dots=False, z_index=1
)
intrinsic_price = DashedVMobject(intrinsic_price['line_graph'], num_dashes=50)
```

## Scene Flow

1. **Variable introduction** (0-10s): Five parameter labels (S0=$300, sigma=10%, t=0.25, K=$310, r=4%) write across the top. Each variable briefly highlights YELLOW as it's introduced.
2. **Left panel: Price distribution** (10-25s): Distribution axes create. Lognormal PDF draws. Strike line and shaded area appear. All elements get updaters.
3. **First sweep** (25-70s): Each of S0, sigma, t, K sweeps through 3 values while only the left panel is visible. Distribution reshapes in real-time. Active variable highlighted YELLOW.
4. **Right panel: Payoff diagram** (70-85s): Payoff axes create. Intrinsic value dashed line draws. White dot appears at current option price. S0 sweeps left/right to show dot tracking.
5. **Option price curve + full sweep** (85-95s): Blue option price curve fades in. Gets updater. Full sweep of all 5 parameters including risk-free rate r for the first time. Both panels update simultaneously.
6. **Delta sensitivity** (95-120s): S0 oscillates through 7 values [260, 280, 260, 340, 320, 340, 300], showing option price sensitivity varies by moneyness. All updaters cleared, everything fades.
7. **FinalTakeaways** (0-15s): "What We Learned" header in YELLOW. Three bullet points: financial knowledge, mathematical finance complexity, general problem-solving technique (simulate, iterate, refine). Third bullet partially colored BLUE. Everything fades.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/visualization_conclusion.py` (247 lines)
