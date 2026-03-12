"""Manim API reference - injected into LLM context for accurate code generation."""

MANIM_API_REFERENCE = """
## Manim Community Edition 0.19.0 API Reference

### IMPORTS
```python
from manim import *
import numpy as np
```

### SCENE CLASSES
- `Scene` - Standard 2D scene (use this by default)
- `ThreeDScene` - For 3D animations
- `MovingCameraScene` - Animated camera movements

Core methods:
- `self.play(*animations, run_time=1)` - Play animations
- `self.wait(duration=1)` - Pause
- `self.add(*mobjects)` - Add without animation
- `self.remove(*mobjects)` - Remove without animation
- `self.camera.background_color = BLACK` - Set background

### AVAILABLE COLORS (use ONLY these)
Primary: RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK, WHITE, GRAY, BLACK, GOLD
Extended: DARK_BLUE, DARK_GRAY, LIGHT_GRAY, LIGHT_PINK, MAROON
With shades: BLUE_A through BLUE_E, RED_A through RED_E, GREEN_A through GREEN_E, etc.
Also: TEAL, TEAL_A-E (these ARE valid in Manim 0.19.0)
Hex colors: "#FF5733", "#00FFFF" etc.

### TEXT & MATH
```python
# Regular text
text = Text("Hello", font_size=36, color=WHITE, weight=BOLD)

# LaTeX math (pure math only — NO \\text{} command, it causes LaTeX errors)
eq = MathTex(r"E = mc^2", font_size=48, color=YELLOW)
eq = MathTex(r"\\int_0^1 x^2 dx = \\frac{1}{3}")
# NEVER use \\text{} inside MathTex — use Text() for words, MathTex for math only
# BAD:  MathTex(r"\\text{Area} = \\pi r^2")  # CRASHES — \\text needs standalone.cls
# GOOD: Text("Area = ", font_size=32) next to MathTex(r"\\pi r^2")

# Multi-part MathTex (for selective coloring)
eq = MathTex("x^2", "+", "y^2", "=", "r^2")
eq[0].set_color(RED)  # Color individual parts

# Bulleted list
bullets = BulletedList("Point 1", "Point 2", font_size=24)

# Code display
code = Code("file.py", language="python")
```

### GEOMETRY
```python
# Basic shapes
circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
square = Square(side_length=2, color=RED)
rect = Rectangle(width=4, height=2, color=GREEN)
dot = Dot(point=ORIGIN, radius=0.08, color=YELLOW)
line = Line(start=LEFT, end=RIGHT, color=WHITE)
arrow = Arrow(start=LEFT, end=RIGHT, color=BLUE, buff=0)
double_arrow = DoubleArrow(LEFT, RIGHT)
arc = Arc(radius=1, start_angle=0, angle=PI/2, color=RED)
angle = Angle(line1, line2, radius=0.5)

# Dashed
dashed = DashedLine(LEFT, RIGHT)
dashed_vmobj = DashedVMobject(some_curve, num_dashes=20)

# Braces
brace = Brace(mobject, direction=DOWN)
brace_label = brace.get_text("label")

# Surrounding
box = SurroundingRectangle(mobject, color=YELLOW, buff=0.1)
```

### GRAPHING & CURVES
```python
# Axes
axes = Axes(
    x_range=[-5, 5, 1],  # [min, max, step]
    y_range=[-3, 3, 1],
    x_length=10,
    y_length=6,
    axis_config={"color": GRAY, "stroke_width": 2},
)
labels = axes.get_axis_labels(x_label="x", y_label="y")

# Function graph on axes
graph = axes.plot(lambda x: x**2, x_range=[-2, 2], color=BLUE)
area = axes.get_area(graph, x_range=[0, 1], color=BLUE, opacity=0.3)

# Parametric curve (standalone)
curve = ParametricFunction(
    lambda t: np.array([np.cos(t), np.sin(t), 0]),
    t_range=[0, 2*PI, 0.01],  # [start, end, step]
    stroke_width=4,
    color=RED,
)

# Number plane with grid
plane = NumberPlane(
    x_range=[-5, 5, 1],
    y_range=[-5, 5, 1],
    background_line_style={"stroke_opacity": 0.2},
)

# Polar plane
polar = PolarPlane(radius_max=3)

# Bar chart
chart = BarChart(values=[1, 2, 4, 3], bar_names=["A", "B", "C", "D"])

# Vector field
field = ArrowVectorField(lambda p: np.array([p[1], -p[0], 0]))
```

### ANIMATIONS - CREATION
```python
self.play(Create(mobject), run_time=2)          # Draw stroke
self.play(Uncreate(mobject))                     # Reverse draw
self.play(Write(text), run_time=1.5)             # Write text
self.play(Unwrite(text))                         # Reverse write
self.play(FadeIn(mobject))                       # Fade in
self.play(FadeIn(mobject, shift=UP))             # Fade in with direction
self.play(FadeOut(mobject))                      # Fade out
self.play(GrowFromCenter(mobject))               # Grow from center
self.play(GrowFromPoint(mobject, point))         # Grow from point
self.play(GrowArrow(arrow))                      # Grow an arrow
self.play(SpinInFromNothing(mobject))            # Spin in
self.play(SpiralIn(group))                       # Spiral group in
self.play(DrawBorderThenFill(mobject))           # Draw border, then fill
self.play(ShowPassingFlash(mobject))             # Flash effect
self.play(AddTextLetterByLetter(text))           # Typewriter effect
```

### ANIMATIONS - TRANSFORM
```python
self.play(Transform(source, target), run_time=2)         # Morph source into target
self.play(ReplacementTransform(source, target))           # Replace source with target
self.play(TransformFromCopy(source, target))              # Copy source, morph to target
self.play(FadeTransform(source, target))                  # Fade between
self.play(TransformMatchingShapes(source, target))        # Match shapes
self.play(TransformMatchingTex(source_tex, target_tex))   # Match LaTeX parts
```

### ANIMATIONS - MOVEMENT & PROPERTY
```python
# .animate syntax (preferred for property changes)
self.play(mobject.animate.shift(RIGHT * 2))
self.play(mobject.animate.move_to(UP * 2))
self.play(mobject.animate.scale(2))
self.play(mobject.animate.rotate(PI/2))
self.play(mobject.animate.set_color(RED))
self.play(mobject.animate.set_opacity(0.5))
self.play(mobject.animate.scale(0.7).move_to(UP * 3))  # Chain multiple

# Specific animations
self.play(Rotate(mobject, angle=PI, axis=UP))
self.play(MoveAlongPath(dot, path))
self.play(Indicate(mobject))                    # Flash highlight
self.play(Flash(point, color=YELLOW))           # Flash at point
self.play(Wiggle(mobject))                      # Wiggle effect
self.play(Circumscribe(mobject, color=YELLOW))  # Draw circle around
self.play(FocusOn(point))                       # Focus camera
self.play(ApplyWave(mobject))                   # Wave distortion
```

### ANIMATIONS - COMPOSITION
```python
# Multiple simultaneous
self.play(Create(circle), Write(text), run_time=2)

# Staggered
self.play(LaggedStart(*[FadeIn(m) for m in group], lag_ratio=0.2))
self.play(AnimationGroup(*anims, lag_ratio=0.1))

# Sequential in one play
self.play(Succession(Create(a), Create(b), Create(c)))
```

### POSITIONING
```python
# Absolute
mobject.move_to(ORIGIN)
mobject.move_to(UP * 2 + RIGHT * 3)
mobject.to_corner(UL)  # UL, UR, DL, DR
mobject.to_edge(UP, buff=0.5)

# Relative
mobject.next_to(other, RIGHT, buff=0.5)
mobject.align_to(other, UP)
mobject.shift(LEFT * 2)

# Center
mobject.center()
```

### GROUPING & LAYOUT
```python
group = VGroup(obj1, obj2, obj3)
group.arrange(DOWN, buff=0.3)                          # Vertical stack
group.arrange(RIGHT, buff=0.5)                         # Horizontal row
group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)       # Left-aligned stack
group.arrange_in_grid(rows=2, cols=3, buff=0.5)        # Grid layout

# Add/remove
group.add(new_obj)
group.remove(old_obj)
```

### STYLING
```python
# Colors
mobject.set_color(RED)
mobject.set_color_by_gradient(RED, BLUE, GREEN)
text.set_color_by_gradient(BLUE, PURPLE)

# Stroke and fill
mobject.set_stroke(color=WHITE, width=2, opacity=0.8)
mobject.set_fill(color=BLUE, opacity=0.5)

# Opacity
mobject.set_opacity(0.5)
```

### RATE FUNCTIONS
linear, smooth, rush_into, rush_from, slow_into,
there_and_back, there_and_back_with_pause,
ease_in_sine, ease_out_sine, ease_in_out_sine,
ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
ease_in_expo, ease_out_expo, ease_in_out_expo,
ease_out_bounce, ease_in_out_elastic, wiggle

### CONSTANTS
UP, DOWN, LEFT, RIGHT, ORIGIN, IN, OUT
UL, UR, DL, DR (corners)
PI, TAU (=2*PI), DEGREES
X_AXIS, Y_AXIS, Z_AXIS
SMALL_BUFF (0.1), MED_SMALL_BUFF (0.25), MED_LARGE_BUFF (0.5), LARGE_BUFF (1.0)

### CAMERA (MovingCameraScene — zoom, pan, follow)
```python
# Use MovingCameraScene instead of Scene for camera control
class GeneratedScene(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BLACK

        # Save initial camera state (restore later)
        self.camera.frame.save_state()

        # ZOOM IN on a specific element
        self.play(self.camera.frame.animate.scale(0.5).move_to(element), run_time=2)

        # ZOOM OUT to see full scene
        self.play(self.camera.frame.animate.scale(2).move_to(ORIGIN), run_time=2)

        # PAN to a specific position
        self.play(self.camera.frame.animate.move_to(RIGHT * 4), run_time=2)

        # AUTO-ZOOM to fit specific mobjects with margin
        self.play(self.camera.auto_zoom([obj1, obj2], margin=0.5))

        # RESTORE to original view
        from manim import Restore
        self.play(Restore(self.camera.frame), run_time=1.5)

        # ZOOM + PAN in one animation
        self.play(self.camera.frame.animate.move_to(target).set(width=6), run_time=2)
```

### VALUE TRACKING (for animated numbers)
```python
tracker = ValueTracker(0)
number = always_redraw(lambda: DecimalNumber(tracker.get_value()).move_to(UP))
self.add(number)
self.play(tracker.animate.set_value(5), run_time=3)
```

### UPDATERS
```python
# Always redraw (recreates each frame)
label = always_redraw(lambda: Text(f"x = {tracker.get_value():.1f}").move_to(UP))

# Add updater function
dot.add_updater(lambda m, dt: m.shift(RIGHT * dt))
# Remove later
dot.clear_updaters()
```

### COMMON PATTERNS

# Progressive equation building:
eq1 = MathTex("a^2")
eq2 = MathTex("a^2", "+", "b^2")
eq3 = MathTex("a^2", "+", "b^2", "=", "c^2")
self.play(Write(eq1))
self.play(TransformMatchingTex(eq1, eq2))
self.play(TransformMatchingTex(eq2, eq3))

# Annotated diagram:
circle = Circle(color=BLUE)
label = Text("r", font_size=24).next_to(circle, RIGHT)
brace = Brace(circle, DOWN)
brace_text = brace.get_text("diameter")

# Color-coded explanation:
formula = MathTex("F", "=", "m", "a")
formula[0].set_color(RED)    # Force
formula[2].set_color(BLUE)   # Mass
formula[3].set_color(GREEN)  # Acceleration
"""
