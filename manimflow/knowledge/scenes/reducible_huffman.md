---
source: https://github.com/nipunramk/Reducible/blob/main/2021/Huffman/huffman.py
project: Reducible
domain: [computer_science, algorithms, compression, information_theory, data_structures]
elements: [tree, binary_tree, node, label, arrow, box, surrounding_rect, formula, equation, bar_chart]
animations: [fade_in, fade_out, write, transform, replacement_transform, transform_from_copy, grow, move, lagged_start]
layouts: [hierarchy, centered, flow_left_right, vertical_stack]
techniques: [custom_mobject, progressive_disclosure, algorithm_class_separation, data_driven, history_replay]
purpose: [step_by_step, demonstration, decomposition, process, derivation]
mobjects: [Circle, Rectangle, VGroup, TextMobject, TexMobject, Line, Arrow, SurroundingRectangle, Brace, Integer]
manim_animations: [FadeIn, FadeOut, Write, ShowCreation, Transform, ReplacementTransform, TransformFromCopy, GrowFromCenter]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 4989
scene_classes: [Node, IntroStory, Transition, HuffmanCodes, HuffmanCodesThumbnail, HuffmanCodesProbDist, HuffmanImplementation, HuffmanConclusion, ShannonFano, ProblemFormulation, BalancingAct, IntroSelfInformation, IntroEntropy, EntropyCompression, EntropyExample]
---

## Summary

Visualizes Huffman coding from first principles: character frequency analysis, priority queue sorting, bottom-up tree construction with animated node merging, binary code assignment by tree traversal, and comparison with Shannon-Fano coding. Also covers information theory foundations including self-information, entropy, and compression bounds. Uses manimlib (not Community Edition) with CONFIG dicts and old-style animation syntax.

## Design Decisions

- **Node as data class with mob generation**: Node stores freq, key, left/right children. `generate_mob()` creates leaf nodes as stacked rectangles (freq box + key box) and internal nodes as circles. This separation means the tree logic is pure Python while visuals are generated on demand.
- **Position map for tree layout**: Hard-coded dict mapping node keys to screen positions. While not generalizable, it gives precise control over tree aesthetics for the specific example used.
- **Heap displayed as vertical list**: Priority queue shown as vertically-arranged nodes on the left side (shift_left=LEFT*5). After each merge, heap re-sorts and transforms to new positions.
- **Leaf vs internal visual distinction**: Leaf nodes are two stacked rectangles (YELLOW freq + BLUE key). Internal nodes are YELLOW circles with frequency text. This visual encoding instantly communicates node type.
- **Binary background for thumbnail**: Full-screen grid of random 0/1 integers at low opacity, with random cells highlighted in blue. Creates a "data" feel behind the tree.
- **manimlib syntax**: Uses TextMobject (not Text), CONFIG dict, positional animation syntax (`obj.move_to, target`), ShowCreation (not Create).

## Composition

- **Tree positions**: Hard-coded position_map dict, e.g. `'E': DOWN*3 + RIGHT*2`, `'DBEA': UP*2.4`
- **Leaf node sizing**: freq_box Rectangle(height=0.5, width=1), key_box Rectangle(height=1, width=1), arranged DOWN buff=0
- **Internal node**: Circle(radius=0.5), YELLOW stroke, freq text scale=0.8+0.4
- **Heap display**: Arranged DOWN on LEFT*5, each node.mob scaled 0.7
- **Tree edges**: Line from parent center to child top (leaf) or child circle edge, GRAY stroke width=6
- **Text characters**: Arranged RIGHT buff=SMALL_BUFF*0.5, positioned UP*3.5
- **Information theory graphs**: GraphScene with custom x/y ranges for entropy plots

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Freq box (leaf) | YELLOW | Rectangle stroke |
| Key box (leaf) | BLUE | Rectangle stroke + fill |
| Internal node circle | YELLOW | Circle stroke |
| Tree edges | GRAY | Line stroke_width=6 |
| Text characters | WHITE | TextMobject default |
| Binary background | WHITE opacity=0.2 | Random highlighted cells BLUE opacity=0.3-0.7 |
| Code highlighting | GREEN_SCREEN | Subsequence indicators |
| Surround rectangles | WHITE | SurroundingRectangle default |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Character text write | default | Write(text) |
| Group text transforms | run_time=3 | TransformFromCopy for each character to group |
| Node transform from text | run_time=2 | ReplacementTransform group to node mob |
| Sort nodes | run_time=2 | Transform to new positions |
| Huffman merge step | run_time=2 | Move nodes + edges + GrowFromCenter parent |
| Heap re-sort | run_time=2 | Transform heap to new arrangement |
| Total video | ~30 minutes | Full Huffman + information theory |

## Patterns

### Pattern: Tree Node with Dual Visual Forms

**What**: Node class generates different mobjects for leaf nodes (two stacked rectangles: freq box on top, character box below) and internal nodes (circle with frequency). The `generate_mob()` method checks key length to decide which form. Leaf nodes store `is_leaf=True` for edge routing.

