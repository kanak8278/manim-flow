---
source: https://github.com/adamisntdead/how-sound-works/blob/main/scenes/title.py, https://github.com/adamisntdead/how-sound-works/blob/main/scenes/definition_of_sound.py, https://github.com/adamisntdead/how-sound-works/blob/main/scenes/guitar_string.py, https://github.com/adamisntdead/how-sound-works/blob/main/scenes/travels.py, https://github.com/adamisntdead/how-sound-works/blob/main/scenes/frequency.py, https://github.com/adamisntdead/how-sound-works/blob/main/scenes/outro.py
project: how-sound-works
domain: [physics, acoustics, waves]
elements: [title, label, function_plot, axes, dot, arrow, speaker, wave, svg_icon]
animations: [write, fade_in, fade_out, transform, lagged_start, indicate]
layouts: [centered, edge_anchored, vertical_stack]
techniques: [svg_integration, custom_animation]
purpose: [definition, demonstration, overview, progression]
mobjects: [TextMobject, SVGMobject, ScreenRectangle, GraphScene, VGroup, Dot, Arrow, Line]
manim_animations: [Write, FadeIn, FadeOut, ShowCreation, Transform, Broadcast, GrowArrow, FadeInAndShiftFromDirection]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 217
scene_classes: [Title, Definition, String, Demo, IntroToSound, Frequency, Covered]
---

## Summary

A six-scene educational explainer about how sound works, covering definition, vibration creation via a guitar string, wave propagation with a speaker SVG broadcasting concentric rings, and frequency visualization comparing 440Hz vs 880Hz sine waves. Uses manimlib's older API (TextMobject, GraphScene, CONFIG dict, Broadcast animation). The outro uses an opacity-based highlight pattern to review covered topics.

## Design Decisions

- **TextMobject with tex_to_color_map**: Key vocabulary words ("Sound", "vibrations", "heard", "waves") are color-coded inline to draw attention without separate labels.
- **GraphScene CONFIG for string vibration**: Uses cosine oscillation between positive and negative curves to simulate a guitar string vibrating, with 15 rapid back-and-forth Transform cycles at 0.5s each.
- **SVGMobject speaker with Broadcast animation**: The speaker icon emits concentric expanding rings (n_circles=10), a manimlib-specific animation that visually represents sound wave propagation.
- **Frequency comparison via Transform**: Rather than showing two separate graphs, the 440Hz sine wave Transforms into the 880Hz sine wave on the same axes, making the frequency doubling immediately visible.
- **Opacity-based topic highlighting in outro**: Each topic in a bullet list gets opacity=1 while others dim to 0.25, creating a spotlight effect that guides viewer attention through a recap.

## Composition

- **Title scene**: TextMobject scaled to 2x, centered at ORIGIN.
- **Definition scene**: TextMobject scaled to 2x, constrained to `FRAME_WIDTH - 1` to prevent overflow.
- **Guitar string**: Title at `to_edge(UP)`, ScreenRectangle(height=4) centered below. GraphScene with x_range=[-pi/2, pi/2], y_range=[-10, 10], graph_origin=ORIGIN.
- **Speaker scene**: SVGMobject centered at ORIGIN, "Gas Molecules" arrow at position (3, -2, 0) to (3, 0, 0).
- **Frequency graph**: GraphScene x_range=[-4pi, 4pi], y_range=[-2, 2], axes_color=BLUE. Title "440Hz"/"880Hz" at `to_edge(UP)`.
- **Outro topics**: VGroup arranged `DOWN, aligned_edge=LEFT, buff=MED_LARGE_BUFF`, each with a BLUE dot to the LEFT.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| "Sound" in title | BLUE | tex_to_color_map |
| "vibrations" | RED | tex_to_color_map |
| "heard" | GREEN | tex_to_color_map |
| "waves" | RED | tex_to_color_map |
| Guitar string graph | BLUE | function_color in CONFIG |
| Guitar axes | BLACK | Hidden against black background |
| Speaker SVG | default, opacity=0.8 | |
| "Gas Molecules" arrow | RED | |
| Frequency axes | BLUE | |
| Frequency graph | WHITE | |
| "440Hz"/"880Hz" | RED | tex_to_color_map |
| Outro dots | BLUE | Dot next_to topic LEFT |
| Dimmed topics | opacity=0.25 | Highlight pattern |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=3 | |
| Definition FadeIn | run_time=5 | lagged_start, lag_factor=4 |
| Guitar string cycle | run_time=0.5 each | 15 cycles = 15s oscillation |
| Broadcast | run_time=5 | 10 concentric circles |
| Frequency graph ShowCreation | default | |
| 440Hz to 880Hz Transform | default | Simultaneous with title transform |
| Outro topic highlight | default per step | wait(2) between each |
| Total video | ~90 seconds estimate | |

