---
source: https://github.com/vivek3141/videos/blob/main/prime.py
project: vivek3141_videos
domain: [mathematics, number_theory, complex_analysis, calculus]
elements: [axes, function_plot, equation, label, number_line, dot, line, arrow, formula]
animations: [write, fade_in, transform, draw]
layouts: [centered, dual_panel, vertical_stack]
techniques: [algorithm_class_separation, progressive_disclosure, scipy_integration, data_driven]
purpose: [derivation, proof, step_by_step, exploration]
mobjects: [Axes, FunctionGraph, TexMobject, TextMobject, VGroup, SVGMobject, Circle, Line, Rectangle, Arrow]
manim_animations: [Write, Transform, TransformFromCopy, FadeInFromDown, ShowCreation, Uncreate, ApplyMethod]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 1186
scene_classes: [IntroQuote, Intro, Money, PartOneTitle, Factorization, EuclidTheorem, PartTwoTitle, Series, EulerProductFormula, PartThreeTitle, PrimeFunc]
---

## Summary

Visualizes the distribution of prime numbers through the Prime Number Theorem and Riemann Hypothesis. Separates algorithm logic (PrimeMethods mixin) from scene rendering. Key visual techniques include: progressive equation transformation chains showing algebraic derivations (Euler product formula built in 7 steps), proof visualization using bullet points with colored variables, and function plotting for pi(x) vs x/ln(x). Uses scipy.special.expi and mpmath for Riemann zeta zero computations.

## Design Decisions

