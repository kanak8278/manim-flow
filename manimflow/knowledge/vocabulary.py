"""Controlled vocabulary for the ManimFlow knowledge system.

This vocabulary bridges the gap between what the pipeline describes
(screenplay shots, story elements) and what the knowledge docs contain
(indexed patterns, techniques). Both sides use these exact terms.

Extracted from 836 Python files across 14 real Manim projects.
"""

# =============================================================================
# DOMAINS — What topic is the video about?
# =============================================================================
DOMAINS = {
    # Mathematics
    "mathematics",
    "algebra",
    "linear_algebra",
    "calculus",
    "differential_equations",
    "geometry",
    "trigonometry",
    "topology",
    "number_theory",
    "complex_analysis",
    "combinatorics",
    "set_theory",
    "probability",
    "statistics",
    "game_theory",
    "fractal",

    # Physics
    "physics",
    "mechanics",
    "electromagnetism",
    "optics",
    "waves",
    "thermodynamics",
    "quantum_mechanics",
    "relativity",
    "astronomy",
    "fluid_dynamics",
    "acoustics",
    "pendulum",
    "collision",
    "gravity",
    "magnetism",

    # Computer Science
    "computer_science",
    "algorithms",
    "sorting",
    "searching",
    "data_structures",
    "graph_theory",
    "dynamic_programming",
    "recursion",
    "complexity",
    "compression",
    "cryptography",
    "error_correction",
    "automata",
    "formal_languages",

    # Machine Learning & AI
    "machine_learning",
    "neural_networks",
    "deep_learning",
    "nlp",
    "transformers",
    "reinforcement_learning",
    "clustering",
    "classification",
    "regression",
    "optimization",
    "computer_vision",
    "attention_mechanism",
    "backpropagation",
    "activation_functions",

    # Applied / Other
    "finance",
    "economics",
    "biology",
    "chemistry",
    "electronics",
    "signal_processing",
    "image_processing",
    "information_theory",
    "music",
    "data_visualization",
    "education",
}

# =============================================================================
# ELEMENTS — What visual objects are on screen?
# =============================================================================
ELEMENTS = {
    # Data representations
    "array",
    "matrix",
    "table",
    "bar_chart",
    "scatter_plot",
    "pie_chart",
    "histogram",
    "heatmap",
    "number_line",
    "axes",
    "coordinate_system",
    "polar_plot",
    "complex_plane",

    # Structural shapes
    "card",
    "box",
    "rounded_box",
    "node",
    "circle_node",
    "rectangle_node",
    "label",
    "badge",
    "dot",
    "pixel",
    "pixel_grid",

    # Connectors
    "arrow",
    "curved_arrow",
    "double_arrow",
    "line",
    "dashed_line",
    "brace",
    "bracket",
    "underline",
    "arc",

    # Graphs & Trees
    "tree",
    "binary_tree",
    "graph",
    "network",
    "directed_graph",
    "state_machine",
    "markov_chain",

    # Flows & Sequences
    "pipeline",
    "flowchart",
    "timeline",
    "sequence",
    "process_diagram",

    # Mathematical
    "equation",
    "formula",
    "function_plot",
    "parametric_curve",
    "vector",
    "vector_field",
    "surface_3d",
    "riemann_rectangles",
    "tangent_line",
    "area_under_curve",

    # Text
    "title",
    "subtitle",
    "paragraph",
    "quote_box",
    "code_block",
    "bullet_list",
    "numbered_list",
    "caption",

    # Containers & Groups
    "group",
    "grid",
    "row",
    "column",
    "section",
    "frame",

    # Indicators & Markers
    "pointer",
    "overlay",
    "highlight_rect",
    "surrounding_rect",
    "cross_mark",
    "checkmark",
    "cursor",

    # Media & Assets
    "image",
    "svg_icon",
    "character",
    "pi_creature",
    "speech_bubble",

    # 3D Objects
    "cube",
    "sphere",
    "cylinder",
    "cone",
    "prism",
    "torus",
    "surface",

    # Physics-specific
    "wave",
    "oscillator",
    "particle",
    "field_line",
    "circuit",
    "resistor",
    "battery",
    "led",
    "speaker",

    # ML-specific
    "neuron",
    "layer",
    "weight_connection",
    "activation_graph",
    "loss_curve",
    "decision_boundary",
    "embedding_space",
    "attention_map",
    "token",

    # Chemistry-specific
    "molecule",
    "atom",
    "bond",
    "orbital",
    "reaction_arrow",
}

