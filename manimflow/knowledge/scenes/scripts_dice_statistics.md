---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/dice_statistics_example.py
project: manim-scripts
domain: [probability, statistics, mathematics]
elements: [bar_chart, dot, label, axes]
animations: [rotate, replacement_transform, indicate, fade_in, fade_out, write, draw]
layouts: [centered, vertical_stack]
techniques: [data_driven, helper_function]
purpose: [simulation, distribution, demonstration]
mobjects: [VGroup, Text, MathTex, BarChart, Dot]
manim_animations: [Write, FadeIn, FadeOut, Rotate, ReplacementTransform, Indicate, Create]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 123
scene_classes: [DiceStatisticsScene]
---

## Summary

Simulates rolling two dice 16 times with animated dice face replacements, tracks sum frequencies, then displays results as a BarChart. Each roll animates dice rotation, face replacement via ReplacementTransform, sum update, and Indicate highlight. After all rolls, dice fade out and a labeled bar chart of sum frequencies (2-12) appears. Uses the shared `get_diceface()` factory from `manim_utils.py`.

## Design Decisions

- **ReplacementTransform for dice face update**: Creates a new dice face mobject at the old position, then transforms. This ensures clean state — no leftover dots from previous face values.
- **Rotation before replacement**: A full 2*PI rotation on each die before showing the new face simulates the "tumbling" of a dice roll. The rotation is purely decorative but adds physicality.
- **Indicate on sum text**: After each roll, the sum text briefly scales up and turns YELLOW to draw attention to the new value. Quick (0.3s) so it does not slow the simulation.
- **BarChart for frequency display**: Manim's built-in BarChart with dynamic y_range based on actual max frequency. Adaptive y_range_step prevents cluttered axis labels when frequencies are high.
- **Sequential rolls (not batch)**: Each roll is individually animated. This is slower but educational — the viewer sees the distribution build up roll by roll.

## Composition

- **Screen regions**:
  - Title: to_edge(UP), font_size=48
  - Dice pair: next_to(title, DOWN, buff=0.5), arranged RIGHT with buff=1, scale=0.8
  - Sum text: next_to(dice_group, DOWN, buff=0.5), font_size=40
  - Bar chart: next_to(chart_title, DOWN, buff=0.5), x_length=10, y_length=5
- **Axis labels**: font_size=30, "Sum of Dice" (x), "Frequency" (y, rotated 90 degrees)
- **Bar chart config**: bar_names=["2".."12"], bar_colors=[BLUE, GREEN, YELLOW, ORANGE, RED] cycling

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Title | WHITE | font_size=48 |
| Sum text | WHITE | font_size=40 |
| Indicate flash | YELLOW | scale_factor=1.2, run_time=0.3 |
| Bar chart bars | BLUE, GREEN, YELLOW, ORANGE, RED | Cycling colors |
| Axis labels | WHITE | font_size=24-30 |
| Chart title | WHITE | font_size=36 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Dice rotation | run_time=0.5 | Full 2*PI per die |
| ReplacementTransform dice | Default | New face replaces old |
| Sum text ReplacementTransform | Default | Number update |
| Indicate sum | run_time=0.3 | YELLOW highlight |
| Wait between rolls | 0.5s | Pause for readability |
| Bar chart creation | Default | Create + Write labels |
| End wait | 3s | View final chart |
| Total video | ~30-40s | 16 rolls + chart |

## Patterns

### Pattern: Animated Dice Roll with ReplacementTransform

**What**: Simulate a dice roll by (1) rotating the current die mobject, (2) creating a new die face at the old position, (3) ReplacementTransform from old to new. The old mobject is fully replaced, avoiding state accumulation.
**When to use**: Any simulation with discrete state changes displayed as visual icons — dice, cards, slot machines, traffic lights, or any scenario where an icon needs to "flip" to a new state.

```python
# Source: projects/manim-scripts/scenes/dice_statistics_example.py:46-59
new_die1_mobject = get_diceface(new_die1_value).scale(0.8).move_to(die1_mobject.get_center())
new_die2_mobject = get_diceface(new_die2_value).scale(0.8).move_to(die2_mobject.get_center())
self.play(
    Rotate(die1_mobject, angle=PI*2, axis=OUT, run_time=0.5),
    Rotate(die2_mobject, angle=PI*2, axis=OUT, run_time=0.5),
)
self.play(
    ReplacementTransform(die1_mobject, new_die1_mobject),
    ReplacementTransform(die2_mobject, new_die2_mobject)
)
die1_mobject = new_die1_mobject  # Update reference
die2_mobject = new_die2_mobject
```

### Pattern: Live Frequency BarChart from Simulation

**What**: After running a simulation loop that accumulates frequencies in a dict, convert to a BarChart. Dynamic y_range adapts to actual max frequency. Bar names and values come directly from the frequency dict.
**When to use**: Histogram from simulation results, frequency distribution display, any scenario where data is accumulated over time and then summarized visually.

```python
# Source: projects/manim-scripts/scenes/dice_statistics_example.py:82-102
bar_values = [sum_frequencies[s] for s in range(2, 13)]
bar_names = [str(s) for s in range(2, 13)]
max_freq = max(bar_values) if any(bar_values) else 0
y_range_step = 2 if max_freq > 10 else 1

bar_chart = BarChart(
    values=bar_values,
    bar_names=bar_names,
    y_range=[0, max_freq + y_range_step, y_range_step],
    x_length=10, y_length=5,
    x_axis_config={"font_size": 24},
    y_axis_config={"font_size": 24},
    bar_colors=[BLUE, GREEN, YELLOW, ORANGE, RED]
).next_to(chart_title, DOWN, buff=0.5)
```

## Scene Flow

1. **Setup** (0-3s): Title "Dice Roll Statistics" writes. Two dice appear with initial random values. Sum displayed below.
2. **Rolling loop** (3-25s): 15 more rolls. Each: 0.5s wait, rotation animation, face replacement, sum update with Indicate.
3. **Transition to chart** (25-28s): Dice and sum fade out. "Sum Frequencies After 16 Rolls" title appears.
4. **Bar chart** (28-32s): BarChart creates with axis labels. 5-color cycling bars show distribution.
5. **End** (32-35s): Wait 3s on final chart.

> Full file: `projects/manim-scripts/scenes/dice_statistics_example.py` (123 lines)
