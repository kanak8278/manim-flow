---
source: https://github.com/vivek3141/videos/blob/main/rs_codes.py
project: vivek3141_videos
domain: [mathematics, error_correction, number_theory, algorithms, computer_science]
elements: [grid, label, equation, surrounding_rect, circle, dot, formula]
animations: [write, transform, fade_in, fade_out, indicate, grow]
layouts: [centered, horizontal_row, vertical_stack]
techniques: [custom_mobject, progressive_disclosure, color_gradient]
purpose: [step_by_step, demonstration, definition, exploration]
mobjects: [Square, Rectangle, VGroup, Tex, TexText, Text, Circle, SurroundingRectangle, Brace, ImageMobject, BackgroundRectangle]
manim_animations: [Write, Transform, TransformMatchingTex, TransformFromCopy, FadeIn, FadeOut, ShowCreation, Uncreate, ReplacementTransform, GrowFromCenter, Indicate, ApplyMethod]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 1473
scene_classes: [NumberSquare, LabelledNumberSquare, PartScene, PartOne, PartTwo, PartThree, TitleScene, RS, RSAppl, ModularIntro]
---

## Summary

Visualizes Reed-Solomon error correction codes by building up from modular arithmetic, through Lagrange interpolation, to the full encoding scheme. The key visual element is NumberSquare -- a colored Square with a centered number, representing data and parity symbols. Modular arithmetic is taught using a circular number layout (5 numbers on a circle) with animated pointer (SurroundingRectangle) that traverses the circle to show addition/subtraction mod 5. The encoding is shown as appending redundancy squares to data squares, with Brace annotations showing k=2 parity symbols.

## Design Decisions

