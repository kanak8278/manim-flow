---
source: https://github.com/nipunramk/Reducible/blob/main/2022/common/classes.py
project: Reducible
domain: [computer_science, image_processing, compression, information_theory, algorithms]
elements: [pixel, pixel_grid, bar_chart, box, label, node, arrow, code_block]
animations: [fade_in, fade_out, transform, lagged_start, grow, write, update_value]
layouts: [grid, side_by_side, flow_left_right, centered, hierarchy]
techniques: [custom_mobject, factory_pattern, brand_palette, data_driven, zoomed_scene, progressive_disclosure]
purpose: [decomposition, comparison, before_after, process, demonstration, step_by_step]
mobjects: [Square, Rectangle, RoundedRectangle, VGroup, Text, DecimalNumber, BarChart, Circle, ImageMobject]
manim_animations: [FadeIn, FadeOut, Transform, TransformFromCopy, LaggedStartMap, Write, UpdateFromAlphaFunc]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 487
scene_classes: [IntroduceRGBAndJPEG, JPEGDiagramScene, IntroPNG]
---

## Summary

Reducible's custom mobject library for pixel-level image compression visualization. Contains 14 reusable classes: Pixel (color-mapped square), PixelArray (numpy array → visual grid with 2D indexing), Byte (data container), Module (process box), Node (tree structures for Huffman coding), RCircularNode (graph nodes), ReducibleBarChart (branded charts), RVariable (live-updating value display). Used across JPEG, PNG, and QOI compression explainer videos. The Pixel/PixelArray system is the standout — it converts numpy image arrays directly into animated grids.

## Design Decisions

- **Pixel as Square subclass**: Each pixel is a colored Square. Color computed from numpy value via rgb_to_hex() or grayscale g2h(). Outline can be BLACK stroke or color-matched. This means you can animate individual pixel color changes, highlights, and transformations — something ImageMobject can't do.
- **PixelArray with 2D indexing**: Supports array[i, j] syntax by mapping to internal 1D VGroup index (i * width + j). This means you can write `pixel_array[3, 5]` to get a specific pixel — natural for anyone who works with numpy arrays.
- **Module as RoundedRectangle + Text**: Process boxes for flow diagrams (Encoder, Decoder, DCT, Quantizer). Standardized sizing with configurable text. Creates consistent pipeline diagrams across all Reducible videos.
- **Branded color palette**: 15 custom colors (REDUCIBLE_PURPLE, REDUCIBLE_YELLOW, etc.) with darker variants for fill. Purple for structural elements, yellow for highlights, green for success. Creates instant brand recognition.
- **SF Mono font for data**: All numbers, bytes, and technical data use "SF Mono" (monospace) at MEDIUM weight. Labels and titles use "CMU Serif" at BOLD. The monospace ensures grid alignment for pixel value overlays.
- **ZoomedScene for pixel inspection**: IntroPNG uses ZoomedScene to show a magnified view of individual pixels while keeping the full image visible. This "zoom into the data" technique is essential for compression explainers.

## Composition

- **Pixel sizing**: Default Square (1x1 units), scaled down for grids. Pixel arrays typically scaled to 0.3-0.5 of frame width.
- **PixelArray from numpy**:
  - Input: numpy array shape (height, width, 3) for RGB or (height, width) for grayscale
  - Grid layout automatic from array dimensions
  - Optional number overlay on each pixel
- **Module boxes**: RoundedRectangle, customizable width/height, centered text
- **Flow diagrams**: Modules arranged with arrange(RIGHT, buff=0.5), arrows between them
- **Bar charts**: ReducibleBarChart extends BarChart with "SF Mono" font and custom styling
- **Zoom display**: Camera zoom frame + inset display, connected by visual bridge

## Color and Styling

