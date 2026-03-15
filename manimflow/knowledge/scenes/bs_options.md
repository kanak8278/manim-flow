---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/what_is_an_option.py
project: ragibson_manim-videos
domain: [finance, economics, probability]
elements: [axes, function_plot, label, title, equation, brace, arrow, dot, group]
animations: [fade_in, fade_out, write, transform, indicate, color_change]
layouts: [centered, edge_anchored, vertical_stack, side_by_side]
techniques: [helper_function, progressive_disclosure]
purpose: [definition, demonstration, step_by_step]
mobjects: [Text, MarkupText, MathTex, Tex, Axes, Square, Circle, Triangle, VGroup, BraceBetweenPoints, DashedLine]
manim_animations: [Write, FadeIn, FadeOut, Create, Transform, Flash, ApplyWave, LaggedStart]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 295
scene_classes: [WhatIsAStock, StockSimulation, WhatIsAnOption]
---

## Summary

Explains stocks and options from first principles using visual metaphors. A company is shown as a grid of blue squares (shares), with one square breaking off as a red "share" to illustrate ownership. A customer-company exchange demonstrates value flow. Stock price dynamics are shown with a simulated path and real Netflix history. The option definition uses color-coded MarkupText with an explicit Apple stock example, then builds a call option payoff diagram with a hockey-stick shape and premium brace annotation.

## Design Decisions

- **Grid of squares for company shares**: A 3x4 grid of filled squares makes "fractional ownership" tangible. Breaking one square off and recoloring it RED immediately communicates the share concept without any math. The opacity-dimming of the original square reinforces that the share came FROM the company.
- **Color-coded option definition with MarkupText**: Using HTML-style span tags with foreground colors (YELLOW for "option", GREEN for "predetermined price", BLUE for "specific date") creates an inline-highlighted definition that mirrors how textbooks present key terms. This is more effective than showing the whole text in one color and highlighting afterward.
- **Flat price oscillation before full simulation**: Before showing the time series, a flat horizontal line at $100 bounces up/down 0.1 units to illustrate that a price represents buyer-seller agreement. This builds intuition for WHY prices move before showing HOW they move.
- **Payoff diagram with manually shifted y-axis**: The y-axis is manually repositioned to sit at the strike price ($300) rather than at x=0, which matches the standard finance convention for payoff diagrams. This is a deliberate hack to avoid Manim's default origin placement.
- **ApplyWave on example text synchronized with graph drawing**: When the profit and worthless cases are plotted, the corresponding example text gets an ApplyWave animation. This cross-references the verbal example with the visual plot, reducing cognitive load.
- **Premium introduced via downward shift**: The entire payoff curve shifts down by the premium amount rather than being redrawn, visually communicating that the premium is a constant cost subtracted from all outcomes.

## Composition

- **WhatIsAStock layout**:
  - Company grid: centered at ORIGIN, 3x4 squares, side_length=0.4, spacing=0.4
  - Company label: next_to grid DOWN buff=0.3
  - Share block: moves to LEFT*4, aligned to company bottom
  - Customer circle: RIGHT*4, radius=0.5, aligned to company bottom
- **StockSimulation axes**: x_range=[0, 1.01], y_range=[80, 120.1], x_length=8, y_length=6, to_edge(DOWN)
- **WhatIsAnOption definition**: arranged DOWN, aligned_edge=LEFT, buff=0.25, to_edge(UP)
- **Payoff diagram axes**: x_range=[260, 340.1, 10], y_range=[-20, 40.1, 10], x_length=6, y_length=4.25, to_edge(DOWN, buff=0.25)
  - Y-axis manually shifted to x=300 (strike price)
  - X-axis labels positioned with label_direction=UP
  - Dollar sign labels on both axes via manual add_labels hack
- **Option premium brace**: BraceBetweenPoints scaled 0.5, positioned at x=$275

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Company blocks | BLUE | fill_opacity=0.7 |
| Share block | RED | Single square broken off |
| Company product | ORANGE | Triangle, fill_opacity=0.7 |
| Customer | GREEN | Circle, fill_opacity=0.7 |
| Dollar signs | YELLOW | font_size=TEXT_SIZE_SMALL |
| Share flash | YELLOW | stroke_width=3 |
| Stock price line | BLUE | Simulated path |
| Option keyword | YELLOW | MarkupText span foreground |
| Strike price keyword | GREEN | MarkupText span foreground |
| Expiry date keyword | BLUE | MarkupText span foreground |
| Payoff line | BLUE | z_index=1 |
| Axis labels background | BLACK | stroke_width=4.0 for visibility |

Color strategy: The option definition uses a three-color system (YELLOW/GREEN/BLUE) that maps to the three key attributes of an option (right, strike, date). The payoff diagram uses BLUE to stay consistent with the stock price color.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Company FadeIn | default | + 1s wait |
| Share break-off | default | animate.move_to |
| Stock flat price oscillation | 0.25s each | 4 up-down cycles |
| Stock simulation Create | 2.0s | rate_func=linear |
| Option definition Write | default per line | 0.5s waits between |
| Example text Write | 0.25s label, default body | |
| Payoff right side Create | 2.0s | rate_func=linear, with ApplyWave |
| Payoff left side Create | 2.0s | rate_func=linear, with ApplyWave |
| Premium shift | default | animate.shift |
| Total (WhatIsAStock) | ~18s | |
| Total (StockSimulation) | ~15s | |
| Total (WhatIsAnOption) | ~30s | |

## Patterns

### Pattern: Grid-of-Squares Ownership Metaphor

