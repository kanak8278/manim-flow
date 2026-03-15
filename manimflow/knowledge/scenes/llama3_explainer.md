---
source: https://github.com/Kaos599/ML-Manim_Animations/blob/main/Meta LLama 3/main.py
project: ML-Manim_Animations
domain: [deep_learning, nlp, transformers, machine_learning, reinforcement_learning, optimization]
elements: [pipeline, box, arrow, label, bullet_list, title, subtitle, surrounding_rect, group, bar_chart, node, line]
animations: [fade_in, fade_out, write, lagged_start, grow_arrow, clear_screen, scene_transition, grow_from_edge]
layouts: [side_by_side, split_screen, flow_left_right, vertical_stack, centered, horizontal_row, radial, grid]
techniques: [multi_scene_in_one_class, scene_segmentation, brand_palette, factory_pattern, helper_function, before_after_comparison, progressive_disclosure]
purpose: [comparison, process, before_after, overview, demonstration, step_by_step, ranking, progression]
mobjects: [Text, Rectangle, RoundedRectangle, MathTex, SurroundingRectangle, Arrow, VGroup, Circle, Line, Sector]
manim_animations: [FadeIn, FadeOut, Write, LaggedStartMap, GrowArrow, Create, GrowFromEdge, Transform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 673
scene_classes: [LlamaThreeAnimation]
---

## Summary

A seven-scene explainer animation for the Meta Llama 3 paper covering multimodal architecture, training pipeline, DPO vs PPO comparison, multilingual strategy, context window expansion, benchmark results, and key innovations. Uses a Meta AI brand palette with primary blue (#1877F2) on a light background (#F8F9FA). Features a radial capability diagram, sector-based pie chart for data composition, progressive bar expansion for context window scaling, and proportional benchmark bar charts. Strong template for multi-faceted model papers with training methodology emphasis.

## Design Decisions

- **Seven scenes covering training depth**: Llama 3's contribution is training methodology over architecture. Five of seven scenes focus on training aspects (pipeline, DPO/PPO, multilingual, context, results), reflecting the paper's emphasis.
- **Light background (#F8F9FA) matching DeepSeek style**: Professional/paper feel for a technical report. Light backgrounds make colored elements pop without needing high fill_opacity.
- **Meta brand palette as module constants**: Eight named constants (META_BLUE, META_TEAL, etc.) create visual consistency and brand recognition. Blue = Meta/Llama, Orange = PPO/comparison, Purple = DPO, Green = multilingual/positive.
- **Radial capability diagram**: Six capabilities arranged in a circle around a unified core. The radial layout communicates "single model, many capabilities" more effectively than a list. Connection lines from center to periphery reinforce the unified architecture concept.
- **Sector-based pie chart for data composition**: The 95%/5% English/multilingual split is best shown as sectors, not bars. The visual area makes the imbalance immediately obvious.
- **GrowFromEdge for context window bars**: Bars grow from the left edge, creating a visual metaphor for context "expanding." Each bar is wider than the previous, making the progressive scaling visible.
- **Separate DPO vs PPO scene**: The sequential PPO→DPO training strategy is a key innovation. A dedicated comparison scene with equations, feature lists, and a bottom synthesis section gives it the attention it deserves.
- **create_silo factory for modality visualization**: Three identical silo rectangles with different labels/colors show modality isolation. The factory method keeps them visually consistent.

## Composition

- **Screen layout per scene**:
  - Title: `to_edge(UP, buff=1)` or `to_edge(UP, buff=0.8)` — font_size=36-48, META_BLUE, BOLD
  - Main content: center area
  - Impact/summary text: `DOWN * 2.8` to `DOWN * 3.8`
- **Opening hook — silo to radial transition**:
  - 3 silos: Rectangle width=2, height=3, at `LEFT * 4.5`, ORIGIN, `RIGHT * 4.5`
  - Barriers: Line stroke_width=8, ACCENT_RED, from `UP * 2` to `DOWN * 2`
  - Unified core: Circle radius=1.8, META_BLUE fill_opacity=0.3
  - Capability labels: font_size=16, at radius 3.2 around center (TAU/6 intervals)
  - Connection lines: META_TEAL stroke_width=2, from circle edge to label
- **Training pipeline (Scene 2)**:
  - 5 boxes: Rectangle width=2.2, height=1.8, x-positions linspace(-6, 6, 5)
  - Labels: font_size=18, line_spacing=1.2, centered in box
  - Details: font_size=14, DARK_GRAY, next_to box DOWN buff=0.4
  - Arrows: between boxes, META_DARK_BLUE stroke_width=4
  - Stats row: 4 items, Rectangle width=2.8 height=0.8, arranged RIGHT buff=0.3
- **DPO vs PPO (Scene 3)**:
  - PPO section: title at `LEFT * 4 + UP * 2`, feature list below, equation at bottom
  - DPO section: title at `RIGHT * 4 + UP * 2`, mirror layout
  - PPO equation: MathTex font_size=18, SurroundingRectangle ACCENT_ORANGE fill_opacity=0.1
  - DPO equation: MathTex font_size=14, SurroundingRectangle ACCENT_PURPLE fill_opacity=0.1
  - Sequential synthesis: at `DOWN * 2.8`, flow arrow LEFT*2 to RIGHT*2
- **Multilingual (Scene 4)**:
  - Pie chart (Sectors): radius=2, at `LEFT * 4 + DOWN * 0.5`
  - English sector: angle=0.95*TAU, META_BLUE
  - Multilingual sector: angle=0.05*TAU, ACCENT_GREEN
  - Language grid: 12 items in 4x3 grid, Rectangle width=1.8 height=0.4, at `RIGHT * 3`
- **Context window expansion (Scene 5)**:
  - 5 bars: base_width=0.5 * multiplier (1-5), height=0.6
  - Vertical spacing: `DOWN * (i-2) * 1.2`, left-anchored at `LEFT * 3`
  - Size label: font_size=20, WHITE, centered in bar
  - Stage label: font_size=16, META_TEAL, next_to bar RIGHT buff=0.5
  - Strategy list: font_size=16, at `RIGHT * 3.5 + UP * 1.5`
  - Applications list: font_size=16, at `RIGHT * 3.5 + DOWN * 1.5`
- **Results (Scene 6)**:
  - 3 benchmarks: chart_spacing=2.2 vertical
  - Bars: height=0.35, width proportional to (score/max_score)*4
  - 3 model bars per benchmark: DOWN * j * 0.8 spacing
  - Colors: META_BLUE (Llama 405B), ACCENT_ORANGE (GPT-4), META_TEAL (Llama 70B)
  - Impact statement: at `DOWN * 3.8`

## Color and Styling

| Element | Color | Hex | Role |
|---------|-------|-----|------|
| Background | Light gray | #F8F9FA | Professional paper feel |
| Primary | Meta Blue | #1877F2 | Main brand, titles, Llama elements |
| Secondary | Meta Teal | #42A5F5 | Supporting elements, connection lines |
| Dark Blue | Meta Dark Blue | #166FE5 | Arrows, capability labels |
| Light Blue | Meta Light Blue | #E3F2FD | Not directly used in scenes |
| PPO/Comparison | Accent Orange | #FF6B35 | PPO section, GPT-4 bars |
| Positive/Multi | Accent Green | #4CAF50 | Multilingual, positive outcomes |
| Warning/Old | Accent Red | #F44336 | Limitations, barriers |
| DPO/Special | Accent Purple | #9C27B0 | DPO section, unique elements |
| Body text | DARK_GRAY | — | Descriptions, bullet text |

**Color strategy**: Blue = Meta/Llama brand identity. Orange = PPO and competitive comparisons (GPT-4). Purple = DPO (visually distinct from PPO). Green = multilingual and positive outcomes. Red = limitations and barriers (removed in transition). The three-model bar chart uses Blue/Orange/Teal to distinguish Llama 405B, GPT-4, and Llama 70B.

**Typography**: Titles use weight=BOLD. Three-tier scale: titles (36-48), subtitles/section headers (24-28), body/labels (14-20).

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title FadeIn | Default (~1s) | shift=UP |
| LaggedStartMap (pipeline boxes) | lag_ratio=0.2 | ~1.5s for 5 elements |
| LaggedStartMap (arrows) | lag_ratio=0.2 | Sequential arrow growth |
| Feature FadeIn (DPO/PPO) | run_time=0.3 | Rapid list reveal |
| GrowFromEdge (context bars) | run_time=0.8 | Left-edge growth |
| Sector Create | Default (~1s) | Pie chart segments |
| LaggedStartMap (language grid) | lag_ratio=0.1 | Rapid grid fill |
| Bar Create (benchmarks) | lag_ratio=0.2 | Per benchmark group |
| LaggedStartMap (innovations) | lag_ratio=0.3 | Conclusion bullets |
| FadeOut all elements | Default (~1s) | Per scene cleanup |
| Wait (inter-scene) | 0.5s | Consistent gap |
| Wait (reading time) | 1-3s | Varies by density |
| Estimated total | ~130-150 seconds | 7 scenes, ~18-22s each |

## Patterns

### Pattern: Silo-to-Unified Radial Transition

**What**: Three isolated modality rectangles (silos) with red barrier lines between them transform into a single unified circle with radial capability labels. The barriers fade out, then the silos merge into a circle via Transform. Capability labels appear at equal angular intervals around the circle with connection lines.
**When to use**: Showing convergence of separate systems into one, multimodal fusion, platform unification, any before-after where fragmented components become integrated.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:56-119
text_silo = self.create_silo("Text\nProcessing", META_BLUE, LEFT * 4.5)
image_silo = self.create_silo("Image\nAnalysis", ACCENT_GREEN, ORIGIN)
speech_silo = self.create_silo("Speech\nRecognition", ACCENT_PURPLE, RIGHT * 4.5)

barrier1 = Line(LEFT * 2.5 + UP * 2, LEFT * 2.5 + DOWN * 2, color=ACCENT_RED, stroke_width=8)

# After showing silos + barriers:
unified_core = Circle(radius=1.8, color=META_BLUE, fill_opacity=0.3)
unified_label = Text("Llama 3\nUnified Core", font_size=24, color=WHITE, weight=BOLD)

self.play(
    Transform(VGroup(text_silo, image_silo, speech_silo), VGroup(unified_core, unified_label)),
    run_time=2
)

# Radial labels
for i, cap in enumerate(capabilities):
    angle = i * TAU / len(capabilities)
    pos = 3.2 * (np.cos(angle) * RIGHT + np.sin(angle) * UP)
    label = Text(cap, font_size=16, color=META_DARK_BLUE, weight=BOLD).move_to(pos)
```

### Pattern: Modality Silo Factory

**What**: A helper method that creates consistent Rectangle + Text groups representing isolated processing silos. Each silo has a colored rectangle with low fill_opacity and a bold label. Used for showing modality-specific processing before unification.
**When to use**: Visualizing isolated systems, microservices, separate processing pipelines, any diagram showing independent components before integration.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:129-135
def create_silo(self, label_text, color, position):
    silo = Rectangle(width=2, height=3, color=color, fill_opacity=0.2)
    label = Text(label_text, font_size=20, color=color, weight=BOLD)
    silo_group = VGroup(silo, label)
    silo_group.move_to(position)
    return silo_group
```

### Pattern: Progressive Bar Expansion with GrowFromEdge

**What**: A series of horizontal bars where each successive bar is wider than the previous, growing from the left edge. Creates a visual metaphor for increasing capacity. Each bar has a label inside and a stage description to the right.
**When to use**: Context window scaling, memory expansion, capacity growth over time, progressive training stages, any visualization of increasing quantity.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:418-455
stages = [
    ("8K", "Base Training", 1),
    ("16K", "Stage 1", 2),
    ("32K", "Stage 2", 3),
    ("64K", "Stage 3", 4),
    ("128K", "Final Stage", 5)
]
base_width = 0.5
for i, (size, stage, multiplier) in enumerate(stages):
    bar = Rectangle(width=base_width * multiplier, height=0.6,
                    color=META_BLUE, fill_opacity=0.7)
    bar.move_to(DOWN * (i - 2) * 1.2 + LEFT * 3)
    size_label = Text(size, font_size=20, color=WHITE, weight=BOLD)
    size_label.move_to(bar.get_center())
    self.play(GrowFromEdge(bar, LEFT), run_time=0.8)
```

### Pattern: Sector-Based Pie Chart for Data Composition

**What**: Two Sector mobjects representing proportional data splits. The larger sector dominates visually, making the imbalance immediately obvious. Labels are positioned inside each sector. The chart is offset to one side to leave room for supplementary content.
**When to use**: Data composition, training data distribution, resource allocation, any two-or-three-way split where proportional area communicates the ratio.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:355-373
english_sector = Sector(
    start_angle=0, angle=0.95 * TAU,
    color=META_BLUE, fill_opacity=0.7, radius=2
)
english_label = Text("95% English", font_size=18, color=WHITE, weight=BOLD)
english_label.move_to(english_sector.get_center() + LEFT * 0.5)

multilingual_sector = Sector(
    start_angle=0.95 * TAU, angle=0.05 * TAU,
    color=ACCENT_GREEN, fill_opacity=0.7, radius=2
)
data_chart = VGroup(english_sector, multilingual_sector, english_label, multilingual_label)
data_chart.move_to(LEFT * 4 + DOWN * 0.5)
```

### Pattern: DPO vs PPO Side-by-Side with Equations

**What**: Two-column comparison of training methodologies, each with a title, bullet feature list, and a MathTex equation inside a SurroundingRectangle. A synthesis section at the bottom explains how both methods combine sequentially.
**When to use**: Comparing two algorithmic approaches (DPO vs PPO, Adam vs SGD, batch vs online), any side-by-side with both prose descriptions and mathematical formulations.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:258-298
ppo_equation = MathTex(
    r"L^{CLIP}(\theta) = \hat{\mathbb{E}}_t[\min(r_t(\theta)\hat{A}_t, "
    r"\text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]",
    font_size=18, color=ACCENT_ORANGE
)
ppo_box = SurroundingRectangle(ppo_equation, color=ACCENT_ORANGE,
                                fill_opacity=0.1, buff=0.3)

dpo_equation = MathTex(
    r"L_{DPO}(\pi_\theta) = -\mathbb{E}[\log \sigma(\beta \log "
    r"\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log "
    r"\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)})]",
    font_size=14, color=ACCENT_PURPLE
)
dpo_box = SurroundingRectangle(dpo_equation, color=ACCENT_PURPLE,
                                fill_opacity=0.1, buff=0.3)
```

### Pattern: Multi-Model Benchmark Bar Chart

**What**: Horizontal bars comparing multiple models across benchmarks. Each benchmark has 3 bars (one per model) in distinct colors. Bar width is proportional to score normalized against the max. Model labels on the left, score labels on the right.
**When to use**: Benchmark comparisons, leaderboard results, multi-model performance visualization, any ranked comparison with 2+ competitors across 2+ metrics.

```python
# Source: projects/ML-Manim_Animations/Meta LLama 3/main.py:522-573
benchmarks = [
    ("MMLU", [85.2, 83.1, 79.3], ["Llama 3 405B", "GPT-4", "Llama 3 70B"]),
    ("HumanEval", [89.0, 87.2, 80.5], ["Llama 3 405B", "GPT-4", "Llama 3 70B"]),
    ("MATH", [73.8, 72.6, 64.2], ["Llama 3 405B", "GPT-4", "Llama 3 70B"])
]
colors = [META_BLUE, ACCENT_ORANGE, META_TEAL]
for i, (benchmark, scores, models) in enumerate(benchmarks):
    for j, (score, model, color) in enumerate(zip(scores, models, colors)):
        bar_width = (score / max(scores)) * 4
        bar = Rectangle(width=bar_width, height=0.35, color=color, fill_opacity=0.7)
        bar.move_to(LEFT * 3 + RIGHT * bar_width/2 + chart_y + DOWN * j * 0.8)
```

## Scene Flow

1. **Opening Hook** (0-20s): Title "The Llama 3 Herd of Models" + subtitle. FadeOut. "Traditional LLM Limitations" with 3 modality silos (Text, Image, Speech) in colored rectangles. Red barrier lines appear. Title transforms to "Llama 3's Unified Approach", barriers fade. Silos transform into a central blue circle. 6 capability labels appear radially with connection lines. FadeOut all.
2. **Training Pipeline** (20-40s): "Llama 3 Training Pipeline" title. 5 stage boxes (Pre-training → SFT → Rejection Sampling → PPO → DPO) animate left-to-right with labels and detail text. Arrows grow between boxes. Stats row at bottom: "15.6T Tokens, 405B Parameters, 128K Context, 16K H100 GPUs." FadeOut all.
3. **DPO vs PPO Comparison** (40-60s): "DPO vs PPO: Training Methodology" title. Left: PPO features + clipped objective equation in orange SurroundingRectangle. Right: DPO features + preference loss equation in purple SurroundingRectangle. Bottom: "Sequential Application: Best of Both" with flow arrow and synthesis text. FadeOut all.
4. **Multilingual Training** (60-76s): "Multilingual Training Strategy" title. Left: Sector pie chart (95% English blue, 5% multilingual green). Right: "30+ Languages Supported" with 4x3 grid of language boxes. FadeOut all.
5. **Context Window Expansion** (76-96s): "Context Window Expansion" title. 5 horizontal bars growing from left edge (8K→128K), each wider than previous. Right side: "Staged Training Strategy" with 4 numbered points + "Applications" with 4 use cases. FadeOut all.
6. **Results and Impact** (96-116s): "Llama 3 Performance Results" title. 3 benchmark groups (MMLU, HumanEval, MATH) with 3 colored bars each (Llama 405B, GPT-4, Llama 70B). Score labels on right, model labels on left. Impact statement: "First open-source model to match GPT-4." FadeOut all.
7. **Conclusion** (116-140s): "The Llama 3 Revolution" title. "Key Innovations" with 6 bullet points in META_BLUE. "Impact on AI Development" with green synthesis text. "Meta AI" branding at bottom right. FadeOut all.

> Full file: `projects/ML-Manim_Animations/Meta LLama 3/main.py` (673 lines)
