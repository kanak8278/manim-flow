---
source: https://github.com/Kaos599/ML-Manim_Animations/blob/main/BERT/main.py
project: ML-Manim_Animations
domain: [deep_learning, nlp, transformers, machine_learning]
elements: [box, rounded_box, arrow, curved_arrow, label, bullet_list, title, subtitle, group, layer, token, grid]
animations: [fade_in, fade_out, write, lagged_start, scene_transition, transform]
layouts: [side_by_side, vertical_stack, centered, flow_left_right, grid]
techniques: [multi_scene_in_one_class, scene_segmentation, helper_function, progressive_disclosure]
purpose: [overview, demonstration, step_by_step, process, definition]
mobjects: [Text, Rectangle, RoundedRectangle, VGroup, CurvedArrow, Arrow, DoubleArrow, SurroundingRectangle, Ellipse, Arc, Line, Circle]
manim_animations: [FadeIn, FadeOut, Write, LaggedStart, Create, Transform, GrowArrow]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 426
scene_classes: [BERTBreakthrough]
---

## Summary

A seven-scene explainer animation for the BERT paper covering bidirectional context, masked language modeling, next sentence prediction, fine-tuning versatility, and a final synthesis. Uses a custom ManimBrain VGroup as a visual icon for the CLS token. The default black background and Manim built-in color palette give it a classic educational feel. Each scene method builds elements from scratch and fades everything out before the next scene begins.

## Design Decisions

- **Seven scenes in one class**: Covers the full BERT paper narrative — title, problem, architecture, MLM, NSP, fine-tuning, synthesis — as sequential methods on a single Scene class. No shared state between scenes; each builds and tears down independently.
- **Custom ManimBrain VGroup for CLS token**: The [CLS] token in BERT is an abstract concept. A stylized brain icon (ellipse + arcs for folds) makes it visually distinct from regular text tokens, helping viewers understand it serves a special classification role.
- **CurvedArrow for unidirectional context**: Arrows arc upward from each preceding word to the blank, visually encoding the one-way information flow. The upward curve prevents arrows from overlapping the sentence text.
- **Yellow [MASK] token with SurroundingRectangle glow**: The mask token needs maximum visual emphasis since it is the core training mechanism. Yellow on black is high contrast, and the fill_opacity=0.3 surrounding rectangle creates a glow effect without obscuring text.
- **Green bidirectional arrows for architecture**: Green = positive/innovation. Bidirectional arrows between transformer layers visually encode the key BERT innovation (reading both directions), contrasting with the red one-directional arrows shown earlier.
- **2x2 grid for fine-tuning tasks**: arrange_in_grid(2,2) creates a compact, balanced layout that shows BERT's versatility without overwhelming the viewer. Four tasks is enough to demonstrate generality.
- **Gradient title (BLUE_C to PURPLE_B)**: The BERT logo uses a gradient to create visual distinction from plain text, establishing brand identity that reappears in the final synthesis.

## Composition

- **Screen layout per scene**:
  - Title: `to_edge(UP, buff=0.5)` — font_size=36, BOLD
  - Main content: centered around ORIGIN, shifted UP * 0.5 to UP * 1
  - Captions/explanations: `next_to(content, DOWN, buff=0.8-1.5)` — font_size=22-24
- **Unidirectional problem (Scene 2)**:
  - Words: font_size=32, arranged RIGHT with buff=0.3, group centered at `ORIGIN + UP * 0.5`
  - CurvedArrows: start from word.get_top() + UP*0.1, angle=-PI/3, stroke_width=3
  - Possibilities: font_size=20, arranged DOWN buff=0.2, next_to target RIGHT buff=0.8
- **BERT architecture (Scene 3)**:
  - 3 Rectangles: width=6, height=0.8, BLUE_B fill_opacity=0.3
  - Arranged UP buff=0.3, centered at ORIGIN
  - Bidirectional arrows between layers: GREEN, stroke_width=3
- **Masked language model (Scene 4)**:
  - Words: font_size=28, RIGHT buff=0.25, group at `ORIGIN + UP * 1`
  - [MASK]: font_size=22, YELLOW, BOLD, SurroundingRectangle buff=0.15 corner_radius=0.1 fill_opacity=0.3
  - CurvedArrows: GREEN, stroke_width=4, angle=-PI/2 (left) and PI/2 (right)
- **Next sentence prediction (Scene 5)**:
  - Brain [CLS]: scaled 0.4, at UP * 2.5
  - Sentence blocks: RoundedRectangle width=8, corner_radius=0.2, fill_opacity=0.4
  - Sentence A: UP * 0.8, Sentence B: DOWN * 0.2
  - Verdict box: RoundedRectangle width=2, height=0.8, next_to brain_cls RIGHT buff=1
- **Fine-tuning (Scene 6)**:
  - BERT base: RoundedRectangle width=3, height=1.5 at LEFT * 3
  - Task heads: RoundedRectangle width=2, height=1, arrange_in_grid(2,2, buff=0.5) at RIGHT * 2.5
  - Arrows: from bert_model.get_right() to each task_head.get_left()
