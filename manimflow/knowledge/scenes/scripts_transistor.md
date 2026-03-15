---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/transistor.py
project: manim-scripts
domain: [electronics, physics, electromagnetism]
elements: [circuit, resistor, battery, led, arrow, line, label, dot]
animations: [write, fade_in, fade_out, draw, passing_flash, indicate, color_change]
layouts: [centered, flow_left_right]
techniques: [custom_mobject, factory_pattern, helper_function, passing_flash_signal, color_state_machine]
purpose: [demonstration, step_by_step, process]
mobjects: [VGroup, Circle, Line, Arrow, Dot, Rectangle, Polygon, Ellipse, Text, MathTex, Tex, Cross, SurroundingRectangle]
manim_animations: [Write, FadeIn, FadeOut, Create, ShowPassingFlash, Indicate, LaggedStart, Succession, AnimationGroup, Rotate, Transform]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 326
scene_classes: [TransistorSwitchExplanation]
---

## Summary

A multi-scene narrative explaining how an NPN transistor works as a switch. Custom mobject factory methods build circuit components (NPN symbol, LED, battery, resistor) from geometric primitives with terminal attachment points. ShowPassingFlash animates current flow through wires. A five-scene structure progresses from title to OFF state, ON state, amplification concept, and summary with a blinking LED loop.

## Design Decisions

