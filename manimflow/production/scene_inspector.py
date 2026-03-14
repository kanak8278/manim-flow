"""Scene Inspector — executes Manim code to extract exact geometry without rendering.

Mocks the animation system so that self.play() applies end states instantly
(no video, no voiceover, no audio). Captures snapshots of object positions
after each animation completes.

This gives us EXACT bounding boxes from Manim's own geometry engine —
not regex estimates. We use these to validate against screenplay intent.

Usage:
    snapshots = inspect_scene(code)
    # snapshots = list of SceneSnapshot, each with element positions
    # after each self.play() call
"""

import re
import sys
import types
import traceback
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class ElementGeometry:
    """Exact geometry of a Manim object at a point in time."""
    name: str  # variable name in code
    center_x: float
    center_y: float
    width: float
    height: float
    obj_type: str  # "RoundedRectangle", "Text", "Dot", etc.

    @property
    def left(self) -> float:
        return self.center_x - self.width / 2

    @property
    def right(self) -> float:
        return self.center_x + self.width / 2

    @property
    def top(self) -> float:
        return self.center_y + self.height / 2

    @property
    def bottom(self) -> float:
        return self.center_y - self.height / 2

    def overlaps(self, other: "ElementGeometry") -> bool:
        return (
            self.left < other.right
            and self.right > other.left
            and self.bottom < other.top
            and self.top > other.bottom
        )

    def overlap_area(self, other: "ElementGeometry") -> float:
        if not self.overlaps(other):
            return 0.0
        dx = min(self.right, other.right) - max(self.left, other.left)
        dy = min(self.top, other.top) - max(self.bottom, other.bottom)
        return dx * dy

    def contains(self, other: "ElementGeometry") -> bool:
        return (
            self.left <= other.left
            and self.right >= other.right
            and self.bottom <= other.bottom
            and self.top >= other.top
        )

    @property
    def area(self) -> float:
        return self.width * self.height

    def is_offscreen(self) -> bool:
        return (
            self.right < -7.11
            or self.left > 7.11
            or self.top < -4.0
            or self.bottom > 4.0
        )


@dataclass
class SceneSnapshot:
    """State of the scene at a point in time (after an animation completes)."""
    step: int  # which self.play() call this is after
    description: str  # what animation triggered this snapshot
    elements: dict[str, ElementGeometry]  # name → geometry for all visible objects


def _extract_geometry(name: str, mob) -> ElementGeometry | None:
    """Extract geometry from a Manim mobject."""
    try:
        center = mob.get_center()
        return ElementGeometry(
            name=name,
            center_x=float(center[0]),
            center_y=float(center[1]),
            width=float(mob.get_width()),
            height=float(mob.get_height()),
            obj_type=type(mob).__name__,
        )
    except Exception:
        return None