**What**: A VGroup of small filled squares arranged in a grid represents fractional ownership of a whole. One square is copied, recolored, and animated to a new position while the original dims, visually communicating "this piece came from that whole." Uses manual positioning with RIGHT*j and UP*i offsets.
**When to use**: Explaining shares/equity, pie charts without the pie, any concept where a part is extracted from a whole (memory allocation, resource partitioning, tokenization).

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/what_is_an_option.py:18-39
company_blocks = VGroup([
    Square(side_length=0.4, color=BLUE, fill_opacity=0.7).shift(RIGHT * j * 0.4 + UP * i * 0.4)
    for i in range(3) for j in range(4)
])
company_blocks.move_to(ORIGIN)

# breaking off one of the shares
share_block = company_blocks[0].copy()
share_block.set_color(RED)
self.play(
    share_block.animate.move_to(LEFT * 4).align_to(company_blocks, DOWN),
    company_blocks[0].animate.set_opacity(0.3)
)
```

### Pattern: MarkupText with Inline Color Highlighting

**What**: Uses MarkupText with HTML-style `<span foreground="COLOR">` tags to create text with multiple inline colors. Each key term gets its own color, creating a textbook-style highlighted definition. More readable than building separate Text objects and positioning them manually.
**When to use**: Formal definitions with multiple key terms, any educational text where 2-4 words need distinct colors, option/contract descriptions, theorem statements with highlighted variables.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/what_is_an_option.py:154-163
lines = [
    f'An option is a contract that:',
    f'• gives you the <span foreground="{YELLOW}">option</span> to buy a stock',
    f'• at a <span foreground="{GREEN}">predetermined price</span> (the "strike price")',
    f'• on a <span foreground="{BLUE}">specific date</span> in the future.'
]
option_definition_lines = (VGroup(*[MarkupText(line, font_size=TEXT_SIZE_MEDIUM) for line in lines])
                           .arrange(DOWN, aligned_edge=LEFT, buff=0.25)
                           .to_edge(UP))
```

### Pattern: Payoff Diagram with Shifted Y-Axis at Strike

**What**: A call option payoff hockey-stick diagram where the y-axis is manually shifted to sit at the strike price instead of the default x-origin. The left side (out-of-the-money) is flat at zero, the right side (in-the-money) is a 45-degree line. Premium is added by shifting both sides down.
**When to use**: Option payoff diagrams, piecewise linear functions where the kink point should be the visual center, any finance visualization where the strike/threshold price is the natural reference point.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/what_is_an_option.py:259-280
# (manually) centering y-axis at $300 instead of $0
ax.get_axes()[1].shift(ax.c2p(300, 0) - ax.c2p(ax.x_range[0], 0))

# plot the payoff in two halves
left_side = ax.plot_line_graph(
    x_values=np.linspace(300, 260, 10), y_values=0 * np.ones(10),
    line_color=BLUE, add_vertex_dots=False, z_index=1
)
right_side = ax.plot_line_graph(
    x_values=np.linspace(300, 340, 10), y_values=np.linspace(0, 40, 10),
    line_color=BLUE, add_vertex_dots=False, z_index=1
)

# shift both sides down by the premium amount
self.play(left_side.animate.shift(ax.c2p(0, -10) - ax.c2p(0, 0)),
          right_side.animate.shift(ax.c2p(0, -10) - ax.c2p(0, 0)))
```

### Pattern: ApplyWave Synchronized with Graph Creation

**What**: Uses LaggedStart to pair an ApplyWave on explanatory text with the Create animation of the corresponding graph segment. The text ripples to draw attention, then the graph draws, creating a clear cross-reference between verbal and visual explanation.
**When to use**: Any time you want to highlight which text description corresponds to which visual element being drawn, synchronized explanation-and-plot reveals, connecting written examples to plotted data.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/what_is_an_option.py:271-275
self.play(LaggedStart(ApplyWave(example_profit, rate_func=linear, ripples=2, amplitude=0.1),
                      Create(right_side, rate_func=linear, run_time=2.0), lag_ratio=0.25))
self.play(LaggedStart(ApplyWave(example_worthless, rate_func=linear, ripples=2, amplitude=0.1),
                      Create(left_side, rate_func=linear, run_time=2.0), lag_ratio=0.25))
```

## Scene Flow

1. **WhatIsAStock** (0-18s): Company grid of blue squares appears. One square breaks off as red "share" to the left, original dims. Customer circle appears on right with dollar signs. Money and product exchange positions. A fraction of money flows to the share. Share flashes yellow to emphasize value.
2. **StockSimulation** (0-15s): Y-axis with dollar labels creates. Flat line at $100 oscillates up/down to show price agreement concept. Full axes appear, simulated stock path draws left-to-right. Real Netflix stock history image overlays the chart.
3. **WhatIsAnOption definition** (0-12s): Four-line color-coded definition writes line-by-line. Footnote about "European call option" appears. The "right, but not the obligation" alternate wording briefly replaces line 2, then reverts.
4. **WhatIsAnOption example** (12-18s): Apple stock example writes with color-coded terms. Two outcome cases ($325 profit, $275 worthless) appear below.
5. **WhatIsAnOption payoff** (18-30s): Definition fades, example moves to top. Payoff axes with shifted y-axis at strike=$300 create. Right side (profit) draws with ApplyWave on example text. Left side (flat) draws similarly. Both sides shift down by premium amount. Brace and "Option Price (Premium)" label appear.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/what_is_an_option.py` (295 lines)
