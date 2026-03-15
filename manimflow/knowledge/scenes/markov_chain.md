---
source: https://github.com/kelvinleandro/manim-animations/blob/main/src/markov.py
project: manim-animations
domain: [probability, statistics, machine_learning]
elements: [circle_node, arrow, curved_arrow, label, markov_chain]
animations: [write, draw]
layouts: [side_by_side]
techniques: []
purpose: [definition, demonstration]
mobjects: [Circle, Arrow, Arc, Text, MathTex]
manim_animations: [Write, Create]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 56
scene_classes: [MarkovChain]
---

## Summary

Visualizes a two-state Markov chain with "Sunny" and "Rainy" weather states. Large colored circles (YELLOW for sunny, BLUE for rainy) represent states, with labeled arrows showing transition probabilities (0.2, 0.4 between states; 0.8, 0.6 self-loops). Self-loops use Arc mobjects with manually added tips. The scene builds incrementally — states first, then transitions one at a time with 1-second pauses between each.

## Design Decisions

- **Color-coded states (YELLOW for sunny, BLUE for rainy)**: Colors match the semantic meaning. YELLOW = sunshine, BLUE = rain. The viewer grasps the states before reading any text. This is the most natural color encoding for a weather Markov chain.
- **Large circles (radius=1)**: States are prominent, centered on the screen. The large size provides ample space for the text labels inside and makes the arrows between states clearly visible.
- **Self-loop arcs with manual tips**: Arc mobjects create semicircular self-loops. Tips are added manually with `add_tip(tip_length=0.2)`. Self-loops on the LEFT side (sunny) and RIGHT side (rainy) maintain visual symmetry.
- **One transition at a time**: Each arrow and its probability label appear separately with 1-second waits. This pacing lets the viewer absorb each transition probability before the next appears. Building incrementally is essential for Markov chains — the viewer needs to understand each probability individually.
- **Bidirectional offset arrows**: Forward arrow is offset UP*0.3, backward arrow DOWN*0.3. This prevents overlap while keeping arrows visually parallel.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)` — "Markov Chain"
  - Sunny state: `shift(LEFT * 3)`, Circle radius=1, YELLOW
  - Rainy state: `shift(RIGHT * 3)`, Circle radius=1, BLUE
  - State labels: `move_to(state.get_center())`, font_size=24
  - Transition labels: `next_to(arrow, UP/DOWN)` for inter-state, `next_to(arc, LEFT/RIGHT, buff=0.2)` for self-loops
- **Arrow offsets**: sunny_to_rainy start at get_right()+UP*0.3, rainy_to_sunny at get_left()+DOWN*0.3
- **Self-loop arcs**: radius=0.5, sunny loop angle=4*PI/3 from PI/3, rainy loop angle=-4*PI/3 from 2*PI/3
- **Self-loop positions**: `next_to(state, LEFT/RIGHT, buff=0.2)`

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Sunny state | YELLOW | Circle radius=1 |
| Rainy state | BLUE | Circle radius=1 |
| State labels | WHITE | font_size=24, centered in circle |
| Transition arrows | WHITE | Default Arrow |
| Self-loop arcs | WHITE | radius=0.5, tip_length=0.2 |
| Probability labels | WHITE | MathTex, default font_size |

Color strategy: Only the state circles are colored. Everything else is WHITE. This keeps the focus on the two states and their semantic meaning (sunny=yellow, rainy=blue).

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | ~1s | + 1s wait |
| States Create | ~1s | Simultaneous, + 1s wait |
| State labels Write | ~1s | Simultaneous, + 1s wait |
| Sunny-to-rainy arrow + label | ~1s | + 1s wait |
| Rainy-to-sunny arrow + label | ~1s | + 1s wait |
| Sunny self-loop + label | ~1s | + 1s wait |
| Rainy self-loop + label | ~1s | + 1s wait |
| Total video | ~14 seconds | |

## Patterns

### Pattern: Two-State Markov Chain Layout

**What**: Two large circles spaced horizontally (LEFT*3 and RIGHT*3) with centered text labels. Bidirectional arrows between them (offset vertically to avoid overlap) and self-loop arcs on the outer sides. Probability labels next to each arrow.
**When to use**: Two-state Markov chains, binary state machines, any system with two states and four transitions (A->A, A->B, B->A, B->B). The symmetric layout works for any pair of states.

```python
# Source: projects/manim-animations/src/markov.py:7-34
sunny_state = Circle(radius=1, color=YELLOW).shift(LEFT * 3)
rainy_state = Circle(radius=1, color=BLUE).shift(RIGHT * 3)

sunny_label = Text("Sunny", font_size=24).move_to(sunny_state.get_center())
rainy_label = Text("Rainy", font_size=24).move_to(rainy_state.get_center())

sunny_to_rainy = Arrow(start=sunny_state.get_right() + UP * 0.3, end=rainy_state.get_left() + UP * 0.3, buff=0.2)
rainy_to_sunny = Arrow(start=rainy_state.get_left() + DOWN * 0.3, end=sunny_state.get_right() + DOWN * 0.3, buff=0.2)

sunny_to_sunny = Arc(
    radius=0.5,
    start_angle=PI / 3,
    angle=4 * PI / 3,
).next_to(sunny_state, LEFT, buff=0.2)
sunny_to_sunny.add_tip(tip_length=0.2)
```

## Scene Flow

1. **Title** (0-2s): "Markov Chain" writes at top.
2. **States** (2-5s): Yellow sunny circle and blue rainy circle create simultaneously. State labels "Sunny" and "Rainy" write inside.
3. **Inter-state transitions** (5-9s): Sunny-to-rainy arrow with "0.2" label appears. Rainy-to-sunny arrow with "0.4" label appears.
4. **Self-loops** (9-14s): Sunny self-loop arc with "0.8" label appears on the left. Rainy self-loop arc with "0.6" label appears on the right.

> Full file: `projects/manim-animations/src/markov.py` (56 lines)
