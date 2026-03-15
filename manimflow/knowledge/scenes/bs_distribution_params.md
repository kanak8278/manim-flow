---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/determining_distribution_parameters.py
project: ragibson_manim-videos
domain: [finance, probability, statistics, calculus, mathematics]
elements: [axes, function_plot, label, title, equation, formula, area_under_curve]
animations: [fade_in, fade_out, write, draw, transform, replacement_transform, indicate, animate_parameter]
layouts: [centered, edge_anchored, vertical_stack]
techniques: [value_tracker, add_updater, progressive_disclosure, scipy_integration]
purpose: [derivation, proof, step_by_step]
mobjects: [Text, MathTex, Tex, Axes, VGroup, ValueTracker, DashedLine]
manim_animations: [Write, FadeIn, FadeOut, Create, ReplacementTransform, Indicate, Circumscribe, Transform]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 442
scene_classes: [DeterminingDistributionMu, DeterminingDistributionSigmaAndSt]
---

## Summary

Derives the two parameters of the lognormal stock price distribution through a sequence of mathematical exercises. First derives the lognormal PDF from the normal PDF via change-of-variables. Then determines mu = -sigma^2/2 through a lengthy integral manipulation involving completing the square, showing that the expectation of a lognormal variable equals exp(sigma^2/2). Sigma is discussed as historical volatility, demonstrated by animating future stock paths at different sigma values (10%, 30%, 20%) via ValueTracker. Finally generalizes from S(1) to S(t) through an inductive argument about adding independent normals.

## Design Decisions

- **Multi-step derivation with progressive reveal**: Each line of the mathematical derivation writes one at a time with 1-second waits. This prevents overwhelming the viewer with a wall of equations. Lines that become intermediate are faded out or shifted to make room for the next step.
- **Completing-the-square shown as blue side-note**: The key algebraic trick (completing the square to get a normal PDF integrand) is shown in BLUE_B as a side annotation, visually separated from the main derivation flow. This signals "here's a tool we're using" without cluttering the main argument.
- **U-substitution shown then cleared**: The change-of-variables is displayed in BLUE_B, used for the next step, then FadeOut'd. This mirrors how a whiteboard lecture works: write the substitution, use it, erase it.
- **Sigma demonstrated via real stock path + simulation**: Rather than defining sigma abstractly, the scene shows a real stock path to "today" and then three different future simulations at sigma=10%, 30%, and 20%. The viewer sees that 10% is too calm, 30% too wild, and 20% matches the historical behavior.
- **ValueTracker for sigma with updater on both graph and text**: Both the future stock simulation and the "sigma = X%" label rebuild every frame as sigma changes. The `create_future_graph_and_text` helper returns both objects, keeping them synchronized.
- **S(t) generalization via pattern recognition**: Rather than a formal proof, S(1) to S(2) is shown by substitution, then S(2) to S(3) by replacing "2" with "3" via Transform on specific MathTex submobjects, then "3" becomes "t". This index-based Transform on submobjects is a gross hack (per the comment) but effectively communicates the inductive step.
- **Fading and shifting for space management**: The derivation frequently fades out earlier steps and shifts remaining work to the top of the screen. This simulates scrolling on a whiteboard and keeps the active working area uncluttered.

## Composition

