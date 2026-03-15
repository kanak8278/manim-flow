---
source: https://github.com/tharun0x/manim-projects/blob/main/2025/shorts/Nov25/episode1.py
project: manim-projects
domain: [mathematics, algebra]
elements: [title, label, equation, formula, brace, circle_node, line, arrow]
animations: [write, fade_in, fade_out, transform, indicate, grow_from_center, rotate]
layouts: [centered, vertical_stack, edge_anchored]
techniques: [custom_animation]
purpose: [demonstration, step_by_step]
mobjects: [Text, Tex, VGroup, Circle, Line, Triangle, SurroundingRectangle, Brace, Cross]
manim_animations: [Write, FadeIn, FadeOut, MoveToTarget, Transform, GrowFromCenter, Rotate, ShowCreation, ShrinkToCenter]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 198
scene_classes: [Episode1]
---

## Summary

A math shorts video demonstrating the mental trick for multiplying any 2-digit number by 11. Shows the simple case (23x11=253: insert sum of digits) and the carry case (58x11=638: carry the tens digit). Digits are animated as large individual Tex elements that split apart, with the computed middle digit sliding into the gap. Includes a timed challenge with an analog clock and a CTA outro.

## Design Decisions

- **Individual digit Tex elements**: Each digit of the number is a separate Tex object so they can be independently animated (split apart, shift, transform). This is critical for showing the "insert digit in the middle" mechanic.
- **Carry visualization with Brace**: When the digit sum exceeds 9 (58: 5+8=13), a Brace groups the carried digit with the left digit, and a "+" sign appears below to show the addition visually before the transform.
- **Analog clock timer for challenge**: A simple clock face (Circle + 4 tick Lines + rotating hand Line) gives the viewer 5 seconds to solve. The hand Rotates -TAU (full clockwise revolution) with linear rate_func.
- **Consistent color scheme**: BLUE for digits being manipulated, RED for titles/emphasis, YELLOW for carry indicators. This keeps the visual language consistent across the episode.
- **CTA with geometric shapes**: The Like/Share/Subscribe text gets wrapped in Triangle, Circle, and SurroundingRectangle shapes for visual flair before shrinking to center.

## Composition

- **Title**: Text(font_size=35, fill_color=RED) at `to_edge(UP, buff=1.5)`.
- **Problem equation**: Tex(font_size=50) at `next_to(title, DOWN, buff=1.5)`.
- **Digit display**: Tex(font_size=120, fill_color=BLUE), arranged `RIGHT, buff=0.2`, centered at ORIGIN.
- **Digit split**: Each digit shifts LEFT/RIGHT * 0.75.
- **Calculation text**: Tex(font_size=80) at `next_to(group, DOWN, buff=1.0)`.
- **Edge case section**: Text(font_size=50) at `to_edge(UP, buff=2.0)`, subtitle at `next_to(edge_cases, DOWN, buff=0.5)`.
- **Clock**: Circle(radius=0.5), hand Line(ORIGIN, UP*0.4), at `next_to(question, DOWN, buff=1)`.
- **CTA**: Text(font_size=40) at `to_edge(UP, buff=1.8)`, stacked DOWN with buff=1.2.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Title text | RED | fill_color |
| Digits | BLUE | fill_color, font_size=120 |
| Calculation | default WHITE | font_size=80 |
| Carry brace | default | Brace with buff=0.1 |
| Plus sign | YELLOW | font_size=40 |
| New carried digit | BLUE | font_size=120 |
| Full equation check | default | font_size=55 |
| Clock hand | RED | stroke_width=4 |
| CTA "Like/Share/Subscribe" | RED | font_size=40 |
| CTA "and" | WHITE | font_size=40 |
| Bell icon text | YELLOW | font_size=30 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=3 | |
| Problem Write | run_time=3 | |
| Digit split | run_time=1 | shift LEFT/RIGHT * 0.75 |
| Middle digit move | run_time=1.5 | scale(1.5) and color change |
| Final arrange | run_time=1 | arrange(RIGHT, buff=0.1) |
| Carry brace + plus | default | GrowFromCenter |
| Carry transform | run_time=1.5 | Multiple simultaneous transforms |
| Clock rotation | run_time=5 | -TAU, linear rate_func |
| CTA ShrinkToCenter | run_time=1.5 | |
| Total video | ~60 seconds | |

## Patterns

### Pattern: Digit Split and Insert for Mental Math

**What**: Displays a multi-digit number as separate Tex objects, animates them splitting apart by shifting left/right, computes a result digit, and slides it into the gap to form a new number. The final result is re-arranged with tight spacing.

