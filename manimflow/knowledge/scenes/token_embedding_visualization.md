---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/_2024/transformers/embedding.py
project: manim-interactive
domain: [machine_learning, deep_learning, nlp, transformers]
elements: [label, box, rounded_box, vector, matrix, arrow, dot, code_block, token]
animations: [fade_in, write, lagged_start, grow, transform, stagger, color_change]
layouts: [horizontal_row, vertical_stack, flow_top_down, centered]
techniques: [custom_mobject, color_gradient, data_driven, progressive_disclosure, factory_pattern]
purpose: [decomposition, transformation, demonstration, step_by_step, definition]
mobjects: [Text, VGroup, Rectangle, SurroundingRectangle, NumericEmbedding, WeightMatrix, EmbeddingArray, Arrow]
manim_animations: [FadeIn, LaggedStartMap, GrowFromCenter, Write, TransformFromCopy, ShowCreation]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 3042
scene_classes: [LyingAboutTokens2, IntroduceEmbeddingMatrix, TokenEmbeddingBreakdown]
---

## Summary

Visualizes how text is converted into numerical vectors for transformer processing. Shows tokenization (splitting text into tokens/words with colored rectangles), embedding lookup (each token maps to a column in the embedding matrix), and the resulting vector representations (NumericEmbedding objects with color-mapped values). Uses tiktoken for real GPT tokenization. This is a foundational pattern for any NLP visualization — it solves the problem of "how do I show text becoming numbers."

## Design Decisions

- **Colored rectangles behind each token**: Using get_piece_rectangles() with random hue_range colors. Each token gets a visually distinct rectangle so the viewer can track individual tokens through transformations. The colors are random within a range (orange for tokens: hue 0.1-0.2, cyan for words: hue 0.5-0.6) — distinct enough to track, cohesive enough to feel unified.
- **NumericEmbedding as vertical column vectors**: Each embedding is a vertical column of numbers with value-to-color mapping (positive=blue, negative=red). This matches the mathematical convention (column vectors) and makes the high-dimensionality tangible — "look, each word becomes 768 numbers."
- **Real tiktoken tokenization**: Uses `tiktoken.encoding_for_model("davinci")` to show actual GPT tokens, not made-up ones. This grounds the visualization in reality — "BPE tokenization sometimes splits words unexpectedly."
- **Embedding matrix with column selection**: The full embedding matrix is shown with one column highlighted at a time. An arrow traces from the token to its column. This explicitly shows "embedding = table lookup" — simpler than the common misconception of "embedding = learned transformation."
- **Image-to-vector baking**: A visual image of a word's meaning gets "baked into" vector entries via FadeOutToPoint animations. Each pixel of the image flies to a random entry position. This creates the metaphor "the vector CONTAINS the meaning" without needing to explain high-dimensional spaces.

## Composition

- **Token display**:
  - Text phrase at 2*UP, centered
  - Colored rectangles: h_buff=0.05, v_buff=0.1, fill_opacity=0.15, stroke_width=1
  - Tokens arranged inline (natural text flow)
- **Embedding vectors**:
  - Arranged RIGHT with buff = 1.0 × vector width
  - Set total width = 12 units
  - Positioned: to_edge(DOWN, buff=1.0), to_edge(LEFT, buff=0.5)
  - Arrow from each token down to its vector
- **Embedding matrix**:
  - WeightMatrix(shape=(10, n_tokens))
  - Width: 13.5 units, centered
  - Column labels: word text rotated -45 degrees, positioned above
  - Column highlight: SurroundingRectangle with buff=0.05
  - Other columns dimmed to opacity=0.2 when one is selected

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Token rectangles (BPE) | Random hue 0.1-0.2 | Orange/warm tones, fill_opacity=0.15 |
| Word rectangles | Random hue 0.5-0.6 | Cyan/cool tones, fill_opacity=0.15 |
| Embedding positive vals | BLUE_E → BLUE_B | Gradient by magnitude |
| Embedding negative vals | RED_E → RED_B | Gradient by magnitude |
| Embedding brackets | GREY_B | backstroke_width=3 |
| Matrix entries | Same blue/red gradient | value_to_color() mapping |
| Column highlight | WHITE | SurroundingRectangle, stroke_width=1 |
| Inactive columns | opacity=0.2 | Dimmed when not selected |
| Text | WHITE | Default, backstroke(BLACK, 5) for visibility |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Token rectangle reveal | LaggedStartMap, lag_ratio=0.1 | ~1.5s for full phrase |
| Embedding vector appear | FadeIn, shift=0.5*DOWN | With LaggedStartMap |
| Arrow growth | GrowFromCenter | One per token |
| Column selection sweep | ~0.5s per column | Sequential MoveToTarget |
| Image baking into vector | run_time=2-4 | FadeOutToPoint per pixel |
| Matrix RandomizeEntries | run_time=3 | Visual "computing" effect |

## Patterns

