---
source: https://github.com/ragibson/manim-videos/blob/main/black_scholes_derivation/introduction.py
project: ragibson_manim-videos
domain: [finance, economics, probability, statistics]
elements: [axes, function_plot, label, title, image, equation, formula]
animations: [fade_in, fade_out, write, draw, transform, indicate]
layouts: [centered, edge_anchored, horizontal_row]
techniques: [helper_function, progressive_disclosure, data_driven]
purpose: [overview, definition, demonstration]
mobjects: [Text, MathTex, Axes, ImageMobject, VGroup, Cross, DashedLine]
manim_animations: [Write, FadeIn, FadeOut, Create, Transform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 244
scene_classes: [TweakedIntroText, BlackScholesIntroduction, BlackScholesTraditionalDerivation, LookingAhead]
---

## Summary

Introduces the Black-Scholes-Merton formula with author portraits, Nobel Prize imagery, and a historical OCC options trading volume chart showing exponential growth from 1973 to 2025. Contrasts the traditional derivation (stochastic calculus, PDEs) against a simpler probability-only approach by crossing out complex topics with red X marks and transforming title text from "Complicated" to "Simpler." Ends with a table of contents for the video series.

## Design Decisions

- **Floating dollar signs as ambient background**: Semi-transparent green dollar signs drift upward during the title reveal, creating a financial atmosphere without competing with the main content. They fade out over 12 seconds so they feel ephemeral.
- **Faded stock chart behind title**: A low-opacity (0.3) stock simulation line runs beneath the title text, visually grounding the formula in actual stock behavior before any explanation begins.
- **Author images in horizontal row**: Fischer Black, Myron Scholes, and Robert Merton appear one-by-one with labels, matching the convention of introducing key figures in educational videos. Images are uniformly scaled to height=5.0 for visual consistency.
- **Cross marks on complex topics**: Red crosses through "Portfolio Hedging," "Stochastic Calculus," and "PDEs" create a satisfying visual elimination. The first topic (Probability & Statistics) turns GREEN to signal it survives the cut.
- **Title word Transform for narrative pivot**: "Traditional" transforms to "Alternate" and "Complicated!" transforms to "Simpler!" in-place, which is more dramatic than replacing the entire title. The color shifts from RED to GREEN reinforce the positive pivot.
- **OCC volume data hardcoded in shared utility**: Real historical trading volume data (1973-2025) is embedded directly in the codebase, enabling accurate data-driven plots without external dependencies.
- **Section title helper function**: `display_section_title()` in shared_data_and_functions.py provides consistent section breaks with keyword highlighting across all files in the series.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP, buff=0.5)`, font_size=TEXT_SIZE_MEDIUM (36)
  - Author images: arranged RIGHT with buff=1.0, each height=5.0
  - Author labels: `next_to(image, DOWN, buff=0.3)`, font_size=TEXT_SIZE_LARGE (40)
  - Nobel Prize image: centered, height=3.0
  - OCC volume axes: `next_to(title, DOWN, buff=1.0)`, x_length=10, y_length=4.5
  - Dollar signs: scattered across screen, 10 in top half, 3 bottom-left, 3 bottom-right
- **TweakedIntroText axes**: x_range=[0, 1.01], y_range=[80, 100.1], x_length=12, y_length=3.25, stroke_opacity=0.2
- **OCC axes**: x_range=[1973, 2025, 4], y_range=[0, 60_000_000], custom x-axis numbers without commas (years)
- **Bullet list**: arranged DOWN with aligned_edge=LEFT, buff=0.75, shifted LEFT 0.5 and DOWN 0.5
- **Math expressions**: next_to topics RIGHT buff=1.0, to_edge RIGHT buff=0.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Title year "1973" | YELLOW | t2c highlight |
| Stock simulation line | GREEN | stroke_width=2, stroke_opacity=0.5 |
| Dollar signs | GREEN | fill_opacity=0.4, font_size=TEXT_SIZE_SMALL |
| Faded axes | WHITE | stroke_width=1, stroke_opacity=0.2, set_opacity(0.3) |
| OCC volume line | YELLOW | stroke_width=2 |
| "Complicated!" text | RED | t2c highlight |
| "Simpler!" text | GREEN | t2c highlight |
| Cross marks | RED | stroke_width=6 |
| Surviving topic | GREEN | animate.set_color(GREEN) |
| Topic highlights | YELLOW | t2c on specific keywords |

Color strategy: YELLOW for emphasis and data, GREEN for positive/approved, RED for negative/eliminated. This three-color system provides clear semantic meaning throughout the introduction.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Dollar signs FadeIn | 1.0s | shift=UP*0.3 |
| Dollar float + fade | 12.0s | rate_func=linear, simultaneous |
| Title Write | 3.0s | Concurrent with stock line |
| Stock line Create | 6.0s | rate_func=linear |
| Author image FadeIn | default | One-by-one with 0.5s waits |
| OCC volume Create | 2.0s | rate_func=linear for graph |
| Cross marks Create | 2.0s | All simultaneously |
| Topic color changes | 0.5s | Concurrent with crosses |
| Total (TweakedIntroText) | ~15s | |
| Total (BlackScholesIntroduction) | ~25s | |
| Total (TraditionalDerivation) | ~20s | |
| Total (LookingAhead) | ~15s | |

## Patterns

### Pattern: Floating Ambient Background Elements

**What**: Semi-transparent text objects scattered across the screen that slowly drift in one direction and fade to zero opacity over a long duration. Creates atmospheric context without visual competition. Each element gets a random horizontal jitter to avoid uniform motion.
**When to use**: Financial visualizations needing market atmosphere, particle-like backgrounds for physics simulations, any scene where ambient motion adds thematic context without distracting from the main content.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/introduction.py:42-51
np.random.seed(0)
dollar_signs = VGroup([Text("$", font_size=TEXT_SIZE_SMALL, color=GREEN, fill_opacity=0.4
                            ).move_to([np.random.uniform(*xbounds), np.random.uniform(*ybounds), 0])
                       for xbounds, ybounds in ([((-7, 7), (0.5, 3))] * 10
                                                + [((-7, -6.5), (-4, -1))] * 3
                                                + [((6.5, 7), (-4, -1))] * 3
                                                + [((-4, -3), (0.5, 1.5))])])
dollar_animations = [dollar.animate(run_time=12.0, rate_func=linear)
                     .move_to(dollar.get_center() + np.array([np.random.uniform(-0.5, 0.5), 1.5, 0]))
                     .set_opacity(0) for dollar in dollar_signs]
```