## Patterns

### Pattern: Broadcast Wave Animation from SVG Speaker

**What**: Uses manimlib's Broadcast animation to emit concentric expanding circles from an SVG speaker icon, simulating sound wave propagation. The speaker's second sub-element (index [1]) is used as the broadcast source point.

**When to use**: Sound wave visualizations, radio signal propagation, any radial emission from a source point. Physics animations showing wave fronts expanding outward from an oscillator or speaker.

```python
# Source: projects/how-sound-works/scenes/travels.py:17-50
speaker = SVGMobject(file_name="speaker")
speaker.set_fill(opacity=0.8)

def broadcast(self, **kwargs):
    kwargs["run_time"] = kwargs.get("run_time", 5)
    kwargs["n_circles"] = kwargs.get("n_circles", 10)
    self.play(Broadcast(self.speaker[1], **kwargs))
```

### Pattern: Rapid Transform Oscillation for Vibration

**What**: Alternates Transform between a positive and negative curve form 15 times at 0.5s intervals to simulate a vibrating string. The graph starts at zero, oscillates, then returns to zero.

**When to use**: Vibrating strings, oscillating springs, any physical system that alternates between two states rapidly. Physics simulations where you need to show periodic motion without parametric animation.

```python
# Source: projects/how-sound-works/scenes/guitar_string.py:47-51
for _ in range(15):
    self.play(Transform(func_graph, self.get_graph(self.function_opposite, self.function_color)), run_time=0.5)
    self.play(Transform(func_graph, self.get_graph(self.function, self.function_color)), run_time=0.5)

self.play(Transform(func_graph, self.get_graph(lambda x: 0, self.function_color)))
```

### Pattern: Opacity-Based Topic Spotlight

**What**: Iterates through a VGroup of text items, setting the current item to full opacity and all others to 0.25, creating a sequential highlight effect for reviewing a list of topics.

**When to use**: Recap or summary scenes, table of contents highlighting, stepping through a bulleted list to review what was covered. Any sequential emphasis on list items.

```python
# Source: projects/how-sound-works/scenes/outro.py:21-29
for i in range(len(topics)):
    self.play(
        topics[i + 1:].set_fill, {"opacity": 0.25},
        topics[:i].set_fill, {"opacity": 0.25},
        topics[i].set_fill, {"opacity": 1},
    )
    self.wait(2)
self.play(topics.set_fill, {"opacity": 1})
```

### Pattern: Frequency Comparison via Graph Transform

**What**: Shows a sine wave at one frequency, then Transforms it into a higher frequency sine wave on the same axes. The graph title also transforms simultaneously ("440Hz" to "880Hz"), then zooms the text to fill screen for emphasis.

**When to use**: Comparing two function variations on the same domain, frequency doubling demonstrations, any side-by-side-on-same-axes comparison where Transform makes the difference visible.

```python
# Source: projects/how-sound-works/scenes/frequency.py:36-54
graph_title_2 = TextMobject("880Hz", tex_to_color_map={"880Hz": RED})
graph_title_2.to_edge(UP)
func_graph_2 = self.get_graph(self.func_to_graph2, self.function_color)

self.play(Transform(graph_title, graph_title_2), Transform(func_graph, func_graph_2))
self.wait(3)
self.play(FadeOut(func_graph), FadeOut(self.x_axis), FadeOut(self.y_axis))

# Zoom text to center for emphasis
new = graph_title_2
new.scale(3)
new.center()
self.play(Transform(graph_title, new))
```

## Scene Flow

1. **Title** (0-8s): "How Does Sound Work?" writes in with "Sound" in BLUE. Holds 5s, fades out.
2. **Definition** (8-16s): Sound definition text fades in with lagged_start character-by-character reveal. "vibrations" in RED, "heard" in GREEN.
3. **Guitar String** (16-38s): "A Guitar String" title writes at top. ScreenRectangle appears as placeholder. GraphScene shows flat line, then 15 oscillation cycles (cos/-cos) at 0.5s each, returns to flat.
4. **Sound Travels** (38-58s): Speaker SVG fades in. Broadcasts 4 rounds of concentric rings. "Gas Molecules" label with arrow appears and disappears between broadcasts.
5. **Frequency** (58-82s): Axes animate in. 440Hz sine wave draws. Transforms to 880Hz. Axes fade. "880Hz" zooms to center, transforms through "Hz" to "Hertz".
6. **Outro** (82-100s): Four bullet points appear with blue dots. Each topic highlights sequentially (others dim to 0.25 opacity). All restore to full opacity.
