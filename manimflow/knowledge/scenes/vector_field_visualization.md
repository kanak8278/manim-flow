---
source: https://github.com/vivek3141/videos/blob/main/divergence.py
project: vivek3141_videos
domain: [mathematics, calculus, physics, electromagnetism, geometry]
elements: [vector_field, axes, parametric_curve, arrow, circle, label, equation, area_under_curve, dot]
animations: [fade_in, fade_out, write, transform, draw, highlight, color_change]
layouts: [centered, side_by_side, grid]
techniques: [color_gradient, data_driven, custom_animation, progressive_disclosure]
purpose: [demonstration, exploration, decomposition, proof, step_by_step]
mobjects: [Vector, Circle, VGroup, Axes, ParametricFunction, Text, TexMobject, Dot]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, Transform, ApplyMethod]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 1120
scene_classes: [Intro, FluxIntegral, DivergenceTheorem, SurfaceIntegral]
---

## Summary

Visualizes vector fields, divergence, and flux integrals for a calculus/physics audience. The core technique is a grid of normalized arrows where magnitude maps to a 9-color spectrum (red=high → blue=low). Vector fields cover a 10×10 region at 1-unit spacing. Parametric curves overlay the field to show flux integrals. Normal vectors (green) indicate direction of measurement. Three fields shown side-by-side demonstrate divergence properties: positive (expanding), zero (rotating), and negative (contracting). This is the standard approach for vector calculus visualization.

## Design Decisions