- **NumberSquare custom mobject**: Square with fill color at 0.5 opacity, centered Tex number. Color encodes the value. This visual maps directly to how error correction works -- each symbol is a colored block with a number.
- **Circular modular arithmetic**: Numbers 0-4 arranged on a Circle (radius 1.5), with SurroundingRectangle (yellow #f5fd62) highlighting the current position. Pointer traverses the circle for addition/subtraction operations. This is more intuitive than a number line for modular arithmetic.
- **Consistent pastel palette**: Uses the same palette as mandelbrot.py (A_AQUA, A_YELLOW, A_LAVENDER, etc.). Color assignments: numbers=A_ORANGE, modulus=A_AQUA, generic variables=A_PINK, results=A_GREEN.
- **Brace for parity annotation**: Brace under the last k=2 squares with label "k = 2", showing how many parity symbols are added.
- **Three-part structure**: Part 1 (Modular Arithmetic), Part 2 (Lagrange Interpolation), Part 3 (Putting it all together). Each with colored PartScene title card.

## Composition

- **NumberSquare grid**: 4-6 squares in a row, side_length=1 to 1.5, spaced at 1.5 or 2 unit intervals, centered horizontally
- **Circular number layout**: Circle radius=2, at 4*RIGHT + 0.5*DOWN, numbers at equal angular intervals from PI/2
- **Equations**: scale=1.5-2.5, positioned above or below the visual elements
- **Brace + label**: Below the NumberSquare row, label includes colored k and value
- **SurroundingRectangle**: color="#f5fd62", buff=0.15, follows pointer position
- **Images**: QR code, barcode, CD at 3*LEFT, 3*RIGHT, 2*DOWN respectively, each scaled 0.5-0.75

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Number squares (by value) | Shades of red | ["#fc998e", "#fb8d80", "#fb8072", "#e27367", "#c9665b"] |
| Numbers (generic) | A_ORANGE (#fdb462) | In tex_to_color_map |
| Modulus p | A_AQUA (#8dd3c7) | In tex_to_color_map |
| Generic variable a | A_PINK (#fccde5) | In tex_to_color_map |
| Result/inverse | A_GREEN (#b3de69) | In tex_to_color_map |
| Parity label k | A_YELLOW (#ffffb3) / A_ORANGE | In tex_to_color_map |
| Pointer rectangle | #f5fd62 | SurroundingRectangle |
| Part 1 title | A_RED (#fb8072) | Modular Arithmetic |
| Part 2 title | A_YELLOW (#ffffb3) | Lagrange Interpolation |
| Part 3 title | A_ORANGE (#fdb462) | Putting it all together |
| Title scene bg | #5b6190 / GREY | TitleScene CONFIG |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| NumberSquare write | ~1s | Write(s) for row |
| Pointer traversal | ~0.5s per step | Transform(b1, b_rects[i]) |
| Equation transform | ~1s | TransformMatchingTex |
| Indicate | ~1s | scale_factor=1.5 |
| GrowFromCenter (Brace) | ~1s | Brace appears |
| Total | ~5+ minutes | Many scenes, first 500 lines cover modular arithmetic |

## Patterns

### Pattern: NumberSquare Custom Mobject

**What**: A VGroup containing a colored Square and a centered Tex number. The square's fill color and opacity are configurable. Parameters control side_length, num_scale, and square/tex kwargs. Rows of NumberSquares represent data symbols in error correction codes. Color encodes the symbol value.

**When to use**: Error correction codes (Reed-Solomon, Hamming), data packet visualization, memory layout diagrams, any scenario where you need colored blocks with numbers -- encoding schemes, cipher visualizations, array element highlighting.

```python
# Source: projects/vivek3141_videos/rs_codes.py:19-28
class NumberSquare(VGroup):
    def __init__(self, number, color=RED, opacity=0.5,
                 num_scale=3, side_length=2,
                 square_kwargs={}, tex_kwargs={}, *args, **kwargs):
        VGroup.__init__(self, *args, **kwargs)
        self.sq = Square(side_length=side_length, fill_color=color,
                         fill_opacity=opacity, **square_kwargs)
        self.num = Tex(str(number), **tex_kwargs)
        self.num.scale(num_scale)
        self.add(self.sq, self.num)
```

### Pattern: Circular Modular Arithmetic with Animated Pointer

**What**: Numbers 0 to p-1 arranged on a Circle using trigonometric positioning. A SurroundingRectangle highlights the "current" number and traverses the circle via Transform to demonstrate modular addition/subtraction. The circle layout makes wrapping around intuitive -- after 4 comes 0.

**When to use**: Modular arithmetic, clock arithmetic, cyclic groups, hash function visualization, circular buffer concepts, any wrap-around numerical system.

```python
# Source: projects/vivek3141_videos/rs_codes.py:292-348
c = Circle(radius=2, stroke_color=A_GREY)
c_nums = VGroup()
for i, t in enumerate(np.linspace(PI/2, PI/2 - 2*PI, 6)[:-1]):
    x, y = 1.5 * np.cos(t), 1.5 * np.sin(t)
    t = Tex(str(i), color=A_ORANGE).scale(1.5)
    t.move_to(c.get_center()).shift(x * RIGHT + y * UP)
    c_nums.add(t)

b_rects = VGroup()
for num in c_nums:
    b = SurroundingRectangle(num, color="#f5fd62", buff=0.15)
    b_rects.add(b)

# Animate: start at 4, move to 4+3=2 (mod 5)
b1 = SurroundingRectangle(eq3[0], color="#f5fd62", buff=0.15)
self.play(Write(b1))
for i in range(4, 8):
    self.play(Transform(b1, b_rects[i % 5]))
    self.wait(0.5)
```

### Pattern: Data + Parity Row with Brace Annotation

**What**: A row of NumberSquares split into data symbols and parity symbols. The parity section is annotated with a Brace below, labeled "k = 2" (number of parity symbols). BackgroundRectangles highlight individual squares that are corrupted or unknown ("?"). This layout is the standard way to show error correction encoding.

**When to use**: Reed-Solomon codes, Hamming codes, parity check matrices, any forward error correction visualization, data redundancy demonstrations.

```python
# Source: projects/vivek3141_videos/rs_codes.py:122-177
numbers = [2, 4, 3, 1, "?", "?"]
shades = ["#fc998e", "#fb8d80", "#fb8072", "#e27367", "#c9665b"]

s2 = VGroup()
for i in range(6):
    s_i = NumberSquare(numbers[i], shades[c[i]],
                       side_length=1, num_scale=1.5)
    s2.add(s_i.shift(1.5*i * RIGHT))
s2.center()

b1 = Brace(s2[-2:])
t1 = b1.get_tex("k = 2", tex_to_color_map={
    "k": A_YELLOW, "2": A_ORANGE})
t1.scale(1.5).shift(0.25 * DOWN)

self.play(GrowFromCenter(b1), Write(t1))

# Highlight corrupted symbols
r1 = BackgroundRectangle(s2[2], buff=0.15)
r2 = BackgroundRectangle(s2[-1], buff=0.15)
self.play(ShowCreation(r1), ShowCreation(r2))
```

## Scene Flow

1. **RS** (0-15s): Row of 4 NumberSquares (data: 2,4,3,1). Highlight corrupted square. Extend to 6 squares with "?" for parity. Brace labels k=2. Highlight two corrupted positions.
2. **RSAppl** (15-20s): Reed-Solomon applications: QR code, barcode, CD images.
3. **Part 1: Modular Arithmetic** (20-60s): Title card. Set {0,1,2,3,4}. Congruence definition with Brace labels. Circular number layout. Animated pointer demonstrates 4+3=2 (mod 5), 1-3=3 (mod 5). Additive inverse. Multiplicative inverse (2*3=1 mod 5). Traversal animation on circle.
4. **Part 2: Lagrange Interpolation** (documented in full file, beyond first 500 lines).
5. **Part 3: Putting it all together** (documented in full file, beyond first 500 lines).

> Full file: `projects/vivek3141_videos/rs_codes.py` (1473 lines, first 500 documented)