### Pattern: Text Tokenization with Colored Rectangles

**What**: Split a text phrase into tokens or words, then overlay each piece with a colored semi-transparent rectangle. Uses tiktoken for BPE tokenization or regex for word splitting. Each rectangle has a random color within a hue range — warm tones for tokens, cool tones for words. The rectangles make individual tokens trackable through later transformations.
**When to use**: Any NLP visualization, text processing, tokenization explainer, or anytime you need to show "this text is made of these pieces." Also works for syntax highlighting, parse trees, or named entity recognition.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/embedding.py
# Break text into pieces
phrase = Text("The goal of our model is to predict the next word")
words = break_into_words(phrase)  # or break_into_tokens(phrase)

# Create colored rectangles
rects = get_piece_rectangles(
    words,
    h_buff=0.05,
    v_buff=0.1,
    fill_opacity=0.15,
    stroke_width=1,
    hue_range=(0.5, 0.6),  # cyan for words, (0.1, 0.2) for tokens
)
self.add(rects, words)
self.play(LaggedStartMap(FadeIn, rects))
```

### Pattern: Embedding Vector Columns

**What**: Show each word/token as a vertical column of numbers with color-mapped values. NumericEmbedding creates a column vector where positive values are blue and negative are red. Vectors are arranged horizontally below the text, with arrows connecting each token to its vector. The vector width and spacing create a clear "one vector per token" visual.
**When to use**: Word embeddings, feature vectors, any "text to numbers" visualization. Also works for audio features, sensor readings, or any per-item feature vector display.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/embedding.py
# Create vectors
vectors = VGroup(*(NumericEmbedding(length=8) for _ in words))
vectors.arrange(RIGHT, buff=1.0 * vectors[0].get_width())
vectors.set_width(12)
vectors.to_edge(DOWN, buff=1.0).to_edge(LEFT, buff=0.5)

# Arrows from words to vectors
arrows = VGroup(*(Arrow(word, vec) for word, vec in zip(words, vectors)))
self.play(
    LaggedStartMap(FadeIn, vectors, shift=0.5 * DOWN),
    LaggedStartMap(GrowFromCenter, arrows)
)
```

### Pattern: Embedding Matrix Column Lookup

**What**: Show the embedding matrix as a WeightMatrix, then highlight one column at a time to show that "embedding a token = looking up a column." Other columns dim to opacity=0.2 while the selected column stays at full opacity. Column labels (word text) are rotated -45 degrees above the matrix.
**When to use**: Embedding table lookup, dictionary/codebook visualization, any "index selects a column/row" operation.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/embedding.py
# Create matrix
matrix = WeightMatrix(shape=(10, len(words)), ellipses_col=dots_index)
matrix.set_width(13.5)
matrix.center()
columns = matrix.get_columns()

# Highlight one column at a time
for index in range(len(columns)):
    columns.target = columns.generate_target()
    columns.target.set_opacity(0.2)
    columns.target[index].set_opacity(1)
    rect = SurroundingRectangle(columns[index], buff=0.05)
    self.play(MoveToTarget(columns), FadeIn(rect))
```

### Pattern: Bake Image Into Vector Entries

**What**: A visual metaphor where an image (representing word meaning) gets "absorbed" into a vector's entries. Each part of the image flies to a random entry position via FadeOutToPoint, while vector entries simultaneously randomize. Creates the impression that "the vector stores the meaning." Uses path_arc=30 degrees for natural curves.
**When to use**: Explaining what embeddings represent, showing how meaning is encoded in numbers, any "abstract concept becomes data" visualization.

```python
# Source: projects/manim-interactive/projects/_2024/transformers/attention.py
# Bake image into vector entries
def bake_mobject_into_vector_entries(scene, source_mob, vector, run_time=3):
    copies = VGroup(*(source_mob.copy() for _ in vector.get_entries()))
    scene.play(
        *(FadeOutToPoint(copy, entry.get_center(), path_arc=30 * DEGREES)
          for copy, entry in zip(copies, vector.get_entries())),
        RandomizeMatrixEntries(vector),
        run_time=run_time
    )
```

## Scene Flow

1. **Show text** (0-3s): Full phrase appears. Then token/word boundaries become visible as colored rectangles fade in one by one.
2. **Reveal tokenization** (3-8s): If using BPE, show that some words get split unexpectedly ("playing" → "play" + "ing"). Rectangles make the splits visible.
3. **Create vectors** (8-15s): NumericEmbedding columns appear below each token. Arrows connect token → vector. The viewer sees "each token becomes a column of numbers."
4. **Show embedding matrix** (15-25s): Full matrix appears. Sweep through columns one by one, highlighting each token's column. Shows that embedding is a table lookup.
5. **Semantic meaning** (25-35s): Optional — bake images into vectors to show what the numbers "mean."

> Full file: `projects/manim-interactive/projects/_2024/transformers/embedding.py` (3042 lines)
