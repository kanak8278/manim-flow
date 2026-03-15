---
source: https://github.com/3b1b/videos/blob/main/_2024/holograms/diffraction.py
project: videos
domain: [optics, waves, physics, electromagnetism]
elements: [wave, dot, line, label, arrow, brace, surface_3d, vector_field, image]
animations: [fade_in, fade_out, write, draw, rotate, camera_rotate, zoom_in, zoom_out, animate_parameter]
layouts: [centered, layered, side_by_side]
techniques: [shader_custom, three_d_camera, value_tracker, add_updater, always_redraw, custom_mobject, moving_camera]
purpose: [demonstration, exploration, simulation, step_by_step]
mobjects: [DotCloud, GlowDot, GlowDots, Line, DashedLine, VGroup, Tex, Text, Brace, Arrow, VectorField, Rectangle, FullScreenRectangle, ImageMobject, Square, Cube]
manim_animations: [FadeIn, FadeOut, ShowCreation, Write, GrowFromCenter, Rotate, VShowPassingFlash, ReplacementTransform]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 4227
scene_classes: [LightFieldAroundScene, DiffractionGratingScene, LightExposingFilm]
---

## Summary

Visualizes light wave diffraction and holography using a custom shader-based LightWaveSlice mobject that renders wave interference patterns in real time on the GPU. Point sources (DotCloud) emit circular waves that interfere constructively and destructively, with the pattern computing superposition of cos(k*r - omega*t) / r^decay for each source. The diffraction grating scene builds walls with slits and shows how point sources at slit positions create the classic interference pattern. The holography scene explains how amplitude and phase of light at a film plane encode a 3D scene.

## Design Decisions

- **Custom GLSL shader for wave rendering**: LightWaveSlice uses a fragment shader that computes wave superposition for up to 30 point sources per pixel. This is vastly faster than computing wave values on the CPU and converting to mobjects. The shader handles time evolution, decay, and intensity display modes.
- **DotCloud for point sources**: Point sources are stored in a DotCloud, allowing efficient bulk updates. Each source's position is passed to the shader as a uniform. The sync_points() method keeps shader uniforms in sync with DotCloud positions.
- **Amplitude + phase labeling**: The holography explanation breaks light into amplitude (height of oscillation, shown with brace and label) and phase (position in cycle, shown with rotating arrow on a circle). These are the two quantities a hologram must record.
- **Diffraction grating from cube parts**: The wall is built from Cube segments with gaps (slit_width) between them. This gives physical 3D presence to the barrier, more convincing than a 2D line.
- **Wave graph overlay on line**: get_graph_over_wave() takes a Line and a LightWaveSlice, samples the wave function along the line, and displaces the line's points to create a 1D cross-section visualization of the 2D wave pattern.
- **Perpendicular wave slices in 3D**: Multiple copies of LightWaveSlice rotated and stacked in the z-direction create a volumetric light field visualization.

## Composition

- **Light field scene**: Scene image 7 units tall, to_edge(RIGHT). Wave shape (50, 100), rotated 70 DEG in LEFT direction. 10 perpendicular wave copies at opacity=0.1 across z from -1 to 1.
- **Diffraction grating**: Wall from Cube parts, each (width, 0.25, 3.0). Total width=40. Sources at midpoints between wall segments.
- **Film exposure**: Film Rectangle(16,9) height=8, centered. Exposure LightIntensity in GREEN. Camera starts at (-18, -7, 0).
- **Amplitude label**: DashedLine 8*OUT to ORIGIN. Brace on RIGHT, rotated PI/2 DOWN. Tex "Amplitude" font_size=72 with backstroke.
- **Phase label**: Circle radius=0.75, BLUE stroke width=2. Arrow from center to right, BLUE fill. Rotated PI/2 DOWN for 3D view.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Wave field | BLUE_D | LightWaveSlice default, opacity=1 |
| Intensity display | BLUE | LightIntensity, show_intensity=True |
| Film exposure | GREEN | LightIntensity, decay_factor=3, opacity=0.7, max_amp=0.15 |
| Amplitude lines | YELLOW | DashedLine, stroke_width=3 |
| Phase circle | BLUE | stroke_width=2 |
| Phase arrow | BLUE | fill |
| Phase wavelength | BLUE | stroke_width=3 |
| Laser light | GREEN_SCREEN | stroke (0,1), width=0.2 |
| Film rectangle | GREY_E->BLACK | fill_opacity=0.75, RED_E tint |
| Wall/grating | GREY_D | shading (0.5, 0.5, 0.5) |
| Fade rectangle | BLACK | opacity=0.7 or 0.9 |
| Cross-section graph | WHITE | stroke_width=2 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Light field fade-in | run_time=2 | FadeIn wave + perpendicular waves |
| Slow zoom out | run_time=12 | frame.animate.to_default_state |
| Observer eye movement | run_time=12 | 45 DEG path_arc, there_and_back |
| Film exposure reveal | run_time=7.5 | Camera orbit to side view |
| Amplitude label | run_time=2 | Write with stroke_color=WHITE |
| Phase rotation | run_time=3 each | Full TAU rotation forward and back |
| Laser creation | lag_ratio=0.001 | ShowCreation 250 lines |
| Linger time | 12s | Watch wave patterns evolve |

