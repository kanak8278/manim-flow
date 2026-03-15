---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/_2024/transformers/mlp.py
project: manim-interactive
domain: [machine_learning, deep_learning, neural_networks, transformers, linear_algebra]
elements: [matrix, node, network, neuron, layer, weight_connection, arrow, label, title, surrounding_rect, axes, formula, cube]
animations: [fade_in, fade_out, write, transform, replacement_transform, highlight, indicate, lagged_start, passing_flash, grow, camera_rotate]
layouts: [flow_left_right, layered, side_by_side, vertical_stack]
techniques: [three_d_camera, custom_mobject, factory_pattern, progressive_disclosure, data_driven, passing_flash_signal, interactive_scene]
purpose: [demonstration, step_by_step, decomposition, exploration]
mobjects: [WeightMatrix, NumericEmbedding, EmbeddingArray, Cube, VCube, Axes, SurroundingRectangle, VGroup, Text, Arrow, Vector, Dot, Line, Rectangle, BackgroundRectangle]
manim_animations: [FadeIn, FadeOut, Write, ShowCreation, Transform, TransformMatchingStrings, GrowArrow, LaggedStartMap, LaggedStart, VShowPassingFlash, RandomizeMatrixEntries, Succession, MoveToTarget, TransformFromCopy, Restore]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 2627
scene_classes: [LastTwoChapters, AltLastTwoChapters, MLPIcon, MLPStepsPreview, MatricesVsIntuition, BasicMLPWalkThrough]
---

## Summary

Comprehensive visualization of the MLP (Multilayer Perceptron) component within transformers. Covers the full pedagogical arc: introducing MLP blocks as transformer components, showing the Linear-ReLU-Linear pipeline structure, demonstrating weight matrices as up-projection and down-projection, visualizing neuron activations, and connecting the abstract math to concrete examples (Michael Jordan plays Basketball). Uses 3D camera work with Cube blocks for transformer architecture overview, WeightMatrix custom mobjects for parameter visualization, and data-flow animations showing information propagating through network layers.

## Design Decisions

- **3D transformer blocks**: Transformer shown as stacked Cube objects (alternating attention/MLP blocks) with 3D camera rotation. Blocks are semi-transparent (opacity=0.8) with depth-test disabled for consistent rendering.
- **MLP icon as dot-line network**: Classical neural network diagram with 3 layers (input, hidden 4x, output), random opacity on dots and random-colored weight lines. Lines use value_to_color for weight visualization.
- **Linear-ReLU-Linear pipeline layout**: Three arrows with labels arranged left-to-right, up_proj matrix above first arrow, ReLU graph above second, down_proj matrix above third. Clean decomposition of MLP steps.
- **Toy example grounding**: Abstract matrices grounded with "Michael Jordan plays Basketball" - row of up_proj corresponds to entity, column of down_proj to fact. Makes matrix factorization intuitive.
- **Frame reorientation for depth**: Frequent frame.animate.reorient() calls to show 3D structure from different angles as the explanation progresses.

## Composition

- **Transformer blocks**: Cube(color=GREY_D, opacity=0.8), set_shape(5, 3, 1), arranged along OUT axis with 0.5 buff. Total depth set to 8.
- **MLP icon**: 3 layers of dots (5, 10, 5 by default), dot_buff=0.15, layer_buff=1.5. Weight lines: stroke_width=3*random()**3.
- **WeightMatrix**: shape=(10, 6) for up_proj, shape=(6, 10) for down_proj, matched to arrow width.
- **ReLU plot**: Axes((-4, 4), (0, 4)), graph stroke YELLOW width 5, plot width = 0.75 * arrow width.
- **Structure layout**: arrows arranged horizontally, labels below arrows, matrices/plot above arrows.
- **EmbeddingArray**: shape=(6, 9), width=10 for the main walkthrough.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Transformer blocks | GREY_D | opacity=0.8, shading=(0.5, 0.5, 0.0) |
| Attention icon dots | WHITE | Random opacity (random()**5) |
| MLP weight lines | value_to_color() | Random values [-10, 10], width=3*random()**3 |
| MLP dots | WHITE | Random opacity, stroke WHITE 0.5 |
| Trans title | Default | font_size=96 |
| Attention/MLP titles | Default | font_size=72 |
| ReLU graph | YELLOW | stroke_width=5 |
| Structure labels | Default | "Linear", "ReLU", "Linear" |
| Question text | Matches rect color | font_size=90, border_width=0.5 |
| Easy label | GREEN | For structure description |
| Hard label | RED | For emergent behavior description |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Block fade in | LaggedStartMap lag_ratio=0.1 | Scale 1.5 entry |
| Camera reorient | run_time=2-4 | Frame.animate.reorient |
| Network write | run_time=5 | stroke_width=0.5, lag_ratio=1e-2 |
| VShowPassingFlash | run_time=3 | time_width=1.5, lag_ratio=5e-3 |
| RandomizeMatrixEntries | Default | Built-in matrix animation |
| data_modifying_matrix | Default | font_size=16, word_shape=(5, 5) |

## Patterns

### Pattern: 3D Transformer Block Architecture

**What**: Visualizes transformer architecture as stacked 3D Cube objects alternating between attention and MLP blocks. Blocks are semi-transparent, depth-sorted, and revealed with LaggedStartMap FadeIn while the camera orbits.