def inspect_scene(code: str) -> list[SceneSnapshot]:
    """Execute Manim code and capture geometry snapshots without rendering.

    Mocks self.play() to apply animation end states instantly.
    Captures element positions after each play() call.

    Args:
        code: Full Manim Python code with GeneratedScene class

    Returns:
        List of SceneSnapshot — one per self.play() call + initial state
    """
    try:
        from manim import Scene, Mobject, VGroup, config
        from manim.animation.animation import Animation
        from manim.animation.fading import FadeOut, FadeIn
        from manim.animation.creation import Create, Write, DrawBorderThenFill
        from manim.animation.transform import Transform, ReplacementTransform
        from manim.animation.growing import GrowFromCenter
        from manim.animation.indication import Indicate, Circumscribe, Flash
    except ImportError:
        return []

    snapshots = []
    step_counter = [0]
    visible_objects = {}  # name → mobject
    all_local_vars = {}  # track all variables

    class MockScene:
        """Mock scene that applies animation end states without rendering."""

        def __init__(self):
            self.mobjects = []
            self.camera = types.SimpleNamespace(
                background_color=None
            )

        def add(self, *mobs):
            for m in mobs:
                if m not in self.mobjects:
                    self.mobjects.append(m)

        def remove(self, *mobs):
            for m in mobs:
                if m in self.mobjects:
                    self.mobjects.remove(m)

        def play(self, *animations, **kwargs):
            """Apply end states of all animations instantly."""
            from manim.mobject.mobject import _AnimationBuilder

            for anim in animations:
                if anim is None:
                    continue

                # Handle .animate builders — build them into real animations
                if isinstance(anim, _AnimationBuilder):
                    try:
                        anim = anim.build()
                    except Exception:
                        continue

                if isinstance(anim, (FadeOut,)):
                    # Remove from scene
                    mob = anim.mobject
                    self.remove(mob)

                elif isinstance(anim, (FadeIn, Create, Write, DrawBorderThenFill, GrowFromCenter)):
                    # Add to scene at current position
                    mob = anim.mobject
                    self.add(mob)

                elif isinstance(anim, (Transform, ReplacementTransform)):
                    # Source becomes target
                    source = anim.mobject
                    target = anim.target_mobject
                    if isinstance(anim, ReplacementTransform):
                        self.remove(source)
                        self.add(target)
                    else:
                        # Transform modifies source to look like target
                        if target is not None:
                            try:
                                source.become(target)
                            except Exception:
                                pass
                        self.add(source)

                elif isinstance(anim, (Indicate, Circumscribe, Flash)):
                    # Visual effects — no position change, ensure mob is in scene
                    self.add(anim.mobject)

                elif isinstance(anim, Animation):
                    # Generic animation (including _MethodAnimation from .animate)
                    # Apply target state if available
                    mob = anim.mobject
                    if hasattr(anim, 'target_mobject') and anim.target_mobject is not None:
                        try:
                            mob.become(anim.target_mobject)
                        except Exception:
                            pass
                    self.add(mob)

            # Take snapshot
            step_counter[0] += 1
            desc = _describe_animations(animations)
            snap = _take_snapshot(self, step_counter[0], desc, all_local_vars)
            snapshots.append(snap)

        def wait(self, *args, **kwargs):
            pass

        def wait_until_bookmark(self, *args, **kwargs):
            pass

        def set_speech_service(self, *args, **kwargs):
            pass

        @contextmanager
        def voiceover(self, *args, **kwargs):
            """Mock voiceover context manager — yields a mock tracker."""
            tracker = types.SimpleNamespace(
                duration=5.0,
                get_remaining_duration=lambda: 5.0,
            )
            yield tracker

    def _describe_animations(animations) -> str:
        parts = []
        for a in animations:
            if a is None:
                continue
            name = type(a).__name__
            mob_name = type(a.mobject).__name__ if hasattr(a, 'mobject') else '?'
            parts.append(f"{name}({mob_name})")
        return ", ".join(parts) if parts else "unknown"

    def _take_snapshot(mock_scene, step, desc, local_vars) -> SceneSnapshot:
        elements = {}

        # Map mobjects back to their variable names
        mob_to_name = {}
        for var_name, var_val in local_vars.items():
            if var_name.startswith('_') or var_name in ('self', 'tracker', 'make_card'):
                continue
            if hasattr(var_val, 'get_center'):
                mob_to_name[id(var_val)] = var_name

        for mob in mock_scene.mobjects:
            name = mob_to_name.get(id(mob), f"unnamed_{id(mob) % 10000}")
            geom = _extract_geometry(name, mob)
            if geom:
                elements[name] = geom

        return SceneSnapshot(step=step, description=desc, elements=elements)

    # Build executable code with mocked scene
    try:
        # Rewrite the code: replace the class body to use our mock
        # Strategy: extract construct() body, run it with mock self
        construct_body = _extract_construct_body(code)
        if not construct_body:
            return []

        # Build a wrapper that creates MockScene and runs the construct body
        mock = MockScene()

        # Execute imports and helper functions from the original code
        import_lines = []
        helper_lines = []
        in_helper = False
        helper_indent = 0

        for line in code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("from ") or stripped.startswith("import "):
                # Skip voiceover imports — we mock those
                if "voiceover" not in stripped and "edge_tts" not in stripped.lower():
                    import_lines.append(line)

        # Execute imports
        import_code = "\n".join(import_lines)
        exec_ns = {"__builtins__": __builtins__}
        try:
            exec(import_code, exec_ns)
        except Exception:
            pass  # some imports may fail, continue

        # Add mocks for common services that aren't available
        class _MockService:
            def __init__(self, *a, **kw): pass
        exec_ns["EdgeTTSService"] = _MockService
        exec_ns["VoiceoverScene"] = type(
            "VoiceoverScene", (exec_ns.get("Scene", object),), {}
        )

        # Add mock self to namespace
        exec_ns["self"] = mock

        # Execute helper functions defined in construct body
        # (like make_card)
        for line in construct_body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("def "):
                # Found a helper function — execute it
                func_lines = [line]
                func_indent = len(line) - len(line.lstrip())
                continue

        # Execute the full construct body line by line, capturing locals
        # But first, make helper functions available
        try:
            exec(construct_body, exec_ns)
        except Exception as e:
            snapshots.append(SceneSnapshot(
                step=step_counter[0] + 1,
                description=f"ERROR at step {step_counter[0]+1}: {type(e).__name__}: {e}",
                elements={},
            ))

        # Map variable names to mobjects for better snapshot names
        for var_name, var_val in exec_ns.items():
            if var_name.startswith('_') or var_name in ('self', '__builtins__'):
                continue
            if hasattr(var_val, 'get_center'):
                all_local_vars[var_name] = var_val

        # Retake final snapshot with variable names resolved
        if snapshots:
            last = snapshots[-1]
            # Re-resolve names from exec namespace
            mob_to_name = {}
            for var_name, var_val in exec_ns.items():
                if var_name.startswith('_') or var_name in ('self', '__builtins__'):
                    continue
                if hasattr(var_val, 'get_center'):
                    mob_to_name[id(var_val)] = var_name

            # Update element names in all snapshots
            for snap in snapshots:
                updated = {}
                for old_name, geom in snap.elements.items():
                    # Try to find a better name
                    new_name = old_name
                    for mob in mock.mobjects + list(exec_ns.values()):
                        if not hasattr(mob, 'get_center'):
                            continue
                        try:
                            c = mob.get_center()
                            if (abs(c[0] - geom.center_x) < 0.01
                                    and abs(c[1] - geom.center_y) < 0.01):
                                vid = id(mob)
                                if vid in mob_to_name:
                                    new_name = mob_to_name[vid]
                                    break
                        except Exception:
                            continue
                    updated[new_name] = ElementGeometry(
                        name=new_name,
                        center_x=geom.center_x,
                        center_y=geom.center_y,
                        width=geom.width,
                        height=geom.height,
                        obj_type=geom.obj_type,
                    )
                snap.elements = updated

    except Exception as e:
        snapshots.append(SceneSnapshot(
            step=step_counter[0] + 1,
            description=f"ERROR: {type(e).__name__}: {e}",
            elements={},
        ))

    return snapshots