## Patterns

### Pattern: Custom Shader Wave Mobject (LightWaveSlice)

**What**: A Mobject subclass that uses a custom GLSL fragment shader to render wave interference patterns. Point sources are passed as uniforms, and the shader computes the superposition of circular waves at each pixel. Supports time evolution (with pause/unpause), amplitude decay, intensity display mode, and wave number/frequency control.

**When to use**: Wave interference, diffraction, holography, any multi-source wave superposition where pixel-level computation is needed. Also useful as a reference for how to build custom shader mobjects in manimlib.

```python
# Source: projects/videos/_2024/holograms/diffraction.py:37-168
class LightWaveSlice(Mobject):
    shader_folder = str(Path(Path(__file__).parent, "diffraction_shader"))
    render_primitive = moderngl.TRIANGLE_STRIP

    def __init__(self, point_sources, shape=(8.0, 8.0),
                 frequency=1.0, wave_number=1.0, decay_factor=0.5,
                 show_intensity=False, **kwargs):
        self.point_sources = point_sources
        # ... setup uniforms ...
        self.add_updater(lambda m, dt: m.increment_time(dt))
        self.always.sync_points()

    def sync_points(self):
        for n, point in enumerate(self.point_sources.get_points()):
            self.set_uniform(**{f"point_source{n}": point})
        self.set_uniform(n_sources=self.point_sources.get_num_points())

    def wave_func(self, points):
        # CPU fallback for sampling wave values
        values = np.zeros(len(points))
        for source_point in self.point_sources.get_points():
            dists = np.linalg.norm(points - source_point, axis=1)
            values += np.cos(TAU * (k * dists - f * time)) * (dists + 1)**(-decay)
        return values
```

### Pattern: Diffraction Grating from Cube Parts

**What**: A wall with N slits, built from N+1 Cube segments with gaps between them. Edge pieces are widened to fill the screen. Point sources are placed at the midpoint of each gap. This gives a physically accurate 3D diffraction barrier.

**When to use**: Single-slit, double-slit, N-slit diffraction demonstrations, any optics scene where a barrier with openings is needed.

```python
# Source: projects/videos/_2024/holograms/diffraction.py:336-357
def get_wall_with_slits(self, n_slits, spacing=1.0, slit_width=0.1,
                         height=0.25, depth=3.0, total_width=40):
    width = spacing - slit_width
    cube = Cube().set_shape(width, height, depth)
    parts = cube.replicate(n_slits + 1)
    parts.arrange(RIGHT, buff=slit_width)
    # Extend edge pieces to fill screen
    edge_piece_width = 0.5 * (total_width - parts.get_width()) + parts[0].get_width()
    parts[0].set_width(edge_piece_width, stretch=True, about_edge=RIGHT)
    parts[-1].set_width(edge_piece_width, stretch=True, about_edge=LEFT)
    return parts

def get_point_sources_from_wall(self, wall, z=0):
    sources = GlowDots(np.array([
        midpoint(p1.get_right(), p2.get_left())
        for p1, p2 in zip(wall, wall[1:])
    ]))
    return sources
```

### Pattern: Wave Cross-Section Graph on a Line

**What**: Takes a Line and a LightWaveSlice, samples the wave function along the line's points, and displaces them perpendicular to the line to create a 1D graph of the wave amplitude. Updates every frame via updater.

**When to use**: Showing wave amplitude along a specific line or surface, cross-section views of 2D wave fields, any visualization where you need a 1D graph of a 2D field.

```python
# Source: projects/videos/_2024/holograms/diffraction.py:361-374
def get_graph_over_wave(self, line, light_wave, direction=OUT, scale_factor=0.5):
    line.insert_n_curves(500 - line.get_num_curves())
    graph = line.copy()
    graph.line = line

    def update_graph(graph):
        points = graph.line.get_anchors()
        values = scale_factor * light_wave.wave_func(points)
        graph.set_points_smoothly(points + values[:, np.newaxis] * direction)

    graph.add_updater(update_graph)
    graph.set_stroke(WHITE, 2)
    return graph
```

## Scene Flow

1. **Light field around a scene** (0-30s): A 3D scene image with 26 point sources scattered on it. LightWaveSlice renders the wave field. Perpendicular slices show the volumetric light field. Camera slowly zooms out. An observer eye moves to show different perspectives.
2. **Hologram recreation** (30-45s): Film rectangle appears. Laser light (green lines) hits the film. Wave pattern continues behind.
3. **Film exposure** (45-90s): Camera orbits to side view of a single plane wave hitting the film. Amplitude labeled with brace. Phase labeled with rotating circle arrow. Phase line shows one wavelength.
4. **Diffraction grating** (later scenes): Wall with N slits. Point sources at gaps. LightWaveSlice shows interference pattern. Progressive addition of slits shows how pattern sharpens.
