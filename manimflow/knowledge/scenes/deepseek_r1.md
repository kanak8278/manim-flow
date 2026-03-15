---
source: https://github.com/Kaos599/ML-Manim_Animations/blob/main/Deepseek R1/main.py
project: ML-Manim_Animations
domain: [machine_learning, deep_learning, reinforcement_learning, nlp, transformers]
elements: [pipeline, card, box, arrow, bar_chart, equation, quote_box, label, bullet_list, surrounding_rect]
animations: [fade_in, fade_out, write, lagged_start, grow_arrow, clear_screen, scene_transition]
layouts: [side_by_side, split_screen, flow_left_right, vertical_stack, centered, edge_anchored]
techniques: [multi_scene_in_one_class, scene_segmentation, brand_palette, factory_pattern, helper_function, before_after_comparison, progressive_disclosure]
purpose: [comparison, process, before_after, ranking, overview, demonstration]
mobjects: [Rectangle, RoundedRectangle, Text, MathTex, SurroundingRectangle, Arrow, VGroup]
manim_animations: [FadeIn, FadeOut, Write, LaggedStartMap, GrowArrow]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 397
scene_classes: [DeepSeekR1Animation]
---

## Summary

A one-minute explainer animation for the DeepSeek-R1 research paper, structured as 5 sequential scenes (~12s each) within a single Scene class. Each scene method builds elements, animates them, then clears everything before the next. Uses a consistent brand color palette and a reusable pipeline_box factory. Covers: paradigm comparison, GRPO algorithm, aha moment phenomenon, training pipeline, and benchmark results. Strong template for any research paper or multi-concept explainer.

## Design Decisions

