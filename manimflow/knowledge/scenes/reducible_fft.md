---
source: https://github.com/nipunramk/Reducible/blob/main/2020/FFT/fft.py
project: Reducible
domain: [computer_science, algorithms, signal_processing, mathematics, complexity]
elements: [graph, node, circle_node, axes, function_plot, formula, equation, label, line, dot, surrounding_rect, code_block]
animations: [fade_in, fade_out, write, draw, transform, replacement_transform, transform_from_copy, highlight, indicate, lagged_start, one_by_one]
layouts: [centered, grid, side_by_side, flow_left_right, vertical_stack, hierarchy]
techniques: [custom_mobject, progressive_disclosure, algorithm_class_separation, data_driven]
purpose: [step_by_step, demonstration, derivation, decomposition, comparison, process]
mobjects: [Circle, Line, Dot, VGroup, TextMobject, TexMobject, Arrow, SurroundingRectangle, GraphScene]
manim_animations: [FadeIn, FadeOut, ShowCreation, Write, Transform, TransformFromCopy, MoveAlongPath, LaggedStartMap, ShowCreationThenDestruction]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 6524
scene_classes: [GraphNode, GraphAnimationUtils, Introduction, FFTIntroApps, FFTGraph, FFTComplexity, TimeToFreq, MultiplyPolynomials, Representation, ValueRepresentationMult, FocusOnInverse, Evaluation, BigPictureEval, IntroduceRootsOfUnity, WhyRootsOfUnity, FFTImplementationP1, FFTImplementationExample, Interpolation, ShowInverseFFT, Conclusion]
---

## Summary

Comprehensive Fast Fourier Transform visualization split across polynomial multiplication (coefficient vs value representation, evaluation at roots of unity) and the divide-and-conquer FFT algorithm. Features a butterfly-network graph visualization (8x4 grid of interconnected nodes), time-to-frequency domain transformation with real WAV file data, step-by-step polynomial algebra with TransformFromCopy between terms, and a hierarchical FFT implementation diagram with color-coded stages. This is the largest Reducible file at 6524 lines.

## Design Decisions

- **Polynomial multiplication as motivation**: FFT introduced through the lens of speeding up polynomial multiplication from O(n^2) to O(n log n). Coefficient representation vs value representation explained before any Fourier theory.
- **FFT butterfly graph**: 32-node graph (8 rows x 4 columns) with cross-connections matching FFT butterfly pattern. Edges colored by stage: BLUE, GREEN_SCREEN, MONOKAI_GREEN for different recursion levels.
- **Real audio data**: WAV file read with scipy.io.wavfile, plotted as time domain signal, then FFT applied to show frequency domain. Concrete, tangible demonstration.
- **Recursive diagram with colored stages**: Input (YELLOW box), base case (BLUE), even/odd recursive calls (YELLOW), combine step (ORANGE), output (GREEN_SCREEN). Each stage gets its own SurroundingRectangle.
- **Code-style pseudocode**: TextMobject with Monokai syntax coloring (MONOKAI_BLUE for keywords, MONOKAI_GREEN for function names, MONOKAI_ORANGE for parameters, MONOKAI_GRAY for comments).
- **GraphScene for plotting**: Uses manimlib's GraphScene for polynomial graphs, axes setup, and point plotting.

## Composition

- **FFT butterfly graph**: 8 rows x 4 columns, row_positions UP*3.5 to DOWN*3.5, column_positions LEFT*3 to RIGHT*3, node radius=0.2
- **Polynomial formulas**: TexMobject, scale 0.7-0.9, left-aligned with indentation LEFT*4
- **FFT diagram**: 5 vertical stages connected by arrows, scale 0.8, shifted RIGHT*3.5 for code on left
- **Time domain graph**: GraphScene origin DOWN*2 + LEFT*3, x_range 0 to 2*TAU, y_range -2 to 2
- **Frequency domain graph**: GraphScene origin RIGHT*1 + DOWN*3, x_range 0 to 200
- **Code blocks**: TextMobject with Monokai coloring, scale 0.8, left-aligned

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| FFT graph stage 1 edges | [BLUE, SKY_BLUE] | Gradient |
| FFT graph stage 2 edges | [GREEN_SCREEN, BLUE] | Gradient |
| FFT graph stage 3 edges | [MONOKAI_GREEN, GREEN_SCREEN] | Gradient |
| Time domain signal | YELLOW | graph.set_color(YELLOW) |
| Freq domain signal | PINK | graph_f.set_color(PINK) |
| Keyword (code) | MONOKAI_BLUE | def, return, if |
| Function name (code) | MONOKAI_GREEN | multPolynomial, FFT |
| Parameter (code) | MONOKAI_ORANGE | A, B |
| Comment (code) | MONOKAI_GRAY | # descriptions |
| Coefficient highlight | MONOKAI_PURPLE | Array values |
| Input box | YELLOW | SurroundingRectangle |
| Base case box | BLUE | SurroundingRectangle |
| Combine box | ORANGE | SurroundingRectangle |
| Output box | GREEN_SCREEN | SurroundingRectangle |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Butterfly graph creation | run_time=3 | LaggedStartMap ShowCreation |
| Edge stage animation | run_time=3 | LaggedStartMap per stage |
| Polynomial expansion | run_time=2 | TransformFromCopy for each term |
| WAV signal plot | run_time=3 | ShowCreation(graph) |
| Time to freq transform | run_time=3 | TransformFromCopy between graphs |
| Code line writes | 2-3s each | Sequential Write |
| FFT diagram build | run_time=2-3 per stage | ShowCreation per component |
| Total video | ~45 minutes | Two-part FFT series |

## Patterns

