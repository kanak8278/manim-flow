---
source: https://github.com/KainaniD/manim-videos/blob/main/bubble-sort.py
project: manim-videos
domain: [computer_science, algorithms, sorting, data_structures]
elements: [array, rectangle_node, pointer, overlay, label, badge]
animations: [swap, arc_swap, highlight, color_change, slide, fade_in, fade_out, write]
layouts: [horizontal_row, edge_anchored]
techniques: [color_state_machine, overlay_tracking, labeled_pointer, status_text, helper_function, factory_pattern]
purpose: [step_by_step, demonstration, comparison]
mobjects: [Rectangle, Square, VGroup, Text, Line]
manim_animations: [Transform, MoveToTarget, FadeToColor, FadeIn, FadeOut, Write]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 267
scene_classes: [BubbleSort]
---

## Summary

Visualizes bubble sort on a 5-element array using rectangular bar elements. Each comparison is shown by sliding colored overlays (RED=current, BLUE=next) across the array. Swaps use 180-degree arc paths so they look distinct from linear slides. A text status bar at the bottom narrates each step. A boolean flag tracks whether any swap occurred this pass.

## Design Decisions

- **Horizontal array layout**: Left-to-right matches natural reading order and how arrays are taught in textbooks. Vertical would feel unnatural for a sequential data structure.
- **Arc swap (180 degrees) instead of linear**: If elements just slid past each other linearly, the swap would be invisible — they'd pass through each other. The arc path creates a visible "crossing over" motion. run_time=0.75 is fast enough to feel snappy but slow enough to see.
- **RED/BLUE overlay system**: RED = active/current (danger/attention), BLUE = next/passive (calm/secondary). Semi-transparent (opacity=0.4) so the underlying data value remains readable. This is a universal UX pattern — red grabs attention, blue is informational.
- **Status text at bottom edge**: Narration stays out of the way of the main visualization. It acts like subtitles — always present, never competing with the visual focus area at center.
- **Swap flag at top-right**: Secondary information positioned in peripheral vision. The viewer only glances at it, doesn't need to read it carefully.
- **Labeled pointers with arrows**: Shows the mapping between code variables ("current", "next") and the visual elements. Critical for teaching — connects abstract code to concrete visual.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Array: centered, shifted `LEFT * 2 + DOWN * 1` (5 elements, 1 unit wide each)
  - Current/next labels: `UP + LEFT * 2` and `UP + LEFT`, scale=0.8
  - Swap flag: `UP * 2 + RIGHT * 3`, scale=0.8
  - Status text: `to_edge(DOWN)`, scale=0.8
- **Element sizing**: Rectangle(width=1, height=1), inner Text scale=0.8
- **Array spacing**: Elements placed via `addToArrayHorizontal` — each shifts RIGHT by 1 unit from the previous element's center
- **Overlay sizing**: Square(side_length=1) matches Rectangle exactly, stroke_width=0 so only the fill color shows
- **Pointer lines**: Line from label to array element, buff=0.2, with arrow tip

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Array rectangles | stroke=WHITE | fill=BLACK, opacity=0 (transparent) |
| Array text | WHITE | Default, scale=0.8 |
| Current overlay | RED | opacity=0.4, stroke_width=0 |
| Next overlay | BLUE | opacity=0.4, stroke_width=0 |
| "current" label | RED | Via `t2c={"current": RED}` |
| "next" label | BLUE | Via `t2c={"next": BLUE}` |
| Status text | WHITE | scale=0.8 |
| Swap flag | WHITE | scale=0.8, changes text content |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Arc swap | run_time=0.75 | Fast enough to feel snappy |
| Linear swap | run_time=1.0 | Slightly slower, used less |
| Overlay slide | run_time=0.75 | Matches swap speed |
| Status text change | run_time=0.4 + wait=0.4 | Quick FadeOut/FadeIn |
| Initial setup (Write) | Default (~1s) | Title, array, labels |
| Total video | ~38 seconds | 4 full passes through array |

## Patterns

### Pattern: Rectangle Array Element

**What**: Create a data element as a VGroup of Text + Rectangle. The text is centered inside the rectangle. This is the atomic building block for any array visualization.
**When to use**: Any array, list, queue, or stack visualization where elements have values to display.

```python
# Source: projects/manim-videos/bubble-sort.py:21-29
def createRectangleNode(data, width=1, height=1):
    data = str(data)
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_rectangle = Rectangle(width=width, height=height, stroke_color=WHITE)
    node_rectangle.set_fill(BLACK, opacity=0)
    node.add(node_data, node_rectangle)
    return node
```

### Pattern: Arc-Based Swap

**What**: Two elements swap positions along curved 180-degree arc paths. The arc makes the swap visually obvious — elements cross OVER each other instead of phasing through. Without the arc, a swap looks identical to two elements just sliding past.
**When to use**: Sorting visualizations, reordering sequences, any pairwise exchange where you need the viewer to SEE that a swap happened.

