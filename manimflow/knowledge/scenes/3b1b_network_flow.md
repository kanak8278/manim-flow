---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/_2024/transformers/network_flow.py
project: manim-interactive
domain: [machine_learning, deep_learning, neural_networks, transformers, nlp]
elements: [matrix, node, network, layer, weight_connection, token, arrow, label, title, cube, surrounding_rect]
animations: [fade_in, fade_out, write, transform, replacement_transform, lagged_start, passing_flash, camera_rotate, draw, grow]
layouts: [flow_left_right, layered, horizontal_row]
techniques: [three_d_camera, custom_mobject, progressive_disclosure, interactive_scene, passing_flash_signal, data_driven]
purpose: [demonstration, step_by_step, overview, progression]
mobjects: [EmbeddingArray, NumericEmbedding, Cube, Text, VGroup, Line, Dot, Arrow, SurroundingRectangle, Underline]
manim_animations: [FadeIn, FadeOut, Write, ShowCreation, ShowCreationThenFadeOut, TransformFromCopy, LaggedStartMap, LaggedStart, VShowPassingFlash, GrowArrow, DrawBorderThenFill, ShowIncreasingSubsets, RandomizeMatrixEntries, Restore, MoveToTarget]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 1531
scene_classes: [HighLevelNetworkFlow]
---

## Summary

Visualizes the complete forward pass of a transformer model from text input to next-token prediction. Shows text being tokenized into colored rectangles, converted to embedding vectors (EmbeddingArray), then passed through alternating attention and MLP blocks rendered as 3D Cubes. Attention is visualized with arc-shaped passing flashes between embeddings, MLP blocks show neuron layers with weight connections. The camera orbits in 3D throughout. Culminates with unembedding to produce a probability distribution over next tokens. The scene is a masterclass in progressive disclosure of a complex system.

## Design Decisions

- **Text to tokens to vectors pipeline**: Shows the full embedding pipeline - raw text split into tokens with colored rectangles, arrows pointing down to NumericEmbedding vectors. This grounds the abstract vectors in concrete text.
- **3D blocks for attention/MLP**: Cubes (GREY_E, opacity=0.75) represent processing stages. Layers pass through blocks along the Z-axis (OUT direction), with camera orbiting to show depth.
- **Arc-based attention visualization**: Attention shown as curved lines between embedding positions (path_arc=PI/3). Random bright colors in hue range (0.1, 0.3) and stroke width scaled by random()**5 give a natural attention weight feel.
- **Progressive depth traversal**: Each block pass adds z_buff=3.0 to layer position. Camera follows along Z-axis, creating a "journey through the network" feel.
- **Embedding columns maintain token identity**: Each column in the EmbeddingArray stays aligned with its source token above, maintaining the spatial correspondence throughout.

## Composition

- **Token blocks**: Text scaled 0.6, colored rectangles via get_piece_rectangles(). Last token rectangle colored YELLOW with "???" below.
- **EmbeddingArray**: shape=(10, n_tokens) where n_tokens=len(words), height=4. No dots_index for full display.
- **Attention/MLP blocks**: Cube body with size_buff=1.0 around layer. depth=2.0 for attention, depth=4.0 for MLP. Titles font_size=96 for attention, 72 for MLP.
- **MLP neurons**: 20 neurons, GREY_C color, shading=(0.25, 0.75, 0.2). Dot columns arranged with configurable buff.
- **Block title**: Text positioned above block (block_to_title_direction=UP), backstroke BLACK width 3.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Token rectangles | Per-token colors | Via get_piece_rectangles, last token YELLOW |
| Question marks | Default | Below last token rectangle |
| Block body | GREY_E | opacity=0.75, shading=(0.25, 0.1, 0.0) |
| Attention arcs | random_bright_color | hue_range=(0.1, 0.3), width=5*random()**5 |
| MLP neurons | GREY_C | shading=(0.25, 0.75, 0.2) |
| MLP weight lines | value_to_color | Random weights, width varies |
| Block titles | Default | font_size=96 (attention) or 72 (MLP) |
| Bracket color | GREY_B | EmbeddingArray brackets |
| Backstroke | BLACK, width 3 | On all text labels |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Text display | run_time=1 | ShowIncreasingSubsets |
| Token coloring | LaggedStart lag_ratio=0.02 | DrawBorderThenFill for rectangles |
| Embedding entry | LaggedStartMap | FadeIn shift=0.5*DOWN |
| Attention animation | run_time=5 | Combined VShowPassingFlash + ShowCreationThenFadeOut |
| Block traversal | run_time=2 | Camera reorient + layer transform |
| Token label arrows | run_time=4 | VFadeInThenOut, lag_ratio=0.25 |

## Patterns

### Pattern: Text Tokenization to Embedding Vectors

**What**: Splits text into tokens (words or subwords), wraps each in a colored rectangle, then creates arrows pointing from each token down to a corresponding NumericEmbedding vector column. The last token position shows "???" to highlight the prediction target.

