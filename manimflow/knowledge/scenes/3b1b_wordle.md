---
source: https://github.com/3b1b/videos/blob/main/_2022/wordle/scenes.py
project: 3blue1brown
domain: [information_theory, probability, combinatorics, game_theory, algorithms]
elements: [grid, label, equation, formula, bar_chart, histogram, surrounding_rect, dot]
animations: [write, fade_in, fade_out, transform, replacement_transform, flash, highlight, color_change, stagger, lagged_start, update_value]
layouts: [grid, side_by_side, vertical_stack, edge_anchored]
techniques: [value_tracker, add_updater, custom_mobject, custom_animation, data_driven, progressive_disclosure, helper_function, interactive_scene]
purpose: [demonstration, exploration, step_by_step, comparison, distribution]
mobjects: [Square, VGroup, Text, Integer, DecimalNumber, OldTex, OldTexText, Rectangle, Underline, Line]
manim_animations: [Write, FadeIn, FadeOut, ShowCreation, LaggedStart, LaggedStartMap, FlashAround, Flash, UpdateFromAlphaFunc, CountInFrom, VFadeIn, VFadeInThenOut, TransformMatchingShapes, TransformMatchingTex]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 4274
scene_classes: [WordleScene, WordleSceneWithAnalysis, WordleDistributions, ExternalPatternEntry, TitleCardScene, LessonTitleCard, DrawPhone, AskWhatWorldeIs, IntroduceGame, ShowTonsOfWords, FirstThoughtsTitleCard, ExampleGridColors, PreviewGamePlay, ButTheyreNotEquallyLikely, KeyIdea, ExpectedMatchesInsert, InformationTheoryTitleCard, DescribeBit, DefineInformation, AskForFormulaForI, MinusLogExpression, TwentyBitOverlay, AddingBitsObservationOverlay, ExpectedInformationLabel, AskAboutPhysicsRelation, ContrastWearyAndSlate, VonNeumannPhrase, MaximumInsert, UniformPriorExample, MentionUsingWordFrequencies, V2TitleCard, HowThePriorWorks, ShowWordLikelihoods, SidewaysWordProbabilities, LookThroughWindowsOfWords, EntropyOfWordDistributionExample, WhatMakesWordleNice, TwoInterpretationsWrapper, FreqPriorExample, ConstrastResultsWrapper, WordlePriorExample, FirstThoughtsOnCombination, EntropyToScoreData, LookTwoStepsAhead, HowLookTwoAheadWorks, BestDoubleEntropies, TripleComparisonFrame, InformationLimit, ShowScoreDistribution]
---

## Summary

A comprehensive Wordle solver visualization built on information theory. Implements an interactive Wordle grid with animated color reveals (grey/yellow/green), probability-weighted word lists, expected information calculations, and entropy-based guess ranking. The WordleScene base class handles grid management, letter input, pattern matching, and animated tile-flip reveals, while WordleSceneWithAnalysis adds real-time entropy displays, top-pick rankings, and probability bars.

## Design Decisions

