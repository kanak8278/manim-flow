# Knowledge Base Scene Documentation — Authoring Guide

This guide defines how to create scene documentation (.md) files for the
ManimFlow knowledge base. These files are indexed by a multi-field BM25
search engine and returned to the LLM during code generation.

## File Location

All scene docs go in `manimflow/knowledge/scenes/` — flat directory, no subfolders.
Tags handle all organization.

## When to Create One File vs Multiple

| Source file | Scenes | Visual concepts | Action |
|-------------|--------|-----------------|--------|
| <500 lines, 1-3 scenes, 1 concept | 1 | 1 | **1 MD file** |
| 500-2000 lines, 3-10 scenes, 1-2 concepts | 1-2 | 1-2 | **1 MD file** with all patterns |
| 2000+ lines, 10+ scenes, 3+ distinct concepts | 3+ | 3+ | **Split into multiple MDs**, one per visual concept |
| Utility file (colors, helpers, no scenes) | 0 | 0 | **Skip** — no doc needed |

**A "visual concept" is a distinct technique** — not a scene class. Examples:
- "How to visualize attention weights as arrows" = 1 concept
- "How to show token embeddings as colored boxes" = 1 concept
- "How to animate softmax as bar heights" = 1 concept

A 4000-line file with 30 scenes about transformers → 4-5 MDs (one per concept).

## File Naming

Use lowercase, underscores, descriptive:
- `bubble_sort.md` (from bubble-sort.py)
- `linear_regression.md` (from linreg.py)
- `attention_weights.md` (from attention.py, just the weights concept)
- `transformer_token_viz.md` (from embedding.py, token visualization)

## Document Structure

Every MD file follows this exact structure:

```markdown
---
[frontmatter]
---

## Summary
## Design Decisions
## Composition
## Color and Styling
## Timing
## Patterns
## Scene Flow
```

---

### Frontmatter

```yaml
---
source: projects/project-name/path/to/file.py
project: project-name
domain: [term1, term2]           # From vocabulary.py DOMAINS
elements: [term1, term2]         # From vocabulary.py ELEMENTS
animations: [term1, term2]       # From vocabulary.py ANIMATIONS
layouts: [term1, term2]          # From vocabulary.py LAYOUTS
techniques: [term1, term2]       # From vocabulary.py TECHNIQUES
purpose: [term1, term2]          # From vocabulary.py VISUAL_PURPOSE
mobjects: [Circle, VGroup, ...]  # Actual Manim class names used
manim_animations: [FadeIn, ...]  # Actual Manim animation names used
scene_type: Scene                # Scene, ThreeDScene, MovingCameraScene, etc.
manim_version: manim_community   # manim_community or manimlib
complexity: beginner             # beginner, intermediate, advanced
lines: 267                       # Source file line count
scene_classes: [ClassName]       # Scene class names in source
---
```

**Tag rules**:
- Use ONLY terms from `vocabulary.py`. If a term doesn't exist, add it to vocabulary.py first.
- Domain: 3-5 tags. Include both specific (sorting) and general (computer_science).
- Elements: Every distinct visual element type on screen.
- Animations: Every distinct animation type used.
- Layouts: How elements are arranged spatially.
- Techniques: Manim-specific implementation patterns.
- Purpose: What the visualization is trying to communicate.

---

### Summary (2-4 sentences)

**Search weight: 2.0x**

What this file visualizes, the key visual approach, and what makes it effective.
Write in natural language — this is matched by free-text search.

**Good**: "Visualizes bubble sort on a 5-element array using rectangular bar
elements. Swaps use 180-degree arc paths so they look distinct from linear
slides. A text status bar at the bottom narrates each step."

**Bad**: "This is a bubble sort animation." (too brief, no searchable detail)

---

### Design Decisions (5-8 bullet points)

**Search weight: 2.0x**

Each bullet explains WHY a visual choice was made, not just WHAT. This is
critical — the LLM needs to understand rationale to adapt patterns to new
contexts.

Format: `**Choice**: Reason.`

```markdown
- **Horizontal array layout**: Left-to-right matches natural reading order
  and how arrays are taught in textbooks.
- **Arc swap (180 degrees) instead of linear**: Linear swap is invisible —
  elements pass through each other. The arc creates a visible crossing.
- **RED/BLUE overlay system**: RED = active/attention, BLUE = passive/next.
  Semi-transparent (opacity=0.4) so underlying data stays readable.
```

**Good reasons**: "because the viewer needs to...", "this matches how X is
taught...", "without this, the Y would be invisible..."

**Bad reasons**: "because it looks nice", "I prefer this" (no insight)

---

### Composition (exact spatial details)

**Search weight: 1.5x**

Exact positions, sizes, spacing, and buffer values. The LLM needs these to
recreate the layout without overlaps.

Must include:
- **Screen regions**: Where each element group lives (UP/DOWN/LEFT/RIGHT with specific values)
- **Element sizing**: Width, height, scale, font_size values
- **Spacing**: buff values, arrange() parameters, shift amounts
- **Axes config**: x_range, y_range, x_length, y_length (if applicable)

