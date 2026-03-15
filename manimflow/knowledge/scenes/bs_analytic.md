---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/analytic_calculation.py
project: ragibson_manim-videos
domain: [finance, probability, statistics, calculus, mathematics]
elements: [axes, function_plot, area_under_curve, dashed_line, label, title, equation, formula]
animations: [fade_in, fade_out, write, draw, transform, indicate, color_change]
layouts: [side_by_side, edge_anchored, vertical_stack]
techniques: [progressive_disclosure, scipy_integration, data_driven, helper_function]
purpose: [derivation, proof, step_by_step]
mobjects: [Text, MathTex, Tex, Axes, VGroup, DashedLine]
manim_animations: [Write, FadeIn, FadeOut, Create, TransformMatchingTex, Circumscribe]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 444
scene_classes: [AnalyticCalculation]
---

## Summary

Derives the complete Black-Scholes formula analytically by splitting the call option price into an expectation term and a probability term, solving each through separate exercises (completing the square and standard normal CDF transformations), then combining the results. Begins with 100 simulated stock paths and a lognormal distribution side-by-side, transitions to pure analytical work across three exercises, and concludes with the time-value-of-money discounting factor. The final reveal shows the full Black-Scholes formula C = D[S(0)/D * Phi(d+) - K * Phi(d-)] with a Circumscribe animation.

## Design Decisions

- **Simulation-to-analytics transition**: Opens with 100 simulated paths (opacity=0.2) next to the theoretical lognormal PDF, then shifts the distribution panel to fill the screen while fading simulations. This visually bridges the Monte Carlo approach (previous scene) to the analytical approach (this scene).
- **In-the-money paths highlighted GREEN**: Paths ending above the strike price change to GREEN with higher opacity (0.75), while the corresponding area under the PDF fills with GREEN. This dual highlighting on both panels creates an immediate visual link between "these specific paths make money" and "this area of the distribution."
- **Two-column u-substitution**: The change-of-variables is displayed in two columns with BLUE_B coloring. The left column shows the substitution definition, the right column shows the differential. A combined form then replaces both columns. This maximizes information density without requiring scrolling.
- **TransformMatchingTex for discount factor insertion**: When adding D=e^{-rt} to the d+ formula, TransformMatchingTex automatically matches "K" in the old formula to "D*K" in the new formula, animating the insertion. This is more elegant than manual positioning but requires careful LaTeX substring isolation.
- **Color-coded time value of money**: Future values are BLUE, present values are YELLOW. The bullet points use set_color_by_tex to color "future option price" BLUE and "current value" YELLOW, maintaining this semantic mapping when explaining discounting.
- **Final formula Circumscribe**: The completed Black-Scholes formula gets a Circumscribe animation before the title "Black-Scholes-Merton Formula for Pricing Options" appears in YELLOW. This creates a dramatic reveal moment for the derivation's conclusion.

## Composition