**When to use**: Explaining how text enters a language model, token embedding visualization, any NLP pipeline where you need to show the text-to-vector conversion step. The colored rectangles maintain identity across the transformation.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/network_flow.py:162-255
phrase = Text(self.example_text)
words = break_into_tokens(phrase)
rects = get_piece_rectangles(words, leading_spaces=True, h_buff=0)
rects[-1].set_color(YELLOW)
q_marks = Text("???")
q_marks.next_to(rects[-1], DOWN)

layer = self.get_embedding_array(shape=(10, len(words)), dots_index=None)
vectors = layer.embeddings

blocks = VGroup(*(VGroup(rect, token) for rect, token in zip(rects, words)))
for block, vector in zip(blocks.target, vectors):
    block.scale(word_scale_factor)
    block.next_to(layer, UP, buff=1.5)
    block.match_x(vector)

arrows = VGroup(*(Arrow(block, vect, stroke_width=3)
    for block, vect in zip(blocks.target, vectors)))
```

### Pattern: Arc-Based Attention Animation

**What**: Visualizes attention as curved lines (path_arc=PI/3) connecting embedding positions. Lines are created with random bright colors and stroke widths proportional to random()**5 (simulating attention weights). Animated with simultaneous VShowPassingFlash (traveling pulse) and ShowCreationThenFadeOut (draw then vanish). Multiple rounds create a rich, layered effect.

**When to use**: Attention mechanism visualization, showing information flow between sequence positions, any pairwise interaction pattern in a sequence. The arc shape prevents line overlap and makes individual connections distinguishable.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/network_flow.py:356-385
arc_groups = VGroup()
for _ in range(3):
    for n, e1 in enumerate(layer.embeddings):
        arc_group = VGroup()
        for e2 in layer.embeddings[n + 1:]:
            sign = (-1)**int(e2.get_x() > e1.get_x())
            arc_group.add(Line(
                e1.get_top(), e2.get_top(),
                path_arc=sign * PI / 3,
                stroke_color=random_bright_color(hue_range=(0.1, 0.3)),
                stroke_width=5 * random.random()**5,
            ))
        arc_groups.add(arc_group)

self.play(
    LaggedStart(*(
        AnimationGroup(
            LaggedStartMap(VShowPassingFlash, arc_group.copy(), time_width=2, lag_ratio=0.15),
            LaggedStartMap(ShowCreationThenFadeOut, arc_group, lag_ratio=0.15),
        )
        for arc_group in arc_groups
    ), lag_ratio=0.0),
    LaggedStartMap(RandomizeMatrixEntries, layer.embeddings, lag_ratio=0.0),
    run_time=run_time
)
```

### Pattern: 3D Block Pass-Through with Camera Follow

**What**: Sends an embedding layer "through" a 3D Cube block by: (1) fading the current layer, (2) fading in the block, (3) creating a copy of the layer inside the block (with randomized values), (4) moving the copy out the other side while the camera follows along the Z-axis. Creates the sense of data being transformed by each processing stage.

**When to use**: Showing data flow through transformer layers, pipeline processing stages, any sequential transformation where you want the viewer to feel the data moving through physical stages.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/network_flow.py:263-325
block = self.get_block(layer, title="Attention", depth=depth)
new_layer = layer.copy()
new_layer.match_z(block)

self.play(
    MoveToTarget(self.frame),
    LaggedStart(
        layer.animate.set_opacity(0.25),
        FadeIn(block),
        TransformFromCopy(layer, new_layer),
        lag_ratio=0.3
    ),
    run_time=2
)
# After attention animation, move layer out of block
new_z = block.get_z() + z_diff
self.play(
    block.body[0].animate.set_opacity(block_opacity),
    new_layer.animate.set_z(new_z),
    self.frame.animate.set_z(new_z),
    Restore(layer),
)
```

## Scene Flow

1. **Text input** (0-5s): Sentence appears word by word, tokens highlighted with colored rectangles. Last position marked with "???" as prediction target.
2. **Token labeling** (5-8s): "Tokens" label with arrows pointing to each rectangle.
3. **Embedding** (8-15s): Tokens shrink above, NumericEmbedding vectors fade in below with connecting arrows.
4. **First attention block** (15-25s): 3D cube appears, camera orbits, arc-based attention flashes between positions. Layer passes through block.
5. **First MLP block** (25-35s): MLP cube with neuron dots and weight lines. Layer passes through.
6. **Repeated layers** (35-60s): Multiple attention+MLP passes with camera following along Z-axis.
7. **Unembedding** (60-75s): Final layer focused, probability distribution over next tokens shown.

## manimlib Notes

- `InteractiveScene` with `self.set_floor_plane("xz")` for 3D
- `self.camera.light_source` positioned and updated for consistent 3D lighting
- `random_bright_color(hue_range=...)` from helpers for attention arc colors
- `break_into_tokens()`, `get_piece_rectangles()` from helpers for text tokenization display
- `EmbeddingArray` custom mobject with `.embeddings`, `.dots`, `.brackets` attributes
- `block.sort(lambda p: np.dot(p, [-1, 1, 1]))` for proper 3D face rendering order
