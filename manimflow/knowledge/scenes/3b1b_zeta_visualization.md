---
source: https://github.com/3b1b/videos/blob/main/_2016/zeta.py
project: videos
domain: [complex_analysis, number_theory, mathematics]
elements: [complex_plane, grid, function_plot, dot, arrow, label, equation, pi_creature]
animations: [write, draw, transform, fade_in, fade_out, lagged_start]
layouts: [centered, grid]
techniques: [custom_mobject, helper_function, progressive_disclosure]
purpose: [exploration, demonstration, definition, overview]
mobjects: [ComplexPlane, VGroup, Line, OldTex, OldTexText, Dot, Arrow, BackgroundRectangle, DecimalNumber]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write, ApplyMethod, LaggedStartMap, Blink, ReplacementTransform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 3407
scene_classes: [ZetaTransformationScene, IntroduceZeta, TestZetaOnHalfPlane, PreviewZetaAndContinuation, WhyPeopleMayKnowIt, ComplexValuedFunctions, AssumeKnowledgeOfComplexNumbers]
---

## Summary

Visualizes the Riemann zeta function as a complex transformation — the complex plane is drawn as a colored grid, then the grid is deformed by applying zeta(s) to every point. The ZetaTransformationScene base class handles grid preparation (adding extra density near the critical strip), stereographic reflection for the left half-plane, and the actual zeta application via apply_complex_function. Uses mpmath for arbitrary-precision zeta computation. The "analytic continuation" is shown by reflecting the right-half-plane grid across the critical line and applying zeta to the mirror.

## Design Decisions

- **Complex transformation as grid deformation**: Instead of plotting zeta(s) as a separate graph, the input plane IS the visualization. Grid lines bend and stretch to show where each point maps. This makes poles, zeros, and the critical strip physically visible as distortions.
- **Adaptive anchor density near pole at s=1**: The prepare_for_transformation method adds more anchor points to lines near s=1, where zeta has a pole. Lines that map to large circles need many points to render smoothly. Uses diameter-based heuristic to determine point count.
- **Reflected plane for analytic continuation**: The right-half-plane grid is copied, reflected about Re(s)=1, and given muted colors (1 - 0.5*rgb). When zeta is applied to this reflected grid, it shows how the function extends to the left half-plane — making "analytic continuation" visual.
- **mpmath for precision**: Uses mpmath.zeta with 7 decimal places (dps=7). Catches exceptions near the pole to return max_norm. This is necessary because numpy can't evaluate the zeta function.
- **Dense grid in critical strip**: get_dense_grid adds lines at step_size=1/16 in the region near Re(s)=1. This high density is needed because the transformation stretches this region dramatically.
- **Background rectangles on text**: All labels use add_background_rectangle() since they overlay the colored grid. Essential for readability.

## Composition

- **Complex plane grid**: Default ComplexPlane with colored horizontal and vertical lines. Horizontal: green gradient. Vertical: blue gradient.
- **Dense grid**: step_size=1/16 in extra_lines region (x: -2 to 4, y: -2 to 2). stroke_width=1.
- **Reflected plane**: Full plane copy, rotated PI about UP at x=1. Colors muted to 1-0.5*rgb.
- **Zeta formula**: OldTex("\\zeta(s) = ") + OldTex("\\sum_{n=1}^\\infty \\frac{1}{n^s}"). Background rectangles. Next to title DOWN.
- **Title**: "Riemann zeta function" in upper left corner with background_rectangle.
- **Input/output demo**: z_in Dot (YELLOW) at UP+RIGHT. z_out Dot (MAROON_B) at 4*RIGHT+2*UP. Arrow between them.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Input point z | YELLOW | Dot |
| Output f(z) | MAROON_B | Dot |
| Arrow | WHITE | Between input and output |
| Zeta sum | YELLOW | Highlighted in title |
| Horizontal grid lines | GREEN gradient | vert_start_color to vert_end_color |
| Vertical grid lines | BLUE gradient | horiz_start_color to horiz_end_color |
| Dense grid | Various | stroke_width=1 |
| Reflected grid | Muted | 1 - 0.5*original_rgb |
| Text backgrounds | BLACK | BackgroundRectangle |
| $1M prize | GREEN_B to GREEN_D | Gradient for money text |
| Divergent sum | YELLOW to MAROON_B | 1+2+3+... gradient |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Plane creation | run_time=2 | ShowCreation |
| Reflected plane | run_time=2 | ShowCreation |
| Zeta application | run_time=5-8 | apply_complex_function (default 5) |
| Formula write | run_time=2 | Write |
| Student thoughts | run_time=2-3 | student_thinks with bubbles |
| Input-output demo | run_time=2 | ShowCreation arrow + dots |
| Grid deformation | run_time=5 | default_apply_complex_function_kwargs |

## Patterns

### Pattern: Complex Function as Grid Deformation

**What**: A ZetaTransformationScene that draws the complex plane as a grid, prepares it with adaptive anchor density, then applies a complex function to deform every point. The prepare_for_transformation method adds curve segments proportional to the expected image diameter. apply_zeta_function delegates to apply_complex_function with the mpmath zeta.