- **Distribution form header**: to_edge(UP, buff=0.25)
- **Left axes (simulations)**: from stock_price_simulation_graph(), x_length=4, y_length=4, to_edge(LEFT, buff=1.0), shift(DOWN*0.25)
- **Right axes (distribution)**: x_length=4, y_length=4, to_edge(RIGHT, buff=1.0), shift(DOWN*0.25)
- **Exercise labels**: next_to(header, DOWN, buff=0.3), to_edge(LEFT, buff=0.5 or 1.0)
- **Answer bodies**: next_to(exercise, DOWN, buff=0.3 or 0.5), to_edge(LEFT, buff=0.5 or 1.0)
- **U-substitution**: next_to(answer, DOWN, buff=2.0), to_edge(LEFT, buff=0.5), BLUE_B
- **Discount exp plot**: x_range=[0, 10, 2], y_range=[1.00, 1.51], x_length=4, y_length=3, next_to(footer, DOWN, buff=1.0)
- **Final formula**: centered at ORIGIN + UP*0.75
- **Final footer (d+, d-, D)**: centered at ORIGIN + DOWN
- **BSM title**: ORIGIN + UP*2.0, YELLOW

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Simulated paths | BLUE | set_stroke(opacity=0.2) |
| In-the-money paths | GREEN | set_stroke(opacity=0.75) |
| Distribution curve | BLUE | |
| Strike lines | WHITE | DashedLine |
| Area above strike | GREEN | opacity=0.5 |
| "Calculate analytically!" | YELLOW | font_size=TEXT_SIZE_MEDIUM |
| Exercise labels | YELLOW | "Exercise #5:", "Exercise #6:" |
| U-substitution | BLUE_B | Side annotation |
| Discount plot | BLUE | exp(rt) curve |
| Future value text | BLUE | set_color_by_tex |
| Present value text | YELLOW | set_color_by_tex |
| D=e^{-rt} formula | WHITE | Added to footer |
| Final formula | WHITE | Circumscribed |
| BSM title | YELLOW | font_size=TEXT_SIZE_LARGE |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Axes Create | 2.0s | Both panels |
| 100 paths Create | 2.0s | All simultaneously |
| Distribution Create | 2.0s | rate_func=linear |
| Strike lines Create | 1.0s | Both simultaneously |
| Green highlight | 1.0s | Paths + area simultaneously |
| Exercise Write | 1.0s-3.0s | |
| Hint countdowns | 5.0s | |
| Derivation lines Write | default | 1s waits |
| U-substitution Write | default per line | 1s waits |
| Discount plot Create + graph | 1.0s | rate_func=linear |
| Circumscribe final formula | default | |
| Total video | ~5 minutes | Longest scene in series |

## Patterns

### Pattern: Simulation-to-Analytics Visual Transition

**What**: Shows simulated paths and the theoretical distribution side-by-side, highlights the paths that end in-the-money (GREEN) and the corresponding PDF area (GREEN), then fades the simulations and shifts the distribution panel to center stage. This creates a narrative bridge from "we approximated via simulation" to "now we'll calculate exactly."
**When to use**: Transitioning from numerical/Monte Carlo methods to analytical/closed-form solutions, showing that a distribution matches empirical data, bridging intuition (simulation) to rigor (derivation) in mathematical finance or statistics.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/analytic_calculation.py:81-99
profit_path_indices = [i for i, p in enumerate(simulation_paths) if p[-1] >= strike]
right_pdf_area = distribution_ax.get_area(distribution_graph,
    x_range=(strike, stock_range[1]), color=GREEN, opacity=0.5)
self.play(
    *[simulation_graphs[i].animate.set_stroke(opacity=0.75, color=GREEN) for i in profit_path_indices],
    FadeIn(right_pdf_area), run_time=1.0
)

# Fade simulations, shift distribution to center
distribution_group = VGroup(distribution_ax, distribution_labels, distribution_graph, strike_line_right, right_pdf_area)
self.play(*[FadeOut(x) for x in [ax, labels, strike_line_left, *simulation_graphs]],
          distribution_group.animate.to_edge(LEFT, buff=0.5), run_time=1.0)
```

### Pattern: TransformMatchingTex for Formula Evolution

**What**: Uses TransformMatchingTex to animate the insertion of new terms into an existing formula. By isolating substrings in MathTex, Manim can match "K" in the old version to "D * K" in the new version and smoothly animate the insertion. Requires careful LaTeX substring isolation in both the old and new MathTex objects.
**When to use**: Evolving a formula by adding terms (like a discount factor), showing how a simple formula becomes more complex, any mathematical derivation where one variable gets replaced by a function of itself.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/analytic_calculation.py:410-418
extended_footer = MathTex(
    r"\text{where } d_+ = { \ln\left(S(0) \over ", r"K",
    r"\right) + {\sigma^2 \over 2} \cdot t \over \sigma \cdot \sqrt{t} }, "
    r"\hspace{0.5em} d_- = d_+ - \sigma \cdot \sqrt{t}, \hspace{0.5em} D = e^{-rt}",
    font_size=MATH_SIZE_SMALL
)
final_footer = MathTex(
    r"\text{where } d_+ = { \ln\left(S(0) \over ", r"D \cdot K",
    r"\right) + {\sigma^2 \over 2} \cdot t \over \sigma \cdot \sqrt{t} }, "
    r"\hspace{0.5em} d_- = d_+ - \sigma \cdot \sqrt{t}, \hspace{0.5em} D = e^{-rt}",
    font_size=MATH_SIZE_SMALL
)
self.play(TransformMatchingTex(extended_footer, final_footer))
```

