---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/dice.py
project: manim-scripts
domain: [probability, statistics, mathematics]
elements: [dot, box, grid, label, formula]
animations: [rotate, write, fade_in]
layouts: [grid, centered, horizontal_row]
techniques: [factory_pattern, helper_function, data_driven]
purpose: [demonstration, distribution]
mobjects: [VGroup, RoundedRectangle, Dot, Cube, Tex, MathTex, Text]
manim_animations: [Rotate, Write, FadeIn, Create]
scene_type: Scene
manim_version: manim_community
complexity: beginner
lines: 125
scene_classes: [Dice, RoundSquareDots, DiceProbability, HundredDice, MatrixScene]
---

## Summary

A set of dice-related scenes using a shared `get_diceface()` factory function that builds dice faces as RoundedRectangle with positioned green dots. Scenes range from a simple 3D cube rotation, to inline probability expressions with dice mobjects, to 10x10 grids of random dice. The factory function from `manim_utils.py` is the reusable core — it handles all 6 face layouts.

## Design Decisions

- **Factory function for dice faces**: `get_diceface(n)` returns a VGroup (RoundedRectangle + positioned Dots) for any value 1-6. This decouples face layout from scene logic, enabling reuse across 5 different scenes.
- **Green dots on white rounded rectangle**: Standard dice aesthetic. Dot radius=0.15, gap_factor=0.6 controls dot spacing relative to center. Positions use standard Manim direction constants (UR, UL, DR, DL, etc.).
- **Dice as inline mobjects in probability expressions**: DiceProbability embeds actual dice face VGroups inside a MathTex probability expression using VGroup.arrange(). This makes the formula concrete — the viewer sees the actual face, not just a number.
- **Grid layout for large collections**: HundredDice and MatrixScene arrange 100 dice in a 10x10 grid using manual positioning (move_to with row/col offsets). Scale=0.2-0.3 to fit all on screen.

## Composition

- **Dice face sizing**: RoundedRectangle height=2.0, width=2.0, corner_radius=0.3 (base size)
- **Dot positions**: gap_factor=0.6 from center. 1: ORIGIN, 2: LEFT/RIGHT, 3: ORIGIN+UP+DOWN, etc.
- **3D Cube**: side_length=3, fill_opacity=0.7, fill_color=BLUE
- **Grid layout (HundredDice)**: scale=0.2, positioned with `LEFT*j - LEFT*1 + UP*i - DOWN*1`
- **Grid layout (MatrixScene)**: scale=0.3, spacing=0.8, starts at LEFT*5 + UP*4.5
- **Probability expression**: VGroup arranged RIGHT, buff=0.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Dice border | WHITE | RoundedRectangle default |
| Dice dots | GREEN | radius=0.15 |
| 3D Cube | BLUE | fill_opacity=0.7, stroke_width=0.2 |
| Title text | WHITE | font_size=48 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Cube rotation | Default | Random axis and angle |
| Dice grid FadeIn | Default | All 100 dice simultaneously |
| Probability Write | Default | Full group writes |
| Rotate each face | Default | PI/3 rotation per face |
| Total (HundredDice) | ~3s | Single FadeIn |

## Patterns

### Pattern: Dice Face Factory Function

**What**: Creates a standard dice face as a VGroup of RoundedRectangle + positioned Dots. Handles all 6 standard layouts using Manim direction constants. Returns a self-contained mobject that can be scaled, positioned, and composed.
**When to use**: Any probability visualization involving dice, board game animations, random variable demonstrations, or any scenario needing a recognizable dice face icon.

```python
# Source: projects/manim-scripts/src/manim_utils.py:3-45
def get_diceface(num=1):
    dice_face = VGroup()
    round_square = RoundedRectangle(corner_radius=0.3, height=2.0, width=2.0)
    dice_face.add(round_square)
    dot1 = Dot(radius=0.15, color=GREEN)
    # ... create dot2-dot6 ...
    gap_factor = 0.6
    if num == 1:
        round_square.add(dot1.move_to(ORIGIN))
    elif num == 4:
        round_square.add(dot1.move_to(UR * gap_factor))
        round_square.add(dot2.move_to(UL * gap_factor))
        round_square.add(dot3.move_to(DR * gap_factor))
        round_square.add(dot4.move_to(DL * gap_factor))
    # ... handles all 6 faces ...
    return dice_face
```

### Pattern: Mobject Inline in Math Expression

**What**: Embed visual mobjects (dice faces, icons) directly inside a mathematical expression by using VGroup.arrange(). The dice face becomes part of the probability formula, making abstract notation concrete.
**When to use**: Probability expressions with dice/cards/coins, any formula where replacing a symbol with its visual representation aids understanding.

```python
# Source: projects/manim-scripts/scenes/dice.py:73-84
dice1 = get_diceface(random.randrange(1, 6))
dice2 = get_diceface(random.randrange(1, 6))
probability_text1 = MathTex("P( ")
probability_text2 = MathTex(") + P( ")
probability_text3 = MathTex(r") = \frac{1}{3}")
probability_group = VGroup(probability_text1, dice1, probability_text2, dice2, probability_text3)
probability_group.arrange(RIGHT, buff=0.5)
self.play(Write(probability_group))
```

## Scene Flow

1. **Dice** (0-5s): 3D cube with face labels appears. Rotates randomly.
2. **RoundSquareDots** (0-8s): Five dice faces at screen edges, each rotates PI/3.
3. **DiceProbability** (0-3s): Probability expression with embedded dice faces writes in.
4. **HundredDice** (0-3s): 100 random dice in 10x10 grid fade in simultaneously.
5. **MatrixScene** (0-3s): 100 dice in tighter grid layout write in.

> Full file: `projects/manim-scripts/scenes/dice.py` (125 lines)