**When to use**: Mental math trick demonstrations, digit manipulation visualizations, any scenario where individual digits of a number need to be independently animated (multiplication tricks, addition carry, digit rearrangement).

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode1.py:18-54
d1 = Tex("2", font_size=120, fill_color=BLUE)
d2 = Tex("3", font_size=120, fill_color=BLUE)
group_23 = VGroup(d1, d2).arrange(RIGHT, buff=0.2)
group_23.move_to(ORIGIN)

self.play(Write(group_23))
# Split digits apart
self.play(
    d1.animate.shift(LEFT * 0.75),
    d2.animate.shift(RIGHT * 0.75),
    run_time=1
)
# Compute and show middle digit
calculation = Tex("2 + 3 = 5", font_size=80)
calculation.next_to(group_23, DOWN, buff=1.0)
self.play(Write(calculation))

middle_digit = calculation[-1].copy()
self.play(
    middle_digit.animate.move_to(ORIGIN).scale(1.5).set_color(BLUE),
    FadeOut(calculation),
    run_time=1.5
)
# Re-form final number
final_result = VGroup(d1, middle_digit, d2)
self.play(final_result.animate.arrange(RIGHT, buff=0.1).move_to(ORIGIN))
```

### Pattern: Carry Digit with Brace Indicator

**What**: When a digit sum exceeds 9, shows the two-digit result in the middle, then uses a Brace and "+" sign to indicate the carry operation. The tens digit fades into the left digit while the ones digit remains.

**When to use**: Carrying in addition or multiplication, any multi-digit arithmetic where overflow from one place value affects the next. Shows the mechanical process of carrying visually.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode1.py:102-121
digit_1 = mid_13[0]  # The '1' to carry
digit_3 = mid_13[1]  # The '3' stays

brace = Brace(VGroup(e_d1, digit_1), DOWN, buff=0.1)
plus_sign = Tex("+", font_size=40, color=YELLOW).next_to(brace, DOWN, buff=0.1)
self.play(GrowFromCenter(brace), Write(plus_sign))

new_d1 = Tex("6", font_size=120, fill_color=BLUE).move_to(e_d1)
self.play(
    FadeOut(brace), FadeOut(plus_sign),
    digit_1.animate.move_to(e_d1.get_center()).set_opacity(0),
    Transform(e_d1, new_d1),
    digit_3.animate.next_to(new_d1, RIGHT, buff=0.1),
    e_d2.animate.next_to(digit_3, RIGHT, buff=0.1),
    run_time=1.5
)
```

### Pattern: Analog Clock Countdown Timer

**What**: A minimal clock face built from a Circle, 4 tick marks at cardinal positions, and a hand Line that rotates -TAU (full revolution clockwise) over 5 seconds with linear rate_func. Used to give the viewer time to solve a challenge.

**When to use**: Timed challenge segments in educational shorts, countdown timers, any pause where the viewer needs thinking time with a visual indicator of time passing.

```python
# Source: projects/manim-projects/2025/shorts/Nov25/episode1.py:142-158
clock = VGroup()
face = Circle(radius=0.5)
ticks = VGroup()
for i in range(4):
    tick = Line(UP * 0.4, UP * 0.5).rotate(i * PI / 2, about_point=ORIGIN)
    ticks.add(tick)
hand = Line(ORIGIN, UP * 0.4, color=RED, stroke_width=4)
clock.add(face, ticks, hand)
clock.next_to(q1, DOWN, buff=1)

self.play(Write(clock))
self.play(
    Rotate(hand, angle=-TAU, about_point=face.get_center()),
    run_time=5,
    rate_func=linear
)
```

## Scene Flow

1. **Hook** (0-7s): Title "Multiply any 2 digit number by 11 in 5 seconds?" writes in RED. Problem "23 x 11 = ?" appears below.
2. **Simple case** (7-22s): Digits 2 and 3 appear large and blue, split apart. "2 + 3 = 5" shows below. The 5 slides into the middle gap. Final "253" forms. Equation check appears.
3. **Edge case** (22-40s): "Edge Cases" title. Digits 5 and 8 split. "5 + 8 = 13" shown. The "13" moves to middle, brace shows carry, 5 becomes 6. Final "638" forms.
4. **Challenge** (40-50s): "Your turn! Try this" with "43 x 11 = ?". Clock timer counts down 5 seconds.
5. **CTA** (50-60s): Like/Share/Subscribe text with geometric shapes (Triangle, Circle, Rectangle). ShrinkToCenter exit.