| Element | Color | Hex | Role |
| ------- | ----- | --- | ---- |
| Brand primary | REDUCIBLE_PURPLE | #8c4dfb | Structural elements, borders |
| Brand light | REDUCIBLE_VIOLET | #d7b5fe | Lighter accents, fills |
| Brand dark fill | PURPLE_DARK_FILL | #331B5D | Dark backgrounds for boxes |
| Highlight | REDUCIBLE_YELLOW | #ffff5c | Emphasis, selection |
| Success | REDUCIBLE_GREEN | #008f4f | Correct, efficient |
| Warning | REDUCIBLE_CHARM | #FF5752 | Error, inefficient |
| Secondary | REDUCIBLE_WARM_BLUE | #08B6CE | Technical flow |
| Orange accent | REDUCIBLE_ORANGE | #FFB413 | Special emphasis |
| Pixel outlines | BLACK or color-matched | — | Configurable per Pixel |
| Data text font | SF Mono, MEDIUM | — | Monospace for alignment |
| Label font | CMU Serif, BOLD | — | Titles and labels |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Pixel grid creation | ~2s | From numpy array |
| Individual pixel highlight | ~0.5s | Color change or SurroundingRectangle |
| Module flow diagram build | LaggedStartMap, lag_ratio=0.3 | Sequential box appearance |
| Bar chart growth | UpdateFromAlphaFunc | Custom animated fill |
| Zoom activation | ~1.5s | Camera zoom frame appears |
| Transform pixel to pixel | ~1s | Color/value change |

## Patterns

### Pattern: Numpy Array to Pixel Grid

**What**: Convert a numpy image array directly into an animated grid of colored squares. Each pixel is a separate Manim Square mobject, so individual pixels can be highlighted, color-changed, or annotated. Supports both RGB (height, width, 3) and grayscale (height, width) arrays. Optional number overlay shows pixel values.
**When to use**: Image processing visualization, compression algorithms, convolution demonstrations, any pixel-level data display. Also works for heatmaps, cellular automata, or grid-based simulations.

```python
# Source: projects/Reducible/2022/common/classes.py (Pixel + PixelArray)
class Pixel(Square):
    def __init__(self, value, color_mode="RGB", outline=True):
        color = rgb_to_hex(value) if color_mode == "RGB" else g2h(value)
        super().__init__(side_length=1, fill_color=color, fill_opacity=1,
                         stroke_color=BLACK if outline else color, stroke_width=1)

class PixelArray(VGroup):
    def __init__(self, image_array, include_numbers=False, color_mode="RGB"):
        pixels = []
        h, w = image_array.shape[:2]
        for i in range(h):
            for j in range(w):
                pixel = Pixel(image_array[i][j], color_mode)
                pixels.append(pixel)
        super().__init__(*pixels)
        self.arrange_in_grid(rows=h, cols=w, buff=0)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            i, j = key
            return super().__getitem__(i * self.width + j)
        return super().__getitem__(key)

# Usage
image = ImageMobject("photo.png")
array = image.get_pixel_array().astype(int)
pixel_mob = PixelArray(array).scale(0.4).shift(UP * 2)
self.play(FadeIn(pixel_mob))

# Highlight specific pixel
self.play(pixel_mob[3, 5].animate.set_stroke(YELLOW, 3))
```

### Pattern: Process Module Box

**What**: A RoundedRectangle with centered text, used as a building block for flow/pipeline diagrams. Standardized sizing ensures all modules in a pipeline look consistent. Can contain single text or a list of items arranged vertically.
**When to use**: Data processing pipelines, encoder/decoder diagrams, system architecture, any multi-step process visualization. Similar to deepseek_r1's pipeline_box but with rounded corners and brand styling.