- **Final synthesis (Scene 7)**:
  - 3 concept icons: arranged RIGHT buff=1.5, centered at ORIGIN
  - Final logo: font_size=120, gradient BLUE_C to PURPLE_B

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default Manim background |
| BERT title gradient | BLUE_C → PURPLE_B | set_color_by_gradient for brand identity |
| Unidirectional arrows | BLUE_D | stroke_width=3, one-way context |
| Wrong predictions | RED_C | font_size=20, incorrect options |
| Transformer layers | BLUE_B | fill_opacity=0.3, width=6 |
| Bidirectional arrows | GREEN | stroke_width=3, innovation indicator |
| [MASK] token | YELLOW | BOLD, with glow SurroundingRectangle |
| Mask glow | YELLOW | fill_opacity=0.3, corner_radius=0.1 |
| Context arrows (MLM) | GREEN | stroke_width=4, bidirectional emphasis |
| Predicted word | GREEN | BOLD, correct prediction |
| Sentence A box | BLUE_C | RoundedRectangle fill_opacity=0.4 |
| Sentence B (coherent) | TEAL_C | RoundedRectangle fill_opacity=0.4 |
| Sentence B (incoherent) | RED_C | RoundedRectangle fill_opacity=0.4 |
| IsNext verdict | GREEN | fill_opacity=0.6, white text |
| NotNext verdict | RED | fill_opacity=0.6, white text |
| Connection lines (NSP) | ORANGE | stroke_width=3 |
| Fine-tuning tasks | GREEN, ORANGE, PURPLE, RED | One color per task type |
| Explanations | GRAY | font_size=22 |
| Footer | GRAY | font_size=24 |

**Color strategy**: GREEN = BERT innovation/correct, RED = wrong/old approach, YELLOW = masked/attention-worthy, BLUE = BERT brand/architecture. Manim built-in colors used throughout (no custom hex palette).

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title FadeIn | Default (~1s) | shift=UP |
| Word LaggedStart | lag_ratio=0.2 | ~1.5s for 5-7 words |
| CurvedArrow LaggedStart | lag_ratio=0.15 | Rapid sequential reveal |
| Layer FadeIn LaggedStart | lag_ratio=0.3 | Architecture build-up |
| Write (captions) | Default (~1s) | After main content |
| FadeOut between scenes | Default (~1s) | All elements grouped |
| Wait (inter-scene) | 0.5s | Brief pause |
| Wait (within scene, reading) | 1-3s | Varies by content density |
| Final Transform | run_time=3 | Concepts → BERT logo |
| Final wait | 4s | Hold on BERT logo |
| Estimated total | ~90-100 seconds | 7 scenes |

## Patterns

### Pattern: Custom VGroup Icon (ManimBrain)

**What**: A reusable custom VGroup that assembles multiple primitive Manim mobjects (Ellipse, Lines, Arcs) into a recognizable icon. Composed as a subclass of VGroup so it can be scaled, positioned, and animated like any other mobject.
**When to use**: Abstract concepts that benefit from a visual icon — neurons, processors, databases, users, or any domain-specific symbol not available in Manim's built-in library.

```python
# Source: projects/ML-Manim_Animations/BERT/main.py:6-17
class ManimBrain(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        outline = Ellipse(width=1.0, height=0.8, color=ORANGE).scale(0.8)
        midline = Line(outline.get_top(), outline.get_bottom(), stroke_width=2)
        left_fold1 = Arc(radius=0.2, start_angle=PI/2, angle=PI, stroke_width=2)
        left_fold1.move_to(outline.get_center() + LEFT*0.2 + UP*0.1)
        # ... symmetric right folds ...
        self.add(outline, midline, left_fold1, left_fold2, right_fold1, right_fold2)
        self.move_to(ORIGIN)
```

### Pattern: CurvedArrow for Directional Context

**What**: CurvedArrow with negative angle creates upward-arcing arrows from source words to a target, visually encoding directional information flow without overlapping the sentence text below.
**When to use**: Language model context windows, attention flow visualization, dependency parsing, any scenario showing which tokens inform a prediction. The arc direction and angle communicate directionality.

```python
# Source: projects/ML-Manim_Animations/BERT/main.py:77-90
for i in range(4):
    start_point = word_objects[i].get_top() + UP*0.1
    end_point = target.get_top() + UP*0.1
    arrow = CurvedArrow(
        start_point, end_point,
        angle=-PI/3,  # Negative = upward curve
        color=BLUE_D, stroke_width=3, tip_length=0.2
    )
    arrow_group.add(arrow)
self.play(LaggedStart(*[Create(a) for a in arrow_group], lag_ratio=0.15))
```

### Pattern: Mask Token with Glow Effect

**What**: A [MASK] text token wrapped in a SurroundingRectangle with low fill_opacity to create a subtle glow/highlight. The rectangle auto-sizes to fit the text with configurable buff and corner_radius.
**When to use**: Highlighting a special token in a sequence — masked tokens in MLM, [CLS] tokens, [SEP] tokens, or any token that needs visual emphasis in a sentence display.

