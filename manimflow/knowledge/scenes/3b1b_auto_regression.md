---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/_2024/transformers/auto_regression.py
project: manim-interactive
domain: [machine_learning, deep_learning, neural_networks, transformers, nlp]
elements: [token, label, title, code_block, cube, arrow, line, surrounding_rect]
animations: [fade_in, fade_out, write, transform, replacement_transform, lagged_start, grow, highlight, indicate, update_value]
layouts: [flow_left_right, horizontal_row, edge_anchored]
techniques: [custom_mobject, interactive_scene, data_driven, progressive_disclosure]
purpose: [demonstration, step_by_step, exploration, progression]
mobjects: [Text, VGroup, VPrism, Vector, Underline, Rectangle, Integer, SurroundingRectangle]
manim_animations: [FadeIn, FadeOut, Write, Transform, FadeTransform, FadeInFromPoint, ShowCreation, GrowArrow, UpdateFromAlphaFunc, MoveToTarget, LaggedStart, Succession]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 599
scene_classes: [SimpleAutogregression, AnnotateNextWord, QuickerRegression, AutoregressionGPT3, GPT3CleverestAutocomplete, GPT3OnLearningSimpler, AthleteCompletion, ThatWhichDoesNotKillMe]
---

## Summary

Visualizes autoregressive text generation by a transformer model. Shows seed text being fed into a 3D "machine" (stacked VPrism blocks labeled "Transformer"), producing a probability distribution over next tokens as horizontal bars, randomly sampling from the distribution with a bouncing highlight rectangle, and appending the selected token to the running text. The cycle repeats, building up generated text token by token. Supports both GPT-2 (local) and GPT-3 (API) predictions, with variants for different seed texts and generation speeds. The AthleteCompletion variant adds parameter visualization with MachineWithDials.

## Design Decisions

- **3D machine as stacked prisms**: The transformer is represented as 10 stacked VPrism(3, 2, 0.2) blocks with slight rotation (phi=10deg, theta=12deg), creating a physical "machine" metaphor. Blocks briefly flash TEAL as data passes through.
- **Horizontal probability bars**: Next-token distribution shown as colored bars (TEAL to YELLOW gradient) with percentage labels. Width proportional to probability, arranged vertically. Ellipses at bottom suggest more options.
- **Random sampling animation**: A highlight rectangle bounces between bar options using UpdateFromAlphaFunc with seed-based pseudo-random selection. This makes the sampling process visible and tangible.
- **Text wrapping with get_paragraph**: Generated text wraps at line_len=31 characters, positioned at text_corner=3.5*UP + 0.75*RIGHT. Seed text colored BLUE_B, new tokens in default color.
- **Real model predictions**: Actually calls GPT-2 tokenizer/model (or GPT-3 API) for authentic next-token distributions, making the visualization data-driven rather than scripted.

## Composition

- **Text area**: Corner at 3.5*UP + 0.75*RIGHT, line_len=31 chars, font_size=35.
- **Machine**: 10 VPrism(3, 2, 0.2) blocks, GREY_D fill, arranged along OUT axis. Rotated phi=10deg RIGHT, theta=12deg UP. Positioned y=0, left edge at -0.6.
- **Distribution bars**: width_100p=1.8 (100% probability = 1.8 units wide), bar_height=0.25. Next to machine right edge + 1.5 RIGHT. Colors: TEAL to YELLOW gradient.
- **Highlight rectangle**: SurroundingRectangle with YELLOW stroke 2, YELLOW fill 0.25.
- **Next word underline**: TEAL stroke 2, below text, 7-char width estimate.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Seed text | BLUE_B | seed_text_color |
| Generated text | Default (WHITE) | Appended tokens |
| Machine blocks | GREY_D | fill_opacity=1, stroke_width=0, shading=(0.25, 0.5, 0.2) |
| Machine label | Default | "Transformer", backstroke BLACK 5 |
| Probability bars | TEAL to YELLOW | Gradient across bars, stroke WHITE 1 |
| Bar labels | Default | font_size=24 for words, 0.75*24 for percentages |
| Highlight rect | YELLOW | stroke 2, fill 0.25 |
| Next word line | TEAL | stroke_width=2 |
| Block flash | TEAL | there_and_back rate_func during data input |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Text input to machine | ~1.5s | MoveToTarget + Transform with lag_ratio=0.02 |
| Block flash cascade | run_time=1 | LaggedStart lag_ratio=0.1, there_and_back |
| Distribution output | run_time=1 | FadeInFromPoint, lag_ratio=0.025 |
| Random sampling | Default | UpdateFromAlphaFunc with seed-based random |
| Word addition | Default | FadeTransform + next_word_line Transform |
| Bar removal | Default | FadeOut(bar_groups) |
| Quick mode | Skip to add | No text input animation, direct bar display |

## Patterns

### Pattern: 3D Machine Metaphor for Neural Network

**What**: Represents a transformer as stacked 3D VPrism blocks with slight perspective rotation (phi + theta angles). Blocks flash sequentially (TEAL, there_and_back) as "data" passes through. A text label sits on the front face. Creates a tangible "black box" metaphor.

