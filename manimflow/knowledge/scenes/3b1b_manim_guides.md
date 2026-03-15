---
source: https://github.com/pprunty/manim-interactive/blob/main/projects/guides/
project: manim-interactive
domain: [mathematics, geometry, computer_science]
elements: [label, title, equation, formula, code_block, image, group, cube, sphere, surface_3d, line, dot]
animations: [fade_in, fade_out, write, transform, rotate, draw]
layouts: [centered, edge_anchored, side_by_side]
techniques: [custom_mobject, three_d_camera]
purpose: [demonstration, definition]
mobjects: [Text, Code, ImageMobject, SVGMobject, VGroup, Cube, Prism, Sphere, SurfaceMesh, Polyhedron, Rectangle, Circle, Line]
manim_animations: [Write, FadeIn, FadeOut, Transform, Rotate, UpdateFromFunc]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 650
scene_classes: [TextScene, SlowText, FastText, FadeOutText, TransformText, AlternativeFontText, SlideInText, ScaleText, RotateText, MoveText, ColorChangeText, CombinedAnimation, HelloWorld, CodeTransform, TypewriterHelloWorld, FadeInImage, MoveImage, ImageWithBorder, ScaleImage, ShakeImage, MoveTwoImages, MorphSVGToSphere, Pyramid3D, Basic3DScene, PrismDemo, RandomMeshAnimation, SmoothedBlobScene, Prismify]
---

## Summary

A collection of beginner reference implementations for manimlib (ManimGL) covering text manipulation, code rendering, image handling, and 3D primitives. These guides serve as copy-paste starting points for common operations: writing/transforming text with different fonts and speeds, rendering syntax-highlighted code blocks, loading and animating images with borders, creating 3D objects (cubes, prisms, pyramids, spheres) with camera rotation, and mesh/surface manipulation. Each file demonstrates one category of operations through minimal scene classes.

## Design Decisions

- **One concept per scene class**: Each scene demonstrates exactly one operation (Write, FadeOut, Transform, Rotate, etc.) for easy reference and copy-pasting.
- **Minimal code per scene**: Typically 5-15 lines in construct(), showing only the essential pattern without complex composition.
- **3D camera setup pattern**: All 3D scenes use `self.camera.frame.set_euler_angles(phi=60*DEGREES, theta=45*DEGREES)` as the standard starting orientation.
- **Progressive complexity within each file**: Simple operations first (Write text), then combined operations (scale + move + color change).

## Patterns

### Pattern: Text Write with Speed Control

**What**: Basic text creation and animation using Write with configurable run_time. Demonstrates the fundamental Write animation that draws text stroke-by-stroke.

**When to use**: Any text that needs to appear as if being written. run_time=0.5 for quick labels, run_time=3 for dramatic reveals.

```python
# Source: projects/manim-interactive/projects/guides/text.py:4-8
class TextScene(Scene):
    def construct(self):
        text = Text("Hello, Manim!")
        self.play(Write(text))
        self.wait(2)
```

### Pattern: Text Slide-In with Direction

**What**: FadeIn with a direction vector (UP/DOWN) to create sliding entrance effects. The text appears to slide in from below or above.

**When to use**: Title cards, sequential information reveal, any text that should appear to come from a specific direction rather than materializing in place.

```python
# Source: projects/manim-interactive/projects/guides/text.py:53-65
class SlideInText(Scene):
    def construct(self):
        text = Text("Here is text that animates into view")
        self.play(FadeIn(text, UP))
        self.wait(1)
        self.play(FadeOut(text, run_time=1))
        self.wait(1)
        self.play(FadeIn(text, DOWN))
```

### Pattern: Syntax-Highlighted Code Block

**What**: Renders syntax-highlighted code using the Code mobject with language specification. Supports transform between different code blocks (e.g., Python to C++).

**When to use**: Algorithm explanations, code walkthroughs, showing equivalent code in different languages. The Code mobject handles syntax highlighting automatically.

```python
# Source: projects/manim-interactive/projects/guides/code.py:3-16
class HelloWorld(Scene):
    def construct(self):
        code = 'print("Hello, World!")'
        rendered_code = Code(
            code=code,
            language="python",
            alignment="LEFT",
            font="monospace"
        )
        self.play(Write(rendered_code))
        self.wait(2)
```

### Pattern: Typewriter Text Effect

**What**: Builds text character by character using a loop that creates progressively longer Text objects and transforms between them. A cursor Line follows the text edge.

**When to use**: Terminal/console simulations, dramatic character-by-character reveal, code typing demonstrations. The cursor adds authenticity.

```python
# Source: projects/manim-interactive/projects/guides/code.py:57-105
class TypewriterHelloWorld(Scene):
    def construct(self):
        text_str = "Hello, World!"
        final_text = Text(text_str, font="Monospace").scale(1.2)
        paper_rect = Rectangle(width=final_text.width + 0.5, height=final_text.height + 0.5,
                              fill_color=WHITE, fill_opacity=1)
        text_mobj = Text("", font="Monospace").scale(1.2)
        cursor = Line(ORIGIN, UP * 0.4, stroke_width=5)
        self.add(paper_rect, text_mobj, cursor)
        for i in range(len(text_str) + 1):
            partial_text = Text(text_str[:i], font="Monospace").scale(1.2)
            partial_text.move_to(paper_rect.get_center())
            self.play(Transform(text_mobj, partial_text),
                     cursor.animate.next_to(text_mobj, RIGHT, buff=0.1),
                     run_time=0.1)
```

