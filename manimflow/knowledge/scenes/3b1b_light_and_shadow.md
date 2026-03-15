---
source: https://github.com/3b1b/videos/blob/main/once_useful_constructs/light.py
project: videos
domain: [mathematics, physics, optics, geometry]
elements: [dot, line, group]
animations: [fade_in, fade_out, animate_parameter]
layouts: [centered]
techniques: [custom_mobject, custom_animation, add_updater]
purpose: [demonstration, exploration]
mobjects: [VMobject, VGroup, Annulus, AnnularSector, SVGMobject, VectorizedPoint]
manim_animations: [LaggedStartMap, FadeIn, FadeOut, Transform]
scene_type: Scene
manim_version: manimlib
complexity: advanced
lines: 602
scene_classes: []
---

## Summary

A lighting and shadow system built for the 3B1B inverse square law video. Provides AmbientLight (radial glow using concentric annuli with opacity falloff), Spotlight (directional cone of light using annular sectors), a Lighthouse SVG, and a composite LightSource that combines all three with shadow casting. The opacity follows configurable power-law functions (default inverse quadratic), and the system supports dimming, moving, and dynamic screen-based shadow updates.

## Design Decisions

- **Annuli-based radial falloff**: AmbientLight is built from concentric Annulus rings with decreasing opacity. This discrete approximation of continuous radial falloff is efficient and works well at NUM_LEVELS=30 subdivisions.
- **Inverse quadratic opacity by default**: `inverse_quadratic(maxint, scale, cutoff)` models realistic light intensity falloff. The cutoff parameter prevents division-by-zero at the source point.
- **Spotlight as annular sectors**: Directional light is approximated using AnnularSector mobjects computed from the viewing angles to a "screen" object. The projection direction is derived from the camera position.
- **Shadow as convex hull complement**: The shadow region is computed from the convex hull of projected screen points relative to the light source, creating realistic shadow geometry.
- **SwitchOn/SwitchOff as LaggedStartMap**: Light appears ring-by-ring from center outward (FadeIn with lag_ratio=0.2), creating a natural "switching on" effect.

## Composition

- **Lighthouse**: SVG mobject, height=0.8 (LIGHTHOUSE_HEIGHT), fill WHITE, positioned with base at source point.
- **AmbientLight**: radius=5.0, 30 levels, centered on source_point.
- **Spotlight**: radius=10.0, 10 levels, requires a "screen" VMobject to define the cone angle.
- **LightSource**: Composite of lighthouse + ambient light + spotlight + shadow.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Light | YELLOW (LIGHT_COLOR) | Default light color |
| Shadow | BLACK (SHADOW_COLOR) | fill_opacity=1.0, stroke_color=BLACK |
| Lighthouse | WHITE | fill_opacity=1.0, SVG |
| Ambient full | 0.8 opacity | AMBIENT_FULL |
| Ambient dimmed | 0.5 opacity | AMBIENT_DIMMED |
| Spotlight full | 0.8 opacity | SPOTLIGHT_FULL |
| Spotlight default color | GREEN | Overridden in most uses |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| SwitchOn | 1.5s | SWITCH_ON_RUN_TIME, lag_ratio=0.2 |
| SwitchOff | 1.5s | Same as SwitchOn but reversed |
| Fast SwitchOn | 0.1s | FAST_SWITCH_ON_RUN_TIME |

## Patterns

### Pattern: Radial Light Glow via Concentric Annuli

**What**: Creates a radial light effect by stacking concentric Annulus mobjects with opacity decreasing according to an inverse power law. Each annulus has width = radius/num_levels, and opacity = max_opacity * opacity_function(r). Supports dimming by proportionally scaling all annulus opacities.

**When to use**: Point light sources, glowing effects, visualizing inverse square law in physics, ambient illumination around any point. The discrete annuli approach works for any radial falloff function.

```python
# Source: projects/videos/once_useful_constructs/light.py:89-132
class AmbientLight(VMobject):
    CONFIG = {
        "opacity_function": lambda r: 1.0 / (r + 1.0)**2,
        "color": LIGHT_COLOR,
        "max_opacity": 1.0,
        "num_levels": NUM_LEVELS,
        "radius": 5.0
    }

    def init_points(self):
        self.add(self.source_point)
        self.radius = float(self.radius)
        dr = self.radius / self.num_levels
        for r in np.arange(0, self.radius, dr):
            alpha = self.max_opacity * self.opacity_function(r)
            annulus = Annulus(
                inner_radius=r, outer_radius=r + dr,
                color=self.color, fill_opacity=alpha
            )
            annulus.move_to(self.get_source_point())
            self.add(annulus)
```

### Pattern: Directional Spotlight with Screen Projection

**What**: Creates a cone of light by computing viewing angles from the source point to a "screen" mobject, then filling that angular range with AnnularSector mobjects. The sectors are projected and rotated into the camera's viewing plane, creating a proper 3D-aware spotlight.

**When to use**: Flashlight beams, projector light, directional illumination in optics demonstrations, visualizing how light cones work with screens/barriers. The screen-based angle computation enables dynamic shadow updates when the screen moves.

```python
# Source: projects/videos/once_useful_constructs/light.py:153-222
class Spotlight(VMobject):
    CONFIG = {
        "screen": None,
        "camera_mob": None,
        "num_levels": 10,
        "radius": 10.0,
    }

    def init_points(self):
        if self.screen is not None:
            lower_angle, upper_angle = self.viewing_angles(self.screen)
            dr = self.radius / self.num_levels
            for r in np.arange(0, self.radius, dr):
                new_sector = self.new_sector(r, dr, lower_angle, upper_angle)
                self.add(new_sector)
```

### Pattern: LaggedStartMap Light Switch Animation

**What**: SwitchOn/SwitchOff animations use LaggedStartMap(FadeIn/FadeOut) on the annuli submobjects, creating a ring-by-ring expansion/contraction effect. The lag_ratio controls how much the rings overlap in their fade timing.

**When to use**: Any "turning on" or "turning off" effect - powering up a light source, expanding/contracting a radial field, wave-like reveal of concentric elements.

```python
# Source: projects/videos/once_useful_constructs/light.py:45-72
class SwitchOn(LaggedStartMap):
    CONFIG = {"lag_ratio": 0.2, "run_time": SWITCH_ON_RUN_TIME}
    def __init__(self, light, **kwargs):
        LaggedStartMap.__init__(self, FadeIn, light, **kwargs)

class SwitchOff(LaggedStartMap):
    CONFIG = {"lag_ratio": 0.2, "run_time": SWITCH_ON_RUN_TIME}
    def __init__(self, light, **kwargs):
        light.set_submobjects(light.submobjects[::-1])
        LaggedStartMap.__init__(self, FadeOut, light, **kwargs)
        light.set_submobjects(light.submobjects[::-1])
```

## manimlib Notes

- Uses legacy CONFIG dict pattern (pre-refactor manimlib)
- `init_points()` instead of `__init__` for mobject construction
- `VectorizedPoint(location=ORIGIN)` for invisible source point tracking
- Shadow computation uses `scipy.spatial.ConvexHull`
- Warning in source: "This class is likely quite buggy" for LightSource
