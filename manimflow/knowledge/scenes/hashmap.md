---
source: https://github.com/KainaniD/manim-videos/blob/main/hashmap.py
project: manim-videos
domain: [computer_science, data_structures, algorithms]
elements: [rectangle_node, arrow, line, label, grid, column]
animations: [write, transform, fade_in]
layouts: [grid, flow_left_right]
techniques: [helper_function, factory_pattern]
purpose: [definition, demonstration, process]
mobjects: [VGroup, Text, Rectangle, Line]
manim_animations: [Write, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 80
scene_classes: [Hashmap]
---

## Summary

Visualizes a hashmap with keys (Student1, Student2), 4 buckets (indices 0-3), and value slots on the right. Animated lines trace the path from key through a hash function (represented by a vertical divider) to the appropriate bucket, then from bucket to the value slot. ReplacementTransform fills the initially empty value rectangle with the mapped value (e.g., "A-" or "B+"). The layout shows the three-column structure: keys -> hash function -> buckets -> values.

## Design Decisions

- **Three-column layout (keys | buckets | values)**: Shows the hashmap as a pipeline: key enters from the left, passes through the hash function, lands in a bucket, and maps to a value on the right. This left-to-right flow matches how data flows through the hash function.
- **Vertical divider line as hash function boundary**: A simple Line from `LEFT * 2 + UP * 2` to `LEFT * 2 + DOWN * 3` separates the key space from the bucket space. The divider represents the hash function without needing to visualize the function itself.
- **Animated path lines**: Lines are drawn sequentially (key -> divider, divider -> bucket, bucket -> value) to show the lookup path step by step. Each segment uses Write() so the viewer follows the path.
- **ReplacementTransform for value insertion**: The initially empty value rectangle transforms into one containing data. This shows that the value "appears" in the slot as a result of the mapping.
- **4 buckets for 2 keys**: Having more buckets than keys shows that many slots can be empty, which is realistic for hashmaps with low load factors.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - Keys: `LEFT * 4` column, shifted UP*(1/2) and DOWN*(3/2)
  - Hash divider: Line from `LEFT * 2 + UP * 2` to `LEFT * 2 + DOWN * 3`
  - Buckets: centered column, indices 0-3 at `UP + DOWN * i`
  - Values: `RIGHT * 3` column, 4 rectangles at `UP + DOWN * i`
- **Element sizing**: Keys are Rectangle(width=3, height=1), buckets are Rectangle(width=1, height=1), values are Rectangle(width=4, height=1)
- **Spacing**: Buckets 1 unit apart vertically, keys 2 units apart

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Key rectangles | stroke=WHITE | fill=WHITE opacity=0, width=3 |
| Bucket rectangles | stroke=WHITE | fill=WHITE opacity=0, width=1 |
| Value rectangles | stroke=WHITE | fill=WHITE opacity=0, width=4 |
| Key text | WHITE | scale=0.8 |
| Bucket text | WHITE | scale=0.8 |
| Path lines | WHITE | Default Line color |
| Hash divider | WHITE | Vertical Line |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + all elements Write | run_time=1 | Simultaneous |
| Each path segment Write | Default (~1s) | 3 segments per lookup |
| ReplacementTransform (value fill) | Default (~1s) | Empty -> filled |
| Wait between lookups | wait=1 | Pause to absorb |
| Final wait | wait=16 | Long hold on final state |
| Total video | ~30 seconds | 2 lookups + long hold |

## Patterns

### Pattern: Fixed-Width Rectangle Node Factory

**What**: Creates a VGroup of Text + Rectangle with a specified width. The text is centered and scaled to 0.8. The rectangle has transparent fill and white stroke. This is the universal building block for keys, buckets, and values in table-like visualizations.
**When to use**: Hashmaps, lookup tables, database row visualizations, any tabular data structure where cells have different widths but consistent height.

```python
# Source: projects/manim-videos/hashmap.py:30-37
def createDataFixedWidth(data, width):
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_rectangle = Rectangle(width=width, height=1, stroke_color=WHITE)
    node_rectangle.set_fill(WHITE, opacity=0)
    node.add(node_data, node_rectangle)
    return node
```

### Pattern: Animated Lookup Path with Sequential Lines

**What**: Three Line segments are drawn sequentially using Write() to trace the path from a key through the hash function to a value slot. Each segment starts where the previous one ended, creating a visual "data flow" through the hashmap. After the path is drawn, ReplacementTransform fills the destination slot.
**When to use**: Hashmap lookups, dictionary access, cache hits, any key-value mapping where you want to show HOW the mapping works, not just the result. Also works for routing diagrams and pipeline flows.

```python
# Source: projects/manim-videos/hashmap.py:65-70
# Trace path: key -> hash boundary -> bucket -> value
self.play(Write(Line(key_group[0], LEFT * 2 + UP * (1/2))))
self.play(Write(Line(LEFT * 2 + UP * (1/2), LEFT * (1/2) + DOWN)))
self.play(Write(Line(RIGHT * (1/2) + DOWN, value_group[2])))

# Fill the value slot
transform_value_one = createDataFixedWidth("A-", 4).shift(RIGHT * 3 + DOWN)
self.play(ReplacementTransform(value_group[2], transform_value_one))
```

## Scene Flow

1. **Setup** (0-2s): Title "What is a hashmap?" writes. All keys, buckets, values, and the hash divider line appear simultaneously.
2. **First lookup** (2-6s): Three lines trace sequentially from Student1 -> hash divider -> bucket 2 -> value slot 2. Value slot transforms from empty to "A-".
3. **Pause** (6-7s): Wait 1s.
4. **Second lookup** (7-11s): Three lines trace from Student2 -> hash divider -> bucket 0 -> value slot 0. Value slot transforms from empty to "B+".
5. **Done** (11-27s): Wait 16s on final state showing both mappings.

> Full file: `projects/manim-videos/hashmap.py` (80 lines)
