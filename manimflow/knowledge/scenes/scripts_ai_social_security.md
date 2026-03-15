---
source: https://github.com/gauravmeena0708/manim-scripts/blob/main/scenes/aiuse.py
project: manim-scripts
domain: [machine_learning, classification, statistics, graph_theory]
elements: [scatter_plot, dot, arrow, curved_arrow, line, label, box, rectangle_node, node, circle_node, graph, network, surrounding_rect, pipeline]
animations: [write, fade_in, fade_out, grow_from_center, draw, indicate, lagged_start, move, shift]
layouts: [centered, split_screen, flow_left_right, vertical_stack, edge_anchored]
techniques: [helper_function, factory_pattern, svg_integration, progressive_disclosure]
purpose: [demonstration, classification, relationship, process, overview]
mobjects: [Text, Tex, MathTex, Axes, Dot, Line, Arrow, Rectangle, SurroundingRectangle, SVGMobject, Graph, VGroup, Ellipse]
manim_animations: [Write, FadeIn, FadeOut, Create, GrowFromCenter, Indicate, LaggedStart, AnimationGroup, ReplacementTransform]
scene_type: Scene
manim_version: manim_community
complexity: intermediate
lines: 401
scene_classes: [IntroScene, LinearRegressionScene, ClassificationScene, AnomalyDetectionScene, NLPScene, OCRScene, RAGScene, GraphModelsScene]
---

## Summary

An 8-scene educational suite visualizing AI/ML techniques applied to social security (EPFO) use cases. Covers linear regression with scatter plot and prediction line, classification with decision boundary and document sorting, anomaly detection with normal/anomalous point clusters, NLP chatbot interaction, OCR document processing pipeline, RAG (Retrieval Augmented Generation) architecture, and graph-based fraud detection with Manim's Graph object and fraud ring highlighting. Shared helper functions `create_title()` and `show_application()` enforce consistent styling across scenes.

## Design Decisions

- **Shared helper functions**: `create_title()` and `show_application()` ensure every scene has the same title style (font_size=36, BOLD, to_edge UP) and application text style. This is critical for a multi-scene presentation — visual consistency signals that scenes belong together.
- **Axes with StealthTip**: The LinearRegressionScene uses `tip_shape=StealthTip` for arrow-style axis tips instead of the default triangular tips. More professional appearance.
- **SVGMobject with fallback**: NLP and RAG scenes try loading SVG files, falling back to Rectangle if the file is missing. Defensive coding for external assets.
- **Graph object for fraud detection**: Manim's built-in Graph with vertex_config per-node colors. Fraud ring nodes are RED, legitimate are BLUE/GREEN. Indicate animation on fraud nodes + edges highlights the ring.
- **t2c for keyword emphasis**: Application text uses `t2c={"EPFO": YELLOW}` to highlight domain keywords in yellow.
- **LaggedStart for scatter plots**: Data points create with lag_ratio=0.1, giving a "plotting one by one" feel rather than simultaneous appearance.

## Composition

- **LinearRegressionScene axes**: x_range=[0,10,2], y_range=[0,10,2], x_length=6, y_length=4, centered + UP*0.5
- **Axis labels**: get_x_axis_label/get_y_axis_label with edge=DOWN/LEFT, direction=DOWN/LEFT, buff=0.4
- **Classification data**: class1 at (1,1)-(2,1.8) range in BLUE, class2 at (2.8,2.5)-(4,3.5) in RED. All shifted to center.
- **Anomaly detection**: 30 normal dots in [-1,1]x[-0.5,0.5], 2 anomalies at [2.5,1.5] and [-2,-1.2]. Highlight circles radius=0.3.
- **RAG pipeline**: Query box LEFT*4+UP*1.5, LLM icon center UP*1.5, DB icon RIGHT*3.5+UP*1.5. Arrows with path_arc for curved connections.
- **Graph (GNN)**: 9 vertices with manual layout. Graph scale=0.9, shift UP*0.2.
- **Document bins**: Rectangle width=2.5, height=1, spaced 3 units apart

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Title text | WHITE | font_size=36, BOLD |
| Application text | WHITE | font_size=24, "EPFO"=YELLOW |
| Scatter points | BLUE | Dot |
| Regression line | GREEN | ax.plot |
| Class 1 dots | BLUE | Classification |
| Class 2 dots | RED | Classification |
| Decision boundary | GREEN | stroke_width=6 |
| Normal data points | BLUE_C | radius=0.05 |
| Anomalous points | RED | radius=0.1 |
| Anomaly highlight | YELLOW | Circle stroke_width=3 |
| Legitimate graph nodes | BLUE_C, GREEN_C | fill_color |
| Fraud graph nodes | RED_C | fill_color |
| LLM icon | PURPLE_A | Text |
| Query box | BLUE | SurroundingRectangle |
| Response box | GREEN | SurroundingRectangle |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Title Write | Default | Per scene |
| Scatter point creation | lag_ratio=0.1 | LaggedStart |
| GrowFromCenter dots | lag_ratio=0.1 | Classification |
| Anomaly Flash | run_time=1.5 | Yellow flash, 12 lines |
| Graph Create | Default | Full graph at once |
| Fraud ring Indicate | lag_ratio=0.1 | AnimationGroup |
| Document sorting | lag_ratio=0.1 | Items to bins |
| Scene wait | 2s | Standard |
| FadeOut transitions | Default | Between scenes |

## Patterns

### Pattern: Consistent Scene Template with Shared Helpers