```markdown
- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Array: centered, shifted `LEFT * 2 + DOWN * 1`
  - Status text: `to_edge(DOWN)`, scale=0.8
- **Element sizing**: Rectangle(width=1, height=1), Text scale=0.8
- **Array spacing**: 1 unit between elements (RIGHT)
- **Overlay sizing**: Square(side_length=1), stroke_width=0
```

---

### Color and Styling

**Search weight: 1.5x**

Exact color values, opacity, stroke widths. Use a table format.

Must include:
- Every distinct element's color
- Opacity values
- Stroke widths
- Font sizes and weights
- Text coloring (t2c maps)
- Background color
- A brief explanation of the color strategy (what each color MEANS)

```markdown
| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Data points | BLUE | Input data |
| Prediction line | RED | Model output |
| Error lines | RED | DashedLine, stroke_width=1.5 |
```

---

### Timing

**Search weight: 1.0x**

Exact durations for every animation type. Use a table format.

Must include:
- run_time for each animation type
- wait() durations
- lag_ratio values for staggered animations
- Total video duration estimate

```markdown
| Animation | Duration | Notes |
|-----------|----------|-------|
| Arc swap | run_time=0.75 | Fast but visible |
| Training epoch | run_time=0.1 | 40 epochs = 4s total |
| Total video | ~38 seconds | |
```

---

### Patterns (the core content)

**Search weight: pattern_names 4.0x, when_to_use 3.0x, code 0.5x**

Each pattern is a reusable visual technique with working code.

Format:
```markdown
### Pattern: Descriptive Name Here

**What**: One sentence — what this pattern does. Include enough detail that
the LLM understands the mechanism, not just the effect.

**When to use**: Specific scenarios where this pattern applies. Use concrete
examples. The more specific, the better the search match.

\```python
# Source: projects/project/file.py:LINE_START-LINE_END
[working code snippet — 5-30 lines, not the whole file]
\```
```

**Pattern naming rules**:
- Use descriptive names: "Arc-Based Swap", "ValueTracker + always_redraw for Dynamic Line"
- Not generic: "Animation 1", "Pattern A"
- Include the key Manim technique in the name when possible

**Code snippet rules**:
- Include the Source comment with exact file path and line numbers
- Only the essential code — not setup, not the whole construct() method
- Must be copy-paste usable (include function signatures, imports if unusual)
- Include a critical gotcha note if there's a common mistake (e.g., `lambda i=i:`)

**"When to use" rules**:
- List 2-4 concrete use cases
- Use the vocabulary terms from vocabulary.py where natural
- This field is weighted 3.0x in search — write it carefully

---

### Scene Flow

**Search weight: 1.0x**

Step-by-step narrative of the video. Each step includes:
- **Timestamp** range
- **What appears/happens**
- **Transitions** between steps

```markdown
1. **Setup** (0-3s): Title writes at top. Array of 5 elements appears.
2. **Iteration 1** (3-15s): Overlay slides right, arc-swaps when needed.
3. **Done** (35-38s): Sorted array scales up. Overlays fade out.
```

This helps the LLM understand narrative pacing and structure.

---

## Depth Guidelines

How much detail to write depends on what's interesting about the source:

| What's interesting | Write more about |
|-------------------|-----------------|
| Novel visual technique | Patterns section — detailed code + when_to_use |
| Good color/design system | Color and Styling + Design Decisions |
| Complex layout | Composition section — exact coordinates |
| Interesting timing/pacing | Timing section — all durations |
| Good narrative structure | Scene Flow — detailed step-by-step |
| Reusable helper functions | Add a Reusable Helpers table at the end |

For a simple 80-line file with one obvious pattern: brief doc is fine (Summary + 1-2 patterns + basic composition).

For a rich 400-line file with brand palette + multi-scene narrative: full doc with all sections detailed.

---

## Handling Multi-File Projects

Some projects have shared utilities across files:

- Reducible: `common/classes.py` (custom mobjects) + `common/reducible_colors.py` (palette) + `scenes.py`
- 3B1B transformers: `helpers.py` (shared functions) + `attention.py` + `embedding.py` + `mlp.py`

**Rule: Don't create docs for utility files. Fold their patterns into the scene docs that USE them.**

Example: Reducible's `classes.py` defines Pixel, PixelArray, Module, Node. These appear as
patterns inside `pixel_compression_visualization.md` — the doc that shows how they're used
in actual scenes. The `classes.py` file is referenced via Source comments in code snippets.

Similarly, `helpers.py` functions like `value_to_color()` or `get_piece_rectangles()` appear
as patterns in the scene docs that use them, with the Source comment pointing to helpers.py.

**For shared color palettes**: Include the full palette in the Color and Styling section of
the doc that best represents the project. Reference it from other docs if needed.

---

## Handling manimlib vs manim Community Edition

Some projects use Grant Sanderson's `manimlib` (ManimGL), others use `manim` (Community Edition).
The APIs differ in subtle ways.

