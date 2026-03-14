"""Design System — generates a complete visual specification for a video.

Takes the approved story from the writers room and decides EVERY visual choice:
colors, layouts, diagrams, animations, camera, typography.

The code generator then just implements this spec — no creative decisions left.
"""

from dataclasses import dataclass, field, asdict
from .llm import call_llm, extract_json


@dataclass
class DesignSystem:
    """Complete visual specification for a video."""

    # Global palette
    palette: dict = field(default_factory=dict)
    # e.g. {"primary": "#3498db", "secondary": "#2ecc71", "accent": "#e74c3c",
    #        "highlight": "#f39c12", "neutral": "#ecf0f1", "background": "#000000"}

    # Semantic color roles — concept name → palette key
    color_roles: dict = field(default_factory=dict)
    # e.g. {"radius": "secondary", "area": "primary", "pi": "accent", "formula": "highlight"}

    # Per-scene visual designs
    scene_designs: list[dict] = field(default_factory=list)

    # Typography
    typography: dict = field(default_factory=dict)
    # e.g. {"title": {"size": 42, "weight": "bold"}, "body": {"size": 28}, "label": {"size": 22}}

    # Animation vocabulary chosen for this video
    animations: dict = field(default_factory=dict)
    # e.g. {"enter_shape": "Create", "enter_text": "Write", "exit": "FadeOut",
    #        "emphasis": "Indicate", "transition": "Transform"}

    # Camera plan
    camera_plan: list[dict] = field(default_factory=list)
    # e.g. [{"scene": "proof", "action": "zoom", "target": "equation", "scale": 0.6}]

    # Elements that persist across scenes (with consistent color)
    persistent_elements: list[dict] = field(default_factory=list)
    # e.g. [{"name": "circle", "color_role": "primary", "appears_in": [1,2,3,4]}]

    def to_dict(self) -> dict:
        return asdict(self)


DESIGN_PROMPT = """You are a visual designer for educational animation videos (like 3Blue1Brown).

Given a story with scenes, design the COMPLETE visual system. Every visual choice must be
made here — the code generator should have zero creative decisions left.

Think like a film's art director:
- What COLOR PALETTE fits this story's mood? (not generic — specific to THIS narrative)
- What SHAPES and DIAGRAMS does each scene need? (be specific: "circle radius=1.5", not "a shape")
- How should elements ENTER and EXIT? (Create for shapes, Write for text, FadeIn for reveals)
- When should the CAMERA zoom/pan? (zoom into the aha moment, pull back for context)
- Which elements PERSIST across scenes? (the circle from scene 2 should still be there in scene 4)
- What COLOR means what? (if radius is green in scene 2, it MUST be green in scene 5)

CRITICAL: Be concrete and specific. Not "show a diagram" — say what diagram, what shapes,
what colors, what positions, what size.

Return JSON:
{
  "palette": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "highlight": "#hex",
    "neutral": "#ecf0f1",
    "background": "#000000"
  },
  "palette_reasoning": "why these colors fit this story",

  "color_roles": {
    "concept_name": "palette_key",
    ...
  },

  "typography": {
    "title": {"size": 42, "weight": "bold", "position": "UP*2.5"},
    "body": {"size": 28, "position": "ORIGIN"},
    "label": {"size": 22, "position": "next_to_parent"},
    "equation": {"size": 36, "position": "center"}
  },

  "animations": {
    "enter_shape": "Create or DrawBorderThenFill",
    "enter_text": "Write or FadeIn",
    "exit": "FadeOut",
    "emphasis": "Indicate or Circumscribe or Flash",
    "transition_between_scenes": "FadeOut then FadeIn, or Transform",
    "reveal_moment": "GrowFromCenter or scale(0)->scale(1) with Flash"
  },

  "camera_plan": [
    {"scene_index": 2, "action": "zoom_in", "target": "equation", "scale": 0.6, "timing": "after_write"},
    {"scene_index": 3, "action": "restore", "timing": "scene_start"}
  ],

  "persistent_elements": [
    {
      "name": "main_circle",
      "description": "the circle being analyzed",
      "color_role": "primary",
      "first_scene": 1,
      "last_scene": 5,
      "transforms": [
        {"in_scene": 3, "transforms_to": "sliced_circle"},
        {"in_scene": 4, "transforms_to": "rectangle"}
      ]
    }
  ],

  "scene_designs": [
    {
      "scene_index": 0,
      "scene_name": "from the story",
      "layout": {
        "top": {"element": "title", "type": "text"},
        "center": {"element": "main_visual", "type": "shape_or_diagram"},
        "bottom": {"element": "subtitle_or_label", "type": "text"}
      },
      "visual_elements": [
        {
          "name": "element_name",
          "type": "circle|rectangle|line|arrow|dot|axes|graph|text|vgroup",
          "color_role": "palette key",
          "position": "UP*2 or ORIGIN or next_to(other)",
          "size": "radius=1.5 or width=3,height=2 or font_size=28",
          "label": {"text": "r", "position": "below", "color_role": "same_as_parent"},
          "persists": true
        }
      ],
      "animation_sequence": [
        {"action": "enter", "element": "title", "style": "Write", "run_time": 1.5},
        {"action": "enter", "element": "circle", "style": "Create", "run_time": 2},
        {"action": "emphasis", "element": "circle", "style": "Indicate", "run_time": 1},
        {"action": "exit_all", "style": "FadeOut", "run_time": 1}
      ],
      "camera": "static or zoom_to(element)"
    }
  ]
}"""