### Pattern: Cross-Out Elimination with Title Transform

**What**: Red Cross mobjects drawn over rejected items while simultaneously transforming words in a title to signal a narrative pivot. Combines visual elimination with text replacement for maximum impact. Uses substring indexing to target specific words within a Text object.
**When to use**: Comparing approaches and eliminating options, contrasting methods in educational content, any "we won't do X, we'll do Y instead" narrative in derivations or algorithm comparisons.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/introduction.py:201-218
xmarks = VGroup([Cross(topics[i], color=RED, stroke_width=6) for i in range(1, len(topics))]
                + [Cross(math_exprs[i], color=RED, stroke_width=6) for i in range(1, len(topics))])

first_word = title[0:len("Traditional")]
new_first_word = Text("Alternate", font_size=TEXT_SIZE_MEDIUM).next_to(first_word.get_right(), LEFT, buff=0.0)
last_word = title[-len("Complicated!"):]
new_last_word = Text("Simpler!", font_size=TEXT_SIZE_MEDIUM, t2c={"Simpler!": GREEN}).next_to(
    last_word.get_left(), RIGHT, buff=0.0)
self.play(
    *[Create(cross, run_time=2.0) for cross in xmarks],
    topics[0].animate(run_time=0.5).set_color(GREEN),
    Transform(first_word, new_first_word, run_time=0.5),
    Transform(last_word, new_last_word, run_time=0.5)
)
```

### Pattern: Data-Driven Historical Line Chart with Dollar Y-Axis

**What**: A line chart plotted from real historical data (dictionary of year:value pairs) with custom year formatting on x-axis (no commas, no decimals) and dollar-sign labels manually added to the y-axis. The manual dollar sign hack works around Manim's lack of native currency formatting.
**When to use**: Plotting real-world financial data over time, any time series with year labels on x-axis, economic data visualizations where currency formatting is needed.

```python
# Source: projects/ragibson_manim-videos/black_scholes_derivation/introduction.py:117-147
axes = Axes(
    x_range=[1973, 2025, 4], y_range=[0, 60_000_000, 10_000_000],
    x_length=10, y_length=4.5, tips=False,
    axis_config={"include_numbers": True, "font_size": 24},
    x_axis_config={
        "include_numbers": [1973, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
        "decimal_number_config": {"group_with_commas": False, "num_decimal_places": 0}
    }
)
# HACK: manually adding dollar signs to y-axis
ax.y_axis.add_labels({i: fr"\${i:.0f}" for i in np.arange(*ax.y_range)})
```

## Scene Flow

1. **TweakedIntroText** (0-15s): Faded axes and green stock line appear at bottom. Dollar signs fade in and float upward. Title "1973: Black-Scholes-Merton Formula for Pricing Options" writes over the stock line. Title moves to top edge, everything else fades.
2. **BlackScholesIntroduction** (0-25s): Title writes at top. Three author portraits appear one-by-one in a row with name labels. Authors fade, Nobel Prize medal appears. OCC volume chart creates alongside the medal (medal shifts left). Exponential growth curve draws left-to-right. Everything fades.
3. **BlackScholesTraditionalDerivation** (0-20s): Four bullet points and matching math expressions appear alternately from left and right. Title "Traditional Derivation is Complicated!" writes after first bullet. Red crosses draw over topics 2-4 and their math. Topic 1 turns green. Title transforms: "Traditional" to "Alternate", "Complicated!" to "Simpler!". Everything fades.
4. **LookingAhead** (0-15s): Table of contents with five bullet points from TITLES list appear one-by-one. Each has a YELLOW-highlighted keyword. Everything fades.

> Full file: `projects/ragibson_manim-videos/black_scholes_derivation/introduction.py` (244 lines)
