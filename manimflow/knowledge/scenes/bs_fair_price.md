---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/finding_a_fair_price.py
project: ragibson_manim-videos
domain: [finance, probability, statistics, economics]
elements: [axes, function_plot, histogram, dashed_line, label, title, equation]
animations: [fade_in, fade_out, write, draw, color_change, lagged_start, stagger]
layouts: [side_by_side, edge_anchored]
techniques: [data_driven, progressive_disclosure, helper_function]
purpose: [simulation, demonstration, step_by_step]
mobjects: [Text, MarkupText, Tex, MathTex, Axes, BarChart, DashedLine, VGroup]
manim_animations: [Write, FadeIn, FadeOut, Create, LaggedStart, Succession]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 179
scene_classes: [GuessingTheFuture, DemonstrateSimulation]
---

## Summary

Demonstrates Monte Carlo option pricing through simulation. First scene shows a stock price path up to "today" with three color-coded possible futures (green/gold/red) representing optimistic, neutral, and pessimistic outcomes. Second scene runs ~550 simulated paths at exponentially increasing speed on the left panel while building a real-time histogram of option profits on the right. Paths progressively dim to near-invisible as more are added. Ends with a yellow dashed line marking the average profit as the suggested fair option price.

## Design Decisions

- **Brownian bridges for future paths**: Rather than pure random simulations, the three example futures use Brownian bridges pinned to specific endpoints ($350, $300, $250). This ensures the green path ends above strike, gold at strike, and red below, making the narrative point crystal clear without relying on random luck.
- **Dual-panel simulation layout**: Simulated paths on the left, histogram on the right. This side-by-side layout lets the viewer see cause (stock paths) and effect (profit distribution) simultaneously. The axes share the same vertical space for visual alignment.
- **Exponentially decaying animation speed**: The first few paths draw slowly (0.25s each), then speed up exponentially via `0.25 * exp(-linspace(0, 4, 50))`. Below 1/60s threshold, multiple paths are batched per frame. This creates a dramatic acceleration effect: slow enough to understand initially, then fast enough to build statistical confidence.
- **Progressive opacity dimming**: As more paths accumulate, each path's opacity decreases with `min(0.2, max(0.025, 1/N))`. This prevents visual clutter while maintaining a sense of density. The formula is clamped to avoid fully transparent or fully opaque extremes.
- **Histogram bar sweep before average**: A LaggedStart Succession sweeps each bar to YELLOW then back to BLUE, drawing the viewer's eye across the full distribution before revealing the average. This undocumented use of `bar.animate.set_color().build()` converts _AnimationBuilder to Animation objects.
- **Average profit as dashed vertical line**: A yellow DashedLine at the histogram's mean profit position, with text showing the dollar amount, serves as the visual punchline: "this is what the option should cost."

## Composition

- **GuessingTheFuture layout**:
  - Quote text: to_edge(UP, buff=0.5)
  - Exercise text: next_to(quote, DOWN, buff=0.5)
  - Stock axes: from `stock_price_to_today()` helper, x_length=8, y_length=4, next_to(exercise, DOWN, buff=1.0)
  - "Simulate!" text: axes center + UP*2 + RIGHT*2
- **DemonstrateSimulation layout**:
  - Left axes (stock sim): from `stock_price_simulation_graph()`, x_length=4, y_length=4, to_edge(LEFT, buff=1.0)
  - Right histogram: BarChart x_length=4, y_length=4, to_edge(RIGHT, buff=1.0)
  - Bar names: "$0", "", "$10", "", "$20", ... (alternating labels)
  - Average profit line: DashedLine from y=0 to y=1.0 at the mean x position
  - Average text: next_to line top, aligned LEFT, shifted DOWN*0.25

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Stock price path | BLUE | Historical path to "today" |
| Future path (optimistic) | GREEN | Brownian bridge to $350 |
| Future path (neutral) | GOLD | Brownian bridge to $300 |
| Future path (pessimistic) | RED | Brownian bridge to $250 |
| Strike line | WHITE | DashedLine at K=$300 |
| Simulated paths | BLUE | Progressive opacity dimming |
| Histogram bars | BLUE | Default, YELLOW during sweep |
| Average profit line | YELLOW | DashedLine, z_index=2 |
| Average text | YELLOW | font_size=TEXT_SIZE_MEDIUM |
| "Simulate!" text | YELLOW | font_size=TEXT_SIZE_MEDIUM |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Stock path Create | 2.0s | rate_func=linear |
| Each future path Create | 2.0s | rate_func=linear, 1s waits |
| First simulation path | 1.0s | rate_func=linear |
| Histogram Create | 2.0s | |
| ~550 paths total | ~5.3s | Exponentially decaying speed |
| Min batch time | 1/60s | Below this, paths are batched |
| Bar sweep | 1.0s | LaggedStart lag_ratio=0.1 |
| Average line Create | default | rate_func=linear |
| Total (GuessingTheFuture) | ~20s | |
| Total (DemonstrateSimulation) | ~15s | |