- **5 scenes in one class, not 5 separate Scene classes**: Avoids scene transition complexity (file loading, config). Each scene is a method that builds, animates, then tears down. Simple, sequential, no shared state between scenes.
- **self.clear() + FadeOut between scenes**: self.clear() removes all mobjects instantly (no animation). But we FadeOut the visible elements first for a clean visual transition, THEN clear. This prevents ghost objects.
- **Brand color palette as module constants**: Colors defined once, used everywhere. Creates visual consistency across all 5 scenes. The viewer subconsciously learns "blue = DeepSeek, red = traditional approach."
- **Light background (#F8FAFC)**: Unusual for Manim (most use black). Light backgrounds feel more "professional/paper" — appropriate for a research paper explainer. Dark backgrounds feel more "cinematic/educational."
- **Pipeline box factory function**: create_pipeline_box() returns consistent VGroup(Rectangle, Text) with two size options. Avoids copy-paste and ensures visual consistency across pipeline diagrams.
- **LaggedStartMap for sequential reveals**: Elements in a pipeline or list appear one by one with lag_ratio=0.3. Creates a natural "building up" rhythm. All-at-once feels abrupt; one-by-one with no overlap feels too slow.
- **Key insight always at bottom**: Each scene ends with a green highlight text at the bottom edge. This creates a consistent structure — viewer learns to look at the bottom for the takeaway.

## Composition

- **Screen layout per scene**:
  - Title: `to_edge(UP, buff=0.8)` — font_size=32-36, BOLD
  - Main content: center area, UP * 1-2 range
  - Key insight/highlight: `DOWN * 1.8` to `to_edge(DOWN, buff=0.8)` — green accent
- **Side-by-side comparison (Scene 1)**:
  - Left title: `LEFT * 4.5 + UP * 2.2`
  - Right title: `RIGHT * 4.5 + UP * 2.2`
  - Left pipeline: `next_to(left_title, DOWN, buff=0.6)`, arranged DOWN buff=0.2
  - Right pipeline: mirror of left
  - Breakthrough text: `DOWN * 1.8` (below both pipelines)
- **Horizontal pipeline (Scene 4)**:
  - 4 boxes: box_width=3.2, box_height=1.2
  - x_spacing=3.8 between box centers
  - Start at `LEFT * 6`, each box at `LEFT * 6 + RIGHT * i * 3.8 + UP * 0.5`
  - Arrows connect get_right() to next box's left edge
- **Bar chart (Scene 5)**:
  - Labels at `LEFT * 5`, bars starting at `LEFT * 2`
  - Bar width proportional to score: `(score / 100) * 3`
  - Rows spaced `DOWN * 1.2`, sub-bars spaced `DOWN * 0.4`

## Color and Styling

| Element | Color | Hex | Role |
|---------|-------|-----|------|
| Background | Light gray | #F8FAFC | Professional paper feel |
| Primary | DeepSeek Blue | #1E40AF | Main brand, titles, innovations |
| Secondary | DeepSeek Teal | #0891B2 | Supporting elements, equation boxes |
| Light accent | DeepSeek Light | #3B82F6 | Response boxes, lighter elements |
| Dark text | DeepSeek Dark | #1E293B | Body text, descriptions, arrows |
| Success/insight | Accent Green | #10B981 | Key takeaways, positive results |
| Warning/old | Accent Red | #EF4444 | Traditional approach, contrast |
| Highlight | Accent Orange | #F59E0B | Quotes, special emphasis |
| Special | Accent Purple | #8B5CF6 | Final stage, unique elements |

**Color strategy**: Blue = new/good (DeepSeek), Red = old/traditional, Green = key insight, Orange = quotes/emphasis. Viewer subconsciously learns: blue sections are the innovation, red sections are what's being replaced.

**Typography**: All titles use weight=BOLD. Three-tier scale: titles (32-36), subtitles (20-26), body (15-18), fine print (11-13).

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title FadeIn | Default (~1s) | + 0.8s wait |
| Pipeline LaggedStartMap | lag_ratio=0.3 | ~1.5s for 3-5 elements |
| Write (key insight) | Default (~1s) | Always at end of scene |
| FadeOut all elements | Default (~1s) | Before self.clear() |
| Wait between scenes | 0.3s | Quick pause |
| Per scene total | ~12s | 5 scenes = 60s total |
| Full video | ~60 seconds | Tight 1-minute format |

## Patterns

### Pattern: Multi-Scene Narrative in One Class

**What**: Structure a multi-scene video as methods on a single Scene class. construct() calls each method in order. Each method builds its elements, animates them, FadeOuts everything, then calls self.clear(). No shared state between scenes.
**When to use**: Explainer videos with 3-7 distinct sections. Research paper animations. Any video where each section has its own visual composition and doesn't share elements with other sections.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:19-33
class DeepSeekR1Animation(Scene):
    def construct(self):
        self.camera.background_color = "#F8FAFC"
        self.paradigm_shift()         # 0-12s
        self.grpo_algorithm()         # 12-24s
        self.aha_moment()             # 24-36s
        self.training_pipeline()      # 36-48s
        self.performance_results()    # 48-60s

    def paradigm_shift(self):
        self.clear()
        # ... build elements, animate ...
        all_elements = VGroup(title, pipeline1, pipeline2, highlight)
        self.play(FadeOut(all_elements))
        self.wait(0.3)
```

### Pattern: Brand Color Palette

**What**: Define all colors as module-level constants with semantic names. Use them consistently across all scenes. The constants serve as a single source of truth — change a color once, it updates everywhere.
**When to use**: Any video that needs visual consistency. Especially brand-specific content, series with multiple episodes, or any video with more than 3-4 colors.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:9-17
DEEPSEEK_BLUE = "#1E40AF"
DEEPSEEK_TEAL = "#0891B2"
DEEPSEEK_LIGHT = "#3B82F6"
DEEPSEEK_DARK = "#1E293B"
ACCENT_GREEN = "#10B981"
ACCENT_ORANGE = "#F59E0B"
ACCENT_RED = "#EF4444"
ACCENT_PURPLE = "#8B5CF6"
```

### Pattern: Side-by-Side Comparison

**What**: Two parallel vertical pipelines (left vs right) showing contrasting approaches. Each side has a title, then a vertical stack of pipeline boxes with arrow text between them. Both sides animate simultaneously with LaggedStartMap.
**When to use**: Before/after, old vs new, traditional vs innovative, any comparison of two methods, systems, or approaches. The spatial separation makes the contrast immediately visible.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:47-79
# Left side
trad_title = Text("Traditional Approach", font_size=26, color=ACCENT_RED, weight=BOLD)
trad_title.move_to(LEFT * 4.5 + UP * 2.2)
trad_pipeline = VGroup(
    self.create_pipeline_box("Massive Datasets", ACCENT_RED, reduced_size=True),
    Text("↓", font_size=20, color=ACCENT_RED),
    self.create_pipeline_box("Supervised Fine-tuning", ACCENT_RED, reduced_size=True),
)
trad_pipeline.arrange(DOWN, buff=0.2)
trad_pipeline.next_to(trad_title, DOWN, buff=0.6)

# Right side — same structure, different color and content
deepseek_title = Text("DeepSeek-R1 Approach", font_size=26, color=DEEPSEEK_BLUE, weight=BOLD)
deepseek_title.move_to(RIGHT * 4.5 + UP * 2.2)

# Animate both simultaneously
self.play(
    LaggedStartMap(FadeIn, trad_pipeline, lag_ratio=0.3),
    LaggedStartMap(FadeIn, deepseek_pipeline, lag_ratio=0.3)
)
```

### Pattern: Reusable Pipeline Box Factory

**What**: A helper method that creates consistent labeled rectangles. Returns a VGroup of Rectangle + centered Text. Has a size option (normal vs reduced) for fitting more boxes on screen.
**When to use**: Flow diagrams, process pipelines, system architecture diagrams, any visualization with multiple labeled boxes. The factory ensures all boxes look consistent without copy-paste.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:375-383
def create_pipeline_box(self, text, color, reduced_size=False):
    if reduced_size:
        box = Rectangle(width=2.5, height=0.6, color=color, fill_opacity=0.2, stroke_width=2)
        label = Text(text, font_size=12, color=color, weight=BOLD)
    else:
        box = Rectangle(width=3, height=0.8, color=color, fill_opacity=0.2, stroke_width=2)
        label = Text(text, font_size=14, color=color, weight=BOLD)
    return VGroup(box, label)
```

### Pattern: Horizontal Pipeline with Arrows

**What**: A sequence of boxes connected by arrows, flowing left-to-right. Each box has a stage number, title, and description stacked vertically inside. Arrows connect the right edge of each box to the left edge of the next. Uses GrowArrow for animated arrow appearance.
**When to use**: Training pipelines, data processing flows, manufacturing processes, any sequential multi-stage process. The left-to-right flow matches natural reading direction and implies progression.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:242-296
stages = [
    ("Stage 1", "Cold Start", "SFT on curated CoT data", DEEPSEEK_BLUE),
    ("Stage 2", "Reasoning RL", "GRPO with rule-based rewards", DEEPSEEK_TEAL),
    ("Stage 3", "Rejection Sampling", "Data filtering", ACCENT_GREEN),
    ("Stage 4", "Multi-scenario RL", "Final alignment", ACCENT_PURPLE)
]
box_width, box_height, x_spacing = 3.2, 1.2, 3.8

for i, (num, name, desc, color) in enumerate(stages):
    box = Rectangle(width=box_width, height=box_height, color=color,
                    fill_opacity=0.2, stroke_width=2)
    box.move_to(LEFT * 6 + RIGHT * i * x_spacing + UP * 0.5)
    content = VGroup(
        Text(num, font_size=13, color=color, weight=BOLD),
        Text(name, font_size=15, color=color, weight=BOLD),
        Text(desc, font_size=11, color=DEEPSEEK_DARK)
    ).arrange(DOWN, buff=0.08).move_to(box.get_center())

    if i < len(stages) - 1:
        arrow = Arrow(start=box.get_right() + RIGHT * 0.1,
                      end=next_box_left, color=DEEPSEEK_DARK, stroke_width=3)

self.play(LaggedStartMap(FadeIn, stage_elements, lag_ratio=0.3))
self.play(LaggedStartMap(GrowArrow, stage_arrows, lag_ratio=0.2))
```

### Pattern: Proportional Bar Chart

**What**: Horizontal bars whose width is proportional to a score. Each benchmark has two bars (model A vs model B) in different colors. Score label is centered inside the bar in white.
**When to use**: Benchmark comparisons, performance results, survey data, any ranked or scored comparison.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:319-342
benchmarks = [
    ("AIME 2024", [79.8, 79.2], ["DeepSeek-R1", "OpenAI o1"]),
    ("MATH-500", [97.3, 96.4], ["DeepSeek-R1", "OpenAI o1"]),
]
for i, (name, scores, models) in enumerate(benchmarks):
    title = Text(name, font_size=16, color=DEEPSEEK_BLUE, weight=BOLD)
    title.move_to(LEFT * 5 + chart_y + DOWN * i * 1.2)
    for j, (score, model) in enumerate(zip(scores, models)):
        bar_width = (score / 100) * 3
        bar_color = DEEPSEEK_TEAL if j == 0 else ACCENT_ORANGE
        bar = Rectangle(width=bar_width, height=0.3, color=bar_color, fill_opacity=0.7)
        bar.move_to(LEFT * 2 + RIGHT * bar_width/2 + chart_y + DOWN * i * 1.2 + DOWN * j * 0.4)
        label = Text(f"{score:.1f}%", font_size=12, color=WHITE, weight=BOLD)
        label.move_to(bar.get_center())
```

### Pattern: Quote Highlight Box

**What**: A bordered rectangle containing an important quote. The box has low fill opacity for a subtle background, and the text inside is bold with the accent color. Creates visual emphasis for key statements.
**When to use**: Paper quotes, key findings, important statements, definitions, or any text that deserves special visual treatment.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:185-191
quote_box = Rectangle(width=13, height=1.8, color=ACCENT_ORANGE,
                      fill_opacity=0.1, stroke_width=3)
quote_text = Text(
    '"Wait, wait. That\'s an aha moment I can flag here.\n'
    'Let\'s reevaluate this step-by-step..."',
    font_size=18, color=ACCENT_ORANGE, weight=BOLD, line_spacing=1.2
)
quote_group = VGroup(quote_box, quote_text)
quote_group.move_to(UP * 1.2)
```

### Pattern: Equation with SurroundingRectangle

**What**: A MathTex equation inside a highlighted rectangle. The SurroundingRectangle auto-sizes to fit the equation with configurable buff. Low fill_opacity creates a subtle highlight box.
**When to use**: Key formulas, theorems, definitions, any mathematical expression that deserves visual emphasis.

```python
# Source: projects/ML-Manim_Animations/Deepseek R1/main.py:114-122
equation = MathTex(r"A_i = \frac{r_i - \bar{r}}{\sigma_r}",
                   font_size=36, color=DEEPSEEK_BLUE)
equation_box = SurroundingRectangle(equation, color=DEEPSEEK_TEAL,
                                    fill_opacity=0.1, buff=0.4)
equation_group = VGroup(equation_box, equation)
equation_group.move_to(UP * 1.8)
```

## Scene Flow

1. **Paradigm Shift** (0-12s): Split screen comparison. Left = "Traditional Approach" in RED (3 pipeline boxes: Massive Datasets → Supervised Fine-tuning → Limited RL). Right = "DeepSeek-R1 Approach" in BLUE (3 boxes: Base Model → Pure RL Training → Reasoning Emergence). Both pipelines animate simultaneously. Green breakthrough text appears at bottom: "AIME 2024: 15.6% → 71.0%". FadeOut all → clear.
2. **GRPO Algorithm** (12-24s): Title at top. MathTex equation in SurroundingRectangle at UP*1.8. Four component descriptions below. "Group Sampling Process" subtitle with 4 response boxes in a horizontal row. Green innovation text at bottom. FadeOut → clear.
3. **Aha Moment** (24-36s): Title at top. Orange quote box at UP*1.2 with paper excerpt. "Emergent Metacognitive Development" subtitle. 4 numbered development steps arranged vertically. Green insight text at bottom. FadeOut → clear.
4. **Training Pipeline** (36-48s): Title at top. 4 horizontal boxes (left-to-right) connected by arrows. Each box has stage number, name, description in matching color (Blue → Teal → Green → Purple). GrowArrow between boxes. Orange achievement text below. FadeOut → clear.
5. **Performance Results** (48-60s): Title at top. Left half: horizontal bar chart comparing 3 benchmarks. Right half: "Distillation Success" with 4 green bullet points. Blue impact statement at bottom. FadeOut → end.

> Full file: `projects/ML-Manim_Animations/Deepseek R1/main.py` (397 lines)
