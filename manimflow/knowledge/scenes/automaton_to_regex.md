---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/automaton.py
project: manim-animations
domain: [computer_science, automata, formal_languages]
elements: [dot, arrow, curved_arrow, label, state_machine, surrounding_rect]
animations: [write, draw, grow_arrow, replacement_transform, color_change, fade_out]
layouts: [horizontal_row, centered, edge_anchored]
techniques: [color_state_machine, progressive_disclosure]
purpose: [transformation, step_by_step, decomposition, process]
mobjects: [Dot, Arrow, CurvedArrow, Arc, MathTex, Text, VGroup, Circle]
manim_animations: [Write, Create, GrowArrow, ReplacementTransform, FadeIn, FadeOut]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 328
scene_classes: [AutomatonToRegex]
---

## Summary

Visualizes the state elimination algorithm for converting a finite automaton to a regular expression. Five states (q0-q4) are laid out horizontally with labeled transitions. States are eliminated one by one: each elimination highlights the affected edges in BLUE, then ReplacementTransforms them into new combined edges with concatenated regex labels. The final result is a single arrow from start to final state with the complete regex "ba*bb(ab)*b(ab(ab)*b)*".

## Design Decisions

- **Horizontal state layout with 2-unit spacing**: States are placed at LEFT*4 through RIGHT*4 in increments of 2. This gives a linear left-to-right reading order matching how automata are typically drawn in textbooks.
- **BLUE highlight before elimination**: Before each state removal, all affected edges and labels turn BLUE. This draws the viewer's eye to exactly what will change. After the transform, the new elements also start BLUE then fade to WHITE. The BLUE acts as a "processing" indicator.
- **Constants for styling consistency**: FONT_SIZE=24, LABEL_BUFF=0.2, ARROW_STROKE_WIDTH=3, ARROW_TIP_LENGTH=0.1, TRANSFORM_RUN_TIME=2 are defined as module-level constants. This ensures visual consistency across all 7 elimination steps.
- **Arc for self-loops**: Self-loops use `Arc(radius=0.15, start_angle=PI, angle=PI)` positioned at the bottom of the state dot. This is the standard visual convention for self-transitions in automata diagrams.
- **CurvedArrow for back-edges**: The q4-to-q2 backward transition uses CurvedArrow to arc over the forward edges. This prevents visual overlap with the left-to-right arrows.
- **Circle indicator for final state**: q4 has a Circle(radius=0.15) surrounding the dot — the double-circle convention for accepting states in automata theory.
- **ReplacementTransform for state elimination**: Groups of old edges collapse into new combined edges via ReplacementTransform. This visually communicates "these separate paths become one path with a combined label."

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Automaton => Regex"
  - States: horizontal line, q0 at LEFT*4, q1 at LEFT*2, q2 at ORIGIN, q3 at RIGHT*2, q4 at RIGHT*4
  - State labels: `next_to(dot, UP, buff=0.2)` — q0 through q4
  - Start indicator: arrow symbol `next_to(q0_dot, LEFT, buff=0.3)`
  - Final state indicator: Circle(radius=0.15) around q4 dot
- **Arrow configuration**: stroke_width=3, max_tip_length_to_length_ratio=0.1
- **Self-loop arcs**: radius=0.15, positioned at dot bottom, tip_length=0.1, tip_width=0.1
- **Transition labels**: font_size=24, next_to arrow with buff=0.2 (UP for forward, DOWN for backward/loops)
- **Bidirectional edges (q2-q3)**: Offset by UP*0.1 and DOWN*0.1 to prevent overlap

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| State dots | WHITE | Default Dot |
| State labels | WHITE | MathTex, font_size=24 |
| Arrows | WHITE | stroke_width=3 |
| Transition labels | WHITE | Text/MathTex, font_size=24 |
| Final state circle | WHITE | stroke_width=2, radius=0.15 |
| Elimination highlight | BLUE | Applied before ReplacementTransform |
| New edges (post-transform) | BLUE then WHITE | Blue briefly, then animated to white |

Color strategy: Minimal — WHITE for all static elements, BLUE exclusively as a transient "this is being processed" state. The color change cycle (WHITE -> BLUE -> transform -> BLUE -> WHITE) creates a clear visual rhythm for each elimination step.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| State + arrow creation | ~1s each | Sequential per state |
| Highlight to BLUE | ~1s | group.animate.set_color(BLUE) |
| ReplacementTransform | run_time=2 | TRANSFORM_RUN_TIME constant |
| Reset to WHITE | ~1s | group.animate.set_color(WHITE) |
| Per elimination step | ~5s | Highlight + transform + reset + wait |
| Total video | ~50 seconds | 7 elimination steps |

## Patterns

### Pattern: State Elimination via Grouped ReplacementTransform

**What**: Group all edges and labels being eliminated into a VGroup, group all new replacement edges into another VGroup, highlight the old group in BLUE, then ReplacementTransform old into new. After the transform, reset the new group to WHITE. This three-phase cycle (highlight, transform, reset) repeats for every elimination step.
**When to use**: Automaton state elimination, graph simplification, any step-by-step reduction where multiple elements merge into fewer elements. Also works for circuit simplification or algebraic reduction steps.

