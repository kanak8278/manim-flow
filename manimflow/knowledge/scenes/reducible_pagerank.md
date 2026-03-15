---
source: https://github.com/nipunramk/Reducible/blob/main/2022/PageRank/markov_chain.py
project: Reducible
domain: [computer_science, algorithms, graph_theory, probability, mathematics]
elements: [directed_graph, node, circle_node, curved_arrow, arrow, label, dot, matrix, equation, formula, bar_chart]
animations: [fade_in, fade_out, write, transform, highlight, indicate, dim, move, color_change, lagged_start]
layouts: [centered, radial, scattered, side_by_side]
techniques: [custom_mobject, brand_palette, algorithm_class_separation, data_driven, progressive_disclosure, overlay_tracking]
purpose: [step_by_step, demonstration, simulation, process, derivation, exploration]
mobjects: [Graph, Circle, Arrow, CurvedArrow, Dot, Text, Tex, MathTex, VGroup, Matrix]
manim_animations: [FadeIn, FadeOut, Write, Transform, LaggedStart, ReplacementTransform, AnimationGroup]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 3512
scene_classes: [MarkovChain, MarkovChainGraph, MarkovChainSimulator, MarkovChainTester, IntroWebGraph, UserSimulationWebGraph, MarkovChainIntroEdited, IntroImportanceProblem, IntroStationaryDistribution, Uniqueness, Periodicity, IntroduceBigTheorem1, PageRank, PageRankAlphaIntro, EigenValueMethodFixed2]
---

## Summary

Visualizes Markov chains and PageRank using a custom MarkovChainGraph class that extends Manim's Graph with directed edges, curved double arrows, transition probability labels, and dynamic edge updaters. Features a MarkovChainSimulator that places yellow dots (users) on graph nodes and animates their probabilistic transitions, demonstrating convergence to stationary distributions. Covers irreducibility, aperiodicity, eigenvalue methods, and the damping factor.

## Design Decisions

- **MarkovChainGraph extends Graph**: Custom class auto-creates curved arrows for bidirectional edges and straight arrows for one-way edges. An updater keeps edge endpoints connected to vertices even when vertices move.
- **CustomCurvedArrow with proper tips**: Standard CurvedArrow tips break on short curves, so tips are popped and re-added with ArrowTriangleFilledTip at 0.15 length. Tip z_index=-100 prevents overlap issues.
- **User dots for simulation**: 50 yellow dots (radius=0.035) distributed across nodes using Poisson distribution around vertex centers. Transitions animated per-step to show random walk convergence.
- **Edge dimming for focus**: When highlighting specific edges/states, all other edges dim to opacity=0.3 and labels fade. This progressive disclosure technique prevents visual overload on dense directed graphs.
- **Transition labels at 20% along edge**: Labels placed at `point_from_proportion(0.2)` rather than midpoint, because curved arrow midpoints can overlap the vertex they curve around.
- **State color map**: Optional per-state color customization via `state_color_map` dict, allowing visual grouping of communicating classes.

## Composition

