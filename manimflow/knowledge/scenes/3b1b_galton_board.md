---
source: https://github.com/3b1b/videos/blob/main/_2023/clt/galton_board.py
project: 3blue1brown
domain: [probability, statistics, combinatorics, mathematics]
elements: [dot, sphere, grid, label, equation, formula, arrow, bar_chart]
animations: [write, fade_in, fade_out, move, stagger, lagged_start, flash, color_change]
layouts: [grid, centered, vertical_stack]
techniques: [custom_mobject, custom_animation, helper_function, data_driven, progressive_disclosure]
purpose: [simulation, demonstration, step_by_step, distribution, proof]
mobjects: [Dot, TrueDot, Sphere, VGroup, Group, VMobject, OldTex, Text, Integer, Vector, FunctionGraph, ParametricCurve, Line]
manim_animations: [Write, FadeIn, FadeOut, LaggedStartMap, MoveAlongPath, TransformFromCopy, FadeTransformPieces, ReplacementTransform, Succession]
scene_type: InteractiveScene
manim_version: manimlib
complexity: intermediate
lines: 400
scene_classes: [GaltonBoard]
---

## Summary

Simulates a Galton board (bean machine) with 3D-rendered balls bouncing through rows of pegs into buckets. Each bounce is a +1 or -1 step (50/50), and the final bucket position equals the sum of all steps. Builds from single step-by-step trajectories with labeled +/-1 arrows to flurries of 250 balls forming a binomial distribution. Overlays Pascal's triangle probabilities on the peg positions, connecting the physical simulation to combinatorial mathematics.

## Design Decisions

- **3D ball rendering**: Uses `TrueDot` with `make_3d()` and shading (0.5, 0.5, 0.2) for physical realism. YELLOW_E color evokes a classic brass/wooden ball machine.
- **Parabolic bounce trajectories**: Each bounce follows a `FunctionGraph(lambda x: -x*(x-1))` stretched to connect adjacent peg positions, creating natural-looking ballistic arcs.
- **+1/-1 arrows as binary choices**: Red LEFT and Blue RIGHT arrows appear at each peg, with the unchosen arrow dimmed to 0.25 opacity. This makes the binary nature explicit.
- **Corner sum accumulation**: Selected +/-1 labels are copied and arranged in the top-left corner, summed to show the final bucket value. Connects individual choices to the aggregate outcome.
- **Pascal's triangle probability labels**: Fractions like `k choose n / 2^n` placed at each peg position, built step-by-step with split/merge animations showing the addition rule.
- **Bucket sum labels**: Each bucket labeled with its net sum (e.g., -5 to +5), connecting the physical position to the mathematical value.
- **Sound effects**: Clink sounds on each peg hit for physical feedback.

## Composition

- **Pegs**: `pegs_per_row=15` dots, `n_rows=5`, spacing=1.0, peg_radius=0.1. Odd rows offset by 0.5*spacing LEFT. Centered, to_edge(UP, buff=1.0).
- **Buckets**: Constructed from VMobject corners, width=0.5*spacing - ball_radius. Floor tracked by `bucket.bottom` VectorizedPoint.
- **Ball**: TrueDot, radius=0.1, YELLOW_E
- **+/-1 arrows**: Vector(0.5*spacing), tip_width_ratio=3, RED(left)/BLUE(right), label font_size=28
- **Probability labels**: font_size=16-24, positioned at peg centers
- **Sum labels**: Integer with include_sign=True, font_size=24, below buckets

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Pegs | GREY_C | fill_opacity=1, shading=(0.5, 0.5) |
| Ball | YELLOW_E | TrueDot, make_3d, shading=(0.5, 0.5, 0.2) |
| Left arrow (-1) | RED | Vector, stroke_color |
| Right arrow (+1) | BLUE | Vector, stroke_color |
| Dimmed arrow | 0.25 opacity | Unchosen direction |
| Bucket walls | GREY_D | fill_opacity=1, stroke_width=0 |
| Bucket floor | GREY_D | Line, stroke_width=1 |
| Sum labels | WHITE | stroke_width=1 |
| Probability labels | default | Tex, font_size=16-24 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Peg/bucket write | default | LaggedStartMap |
| Ball falling per bounce | `fall_factor * arc_length` | fall_factor=0.6, rate_func=linear |
| Arrow fade in | default | FadeIn with lag_ratio=0.1 |
| Arrow dim | default | animate set_opacity(0.25) |
| Corner sum | Succession | MoveToTarget then sum appear |
| Initial flurry | 25 balls | With sound effects |
| Final flurry | 250 balls | stack_ratio=0.125 for tight packing |

## Patterns

### Pattern: Parabolic Bounce Trajectory Between Pegs

**What**: Creates a FunctionGraph with a parabolic arc `(-x*(x-1))` stretched and positioned to connect a peg's top to the next peg position (left or right depending on the random bit). The ball moves along this path with `MoveAlongPath` at linear rate.