```python
# Source: projects/manim-videos/bubble-sort.py:43-46
def playArcSwap(self, element1, element2, arc=180):
    element1_copy = element1.copy().shift(element2.get_center() - element1.get_center())
    element2_copy = element2.copy().shift(element1.get_center() - element2.get_center())
    self.play(
        Transform(element1, element1_copy, path_arc=arc * DEGREES),
        Transform(element2, element2_copy, path_arc=arc * DEGREES),
        run_time=0.75
    )
```

### Pattern: Target-Based Position Swap

**What**: Prepare two elements to swap positions using generate_target(), then animate with MoveToTarget. This is a two-step pattern — first set up where things will go, then animate. Useful when you need to batch multiple movements into one self.play() call.
**When to use**: When you need to set up a swap before animating it, or when batching multiple swaps or movements simultaneously.

```python
# Source: projects/manim-videos/bubble-sort.py:31-38
def swap(first, second):
    first.generate_target()
    second.generate_target()
    first.target.shift(second.get_center() - first.get_center())
    second.target.shift(first.get_center() - second.get_center())

def playSwap(self, element1, element2):
    self.play(MoveToTarget(element1), MoveToTarget(element2), run_time=1)
```

### Pattern: Color Overlay Tracking

**What**: Semi-transparent colored squares overlaid on array elements to show which elements are currently being processed. The overlay is a separate Square mobject (not a color change on the element itself) so it can slide independently. Group both overlays in a VGroup so they move together.
**When to use**: Algorithm state tracking — highlight "current", "next", "visited", "sorted" etc. Better than changing element color directly because the overlay can be animated independently.

```python
# Source: projects/manim-videos/bubble-sort.py:123-125
current_overlay = Square(1, stroke_width=0).shift(array[0].get_center())
current_overlay.set_fill(RED, opacity=0.4)
next_overlay = Square(1, stroke_width=0).shift(array[1].get_center())
next_overlay.set_fill(BLUE, opacity=0.4)
overlay_group = VGroup().add(current_overlay).add(next_overlay)

# Slide overlays to next position:
overlay_group.generate_target()
overlay_group.target.shift(RIGHT)
self.play(MoveToTarget(overlay_group), run_time=0.75)
```

### Pattern: Step-by-Step Status Text

**What**: Replace bottom-of-screen text to narrate what the algorithm is doing at each step. Uses FadeOut old + FadeIn new simultaneously for a clean swap. The 0.4s wait after gives the viewer time to read.
**When to use**: Any step-by-step algorithm walkthrough, tutorial, or demonstration where you need to explain what's happening at each stage.

```python
# Source: projects/manim-videos/bubble-sort.py:93-95
def updateText(self, text, new_text):
    self.play(FadeOut(text), FadeIn(new_text), run_time=0.4)
    self.wait(0.4)

# Pre-create all status variants:
current_step = Text("Current Step").to_edge(DOWN).scale(0.8)
current_step_increment = Text("increment current and next indices").to_edge(DOWN).scale(0.8)
current_step_correct_order = Text("correct order of current and next element").to_edge(DOWN).scale(0.8)
current_step_restart = Text("restart if you swapped").to_edge(DOWN).scale(0.8)
```

### Pattern: Labeled Pointer with Arrow

**What**: A text label with an arrow line pointing to an array element, showing the mapping between a variable name and the visual element it references. Uses t2c (text-to-color) to color the variable name in the label.
**When to use**: When you need to show which code variable points to which visual element. Essential for teaching data structure operations.

```python
# Source: projects/manim-videos/bubble-sort.py:116-121
current_label = Text("current", t2c={"current": RED}).shift(UP + LEFT * 2).scale(0.8)
current_label_line = Line(current_label, array[0], buff=0.2).add_tip()
current_label_group = VGroup().add(current_label).add(current_label_line)
```

## Scene Flow

1. **Setup** (0-3s): Title "What is Bubble Sort?" writes at top. Array of 5 elements [4,5,2,1,3] writes at center. "current" and "next" labels with pointer arrows appear above the first two elements. Swap flag "swapped == false" appears top-right.
2. **Iteration 1** (3-15s): Overlay slides right one position at a time. At each position: check if current > next. If yes → arc swap + set swapped=true. If no → just advance. Status text narrates each decision. After reaching the end → "restart if you swapped."
3. **Iteration 2** (15-25s): Overlay resets to position 0. Same process, fewer swaps needed because largest element is already at the end.
4. **Iteration 3** (25-32s): Even fewer swaps. Array is almost sorted.
5. **Iteration 4** (32-36s): Full pass with no swaps. Swap flag stays "false."
6. **Done** (36-38s): Status shows "did not swap, so array is sorted." Overlays fade out. Sorted array scales up to 1.2x to celebrate completion.

> Full file: `projects/manim-videos/bubble-sort.py` (267 lines)