**When to use**: Huffman trees, decision trees, any binary tree where leaf and internal nodes need visually distinct representations. Also useful for parse trees or expression trees.

```python
# Source: projects/Reducible/2021/Huffman/huffman.py:6-45
class Node:
    def __init__(self, freq, key=''):
        self.freq = freq
        self.key = key
        self.left = None
        self.right = None

    def generate_mob(self, text_scale=0.8, radius=0.5, is_leaf=False):
        if len(self.key) != 1 and not is_leaf:
            self.is_leaf = False
            freq = TextMobject(str(self.freq)).scale(text_scale + 0.4)
            node = Circle(radius=radius).set_color(YELLOW)
            freq.move_to(node.get_center())
            self.mob = VGroup(node, freq)
            return self.mob
        # Leaf: two rectangles
        self.is_leaf = True
        freq_box = Rectangle(height=0.5, width=1).set_color(YELLOW)
        freq_interior = TextMobject(str(self.freq)).scale(text_scale)
        freq_interior.move_to(freq_box.get_center())
        key_box = Rectangle(height=1, width=1).set_color(BLUE)
        key_interior = TextMobject(self.key).scale(text_scale + SMALL_BUFF * 5)
        key_interior.move_to(key_box.get_center())
        self.mob = VGroup(VGroup(freq_box, freq_interior),
                          VGroup(key_box, key_interior)).arrange(DOWN, buff=0)
        return self.mob
```

### Pattern: Animated Huffman Tree Construction

**What**: Builds the Huffman tree step by step: pop two smallest nodes from heap, create parent, animate nodes moving to tree positions, draw edges, grow parent, then re-sort the heap. Position map controls final tree layout. Heap displayed as vertical list that shrinks each step.

**When to use**: Priority queue algorithms, bottom-up tree construction, any algorithm that repeatedly merges smallest elements. Greedy algorithm visualization.

```python
# Source: projects/Reducible/2021/Huffman/huffman.py:599-709
def make_huffman_tree(self, heap, text_scale=0.8):
    while len(heap) > 1:
        first = heap.pop(0)
        second = heap.pop(0)
        parent = Node(first.freq + second.freq, first.key + second.key)
        parent.generate_mob(text_scale=text_scale).scale(0.7)
        parent.connect_node(first, left=True)
        parent.connect_node(second, left=False)
        self.animate_huffman_step(parent, first, second, position_map,
                                  nodes, edges, edge_dict, heap)

def get_edge_mob(self, parent, child):
    start, end = parent.mob.get_center(), child.mob.get_center()
    if child.is_leaf:
        end = child.mob.get_top()
    unit_v = (end - start) / np.linalg.norm(end - start)
    start = start + unit_v * parent.mob[0].radius
    edge = Line(start, end).set_stroke(color=GRAY, width=6)
    return edge
```

### Pattern: Character Grouping with TransformFromCopy

**What**: Takes a string of characters, groups identical ones, and animates each character flying from its original position to form sorted groups. Uses a mapping dict to track which characters go where, then batch TransformFromCopy animations.

**When to use**: Frequency analysis visualization, any scenario where you need to show items being categorized/grouped from a sequence. Sorting visualizations, histogram construction from raw data.

```python
# Source: projects/Reducible/2021/Huffman/huffman.py:501-552
def group_text(self, text_mobs):
    mapping = {}
    mapping_indices = {}
    for i, text in enumerate(text_mobs):
        if text.tex_string not in mapping:
            mapping[text.tex_string] = 1
            mapping_indices[text.tex_string] = [i]
        else:
            mapping[text.tex_string] += 1
            mapping_indices[text.tex_string].append(i)
    # Create target groups arranged vertically
    for i, key in enumerate(mapping_to_text_mobs):
        mapping_to_text_mobs[key].move_to(positions[i])
    # Animate each character to its group
    transforms = []
    for key in mapping_indices:
        for i, index in enumerate(mapping_indices[key]):
            transforms.append(TransformFromCopy(text_mobs[index], mapping_to_text_mobs[key][i]))
    self.play(*transforms, run_time=3)
```

## Scene Flow

1. **Intro Story** (0-3min): Huffman vs Fano historical context. Data compression problem statement. Binary representation of text, images, video.
2. **Huffman Codes** (3-12min): Character text displayed, grouped by frequency, transformed to leaf nodes, sorted by priority. Step-by-step tree construction with heap visualization. Binary code assignment.
3. **Probability Distribution** (12-14min): Huffman tree for arbitrary probability distributions.
4. **Implementation** (14-18min): Code walkthrough of Huffman algorithm.
5. **Shannon-Fano** (18-22min): Alternative top-down approach, comparison with Huffman.
6. **Information Theory** (22-30min): Self-information derivation, entropy definition, connection to optimal compression. Graphical entropy plots.

> Note: This file uses manimlib (Grant Sanderson's version), not Manim Community Edition. Key differences: TextMobject instead of Text, CONFIG dict, ShowCreation instead of Create, positional animation syntax.
