---
source: https://github.com/nipunramk/Reducible/blob/main/2021/MarchingSquares/scene.py
project: Reducible
domain: [computer_science, algorithms, geometry, mathematics]
elements: [grid, dot, line, pixel_grid, function_plot, label, surrounding_rect, box]
animations: [fade_in, fade_out, write, draw, transform, color_change, grow, lagged_start]
layouts: [grid, centered, side_by_side]
techniques: [custom_mobject, data_driven, zoomed_scene, progressive_disclosure, factory_pattern]
purpose: [step_by_step, demonstration, process, exploration, simulation]
mobjects: [Circle, Dot, Line, Polygon, VGroup, DecimalNumber, Square, Cube, Text, Tex, NumberPlane]
manim_animations: [FadeIn, FadeOut, Create, Write, Transform, LaggedStartMap]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 5160
scene_classes: [MarchingSquare, MarchingSquaresUtils, MarchingCube, MarchingCubesUtils, Ball, MetaBalls, Introduction, TwoMetaball, ShowEasyCases, CirclesAndEllipses, DrawFunction, GuessImplicitFunctionValues, ImplicitFunctionCases, FocusOnContour, IntroMarchingSquaresIdea, MarchingSquaresCases, LerpImprovement, MarchingSquaresSummary, EnergyFieldsTakeTwoCut, MetaBallsWithLabels, MarchingCubes3DCameraRotation, MarchingCubesAnimation]
---

## Summary

Visualizes the marching squares algorithm for implicit function contouring, extended to marching cubes for 3D. Implements the full algorithm as a reusable MarchingSquaresUtils scene base class: sample space generation, implicit function evaluation, dot coloring by inside/outside classification, and contour line/polygon extraction via lookup tables. Features metaball simulations where bouncing circles merge via the marching squares contour. Also includes ZoomedScene for magnified contour inspection.

## Design Decisions

- **MarchingSquare as algorithm class**: Pure data class holding four corner positions and a function map. Handles case lookup, edge interpolation (lerp), and contour line/polygon generation. No Manim dependencies in the core logic.
- **MarchingSquaresUtils as base Scene**: Provides set_sample_space(), get_implicit_function_samples(), march_squares(), and dot visualization. Scene classes inherit from this to get algorithm utilities for free.
- **Color-coded dots**: Inside points shown as PURE_GREEN, outside as BLUE. This binary classification is the foundation of the marching squares visualization.
- **Lookup table approach**: 16 cases encoded as dict mapping case number to edge pairs. Polygon variant maps to mixed corner/edge point sequences for filled regions.
- **Linear interpolation on edges**: lerp() between corner values to find exact contour crossing point. This is the key improvement over midpoint approximation, shown explicitly in LerpImprovement scene.
- **Gradient coloring**: Optional position_to_color() function maps contour position to color, creating rainbow-like metaball contours.
- **Ball as Circle subclass**: Reusable physics ball with velocity, mass, position tracking, and boundary collision detection. Used for both metaball centers and collision detection demos.
- **ZoomedScene for detail**: FocusOnContour and IntroMarchingSquaresIdea use ZoomedScene to magnify individual marching squares while keeping the full contour visible.

## Composition

- **Sample space**: x_range=(-7.5, 7.5), y_range=(-4, 4), configurable step sizes (default 0.5, fine 0.075 for metaballs)
- **Dots**: radius=0.05, colored by inside/outside condition
- **Contour lines**: Line between interpolated edge points, stroke width=2-5
- **Metaball circles**: Ball(radius=0.3-0.9), initial grid of 8 positions
- **Marching cube 3D**: ThreeDScene, vertex labeling following paulbourke.net conventions
- **Zoomed display**: ZoomedScene with camera frame + inset

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Inside dots | PURE_GREEN | Dot radius=0.05 |
| Outside dots | BLUE | Dot radius=0.05 |
| Contour lines | YELLOW (CONTOUR_COLOR) | stroke_width=2-5 |
| Contour polygons | YELLOW fill | opacity=1, stroke_width=1 |
| Gradient contours | position_to_color() | Rainbow based on position |
| Metaball bodies | BLACK (invisible) | Only contour visible |
| Key algorithm text | YELLOW | set_color on specific substring |
| Box boundary | COBALT_BLUE | For collision scenes |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Sample space display | instant | self.add(dots) |
| March squares contour | instant | self.add(contour), computed offline |
| Metaball simulation | 120s | Real-time updater recomputes contour each frame |
| Zoomed scene activation | ~1.5s | Camera frame zoom |
| Case-by-case explanation | ~2s each | 16 cases shown sequentially |
| Total video | ~25 minutes | Full marching squares tutorial |

## Patterns

### Pattern: Marching Squares Algorithm as Scene Utility

**What**: MarchingSquaresUtils provides the full marching squares pipeline as inheritable methods: set_sample_space() creates the grid, get_implicit_function_samples() evaluates the function, march_squares() generates contour VGroup. Any scene inheriting this gets contouring for free.