def generate_design_system(story: dict, angle_title: str = "", angle_mood: str = "") -> DesignSystem:
    """Generate a complete design system for a video."""
    scenes_text = ""
    for i, scene in enumerate(story.get("scenes", [])):
        if isinstance(scene, dict):
            scenes_text += (
                f"\nScene {i+1}: {scene.get('name', '')}\n"
                f"  Visual: {scene.get('visual', scene.get('visual_description', ''))}\n"
                f"  Narration: \"{scene.get('narration', '')[:100]}\"\n"
                f"  Teaching: {scene.get('teaching_goal', scene.get('emotion', ''))}\n"
            )

    user_prompt = (
        f"Design the complete visual system for this video:\n\n"
        f"TITLE: {story.get('title', '')}\n"
        f"CREATIVE ANGLE: {angle_title}\n"
        f"MOOD: {angle_mood}\n\n"
        f"SCENES:\n{scenes_text}\n\n"
        f"Design EVERY visual choice: colors, shapes, animations, camera, layout.\n"
        f"Be concrete and specific — the code generator needs exact specifications.\n\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(DESIGN_PROMPT, user_prompt)
    data = extract_json(response)

    return DesignSystem(
        palette=data.get("palette", {}),
        color_roles=data.get("color_roles", {}),
        scene_designs=data.get("scene_designs", []),
        typography=data.get("typography", {}),
        animations=data.get("animations", {}),
        camera_plan=data.get("camera_plan", []),
        persistent_elements=data.get("persistent_elements", []),
    )


def design_to_codegen_context(design: DesignSystem) -> str:
    """Convert design system to context string for the code generator."""
    lines = ["## VISUAL DESIGN SYSTEM (follow this EXACTLY)\n"]

    # Palette
    if design.palette:
        lines.append("COLOR PALETTE:")
        for name, color in design.palette.items():
            lines.append(f"  {name}: \"{color}\"")

    # Color roles
    if design.color_roles:
        lines.append("\nCOLOR ROLES (use these consistently):")
        for concept, role in design.color_roles.items():
            color = design.palette.get(role, role)
            lines.append(f"  {concept} → \"{color}\"")

    # Typography
    if design.typography:
        lines.append("\nTYPOGRAPHY:")
        for level, spec in design.typography.items():
            size = spec.get("size", "?")
            pos = spec.get("position", "?")
            lines.append(f"  {level}: font_size={size}, position={pos}")

    # Animation vocabulary
    if design.animations:
        lines.append("\nANIMATION VOCABULARY:")
        for anim_type, style in design.animations.items():
            lines.append(f"  {anim_type}: {style}")

    # Camera plan
    if design.camera_plan:
        lines.append("\nCAMERA PLAN:")
        for cam in design.camera_plan:
            lines.append(
                f"  Scene {cam.get('scene_index', '?')}: {cam.get('action', '?')} "
                f"→ {cam.get('target', '?')} (scale {cam.get('scale', '?')})"
            )

    # Persistent elements
    if design.persistent_elements:
        lines.append("\nPERSISTENT ELEMENTS (same color across scenes):")
        for elem in design.persistent_elements:
            lines.append(
                f"  {elem.get('name', '?')}: color={elem.get('color_role', '?')}, "
                f"scenes {elem.get('first_scene', '?')}-{elem.get('last_scene', '?')}"
            )
            for t in elem.get("transforms", []):
                lines.append(f"    → transforms to \"{t.get('transforms_to', '?')}\" in scene {t.get('in_scene', '?')}")

    # Per-scene layouts
    if design.scene_designs:
        lines.append("\nSCENE LAYOUTS:")
        for sd in design.scene_designs:
            name = sd.get("scene_name", sd.get("scene_index", "?"))
            lines.append(f"\n  Scene '{name}':")
            layout = sd.get("layout", {})
            for zone, spec in layout.items():
                lines.append(f"    {zone}: {spec.get('element', '?')} ({spec.get('type', '?')})")
            for elem in sd.get("visual_elements", [])[:5]:
                lines.append(
                    f"    Element: {elem.get('name', '?')} ({elem.get('type', '?')}) "
                    f"color={elem.get('color_role', '?')} at {elem.get('position', '?')}"
                )

    return "\n".join(lines)


def print_design_system(design: DesignSystem):
    """Pretty-print a design system."""
    print("\n--- Design System ---")

    if design.palette:
        print("\nPalette:")
        for name, color in design.palette.items():
            print(f"  {name:12s}: {color}")

    if design.color_roles:
        print("\nColor Roles:")
        for concept, role in design.color_roles.items():
            print(f"  {concept:20s} → {role}")

    if design.persistent_elements:
        print(f"\nPersistent Elements ({len(design.persistent_elements)}):")
        for elem in design.persistent_elements:
            print(f"  {elem.get('name', '?')}: {elem.get('description', '')[:60]}")

    if design.scene_designs:
        print(f"\nScene Designs ({len(design.scene_designs)}):")
        for sd in design.scene_designs:
            name = sd.get("scene_name", sd.get("scene_index", "?"))
            elems = sd.get("visual_elements", [])
            print(f"  {name}: {len(elems)} visual elements")
