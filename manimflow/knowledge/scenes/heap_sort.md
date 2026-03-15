---
source: https://github.com/KainaniD/manim-videos/blob/main/heap-sort.py
project: manim-videos
domain: [computer_science, algorithms, sorting, data_structures]
elements: [tree, circle_node, rectangle_node, arrow, line, label]
animations: [swap, highlight, color_change, fade_out, write]
layouts: [dual_panel, hierarchy, vertical_stack]
techniques: [dual_track_visualization, color_state_machine, helper_function, factory_pattern, status_text]
purpose: [step_by_step, demonstration, process]
mobjects: [Circle, Rectangle, VGroup, Text, Line]
manim_animations: [Write, MoveToTarget, FadeOut, FadeToColor, Transform]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 214
scene_classes: [HeapSort]
---

## Summary

Visualizes heap sort on a 7-element max-heap shown as both a tree (left side) and an array (right side). The algorithm repeats: swap root with last unsorted node, remove it from the tree (marking it GREEN in the array as "sorted"), then heapify down. Both tree and array update simultaneously via synchronized double-swaps. A status text at the bottom narrates each step. The dual representation reveals why heap sort works -- the tree structure drives the sorting but the result is a sorted array.

## Design Decisions

- **Dual-track visualization (tree + array)**: The tree shows the heap property and parent-child relationships. The array shows the underlying storage and final sorted order. Seeing both simultaneously connects the abstract heap concept to the concrete array.
- **Synchronized double-swap**: When two tree nodes swap, the corresponding array elements also swap in the same animation call (playDoubleSwap). This visual linkage proves that swapping in the tree IS swapping in the array.
- **GREEN for sorted elements**: When an element is removed from the heap and placed in its final sorted position, its array rectangle turns GREEN. This progressively reveals the sorted section growing from the end.
- **Status text narrates algorithm steps**: "swap first and last node", "remove last node from tree", "heapify" -- these map to the three phases of each heap sort iteration. The viewer can follow the algorithm by reading the status.
- **Tree nodes FadeOut when removed**: When the root is swapped to the end and "removed" from the heap, both the tree node and its edge FadeOut. This shrinks the visual tree, showing the heap getting smaller each iteration.
- **Array scaled to 0.8**: The array is slightly smaller than the tree to maintain visual hierarchy -- the tree is the primary visualization, the array is supplementary.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Heap tree: `UP * 2 + LEFT * 2` (root), children offset with buffer_1=0.35, buffer_2=0.31
  - Array: `RIGHT * 4 + UP * 2.5`, vertical stack of rectangles, scale=0.8
  - Status text: `LEFT * 2 + DOWN * 2.5`, scale=0.8
- **Tree layout**:
  - Root at `UP * 2 + LEFT * 2`
  - Level 1: x_offset=+-2, y_offset=1, buffer=0.35
  - Level 2: x_offset=+-1, y_offset=2, buffer=0.31
- **Array layout**:
  - Starts at `RIGHT * 4 + UP * 2.5`, elements stack DOWN by 1 unit each
  - Rectangle width=3, height=1
  - Entire array scaled 0.8
- **Node sizing**: Circle radius=0.5 for tree, Rectangle(3,1) for array elements

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Tree node circles | WHITE | stroke_color=WHITE, no fill |
| Tree node text | WHITE | Default |
| Array rectangles | WHITE | stroke=WHITE, fill=BLACK opacity=0.3 |
| Array text | WHITE | scale=0.8 |
| Sorted array element | GREEN | FadeToColor on rectangle [1] |
| Status text | WHITE | scale=0.8 |
| Tree edges | WHITE | Line with arrow tip |
| Title | WHITE | scale=1.2 |

Color strategy: WHITE (unsorted/active) -> GREEN (sorted/final position). GREEN signals "done" and creates a growing visual indicator of progress.

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Initial setup Write | Default (~1s) | All elements simultaneously |
| Status text update | run_time=0.75 + wait=0.5 | Transform-based |
| Double swap | run_time=1 | Tree + array swap simultaneously |
| Node removal FadeOut | Default (~1s) | Tree node + edge |
| GREEN color change | Default (~1s) | Bundled with FadeOut |
| Final array slide left | Default (~1s) | MoveToTarget LEFT * 4 |
| Total video | ~60 seconds | 7 elements, ~8s per extraction |

