---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/_2024/transformers/attention.py
project: manim-interactive
domain: [machine_learning, deep_learning, transformers, nlp, attention_mechanism, linear_algebra]
elements: [matrix, vector, arrow, axes, surface_3d, label, equation, surrounding_rect, dot]
animations: [transform, fade_in, fade_out, grow_arrow, lagged_start, stagger, write, camera_rotate]
layouts: [grid, flow_left_right, centered, layered, side_by_side]
techniques: [value_tracker, three_d_camera, custom_mobject, color_gradient, algorithm_class_separation, progressive_disclosure, data_driven]
purpose: [decomposition, transformation, demonstration, step_by_step, process]
mobjects: [WeightMatrix, NumericEmbedding, Axes, ThreeDAxes, NumberPlane, Arrow, SurroundingRectangle, VGroup, Text, MathTex, Dot]
manim_animations: [FadeIn, FadeOut, FadeTransform, TransformFromCopy, GrowArrow, LaggedStartMap, RandomizeMatrixEntries, ShowCreation, Write]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 4093
scene_classes: [QueryMap, KeyMap, DescribeAttentionEquation, IntroduceValueMatrix, CountMatrixParameters, OutputMatrix]
---

## Summary

Visualizes the core linear algebra of transformer attention — how embeddings are transformed into Query, Key, and Value vectors via weight matrices, and how these interact to produce attention patterns. Uses 3D visualization for the Q/K mapping (input vector in 3D space projected onto a 2D plane via matrix multiplication), grid-based attention pattern display, and matrix arithmetic animations. This is 3Blue1Brown's actual production code for the transformer explainer series.

## Design Decisions

- **3D for Q/K projections**: The input embedding lives in a high-dimensional space (shown as 3D), and the weight matrix W_Q projects it onto a lower-dimensional query space (shown as a 2D plane). Using ThreeDAxes with a NumberPlane makes the dimensionality reduction physically visible — you see the vector "falling" onto a plane.
- **Color coding Q=YELLOW, K=TEAL, V=RED**: Consistent across ALL transformer scenes. The viewer learns this mapping once and it carries through 30+ scenes. Query is yellow (active/searching), Key is teal (matching/receptive), Value is red (the actual content).
- **WeightMatrix with value-to-color**: Matrix entries are color-mapped: positive=BLUE gradient, negative=RED gradient. The viewer can see the "personality" of each matrix without reading numbers. RandomizeMatrixEntries creates a visual "computing" effect.
- **Grid-based attention patterns**: Attention weights shown as an NxN grid where each cell contains a Dot sized proportional to the weight. This is more informative than a heatmap — you can see individual attention relationships as discrete objects.
- **Ambient camera rotation (1 degree/frame)**: Keeps the 3D scenes feeling dynamic and helps depth perception. Without rotation, 3D scenes look flat.

## Composition

- **3D Q/K mapping scene**:
  - ThreeDAxes at center, NumberPlane on xz-plane (rotated 90 degrees RIGHT)
  - Field of view: 30 degrees
  - Camera orientation: (-32, 0, 0) for Query, different angles for Key
  - Input vector: 3D arrow from origin, color=BLUE_B
  - Output vector: on the 2D plane
  - Transformation arrow with label (W_Q in YELLOW or W_K in TEAL)
- **Attention equation scene**:
  - Q vectors arranged RIGHT with h_buff=0.8
  - K vectors arranged DOWN with MED_LARGE_BUFF
  - Grid at intersection: dot products at each cell
  - Denominator (sqrt) copied from equation and scaled to fit
  - Grid lines: GREY_B at 1 stroke width
- **Matrix parameter counting**:
  - Three matrices (Q, K, V) arranged DOWN with 0.75 buff
  - Titles LEFT with LARGE_BUFF
  - Matrix max width: 4 units
  - Title aligned to matrix center: title.match_y(matrix)

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Query (Q) | YELLOW | All Q-related: labels, arrows, matrices |
| Key (K) | TEAL | All K-related: labels, arrows, matrices |
| Value (V) | RED / RED_B / RED_C | All V-related |
| Input embeddings | BLUE_B | 3D vector arrows |
| Matrix positive values | BLUE_E → BLUE_B | Gradient by magnitude |
| Matrix negative values | RED_E → RED_B | Gradient by magnitude |
| Grid lines | GREY_B | stroke_width=1 |
| Masked cells | RED | fill_opacity=0.75 |
| Text backstroke | BLACK, width=5 | Visibility on any background |
| Attention dots | GREY_B / GREY_C | radius proportional to weight |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| 3D vector transformation | run_time=2 | GrowArrow + FadeTransform |
| RandomizeMatrixEntries | run_time=3 | Visual "computing" effect |
| Matrix row highlighting | run_time=0.75 per row | Sequential illumination |
| Attention grid reveal | lag_ratio=0.05 | Smooth cascading |
| Large grid zoom-out | run_time=20 | 50x50 dramatic reveal |
| Camera ambient rotation | 1 degree continuous | Depth perception |
| Cross-attention lines | run_time=2, lag_ratio=0.01 | Rapid connection drawing |

## Patterns

### Pattern: 3D Matrix Projection Visualization

**What**: Show a matrix multiplication as projecting a 3D vector onto a 2D plane. Uses ThreeDAxes with a NumberPlane rotated to represent the target subspace. An arrow grows from the 3D vector and a transformed arrow appears on the plane. Ambient camera rotation adds depth perception.
**When to use**: Linear transformations, dimensionality reduction, PCA, any projection from high-D to low-D space. Also works for showing how encoder/decoder spaces relate.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/attention.py (QueryMap scene)
# Setup 3D space with 2D target plane
axes = ThreeDAxes()
plane = NumberPlane()
plane.rotate(90 * DEGREES, RIGHT)  # xz-plane as target