- **Custom mobject factories with terminal lambdas**: Each component (NPN, LED, battery, resistor) is built as a VGroup with lambda accessors like `get_collector_terminal()`, `get_base_terminal()`. This makes wiring trivial — just connect terminals without calculating positions manually.
- **ShowPassingFlash for current flow**: Current is visualized as a bright stroke flash traveling along wire paths. This avoids adding persistent arrows that clutter the circuit. The flash is transient — it shows flow direction without leaving visual residue.
- **Succession for sequential current path**: Main current flows through battery → resistor → LED → NPN → back to battery. Each segment gets its own ShowPassingFlash in a Succession, creating a continuous flow effect.
- **Color-coded current types**: Base current = YELLOW_C (small signal), main current = GREEN_B (large output). This directly supports the amplification concept — small yellow triggers large green.
- **Dark grey background (#2E2E2E)**: Circuit diagrams read better on dark grey than pure black. The grey provides enough contrast for white wires without the harshness of black.
- **Scene bundle pattern**: Each `_animate_sceneN_*` method returns a dict of created mobjects, allowing later scenes to reference and fade out elements from earlier scenes. Clean separation of scene logic.
- **Cross (X) for blocked state**: A red X on the NPN bar immediately communicates "no current flows here" — a universal symbol.

## Composition

- **Screen regions**:
  - NPN BJT: ORIGIN + RIGHT*0.5, scale=1.2
  - Battery: LEFT*4.5 + DOWN*0.5, scale=0.8
  - LED: NPN collector terminal + UP*2.0 + LEFT*0.2, scale=0.7
  - Resistor: next_to LED, LEFT, buff=0.5, scale=0.6
  - Status text: to_corner(UL, buff=0.5), font_size=24
  - Summary text: to_edge(UP, buff=1.0), font_size=32
- **Wire connections**: Line objects between terminal attachment points
- **Component labels**: font_size=20, positioned with next_to(component, DOWN/UP, buff=0.3)

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | #2E2E2E | Dark grey |
| Title text | WHITE | font_size=48 |
| Subtitle/annotations | GREY_B | font_size=28 |
| NPN symbol | BLUE_D | stroke_width=3 |
| C/B/E labels | WHITE | MathTex, label_scale=0.5-0.6 |
| Wires | GREY_A | Line objects |
| LED off | GREY_C | fill_opacity=0.7 |
| LED on | GREEN_C | fill_opacity=0.8 |
| Battery plates | WHITE | stroke_width varies with scale |
| Resistor | WHITE | Rectangle + wire leads |
| Blocked state | RED_D | Cross overlay |
| Base current flash | YELLOW_C | stroke_width=5 |
| Main current flash | GREEN_B | stroke_width=7-8 |
| Off state text | YELLOW_C | font_size=24 |
| On state text | GREEN_C | font_size=22 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | run_time=2 | Scene 1 |
| Subtitle FadeIn | run_time=1.5 | shift=UP*0.5 |
| NPN symbol Create | run_time=2 | With LaggedStart labels |
| Circuit components FadeIn | run_time=3 | LaggedStart |
| Base current flash | run_time=1.5 | time_width=0.4 |
| Main current flash (Succession) | run_time=2.6 | 7 segments, 0.3-0.5s each |
| Switch close | run_time=0.5 | Lever animation |
| LED blink loop (summary) | 0.6s on, 0.6s off | Repeats 2x |
| Scene wait between scenes | 1.5-3s | Absorption time |
| Total video | ~45-55s | 5 scenes |

## Patterns

### Pattern: Custom Circuit Component with Terminal Accessors

**What**: Build circuit components (NPN transistor, LED, battery, resistor) as VGroups from geometric primitives, then attach lambda methods for terminal positions. This allows wiring by calling `component.get_terminal()` instead of manual coordinate math.
**When to use**: Any circuit diagram, electronics visualization, or node-and-wire diagram where components need connection points. Also applicable to pipeline diagrams, flowcharts, or any system where boxes connect via specific attachment points.

```python
# Source: projects/manim-scripts/scenes/transistor.py:261-285
def _create_npn_bjt_symbol(self, scale=1.0, label_scale=0.5, colors=None):
    c = colors if colors else {"npn": NPN_SYMBOL_COLOR, "text": LABEL_COLOR}
    s_parts = VGroup()
    circle = Circle(radius=0.7*scale, color=c["npn"], stroke_width=3)
    bar = Line([bar_cx, 0.4*scale, 0], [bar_cx, -0.4*scale, 0], color=c["npn"], stroke_width=3)
    # ... collector, base, emitter lines ...
    group = VGroup(s_parts, cl, bl, el)
    group.symbol_only = s_parts
    group.get_collector_terminal = lambda: c_line.get_end()
    group.get_base_terminal = lambda: b_line.get_end()
    group.get_emitter_terminal = lambda: e_line.get_end()
    return group
```

### Pattern: ShowPassingFlash for Current Flow

**What**: Animate electrical current or signal flow along a wire path using ShowPassingFlash. The flash is a bright copy of the path line with increased stroke width that travels along it and disappears. Use Succession to chain multiple path segments for continuous flow.
**When to use**: Circuit current flow, signal propagation in networks, data flow in pipelines, information flow in neural networks — any visualization where something moves ALONG a path without leaving a permanent trace.

```python
# Source: projects/manim-scripts/scenes/transistor.py:153-157
base_current_flash_anim = ShowPassingFlash(
    base_current_path.copy().set_stroke(color=BASE_CURRENT_COLOR, width=5),
    time_width=0.4, run_time=1.5
)
self.play(base_current_flash_anim)
```

### Pattern: Succession for Multi-Segment Sequential Flash

**What**: Chain multiple ShowPassingFlash animations in a Succession so current appears to flow through an entire circuit path segment by segment. Each segment gets its own flash with appropriate timing.
**When to use**: Multi-hop signal flow — circuit current through battery→resistor→LED→transistor, data through a pipeline of stages, packet traversal through network nodes.

```python
# Source: projects/manim-scripts/scenes/transistor.py:171-179
main_current_flash_anims = Succession(
    ShowPassingFlash(path_bat_to_res.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.3, run_time=0.4),
    ShowPassingFlash(path_res_internal.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.2, run_time=0.3),
    ShowPassingFlash(path_res_to_led.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.3, run_time=0.4),
    ShowPassingFlash(path_led_internal.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.2, run_time=0.3),
    ShowPassingFlash(path_led_to_C.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.3, run_time=0.4),
    ShowPassingFlash(path_npn_internal.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.2, run_time=0.3),
    ShowPassingFlash(path_E_to_bat.copy().set_stroke(color=MAIN_CURRENT_COLOR, width=7), time_width=0.4, run_time=0.5),
)
```

### Pattern: Scene Bundle for Multi-Scene Narrative

**What**: Each scene method returns a dictionary of created mobjects. Later scenes unpack these to reference, transform, or fade out elements from previous scenes. This avoids global state while maintaining continuity.
**When to use**: Any multi-act narrative where elements persist across scenes — progressive disclosure, before/after comparisons, tutorial flows with persistent diagrams.

```python
# Source: projects/manim-scripts/scenes/transistor.py:122-126
return {
    "npn_bjt": npn_bjt, "led": led_obj, "battery": battery_obj,
    "resistor_led": resistor_led, "wires": wires, "component_labels": component_labels,
    "off_state_text": off_state_text, "blocked_X": blocked_X
}
# Later scene unpacks:
# npn_bjt, led, battery = scene2_bundle["npn_bjt"], scene2_bundle["led"], ...
```

## Scene Flow

1. **Scene 1 - Title** (0-5s): "How a Transistor Works as a Switch" writes in. Subtitle fades in. Background NPN symbol at low opacity in corner.
2. **Scene 2 - OFF State** (5-18s): NPN symbol draws with labels C, B, E. Circuit components (battery, LED, resistor, wires) fade in with LaggedStart. Red X appears on NPN bar. "No Base Current (OFF State)" text.
3. **Scene 3 - ON State** (18-32s): Base switch and resistor appear. Switch closes (lever animates). Yellow base current flash travels along base wire. NPN bar turns green (opens). Green main current flash traverses full circuit via Succession. LED fills with GREEN_C. "LED Lights Up!" text.
4. **Scene 4 - Amplification** (32-40s): "Small Base signal controls large C-E current" text. Re-runs both current flashes with labels "Small Input" and "Large Output" to reinforce amplification concept.
5. **Scene 5 - Summary** (40-50s): Key takeaway text. Miniature NPN + LED appear. LED blinks on/off twice synchronized with base terminal Indicate. FadeOut all.

> Full file: `projects/manim-scripts/scenes/transistor.py` (326 lines)
