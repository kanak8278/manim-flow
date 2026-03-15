---
source: https://github.com/nipunramk/Reducible/blob/main/2020/BigO/bigo.py
project: Reducible
domain: [computer_science, algorithms, complexity, mathematics]
elements: [axes, function_plot, label, formula, equation, table, line, arrow]
animations: [fade_in, fade_out, write, draw, transform, replacement_transform, grow]
layouts: [centered, side_by_side, vertical_stack]
techniques: [progressive_disclosure, data_driven]
purpose: [comparison, demonstration, derivation, step_by_step]
mobjects: [GraphScene, Line, Arrow, VGroup, TextMobject, TexMobject, RegularPolygon, DecimalNumber, Circle, Rectangle]
manim_animations: [FadeIn, FadeOut, ShowCreation, Write, Transform, ReplacementTransform, Rotate]
scene_type: GraphScene
manim_version: manimlib
complexity: beginner
lines: 2772
scene_classes: [PlotFunctions, GraphCounter, Thumbnail, Comparison, Story, IntroduceBigO, Definition, RunningTimeClasses, BigOSteps, Ex1, Conclusion, ExampleProblem]
---

## Summary

Visualizes Big O notation concepts using GraphScene for plotting growth functions (O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n)). Features a comparison scene where two algorithms (Bob's and Alice's) are timed on increasing input sizes using tables and graphs, demonstrating why runtime analysis matters more than benchmarking. Includes interactive counter display, formal Big O definition with epsilon-delta style proofs, and running time class hierarchy.

## Design Decisions

- **GraphScene for function plotting**: Uses manimlib's GraphScene with configurable axis ranges. Multiple growth functions plotted simultaneously with distinct colors for comparison.
- **Bob vs Alice comparison**: Two colored tables (ORANGE for Bob, GREEN_SCREEN for Alice) showing runtime data. Tables transform into graphs to motivate mathematical analysis over empirical timing.
- **Clock animation for timing**: Two analog clocks (Circle + Line hands) that rotate to show algorithm execution time. Visceral representation of "waiting for the algorithm."
- **Color gradient for complexity**: O(1) to O(2^n) displayed left to right with a GREEN_SCREEN to BRIGHT_RED gradient arrow, intuitively mapping "fast" to "slow."
- **GraphCounter with live values**: Graph that extends as x_max increases, with DecimalNumber displays showing current x and f(x) values updating in real time.

## Composition

- **Growth function graphs**: graph_origin LEFT*4 + DOWN*3, x/y ranges vary per scene
- **Comparison tables**: make_2_column_table() at LEFT*5 and RIGHT*5, 6 rows, width=4
- **Clocks**: Circle(radius=0.5), blue, positioned LEFT*3 and RIGHT*3 at DOWN
- **Running time labels**: scale=1.2, positioned every 2 units from LEFT*5.4 to RIGHT*5.4 at DOWN*1.5
- **Gradient arrow**: Line from LEFT*5.5 to RIGHT*5.4 with color gradient

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| O(1) | GREEN_SCREEN | Constant time |
| O(log n) | GREEN | Logarithmic |
| O(n) | YELLOW | Linear |
| O(n log n) | ORANGE | Linearithmic |
| O(n^2) | RED | Quadratic |
| O(2^n) | BRIGHT_RED | Exponential |
| Bob's data | ORANGE | Table + graph |
| Alice's data | GREEN_SCREEN | Table + graph |
| Clock elements | BLUE | Circle + hands |
| Complexity arrow | gradient GREEN_SCREEN to BRIGHT_RED | Speed indicator |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Function graph creation | default | ShowCreation per graph |
| Clock rotation | run_time=4 | 4 full rotations |
| Table data population | run_time=2 | FadeIn all cells |
| Counter increment | run_time=0.5 | Transform per step |
| Total video | ~15 minutes | Big O tutorial |

## Patterns

### Pattern: Multi-Function GraphScene Comparison

**What**: Multiple mathematical functions plotted on the same axes with distinct colors. Each function's graph created via self.get_graph(), displayed simultaneously. Labels via get_graph_label(). Shows relative growth rates visually.

**When to use**: Complexity class comparison, any mathematical function comparison, algorithm performance visualization, statistical distribution overlays.

```python
# Source: projects/Reducible/2020/BigO/bigo.py:3-41
class PlotFunctions(GraphScene):
    CONFIG = {"x_min": 0, "x_max": 900, "y_min": 0, "y_max": 1000000, ...}
    def construct(self):
        self.setup_axes(animate=True)
        func_graph = self.get_graph(self.func_to_graph, self.function_color)
        func_graph2 = self.get_graph(self.func_to_graph2)
        func_graph3 = self.get_graph(self.func_to_graph3, YELLOW)
        self.play(ShowCreation(func_graph), ShowCreation(func_graph2), ShowCreation(func_graph3))
```

### Pattern: Analog Clock for Time Visualization

**What**: Circle + two Line hands (minute and hour) animated with Rotate around the circle center. Multiple rotations create the impression of time passing. Paired with text labels showing actual timing results.

**When to use**: Algorithm timing demonstrations, any scenario where you need to visually represent the passage of time during a computation.

```python
# Source: projects/Reducible/2020/BigO/bigo.py:265-314
clock_circle = Circle(radius=0.5).set_color(BLUE)
minute_hand = Line(clock_circle.get_center(), clock_circle.get_center() + UP * 0.95 * clock_circle.radius)
hour_hand = Line(clock_circle.get_center(), clock_circle.get_center() + RIGHT * 0.75 * clock_circle.radius)
clock = VGroup(clock_circle, minute_hand, hour_hand).shift(LEFT * 3 + DOWN)
self.play(
    Rotate(minute_hand, angle=-360*4*DEGREES, about_point=clock_circle.get_center()),
    Rotate(hour_hand, angle=-30*4*DEGREES, about_point=clock_circle.get_center()),
    run_time=4
)
```

## Scene Flow

1. **Comparison** (0-5min): Bob vs Alice timing. Clock animations. Tables with increasing input sizes. Transform to graphical comparison.
2. **Story** (5-7min): Why we need Big O, not benchmarks.
3. **Big O Definition** (7-12min): Formal definition with c and n0. GraphScene showing f(n) <= c*g(n) for n >= n0.
4. **Running Time Classes** (12-14min): O(1) through O(2^n) with color gradient.
5. **Steps for Analysis** (14-16min): How to determine Big O of an algorithm.
6. **Example Problem** (16-18min): Worked example with code analysis.

> Note: Uses manimlib (oldest Reducible file, uses big_ol_pile_of_manim_imports). GraphScene, TexMobject, TextMobject.