```python
# Source: projects/manim-animations/src/automaton.py:195-217
group_to_remove = VGroup(
    arrow_q0_q2, text_q0_q2, q2_dot, q2_text,
    arrow_q2_q3, text_q2_q3, arrow_q3_q2, text_q3_q2,
    arrow_q4_q2, text_q4_q2,
)

group_to_create = VGroup(
    arrow_q0_q3, text_q0_q3, arrow_q3_q3, text_q3_q3, arrow_q4_q3, text_q4_q3
)

self.play(group_to_remove.animate.set_color(BLUE))
self.play(
    ReplacementTransform(group_to_remove, group_to_create),
    run_time=TRANSFORM_RUN_TIME,
)
self.play(group_to_create.animate.set_color(WHITE))
```

### Pattern: Bidirectional Arrows with Vertical Offset

**What**: When two states have transitions in both directions, offset the arrows vertically (UP*0.1 for forward, DOWN*0.1 for backward) so they don't overlap. Labels go above and below respectively.
**When to use**: Any directed graph with bidirectional edges — automata, network diagrams, Markov chains, flow diagrams where two nodes communicate in both directions.

```python
# Source: projects/manim-animations/src/automaton.py:72-85
arrow_q2_q3 = Arrow(
    start=q2_dot.get_right() + UP * 0.1,
    end=q3_dot.get_left() + UP * 0.1,
    stroke_width=ARROW_STROKE_WIDTH,
    max_tip_length_to_length_ratio=ARROW_TIP_LENGTH,
)
text_q2_q3 = b.copy().next_to(arrow_q2_q3, UP, buff=LABEL_BUFF)
arrow_q3_q2 = Arrow(
    start=q3_dot.get_left() + DOWN * 0.1,
    end=q2_dot.get_right() + DOWN * 0.1,
    stroke_width=ARROW_STROKE_WIDTH,
    max_tip_length_to_length_ratio=ARROW_TIP_LENGTH,
)
text_q3_q2 = a.copy().next_to(arrow_q3_q2, DOWN, buff=LABEL_BUFF)
```

### Pattern: Self-Loop Arc with Tip

**What**: Create a self-loop on a state using `Arc(radius=0.15, start_angle=PI, angle=PI)` positioned at the bottom of the state dot. Manually add a tip with `add_tip(tip_length=0.1, tip_width=0.1)`. The arc creates a semicircle below the node.
**When to use**: Self-transitions in automata, recursive state in state machines, self-referencing nodes in any graph visualization.

```python
# Source: projects/manim-animations/src/automaton.py:59-64
arrow_q1_q1 = (
    Arc(radius=0.15, start_angle=PI, angle=PI)
    .move_to(q1_dot.get_bottom())
    .add_tip(tip_length=0.1, tip_width=0.1)
)
text_q1_q1 = a.copy().next_to(arrow_q1_q1, DOWN, buff=LABEL_BUFF)
```

### Pattern: Final State Double Circle

**What**: An accepting/final state is shown as a Dot with a surrounding Circle(radius=0.15, stroke_width=2). Both are grouped into a VGroup so they move together. This follows the standard automata theory visual convention.
**When to use**: Finite automata final/accepting states, goal states in search problems, terminal nodes in any state machine diagram.

```python
# Source: projects/manim-animations/src/automaton.py:43-47
q4_dot = dot.copy().shift(RIGHT * 4)
final_indicator = Circle(radius=0.15, color=WHITE, stroke_width=2).move_to(
    q4_dot.get_center()
)
final_state = VGroup(q4_dot, final_indicator)
```

## Scene Flow

1. **Build automaton** (0-12s): Title writes. States q0-q4 appear left to right with arrows and transition labels (a, b). Self-loop on q1, bidirectional edges between q2-q3, back-edge from q4 to q2.
2. **Eliminate q1 loop** (12-17s): Self-loop "a" and edge label "b" on q1-q2 highlight BLUE, transform to "a*b" label.
3. **Eliminate q1** (17-22s): q0-q1 and q1-q2 edges merge into single q0-q2 edge with label "ba*b".
4. **Eliminate q2** (22-27s): All edges through q2 merge. New edges: q0-q3 "ba*bb", q3 self-loop "ab", q4-q3 "ab".
5. **Eliminate q3 loop** (27-32s): q3 self-loop absorbed. Labels become "ba*bb(ab)*" and "ab(ab)*".
6. **Eliminate q3** (32-37s): q0-q4 becomes "ba*bb(ab)*b", q4 self-loop "ab(ab)*b".
7. **Eliminate q4 loop** (37-42s): Final edge q0-q4 becomes "ba*bb(ab)*b(ab(ab)*b)*".
8. **Cleanup** (42-47s): Start indicator, states, and arrows fade out. Only the regex text remains.

> Full file: `projects/manim-animations/src/automaton.py` (328 lines)