## Patterns

### Pattern: Synchronized Tree-Array Double Swap

**What**: Two tree nodes and their corresponding array elements swap positions in a single animation call. Both use generate_target/MoveToTarget. The swap() helper sets targets for two elements, then playDoubleSwap() animates all four movements simultaneously. This visual synchronization proves the tree and array are the same data structure.
**When to use**: Heap sort, heap operations (insert, extract-max), any visualization where a tree has an underlying array representation. Also works for any dual-view data structure where changes must stay in sync.

```python
# Source: projects/manim-videos/heap-sort.py:31-41
def swap(first, second):
    first.generate_target()
    second.generate_target()
    first.target.shift(second.get_center() - first.get_center())
    second.target.shift(first.get_center() - second.get_center())

def playDoubleSwap(self, element1, element2, element3, element4):
    self.play(MoveToTarget(element1), MoveToTarget(element2),
              MoveToTarget(element3), MoveToTarget(element4), run_time=1)

# Usage: swap tree root with last node AND array first with last
swap(heap_tree[0], heap_tree[-2])
swap(heap[0], heap[-1])
playDoubleSwap(self, heap[0], heap[-1], heap_tree[0], heap_tree[-2])
```

### Pattern: Progressive Sorted Marking with GREEN

**What**: After extracting the max from the heap, the corresponding array element's rectangle turns GREEN via FadeToColor. This is bundled with FadeOut of the tree node/edge in the same play() call. The GREEN elements accumulate from the end of the array, showing the sorted portion growing.
**When to use**: Heap sort, selection sort, any sorting algorithm where elements reach their final position one at a time. The GREEN color creates a visual progress bar.

```python
# Source: projects/manim-videos/heap-sort.py:132-133
# Remove from tree + mark as sorted in array
self.play(FadeOut(heap_tree[0]), FadeOut(heap_tree[12]), FadeToColor(heap[0][1], GREEN))
```

### Pattern: Vertical Array with addToArray Helper

**What**: Creates a vertical array where each new element is positioned at `array[-1].get_center() + DOWN`. The array is a VGroup, and addToArray shifts the new element relative to the last element. This builds a vertical column of rectangles.
**When to use**: Array representation alongside a tree (heap visualization), vertical lists, any vertical sequence where elements stack downward.

```python
# Source: projects/manim-videos/heap-sort.py:56-60
def createArray(element):
    return VGroup().add(element)

def addToArray(array, element):
    array.add(element.shift(array[-1].get_center() + DOWN))
```

### Pattern: Transform-Based Status Text Update

**What**: Status text updates by transforming the existing Text mobject into a new one at the same position. Uses Transform (not ReplacementTransform) so the original reference stays valid for future updates. A 0.5s wait after gives reading time.
**When to use**: Algorithm step narration, instruction text that changes frequently, any bottom-of-screen status that must update without FadeOut/FadeIn flicker.

```python
# Source: projects/manim-videos/heap-sort.py:88-91
def updateText(self, text, new_text, scale=0.8):
    transformedText = Text(new_text).shift(text.get_center()).scale(scale)
    self.play(Transform(text, transformedText), run_time=0.75)
    self.wait(0.5)
```

## Scene Flow

1. **Setup** (0-2s): Title "What is Heap Sort?" writes. Max-heap tree (7 nodes: 9,8,5,4,1,3,2) and vertical array appear. Status text "current step" at bottom.
2. **Iteration 1** (2-10s): Swap root (9) with last (2) in both views. FadeOut tree node 9 + edge, mark array[0] GREEN. Heapify: swap 2 down twice (2->8, 2->5 paths).
3. **Iteration 2** (10-18s): Swap root (8) with last unsorted. Remove, mark GREEN. Heapify: swap down once.
4. **Iteration 3** (18-26s): Swap root (5) with last unsorted. Remove, mark GREEN. Heapify: swap down.
5. **Iterations 4-6** (26-50s): Same pattern, tree shrinks with each extraction. Array accumulates GREEN from end. Heapify paths get shorter as tree shrinks.
6. **Final element** (50-55s): Last remaining tree node removed. All array elements GREEN.
7. **Cleanup** (55-60s): Status text fades out. Array slides left to center (MoveToTarget LEFT * 4). Wait 1s.

> Full file: `projects/manim-videos/heap-sort.py` (214 lines)