**When to use**: Any physics simulation with ballistic trajectories, bouncing ball animations, pinball machines, particle systems with gravity-like arcs between collision points.

```python
# Source: projects/videos/_2023/clt/galton_board.py:328-341
def single_bounce_trajectory(self, ball, peg, direction):
    sgn = np.sign(direction[0])
    trajectory = FunctionGraph(lambda x: -x * (x - 1), x_range=(0, 2, 0.2))
    p1 = peg.get_top()
    p2 = p1 + self.spacing * np.array([sgn * 0.5, -0.5 * math.sqrt(3), 0])
    vect = trajectory.get_end() - trajectory.get_start()
    for i in (0, 1):
        trajectory.stretch((p2 - p1)[i] / vect[i], i)
    trajectory.shift(p1 - trajectory.get_start() + 0.5 * ball.get_height() * UP)
    return trajectory
```

### Pattern: Binary Choice Arrows with Dim/Highlight

**What**: At each peg, two arrows (left=-1, right=+1) appear with 50% probability labels. After the random choice, the unchosen arrow dims to 0.25 opacity, visually encoding the path taken. Arrows accumulate in a corner for the final sum.

**When to use**: Binary decision trees, random walk step-by-step, A/B choice visualizations, coin flip sequences, any scenario where binary outcomes need to be tracked visually.

```python
# Source: projects/videos/_2023/clt/galton_board.py:288-292
def get_pm_arrows(self, ball, show_prob=True):
    return self.get_ball_arrows(
        ball, ["$-1$", "$+1$"],
        sub_labels=(["50%", "50%"] if show_prob else [])
    )
# Usage: pm_arrows[1 - bit].animate.set_opacity(0.25)
```

### Pattern: Pascal's Triangle Probability Build-Up

**What**: At each row of pegs, probability labels are built by showing the split (two parent fractions) then merging into the combined fraction. Uses `TransformFromCopy` for parent-to-child and `FadeTransformPieces` for split-to-merged transitions.

**When to use**: Pascal's triangle constructions, binomial coefficient demonstrations, recursive probability calculations, any tree-structured quantity that sums from parents.

```python
# Source: projects/videos/_2023/clt/galton_board.py:173-189
for n in range(1, self.n_rows + 1):
    split_labels = VGroup(*(get_peg_label(n, k, split=True) for k in range(n + 1)))
    unsplit_labels = VGroup(*(get_peg_label(n, k, split=False) for k in range(n + 1)))
    anims = [TransformFromCopy(last_labels[0], split_labels[0]),
             TransformFromCopy(last_labels[-1], split_labels[-1])]
    for k in range(1, n):
        anims.append(TransformFromCopy(last_labels[k - 1], split_labels[k][0]))
        anims.append(TransformFromCopy(last_labels[k], split_labels[k][1]))
    self.play(*anims)
    self.play(*(FadeTransformPieces(s, u) for s, u in zip(split_labels, unsplit_labels)))
```

### Pattern: Bucket Stacking with Bottom Tracker

**What**: Each bucket tracks a `bottom` VectorizedPoint that shifts upward by `2 * ball_radius * stack_ratio` each time a ball lands, naturally stacking balls. The bucket also maintains a `balls` Group for cleanup.

**When to use**: Any accumulation visualization: histogram bins filling up, stacking objects, resource pools, voting tallies, any scenario where items pile up in discrete containers.

```python
# Source: projects/videos/_2023/clt/galton_board.py:360-367
bucket = buckets[index]
final_line = Line(
    bounces[-1].get_end(),
    bucket.bottom.get_center() + self.ball_radius * UP
)
bucket.bottom.shift(2 * self.ball_radius * self.stack_ratio * UP)
bucket.balls.add(ball)
```

## Scene Flow

1. **Setup** (0-5s): Pegs and buckets written with LaggedStartMap.
2. **Initial flurry** (5-15s): 25 balls dropped with clink sounds, forming a rough distribution. Then cleared.
3. **Step-by-step single ball** (15-60s): One ball bounces through pegs. At each peg, +/-1 arrows appear, choice is made (unchosen dims), ball follows parabolic arc with clink sound. All arrows accumulated in corner with running sum.
4. **Bucket sum labels** (60-75s): Sum labels (-5 to +5) placed below buckets.
5. **More trajectories** (75-120s): 3 more balls with abbreviated step-by-step, each showing corner sum.
6. **Flurry + fade periphery** (120-150s): 25 more balls. Peripheral pegs and buckets fade to 0.25 opacity, focusing on central triangle.
7. **Pascal's triangle** (150-210s): Probability fractions built row-by-row at peg positions, showing split/merge addition rule.
8. **Large flurry** (210-240s): 250 balls with stack_ratio=0.125, filling buckets to show binomial distribution shape.