```python
# Source: projects/ML-Manim_Animations/BERT/main.py:170-182
mask_token = Text("[MASK]", color=YELLOW, weight=BOLD, font_size=22)
mask_token.match_height(target_word)
mask_token.move_to(target_word.get_center())

mask_glow = SurroundingRectangle(
    mask_token, color=YELLOW, buff=0.15,
    corner_radius=0.1, fill_opacity=0.3, stroke_width=2
)
self.play(FadeOut(target_word), FadeIn(mask_token), Create(mask_glow))
```

### Pattern: Sentence Block Factory with Auto-Scaling

**What**: A local helper function that creates a RoundedRectangle containing text, with automatic width-based scaling to ensure text fits. Returns a VGroup(box, text) ready for positioning.
**When to use**: Next sentence prediction, sentence pair classification, any visualization with variable-length text inside boxes where overflow must be prevented.

```python
# Source: projects/ML-Manim_Animations/BERT/main.py:258-273
def create_sentence_block(text, color, width=8):
    text_mobj = Text(text, font_size=20)
    if text_mobj.width > width - 0.8:
        text_mobj.scale((width - 0.8) / text_mobj.width)
    box = RoundedRectangle(
        height=text_mobj.height + 0.6, width=width,
        corner_radius=0.2, color=color,
        fill_opacity=0.4, stroke_width=2
    )
    text_mobj.move_to(box.get_center())
    return VGroup(box, text_mobj)
```

### Pattern: One-to-Many Arrow Fan (Fine-Tuning)

**What**: A single source model box on the left with arrows fanning out to multiple task boxes arranged in a grid on the right. Demonstrates one-to-many relationships (pre-trained model to downstream tasks).
**When to use**: Transfer learning visualization, fine-tuning versatility, service architecture (one service, many consumers), any one-to-many relationship diagram.

```python
# Source: projects/ML-Manim_Animations/BERT/main.py:330-360
bert_model = VGroup(bert_base, bert_text).move_to(LEFT * 3)
task_heads = VGroup()
for task_name, color in tasks:
    task_box = RoundedRectangle(width=2, height=1, color=color, fill_opacity=0.3)
    task_text = Text(task_name, font_size=14).move_to(task_box)
    task_heads.add(VGroup(task_box, task_text))

task_heads.arrange_in_grid(2, 2, buff=0.5).move_to(RIGHT * 2.5)

arrows = VGroup()
for task_head in task_heads:
    arrow = Arrow(bert_model.get_right(), task_head.get_left(), color=GRAY, stroke_width=3)
    arrows.add(arrow)
```

## Scene Flow

1. **Title Screen** (0-8s): "Let's Understand" fades in above, then "BERT" in gradient BLUE_C→PURPLE_B (font_size=120). Full form text writes below. All fade out downward.
2. **Unidirectional Problem** (8-22s): "The Old Way: A One-Way Street" title. Sentence "The model finished its ____" appears word by word. Blue curved arrows arc from each word to the blank (left-to-right only). Red prediction possibilities ("training?", "report?", "lunch?") appear beside the blank. Caption explains limitation. FadeOut all.
3. **BERT Architecture** (22-32s): "BERT's Revolutionary Architecture" title. Three stacked transformer layer rectangles (BLUE_B) fade in bottom-to-top. Green bidirectional arrows appear between layers. Caption: "Each layer can see information from ALL directions." FadeOut all.
4. **Masked Language Model** (32-50s): "BERT's Masked Language Model" title. Seven-word sentence writes in. Caption about random masking. Word "large" replaced by yellow [MASK] with glow rectangle. Green curved arrows from left and right context to mask. "Prediction: 'large'" appears above. Mask transforms back to original word. FadeOut all.
5. **Next Sentence Prediction** (50-68s): "Next Sentence Prediction Task" title. Brain [CLS] icon at top. Sentence A (BLUE_C) and Sentence B (TEAL_C) in RoundedRectangles. Orange connection lines to CLS. Green "IsNext" verdict appears. Sentence B transforms to incoherent text (RED_C). Verdict transforms to red "NotNext". Explanation writes below. FadeOut all.
6. **Fine-Tuning Power** (68-82s): "BERT's Fine-tuning Versatility" title. Pre-trained BERT box on left. 2x2 grid of task boxes (QA, Sentiment, NER, Classification) on right in different colors. Gray arrows fan from BERT to each task. Explanation: "One pre-trained model -> Multiple specialized applications." FadeOut all.
7. **Final Synthesis** (82-100s): "The BERT Revolution" title. Three concept icons (bidirectional arrows, [MASK], A→B) appear in a row. Hold 2 seconds. Concepts transform into large BERT gradient logo with italic caption "Transforming Natural Language Understanding." Footer credit. Hold 4 seconds.

> Full file: `projects/ML-Manim_Animations/BERT/main.py` (426 lines)
