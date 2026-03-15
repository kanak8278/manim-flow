---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/autoencoder.py
project: manim-animations
domain: [machine_learning, deep_learning, statistics, classification]
elements: [equation, formula, axes, function_plot, area_under_curve, arrow, label, surrounding_rect]
animations: [write, fade_in, fade_out, replacement_transform, transform, color_change, move, draw]
layouts: [centered, side_by_side, edge_anchored]
techniques: [progressive_disclosure, scene_segmentation, multi_scene_in_one_class]
purpose: [decomposition, transformation, classification, step_by_step]
mobjects: [MathTex, Text, Axes, SurroundingRectangle, Arrow, Line, VGroup]
manim_animations: [Write, FadeIn, FadeOut, ReplacementTransform, Transform, TransformMatchingShapes, Create, GrowArrow]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 230
scene_classes: [Autoencoder]
---

## Summary

Visualizes an autoencoder pipeline in three parts: (1) encoder/decoder flow showing original vector X compressing to latent vector Z then reconstructing to X-tilde, (2) reconstruction error as the squared L2 norm of the difference vector, and (3) classification using a chi-squared distribution with colored regions for crisis/no-crisis decision boundaries. Uses ReplacementTransform to morph vectors between stages and scipy's chi2 distribution for the classification curve.

## Design Decisions

- **Three-part narrative in one scene class**: The scene segments into encoder-decoder flow, reconstruction error, and classification. Each part clears the screen before the next. This mirrors the conceptual pipeline: compress, measure error, classify.
- **MathTex vectors instead of Matrix mobject**: Commented-out Matrix code shows the author switched to raw MathTex bmatrix. This gives more control over individual character indexing for selective coloring via the change_colors helper.
- **Selective character coloring via index**: Subscript numbers in vectors are colored (BLUE for original/reconstructed, GREEN for latent) by targeting specific character indices. This draws attention to which variables belong to which space without labels.
- **ReplacementTransform for encoding/decoding**: The original vector morphs into the latent vector, and the latent vector morphs into the reconstructed vector. This visually communicates "compression" and "reconstruction" as spatial transformations.
- **Chi-squared distribution for classification**: The error norm follows a chi-squared distribution. The colored areas (BLUE = no crisis, RED = crisis) split by a threshold line show how the autoencoder error is used as a classifier.
- **Animated error norm sliding across threshold**: The norm label starts BLUE (no crisis), slides right past the threshold, and turns RED (crisis). This demonstrates how the same measurement changes classification based on magnitude.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — changes text per part
  - Original vector: `shift(LEFT * 5)` — left side
  - Latent vector: centered (default position), font_size=36
  - Reconstructed vector: `shift(RIGHT * 5)` — right side
  - Encoder/Decoder labels: `next_to(latent_vector, LEFT/RIGHT, buff=1)`, font_size=24
  - Chi-squared axes (Part 3): centered, x_length=6, y_length=3
  - Norm label: `next_to(axes, DOWN, buff=0.5).shift(LEFT * 2)`
- **Axes configuration (Part 3)**: x_range=[0, 20, 1], y_range=[0, 0.2, 0.01], no numbers, no ticks
- **Threshold line**: vertical at x=9.5, from y=0 to y=0.2

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Vector subscripts (X) | BLUE | Indices manually targeted |
| Latent subscripts (Z) | GREEN | Indices manually targeted |
| Reconstructed subscripts | BLUE | Same as original |
| Norm difference subscripts | BLUE | Indices manually targeted |
| Chi-squared curve | GREEN | Full distribution |
| No-crisis area | BLUE | axes.get_area, left of threshold |
| Crisis area | RED | axes.get_area, right of threshold |
| Threshold line | GREEN | Vertical Line at x=9.5 |
| "SEM CRISE" text | WHITE with BLUE "SEM" | t2c={"SEM": BLUE}, font_size=18 |
| "COM CRISE" text | WHITE with RED "COM" | t2c={"COM": RED}, font_size=18 |
| Norm label | BLUE then RED | Animated color change |
| Encoder/Decoder boxes | WHITE | SurroundingRectangle default |

Color strategy: BLUE represents original/known data space, GREEN represents latent/compressed space. In classification, BLUE = safe (no crisis), RED = anomalous (crisis). The norm label changing from BLUE to RED demonstrates the classification boundary crossing.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| Vector Write | ~1s | + 1.5s wait |
| ReplacementTransform (encode) | run_time=2 | + 1s wait |
| Encoder/Decoder FadeIn | ~1s | + 1s wait |
| SurroundingRectangle Create | ~1s | + 1.5s wait, then FadeOut |
| Part 2 Transform | run_time=2 | TransformMatchingShapes |
| Chi-squared curve Create | run_time=3 | + 2s wait |
| Area Create | run_time=2 | rate_func=linear |
| Norm slide | run_time=2 | shift(RIGHT * 4) |
| Total video | ~75 seconds | Three-part scene |

