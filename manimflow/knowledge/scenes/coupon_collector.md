---
source: https://github.com/vivek3141/videos/blob/main/coupon.py
project: vivek3141_videos
domain: [mathematics, probability, statistics, combinatorics]
elements: [equation, label, bar_chart, svg_icon, arrow, surrounding_rect, formula, line, dot]
animations: [write, transform, fade_in, fade_out, grow]
layouts: [centered, horizontal_row, vertical_stack]
techniques: [custom_mobject, progressive_disclosure, data_driven]
purpose: [derivation, step_by_step, demonstration, distribution]
mobjects: [VGroup, Circle, Rectangle, TexMobject, TextMobject, SVGMobject, Line, BackgroundRectangle, Brace, ScreenRectangle, Arrow, ImageMobject]
manim_animations: [Write, Transform, TransformFromCopy, FadeInFromDown, Uncreate, ApplyMethod, GrowFromCenter]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 708
scene_classes: [TreeMobject, Intro, ExpectedValue, Tails, Bernoulli, RollingDice, ExpectBern, DiceExp, NumberedCoupon, CouponCalc, Asymptote]
---

## Summary

Derives the coupon collector problem solution E[n] = N * H_N (N times the N-th harmonic number) through progressive probability concepts. Starts with expected value definition using a coin-flip tree diagram, moves through Bernoulli trials and geometric distribution (E[x] = 1/p), then builds the coupon-specific calculation. A custom RollingDice mobject simulates dice rolls with configurable dot patterns. NumberedCoupon wraps an SVG coupon with a numbered label. The probability decreases as coupons are collected (5/5, 4/5, 3/5...), leading to the harmonic series. A bar chart shows E[n] growing sub-linearly.

## Design Decisions

- **Tree diagram for expected value**: A TreeMobject (1 root -> 2 leaves for H/T) with branch labels showing x*p products. Sum line at bottom. This is the standard way to teach expected value visually.
- **RollingDice custom mobject**: Rectangle with configurable dot patterns (1-6) using Circles at fixed positions. `set_value()` method switches patterns. Rolling animation uses decreasing wait times (geometric acceleration: t *= 2) for a realistic slow-down effect.
- **NumberedCoupon SVG wrapper**: SVG coupon icon rotated -PI/2, with a colored Tex number overlaid at 0.4*UP. This creates a recognizable "coupon card" visual.
- **Two-row coupon tracking**: "Don't Have" row (YELLOW) and "Have" row (GREEN) of 5 coupons. As each is collected, it moves from Don't Have to Have, and the probability fraction updates.
- **Harmonic series via telescoping**: The derivation builds E[n] recursively: E[n] = E[n-1] + 1/p_{n-1}, then expands to sum of 1/p_i, then substitutes p_i = (N-i)/N to get N * sum(1/k).
- **Bar chart for growth visualization**: Rectangles with width = (range/count) and height = 0.1*coupon(i), colored RED->BLUE gradient, showing E[n] for n=0,4,8,...,76.

## Composition