- **Normalized arrow length, color encodes magnitude**: All arrows are the same length — magnitude is shown by COLOR, not size. This prevents visual clutter from long arrows overlapping, which is the biggest problem with naive vector field rendering. The viewer reads "red = strong, blue = weak" instead of trying to compare arrow lengths.
- **9-color rainbow spectrum**: Red (#e22b2b) → Orange → Yellow → Green → Cyan → Blue → Indigo → Purple → Pink. Each color maps to a magnitude bin (0-8). The spectrum is intuitive — "hot colors = strong field" follows thermal intuition from physics.
- **Grid at 1-unit spacing**: Dense enough to see the field pattern, sparse enough that arrows don't overlap. For a [-5, 5] × [-5, 5] domain, that's 121 arrows — enough for visual impact without performance issues.
- **Green for normal vectors**: Normal vectors to curves are always GREEN, distinct from the rainbow field colors. Green is "measurement/tool" color — it's not part of the data, it's part of the analysis.
- **Side-by-side comparison for divergence types**: Three smaller fields arranged horizontally, each showing a different divergence case. The viewer compares them directly without needing to remember what they saw before.
- **Focus technique (opacity dimming)**: When explaining one concept, unrelated elements dim to low opacity. This directs attention without removing context entirely.

## Composition

- **Vector field grid**:
  - Domain: x ∈ [-5, 5], y ∈ [-5, 5] at 1-unit intervals
  - Each vector: normalized direction, length ~0.67 units (1/1.5 scaling)
  - Positioned at grid point via `.shift(point)`
  - 121 vectors per field
- **Side-by-side layout**:
  - Three fields scaled to 0.35-0.6 of original
  - Arranged with 3*LEFT, CENTER, 3*RIGHT horizontal offsets
  - Labels below each field
- **Curve overlays**:
  - ParametricFunction on top of field
  - Normal vectors at regular intervals along curve
  - Normal color: GREEN, distinct from field colors

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Field magnitude 0 (weakest) | #e22b2b | Red |
| Field magnitude 1 | #e88e10 | Orange |
| Field magnitude 2 | #eae600 | Yellow |
| Field magnitude 3 | #88ea00 | Lime |
| Field magnitude 4 | #00eae2 | Cyan |
| Field magnitude 5 | #0094ea | Blue |
| Field magnitude 6 | #2700ea | Indigo |
| Field magnitude 7 | #bf00ea | Purple |
| Field magnitude 8+ (strongest) | #ea0078 | Pink |
| Normal vectors | GREEN | Measurement direction |
| Curves | WHITE/YELLOW | Parametric paths |
| Background | BLACK | Default |
| Equations | WHITE | TexMobject |

Color strategy: Rainbow spectrum (red→pink) for magnitude bins. This is a discrete colormap — each color represents a range, not a continuous gradient. Discrete coloring is easier to read than continuous gradients for vector fields because the viewer can count distinct color bands.

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Field creation | ShowCreation, ~2s | All 121 vectors appear |
| Curve drawing | ShowCreation, ~2s | Parametric path traces |
| Normal vector appearance | FadeIn or ShowCreation | Per-vector or batched |
| Field comparison (3 panels) | Transform, ~2s each | Morph from full to scaled |
| Focus dimming | ApplyMethod opacity, ~1s | Unrelated elements dim |
| Total per scene | ~30-60s | Varies by complexity |

## Patterns

### Pattern: Color-Mapped Vector Field Grid

**What**: A grid of Vector arrows at regular intervals. Each arrow is normalized to equal length — magnitude is encoded as color using a 9-bin rainbow palette. The field function f(x,y) returns a 2D vector; its direction becomes the arrow direction, its magnitude becomes the color index. This avoids the visual clutter of variable-length arrows.
**When to use**: Any 2D vector field visualization — electric fields, fluid flow, gravitational fields, gradient fields, wind maps. Also works for force diagrams, velocity fields, or any spatial vector data.

```python
# Source: projects/vivek3141_videos/divergence.py
color_list = ['#e22b2b', '#e88e10', '#eae600', '#88ea00',
              '#00eae2', '#0094ea', '#2700ea', '#bf00ea', '#ea0078']

def calc_field_color(self, point, f, prop=0.0, opacity=None):
    x, y = point[:2]
    func = f(x, y)
    magnitude = math.sqrt(func[0] ** 2 + func[1] ** 2)
    func = func / magnitude if magnitude != 0 else np.array([0, 0])
    func = func / 1.5  # Scale arrow length
    v = int(magnitude / 10 ** prop)  # Bin by magnitude
    index = min(v, len(self.color_list) - 1)
    c = self.color_list[index]
    v = Vector(func, color=c).shift(point)
    return v

# Generate full field
field = VGroup(*[
    self.calc_field_color(x * RIGHT + y * UP, self.vect, prop=0)
    for x in np.arange(-5, 6, 1)
    for y in np.arange(-5, 6, 1)
])
self.play(ShowCreation(field))
```

### Pattern: Flux Integral with Normal Vectors

**What**: Overlay a parametric curve on a vector field, then show normal vectors along the curve pointing outward. The normal vectors (GREEN) show the direction of flux measurement. This visually explains the flux integral — "how much of the field passes through this curve."
**When to use**: Line integrals, flux calculations, divergence theorem visualization, boundary integrals. Also works for any "measurement along a path" concept.

```python
# Source: projects/vivek3141_videos/divergence.py (FluxIntegral scene)
# Parametric curve
curve = ParametricFunction(
    lambda t: np.array([2 * np.cos(t), 2 * np.sin(t), 0]),
    t_min=0, t_max=2 * PI, color=YELLOW
)

# Normal vectors at intervals along curve
normals = VGroup()
for t in np.linspace(0, 2 * PI, 20):
    point = curve.point_from_proportion(t / (2 * PI))
    # Outward normal for circle: same direction as position
    normal_dir = point / np.linalg.norm(point)
    normal = Vector(normal_dir * 0.5, color=GREEN).shift(point)
    normals.add(normal)

self.play(ShowCreation(curve))
self.play(FadeIn(normals))
```

### Pattern: Side-by-Side Field Comparison

**What**: Three vector fields displayed side by side at reduced scale, each demonstrating a different property (e.g., positive divergence, zero divergence, negative divergence). Each field has a label below. The viewer compares patterns directly without needing to remember previous frames.
**When to use**: Comparing field properties, showing positive/negative/zero cases, parameter sweeps, any "three variants of the same concept" visualization.

```python
# Source: projects/vivek3141_videos/divergence.py (DivergenceTheorem)
# Three different fields
fields = [
    make_field(lambda x, y: (x, y)),       # Expanding (positive div)
    make_field(lambda x, y: (-y, x)),       # Rotating (zero div)
    make_field(lambda x, y: (-x, -y)),      # Contracting (negative div)
]
labels = ["div > 0", "div = 0", "div < 0"]

for i, (field, label) in enumerate(zip(fields, labels)):
    field.scale(0.35)
    field.shift((i - 1) * 3 * RIGHT)  # Left, center, right
    text = Text(label).next_to(field, DOWN)
    group = VGroup(field, text)
```

### Pattern: Focus by Opacity Dimming

**What**: When explaining one element, dim everything else to low opacity (0.2-0.3). This directs attention without removing context. The dimmed elements are still visible for reference but don't compete for attention. Restore full opacity when moving to the next topic.
**When to use**: Any complex scene where you need to focus attention — multi-element diagrams, busy layouts, scenes with >5 visual elements. Also works for progressive disclosure.

```python
# Source: projects/vivek3141_videos/divergence.py
# Dim everything except the target
def focus_on(self, target, others, dim_opacity=0.2):
    self.play(
        target.animate.set_opacity(1),
        *[other.animate.set_opacity(dim_opacity) for other in others]
    )

# Restore all
def unfocus(self, *all_elements):
    self.play(*[elem.animate.set_opacity(1) for elem in all_elements])
```

## Scene Flow

1. **Intro** (0-15s): Full vector field appears on screen. Narrator explains what the arrows represent. One area highlighted to show "strong" vs "weak" field regions via color.
2. **Flux Integral** (15-40s): Parametric curve overlays the field. Green normal vectors appear along the curve. Equation for flux integral shown. Animation traces the integral path.
3. **Divergence** (40-60s): Three side-by-side fields (expanding, rotating, contracting). Labels below. Each field highlighted in turn with opacity dimming on others.
4. **Divergence Theorem** (60-80s): Full field with curve. Show that flux through boundary equals integral of divergence inside. Connect the visual patterns to the mathematical statement.

> Full file: `projects/vivek3141_videos/divergence.py` (1120 lines)