- **Exercise labels**: to_edge(UP, buff=0.5), to_edge(LEFT, buff=0.5 or 1.0)
- **Exercise text**: next_to(label, RIGHT, buff=0.25), aligned to label top
- **Answer body**: next_to(answer_start, DOWN, buff=0.5), aligned LEFT
- **Hint structure**: hint_label next_to(exercise, DOWN, buff=0.5), countdown next_to(hint, RIGHT, buff=0.25)
- **Normal/lognormal axes**: x_range=[-10, 60.1, 10], y_range=[0.0, 0.05], x_length=6, y_length=4, centered
- **U-substitution notes**: BLUE_B, next_to derivation body DOWN buff=2.0, shifted LEFT*2.0
- **Sigma demonstration axes**: from stock_price_to_today() helper, x_length=8, y_length=4
- **Sigma text**: axes center + UP*2 + RIGHT*2
- **S(t) math lines**: next_to(header, DOWN, buff=0.25), arranged DOWN aligned LEFT

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Exercise labels | YELLOW | "Exercise #3:", "Exercise #4:" |
| Hint labels | WHITE | "Hint:", "Hint #1:", "Hint #2:" |
| Countdown text | WHITE | "(revealed in 5 seconds)" |
| Main derivation | WHITE | MathTex default |
| Side annotations | BLUE_B | U-substitution, completing square, goals |
| Mu highlight | YELLOW | Indicate + set_color on Circumscribed mu |
| Sigma highlight | YELLOW | animate.set_color on S1_header sigma |
| Normal distribution | BLUE | plot_line_graph line_color |
| Ghost normal | GRAY | set_stroke(opacity=0.5) |
| Lognormal areas | YELLOW | Bounded area between PDFs |
| Future stock simulation | GREEN | plot_line_graph line_color |
| Footnote | WHITE | font_size=TEXT_SIZE_TINY, scaled 0.9 |
| "1" in S(1) | BLUE | set_color_by_tex |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Exercise label Write | default | |
| Exercise text Write | 3.0s | Longer for multi-line |
| Hint countdown wait | 5.0s | Per hint |
| Derivation line Write | default | 1s waits between |
| Normal to lognormal | 2.0s | ReplacementTransform |
| Bounded area FadeIn | default | rate_func=linear |
| Sigma animate 0.1 to 0.3 | 2.0s | ValueTracker |
| Sigma animate 0.3 to 0.2 | 2.0s | ValueTracker |
| S(t) line Write | default | 1s waits |
| S(2) to S(3) Transform | default | On submobject indices |
| Total (DeterminingDistributionMu) | ~3 minutes | Heavy derivation |
| Total (DeterminingDistributionSigmaAndSt) | ~2 minutes | |

## Patterns

### Pattern: Multi-Step Mathematical Derivation with Space Reclamation

**What**: A long derivation is written line-by-line, with earlier intermediate steps faded out and remaining work shifted to the top of the screen when space runs low. The key technique is animating specific submobjects to new positions while fading others, then continuing to write below the repositioned work. Side annotations in BLUE_B appear temporarily to explain algebraic tricks.
**When to use**: Any mathematical proof or derivation longer than 4-5 lines, integral calculations, algebraic manipulations where intermediate steps need to be shown then discarded, completing-the-square or u-substitution demonstrations.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/determining_distribution_parameters.py:260-286
# Fade earlier work, shift current line to top
self.play(expectation_body[3].animate.align_to(expectation_body[0].get_top() + UP * 0.025, UP),
          normal_goal.animate.shift(UP * 1.0),
          *[FadeOut(x) for x in (
              expectation_body[0][15:],
              line2_replacement,
              expectation_body[2]
          )])

# Replace shifted line with fresh MathTex (easier to work with)
new_expectation_body = MathTex(
    r"&= \int ...", r"&= \int ...", # multiple lines
    font_size=MATH_SIZE_SMALL
).move_to(expectation_body[3].get_left(), LEFT).align_to(expectation_body[3], UP)
self.remove(expectation_body[3])
self.add(new_expectation_body[0])
```

### Pattern: ValueTracker Sigma with Dual Updater (Graph + Text)

**What**: A ValueTracker controls a parameter (sigma) that affects both a graph plot and a text label. A helper function returns both objects computed from the current tracker value. Both use add_updater with lambda that calls the helper, keeping them synchronized. The helper recreates both mobjects from scratch each frame.
**When to use**: Any parameter exploration where a numeric display and a graph need to stay synchronized, sensitivity analysis visualizations, interactive distribution parameter tuning, volatility demonstrations.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/determining_distribution_parameters.py:364-390
def create_future_graph_and_text(sigma):
    graph = ax.plot_line_graph(
        x_values=np.linspace(0.5, 1.0, len(simulated_path)),
        y_values=simple_stock_simulation(start_price=simulated_path[-1], sigma=sigma, seed=1, T=0.5),
        line_color=GREEN, add_vertex_dots=False
    )
    text = MathTex(rf"\sigma = {future_sigma.get_value() * 100:.1f}\%", font_size=MATH_SIZE_MEDIUM)
    return graph, text.move_to(ax.get_center() + UP * 2.0 + RIGHT * 2.0)

future_sigma = ValueTracker(0.1)
future_graph.add_updater(
    lambda g: g.become(create_future_graph_and_text(future_sigma.get_value())[0])
)
sigma_text.add_updater(
    lambda t: t.become(create_future_graph_and_text(future_sigma.get_value())[1])
)
self.play(future_sigma.animate.set_value(0.3), run_time=2.0)
```

