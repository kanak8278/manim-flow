---
source: https://github.com/ragibson/manim-videos/blob/main/manim_examples/3d_camera_rotation.py
project: ragibson_manim-videos
domain: [mathematics, geometry]
elements: [axes, coordinate_system]
animations: [camera_rotate]
layouts: [centered]
techniques: [three_d_camera, ambient_camera_rotation]
purpose: [demonstration]
mobjects: [ThreeDAxes, Circle]
manim_animations: []
scene_type: ThreeDScene
manim_version: manim_community
complexity: beginner
lines: 17
scene_classes: [ThreeDCameraRotation]
---

## Summary

Minimal example of ambient camera rotation in a ThreeDScene. A circle and 3D axes are placed in the scene, then the camera continuously rotates around the z-axis at rate=0.1. After stopping the ambient rotation, the camera snaps to a specific orientation. This is the canonical example for setting up auto-rotating 3D views.

## Design Decisions

- **begin_ambient_camera_rotation for auto-rotate**: This method starts a continuous camera orbit that runs during self.wait() calls. The rate parameter controls angular speed. This is the simplest way to give a 3D scene a "turntable" effect without manually animating theta.
- **stop then move_camera**: After stopping the ambient rotation, move_camera explicitly sets the final orientation. This ensures the camera ends at a known state regardless of how long the ambient rotation ran.
- **Circle in 3D space**: A standard Circle is placed in the XY-plane of a ThreeDScene. The 3D camera rotation reveals that it's a flat object viewed from different angles, which can be instructive for understanding 3D projection.

## Composition

- **Camera**: phi=75 degrees, theta=30 degrees
- **Axes**: ThreeDAxes() default
- **Circle**: default Circle(), lies in XY-plane

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Axes | WHITE | Default ThreeDAxes |
| Circle | WHITE | Default |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Ambient rotation | default wait | rate=0.1 radians/s |
| move_camera | default | phi=75, theta=30 |
| Final wait | default | |
| Total | ~3s | |

## Patterns

### Pattern: Ambient Camera Rotation in ThreeDScene

**What**: Uses `begin_ambient_camera_rotation(rate=0.1)` to start a continuous camera orbit around the z-axis. The rotation runs during any `self.wait()` or `self.play()` calls. `stop_ambient_camera_rotation()` halts it, and `move_camera()` can then set a specific final orientation. The initial camera orientation is set with `set_camera_orientation(phi, theta)`.
**When to use**: 3D surface exploration, rotating a 3D object to show all sides, any ThreeDScene where a turntable effect adds understanding, presenting 3D graphs from multiple angles without manual camera animation.

```python
# Source: projects/ragibson_manim-videos/manim_examples/3d_camera_rotation.py:4-16
class ThreeDCameraRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        circle = Circle()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(circle, axes)

        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait()

        self.stop_ambient_camera_rotation()
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
        self.wait()
```

## Scene Flow

1. **Setup** (instant): 3D axes and circle added. Camera at phi=75, theta=30.
2. **Rotation** (0-1s): Camera slowly orbits around z-axis at 0.1 rad/s.
3. **Stop and reposition** (1-2s): Rotation stops, camera snaps to phi=75, theta=30.

> Full file: `projects/ragibson_manim-videos/manim_examples/3d_camera_rotation.py` (17 lines)