## Patterns

### Pattern: Selective Character Coloring in MathTex

**What**: Color specific characters within a MathTex expression by indexing into the first submobject `tex[0][idx]`. A helper function `change_colors` takes a list of character indices and applies a color. This requires manually identifying which index corresponds to which character.
**When to use**: Coloring subscripts, variables, or operators within equations to show which terms belong to which category. Useful for encoding/decoding visualizations, equation derivations, or any math where different symbols have different semantic meanings.

```python
# Source: projects/manim-animations/src/autoencoder.py:4-6
def change_colors(tex: MathTex, indices: list[int], color: ParsableManimColor) -> None:
    for idx in indices:
        tex[0][idx].set_color(color)

# Usage: color subscript numbers in a bmatrix vector
vec_ori_num_idx = [8, 10, 12, 17, 18, 19]
change_colors(vetor_original, vec_ori_num_idx, BLUE)
```

### Pattern: Vector Morphing with ReplacementTransform

**What**: Use ReplacementTransform on a copy of a vector to visually "send" it to another location while keeping the original in place. The `.copy()` is critical — without it, the original disappears. This creates the effect of data flowing through a pipeline.
**When to use**: Encoder-decoder flows, data pipelines, any transformation where input produces output while the input should remain visible. Also works for showing how one representation becomes another.

```python
# Source: projects/manim-animations/src/autoencoder.py:78-79
self.play(ReplacementTransform(vetor_original.copy(), vetor_espaco_latente), run_time=2)
```

### Pattern: Colored Distribution Areas for Classification

**What**: Split a probability distribution into colored regions using `axes.get_area()` with different x_ranges and colors. A vertical threshold line separates the regions. Each area represents a classification outcome. Arrows and labels annotate each region.
**When to use**: Binary classification visualization, hypothesis testing (accept/reject regions), anomaly detection thresholds, any scenario where a continuous score maps to discrete categories via a cutoff.

```python
# Source: projects/manim-animations/src/autoencoder.py:169-179
area_neg = axes.get_area(
    graph=axes.plot(lambda x: chi2.pdf(x, graus_liberdade), x_range=[0, 9.5], color=BLUE),
    x_range=(0, 9.5),
    color=BLUE
)

area_pos = axes.get_area(
    graph=axes.plot(lambda x: chi2.pdf(x, graus_liberdade), x_range=[9.5, 20], color=RED),
    x_range=(9.5, 20),
    color=RED
)
```

### Pattern: Animated Object Sliding Across Threshold

**What**: Move a label (the error norm) horizontally across the screen while changing its color to demonstrate how the same quantity changes classification. First set to BLUE (safe), animate slide with `shift(RIGHT * 4)`, then set to RED (anomalous).
**When to use**: Decision boundary demonstrations, threshold-based classification, showing how a continuous value crosses a critical point. Works for anomaly detection, binary classifiers, or any pass/fail visualization.

```python
# Source: projects/manim-animations/src/autoencoder.py:220-229
self.play(FadeIn(norma_vetor))
self.wait(2)
self.play(norma_vetor.animate.set_color(BLUE))
self.wait(1)
self.play(norma_vetor.animate.shift(RIGHT * 4), run_time=2)
self.wait(1)
self.play(norma_vetor.animate.set_color(RED))
```

## Scene Flow

1. **Part 1 - Encoder/Decoder** (0-25s): Title "Autoencoder" writes. Original vector X (276-dim) appears left. Morphs into latent vector Z (center). "Encoder" label and box appear. Latent morphs into reconstructed X-tilde (right). "Decoder" label and box appear. Middle elements fade out, leaving original and reconstructed vectors.
2. **Part 2 - Reconstruction Error** (25-35s): Title changes to "Autoencoder - Erro de reconstrucao". Original and reconstructed vectors morph (TransformMatchingShapes) into a difference norm expression. Error vector label writes. All elements fade out.
3. **Part 3 - Classification** (35-75s): Title "Classificacao" writes. Chi-squared axes create. Green distribution curve draws (3s). Vertical threshold line appears. Blue area fills left of threshold ("SEM CRISE" = no crisis). Red area fills right of threshold ("COM CRISE" = crisis). Error norm label fades in, turns BLUE, slides right past threshold, turns RED. Final 3s hold.

> Full file: `projects/manim-animations/src/autoencoder.py` (230 lines)