def _extract_construct_body(code: str) -> str:
    """Extract the body of the construct() method, dedented to top level."""
    lines = code.split("\n")
    in_construct = False
    construct_lines = []
    construct_indent = 0

    for line in lines:
        stripped = line.strip()

        if "def construct(self" in stripped:
            in_construct = True
            # Find indentation of the def line + one level
            construct_indent = len(line) - len(line.lstrip()) + 4
            continue

        if in_construct:
            # Check if we've left construct (another def at same or lower indent)
            if stripped and not stripped.startswith("#"):
                current_indent = len(line) - len(line.lstrip())
                if current_indent < construct_indent and stripped.startswith("def "):
                    break

            # Dedent the line
            if line.strip() == "":
                construct_lines.append("")
            elif len(line) >= construct_indent:
                construct_lines.append(line[construct_indent:])
            else:
                construct_lines.append(line.lstrip())

    return "\n".join(construct_lines)


def print_snapshots(snapshots: list[SceneSnapshot]):
    """Pretty-print scene snapshots."""
    print(f"\n--- Scene Inspector: {len(snapshots)} snapshots ---")
    for snap in snapshots:
        elem_count = len(snap.elements)
        print(f"\n  Step {snap.step}: {snap.description} ({elem_count} elements)")
        for name, geom in snap.elements.items():
            print(f"    {name}: {geom.obj_type} at ({geom.center_x:.1f}, {geom.center_y:.1f}) "
                  f"size={geom.width:.1f}x{geom.height:.1f}"
                  f"{' [OFF-SCREEN]' if geom.is_offscreen() else ''}")
