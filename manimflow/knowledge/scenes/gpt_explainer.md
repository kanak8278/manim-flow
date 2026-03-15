---
source: https://github.com/Kaos599/ML-Manim_Animations/blob/main/GPT/main.py
project: ML-Manim_Animations
domain: [deep_learning, nlp, transformers, machine_learning, optimization]
elements: [box, arrow, label, bullet_list, title, subtitle, equation, formula, timeline, layer, node]
animations: [fade_in, fade_out, write, grow_arrow, scene_transition]
layouts: [side_by_side, vertical_stack, centered, flow_left_right, horizontal_row]
techniques: [multi_scene_in_one_class, scene_segmentation, brand_palette, progressive_disclosure]
purpose: [overview, process, step_by_step, comparison, ranking, demonstration]
mobjects: [Text, Rectangle, MathTex, VGroup, Arrow, Circle, Line]
manim_animations: [FadeIn, FadeOut, Write, GrowArrow, Create]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 530
scene_classes: [GPTPaperAnimation]
---

## Summary

An eight-scene explainer animation for the original GPT-1 paper by OpenAI, structured as sequential methods in a single Scene class. Uses a dark background (#0f1419) for a cinematic feel, built-in Manim colors (no custom palette), and covers: title, NLP challenges, two-stage training innovation, transformer architecture specs, training methodology with equations, benchmark results, GPT timeline evolution, and key takeaways. Strong template for any foundational research paper walkthrough.

## Design Decisions

- **Eight scenes for comprehensive coverage**: The GPT-1 paper has many distinct concepts (problem, innovation, architecture, training, results, legacy). Eight short scenes keep each focused without cramming.
- **Dark background (#0f1419)**: A near-black background with slight warmth creates a cinematic, serious tone appropriate for a foundational AI paper. Contrasts with the lighter backgrounds used for newer papers.
- **Side-by-side stage boxes for two-stage training**: The pre-training vs fine-tuning distinction is the paper's core contribution. Placing them side-by-side with an arrow between them makes the two-step nature immediately visible.
- **Bullet-by-bullet reveal for problem statement and specs**: Each bullet animates individually with shift=LEFT to create a natural reading pace. All-at-once would overwhelm; lag_ratio stagger would be too fast for dense text.
- **MathTex equations for training objectives**: The language modeling and fine-tuning loss functions are central to the paper. Displaying them as proper LaTeX equations rather than plain text conveys mathematical rigor.
- **Timeline with circles for GPT evolution**: Circles connected by a line create a natural timeline metaphor. Each milestone gets its own color to distinguish eras. The progression from 117M to "Changed everything" tells the impact story visually.
- **Simplified transformer visual on the right side**: Rather than a full architecture diagram, 3 stacked rectangles with input/output text convey the decoder-only structure without overwhelming viewers with detail.

## Composition

- **Screen layout per scene**:
  - Title: `to_edge(UP, buff=1)` or `to_edge(UP, buff=1.2)` — font_size=32-34, BOLD
  - Main content: center area, varies by scene
  - Bottom info/messages: `to_edge(DOWN, buff=1.2)` — font_size=20-28
- **Title sequence (Scene 1)**:
  - Title: font_size=36, line_spacing=1.3, at `UP * 1.5`
  - Authors: font_size=22, BLUE, next_to title DOWN buff=0.8
  - Company+date: next_to authors DOWN buff=0.8
  - Key message: font_size=28, YELLOW BOLD, next_to company DOWN buff=1.2
- **Two-stage innovation (Scene 3)**:
  - Stage 1 box: Rectangle width=4, height=2.5, BLUE fill_opacity=0.1, at `LEFT * 2.8 + UP * 0.3`
  - Stage 2 box: Rectangle width=4, height=2.5, YELLOW fill_opacity=0.1, at `RIGHT * 2.8 + UP * 0.3`
  - Arrow: from stage1_box.get_right() + RIGHT*0.1 to stage2_box.get_left() + LEFT*0.1, WHITE stroke_width=5
  - Bullet points: font_size=18, arranged DOWN buff=0.2, aligned_edge=LEFT
  - Dataset info: font_size=20, PURPLE, to_edge(DOWN, buff=1.2)
- **Transformer visual (Scene 4)**:
  - Base position: `RIGHT * 3 + UP * 0.3`
  - 3 layers: Rectangle width=2.5, height=0.5, BLUE fill_opacity=0.2, arranged UP buff=0.15
  - Input text: font_size=16, GREEN, at base_pos + DOWN * 1.5
  - Output text: font_size=16, RED, at base_pos + UP * 1.5
  - Specs list: font_size=22, left-aligned at LEFT * 1.5
- **Training equations (Scene 5)**:
  - Pre-training equation: MathTex font_size=28, next_to desc DOWN buff=0.6
  - Fine-tuning equation: MathTex font_size=28, next_to desc DOWN buff=0.6
  - Vertical layout: pretrain section at top, finetune section below
- **Results (Scene 6)**:
  - Achievement: font_size=28, YELLOW BOLD, next_to title DOWN buff=1
  - Improvement rows: task (font_size=22) + score (font_size=26 BOLD), RIGHT buff=1.5
  - Rows: DOWN buff=0.6, next_to achievement DOWN buff=1.2
- **Timeline (Scene 7)**:
  - Circles: radius=0.2, fill_opacity=0.8
  - Arranged RIGHT buff=1.5 at `ORIGIN + DOWN * 0.3`
  - Model name: font_size=20, above circle buff=0.3
  - Year: font_size=18, below circle buff=0.15
  - Description: font_size=14, below year buff=0.15
  - Connecting line: WHITE stroke_width=3 between first and last circle centers

## Color and Styling

| Element | Color | Hex | Details |
|---------|-------|-----|---------|
| Background | Dark blue-gray | #0f1419 | Cinematic dark theme |
| Title text | WHITE | — | font_size=36, line_spacing=1.3 |
| Authors | BLUE | — | font_size=22 |
| Company | GREEN | — | font_size=26, BOLD |
| Key message | YELLOW | — | font_size=28, BOLD |
| Problem title | RED | — | font_size=34, BOLD |
| Bullets | YELLOW | — | font_size=28, as bullet markers |
| Pre-training box | BLUE | — | fill_opacity=0.1 |
| Fine-tuning box | YELLOW | — | fill_opacity=0.1 |
| Spec labels | GREEN | — | font_size=22, BOLD |
| Training title | ORANGE | — | font_size=32, BOLD |
| Equations | WHITE | — | MathTex font_size=28 |
| Results title | GREEN | — | font_size=32, BOLD |
| Achievement text | YELLOW | — | font_size=28, BOLD |
| Task improvements | BLUE, GREEN, RED, PURPLE | — | One color per benchmark |
| Timeline circles | BLUE, GREEN, YELLOW, RED | — | One per GPT generation |
| Date text | Color-matched | — | Matches circle color |
| Descriptions | GRAY | — | font_size=14 |
| Conclusion title | GREEN | — | font_size=32, BOLD |
| Final message | YELLOW | — | font_size=28, BOLD |

**Color strategy**: Uses Manim built-in constants, no custom hex palette. YELLOW = emphasis/key points. GREEN = positive/innovation. RED = problems/challenges. BLUE = technical/neutral. PURPLE = supplementary info. Each benchmark gets a unique color for visual differentiation.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title FadeIn | Default (~1s) | shift=UP |
| Write (authors, descriptions) | Default (~1s) | Standard write speed |
| Bullet-by-bullet FadeIn | Default + 0.3-0.8s wait | One at a time with pauses |
| GrowArrow | Default (~1s) | Between stage boxes |
| Layer FadeIn | Default + 0.3s wait | 3 layers sequential |
| Write (equations) | Default (~1s) | + 1.5-2s wait for reading |
| Result row FadeIn | Default + 0.8s wait | Per benchmark row |
| Timeline event FadeIn | Default + 0.8s wait | Per era |
| FadeOut between scenes | Default (~1s) | VGroup all elements |
| Wait (reading time) | 1-3s | Varies by content density |
| Wait (inter-scene) | 0.5s | Consistent gap |
| Estimated total | ~120-140 seconds | 8 scenes, ~15-18s each |

## Patterns

### Pattern: Problem Statement with Bullet Reveal

**What**: A titled problem section where each bullet point animates individually with a directional shift. Bullets are arranged vertically with left alignment. Each bullet has a colored marker (dot/bullet character) followed by descriptive text.
**When to use**: Listing challenges, requirements, features, or any enumerated items where sequential revelation helps the viewer absorb each point. Research paper problem statements, feature lists, pros/cons.

```python
# Source: projects/ML-Manim_Animations/GPT/main.py:82-108
problems = [
    "Limited labeled data for specific tasks",
    "Task-specific model architectures required",
    "Poor transfer learning across different tasks",
    "Expensive manual annotation requirements"
]
problem_list = VGroup()
for problem in problems:
    bullet = Text("•", font_size=28, color=YELLOW)
    problem_text = Text(problem, font_size=24, color=WHITE)
    problem_row = VGroup(bullet, problem_text).arrange(RIGHT, buff=0.3)
    problem_list.add(problem_row)

problem_list.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
problem_list.next_to(problem_title, DOWN, buff=1.5)

for problem_row in problem_list:
    self.play(FadeIn(problem_row, shift=LEFT))
    self.wait(0.7)
```

### Pattern: Two-Stage Process Comparison

**What**: Two side-by-side rectangles with titles and bullet points, connected by an arrow. Each stage has its own color coding. Stages are animated sequentially: left stage appears, arrow grows, then right stage appears.
**When to use**: Pre-training vs fine-tuning, training vs inference, design vs implementation, any two-phase process where the left feeds into the right. The arrow makes the sequential dependency explicit.

```python
# Source: projects/ML-Manim_Animations/GPT/main.py:122-199
stage1_box = Rectangle(width=4, height=2.5, color=BLUE, fill_opacity=0.1)
stage1_box.move_to(LEFT * 2.8 + UP * 0.3)
stage1_title = Text("Stage 1: Pre-training", font_size=26, color=BLUE, weight=BOLD)
stage1_title.next_to(stage1_box.get_top(), DOWN, buff=0.3)

stage2_box = Rectangle(width=4, height=2.5, color=YELLOW, fill_opacity=0.1)
stage2_box.move_to(RIGHT * 2.8 + UP * 0.3)

arrow = Arrow(
    start=stage1_box.get_right() + RIGHT * 0.1,
    end=stage2_box.get_left() + LEFT * 0.1,
    color=WHITE, stroke_width=5
)

# Animate: Stage 1 → Arrow → Stage 2
self.play(Create(stage1_box))
self.play(FadeIn(stage1_title, shift=DOWN))
# ... bullet reveals ...
self.play(GrowArrow(arrow))
self.play(Create(stage2_box))
```

### Pattern: Spec List with Label-Value Pairs

**What**: Architecture specifications displayed as label-value rows where labels are bold and colored, values are white. Rows are left-aligned and spaced vertically. Each row animates individually with shift=LEFT.
**When to use**: Model architecture specs, system requirements, configuration parameters, any key-value information that benefits from structured display.

```python
# Source: projects/ML-Manim_Animations/GPT/main.py:213-244
specs = [
    ("Layers:", "12 decoder-only transformer layers"),
    ("Parameters:", "117 million parameters"),
    ("Hidden Size:", "768-dimensional states"),
    ("Attention Heads:", "12 multi-head attention heads"),
    ("Context Window:", "512 tokens maximum")
]
specs_group = VGroup()
for label, value in specs:
    label_text = Text(label, font_size=22, color=GREEN, weight=BOLD)
    value_text = Text(value, font_size=22, color=WHITE)
    spec_row = VGroup(label_text, value_text).arrange(RIGHT, buff=0.5)
    specs_group.add(spec_row)

specs_group.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
```

### Pattern: Circle-Based Timeline

**What**: A horizontal timeline with colored circles at milestones, connected by a straight line. Each circle has a label above, date below, and description further below. Colors differentiate eras. Line drawn first, then events animate one by one.
**When to use**: Model evolution (GPT-1 to GPT-4), historical progression, version history, any chronological sequence of events with associated metadata.

```python
# Source: projects/ML-Manim_Animations/GPT/main.py:408-461
timeline_events = [
    ("GPT-1", "2018", "117M", BLUE),
    ("GPT-2", "2019", "1.5B", GREEN),
    ("GPT-3", "2020", "175B", YELLOW),
    ("ChatGPT", "2022", "Changed everything", RED)
]
timeline = VGroup()
for i, (model, year, description, color) in enumerate(timeline_events):
    circle = Circle(radius=0.2, color=color, fill_opacity=0.8)
    model_text = Text(model, font_size=20, color=WHITE, weight=BOLD)
    model_text.next_to(circle, UP, buff=0.3)
    year_text = Text(year, font_size=18, color=color, weight=BOLD)
    year_text.next_to(circle, DOWN, buff=0.15)
    event_group = VGroup(circle, model_text, year_text, desc_text)
    timeline.add(event_group)

timeline.arrange(RIGHT, buff=1.5)
timeline.move_to(ORIGIN + DOWN * 0.3)

line = Line(start=timeline[0][0].get_center(), end=timeline[-1][0].get_center(),
            color=WHITE, stroke_width=3)
self.play(Create(line))
for event in timeline:
    self.play(FadeIn(event, shift=UP))
```

### Pattern: Training Equations with Section Labels

**What**: Mathematical equations displayed with section titles and plain-text descriptions above them. Pre-training and fine-tuning objectives are stacked vertically with clear section separation. MathTex renders proper LaTeX.
**When to use**: Research paper training objectives, loss functions, mathematical formulations where both the equation and its context need to be shown.

```python
# Source: projects/ML-Manim_Animations/GPT/main.py:306-342
pretrain_title = Text("Pre-training: Language Modeling", font_size=26, color=BLUE)
pretrain_title.move_to(UP * 1.5)
pretrain_desc = Text("Predict next token given previous context", font_size=20, color=WHITE)
pretrain_desc.next_to(pretrain_title, DOWN, buff=0.3)

equation1 = MathTex(
    r"L_1(U) = \sum_i \log P(u_i | u_{i-k}, ..., u_{i-1}; \Theta)",
    font_size=28, color=WHITE
)
equation1.next_to(pretrain_desc, DOWN, buff=0.6)

finetune_title = Text("Fine-tuning: Task Adaptation", font_size=26, color=GREEN)
finetune_title.next_to(equation1, DOWN, buff=1)

equation2 = MathTex(
    r"L_3(C) = L_2(C) + \lambda \cdot L_1(C)",
    font_size=28, color=WHITE
)
```

## Scene Flow

1. **Title Sequence** (0-12s): Paper title (two lines, font_size=36) at UP*1.5. Authors in BLUE. "OpenAI" in GREEN + "June 2018". Yellow key message: "The Foundation of Modern Large Language Models." FadeOut all.
2. **Problem Statement** (12-26s): "The NLP Challenge in 2018" in RED at top. Four yellow-bullet problems animate one by one with shift=LEFT and 0.7s pauses. 2s reading time. FadeOut all.
3. **Core Innovation** (26-48s): "GPT's Two-Stage Training Innovation" in GREEN. Left blue box (Pre-training) with 4 bullets animates first. White arrow grows to right yellow box (Fine-tuning) with 4 bullets. Purple dataset info at bottom. FadeOut all.
4. **Transformer Architecture** (48-62s): "GPT-1 Transformer Architecture" title. Left side: 5 spec label-value rows animate sequentially. Right side (helper method): input text, 3 stacked layer rectangles, output text animate bottom-to-top. FadeOut both groups.
5. **Training Process** (62-78s): "Training Methodology" in ORANGE. Pre-training section with language modeling equation (MathTex). Fine-tuning section with combined loss equation. Both sections stacked vertically. FadeOut all.
6. **Key Results** (78-96s): "Breakthrough Performance" in GREEN. Yellow achievement: "State-of-the-art on 9 out of 12 tasks." Four improvement rows (task + percentage) in different colors animate one by one. FadeOut all.
7. **Impact Legacy** (96-116s): "The GPT Revolution" in PURPLE. White connecting line draws. Four timeline circles (GPT-1 through ChatGPT) with years and parameter counts animate left to right. FadeOut all.
8. **Conclusion** (116-132s): "Key Takeaways" in GREEN. Four yellow-bullet takeaways animate one by one. Yellow final message: "The Beginning of the AI Revolution" fades in with scale. FadeOut all.

> Full file: `projects/ML-Manim_Animations/GPT/main.py` (530 lines)