**When to use**: Visualizing any complex function — conformal maps, Mobius transformations, polynomial maps, analytic functions. The grid deformation makes singularities, branch cuts, and conformal properties visible. The adaptive density pattern is essential for functions with poles.

```python
# Source: projects/videos/_2016/zeta.py:25-134
class ZetaTransformationScene(ComplexTransformationScene):
    CONFIG = {"anchor_density": 35, "min_added_anchors": 10, "max_added_anchors": 300}

    def prepare_for_transformation(self, mob):
        for line in mob.family_members_with_points():
            # Estimate image size via zeta at closest point to s=1
            closest_to_one = interpolate(line.get_start(), line.get_end(), t)
            diameter = abs(zeta(complex(*closest_to_one[:2])))
            target_num_curves = np.clip(
                int(self.anchor_density * np.pi * diameter),
                self.min_added_anchors, self.max_added_anchors,
            )
            if line.get_num_curves() < target_num_curves:
                line.insert_n_curves(target_num_curves - line.get_num_curves())

    def apply_zeta_function(self, **kwargs):
        self.apply_complex_function(zeta, **kwargs)
```

### Pattern: Analytic Continuation as Reflected Grid

**What**: The right-half-plane grid is copied and reflected about the line Re(s)=1 (rotated PI about UP). Colors are muted (1-0.5*rgb) to distinguish original from continuation. When zeta is applied to both grids, the reflected grid fills in the left half-plane, visually demonstrating how the function extends beyond its original domain of convergence.

**When to use**: Visualizing analytic continuation of any function, domain extension, or any scenario where a function defined on a subset extends to a larger domain. The color-muting technique for the "extended" domain is broadly useful.

```python
# Source: projects/videos/_2016/zeta.py:111-134
def get_reflected_plane(self):
    reflected_plane = self.plane.copy()
    reflected_plane.rotate(np.pi, UP, about_point=RIGHT)  # Reflect about Re(s)=1
    for mob in reflected_plane.family_members_with_points():
        mob.set_color(Color(rgb=1 - 0.5 * color_to_rgb(mob.get_color())))
    self.prepare_for_transformation(reflected_plane)
    return reflected_plane

# Usage in PreviewZetaAndContinuation:
self.add_transformable_plane()
self.add_extra_plane_lines_for_zeta()
self.apply_zeta_function()  # Deform right half
reflected_plane = self.get_reflected_plane()
self.play(ShowCreation(reflected_plane, lag_ratio=0, run_time=2))
```

### Pattern: Dense Grid for Critical Region

**What**: Adds a fine grid (step_size=1/16) in the region near the singularity of the zeta function. Vertical and horizontal lines at this finer resolution, colored by gradient, with stroke_width=1. Lines at exactly x=1 or y=0 are excluded (epsilon=0.1 exclusion zone) to avoid the pole.

**When to use**: Any complex transformation where certain regions need higher visual resolution — near poles, branch points, or zeros. The epsilon exclusion prevents rendering artifacts at singularities.

```python
# Source: projects/videos/_2016/zeta.py:73-109
def get_dense_grid(self, step_size=1./16):
    epsilon = 0.1
    x_range = np.arange(self.extra_lines_x_min, self.extra_lines_x_max, step_size)
    y_range = np.arange(self.extra_lines_y_min, self.extra_lines_y_max, step_size)
    vert_lines = VGroup(*[
        Line(self.y_min*UP, self.y_max*UP).shift(x*RIGHT)
        for x in x_range if abs(x-1) > epsilon
    ])
    vert_lines.set_color_by_gradient(self.vert_start_color, self.vert_end_color)
    horiz_lines = VGroup(*[
        Line(self.x_min*RIGHT, self.x_max*RIGHT).shift(y*UP)
        for y in y_range if abs(y) > epsilon
    ])
    dense_grid = VGroup(horiz_lines, vert_lines)
    dense_grid.set_stroke(width=1)
    return dense_grid
```

## Scene Flow

1. **Complex Functions Intro** (0-15s): "Complex-valued function" title. Yellow input dot z, arrow, maroon output f(z). Simple mapping demonstration.
2. **Why People Know It** (15-45s): TeacherStudentsScene. $1,000,000 prize for zeros. Divergent sum 1+2+3+...=-1/12 shock. Student asks about analytic continuation.
3. **Assumed Knowledge** (45-60s): Complex number on plane with real (GREEN) and imaginary (RED) components. Three prerequisites listed.
4. **Grid Drawing** (60-90s): Complex plane grid appears. Dense grid added in critical strip. Formula and title displayed.
5. **First Transformation** (90-120s): apply_zeta_function deforms the right-half grid over 5-8 seconds. Grid lines bend dramatically near the pole at s=1.
6. **Analytic Continuation** (120-150s): "What does analytic continuation look like?" Reflected grid (muted colors) appears. Zeta applied to it. The full zeta landscape revealed. Critical line at Re(s)=1/2 visible as a distinguished feature.

> Note: This is 2016-era manimlib code. Uses deprecated APIs: ComplexTransformationScene, apply_complex_function, add_transformable_plane. The CONFIG dict pattern is used throughout. See also `3b1b_zeta_function.md` for the 2025 version using InteractiveScene with ComplexValueTracker.