**When to use**: Any scenario where you need a physical representation of a neural network or processing pipeline - language models, image classifiers, any multi-layer system where the internal workings are abstracted away.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/auto_regression.py:130-163
def get_transformer_drawing(self):
    self.frame.set_field_of_view(20 * DEGREES)
    blocks = VGroup(VPrism(3, 2, 0.2) for n in range(10))
    blocks.set_fill(GREY_D, 1)
    blocks.set_stroke(width=0)
    blocks.set_shading(0.25, 0.5, 0.2)
    blocks.arrange(OUT)
    blocks.move_to(ORIGIN, OUT)
    blocks.rotate(self.machine_phi, RIGHT, about_edge=OUT)
    blocks.rotate(self.machine_theta, UP, about_edge=OUT)
    blocks.deactivate_depth_test()
    for block in blocks:
        block.sort(lambda p: p[2])
    word = Text(self.machine_name, alignment="LEFT")
    word.move_to(blocks[-1])
    word.set_backstroke(BLACK, 5)
    return VGroup(blocks, word, out_arrow)
```

### Pattern: Probability Distribution as Horizontal Bar Chart

**What**: Creates a vertical stack of horizontal bars where width encodes probability. Each bar has a token label on the left and percentage on the right. Colors grade from TEAL to YELLOW. Bars appear via FadeInFromPoint from the machine's output.

**When to use**: Showing softmax output, next-token predictions, classification probabilities, any discrete distribution. The horizontal layout reads naturally and the gradient distinguishes high from low probability.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/auto_regression.py:165-198
def get_distribution(self, words, probs, machine, font_size=24,
                     width_100p=1.8, bar_height=0.25):
    labels = VGroup(Text(word, font_size=font_size) for word in words)
    bars = VGroup(Rectangle(prob * width_100p, bar_height) for prob in probs)
    bars.arrange(DOWN, aligned_edge=LEFT, buff=0.5 * bar_height)
    bars.set_fill(opacity=1)
    bars.set_submobject_colors_by_gradient(TEAL, YELLOW)
    bars.set_stroke(WHITE, 1)
    for label, bar, prob in zip(labels, bars, probs):
        prob_label = Integer(int(100 * prob), unit="%", font_size=0.75 * font_size)
        prob_label.next_to(bar, RIGHT, buff=SMALL_BUFF)
        label.next_to(bar, LEFT)
```

### Pattern: Animated Random Sampling from Distribution

**What**: Visualizes sampling from a probability distribution using a highlight rectangle that "bounces" between options. Uses UpdateFromAlphaFunc with seed-based pseudo-random index selection at each alpha step, creating the appearance of randomness settling on a choice.

**When to use**: Demonstrating stochastic processes, random sampling, Monte Carlo methods, any scenario where you need to show a random selection being made from a set of weighted options.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/auto_regression.py:247-265
def animate_random_sample(self, bar_groups):
    widths = np.array([group[1].get_width() for group in bar_groups[:-1]])
    dist = widths / widths.sum()
    seed = random.randint(0, 1000)

    def highlight_randomly(rect, dist, alpha):
        np.random.seed(seed + int(10 * alpha))
        index = np.random.choice(np.arange(len(dist)), p=dist)
        rect.surround(bar_groups[index], buff=buff)

    self.play(
        UpdateFromAlphaFunc(highlight_rect,
            lambda rect, a: highlight_randomly(rect, dist, a)),
        Animation(bar_groups)
    )
```

### Pattern: Autoregressive Text Generation Loop

**What**: A complete cycle: (1) animate text flowing into machine, (2) show probability distribution output, (3) randomly sample, (4) append selected token to running text, (5) repeat. Supports "quick" mode that skips input animation after initial iterations. Real model predictions drive the distribution.

**When to use**: Demonstrating language model generation, autoregressive decoding, any sequential generation process where each output feeds back as input.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/auto_regression.py:320-336
def new_selection_cycle(self, text_mob, next_word_line, machine, quick=False):
    if quick:
        words, probs = self.predict_next_token(self.cur_str)
        bar_groups = self.get_distribution(words, probs, machine)
        self.add(bar_groups)
    else:
        self.animate_text_input(text_mob, machine)
        bar_groups = self.animate_prediction_ouptut(machine, self.cur_str)
    self.animate_random_sample(bar_groups)
    new_text_mob = self.animate_word_addition(bar_groups, text_mob, next_word_line)
    return new_text_mob
```

## Scene Flow

1. **Setup** (0-3s): Seed text displayed at top-right corner. 3D transformer machine positioned at left. Underline marks next-token position.
2. **First full cycle** (3-12s): Text copies shrink into machine top, blocks flash sequentially, probability bars emerge from right side, highlight bounces and selects a token.
3. **Token addition** (12-15s): Selected token FadeTransforms into running text. Bars fade out. Underline advances.
4. **Repeated cycles** (15s+): Full animation for first ~10 tokens, then "quick" mode (skip input animation) for remaining. Each cycle ~2-3s in quick mode.
5. **Variants**: AthleteCompletion shows facts being absorbed into machine before prediction. GPT3OnLearningSimpler runs at 0.2s per prediction for rapid generation.

## manimlib Notes

- `InteractiveScene` with `self.frame.set_field_of_view(20 * DEGREES)` for mild perspective
- `VPrism(width, height, depth)` for 3D blocks
- `set_backstroke(BLACK, 5)` for text readability over 3D objects
- Uses HuggingFace `transformers` library for GPT-2 and OpenAI API for GPT-3
- `get_paragraph()` helper from helpers.py for word-wrapped text layout
- `break_into_tokens()` for tokenizer-aware text splitting