- **MarkovChainGraph**: Default scale 1.2 for 4-state chains, clear_updaters() before scaling
- **Transition labels**: SF Mono font, scale=0.3, BLACK stroke background (width=8, opacity=0.8)
- **Web graph**: 384 nodes on a grid with noise, radius-based edge generation (distance < 0.8), no labels
- **User dots**: Dot(radius=0.035), REDUCIBLE_YELLOW, opacity=0.6, stroke width=2
- **Simulation users (web)**: 3000 users, radius=0.01 for web graph scale
- **Matrix displays**: Standard Manim Matrix, scale 0.8
- **Equations**: Tex/MathTex, scale 0.7-0.8, positioned UP*3.5 or DOWN*3

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Vertex stroke | REDUCIBLE_PURPLE (#8c4dfb) | stroke_width=3 |
| Vertex fill | REDUCIBLE_PURPLE | fill_opacity=0.5 |
| Edges (curved) | REDUCIBLE_VIOLET (#d7b5fe) | stroke_width=3, radius=4 |
| Edges (straight) | REDUCIBLE_VIOLET | stroke_width=3, Arrow |
| Transition labels | SF Mono, WHITE | BLACK stroke background |
| Highlighted labels | REDUCIBLE_YELLOW (#ffff5c) | Focus color for probabilities |
| User dots | REDUCIBLE_YELLOW | opacity=0.6, stroke_width=2 |
| Glowing surround | via get_glowing_surround_circle() | Highlights active vertex |
| Dimmed elements | opacity=0.3 | Edges, tips, labels when not focused |
| Text labels | CMU Serif, BOLD | States label, Transition Probabilities |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| FadeIn graph + labels | default | Single play call |
| Edge highlight/dim | default | Batch opacity changes |
| User transition step | default | All users move simultaneously |
| LaggedStart transitions | per-state groups | Lagged by state for visual clarity |
| Web graph simulation | 50 steps | rate_func=linear per step |
| Total video | ~25 minutes | Full PageRank tutorial |

## Patterns

### Pattern: Directed Graph with Curved Double Arrows

**What**: MarkovChainGraph auto-detects bidirectional edges and renders them as curved arrows to avoid overlap. Unidirectional edges get straight arrows. Edge endpoints update when vertices move via a graph updater.

**When to use**: Markov chains, state machines, web link graphs, any directed graph where two nodes can point to each other. Also useful for network flow with bidirectional capacity.

```python
# Source: projects/Reducible/2022/PageRank/markov_chain.py:133-217
class MarkovChainGraph(Graph):
    def __init__(self, markov_chain, vertex_config={...},
                 enable_curved_double_arrows=True, labels=True, **kwargs):
        super().__init__(markov_chain.get_states(), markov_chain.get_edges(),
                         vertex_config=vertex_config, labels=labels, **kwargs)
        self._graph = self._graph.to_directed()
        self.remove_edges(*self.edges)
        self.add_markov_chain_edges(*markov_chain.get_edges(), ...)

        def update_edges(graph):
            for (u, v), edge in graph.edges.items():
                v_c = self.vertices[v].get_center()
                u_c = self.vertices[u].get_center()
                vec = v_c - u_c
                unit_vec = vec / np.linalg.norm(vec)
                arrow_start = u_c + unit_vec * self.vertices[u].width / 2
                arrow_end = v_c - unit_vec * self.vertices[v].width / 2
                edge.put_start_and_end_on(arrow_start, arrow_end)
        self.add_updater(update_edges)
```

### Pattern: Transition Probability Labels on Edges

**What**: Generates a VGroup of probability labels from the transition matrix, positioned at 20% along each edge. Labels auto-update position via updater when edges move. Uses SF Mono with BLACK stroke background for readability on any edge color.

**When to use**: Weighted directed graphs, Markov chains, probability networks, any graph where edge weights need to be displayed as text.

```python
# Source: projects/Reducible/2022/PageRank/markov_chain.py:328-368
def get_transition_labels(self, scale=0.3, round_val=True):
    tm = self.markov_chain.get_transition_matrix()
    labels = VGroup()
    for s in range(len(tm)):
        for e in range(len(tm[0])):
            if s != e and tm[s, e] != 0:
                matrix_prob = tm[s, e]
                label = (Text(str(matrix_prob), font=REDUCIBLE_MONO)
                    .set_stroke(BLACK, width=8, background=True, opacity=0.8)
                    .scale(scale)
                    .move_to(self.edges[(s, e)].point_from_proportion(0.2)))
                labels.add(label)
                self.labels[(s, e)] = label
    def update_labels(graph):
        for e, l in graph.labels.items():
            l.move_to(graph.edges[e].point_from_proportion(0.2))
    self.add_updater(update_labels)
    return labels
```

### Pattern: Random Walk Simulation with Dot Agents

**What**: MarkovChainSimulator creates N dot agents distributed across graph states. Each step, agents transition according to the Markov chain's probability matrix. Agents positioned around vertex centers using Poisson distribution (Gaussian noise within vertex radius).

**When to use**: Random walk visualization, convergence demonstrations, PageRank intuition, any scenario where multiple agents traverse a probabilistic graph to show emergent distribution.

```python
# Source: projects/Reducible/2022/PageRank/markov_chain.py:371-457
class MarkovChainSimulator:
    def __init__(self, markov_chain, markov_chain_g, num_users=50, user_radius=0.035):
        self.users = [
            Dot(radius=self.user_radius).set_color(REDUCIBLE_YELLOW)
            .set_opacity(0.6).set_stroke(REDUCIBLE_YELLOW, width=2, opacity=0.8)
            for _ in range(self.num_users)]
        # Distribute to initial states
        for user_id, user in enumerate(self.users):
            user.move_to(self.get_user_location(user_id))

    def get_instant_transition_animations(self):
        self.transition()
        return [user.animate.move_to(self.get_user_location(user_id))
                for user_id, user in enumerate(self.users)]
```

### Pattern: Edge Focus via Opacity Dimming

**What**: Highlights specific edges by dimming all others to opacity=0.3. Both the edge stroke and tip must be separately animated (tips don't inherit parent opacity). Labels also dimmed. Reset function restores all to opacity=1.

**When to use**: Explaining specific transitions in a dense graph, focusing on one path through a network, any directed graph where you need to draw attention to specific edges.

```python
# Source: projects/Reducible/2022/PageRank/markov_chain.py:790-846
def highlight_edge(self, markov_chain_g, edge_tuple):
    highlight_animations = []
    for edge in markov_chain_g.edges:
        if edge == edge_tuple:
            highlight_animations.extend([
                markov_chain_g.edges[edge].animate.set_stroke(opacity=1),
                markov_chain_g.edges[edge].tip.animate.set_stroke(opacity=1).set_fill(opacity=1),
                markov_chain_g.labels[edge].animate.set_fill(color=REDUCIBLE_YELLOW, opacity=1),
            ])
        else:
            highlight_animations.extend([
                markov_chain_g.edges[edge].animate.set_stroke(opacity=0.3),
                markov_chain_g.edges[edge].tip.animate.set_stroke(opacity=0.3).set_fill(opacity=0.3),
                markov_chain_g.labels[edge].animate.set_fill(color=WHITE, opacity=0.3),
            ])
    self.play(*highlight_animations)
```

## Scene Flow

1. **Web Graph Intro** (0-2min): 384-node web graph with proximity edges. 3000 user dots simulate random surfing.
2. **Markov Chain Basics** (2-8min): 4-state chain with curved arrows. Highlight states, then transitions. Show P(i,j) notation. Modify transition probabilities live.
3. **Importance Problem** (8-12min): Which states are most important? Introduce stationary distribution concept.
4. **Stationary Distribution** (12-16min): Matrix power method visualization. Show distribution convergence over iterations.
5. **Uniqueness & Periodicity** (16-20min): Demonstrate reducible and periodic chains that break convergence. Visual proof via state color grouping.
6. **PageRank** (20-25min): Apply Markov chain theory to web pages. Introduce damping factor alpha. Eigenvalue method for computing stationary distribution.