- **Card images**: 4 ImageMobjects at 5,2,-2,-5 LEFT, scaled 1.5, shifted 1*UP, plus "..." ellipsis
- **Brace for N**: Full-width Brace under cards, label "N" colored TEAL
- **Tree diagram**: TreeMobject([1, 2]) scaled 3x, shifted 4*LEFT, with H/T labels
- **Expected value labels**: x_i, p_i values at 1*UP/DOWN + 1*RIGHT, scale=1
- **Coupon rows**: 5 NumberedCoupons scaled 0.5, spaced 1.5 units apart at 2.5*UP (Don't Have) and center (Have)
- **Probability equation**: scale=1.5, at 2.5*DOWN
- **Bar chart**: Rectangles from x=-6 to x=6, shifted 1*UP, height = 0.1*coupon(n)

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| N (total coupons) | TEAL | tex_to_color_map |
| Expected value E | GOLD | tex_to_color_map |
| Variable x | TEAL or BLUE | tex_to_color_map |
| Probability p | GREEN or TEAL | tex_to_color_map |
| Coupon numbers (don't have) | YELLOW | NumberedCoupon default |
| Coupon numbers (have) | GREEN | NumberedCoupon color param |
| P(new coupon) | TEAL | tex_to_color_map |
| "new coupon" text | ORANGE | tex_to_color_map |
| Numerator highlight | GOLD | eq[-2].set_color(GOLD) |
| Boxed result | YELLOW | BackgroundRectangle stroke_width=4 |
| Harmonic number H | PURPLE | tex_to_color_map |
| Bar chart bars | RED->BLUE gradient | set_color_by_gradient |
| Dice dots | WHITE | Circle fill_opacity=1, radius=0.1 |
| Dice border | WHITE | Rectangle height=2, width=2 |
| Tails probability | RED->ORANGE gradient | set_color_by_gradient |
| Heads probability | YELLOW->GOLD | set_color |
| Bernoulli bullets | Default | dot_scale_factor=5 |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Dice roll | ~2s | Accelerating wait times |
| Coupon transfer | ~1s each | Transform(have[i], dont[i]) |
| Probability update | ~1s | Transform(eq1[-2], eq[-2]) |
| Equation chain | ~1s each | 7 telescoping steps |
| Bar chart | Write ~2s | All bars at once |
| Total | ~4 minutes | 11 scenes |

## Patterns

### Pattern: RollingDice Custom Mobject with Animation

**What**: A VGroup with a Rectangle border and a `dots` VGroup that changes configuration. `set_value(n)` calls one(), two()...six() which clear dots and add Circles at fixed positions for each face. The rolling animation uses decreasing wait times (t starts at 0.01, doubles each frame) so the dice appears to decelerate naturally.

**When to use**: Probability demonstrations, gambling simulations, random variable visualization, any dice-based game or experiment. The acceleration pattern is reusable for any "slot machine" or "spinning wheel" effect.

```python
# Source: projects/vivek3141_videos/coupon.py:323-445
class RollingDice(VGroup):
    def __init__(self, *args, **kwargs):
        VGroup.__init__(self, *args, **kwargs)
        rect = Rectangle(height=2, width=2)
        self.dots = VGroup()
        self.add(self.dots, rect)

    def set_value(self, value):
        if value == 1: self.one()
        elif value == 2: self.two()
        # ... etc

    def four(self):
        self.remove(self.dots)
        self.dots = VGroup()
        self.dots.add(
            Circle(radius=0.1, fill_opacity=1, color=WHITE).shift([-0.45, 0.45, 0]),
            Circle(radius=0.1, fill_opacity=1, color=WHITE).shift([0.45, -0.45, 0]),
            Circle(radius=0.1, fill_opacity=1, color=WHITE).shift([0.45, 0.45, 0]),
            Circle(radius=0.1, fill_opacity=1, color=WHITE).shift([-0.45, -0.45, 0]))
        self.add(self.dots)

# Rolling animation with deceleration
def roll(self, value=None, time=2, a=2):
    value = random.randint(1, 6) if value is None else value
    t = 0.01
    while t < time:
        v = random.randint(1, 6)
        self.d.set_value(v)
        self.wait(t)
        t *= a
    self.d.set_value(value)
```

### Pattern: SVG-Wrapped Numbered Element

**What**: An SVG icon (coupon shape) with a colored Tex number overlaid. The SVG is loaded, rotated, and set to low opacity as a background shape. The number is positioned slightly above center. This creates a recognizable domain-specific visual element that can be arranged in rows.

**When to use**: Card collecting problems, inventory displays, ticket/coupon visualizations, any scenario where you need a distinctive icon with a changeable label.

```python
# Source: projects/vivek3141_videos/coupon.py:487-500
class NumberedCoupon(VGroup):
    def __init__(self, number, color=YELLOW, *args, **kwargs):
        VGroup.__init__(self, *args, **kwargs)
        coupon = SVGMobject("./img/coupon.svg", stroke_width=2)
        coupon.rotate(-PI/2)
        coupon.set_opacity(0.5)
        coupon.set_stroke(opacity=0.5)
        n = TexMobject(number, color=color)
        n.scale(2)
        n.shift(0.4 * UP)
        self.add(coupon, n)
```

### Pattern: Telescoping Derivation via Recursive Expansion

**What**: An expected value equation E[n] = E[n-1] + 1/p_{n-1} is expanded recursively by substituting for E[n-1], E[n-2], etc. Each expansion step is shown via Transform. The viewer watches the recursive structure unfold into a sum, which then simplifies to N*H_N. The final boxed result uses BackgroundRectangle.

**When to use**: Any recursive formula derivation, telescoping series proofs, dynamic programming recurrence explanations, harmonic series construction. The pattern of expanding a recurrence visually is broadly applicable.

```python
# Source: projects/vivek3141_videos/coupon.py:617-673
eq7 = TexMobject(r"E[n] = E[n-1] + {{1} \over {p_{n-1}}",
                 tex_to_color_map={r"n": YELLOW, r"E": GOLD})
eq7.scale(1.5)
self.play(Write(eq7))

# Expand: E[n] = E[n-2] + 1/p_{n-1} + 1/p_{n-2}
eq8 = TexMobject(r"E[n] = E[n-2] + \frac{1}{p_{n-1}}",
                 r"+ \frac{1}{p_{n-2}}", ...)
self.play(Transform(eq7, eq8))

# ... continue expanding until ...

# Final: E[n] = N * H_N
eq13 = TexMobject(r"E[n] = N \cdot H_N",
    tex_to_color_map={r"n": YELLOW, r"E": GOLD,
                      r"N": GREEN, r"H": PURPLE})
self.play(Transform(eq7, eq13))
rect = BackgroundRectangle(eq13, buff=0.2, color=YELLOW,
    stroke_opacity=1, fill_opacity=0, stroke_width=4)
self.play(Write(rect))
```

## Scene Flow

1. **Intro** (0-15s): Card images (1-4 + ...). Brace labeled N. "How many draws to get all N cards?" -> "Expected value of number of draws."
2. **ExpectedValue** (15-35s): Tree diagram (H/T) with x*p labels. Sum = 2.5. E[x] = sum(x_i * p_i) formula boxed.
3. **Tails** (35-40s): (1/2)(1/2)(1/2) = 1/8. Braces label "tails" and "heads."
4. **Bernoulli** (40-50s): Three properties of Bernoulli trial. BulletedList with fade_all_but.
5. **ExpectBern** (50-55s): Rolling dice animation. Decelerating random faces.
6. **DiceExp** (55-65s): E[x] = 1/p. For dice: p = 1/6, so E[x] = 6. Boxed.
7. **CouponCalc** (65-90s): 5 coupons. Probability decreases 5/5, 4/5, 3/5... as coupons collected. p_i = (N-i)/N. E[i-th new] = N/(N-i). Telescoping derivation: E[n] = N*H_N. Boxed.
8. **Asymptote** (90-100s): Bar chart of E[n] = N*coupon(N) for N=0 to 76, step 4. RED->BLUE gradient bars.

> Full file: `projects/vivek3141_videos/coupon.py` (708 lines)
