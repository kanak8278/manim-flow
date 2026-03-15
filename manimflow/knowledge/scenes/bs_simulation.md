---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/how_to_simulate.py
project: ragibson_manim-videos
domain: [finance, probability, statistics, mathematics]
elements: [axes, function_plot, label, title, equation, formula, area_under_curve, arrow]
animations: [fade_in, fade_out, write, draw, transform, replacement_transform, indicate, animate_parameter]
layouts: [centered, edge_anchored, vertical_stack]
techniques: [value_tracker, add_updater, progressive_disclosure, scipy_integration]
purpose: [derivation, step_by_step, exploration, demonstration]
mobjects: [Text, MathTex, Tex, Axes, Paragraph, VGroup, ValueTracker, Arrow]
manim_animations: [Write, FadeIn, FadeOut, Create, ReplacementTransform, Circumscribe]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 331
scene_classes: [DesiredSimulationQualities]
---

## Summary

Motivates the lognormal distribution for stock price simulation by building three requirements one at a time: prices must be non-negative, moves must be relative, and relative changes must compound. Uses a normal distribution that widens via ValueTracker to show the negative-price problem, real stock screenshots (NVDA vs HD) to demonstrate scale differences, and step-by-step compounding arithmetic to motivate the exponential function. Culminates in an interactive exercise leading to the lognormal distribution, with a side-by-side normal-to-lognormal transformation showing "no negatives" and "compounding returns" as annotated advantages.

## Design Decisions

- **Three qualities as a numbered checklist**: Using a Paragraph with three lines that individually appear and gray out after discussion creates a progress-tracker feel. The viewer always knows where they are in the argument. Each quality grays out (set_color(GRAY)) once covered, then all restore to WHITE before the exercise.
- **ValueTracker to widen normal distribution**: Animating the scale parameter from 5 to 10 makes the negative-price problem emerge dynamically rather than being stated. The viewer watches the bell curve's left tail creep past zero, making the flaw visceral.
- **Shaded negative area in RED**: The area under the curve for x<0 gets a colored fill at opacity=0.75, directly showing "this is the probability of impossible negative prices." This is the same get_area() technique used throughout the series for highlighting probability regions.
- **Real stock screenshots for scale comparison**: Showing NVDA (high growth, lower price) vs HD (lower growth, higher price) with yellow rectangles around the price vs return figures demonstrates that absolute prices are misleading. This grounds the mathematical argument in real data.
- **Compounding arithmetic table**: Left column (text) and right column (math) create a two-column proof layout. Each row builds on the previous, showing $100 * 1.10 = $110, then $110 * 1.10 = $121, making the multiplicative nature of returns obvious.
- **Exercise with timed hint reveal**: The exercise prompt appears first, then a countdown "(revealed in 5 seconds)" before the hint, giving viewers time to attempt the problem. This pedagogical pattern recurs across the entire series.
- **Normal-to-lognormal transformation with annotations**: The normal distribution (kept as gray ghost) transforms into the lognormal, with RED arrow pointing to "No negatives!" on the left and GREEN arrow pointing to "Compounding returns!" on the right. The annotations directly map the mathematical properties to the three requirements established earlier.

## Composition

