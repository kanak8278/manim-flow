---
source: https://github.com/3b1b/videos/blob/main/once_useful_constructs/fractals.py
project: videos
domain: [mathematics, geometry]
elements: [group, parametric_curve]
animations: [transform, fade_in]
layouts: [centered]
techniques: [custom_mobject, factory_pattern, color_gradient]
purpose: [demonstration, exploration, definition]
mobjects: [VMobject, VGroup, Polygon, RegularPolygon, Circle, PiCreature]
manim_animations: []
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 628
scene_classes: []
---

## Summary

A recursive fractal generation framework built on VMobject. Provides both a procedural `fractalify()` function that adds random fractal roughness to any VMobject path, and a `SelfSimilarFractal` base class for building classical fractals (Sierpinski triangle, diamond fractal, pentagonal fractal) through recursive self-similar subdivision. The system uses a clean template method pattern: subclasses define `get_seed_shape()` and `arrange_subparts()`, and the base class handles recursive construction and color gradients.

## Design Decisions

- **Template method pattern for fractals**: Base class handles recursion depth, height normalization, and color gradients. Subclasses only define the seed shape and spatial arrangement, making it trivial to create new fractal types.
- **Color gradient across recursion**: `set_color_by_gradient(*self.colors)` applied after construction gives visual depth without per-level color management.
- **Procedural fractalification as separate function**: `fractalify()` works on any existing VMobject by perturbing anchor points with random offsets scaled by a fractal dimension parameter. This separates "make something look fractal" from "build a self-similar structure."
- **Height normalization at each recursion level**: Every `get_order_n_self()` call normalizes to `self.height` and centers, so subpart arrangement code works in relative coordinates.

## Composition

- **SelfSimilarFractal**: Default height=4, centered. Order controls recursion depth (default 5).
- **Sierpinski**: 3 subparts, equilateral triangle seed (RIGHT, sqrt(3)*UP, LEFT).
- **DiamondFractal**: 4 subparts, RegularPolygon(n=4), arranged in compass directions rotated 45 degrees.
- **PentagonalFractal**: 5 subparts, RegularPolygon(n=5), height=6, shifted up and rotated by 2pi/5.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| SelfSimilarFractal default | RED to WHITE gradient | stroke_width=1, fill_opacity=1 |
| DiamondFractal | GREEN_E to YELLOW gradient | height=4 |
| PentagonalFractal | MAROON_B to YELLOW to RED | height=6 |
| PiCreatureFractal | 10-color array | BLUE_D, BLUE_B, MAROON_B, MAROON_D, GREY, YELLOW, RED, GREY_BROWN, RED, RED_E |

## Patterns

### Pattern: Template Method Fractal Construction

**What**: A base class that recursively constructs self-similar fractals. Subclasses only define `get_seed_shape()` (the base shape) and `arrange_subparts()` (how copies are positioned). The base class handles recursion, height normalization, centering, and color gradients.

**When to use**: Any self-similar geometric pattern - Sierpinski triangles, Koch snowflakes, tree fractals, Cantor sets. Also applicable to recursive visual decompositions in algorithm visualization (divide-and-conquer diagrams).

```python
# Source: projects/videos/once_useful_constructs/fractals.py:74-114
class SelfSimilarFractal(VMobject):
    order = 5
    num_subparts = 3
    height = 4
    colors = [RED, WHITE]

    def get_order_n_self(self, order):
        if order == 0:
            result = self.get_seed_shape()
        else:
            lower_order = self.get_order_n_self(order - 1)
            subparts = [lower_order.copy() for x in range(self.num_subparts)]
            self.arrange_subparts(*subparts)
            result = VGroup(*subparts)
        result.set_height(self.height)
        result.center()
        return result

class Sierpinski(SelfSimilarFractal):
    def get_seed_shape(self):
        return Polygon(RIGHT, np.sqrt(3) * UP, LEFT)

    def arrange_subparts(self, *subparts):
        tri1, tri2, tri3 = subparts
        tri1.move_to(tri2.get_corner(DOWN + LEFT), UP)
        tri3.move_to(tri2.get_corner(DOWN + RIGHT), UP)
```

### Pattern: Procedural Fractal Roughness

**What**: Adds fractal-like roughness to any VMobject path by iteratively inserting random anchor points with perpendicular offsets scaled by a fractal dimension parameter. The dimension controls how "rough" the result looks (1.05 = subtle, higher = more jagged).

**When to use**: Making smooth curves look natural or organic - coastlines, mountain silhouettes, rough boundaries. Also useful for visual effects where you want to "fractalify" an existing shape without building it from scratch.

```python
# Source: projects/videos/once_useful_constructs/fractals.py:30-71
def fractalify(vmobject, order=3, *args, **kwargs):
    for x in range(order):
        fractalification_iteration(vmobject)
    return vmobject

def fractalification_iteration(vmobject, dimension=1.05, num_inserted_anchors_range=list(range(1, 4))):
    num_points = vmobject.get_num_points()
    if num_points > 0:
        original_anchors = [
            vmobject.point_from_proportion(x)
            for x in np.linspace(0, 1 - 1. / num_points, num_points)
        ]
        new_anchors = []
        for p1, p2 in zip(original_anchors, original_anchors[1:]):
            num_inserts = random.choice(num_inserted_anchors_range)
            # ... offset calculation using fractal dimension ...
            offset_unit_vect = rotate_vector(unit_vect, np.pi / 2)
            inserted_points = [
                point + u * offset_len * offset_unit_vect
                for u, point in zip(it.cycle([-1, 1]), inserted_points)
            ]
            new_anchors += [p1] + inserted_points
        vmobject.set_points_as_corners(new_anchors)
```

## Scene Flow

1. **Fractal construction**: Recursive build from order 0 (seed shape) up to target order, with copies arranged at each level.
2. **Color application**: Gradient applied across all submobjects after construction.
3. **Display**: Centered on screen at specified height.