- **Mixin class for computation**: `PrimeMethods` contains all math (isPrime, count_prime, li, riemann_count) as a mixin class, keeping scene code focused on visuals. The scene inherits from both `Scene` and `PrimeMethods`.
- **PartScene pattern for chapter titles**: Reusable base class with CONFIG dict for part number, title text, and subtitle. Each chapter (Euclid's Theorem, Euler Product, PNT) gets a title card with consistent formatting.
- **7-step equation chain for Euler Product**: The derivation is shown as a chain of Transform animations, each step building on the previous. This mirrors chalkboard mathematics and lets the viewer follow the algebraic manipulation.
- **Color-coded variables in proofs**: tex_to_color_map assigns consistent colors: P=YELLOW, Q=PURPLE, p=RED throughout the Euclid's Theorem proof. This visual tracking helps viewers follow variable references.
- **Bullet points with blue dots for proof steps**: Euclid's proof uses blue filled circles as bullet markers with if/then branching, mimicking a structured proof layout.

## Composition

- **Quote scenes**: TextMobject centered, author shifted `1 * DOWN + 1 * RIGHT`, author colored YELLOW
- **Title cards**: Part number at `1.5 * UP`, title text centered, subtitle at `1.5 * DOWN`
- **Proof layout**: Title at `3 * UP` (scale 2/3 after animation), horizontal line at `3 * UP`, proof steps stacked vertically with 1-unit spacing
- **Function plots**: Axes with variable ranges, functions overlaid, labels positioned with `.move_to()`
- **Equation chains**: Each equation centered at ORIGIN, scale=1.5, transformed sequentially

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Part titles | PURPLE | PartScene title_color |
| Chapter titles | BLUE/YELLOW/GREEN | Varies per chapter |
| Variable P | YELLOW | Product of primes |
| Variable Q | PURPLE | P + 1 |
| Variable p | RED | Prime factor |
| Proof bullets | BLUE | Circle(fill_opacity=1, radius=0.1) |
| Zeta function | WHITE | Default |
| Exponent s | YELLOW | In tex_to_color_map |
| Boxed result | YELLOW | Rectangle(height=3, width=10) |
| Series equations | WHITE | scale=1.5 |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Equation Transform | ~1s default | Each step in chain |
| wait() between steps | default | Standard pacing |
| Write (title) | ~1s | Title cards |
| Write (proof steps) | ~1s each | Sequential |
| Total per scene | ~20-40s | Varies |

## Patterns

### Pattern: Mixin Class for Algorithm Separation

**What**: A standalone class `PrimeMethods` containing all mathematical computations (prime counting, logarithmic integral, Riemann zeta zeros). Scene classes inherit from both `Scene` and `PrimeMethods`, giving clean separation between computation and visualization. The mixin uses scipy and mpmath for heavy math.

**When to use**: Any visualization where the math is nontrivial -- number theory computations, statistical distributions, numerical integration, ODE solvers. Keeps the construct() method focused on animation logic.

```python
# Source: projects/vivek3141_videos/prime.py:8-71
class PrimeMethods:
    def count_prime(self, x):
        counter = 0
        for i in range(2, int(x) + 1):
            if self.isPrime(i):
                counter += 1
        return counter

    def li(self, x):
        return expi(math.log(x))

    def riemann_count(self, x, num_zeros=35):
        return float(self.single_pi(x, num_zeros, "zeros.txt"))

# Usage in scene:
class PrimeFunc(Scene, PrimeMethods):
    def construct(self):
        count = self.count_prime(100)  # Direct access to math
```

### Pattern: Multi-Step Equation Derivation Chain

**What**: A sequence of equations shown one after another using Transform, each building on the previous. The viewer watches an algebraic derivation unfold step by step. Each equation is at scale=1.5 and centered. The final result gets a colored Rectangle border and a title label.

**When to use**: Algebraic proofs, derivations in calculus or physics, step-by-step simplification of expressions, building up to a famous result (Euler product, quadratic formula, etc.).

```python
# Source: projects/vivek3141_videos/prime.py:304-361
# Euler Product Formula in 7 steps
eq1 = TexMobject(r"\zeta(s) = 1 + \frac{1}{2^s} + ...").scale(1.5)
eq2 = TexMobject(r"\frac{1}{2^s} \zeta(s) = ...").scale(1.5)
# ... eq3 through eq6 ...
eq7 = TexMobject(
    r"\sum_{n \in \mathbb{N}} \frac{1}{n^s} = "
    r"\prod_{p \text{ prime}} \frac{1}{1-p^{-s}}")
eq7.scale(1.5)

self.play(Write(eq1))
self.wait()
for eq in [eq2, eq3, eq4, eq5, eq6, eq7]:
    self.play(Transform(eq1, eq))
    self.wait()

box = Rectangle(height=3, width=10, color=YELLOW)
text = TextMobject("Euler Product Formula", color=GREEN)
text.shift(3 * UP).scale(1.5)
self.play(Write(box), Write(text))
```

### Pattern: Reusable PartScene Title Card

**What**: A base class with CONFIG dict for generating consistent chapter title cards. Each part has a number, title, and optional subtitle (which can contain LaTeX). Subclasses only need to set CONFIG values.

**When to use**: Multi-part educational videos, lecture series, any video with distinct chapters or sections that need consistent title formatting.

```python
# Source: projects/vivek3141_videos/prime.py:73-101
class PartScene(Scene):
    def construct(self):
        grp = VGroup()
        if hasattr(self, 'num'):
            title = TextMobject(f"Part {str(self.num)}", color=PURPLE)
            title.scale(1.5).shift(1.5 * UP)
            grp.add(title)
        if hasattr(self, 'text'):
            text = TextMobject(self.text).scale(2)
            grp.add(text)
        if hasattr(self, 'subt'):
            subt = TextMobject(self.subt).shift(1.5 * DOWN)
            grp.add(subt)
        self.play(Write(grp))

class PartTwoTitle(PartScene):
    CONFIG = {
        "num": 2,
        "text": "The Euler Product Formula",
        "subt": r"$$\sum_{n} \frac{1}{n^s} = \prod_{p} \frac{1}{1-p^{-s}}$$"
    }
```

## Scene Flow

1. **IntroQuote** (0-5s): R.C. Vaughan quote about primes being random. White text, yellow author name.
2. **Intro** (5-10s): "Continue the Following Sequence: 2, 3, 5, 7, 11, 13, 17, 19, ..."
3. **Part 1: Euclid's Theorem** (10-40s): Title card. Statement. Proof by contradiction with bullet points: let P = product of all primes, Q = P+1, case analysis.
4. **Part 2: Euler Product** (40-80s): Harmonic series intro. Generalize to zeta function. 7-step derivation of Euler product formula. Yellow box around final result.
5. **Part 3: PNT** (80-120s): Prime counting function pi(x). Compute pi(5), pi(10), pi(20). Plot pi(x) vs x/ln(x). Convergence to 1.

> Full file: `projects/vivek3141_videos/prime.py` (1186 lines, first 400 documented)