### Pattern: Color-Coded Time Value Explanation

**What**: Uses set_color_by_tex with isolated substrings to color "future" terms BLUE and "present/current" terms YELLOW in bullet point explanations. The MathTex substrings_to_isolate parameter ensures the color targets are findable. This creates a consistent visual language for the discounting concept.
**When to use**: Explaining present value vs future value in finance, time-based comparisons, any paired concept where "before" and "after" or "input" and "output" need distinct colors throughout a text block.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/analytic_calculation.py:384-394
bullet_points = VGroup(
    MathTex(r"\text{Need to:}", font_size=MATH_SIZE_MEDIUM),
    MathTex(r"\text{... future option price ...current value ...}", font_size=MATH_SIZE_MEDIUM,
            substrings_to_isolate=[r"\text{future option price }", r"\text{current value }"])
    .set_color_by_tex("future option price", BLUE).set_color_by_tex("current value", YELLOW),
    MathTex(r"\text{... current price ...future value ...}", font_size=MATH_SIZE_MEDIUM,
            substrings_to_isolate=[r"\text{current price }", r"\text{future value }"])
    .set_color_by_tex("current price", YELLOW).set_color_by_tex("future value", BLUE)
).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
```

## Scene Flow

1. **Simulation + distribution** (0-30s): Section title. Left: 100 simulated paths (opacity=0.2) on stock axes. Right: lognormal PDF curve on distribution axes. S(t) distribution formula at top. Strike lines appear on both panels. In-the-money paths turn GREEN, corresponding PDF area fills GREEN. "Calculate it all analytically!" text. Simulations fade, distribution shifts left.
2. **Option price formula** (30-45s): C-tilde = E[S(t)-K | S(t)>K] writes. Split into expectation and probability terms. Distribution fades.
3. **Exercise #5: Probability** (45-90s): Calculate P[S(t)>K]. Hint with 5s countdown. Step-by-step: take logs, subtract mean, divide by sigma*sqrt(t), arrive at standard normal CDF. Result: 1 - Phi((ln(K/S0) + sigma^2/2 * t) / (sigma*sqrt(t))). Intermediate lines compressed.
4. **Exercise #6: Expectation** (90-160s): Calculate E[S(t) | S(t)>K]. Hint with 5s countdown. Expand integral with lognormal PDF. U-substitution in two blue columns, combined into one. Main integral continues: completing square in exponent, factor out S(0), recognize normal CDF. Result: S(0) * [1 - Phi(...)].
5. **Combining** (160-200s): C-tilde formula with both terms substituted. Simplify using 1-Phi(x) = Phi(-x) and -ln(K/S0) = ln(S0/K). Arrive at S(0)*Phi(d+) - K*Phi(d-). Shorthand for d+, d- writes below.
6. **Discounting** (200-250s): Time value of money: exp(rt) growth curve on small axes. Cash(t) = e^{rt}*Cash(0) in blue/yellow. D=e^{-rt} added to formula footer. Two bullet points explain: convert future price to present value (D*C-tilde), convert current price to future value (S(0)/D). Final formula: C = D[S(0)/D * Phi(d+) - K * Phi(d-)]. D*K replaces K in d+ via TransformMatchingTex. Circumscribe on formula. "Black-Scholes-Merton Formula" title in YELLOW. Everything fades.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/analytic_calculation.py` (444 lines)