**Always note which version in frontmatter**: `manim_version: manimlib` or `manim_version: manim_community`

**Key API differences to document**:

- manimlib uses `ShowCreation`, CE uses `Create`
- manimlib uses `TextMobject`/`TexMobject`, CE uses `Text`/`Tex`/`MathTex`
- manimlib uses `CONFIG` dict, CE uses `__init__` params
- manimlib has `InteractiveScene`, CE does not
- Frame manipulation differs (`self.camera.frame` vs `self.frame`)

When documenting patterns from manimlib code, note any CE-incompatible calls so the LLM
knows to adapt.

---

## Writing Effective "When to use" Descriptions

This field is weighted 3.0x in search — the second most important after tags. The LLM's
natural language query will often match against "When to use" text. Write it carefully.

**Rules**:

1. List 2-4 concrete scenarios, not abstract descriptions
2. Use domain-crossing language — the same pattern works in different fields
3. Include the visual EFFECT, not just the Manim API
4. Avoid words that are common across many docs — be specific

**Good** (from Arc-Based Swap):
> Sorting visualizations, reordering sequences, any pairwise exchange where you need
> the viewer to SEE that a swap happened.

Why it works: "sorting", "reordering", "pairwise exchange", "swap" — all specific, all
searchable, and "where you need the viewer to SEE" explains the WHY.

**Good** (from Dual-Track Algorithm Visualization):
> BFS (tree + queue), DFS (tree + stack), Dijkstra (graph + priority queue), any algorithm
> where an auxiliary data structure drives the traversal.

Why it works: Lists specific algorithms by name. Someone searching "BFS queue" or "Dijkstra
priority queue" will match directly.

**Bad**:
> Use this when you want to show something moving.

Why it fails: Matches everything. "Moving" appears in every animation doc.

**Disambiguation tip**: If your pattern uses common words (like "flow", "path", "color"),
add domain-specific qualifiers. Instead of "flow animation", write "information flow in
neural networks" or "fluid flow in vector fields." This prevents cross-domain confusion
in search results.

---

## Code Snippet Depth Guide

How many lines to include depends on the pattern's complexity:

| Pattern type | Lines | Example |
| ------------ | ----- | ------- |
| Simple factory function | 5-10 | createRectangleNode(), create_pipeline_box() |
| Animation technique | 8-15 | playArcSwap(), ContextAnimation usage |
| Setup + animate combo | 15-25 | ValueTracker + always_redraw + loop |
| Custom Mobject class | 15-30 | Pixel, PixelArray, WeightMatrix |
| Full scene structure | 20-30 | Multi-scene-in-one-class construct() |

**Include enough context to be copy-paste usable**. A function call without the function
definition is useless. A class usage without showing the constructor is confusing.

**Don't include**: Import statements (unless unusual), full construct() methods, repetitive
loop bodies, comments that just restate the code.

**Do include**: Function signatures, key parameters with their values, the critical
gotcha note if there's a common mistake.

---

## Reference Examples

These existing scene docs demonstrate the format at different complexity levels:

| Doc | Complexity | Demonstrates |
| --- | ---------- | ------------ |
| `bubble_sort.md` | Beginner | Simple single-scene, helper functions, clear step-by-step flow |
| `linear_regression.md` | Intermediate | Algorithm+Scene separation, ValueTracker pattern, lambda gotcha |
| `deepseek_r1.md` | Intermediate | Multi-scene narrative, brand palette, pipeline diagrams |
| `kmeans_clustering.md` | Intermediate | Iterative replay, color-based classification, clean composition |
| `bfs_tree_traversal.md` | Intermediate | Dual-track visualization, three-state color machine, queue pattern |
| `attention_qkv_matrices.md` | Advanced | 3D projection, grid-based attention, cross-attention, split from 4K-line file |
| `token_embedding_visualization.md` | Advanced | Text tokenization, embedding vectors, matrix lookup, custom mobjects |
| `pixel_compression_visualization.md` | Advanced | Custom Pixel/PixelArray classes, branded palette, multi-file project |
| `vector_field_visualization.md` | Advanced | Color-mapped field grid, normal vectors, side-by-side comparison |

Read these before creating new docs to calibrate depth and style.

---

## Quality Checklist

Before committing a scene doc:

- [ ] All frontmatter tags use terms from vocabulary.py
- [ ] Summary is 2-4 sentences with searchable detail
- [ ] Design Decisions explain WHY, not just WHAT
- [ ] Composition has exact position values (not "somewhere on the left")
- [ ] Color table has every distinct element
- [ ] Timing table has run_time for every animation type
- [ ] Every pattern has Source comment with file:line
- [ ] Every pattern "When to use" is specific and domain-qualified (see guide above)
- [ ] Code snippets are copy-paste usable (see depth guide above)
- [ ] Scene Flow has timestamps and transitions
- [ ] manim_version noted correctly (manimlib vs manim_community)
- [ ] Multi-file project utilities folded into scene docs (not separate docs)
