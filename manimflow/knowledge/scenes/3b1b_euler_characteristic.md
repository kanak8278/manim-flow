---
source: https://github.com/3b1b/videos/blob/main/_2015/eulers_characteristic_formula.py
project: videos
domain: [topology, geometry, mathematics, combinatorics]
elements: [graph, node, line, dot, label, equation, pi_creature]
animations: [write, draw, transform, fade_in, fade_out, color_change, rotate]
layouts: [centered, radial]
techniques: [custom_mobject, helper_function, progressive_disclosure]
purpose: [proof, definition, demonstration, step_by_step]
mobjects: [GraphScene, VGroup, Line, Dot, OldTex, OldTexText, Face, SpeechBubble, Circle, Cube]
manim_animations: [ShowCreation, FadeIn, FadeOut, Write, Transform, CounterclockwiseTransform, Rotating, WalkPiCreature, ApplyMethod]
scene_type: GraphScene
manim_version: manimlib
complexity: intermediate
lines: 1186
scene_classes: [EulersFormulaWords, IllustrateDuality, IntroduceGraph, TerminologyFromPolyhedra, ThreePiecesOfTerminology, DefineSpanningTree, WalkingRandolph]
---

## Summary

Visualizes Euler's characteristic formula V-E+F=2 for connected planar graphs. Built on a custom GraphScene base class that manages vertices (Dots), edges (Lines), and regions. Demonstrates graph duality by transforming edges and vertices into their duals. Introduces three key concepts — cycles, spanning trees, and dual graphs — using Randolph (pi creature) walking along graph paths. The proof construction uses spanning tree + dual spanning tree to show the formula holds. Uses very early manimlib (2015) with face-based and region-based rendering.

## Design Decisions

- **GraphScene base class**: Manages graph data structure, vertex positions, edge drawing, and region generation. Provides draw_vertices, draw_edges, generate_spanning_tree, generate_dual_graph methods. This encapsulates all graph operations.
- **Randolph walks the graph**: A pi creature (scaled to 0.3) physically walks along graph edges via WalkPiCreature animation. Path visualization as yellow lines. This makes abstract graph traversal concrete.
- **Duality as Transform**: Graph edges and dual edges are paired, and Transform animates each pair simultaneously (run_time=5 with special_alpha rate function). Vertices morph into dual vertices (one per face). The duality becomes a visual morphing operation.
- **Three-term introduction**: Cycles, Spanning Trees, Dual Graphs introduced as three terms with vertical layout. Each is accented (scaled, colored YELLOW) when active, then toned down.
- **Polyhedron to graph transition**: A 3D cube (Rotating with radians=PI/3) flattens into a planar graph. "Dots -> Vertices", "Lines -> Edges", "Regions -> Faces" labels appear sequentially. This connects 3D polyhedra to 2D graph theory.
- **Face-based SpeechBubble**: The Face class and SpeechBubble provide a dialogue interface for teacher-student interactions within the proof narrative.

## Composition

- **Graph**: SampleGraph with 9 vertices and edges. Vertices as Dots at predefined positions. Edges as Lines between vertex positions.
- **Randolph**: scale=0.3 (RANDOLPH_SCALE_FACTOR). Walks along paths defined by vertex index lists.
- **Edge annotations**: scale=0.7 (EDGE_ANNOTATION_SCALE_FACTOR). Labels at edge midpoints (e.g., "Friends", dollar signs).
- **Terminology**: Three labels at y=3, 1, -1 with to_edge alignment. Accent via scale(1.2) + set_color("yellow").
- **Cube**: 3D wireframe rotating about [0,0,1] then [0,1,0]. Transitions to planar graph.
- **Spanning tree**: Generated from graph, shown as yellow highlighted edges.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Graph edges | WHITE | Default lines |
| Spanning tree | YELLOW | Highlighted edges |
| Cycles | YELLOW | Accented label |
| Dual graphs | RED | Accented label |
| Randolph | BLUE | Default pi creature |
| Path trace | YELLOW | Line along walked path |
| Vertices | WHITE | Dot default |
| Green dots | LIGHTGREEN | Spanning tree visited nodes |
| Unneeded edges | RED | Edges not in spanning tree |
| Regions | Various | set_color_region for faces |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Duality transform | run_time=5 | special_alpha rate_func |
| Graph drawing | run_time=1 | draw_vertices + draw_edges |
| Randolph walking | run_time=2 per edge | WalkPiCreature + line ShowCreation |
| Spanning tree build | run_time=0.5 per branch | Sequential edge + vertex |
| Cube rotation | run_time=5 | radians=PI/3 |
| Term accent | instant | scale(1.2) + set_color |