**When to use**: Implicit function visualization, contour plots, level set rendering, metaball effects, any 2D scalar field visualization that needs boundary extraction.

```python
# Source: projects/Reducible/2021/MarchingSquares/scene.py:115-269
class MarchingSquaresUtils(Scene):
    def set_sample_space(self, x_range=(-7.5, 7.5), y_range=(-4, 4),
                         x_step=0.5, y_step=0.5):
        self.sample_space = []
        for x in np.arange(*self.get_iterable_range(x_range, x_step)):
            for y in np.arange(*self.get_iterable_range(y_range, y_step)):
                self.sample_space.append(np.array([x, y, 0.]))

    def march_squares(self, condition, implicit_function, value=1,
                      line_width=2, gradient=False, fill=False, color=CONTOUR_COLOR):
        contour = VGroup()
        for key in self.function_map:
            marching_square = self.get_marching_square(key)
            case = self.get_case(square_corners, condition, implicit_function)
            lines = self.process_case(case, marching_square, implicit_function,
                                      value=value, width=line_width, gradient=gradient)
            if lines:
                contour.add(lines)
        return contour
```

### Pattern: Real-Time Metaball Simulation via Updater

**What**: Bouncing Ball objects with velocity vectors. An updater recomputes the implicit function (sum of 1/distance^2 for all balls), re-runs marching squares, and calls `contour.become(new_contour)` every frame. This creates smooth, real-time metaball merging animations.

**When to use**: Fluid-like blob effects, energy field visualization, any simulation where contours of a dynamic scalar field need to animate smoothly.

```python
# Source: projects/Reducible/2021/MarchingSquares/scene.py:559-638
class MetaBalls(MarchingSquaresUtils):
    def construct(self):
        balls = VGroup(*[Ball(radius=np.random.uniform(0.3, 0.9)) for _ in range(8)])
        self.set_sample_space(x_step=0.075, y_step=0.075)
        implicit_function = implicit_function_group_of_circles(balls)
        function_map = self.get_implicit_function_samples(implicit_function)
        condition = lambda x: x >= 1
        contour = self.march_squares(condition, implicit_function, line_width=5, gradient=True)
        self.add(contour)

        def update_ball(balls, dt):
            for ball in balls:
                ball.shift(ball.velocity * dt)
                handle_collision_with_boundary(ball)
            implicit_function = implicit_function_group_of_circles(balls)
            self.get_implicit_function_samples(implicit_function)
            new_contour = self.march_squares(condition, implicit_function,
                                             line_width=5, gradient=True)
            contour.become(new_contour)
        balls.add_updater(update_ball)
```

### Pattern: Lookup Table Case Processing

**What**: 16 marching square cases encoded in a dict mapping case number (4-bit binary from corner classification) to edge pairs. Each edge pair defines a contour line segment. Separate polygon lookup table for filled rendering.

**When to use**: Any algorithm with a finite set of geometric cases (marching cubes 256 cases, 2D cellular automata patterns, tile-based procedural generation).

```python
# Source: projects/Reducible/2021/MarchingSquares/scene.py:13-95
class MarchingSquare:
    NORTH = (0, 1)
    EAST = (1, 2)
    SOUTH = (2, 3)
    WEST = (3, 0)

    lookup_table = {
        1: [(SOUTH, WEST)],
        2: [(EAST, SOUTH)],
        3: [(EAST, WEST)],
        # ... 14 non-trivial cases
        5: [(WEST, NORTH), (EAST, SOUTH)],  # Ambiguous saddle case
    }

    def get_lines_for_case(self, case, implicit_function, value=1, width=2, color=CONTOUR_COLOR):
        lines = VGroup()
        for edge1, edge2 in MarchingSquare.lookup_table[case]:
            start = self.get_point_on_edge(edge1, implicit_function, value=value)
            end = self.get_point_on_edge(edge2, implicit_function, value=value)
            lines.add(Line(start, end, color=color).set_stroke(width=width))
        return lines
```

## Scene Flow

1. **Introduction** (0-3min): Task statement "Generate Metaballs." Initial questions about modeling. Key algorithm: Marching Squares.
2. **Implicit Functions** (3-8min): Show circles/ellipses as implicit functions. Sample space with colored dots (inside/outside). Zoom into individual squares.
3. **Case Analysis** (8-14min): 16 cases explained with corner classification. Edge interpolation (lerp) for precise contour positions.
4. **Full Algorithm** (14-18min): March across entire grid, assemble contour. Summary with different step sizes showing quality tradeoff.
5. **Parallelization** (18-20min): Each square independent, ideal for GPU.
6. **Energy Fields & Metaballs** (20-24min): Implicit function as sum of inverse distances. Bouncing ball simulation with real-time contour updates.
7. **Marching Cubes 3D** (24-25min): Extension to 3D with ThreeDScene camera rotation.