# =============================================================================
# ANIMATIONS — What motion/change happens?
# =============================================================================
ANIMATIONS = {
    # Appear / Disappear
    "fade_in",
    "fade_out",
    "grow",
    "grow_from_center",
    "grow_from_edge",
    "shrink",
    "write",
    "unwrite",
    "draw",
    "draw_then_fill",
    "dissolve",
    "pop_in",
    "spin_in",

    # Movement
    "move",
    "slide",
    "swap",
    "arc_swap",
    "shift",
    "follow_path",
    "move_along_path",
    "orbit",
    "bounce",

    # Transform
    "transform",
    "morph",
    "replace",
    "replacement_transform",
    "transform_from_copy",
    "split",
    "merge",
    "reshape",
    "scale_up",
    "scale_down",

    # Emphasis
    "highlight",
    "indicate",
    "flash",
    "pulse",
    "wiggle",
    "color_change",
    "dim",
    "undim",
    "glow",
    "passing_flash",

    # Connectors
    "connect",
    "disconnect",
    "grow_arrow",
    "trace_line",
    "trace_path",

    # Data-driven
    "update_value",
    "animate_parameter",
    "count_up",
    "count_down",
    "progress_bar",
    "sweep",

    # Sequencing
    "stagger",
    "cascade",
    "lagged_start",
    "one_by_one",
    "simultaneous",
    "wave_effect",

    # Camera
    "zoom_in",
    "zoom_out",
    "pan",
    "focus",
    "camera_rotate",
    "camera_follow",

    # Rotation
    "rotate",
    "spin",
    "flip",

    # Scene-level
    "clear_screen",
    "scene_transition",
    "cross_fade",
}

# =============================================================================
# LAYOUTS — How are things arranged on screen?
# =============================================================================
LAYOUTS = {
    "side_by_side",
    "split_screen",
    "vertical_stack",
    "horizontal_row",
    "grid",
    "arranged_grid",
    "radial",
    "circular",
    "hierarchy",
    "tree_layout",
    "flow_left_right",
    "flow_top_down",
    "centered",
    "edge_anchored",
    "scattered",
    "clustered",
    "layered",
    "nested",
    "diagonal",
    "three_zone",
    "dual_panel",
    "overlay_stack",
}

# =============================================================================
# TECHNIQUES — What Manim-specific approach is used?
# =============================================================================
TECHNIQUES = {
    # Core dynamic patterns
    "value_tracker",
    "always_redraw",
    "add_updater",
    "update_from_alpha_func",

    # Camera
    "moving_camera",
    "zoomed_scene",
    "camera_save_restore",
    "ambient_camera_rotation",
    "three_d_camera",

    # Scene types
    "voiceover_scene",
    "interactive_scene",
    "teacher_students_scene",

    # Color
    "color_state_machine",
    "brand_palette",
    "color_gradient",
    "tex_to_color_map",
    "semantic_color",

    # Math rendering
    "math_tex",
    "surrounding_rectangle",
    "brace_annotation",
    "equation_transform",

    # Data
    "algorithm_class_separation",
    "history_replay",
    "scipy_integration",
    "data_driven",

    # Reusable components
    "helper_function",
    "factory_pattern",
    "custom_mobject",
    "custom_animation",

    # Visual effects
    "arc_path",
    "traced_path",
    "passing_flash_signal",
    "svg_integration",
    "image_integration",
    "shader_custom",
    "dual_track_visualization",

    # Layout helpers
    "overlay_tracking",
    "labeled_pointer",
    "status_text",
    "step_counter",

    # Narrative
    "multi_scene_in_one_class",
    "scene_segmentation",
    "progressive_disclosure",
    "before_after_comparison",

    # Error avoidance
    "lambda_capture_i",
    "if_mobjects_guard",
    "ascii_only_text",
}

# =============================================================================
# VISUAL PURPOSE — Why is this visual on screen?
# =============================================================================
VISUAL_PURPOSE = {
    "comparison",
    "progression",
    "decomposition",
    "accumulation",
    "transformation",
    "classification",
    "ranking",
    "distribution",
    "relationship",
    "process",
    "hierarchy",
    "cycle",
    "cause_effect",
    "part_whole",
    "before_after",
    "step_by_step",
    "proof",
    "derivation",
    "demonstration",
    "simulation",
    "exploration",
    "analogy",
    "counterexample",
    "definition",
    "overview",
}

# =============================================================================
# COMPLETE VOCABULARY — all terms combined for search
# =============================================================================
ALL_TERMS = DOMAINS | ELEMENTS | ANIMATIONS | LAYOUTS | TECHNIQUES | VISUAL_PURPOSE


def get_vocabulary_stats() -> dict:
    """Return counts for each vocabulary category."""
    return {
        "domains": len(DOMAINS),
        "elements": len(ELEMENTS),
        "animations": len(ANIMATIONS),
        "layouts": len(LAYOUTS),
        "techniques": len(TECHNIQUES),
        "visual_purpose": len(VISUAL_PURPOSE),
        "total": len(ALL_TERMS),
    }
