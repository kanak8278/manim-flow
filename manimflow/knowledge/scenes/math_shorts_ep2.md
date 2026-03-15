---
source: https://github.com/tharun0x/manim-projects/blob/main/2025/shorts/Nov25/episode2.py
project: manim-projects
domain: [mathematics, algebra]
elements: [title, label, equation, formula]
animations: [write, fade_in, fade_out, transform, indicate, rotate]
layouts: [centered, vertical_stack, edge_anchored]
techniques: [custom_animation]
purpose: [demonstration, step_by_step]
mobjects: [Text, Tex, VGroup, Circle, Line]
manim_animations: [Write, FadeIn, FadeOut, Transform, Indicate, Rotate, TransformFromCopy]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 199
scene_classes: [Episode2]
---

## Summary

A math shorts video demonstrating the trick for squaring any number ending in 5. The pattern: take the tens digit, multiply by (itself+1), append "25". Shows two examples (35^2=1225, 65^2=4225) with the tens digit isolated and calculated separately while the 5 dims to 0.3 opacity. Uses the same analog clock timer and cascading CTA pattern as other episodes in the series.

## Design Decisions

- **Dim the trailing 5 to opacity 0.3**: Since the 5 always contributes "25" to the answer, dimming it focuses attention on the tens digit where the actual calculation happens (n x (n+1)).
- **TEAL for tens digit, GOLD for "25" suffix**: Color-codes the two parts of the answer separately so the viewer sees how the final number is composed from two independent computations.
- **GREEN_C for intermediate calculation**: The "3 x 4 = 12" step is colored green to distinguish the working from the input (TEAL) and output (GOLD).
- **Two full examples before challenge**: Reinforces the pattern with both 35^2 and 65^2 so the viewer has confidence before the timed challenge (85^2).
- **TransformFromCopy for CTA cascade**: LIKE transforms a copy into SHARE, which transforms a copy into SUBSCRIBE, creating a cascading reveal effect.

## Composition

- **Title**: Text(font_size=35, fill_color=RED) at `to_edge(UP, buff=1.5)`.
- **Digit display**: Tex(font_size=80), tens digit fill_color=TEAL, ones digit fill_color=WHITE. Arranged RIGHT, buff=0.2 at ORIGIN.
- **Tens digit shift**: LEFT * 1.
- **Calculation text**: Tex(font_size=60) at `next_to(group, DOWN, buff=0.5)`.
- **Result digits**: Tex(font_size=120), GREEN_C for left part, GOLD for "25". Arranged RIGHT, buff=0.1 at ORIGIN.
- **Full equation**: Tex(font_size=55) at `next_to(final, DOWN, buff=1.0)`.
- **CTA**: Text using "American Captain" font, font_size=60, stacked DOWN, buff=0.5 at ORIGIN.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Title | RED | fill_color |
| Tens digit | TEAL | font_size=80 |
| Ones digit (5) | WHITE, then opacity=0.3 | Dimmed during calculation |
| Calculation "n x (n+1)" | default | font_size=60 |
| Calculation result | GREEN_C | font_size=60 |
| Left part of answer | GREEN_C | font_size=120 |
| Right part "25" | GOLD | font_size=120 |
| CTA LIKE | TEAL | American Captain font |
| CTA SHARE | WHITE | American Captain font |
| CTA SUBSCRIBE | RED | American Captain font |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=2 | |
| Problem Write | run_time=1 | |
| Indicate trailing 5 | default | color=RED |
| Tens digit shift | default | LEFT * 1 |
| Calculation write | default | |
| Transform to result | run_time=1.5 | |
| Clock rotation | run_time=5 | linear rate_func |
| CTA cascade | 0.5s each | TransformFromCopy between items |
| CTA exit | run_time=0.8 | lag_ratio=0.1, shift LEFT/RIGHT * 10 |
| Total video | ~55 seconds | |

## Patterns

### Pattern: Dim-and-Focus Digit Isolation

**What**: In a multi-digit number, dims the non-essential digit to opacity 0.3 and shifts the focus digit to the left, visually isolating it for a calculation step. The dimmed digit later transforms into a known constant ("25").

**When to use**: Any mental math trick where part of the input is constant and can be set aside (squaring numbers ending in 5, multiplying by special numbers). Digit decomposition where different parts of a number follow different rules.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode2.py:28-36
# Emphasize the trailing 5
self.play(Indicate(d2, color=RED))

# Isolate tens digit, dim the 5
self.play(
    d1.animate.shift(LEFT * 1),
    d2.animate.set_opacity(0.3)
)
```

### Pattern: Cascading CTA with TransformFromCopy

**What**: Each CTA line (LIKE, SHARE, SUBSCRIBE) appears by TransformFromCopy from the previous line, creating a cascading reveal. Exit animation staggers all three off-screen in alternating directions with lag_ratio=0.1.

**When to use**: Call-to-action endings for YouTube shorts, sequential reveal of related items where each builds on the previous, any staggered text reveal pattern.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode2.py:175-198
like_text = Text("LIKE", font="American Captain", font_size=60, fill_color=TEAL)
share_text = Text("SHARE", font="American Captain", font_size=60, fill_color=WHITE)
sub_text = Text("SUBSCRIBE", font="American Captain", font_size=60, fill_color=RED)

cta_group = VGroup(like_text, share_text, sub_text).arrange(DOWN, buff=0.5)
cta_group.move_to(ORIGIN)

self.play(Write(like_text))
self.play(TransformFromCopy(like_text, share_text))
self.play(TransformFromCopy(share_text, sub_text))

# Staggered exit
self.play(
    like_text.animate.shift(LEFT * 10),
    share_text.animate.shift(RIGHT * 10),
    sub_text.animate.shift(LEFT * 10),
    run_time=0.8,
    lag_ratio=0.1
)
```

## Scene Flow

1. **Hook** (0-4s): Title "Square any number ending in 5 quickly" writes in RED. "35^2 = ?" appears.
2. **Example 1: 35^2** (4-22s): Digits 3 and 5 appear. 5 is Indicated in RED, then dimmed. "3 x (3+1)" transforms to "3 x 4 = 12". The 12 and 25 form "1225". Equation check shown.
3. **Example 2: 65^2** (22-40s): Same pattern with 6. "6 x 7 = 42". Result "4225". Equation check shown.
4. **Challenge** (40-50s): "85^2 = ?" with analog clock countdown (5 seconds).
5. **CTA** (50-55s): LIKE -> SHARE -> SUBSCRIBE cascade. Staggered exit off-screen.