**What**: Helper functions `create_title()` and `show_application()` standardize title and application text across all scenes. Every scene follows the same structure: title → visualization → application text → FadeOut all.
**When to use**: Multi-scene presentations, educational series, any project with 3+ scenes that need consistent styling. Also useful as a template for generating scene code programmatically.

```python
# Source: projects/manim-scripts/scenes/aiuse.py:6-22
def create_title(scene, text):
    title = Text(text, font_size=36, weight=BOLD)
    title.to_edge(UP)
    scene.play(Write(title))
    scene.wait(0.5)
    return title

def show_application(scene, app_text_str, position_relative_to=None, direction=DOWN, wait_time=2):
    app_text = Text(app_text_str, font_size=24, t2c={"EPFO": YELLOW, "Social Security": YELLOW})
    if position_relative_to:
        app_text.next_to(position_relative_to, direction, buff=0.5)
    else:
        app_text.center().shift(DOWN*1.5)
    scene.play(FadeIn(app_text, shift=UP*0.5))
    scene.wait(wait_time)
    return app_text
```

### Pattern: Graph-Based Fraud Ring Detection Visualization

**What**: Use Manim's Graph object with per-vertex colors to represent an entity network. Fraud ring nodes are colored RED_C. After the graph appears, Indicate animations on fraud nodes and edges highlight the suspicious cluster. Uses AnimationGroup with lag_ratio for staggered highlighting.
**When to use**: Social network analysis, fraud detection visualization, any graph where a subgraph needs to be highlighted as anomalous. Also useful for community detection, influence networks.

```python
# Source: projects/manim-scripts/scenes/aiuse.py:353-393
graph = Graph(
    vertices, edges, layout=layout, labels=True,
    vertex_config={v: {"fill_color": nodes_data[v]["color"], "radius": 0.3} for v in vertices},
    edge_config={"stroke_width": 2}
)
self.play(Create(graph))
# Highlight fraud ring
fraud_ring_nodes = ["M3", "E2", "B2", "A1"]
highlight_anims = []
for node_key in fraud_ring_nodes:
    highlight_anims.append(Indicate(graph.vertices[node_key], color=RED, scale_factor=1.5))
for u, v in fraud_ring_edges_tuples:
    if (u,v) in graph.edges:
        highlight_anims.append(Indicate(graph.edges[(u,v)], color=RED, scale_factor=1.2))
self.play(AnimationGroup(*highlight_anims, lag_ratio=0.1))
```

### Pattern: Anomaly Detection with Flash Highlight

**What**: Normal data points as small blue dots in a cluster. Anomalies as larger red dots outside the cluster. After all points appear, Flash animation + SurroundingRectangle on each anomaly creates a "detection" effect. Color-based filtering identifies which points are anomalies.
**When to use**: Anomaly/outlier visualization, quality control dashboards, any scatter plot where certain points need to be flagged after initial display.

```python
# Source: projects/manim-scripts/scenes/aiuse.py:146-174
normal_points = VGroup()
for _ in range(30):
    point = Dot([random.uniform(-1,1), random.uniform(-0.5,0.5), 0], color=BLUE_C, radius=0.05)
    normal_points.add(point)
anomaly1 = Dot([2.5, 1.5, 0], color=RED, radius=0.1)
# After display...
highlight_circles = VGroup(*[Circle(radius=0.3, color=YELLOW, stroke_width=3).move_to(a.get_center()) for a in anomalies])
self.play(LaggedStart(*[Create(c) for c in highlight_circles], lag_ratio=0.3))
```

### Pattern: RAG Architecture Pipeline Diagram

**What**: Visualizes Retrieval Augmented Generation as a flow diagram: User query → LLM → Knowledge Base (with curved arrow for retrieval) → Generated response. Arrows with path_arc create curved connections. SVGMobject for database icon with Rectangle fallback.
**When to use**: Any AI/ML pipeline visualization, system architecture diagrams, information flow through components. The curved arrow pattern is useful for showing bidirectional or feedback connections.

```python
# Source: projects/manim-scripts/scenes/aiuse.py:266-310
query_group = VGroup(query_text, query_box).shift(LEFT*4 + UP*1.5)
llm_icon = Text("LLM", font_size=28, color=PURPLE_A).shift(UP*1.5)
arrow_llm_to_db = Arrow(llm_icon.get_right(), db_icon.get_left(), buff=0.2, path_arc=-0.5*PI)
arrow_db_to_llm = Arrow(db_icon.get_left(), llm_icon.get_right(), buff=0.2, path_arc=-0.5*PI)
arrow_llm_to_response = Arrow(llm_icon.get_bottom(), response_group.get_top(), buff=0.2)
```

## Scene Flow

1. **IntroScene** (0-7s): "AI in Social Security" title, subtitle, EPFO mention. All fade out.
2. **LinearRegressionScene** (0-15s): Axes with labels. 9 scatter points lag in. Green regression line. Application text.
3. **ClassificationScene** (0-15s): Two-class dots. Green decision boundary. Document sorting to bins animation.
4. **AnomalyDetectionScene** (0-12s): 30 normal dots + 2 anomalies. Yellow highlight circles on anomalies. Application text.
5. **NLPScene** (0-12s): User chat bubble, chatbot icon (thinking → responding), AI response bubble. Application text.
6. **OCRScene** (0-12s): Scanned document rectangle with lines → arrow → extracted text. Application text.
7. **RAGScene** (0-15s): Query → LLM → Knowledge Base retrieval → contextual response. Curved arrows for retrieval flow.
8. **GraphModelsScene** (0-15s): 9-node entity graph creates. Fraud ring (4 nodes) highlighted with Indicate. Application text.

> Full file: `projects/manim-scripts/scenes/aiuse.py` (401 lines)