- **Title and qualities**: Title at UP buff=0.5. Paragraph with line_spacing=0.75, aligned to title's UP and LEFT edges.
- **Normal distribution axes**: x_range=[-10, 50.1, 10], y_range=[0.0, 0.08, 0.02], x_length=6, y_length=4, next_to(title, DOWN, buff=1.0)
- **Negative area**: get_area() with x_range=(-10, 0), color=RED, opacity=0.75
- **Stock screenshots**: scale=1.25, to_edge(LEFT/RIGHT, buff=0.5), shift(DOWN*0.5)
- **Highlight rectangles**: Manually positioned at specific pixel coordinates matching the screenshot layout
- **Compounding table**: Left text aligned_edge=LEFT, aligned RIGHT to ORIGIN, shifted LEFT*0.5. Right math next_to LEFT buff=0.5.
- **Exercise exp(x) plot**: x_range=[-2, 2.01], y_range=[0, 8.01], x_length=3, y_length=2, to_edge(DOWN, buff=0.5).to_edge(LEFT, buff=2.0)
- **Lognormal axes**: x_range=[-10, 60.1, 10], y_range=[0.0, 0.05], x_length=6, y_length=4, centered horizontally
- **Lognormal annotations**: RED arrow start=(-20, 0.025), GREEN arrow start=(55, 0.025)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Normal distribution | BLUE | plot_line_graph line_color |
| Original normal (ghost) | GRAY | copy().set_stroke(opacity=0.5) |
| Negative price area | RED | opacity=0.75 |
| "Negative Stock Prices?" | RED | font_size=TEXT_SIZE_MEDIUM |
| "No negatives!" annotation | RED | Arrow and Text |
| "Compounding returns!" annotation | GREEN | Arrow and Text |
| Stock comparison warning | RED | font_size=TEXT_SIZE_MEDIUM |
| Highlight rectangles | YELLOW | On stock screenshots |
| Exercise label | YELLOW | "Exercise #2:" |
| exp(x) graph | BLUE | |
| Lognormal dist | BLUE | z_index=1 (on top of ghost) |
| Quality text (covered) | GRAY | set_color(GRAY) after discussion |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Normal dist Create | 2.0s | |
| Scale widen (5 to 10) | 2.0s | ValueTracker animate |
| Negative area FadeIn | 1.0s | rate_func=linear |
| Stock images FadeIn | default | |
| Rectangle highlights Create | default | |
| Compounding rows Write | default | 0.5s waits |
| Exercise Write | 3.0s | |
| Hint countdown wait | 5.0s | Viewer pause |
| exp(x) graph Create | 1.0s | rate_func=linear |
| Normal to lognormal transform | 2.0s | ReplacementTransform |
| Circumscribe mu, sigma | default | At end |
| Total video | ~3-4 minutes | Long pedagogical scene |

## Patterns

### Pattern: ValueTracker-Animated Distribution Parameter

**What**: A ValueTracker controls a distribution parameter (scale/sigma). The distribution plot uses add_updater to rebuild from the current tracker value every frame. When the tracker animates, the distribution smoothly morphs, revealing properties like negative-area probability that emerge only at certain parameter values.
**When to use**: Exploring how distribution shape changes with parameters, showing failure modes of statistical models, demonstrating sensitivity to variance/spread in probability distributions, interactive parameter exploration.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/how_to_simulate.py:77-91
scale_tracker = ValueTracker(5.0)
plot_xs = np.linspace(*ax.x_range[:2], 1000)
normal_dist = ax.plot_line_graph(plot_xs, norm.pdf(plot_xs, loc=20, scale=scale_tracker.get_value()),
                                 line_color=BLUE, add_vertex_dots=False)

normal_dist.add_updater(
    lambda x: x.become(ax.plot_line_graph(plot_xs, norm.pdf(plot_xs, loc=20, scale=scale_tracker.get_value()),
                                          line_color=BLUE, add_vertex_dots=False))
)
self.play(scale_tracker.animate.set_value(10.0), run_time=2.0)
normal_dist.clear_updaters()
```

### Pattern: Ghost Distribution Overlay for Before/After

**What**: Before transforming a distribution plot, copy it and set it to gray with reduced opacity. This "ghost" stays in place while the original transforms into a new shape, giving the viewer a visual reference for comparison. The gray copy is added to the scene (self.add) rather than played in, so it appears instantly.
**When to use**: Normal-to-lognormal transformations, any distribution comparison, before/after overlays for function transformations, showing how a model changes after training.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/how_to_simulate.py:23-28
# (from create_normal_lognormal_comparison helper)
normal_dist_original = price_distribution.copy().set_stroke(opacity=0.5).set_color(GRAY)

# In scene:
self.add(normal_dist_original)  # instant, no animation
self.play(ReplacementTransform(price_distribution, lognormal_dist), run_time=2.0)
```