- **Custom color map for pattern states**: Grey (#797C7E), Yellow (#C6B566), Green (GREEN_D) map to 0/1/2 pattern codes, matching the actual Wordle game's color scheme exactly.
- **Tile-flip animation via stretch/squeeze**: Squares and letters are squished to zero height at the midpoint, then color fills at alpha > 0.5, creating the physical card-flip effect from the real game.
- **Side-by-side grid + analysis layout**: Grid shifted to `[-1.75, 1, 0]` at height=4.5, with word lists and entropy rankings on the right side, maintaining the game feel while adding analytical overlay.
- **Entropy coloring (TEAL_C) vs prior coloring (BLUE_C)**: Information-theoretic quantities use TEAL, word probability uses BLUE, creating clear visual distinction between the two optimization dimensions.
- **Interactive key handling**: `on_key_press` processes letter input, backspace, and enter, allowing live interactive play during presentations.
- **Probability bars next to word list**: Small colored bars proportional to word frequency appear next to each possible word, making the prior distribution tangible.

## Composition

- **Grid**: 6 rows x 5 cols of Squares, side_length derived from grid_height=6, buff=0.1 between cells.
- **Analysis grid center**: `[-1.75, 1, 0]`, grid_height=4.5
- **Font**: "Consolas" for letters, size = 65 * square_height
- **Top picks grid**: Right side, 13 rows (`n_top_picks`), with underlined column headers
- **Count label**: Integer + "Pos," + DecimalNumber + "Bits", scale=0.6, next to current row
- **Word grid**: 20 rows (decreasing by 2 per guess), 1 column, font_size=24

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Grey tile (miss) | #797C7E | Pattern code 0 |
| Yellow tile (wrong position) | #C6B566 | Pattern code 1 |
| Green tile (correct) | GREEN_D | Pattern code 2 |
| Grid stroke | WHITE | stroke_width=2 |
| Entropy values | TEAL_C | `entropy_color` |
| Prior probability | BLUE_C | `prior_color` |
| Word text | GREY_A | Consolas font |
| Eliminated words | RED | fill_opacity=0.5 |
| Info bits label | RED | For per-guess information |
| Selected guess row | YELLOW | fill_opacity=1 when isolated |
| Probability bars | BLUE_C | fill_opacity=0.7, max_width=1.0 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Letter typing | 0.1s per letter | `wait_time_per_letter` |
| Pattern reveal | 2s | `reveal_run_time`, lag_ratio=0.5 |
| Win bounce | 1.5s | Bezier bounce with Flash per letter |
| Invalid word shake | 0.5s | Bezier shake function |
| Tile flip | 2s | Squish to 0 at alpha=0.5, color at >0.5 |

## Patterns

### Pattern: Card-Flip Tile Reveal with Color Change

**What**: Animates Wordle tiles flipping by stretching squares to zero height at the midpoint, applying the target color when alpha > 0.5, then stretching back. Letters flip in sync with the same UpdateFromAlphaFunc. LaggedStart creates the cascading left-to-right reveal.

**When to use**: Any grid-based reveal animation: game boards, quiz answers, memory card flips, matrix value reveals. Any time you want a physical "flip" feel for discrete state changes.

```python
# Source: projects/videos/_2022/wordle/scenes.py:186-212
def alpha_func(mob, alpha):
    if not hasattr(mob, 'initial_height'):
        mob.initial_height = mob.get_height()
    mob.set_height(
        mob.initial_height * max(abs(interpolate(1, -1, alpha)), 1e-6),
        stretch=True
    )
    if isinstance(mob, Square) and alpha > 0.5:
        mob.set_fill(mob.future_color, 1)

self.play(*(
    LaggedStart(
        *(UpdateFromAlphaFunc(sm, alpha_func) for sm in mob),
        lag_ratio=self.reveal_lag_ratio,
        run_time=self.reveal_run_time,
    )
    for mob in (row, word)
))
```

### Pattern: Win Celebration with Bezier Bounce

**What**: On winning, each letter/square pair bounces vertically using a bezier curve `[0,0,1,1,-1,-1,0,0]` and fires a Flash effect, both LaggedStart'd across the row.

**When to use**: Success/completion celebrations, game-over screens, quiz completion, achievement unlocks. Any positive outcome that warrants per-element celebration.

```python
# Source: projects/videos/_2022/wordle/scenes.py:220-237
bf = bezier([0, 0, 1, 1, -1, -1, 0, 0])
self.play(
    LaggedStart(*(
        UpdateFromAlphaFunc(sm, lambda m, a: m.set_y(y + 0.2 * bf(a)))
        for sm in mover
    ), lag_ratio=0.1, run_time=1.5),
    LaggedStart(*(
        Flash(letter, line_length=0.1, flash_radius=0.4)
        for letter in letters
    ), lag_ratio=0.3, run_time=1.5),
)
```

### Pattern: Invalid Input Shake Animation

**What**: Uses a bezier curve `[0,0,1,1,-1,-1,0,0]` to shake the current row horizontally when an invalid word is entered, then clears the pending letters.

**When to use**: Error feedback, invalid input indication, rejection animations. Any time user input needs visual "nope" feedback.

```python
# Source: projects/videos/_2022/wordle/scenes.py:156-165
def shake_word_out(self):
    row = self.get_curr_row()
    c = row.get_center().copy()
    func = bezier([0, 0, 1, 1, -1, -1, 0, 0])
    self.play(UpdateFromAlphaFunc(
        VGroup(row, self.grid.pending_word),
        lambda m, a: m.move_to(c + func(a) * RIGHT),
        run_time=0.5,
    ))
```

### Pattern: Data-Driven Grid of Words with Ellipsis

**What**: Creates a monospace text grid of words from a filtered list, automatically inserting "..." when the list exceeds display capacity, with the last few entries always showing the actual final words.

**When to use**: Displaying large filtered datasets, search results, vocabulary lists, any enumeration that needs truncation with visible continuation indicator.

```python
# Source: projects/videos/_2022/wordle/scenes.py:243-276
@staticmethod
def get_grid_of_words(all_words, n_rows, n_cols, dots_index=-5, font_size=24):
    subset = all_words[:n_rows * n_cols]
    if len(subset) < len(all_words):
        subset[dots_index] = "..." if n_cols == 1 else "....."
        subset[dots_index + 1:] = all_words[dots_index + 1:]
    full_string = ""
    for i, word in zip(it.count(1), subset):
        full_string += str(word)
        full_string += " \n" if i % n_cols == 0 else "  "
    full_text_mob = Text(full_string, font="Consolas", font_size=font_size)
    result = VGroup()
    for word in subset:
        part = full_text_mob.get_part_by_text(word)
        part.text = word
        result.add(part)
    return result
```

## Scene Flow

1. **IntroduceGame** (0-60s): Wordle grid introduced, letters typed, first pattern revealed with tile-flip animation. Concept of color-coded feedback explained.
2. **PreviewGamePlay** (60-180s): Full game with analysis sidebar. Word possibilities count and entropy bits shown. Top picks ranked by expected information. Each guess reveals pattern, eliminates words (shown turning red), updates entropy.
3. **DefineInformation** (180-300s): Information theory concepts introduced. Bits defined via coin flip analogy. Formula -log2(p) derived. Expected information as weighted sum explained.
4. **EntropyOfWordDistributionExample** (300-420s): Shows how different guess words split possibility space differently. Distribution of pattern outcomes visualized as colored bar charts.
5. **LookTwoStepsAhead** (420-480s): Two-step lookahead optimization explained, comparing greedy vs optimal strategies.
6. **ShowScoreDistribution** (480-540s): Final score distributions compared across different strategies.
