---
source: https://github.com/behackl/manim-with-ease/blob/main/E03 - animations.ipynb
project: manim-with-ease
domain: [mathematics, geometry]
elements: [dot, group]
animations: [fade_out, custom_animation]
layouts: [centered]
techniques: [custom_animation]
purpose: [demonstration]
mobjects: [VGroup, Dot, Star]
manim_animations: []
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 40
scene_classes: [CustomAnimationExample]
---

## Summary

Demonstrates building a custom Manim Animation subclass called `Disperse` that explodes a mobject into dots that fly outward. The mobject fades out during the first half of the animation while dots fade in at sampled boundary points, then in the second half the dots fly outward along radial vectors while fading out. This is a canonical example of the Animation lifecycle: `begin()` for setup, `interpolate_mobject(alpha)` for per-frame logic, and `clean_up_from_scene()` for teardown.

## Design Decisions

- **Subclassing Animation directly**: This is the correct approach when you need per-frame control over multiple sub-objects that don't fit the `interpolate_submobject` pattern. The alternative `UpdateFromAlphaFunc` is simpler but messier for multi-object orchestration.
- **Two-phase alpha split (0-0.5 and 0.5-1)**: The first half crossfades from mobject to dots, the second half disperses the dots. This creates a smooth visual transition — the shape dissolves into particles which then explode.
- **point_from_proportion for dot placement**: Samples points evenly along the mobject's boundary curve. This works for any VMobject shape, making the pattern generic.
- **Radial shift vectors**: Each dot's flight direction is `2*(dot_center - mobject_center)`, pushing dots outward from the center. The factor of 2 ensures they travel far enough to feel like an explosion.
- **Manual rate_func application**: `alpha = self.rate_func(alpha)` is called explicitly in `interpolate_mobject`. This is required when overriding `interpolate_mobject` directly rather than using the built-in interpolation machinery.

## Composition

- **Screen regions**:
  - Star: centered, scale(3)
  - Dots: 200 dots sampled along star boundary, dispersing outward
- **Element sizing**: Dot radius=0.05, Star scale=3

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Background | BLACK | Default |
| Star | YELLOW | fill_opacity=1 |
| Disperse dots | YELLOW | Inherit from parent mobject's boundary |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Initial wait | default (~1s) | Show the star |
| Disperse | run_time=4 | First 2s: crossfade, last 2s: scatter |
| Total video | ~5 seconds | |

## Patterns

### Pattern: Custom Animation Subclass (Disperse)

**What**: A full Animation subclass with three lifecycle methods: `begin()` creates dot submobjects and computes their radial flight vectors; `interpolate_mobject(alpha)` handles the two-phase crossfade-then-scatter logic; `clean_up_from_scene()` removes the dots. This is the template for any custom animation that needs setup/teardown beyond simple interpolation.

**When to use**: Explosion/disperse effects, particle-based transitions, any animation where a mobject transforms into multiple sub-objects that move independently. Also the reference pattern for understanding Manim's Animation lifecycle — useful anytime `animate` or `UpdateFromAlphaFunc` are too limited.

```python
# Source: projects/manim-with-ease/E03 - animations.ipynb (cell 9)
class Disperse(Animation):
    def __init__(self, mobject, dot_radius=0.05, dot_number=100, **kwargs):
        super().__init__(mobject, **kwargs)
        self.dot_radius = dot_radius
        self.dot_number = dot_number

    def begin(self):
        dots = VGroup(
            *[Dot(radius=self.dot_radius).move_to(self.mobject.point_from_proportion(p))
              for p in np.linspace(0, 1, self.dot_number)]
        )
        for dot in dots:
            dot.initial_position = dot.get_center()
            dot.shift_vector = 2*(dot.get_center() - self.mobject.get_center())
        dots.set_opacity(0)
        self.mobject.add(dots)
        self.dots = dots
        super().begin()

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        scene.remove(self.dots)

    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)  # manually apply rate function
        if alpha <= 0.5:
            self.mobject.set_opacity(1 - 2*alpha, family=False)
            self.dots.set_opacity(2*alpha)
        else:
            self.mobject.set_opacity(0)
            self.dots.set_opacity(2*(1 - alpha))
            for dot in self.dots:
                dot.move_to(dot.initial_position + 2*(alpha-0.5)*dot.shift_vector)
```

> Gotcha: You MUST call `alpha = self.rate_func(alpha)` manually in `interpolate_mobject`. The base class does NOT apply it for you when you override this method.

> Gotcha: `set_opacity(1 - 2*alpha, family=False)` — the `family=False` flag is critical. Without it, the opacity change propagates to child dots, making them invisible too.

### Pattern: point_from_proportion Boundary Sampling

**What**: Use `mobject.point_from_proportion(p)` with `np.linspace(0, 1, N)` to sample N evenly-spaced points along any VMobject's boundary. This works for circles, polygons, stars, text outlines — anything that's a VMobject.

**When to use**: Particle effects along shape boundaries, creating dot decorations around any shape, path-based animations where you need reference points along a contour, stippled/dotted outlines.

```python
# Source: projects/manim-with-ease/E03 - animations.ipynb (cell 9)
dots = VGroup(
    *[Dot(radius=0.05).move_to(self.mobject.point_from_proportion(p))
      for p in np.linspace(0, 1, self.dot_number)]
)
```

### Pattern: Animation Lifecycle (begin / interpolate / cleanup)

**What**: The three-method lifecycle for custom Animation subclasses: `begin()` runs once at animation start (create temporary objects, compute vectors), `interpolate_mobject(alpha)` runs every frame with alpha in [0,1], `clean_up_from_scene(scene)` runs once at the end (remove temporary objects). This is Manim's core animation contract.

**When to use**: Any time you need animation logic that goes beyond what `.animate` or `UpdateFromAlphaFunc` can express — multi-object orchestration, temporary submobjects, phased animations, cleanup of generated objects.

```python
# Source: projects/manim-with-ease/E03 - animations.ipynb (cell 9)
class MyAnimation(Animation):
    def begin(self):
        # Create temporary objects, compute trajectories
        super().begin()

    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)
        # Per-frame logic using alpha in [0, 1]

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        # Remove temporary objects from scene
```

## Scene Flow

1. **Setup** (0-1s): Yellow star appears centered, scaled to 3x.
2. **Crossfade** (1-3s): Star fades to transparent while 200 yellow dots appear along its boundary, creating a dotted outline.
3. **Scatter** (3-5s): Dots fly outward radially from center while fading to transparent. Screen ends empty.

> Source: `projects/manim-with-ease/E03 - animations.ipynb` (cell 9, Disperse class + CustomAnimationExample scene)
