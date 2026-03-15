---
source: https://github.com/3b1b/videos/blob/main/_2019/bayes/part1.py
project: videos
domain: [probability, statistics, mathematics]
elements: [formula, brace, surrounding_rect, label, bar_chart, dot, arrow, pi_creature]
animations: [write, transform, replacement_transform, transform_from_copy, fade_in, fade_out, grow, animate_parameter, update_value]
layouts: [centered, vertical_stack, side_by_side]
techniques: [value_tracker, always_redraw, add_updater, custom_mobject, progressive_disclosure, helper_function]
purpose: [demonstration, step_by_step, derivation, exploration]
mobjects: [BayesDiagram, ProbabilityBar, VGroup, OldTex, OldTexText, Brace, Rectangle, Square, Line, Integer, SVGMobject, Dot, Arrow]
manim_animations: [FadeIn, FadeOut, GrowArrow, ShowCreation, Write, TransformFromCopy, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 4906
scene_classes: [IntroduceFormula, IntroduceSteve, IsHeALibrarian, DiscussPriors, ShowBayesFormula, UpdatePosterior]
---

## Summary

Visualizes Bayes' theorem through a geometric area model (BayesDiagram) and a dynamic probability bar (ProbabilityBar). The BayesDiagram is a square partitioned into rectangles representing prior, likelihood, and posterior — the viewer physically sees how evidence updates beliefs by watching rectangle proportions change. ProbabilityBar uses ValueTracker to animate a split bar with live percentage labels. Pi creature characters (Steve, Librarian, Farmer) serve as the concrete Bayesian example.

## Design Decisions

- **Square area model (BayesDiagram)**: A unit square is partitioned into hypothesis/not-hypothesis horizontally, then evidence/not-evidence vertically. This makes probability = area, so Bayes' update is literally "what fraction of the evidence column belongs to the hypothesis." Geometric reasoning beats symbolic manipulation for intuition.
- **Color coding: YELLOW=hypothesis, BLUE=evidence, GREY=negation**: Consistent across all formula terms and diagram regions. The t2c (tex_to_color_map) in the formula links symbols to their visual meaning.
- **ProbabilityBar with ValueTracker**: The split bar animates smoothly via p_tracker, showing the prior-to-posterior shift as a continuous motion rather than a discrete jump. Percentages auto-update via always_redraw.
- **Progressive formula reveal**: The Bayes formula is built term by term (posterior, prior, likelihood, denominator) using TransformFromCopy from relevant diagram regions. Each piece has physical meaning before it becomes symbolic.
- **SVG-based character icons (Steve, Librarian, Farmer)**: Concrete narrative characters make the abstract probability tangible. The Person class with overlaid profession icons creates a visual vocabulary for the population model.
- **Braces for dimension labeling**: Brace mobjects on each rectangle edge show the probability value, auto-refreshing when proportions change via set_prior/set_likelihood methods.

## Composition

- **BayesDiagram**: Square with side_length=height (default 2), partitioned into 6 rectangles via stretch(). Positioned centrally.
- **ProbabilityBar**: width=6, height=0.5, horizontal split bar. Backbone is invisible Line. Percentage labels inside bars at 0.75x bar height.
- **Formula**: Full width (FRAME_WIDTH - 1). Posterior on left, prior and likelihood on right of equals, denominator below fraction line.
- **Character icons**: Steve SVGMobject height=3, Person height=1.5, profession icons at 0.5x person width.
- **Labels**: hyp_label and evid_label with LARGE_BUFF spacing from formula, connected by Arrows.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Hypothesis (H) | YELLOW | Formula terms, h_rect fill |
| Not Hypothesis | GREY | nh_rect, formula negation terms |
| Evidence (E) | BLUE_C | he_rect, evidence formula terms |
| Evidence alt | BLUE_E | nhe_rect (evidence under not-H) |
| Not Evidence | GREY / GREY_D | hne_rect, nhne_rect |
| Square outline | WHITE | stroke_width=2 |
| Rectangle outlines | WHITE | stroke_width=1 |
| ProbabilityBar left | BLUE_D | Hypothesis proportion |
| ProbabilityBar right | GREY_BROWN | Complement proportion |
| Steve character | GREY | sheen_factor=0.5, sheen_direction=UL |
| Percentage labels | WHITE | background_stroke: BLACK, width=2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Formula piece reveal | run_time=1 each | TransformFromCopy |
| Prior/likelihood change | run_time=2-3 | Smooth rectangle stretch |
| ProbabilityBar update | continuous | ValueTracker driven |
| Arrow growth | run_time=1 | GrowArrow for labels |
| Diagram transition | run_time=2 | Full diagram rebuild |

## Patterns

### Pattern: Geometric Probability Diagram (BayesDiagram)

**What**: A unit square partitioned into rectangles where area = probability. The square is split horizontally by prior P(H), then each half is split vertically by likelihood P(E|H) and P(E|not H). Rectangles can be dynamically resized via set_prior(), set_likelihood(), and set_antilikelihood() methods, with braces auto-refreshing.

**When to use**: Bayes' theorem visualization, conditional probability, any scenario where probability is best understood as area proportion. Also useful for contingency tables, joint distributions, or partition-of-unity demonstrations.

```python
# Source: projects/videos/_2019/bayes/part1.py:53-122
class BayesDiagram(VGroup):
    CONFIG = {
        "height": 2,
        "square_style": {"fill_color": GREY_D, "fill_opacity": 1, "stroke_color": WHITE, "stroke_width": 2},
        "rect_style": {"stroke_color": WHITE, "stroke_width": 1, "fill_opacity": 1},
        "hypothesis_color": YELLOW,
        "evidence_color1": BLUE_C,
    }

    def __init__(self, prior, likelihood, antilikelihood, **kwargs):
        super().__init__(**kwargs)
        square = Square(side_length=self.height)
        # Create 6 rectangles: h, nh, he, nhe, hne, nhne
        h_rect, nh_rect, he_rect, nhe_rect, hne_rect, nhne_rect = [
            square.copy().set_style(**self.rect_style) for x in range(6)
        ]
        # Stretch by prior horizontally
        for rect in h_rect, he_rect, hne_rect:
            rect.stretch(prior, 0, about_edge=LEFT)
        for rect in nh_rect, nhe_rect, nhne_rect:
            rect.stretch(1 - prior, 0, about_edge=RIGHT)
        # Stretch by likelihood vertically
        he_rect.stretch(likelihood, 1, about_edge=DOWN)
        hne_rect.stretch(1 - likelihood, 1, about_edge=UP)
```

### Pattern: Dynamic Probability Bar with ValueTracker

**What**: A horizontal bar split into two colored rectangles whose widths track a ValueTracker. Includes optional braces and percentage labels that auto-update via always_redraw. The bar visually represents P vs 1-P and animates smoothly when the tracker value changes.

**When to use**: Any binary probability display, prior-to-posterior transitions, A/B comparison bars, proportion visualization. Works for any value that splits into complementary parts.

```python
# Source: projects/videos/_2019/bayes/part1.py:215-307
class ProbabilityBar(VGroup):
    CONFIG = {
        "color1": BLUE_D, "color2": GREY_BROWN,
        "height": 0.5, "width": 6,
        "include_percentages": True,
    }

    def __init__(self, p=0.5, **kwargs):
        super().__init__(**kwargs)
        self.add_backbone()  # Invisible Line for width reference
        self.add_p_tracker(p)  # ValueTracker
        self.add_bars()  # Two rectangles with updater

    def add_bars(self):
        bars = VGroup(Rectangle(), Rectangle())
        bars.set_height(self.height)
        bars.add_updater(self.update_bars)  # Stretches to match p_tracker

    def update_bars(self, bars):
        p = self.p_tracker.get_value()
        total_width = self.backbone.get_width()
        for bar, vect, value in zip(bars, [LEFT, RIGHT], [p, 1 - p]):
            bar.set_width(value * total_width, stretch=True)
            bar.move_to(self.backbone, vect)
```

### Pattern: Formula Progressive Disclosure with tex_to_color_map

**What**: A Bayes formula built with OldTex using tex_to_color_map (t2c) to color-code each variable. The formula is revealed piece by piece using TransformFromCopy — each symbolic term visually emerges from its geometric counterpart (diagram rectangle). Named sub-parts (formula.posterior, formula.prior, etc.) enable targeted animations.

**When to use**: Any mathematical formula that should be revealed incrementally with visual grounding. Useful for equations where each term has a physical meaning that should be established first.

```python
# Source: projects/videos/_2019/bayes/part1.py:17-50
def get_bayes_formula(expand_denominator=False):
    t2c = {
        "{H}": HYPOTHESIS_COLOR,
        "{\\neg H}": NOT_HYPOTHESIS_COLOR,
        "{E}": EVIDENCE_COLOR1,
    }
    formula = OldTex(tex, tex_to_color_map=t2c, isolate=["P", "\\over", "="])
    # Named parts for targeted animation
    formula.posterior = formula[:6]
    formula.prior = formula[8:12]
    formula.likelihood = formula[13:19]
```

## Scene Flow

1. **Formula Introduction** (0-30s): Bayes formula appears. H and E labeled as "Hypothesis" and "Evidence" with arrows. Terms revealed left-to-right: posterior = prior x likelihood / evidence.
2. **Steve Example** (30-90s): SVG character Steve introduced. Population of librarians vs farmers shown. The question: given Steve's description, what's P(librarian|description)?
3. **BayesDiagram Construction** (90-150s): Unit square appears. Split by prior (1/21 librarians). Then split by likelihoods. Evidence regions highlighted. Posterior = area ratio.
4. **Dynamic Updates** (150-210s): ValueTracker animates prior changes. Diagram rectangles smoothly resize. ProbabilityBar shows the corresponding numerical shift. Braces and labels auto-update.
5. **Formula Connection** (210-270s): Each diagram region linked to its formula term via TransformFromCopy. Expanded denominator shown. The geometric and algebraic views unified.
