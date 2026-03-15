---
source: https://github.com/KainaniD/manim-videos/blob/main/pointers.py
project: manim-videos
domain: [computer_science, data_structures]
elements: [circle_node, rectangle_node, arrow, label, pointer]
animations: [write, slide, fade_in, fade_out]
layouts: [side_by_side]
techniques: [labeled_pointer, helper_function, factory_pattern]
purpose: [definition, demonstration, relationship]
mobjects: [VGroup, Text, Circle, Square, Line]
manim_animations: [Write, ShowCreation, MoveToTarget, FadeOut]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 112
scene_classes: [Pointers]
---

## Summary

Visualizes the concept of pointers by showing two variables (myNum=5, myChar='c') as BLUE-filled circle nodes, and their pointers (myNumPointer, myCharPointer) as square nodes containing hex memory addresses (0x6dfed4, 0x68b3a2). Arrow-tipped lines connect each pointer to its target variable. Brief "variable name" and "variable data" labels introduce the parts of a variable before the pointer concept is shown.

## Design Decisions

- **Circle for variables, square for pointers**: The visual distinction (round vs rectangular) teaches that a pointer is a DIFFERENT kind of thing than the variable it points to. Circles suggest "data containers", squares suggest "address holders."
- **Hex address in pointer**: Showing the actual hex address (0x6dfed4) makes the abstraction concrete. The viewer sees that a pointer literally stores a memory address, not the data itself.
- **Arrow from pointer to variable**: The arrow-tipped line IS the "pointing" -- it visualizes the indirection. Without the arrow, the viewer would just see two unrelated boxes.
- **BLUE-filled circles for variables**: BLUE fill (opacity=0.5) makes variables visually prominent. The surround() auto-sizing handles varying content widths.
- **Two pointer examples**: One int pointer (myNum) and one char pointer (myChar) show that pointers work for any data type. The two examples are laid out in a diagonal pattern to use screen space efficiently.
- **Brief label introduction**: "variable name" and "variable data" labels briefly appear and fade to teach vocabulary before introducing the pointer concept. This progressive disclosure avoids overwhelming the viewer.

## Composition

- **Screen regions**:
  - Title: `to_edge(UP)`, scale=1.2
  - myNum variable: initially at center (UP), then shifts to `RIGHT * 2 + UP * 2`
  - myNum label: `UP`, scale=0.9
  - Pointer 1 (myNumPointer): label at `LEFT * 2 + UP * 2`, data at `LEFT * 2 + UP`
  - myChar variable: `RIGHT * 2 + DOWN * 2`
  - myChar label: `RIGHT * 2 + DOWN`, scale=0.9
  - Pointer 2 (myCharPointer): label at `LEFT * 2 + DOWN`, data at `LEFT * 2 + DOWN * 2`
- **Node sizing**: Circle with surround(buff=0.5), Square with surround(buff=0.5)
- **Arrow lines**: Line(start=pointer_data, end=variable_node) with add_tip()

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Variable circles | BLUE | stroke=BLUE, fill=BLUE opacity=0.5 |
| Variable text | WHITE | Default |
| Pointer squares | WHITE | stroke=WHITE, fill=WHITE opacity=0 |
| Pointer text (hex) | WHITE | scale=0.8 |
| Pointer arrows | WHITE | Line with add_tip() |
| Labels | WHITE | scale=0.8-0.9 |
| Title | WHITE | scale=1.2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title + variable Write | run_time=1 | Simultaneous |
| Vocabulary labels Write | run_time=0.5 | Brief |
| Vocabulary labels FadeOut | run_time=0.5 | Clear clutter |
| Variable reposition | run_time=1 | MoveToTarget shift |
| Pointer + arrow Write | run_time=1 | Label + data + arrow |
| Second variable + pointer | run_time=1 each | Same pattern |
| Final wait | wait=6 | Long hold |
| Total video | ~18 seconds | 2 pointer examples + hold |

## Patterns

### Pattern: Pointer Visualization with Arrow Connection

**What**: A pointer is shown as a square/rectangle containing a hex memory address, connected by an arrow-tipped line to the variable it references. The arrow is the key visual -- it makes the "pointing" relationship explicit. The pointer label sits above the address box.
**When to use**: Teaching pointer concepts, memory layout diagrams, reference/dereference visualization, linked data structure node connections, object reference diagrams in any language.

```python
# Source: projects/manim-videos/pointers.py:69-85
pointer_label = Text("myNumPointer")
pointer_label.shift(LEFT * 2 + UP * 2).scale(0.9)

pointer_data = createData("0x6dfed4")
pointer_data.shift(LEFT * 2 + UP)

pointer_data_to_myNum = Line(start=pointer_data, end=myNum_node)
pointer_data_to_myNum.add_tip()

self.play(Write(pointer_label), Write(pointer_data[0]),
          ShowCreation(pointer_data[1]), Write(pointer_data_to_myNum))
```

### Pattern: Variable Introduction with Vocabulary Labels

**What**: Brief text labels ("variable name", "variable data") appear next to a variable to teach terminology, then fade out before the main concept is introduced. This progressive disclosure builds vocabulary before layering on complexity.
**When to use**: Introductory CS concepts, teaching variable anatomy, any educational animation where vocabulary must be established before the main topic.

```python
# Source: projects/manim-videos/pointers.py:51-67
variable_name_label = Text("variable name")
variable_name_label.shift(UP + LEFT * 3).scale(0.8)
variable_data_label = Text("variable data")
variable_data_label.shift(LEFT * 3).scale(0.8)

self.play(Write(variable_data_label), Write(variable_name_label), run_time=0.5)
self.wait(2)
self.play(FadeOut(variable_data_label), FadeOut(variable_name_label), run_time=0.5)
```

### Pattern: Auto-Sized Node with surround()

**What**: Both circle nodes (variables) and square nodes (pointers) use surround(node_data, buff=0.5) to auto-size the shape around the text content. This handles varying text widths without manual sizing.
**When to use**: Nodes with varying content lengths (short integers vs long hex addresses), any visualization where you want consistent padding regardless of text width.

```python
# Source: projects/manim-videos/pointers.py:13-30
def createNode(data):
    node = VGroup()
    node_data = Text(data)
    node_circle = Circle(stroke_color=BLUE)
    node_circle.set_fill(BLUE, opacity=0.5)
    node_circle.surround(node_data, buff=0.5)
    node.add(node_data, node_circle)
    return node

def createData(data):
    node = VGroup()
    node_data = Text(data)
    node_data.scale(0.8)
    node_square = Square(stroke_color=WHITE)
    node_square.set_fill(WHITE, opacity=0)
    node_square.surround(node_data, buff=0.5)
    node.add(node_data, node_square)
    return node
```

## Scene Flow

1. **Setup** (0-1s): Title "What is a pointer?" writes. Variable myNum (circle with 5) and its label "myNum" appear at center.
2. **Vocabulary** (1-4s): "variable name" and "variable data" labels appear briefly, then fade out.
3. **Reposition** (4-5s): myNum group shifts right and up to make room for pointer on the left.
4. **First pointer** (5-7s): myNumPointer label, hex address box (0x6dfed4), and arrow to myNum all write simultaneously.
5. **Second variable** (7-8s): myChar variable (circle with 'c') and label appear at bottom-right.
6. **Second pointer** (8-10s): myCharPointer label, hex address box (0x68b3a2), and arrow to myChar all write.
7. **Done** (10-16s): Wait 6s on final state showing both pointer-variable pairs.

> Full file: `projects/manim-videos/pointers.py` (112 lines)