## Patterns

### Pattern: Graph Scene with Duality Transform

**What**: A GraphScene base class that generates graph vertices, edges, and regions. The generate_dual_graph method creates dual vertices (one per face) and dual edges. Duality is animated by pairing each edge with its dual and running simultaneous Transforms. The special_alpha rate_func creates a morph that goes forward, pauses, and returns — showing the correspondence.

**When to use**: Graph theory visualization, planar graph proofs, duality demonstrations, Euler formula proofs. The GraphScene pattern is reusable for any graph algorithm visualization.

```python
# Source: projects/videos/_2015/eulers_characteristic_formula.py:62-97
class IllustrateDuality(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        self.generate_dual_graph()
        def special_alpha(t):
            if t > 0.5: t = 1 - t
            return smooth(4*t) if t < 0.25 else 1
        self.play(*[
            Transform(*edge_pair, run_time=5, rate_func=special_alpha)
            for edge_pair in zip(self.edges, self.dual_edges)
        ] + [
            Transform(Mobject(*[self.vertices[i] for i in cycle]), dv, ...)
            for cycle, dv in zip(self.graph.region_cycles, self.dual_vertices)
        ])
```

### Pattern: Pi Creature Walking Graph Paths

**What**: A Randolph character physically walks along graph edges. At each step, the creature moves to the next vertex (WalkPiCreature) while a yellow Line is drawn along the traversed edge (ShowCreation). The path is defined as a list of vertex indices.

**When to use**: Graph traversal demonstrations (BFS, DFS, shortest path), any algorithm that visits nodes in sequence. The walking character makes the traversal order visceral.

```python
# Source: projects/videos/_2015/eulers_characteristic_formula.py:320-344
class WalkingRandolph(GraphScene):
    def construct(self):
        GraphScene.construct(self)
        point_path = [self.get_points()[i] for i in self.path]
        randy = Randolph().scale(RANDOLPH_SCALE_FACTOR)
        randy.move_to(point_path[0])
        for next, last in zip(point_path[1:], point_path):
            self.play(
                WalkPiCreature(randy, next),
                ShowCreation(Line(last, next).set_color("yellow")),
                run_time=2.0
            )
```

## Scene Flow

1. **V-E+F=2** (0-5s): Formula displayed as OldTex.
2. **Introduce Graph** (5-30s): Connected planar graph drawn. "Connected Planar Graph" labels appear. Demonstration of non-planar graph (edges removed), non-connected graph.
3. **Polyhedron Connection** (30-60s): 3D cube rotates, then flattens to planar graph. "Dots->Vertices, Lines->Edges, Regions->Faces" terminology.
4. **Three Concepts** (60-90s): Cycles, Spanning Trees, Dual Graphs introduced. Each demonstrated on the sample graph.
5. **Spanning Tree Walk** (90-120s): Randolph walks the graph, building a spanning tree. Unneeded edges marked RED with "unneeded!" labels.
6. **Duality** (120-150s): Graph edges morph into dual edges. Vertices morph into face-center dual vertices. The dual spanning tree revealed.
7. **Proof** (150-180s): Spanning tree has V-1 edges. Dual spanning tree has F-1 edges. Together they account for all E edges. V-1+F-1=E, so V-E+F=2.

> Note: Very early manimlib (2015). Uses deprecated APIs: Face, SpeechBubble, region_from_polygon_vertices, set_color_region, WalkPiCreature, GraphScene. Scene classes chain via constructor inheritance.