### Pattern: Polynomial Algebra with TransformFromCopy

**What**: Step-by-step polynomial multiplication shown by distributing terms. Each coefficient from polynomial A is matched with polynomial B via TransformFromCopy, creating visual connections between source terms and expanded result terms. Multiple animation stages: unexpanded, distributed, simplified.

**When to use**: Any algebraic derivation where terms need to be visually tracked through transformations. Matrix multiplication, convolution, any product expansion.

```python
# Source: projects/Reducible/2020/FFT/fft.py:901-1016
A_x = TexMobject("A(x) = ", "x^2 + 3x + 2")
B_x = TexMobject("B(x) = ", "2x^2 + 1")
C_x_mult = TexMobject("C(x) = ", "(", "x^2 + 3x + 2", ")(", "2x^2 + 1", ")")
self.play(
    TransformFromCopy(A_x[1], C_x_mult[2]),
    TransformFromCopy(B_x[1], C_x_mult[4]),
    FadeIn(C_x_mult[1]), FadeIn(C_x_mult[3]), FadeIn(C_x_mult[5])
)
```

### Pattern: Monokai-Colored Pseudocode

**What**: TextMobject with manual substring coloring to match Monokai syntax theme. Keywords in MONOKAI_BLUE, function names in MONOKAI_GREEN, parameters in MONOKAI_ORANGE, comments in MONOKAI_GRAY. Uses character-index slicing on TextMobject strings.

**When to use**: Any code/pseudocode display in educational animations. Algorithm implementation walkthroughs.

```python
# Source: projects/Reducible/2020/FFT/fft.py:1024-1037
function_def = TextMobject(r"def multPolynomial($A, B$)").scale(code_scale)
function_def[0][:3].set_color(MONOKAI_BLUE)
function_def[0][3:17].set_color(MONOKAI_GREEN)
function_def[0][18].set_color(MONOKAI_ORANGE)
function_def[0][20].set_color(MONOKAI_ORANGE)

description = TextMobject(r"\# computes polynomial $C = A \cdot B$").scale(code_scale)
description.set_color(MONOKAI_GRAY)
```

### Pattern: Hierarchical Algorithm Diagram

**What**: FFT recursive structure shown as a vertical stack of color-coded boxes. Input at top (YELLOW rect), base case below (BLUE rect), recursive even/odd calls side-by-side (YELLOW), combine step (ORANGE rect), output at bottom (GREEN_SCREEN rect). Side facts connected by arrows. Diagram scales and shifts to make room for code.

**When to use**: Any divide-and-conquer algorithm visualization, recursive structure diagrams, MapReduce pipelines, any multi-level computation flow.

```python
# Source: projects/Reducible/2020/FFT/fft.py:3908-4121
class FFTImplementationP1(Scene):
    def show_diagram(self):
        fft_input = self.make_eval_component(poly_rep, point_text)
        fft_input.move_to(UP * 3)
        base_case_component = VGroup(base_case_rect, base_case_text)
        base_case_component.next_to(fft_input, DOWN)
        fft_even = self.make_eval_component(poly_even, point_even)
        fft_odd = self.make_eval_component(poly_odd, point_odd)
        recursive_component = VGroup(fft_even, fft_odd).arrange(RIGHT, buff=1)
        conquer_component = VGroup(rect_split_text, conquer_text)  # ORANGE
        result_component = VGroup(result_rect, result_text)  # GREEN_SCREEN
```

### Pattern: FFT Butterfly Network Graph

**What**: 32 nodes arranged in 8x4 grid with specific cross-connections matching the FFT butterfly pattern. Edges colored by stage (recursion depth). LaggedStartMap ShowCreation for dramatic build, then per-stage ShowCreationThenDestruction to highlight signal flow.

**When to use**: FFT circuit diagrams, sorting networks, any interconnection pattern with regular structure.

```python
# Source: projects/Reducible/2020/FFT/fft.py:572-655
class FFTGraph(GraphAnimationUtils):
    def create_graph(self):
        row_positions = [UP * 3.5, UP * 2.5, ..., DOWN * 3.5]
        column_positions = [LEFT * 3, LEFT * 1, RIGHT * 1, RIGHT * 3]
        for vert in row_positions:
            for hor in column_positions:
                node = GraphNode('', position=vert + hor, radius=0.2)
        # Cross-connections per stage
        for i in range(len(graph) - 1):
            if i % 4 == 0:
                if i % 8 == 0:
                    edges[(i, i + 5)] = graph[i].connect(graph[i + 5])
                else:
                    edges[(i, i - 3)] = graph[i].connect(graph[i - 3])
```

## Scene Flow

1. **Introduction** (0-3min): Earth SVG, utility vs beauty of algorithms. FFT title.
2. **Applications** (3-5min): Wireless comm, GPS, signal processing. Time-domain WAV signal to frequency domain via FFT.
3. **Polynomial Multiplication** (5-15min): A(x)*B(x) expansion. Coefficient representation. O(d^2) complexity. Can we do better?
4. **Value Representation** (15-25min): Polynomial uniquely determined by d+1 points. Evaluation + pointwise multiply + interpolation pipeline.
5. **Roots of Unity** (25-32min): Why evaluate at roots of unity. Complex plane visualization. Collapsing property.
6. **FFT Implementation** (32-40min): Recursive diagram. Even/odd split. Butterfly combine step. Code walkthrough with diagram.
7. **Inverse FFT** (40-45min): Interpolation as inverse evaluation. Same FFT structure with conjugate roots.

> Note: Uses manimlib. GraphScene for plots, TextMobject, ShowCreation, CONFIG dict. Reuses GraphNode from BFS/DFS for butterfly network.