```python
# Source: projects/Reducible/2022/common/classes.py (Module)
class Module(VGroup):
    def __init__(self, text, width=3, height=1.5, text_weight=NORMAL):
        rect = RoundedRectangle(
            width=width, height=height, corner_radius=0.1,
            fill_color=REDUCIBLE_PURPLE_DARK_FILL, fill_opacity=1,
            stroke_color=REDUCIBLE_VIOLET, stroke_width=2
        )
        label = Text(text, font="CMU Serif", weight=text_weight).scale_to_fit_width(width * 0.8)
        label.move_to(rect)
        super().__init__(rect, label)

# Pipeline usage
encoder = Module("Encoder", width=2.5)
transform = Module("DCT", width=2.0)
quantizer = Module("Quantize", width=2.5)
pipeline = VGroup(encoder, transform, quantizer).arrange(RIGHT, buff=0.5)
arrows = VGroup(*(Arrow(a.get_right(), b.get_left(), buff=0.1) for a, b in zip(pipeline, pipeline[1:])))
```

### Pattern: Live-Updating Variable Display

**What**: A label-value pair that updates in real-time via ValueTracker. Shows as "label = value" with automatic decimal formatting. The value tracks a ValueTracker and redraws each frame. Uses monospace font for alignment.
**When to use**: Counters during algorithms, parameter tracking, compression ratio display, any numeric value that changes during animation.

```python
# Source: projects/Reducible/2022/common/classes.py (RVariable)
class RVariable(VMobject):
    def __init__(self, label, tracker, num_decimal_places=2):
        self.tracker = tracker
        self.label = Text(label, font="SF Mono")
        self.value = RDecimalNumber(tracker.get_value(), num_decimal_places=num_decimal_places)
        self.equals = Text("=", font="SF Mono")
        group = VGroup(self.label, self.equals, self.value).arrange(RIGHT, buff=0.2)
        # Value auto-updates via tracker

# Usage
ratio_tracker = ValueTracker(1.0)
ratio_display = RVariable("Compression", ratio_tracker, num_decimal_places=1)
self.play(ratio_tracker.animate.set_value(3.5), run_time=2)
```

### Pattern: Huffman Tree Node

**What**: Tree nodes for Huffman coding visualization. Leaf nodes show character + frequency as two stacked rectangles. Internal nodes show just the combined frequency in a circle. The generate_mob() method creates the appropriate visual based on node type and tree depth. Edges connect parent to children.
**When to use**: Huffman coding, binary tree construction, priority queue visualization, any tree where leaf and internal nodes look different.

```python
# Source: projects/Reducible/2022/common/classes.py (Node)
class Node:
    def __init__(self, freq, key=None, left=None, right=None):
        self.freq = freq
        self.key = key
        self.left = left
        self.right = right

    def generate_mob(self, scale=1.0):
        if self.key:  # Leaf node
            freq_box = Rectangle(width=0.8, height=0.5, fill_color=REDUCIBLE_PURPLE)
            key_box = Rectangle(width=0.8, height=0.5, fill_color=REDUCIBLE_GREEN)
            return VGroup(freq_box, key_box).arrange(DOWN, buff=0)
        else:  # Internal node
            return Circle(radius=0.3, fill_color=REDUCIBLE_WARM_BLUE, fill_opacity=1)
```

## Scene Flow

1. **Introduce pixels** (0-10s): Show a real image, zoom into pixel grid, reveal individual pixel values. PixelArray makes each pixel a separate object.
2. **RGB channels** (10-20s): Extract R, G, B channels as separate PixelArrays. Show each as a grayscale grid. Demonstrates that images are 3 layers of numbers.
3. **Compression pipeline** (20-40s): Module boxes arranged left-to-right: Input → Encoder → DCT → Quantize → Entropy Code → Output. Arrows connect them. Data flows through with animations showing transformation at each step.
4. **Algorithm detail** (40-60s): Zoom into one step. Show pixel values changing. Show compression ratio updating via RVariable.
5. **Comparison** (60-75s): ReducibleBarChart comparing formats (JPEG vs PNG vs QOI) on file size, quality, speed.

> Full file: `projects/Reducible/2022/common/classes.py` (487 lines) + scenes in JPEG/PNG/QOI directories