## Patterns

### Pattern: Exponentially Accelerating Monte Carlo Simulation

**What**: Runs many simulation paths with exponentially decreasing animation time per path. Uses a decay schedule `0.25 * exp(-linspace(0, 4, 50))` where early paths take 0.25s and later paths are batched at 1/60s (one frame). Each path dims to a computed opacity based on total count. The histogram updates in parallel with new path creation.
**When to use**: Monte Carlo simulations, convergence demonstrations, any visualization where many samples build up a distribution, statistical estimation showing law of large numbers.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/finding_a_fair_price.py:127-153
decay_curve = 0.25 * np.exp(-np.linspace(0, 4, 50))
schedule = [(1, t) if t >= 1 / 60 else (int(np.ceil(1 / 60 / t)), 1 / 60)
            for t in decay_curve]
schedule += [schedule[-1]] * 120
path_opacity = lambda: min(0.2, max(0.025, 1.0 / len(self.simulation_paths)))

for num_paths_this_tick, run_time in schedule:
    # dim prior paths
    self.play(*[
        self.simulation_graphs[-idx].animate.set_stroke(opacity=path_opacity())
        for idx in range(1, num_paths_this_tick + 1)], run_time=run_time)
    for _ in range(num_paths_this_tick):
        self.generate_next_path(ax)
    # create new paths and update histogram simultaneously
    self.play(
        *[Create(self.simulation_graphs[-idx], rate_func=linear) for idx in range(1, num_paths_this_tick + 1)],
        bar_chart.animate.change_bar_values([x / sum(self.histogram_counts) for x in self.histogram_counts]),
        run_time=run_time
    )
```

### Pattern: Brownian Bridge for Controlled Random Paths

**What**: Generates random stock paths that are forced to end at specific target values. Starts with a regular simulation, subtracts the drift to make it a bridge (ends at zero), then adds a linear interpolation to the desired endpoint. This gives realistic-looking paths that hit predetermined final values.
**When to use**: Showing specific outcomes of a random process, educational scenarios where you need the "lucky" and "unlucky" cases to be visually distinct, demonstrating option payoff under different market scenarios.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/finding_a_fair_price.py:35-40
brownian_rvs = [simple_stock_simulation(start_price=simulated_path[-1], sigma=0.15, seed=seed, T=0.5)
                - simulated_path[-1] for seed in [4, 1, 2]]
ts = np.linspace(0, 0.5, len(brownian_rvs[0]))
brownian_rvs = [sim - ts / 0.5 * sim[-1]
                + np.linspace(simulated_path[-1], end_point, len(sim))
                for sim, end_point in zip(brownian_rvs, [350, 300, 250])]
```

### Pattern: Histogram Bar Sweep Highlight

**What**: Uses LaggedStart with Succession to sweep each bar in a BarChart to YELLOW then back to BLUE, creating a left-to-right highlighting wave. The undocumented `.build()` method converts _AnimationBuilder objects into Animation objects for use inside Succession.
**When to use**: Drawing attention across a full distribution before revealing a summary statistic, histograms where you want the viewer to notice the shape before seeing the mean/median, any sequential highlight across chart elements.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/finding_a_fair_price.py:159-161
self.play(LaggedStart(*[Succession(bar.animate.set_color(YELLOW).build(),
                                   bar.animate.set_color(BLUE).build())
                        for bar in bar_chart.bars], run_time=1.0, lag_ratio=0.1))
```

**Critical**: The `.build()` call is undocumented in Manim CE. It converts the `_AnimationBuilder` returned by `.animate.set_color()` into an actual `Animation` object that Succession can use.

## Scene Flow

1. **GuessingTheFuture** (0-20s): Section title "fair price for an option?" fades in/out. Quote about future prices writes at top. Exercise #1 asks how to find a fair price. Stock axes with path-to-today and strike line appear. Three Brownian-bridge futures draw in green ($350), gold ($300), red ($250). "Simulate!" text appears.
2. **DemonstrateSimulation setup** (0-5s): Left stock-sim axes and right histogram appear. First path draws slowly on the left. Histogram bar for that path's bin updates.
3. **DemonstrateSimulation acceleration** (5-10s): ~550 paths draw with exponentially increasing speed. Paths progressively dim. Histogram bars update in real-time, converging toward a smooth distribution shape.
4. **DemonstrateSimulation result** (10-15s): Bar sweep highlights each histogram bar YELLOW then BLUE from left to right. Yellow dashed average-profit line draws vertically through the histogram. "Average: ~$X" text appears. Everything fades.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/finding_a_fair_price.py` (179 lines)