### Pattern: Image with Border Frame

**What**: Loads a raster image via ImageMobject, creates a matching Rectangle border (stroke WHITE, width 8), and animates them scaling together.

**When to use**: Displaying reference images, thumbnails, photo frames in educational content. The border adds visual polish and makes images stand out against the background.

```python
# Source: projects/manim-interactive/projects/guides/image.py:30-52
class ImageWithBorder(Scene):
    def construct(self):
        image = ImageMobject("media/images/example.jpg").scale(0.5)
        border = Rectangle(width=image.get_width(), height=image.get_height())
        border.set_stroke(WHITE, width=8)
        border.move_to(image.get_center())
        self.add(border, image)
        self.play(border.animate.scale(1.6), image.animate.scale(1.6))
```

### Pattern: 3D Camera Setup and Object Rotation

**What**: Standard 3D scene setup using euler angles for camera orientation, then animating object rotation around different axes. Works with Cube, Prism, Sphere, and Polyhedron.

**When to use**: Any 3D visualization - mathematical surfaces, geometric solids, spatial transformations. The euler angle setup is the canonical way to orient the 3D camera in manimlib.

```python
# Source: projects/manim-interactive/projects/guides/3d.py:54-85
class Basic3DScene(ThreeDScene):
    def construct(self):
        self.camera.frame.set_euler_angles(
            phi=60 * DEGREES,
            theta=45 * DEGREES
        )
        cube = Cube()
        for face in cube:
            face.set_color(BLUE)
            face.set_opacity(0.7)
        cube.scale(2)
        self.play(Rotate(cube, angle=PI, axis=UP), run_time=3)
        self.play(Rotate(cube, angle=PI / 2, axis=RIGHT), run_time=2)
```

### Pattern: Sphere Mesh with Random Perturbation

**What**: Creates a Sphere with SurfaceMesh overlay, then perturbs vertices randomly using UpdateFromFunc to create organic blob-like shapes. Demonstrates surface manipulation at the point level.

**When to use**: Creating organic 3D shapes, demonstrating surface deformations, procedural geometry, any scenario where you need to show a surface being warped or deformed.

```python
# Source: projects/manim-interactive/projects/guides/3d.py:120-161
class RandomMeshAnimation(ThreeDScene):
    def construct(self):
        self.camera.frame.set_euler_angles(phi=60 * DEGREES, theta=45 * DEGREES)
        sphere = Sphere(radius=2.0, resolution=(20, 20), color=BLUE_E)
        mesh = SurfaceMesh(uv_surface=sphere, resolution=(10, 10),
                          stroke_width=1.5, stroke_color=WHITE)
        self.add(sphere, mesh)
        self.play(UpdateFromFunc(mesh, randomize_mesh),
                 run_time=5, rate_func=there_and_back)
```

### Pattern: Prismify - Extrude 2D VMobject to 3D

**What**: Takes any 2D VMobject and extrudes it into 3D by creating wall faces between adjacent anchor points and a reversed-points top face. Creates proper 3D solids from flat shapes.

**When to use**: Converting 2D diagrams to 3D, creating custom 3D shapes from polygon outlines, any situation where you need a 3D solid with a specific cross-section.

```python
# Source: projects/manim-interactive/projects/guides/3d.py:164-179
class Prismify(VGroup3D):
    def __init__(self, vmobject, depth=1.0, direction=IN, **kwargs):
        vect = depth * direction
        pieces = [vmobject.copy()]
        points = vmobject.get_anchors()
        for p1, p2 in adjacent_pairs(points):
            wall = VMobject()
            wall.match_style(vmobject)
            wall.set_points_as_corners([p1, p2, p2 + vect, p1 + vect])
            pieces.append(wall)
        top = vmobject.copy()
        top.shift(vect)
        top.reverse_points()
        pieces.append(top)
        super().__init__(*pieces, **kwargs)
```

## Composition

- **Text scenes**: Text centered by default, font_size varies. Custom fonts via font="Arial".
- **Code blocks**: scale(0.6) for side-by-side comparison, alignment="LEFT", font="monospace".
- **Images**: scale(0.33-0.5) for initial display, to_corner() for positioning.
- **3D scenes**: Camera phi=60-75 degrees, theta=30-45 degrees. Objects at ORIGIN, scale(2) for visibility.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Default text | WHITE | On black background |
| Code background | Default | Code mobject handles it |
| Image border | WHITE | stroke_width=8 |
| Paper rectangle | WHITE fill | fill_opacity=1, stroke BLACK width 2 |
| 3D objects | BLUE / BLUE_E | opacity=0.7 for transparency |
| Blob gradient | RED to ORANGE to YELLOW | set_color_by_gradient |
| Cursor | Default | Line, stroke_width=5 |

## manimlib Notes

- `from manimlib import *` for all guides
- `Text()` for plain text, `Code()` for syntax-highlighted blocks
- `ImageMobject()` for raster images, `SVGMobject()` for vector
- `ThreeDScene` base class required for 3D (provides camera frame euler angles)
- `camera.frame.set_euler_angles()` is the manimlib way (not `self.set_camera_orientation()`)
- `Polyhedron(vertices, faces)` for arbitrary 3D solids
- `SurfaceMesh(uv_surface=sphere)` for wireframe overlays on parametric surfaces
- `VGroup3D` for 3D-aware grouping (used by Prismify)