### Pattern: Inductive Generalization via Submobject Transform

**What**: A mathematical statement for a specific case (t=2) is generalized by Transform-ing the specific submobjects containing "2" into "3", then "t". The submobjects are addressed by index into the MathTex object. This is fragile (the comment calls it a "gross hack") but effective for showing pattern recognition in inductive arguments.
**When to use**: Generalizing from n=2 to n=k to n in mathematical induction, showing how a formula extends from a specific case to the general case, any "and by the same argument..." step in a derivation.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/determining_distribution_parameters.py:429-433
for new_tex in ["3", "t"]:
    self.play(*[Transform(x, MathTex(new_tex, font_size=MATH_SIZE_SMALL).move_to(x))
                for x in [math_lines[-1][i] for i in (2, 22, 27)]])
    self.wait(1.0)
```

**Critical**: The indices (2, 22, 27) are manually determined by inspecting the MathTex submobject structure. These are brittle and will break if the LaTeX string changes. Always verify indices when adapting this pattern.

## Scene Flow

1. **Lognormal PDF derivation** (0-40s): Exercise #3 asks for PDF of exp(N(mu,sigma^2)). Normal PDF reminder shown then cleared. Step-by-step derivation via CDF differentiation: P[X<=x] = P[Y<=ln(x)] = F_Y(ln(x)), then chain rule gives f_Y(ln(x)) / x. Final lognormal PDF formula.
2. **Consider S(1)** (40-70s): Header "S(t)/S(0) ~ exp(N(mu,sigma^2))" writes. Mu and sigma Circumscribed. t transforms to 1 (blue). Mu highlighted yellow. Normal-to-lognormal transformation reappears with ghost overlay. Yellow bounded areas shown between the two PDFs to highlight the difference.
3. **Exercise mu** (70-120s): Exercise #4 asks for mu that keeps E[S(1)]=S(0). Two hints with timed reveals (5s, 10s). Answer begins: take mu=0, expand expectation. Key integrand isolated with Indicate.
4. **Expectation integral** (120-200s): Full screen derivation of E[exp(N(0,sigma^2))]. U-substitution (u=ln(x)) shown in blue, used, cleared. Completing the square shown in blue. Line-by-line algebraic manipulation until integral becomes a standard normal PDF = 1. Result: exp(sigma^2/2). Formula becomes S(1)/S(0) ~ exp(N(-sigma^2/2, sigma^2)).
5. **Sigma discussion** (200-240s): Sigma highlighted yellow in header. Stock path to "today" with three future simulations at sigma=10%, 30%, 20%. ValueTracker animates sigma with graph and text updaters. Footnote about historical vs implied volatility.
6. **S(t) generalization** (240-270s): "What does S(t) look like?" header. S(1) and S(2) formulas written. S(2) expanded via substitution. Independent normals add: N+N = N(2mu, 2sigma^2). All intermediate lines fade, S(2) result centered. "2" transforms to "3" then "t" via submobject indices.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/determining_distribution_parameters.py` (442 lines)