# Camera setup
frame = self.frame
frame.set_field_of_view(30 * DEGREES)
frame.reorient(-32, 0, 0)
self.play(frame.animate.add_ambient_rotation(1 * DEGREES))

# Show input vector in 3D
input_arrow = Arrow(axes.c2p(0, 0, 0), axes.c2p(*coords), buff=0, color=BLUE_B)

# Show projection via matrix
label = Tex("W_Q", color=YELLOW)
self.play(GrowArrow(transform_arrow), FadeIn(label))
self.play(FadeTransform(input_arrow.copy(), output_arrow), run_time=2)
```

### Pattern: Attention Grid with Proportional Dots

**What**: An NxN grid where each cell contains a Dot whose radius is proportional to the attention weight. Created with Square().get_grid(). Dots are GREY_B/GREY_C. Masked positions (causal attention) can be filled RED. The grid itself has GREY_B stroke lines. This is more readable than a heatmap for small N because individual relationships are discrete objects.
**When to use**: Attention weight visualization, confusion matrices, correlation displays, any NxN relationship matrix where individual cell values matter.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/attention.py (DescribeAttentionEquation)
# Create grid
grid = Square().get_grid(n, n, buff=0)
grid.set_stroke(GREY_B, 1)

# Add dots sized by attention weight
for i, square in enumerate(grid):
    row, col = divmod(i, n)
    value = attention_weights[row][col]
    if value < 1e-3:
        continue
    dot = Dot(radius=value ** 0.75)
    dot.set_fill(GREY_B)
    dot.move_to(square)
    grid.add(dot)
```

### Pattern: WeightMatrix with Color-Mapped Values

**What**: A custom matrix mobject where each entry is colored by its value — positive values in blue gradient, negative in red gradient. RandomizeMatrixEntries animates all entries changing simultaneously, creating a "computing" visual effect. Used for W_Q, W_K, W_V matrices.
**When to use**: Any weight matrix visualization, neural network parameters, covariance matrices, any matrix where the sign and magnitude of values is meaningful.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/helpers.py
# WeightMatrix auto-colors entries
matrix = WeightMatrix(shape=(6, 8), value_range=(-9.9, 9.9))

# Color mapping function
def value_to_color(value, low_positive_color=BLUE_E, high_positive_color=BLUE_B,
                   low_negative_color=RED_E, high_negative_color=RED_B,
                   min_value=0.0, max_value=10.0):
    # Maps scalar to color gradient

# Animate "computing" effect
self.play(RandomizeMatrixEntries(matrix), run_time=3)
```

### Pattern: ContextAnimation (Attention Flow)

**What**: Animated curved paths flowing from source objects to a target object, showing information flow. Stroke width varies temporally (peaks at max_stroke_width). Multiple sources create parallel flowing lines to one target. The hue_range parameter controls the color palette of connection lines.
**When to use**: Attention visualization, information flow, influence diagrams, any "many contribute to one" relationship. Essential for showing how context words influence a target word.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/helpers.py
ContextAnimation(
    target_mob,
    sources,
    strengths=[1, 1],
    time_width=2,
    max_stroke_width=10,
    lag_ratio=0.2,
    path_arc=150 * DEGREES,
    hue_range=(0.1, 0.3),
    run_time=2
)
```

### Pattern: Cross-Attention Bipartite Connection

**What**: Two token sequences (e.g., English → French) with curved lines connecting them. Each line's stroke opacity equals the attention weight — strong connections are visible, weak ones fade. Stroke color is blended from source and target token colors. Lines use path_arc=-PI/2 for smooth curves.
**When to use**: Translation attention, encoder-decoder attention, any bipartite relationship between two sequences.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/attention.py (CrossAttention)
# Two token groups
en_tokens.arrange(DOWN, buff=2.0)
fr_tokens.arrange(DOWN, buff=2.0)

# Connection lines
for i, en_tok in enumerate(en_tokens):
    for j, fr_tok in enumerate(fr_tokens):
        line = Line(en_tok, fr_tok, path_arc=-PI/2)
        weight = attention_matrix[i][j]
        line.set_stroke(
            color=interpolate_color(en_tok.get_color(), fr_tok.get_color(), 0.5),
            opacity=weight
        )
lines_group = VGroup(*all_lines)
self.play(ShowCreation(lines_group, lag_ratio=0.01), run_time=2)
```

## Scene Flow

1. **Q/K Mapping** (3D): Input vector in 3D space → W_Q projects onto 2D query plane. Camera rotates slowly. Then same for W_K to key plane. Shows dimensionality reduction physically.
2. **Attention Equation**: Q vectors across top, K vectors down left side. Grid forms at intersection. Each cell fills with dot product → scale by sqrt(d_k) → softmax. Shows the full attention(Q,K,V) computation.
3. **Masking**: Two NxN grids side by side. Left shows raw scores. Lower triangle masked with -infinity in RED. Right shows softmax output where masked cells are zero.
4. **Value Integration**: V vectors multiplied by attention weights. Shows how each word's value contributes to the output, weighted by attention score.
5. **Multi-Head**: 15 attention patterns arranged in 3D depth. Camera pulls back to show diversity. Then patterns flatten to 2D for comparison.
6. **Parameter Counting**: Three matrices (Q, K, V) with dimension labels. Count rows × columns × 3 heads. Shows total parameter count.

> Full file: `projects/manim-interactive/projects/_2024/transformers/attention.py` (4093 lines, split across multiple concept docs)
