---
source: https://github.com/3b1b/videos/blob/main/_2015/pythagorean_proof.py
project: videos
domain: [geometry, mathematics]
elements: [line, label, equation, surrounding_rect, grid]
animations: [write, draw, transform, color_change]
layouts: [centered, grid, side_by_side]
techniques: [helper_function, custom_mobject]
purpose: [proof, demonstration, step_by_step]
mobjects: [Polygon, Line, OldTex, Square, Circle, Arrow]
manim_animations: [ShowCreation, Transform]
scene_type: Scene
manim_version: manimlib
complexity: beginner
lines: 509
scene_classes: [Triangle, DrawTriangle, DrawAllThreeSquares, DrawCSquareWithAllTraingles, ShowRearrangementInBigSquare]
---

## Summary

Visualizes the classic rearrangement proof of the Pythagorean theorem (a^2 + b^2 = c^2). A right triangle with labeled sides a, b, c is used to construct squares on each side. Four copies of the triangle are arranged inside a (a+b)x(a+b) square in two different configurations — one leaving c^2 as the inner gap, the other leaving a^2+b^2. The proof is entirely geometric with colored regions highlighting areas. Uses the very early manimlib API (pre-2017) with region_from_polygon_vertices for area coloring.

## Design Decisions

- **Color coding: a=BLUE, b=MAROON_D, c=YELLOW**: Each side of the triangle and its corresponding square share a color. The triangle edges are colored to match: edge_colors=[B_COLOR, C_COLOR, A_COLOR].
- **Fixed point coordinates**: All geometry is built from 9 hardcoded POINTS array coordinates. This avoids computed geometry and makes the construction exact. Triangles are placed by matching hypotenuse endpoints.
- **Right angle marker**: A small elbow (two perpendicular lines with nudge=0.2) at the right angle vertex. Created manually with add_line.
- **Two-configuration proof**: Configuration 1: four triangles + c^2 central square. Configuration 2: rearranged triangles reveal a^2 + b^2 separately. Same total area proves the theorem.
- **Region coloring**: Uses set_color_region with region_from_polygon_vertices — an older manimlib API that fills regions bounded by polygon vertices. Triangles filled BLUE_D, c-square filled YELLOW.
- **place_hypotenuse_on method**: Scales and rotates a triangle so its hypotenuse matches two given points. This enables placing triangle copies at arbitrary positions in the big square.

## Composition

- **Triangle vertices**: POINTS[0]=DOWN, POINTS[1]=2*UP, POINTS[2]=DOWN+RIGHT. Right angle at POINTS[0].
- **a-square**: POINTS[0,2,4,3] — BLUE.
- **b-square**: POINTS[1,0,5,6] — MAROON_D.
- **c-square**: POINTS[1,2,7,8] — YELLOW.
- **Labels**: OldTex("a"), OldTex("b"), OldTex("c") at scale=0.5 (TEX_MOB_SCALE_FACTOR). Positioned at edge midpoint + normal direction * nudge=0.3.
- **Big square**: (a+b) side length. Underbrace below, side_brace rotated 90deg.
- **Elbow**: 0.2 offset from vertex, two perpendicular lines.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Side a / a-square | BLUE | A_COLOR constant |
| Side b / b-square | MAROON_D | B_COLOR constant |
| Side c / c-square | YELLOW | C_COLOR constant |
| Triangle fill | BLUE_D | region_from_polygon_vertices |
| Right angle marker | WHITE | Two short perpendicular lines |
| Labels | WHITE | scale=0.5 |
| Grid lines | WHITE | Full screen lines for construction |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Triangle drawing | instant | self.add() — early API, no animation |
| Region coloring | instant | set_color_region — static |
| Rearrangement | manual | Separate scene classes per step |

## Patterns

### Pattern: Triangle with Hypotenuse Placement

**What**: A custom Triangle Polygon with a place_hypotenuse_on(point1, point2) method. Scales the triangle so its hypotenuse matches the length between two points, rotates to align, and shifts to match position. Also has add_letter for positioning side labels along edges with outward-facing normal offset.

**When to use**: Any geometric proof involving triangle rearrangement, tiling, or tessellation. The place_hypotenuse_on pattern enables placing triangles at arbitrary positions defined by two endpoints.

```python
# Source: projects/videos/_2015/pythagorean_proof.py:67-75
def place_hypotenuse_on(self, point1, point2):
    start1, start2 = self.get_vertices()[[1, 2]]
    target_vect = np.array(point2) - np.array(point1)
    curr_vect = start2 - start1
    self.scale(get_norm(target_vect) / get_norm(curr_vect))
    self.rotate(angle_of_vector(target_vect) - angle_of_vector(curr_vect))
    self.shift(point1 - self.get_vertices()[1])
    return self
```

### Pattern: Geometric Proof by Rearrangement

**What**: Two configurations of the same four triangles inside a big square. In DrawCSquareWithAllTraingles, four triangles surround a c^2 square. In ShowRearrangementInBigSquare, the same triangles are rearranged to reveal a^2 and b^2 squares. Since the big square area is the same in both cases, a^2+b^2=c^2.

**When to use**: Any area-based proof, dissection proof, or rearrangement argument in geometry. The pattern of showing two configurations of the same pieces is a fundamental proof visualization technique.

```python
# Source: projects/videos/_2015/pythagorean_proof.py:488-509
class ShowRearrangementInBigSquare(DrawCSquareWithAllTraingles):
    def construct(self):
        self.add(Square(side_length=4, color=WHITE))
        DrawCSquareWithAllTraingles.construct(self)
        self.remove(self.c_square)
        self.triangles[1].shift(LEFT)
        for i, j in [(0, 2), (3, 1)]:
            self.triangles[i].place_hypotenuse_on(
                *self.triangles[j].get_vertices()[[2, 1]]
            )
```

## Scene Flow

1. **Triangle**: Right triangle drawn with side labels a, b, c and right angle marker.
2. **Three Squares**: Squares on each side appear (a^2 BLUE, b^2 MAROON, c^2 YELLOW).
3. **Big Square with c^2**: Four triangle copies arranged inside (a+b)x(a+b) square. Central c^2 gap highlighted YELLOW.
4. **Rearrangement**: Same four triangles moved to leave a^2 and b^2 gaps instead. Regions colored.
5. **Conclusion**: Both configurations have same total area. Therefore a^2 + b^2 = c^2.

> Note: This is a very early manimlib file (2015). Uses deprecated APIs: region_from_polygon_vertices, set_color_region, Underbrace, direct constants import. The scene classes use static `construct` calls and `self.add` without animation.