**When to use**: High-level architecture overviews of transformers, neural network layer stacking, any pipeline where you want to show sequential processing stages as physical blocks in 3D space.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/mlp.py:22-38
blocks = Group(self.get_block() for x in range(10))
blocks[1::2].stretch(2, 2).set_opacity(1)
blocks.arrange(OUT, buff=0.5)
blocks.set_depth(8, stretch=True)
blocks.set_opacity(0.8)
blocks.apply_depth_test()

self.play(
    frame.animate.reorient(-32, 0, 0, (0.56, 2.48, 0.32), 12.75),
    LaggedStartMap(FadeIn, blocks, shift=0.25 * UP, scale=1.5, lag_ratio=0.1),
    FadeIn(trans_title, UP),
)

def get_block(self, width=5, height=3, depth=1, color=GREY_D, opacity=0.8):
    block = Cube(color=color, opacity=opacity)
    block.deactivate_depth_test()
    block.set_shape(width, height, depth)
    block.set_shading(0.5, 0.5, 0.0)
    block.sort(lambda p: np.dot(p, [-1, 1, 1]))
    return block
```

### Pattern: Neural Network Icon with Random Weights

**What**: Creates a classic 3-layer neural network diagram with dots as neurons and lines as weights. Dot opacity and line color/width are randomized to suggest learned parameters. value_to_color maps weight values to a diverging color scale.

**When to use**: MLP visualizations, neural network architecture diagrams, showing parameter density. The random styling gives the impression of a trained network without needing real weights.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/mlp.py:145-171
def get_mlp_icon(self, block, dot_buff=0.15, layer_buff=1.5, layer0_size=5):
    layers = VGroup(
        Dot().get_grid(layer0_size, 1, buff=dot_buff),
        Dot().get_grid(2 * layer0_size, 1, buff=dot_buff),
        Dot().get_grid(layer0_size, 1, buff=dot_buff),
    )
    layers.arrange(RIGHT, buff=layer_buff)
    for layer in layers:
        for dot in layer:
            dot.set_fill(opacity=random.random())
    lines = VGroup(
        Line(dot1.get_center(), dot2.get_center(), buff=dot1.get_width() / 2)
        for l1, l2 in zip(layers, layers[1:])
        for dot1 in l1 for dot2 in l2
    )
    for line in lines:
        line.set_stroke(color=value_to_color(random.uniform(-10, 10)),
                       width=3 * random.random()**3)
    return VGroup(layers, lines)
```

### Pattern: Passing Flash Signal Propagation

**What**: Shows information flowing through a neural network by creating thickened copies of weight lines and applying VShowPassingFlash. The flash travels along each line with time_width controlling the pulse length, creating a "signal propagation" effect.

**When to use**: Showing forward pass through a network, data flow through pipeline stages, signal propagation in any graph/network structure. The flash effect is more dynamic than simple color changes.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/mlp.py:221-227
thick_layers = VGroup(network[1].family_members_with_points()).copy()
for line in thick_layers:
    line.set_stroke(width=2 * line.get_width())
    line.insert_n_curves(20)
self.play(LaggedStartMap(VShowPassingFlash, thick_layers,
    time_width=1.5, lag_ratio=5e-3, run_time=3))
```

### Pattern: Matrix Row/Column Fact Encoding

**What**: Visualizes how rows of one matrix and columns of another encode facts (entity-attribute pairs). Uses SurroundingRectangle to highlight a row/column, BackgroundRectangle to dim the rest, and Brace + Text to label what each encodes.

**When to use**: Explaining matrix factorization, word embeddings, knowledge storage in neural networks, any scenario where matrix rows/columns have semantic meaning.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/mlp.py:340-369
row_rect = SurroundingRectangle(low_matrices[0].get_rows()[0], buff=0.1)
col_rect = SurroundingRectangle(low_matrices[1].get_columns()[0], buff=0.1)
fact = Text("Michael Jordan plays Basketball", font_size=36)
mj_brace = Brace(mj, DOWN, buff=0.1)
bb_brace = Brace(bb, DOWN).match_y(mj_brace)
row_cover = BackgroundRectangle(low_matrices[0].get_rows()[1:], buff=0.05)
row_cover.set_fill(BLACK, 0.75)

self.play(LaggedStart(
    FadeIn(row_cover), FadeIn(row_rect),
    GrowFromCenter(mj_brace), FadeIn(mj, 0.5 * UP)
))
```

## Scene Flow

1. **Architecture overview** (0-15s): 3D transformer blocks appear, camera orbits. Attention and MLP blocks separated.
2. **MLP structure** (15-30s): Linear-ReLU-Linear pipeline shown with arrows, matrices, and ReLU graph. Labeled "Easy".
3. **Emergent behavior** (30-45s): Contrasted as "Exceedingly challenging". Data flies into matrices.
4. **Toy example** (45-75s): Michael Jordan fact encoded as matrix row/column pair. Matrices randomized.
5. **Basic walkthrough** (75s+): EmbeddingArray enters MLP block, single vector highlighted, operations shown step by step.

## manimlib Notes

- `InteractiveScene` base with `self.frame` for camera control
- `set_floor_plane("xz")` for 3D scene setup
- `self.camera.light_source.set_z(15)` for 3D lighting
- Custom mobjects from helpers.py: WeightMatrix, NumericEmbedding, EmbeddingArray, RandomizeMatrixEntries, data_modifying_matrix, value_to_color
- `VCube` for transparent block with individually styled faces
- `block.sort(lambda p: np.dot(p, [-1, 1, 1]))` for correct face rendering order