### Pattern: Paragraph as Progressive Checklist

**What**: Manim's Paragraph creates multi-line text where each line is accessible via `.chars[i]`. Lines appear individually during different parts of the scene, then gray out when their topic is complete, functioning as a progress tracker. At the end, all lines restore to WHITE before a final exercise.
**When to use**: Building up a list of requirements, step-by-step arguments where you need to show progress, any educational sequence with 3-5 points that are covered one-by-one.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/how_to_simulate.py:309-326
qualities_text = Paragraph(
    "#1: Prices should not go negative",
    "#2: Price moves should be relative",
    "#3: Relative changes should compound",
    font_size=TEXT_SIZE_SMALL, alignment="left", line_spacing=0.75
).move_to(title_text, aligned_edge=UP).align_to(title_text, LEFT)

first_quality, second_quality, third_quality = qualities_text.chars

# After discussing each quality:
self.play(first_quality.animate.set_color(GRAY))
# ... discuss second quality ...
self.play(second_quality.animate.set_color(GRAY))
# ... restore all at end:
self.play(*[t.animate.set_color(WHITE) for t in qualities_text])
```

### Pattern: Timed Exercise with Countdown Hint

**What**: An exercise prompt appears, followed by a hint with a "(revealed in N seconds)" countdown. After waiting N seconds, the countdown text is replaced with the actual hint via FadeOut/Write. This creates natural pause points for viewers to attempt the problem themselves.
**When to use**: Educational videos with exercises, interactive derivations, any pedagogical content where the viewer should try before seeing the answer. This pattern recurs throughout the Black-Scholes series (Exercises #1-#6).

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/how_to_simulate.py:189-205
hint_label = Text("Hint:", font_size=TEXT_SIZE_MEDIUM).next_to(exercise_text, DOWN, buff=0.5)
hint_countdown = (Text("(revealed in 5 seconds)", font_size=TEXT_SIZE_MEDIUM)
                  .next_to(hint_label, RIGHT, buff=0.25).align_to(hint_label, UP))
self.play(Write(hint_label))
self.play(Write(hint_countdown))
self.wait(5.0)

hint_text = Tex(r"...", font_size=MATH_SIZE_MEDIUM
                ).next_to(hint_label, RIGHT, buff=0.25).align_to(hint_label, UP)
self.play(FadeOut(hint_countdown))
self.play(Write(hint_text))
```

## Scene Flow

1. **Title and first quality** (0-30s): "How to Simulate Stock Prices?" writes. Normal distribution plots on axes with dollar-sign x-labels. ValueTracker widens the scale from 5 to 10, revealing negative-price probability. Red shaded area appears below $0. First quality text appears via ReplacementTransform from the title. Quality grays out.
2. **Second quality** (30-60s): NVDA and HD stock screenshots appear side-by-side. Yellow rectangles highlight price vs return numbers. "Stock prices cannot be compared directly!" warning appears. Rectangles move from price to return fields. Second quality text writes, then grays.
3. **Third quality** (60-80s): Compounding arithmetic table shows $100 growing through three 10% increases. Third quality text writes, then grays.
4. **Exercise and lognormal** (80-150s): All qualities restore to white. Exercise #2 asks to construct S(t). Hint countdown (5s), then "adding into multiplying" hint. exp(x) plot and identity write. "Consider S(t)/S(0) ~ exp(N(mu, sigma^2))" formula appears.
5. **Lognormal discussion** (150-200s): "Lognormal Distribution" label and equivalence formula. Normal distribution plots, then transforms to lognormal with gray ghost overlay. "No negatives!" (RED) and "Compounding returns!" (GREEN) annotations with arrows. mu and sigma are Circumscribed to flag them as the next topic.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/how_to_simulate.py` (331 lines)
