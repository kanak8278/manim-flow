---
source: https://github.com/nipunramk/Reducible/blob/main/2022/TSPProblem/solving_tsp.py
project: Reducible
domain: [computer_science, algorithms, graph_theory, complexity]
elements: [graph, node, circle_node, directed_graph, arrow, label, surrounding_rect, dot, line, bar_chart]
animations: [fade_in, fade_out, write, transform, grow, lagged_start, highlight, indicate, passing_flash, color_change, move]
layouts: [centered, scattered, side_by_side, flow_left_right]
techniques: [custom_mobject, brand_palette, algorithm_class_separation, progressive_disclosure, data_driven]
purpose: [step_by_step, demonstration, comparison, simulation, exploration]
mobjects: [Graph, Line, Arrow, CurvedArrow, Dot, Text, Tex, MathTex, VGroup, SurroundingRectangle, Module, RoundedRectangle]
manim_animations: [FadeIn, FadeOut, Write, Transform, LaggedStartMap, GrowFromCenter, ShowPassingFlash, ReplacementTransform]
scene_type: Scene
manim_version: manim_community
complexity: advanced
lines: 4994
scene_classes: [TSPGraph, TSPTester, NearestNeighbor2, LowerBoundTSP, GreedyApproach2, Christofides, TourImprovement, LocalMinima, Ant, AntColonySimulation, AntColonyExplanation, AntSimulation, SimulatedAnnealingIntro, Conclusion, ConclusionFlow]
---

## Summary

Comprehensive TSP (Travelling Salesman Problem) visualization covering heuristic approaches: nearest neighbor, greedy edge insertion, Christofides algorithm, 2-opt tour improvement, ant colony optimization, and simulated annealing. Uses a custom TSPGraph class extending Manim's Graph for complete graph handling with distance matrices. Features Reducible's branded Module boxes for conceptual flow diagrams and yellow ShowPassingFlash for edge selection animations.

## Design Decisions

- **TSPGraph extends Graph**: Custom class wraps Manim's Graph to add distance matrices, tour edge generation, and subset edge sampling. This separation lets scenes focus on animation logic without graph math.
- **Scattered layout from random positions**: Cities placed at random frame positions to look like real TSP instances. Layout dict maps vertex IDs to coordinates via `get_random_points_in_frame()`.
- **Yellow ShowPassingFlash for edge selection**: When the nearest neighbor algorithm picks an edge, a yellow flash travels along it then the edge stays yellow. Visually distinguishes "selected" from "considered" edges.
- **Module boxes for conceptual diagrams**: Heuristic Solution, Optimal Solution, Lower Bound shown as color-coded Module boxes (purple, green, yellow) with curved arrows between them to illustrate approximation ratios.
- **Ant as Dot mob**: Each ant in the colony is a tiny yellow Dot (radius=0.02) that moves along tour edges. Pheromone-weighted probability drives next-vertex selection.
- **Side-by-side comparison**: NN tour vs optimal tour shown at 0.6 scale, shifted LEFT*3.2 and RIGHT*3.2, with distance labels above each.
- **Background image**: All scenes add a dark background image (bg-75.png) for the branded Reducible look.

## Composition

- **Graph placement**: TSPGraph with circular or random layout, scaled 0.8, shifted UP*0.5 for room below
- **Module boxes**: width=4, height=2, arranged with `arrange(RIGHT, buff=1)`, scale 0.7 for multi-module layouts
- **Side-by-side graphs**: scale 0.6, shift LEFT*3.2 / RIGHT*3.2
- **Distance labels**: SF Mono font, scale=0.3, positioned at edge midpoint via `point_from_proportion(0.5)`
- **Large graph demos**: 100-200 vertices, labels=False, radius=0.05 for vertex dots
- **Approximation ratio text**: Tex with formula, scale 0.8, positioned DOWN*2.5 or DOWN*3.5

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Vertex stroke | REDUCIBLE_PURPLE (#8c4dfb) | stroke_width=3 |
| Vertex fill | REDUCIBLE_PURPLE_DARK_FILL (#331B5D) | fill_opacity=1 |
| Edge default | REDUCIBLE_VIOLET (#d7b5fe) | stroke_width=3 |
| Selected tour edge | REDUCIBLE_YELLOW (#ffff5c) | After ShowPassingFlash |
| MST edge selected | REDUCIBLE_YELLOW | set_stroke(opacity=1) |
| Heuristic module | REDUCIBLE_PURPLE_DARKER (#3B0893) | Default Module |
| Optimal module | REDUCIBLE_GREEN_DARKER / LIGHTER | Green variant |
| Lower bound module | REDUCIBLE_YELLOW_DARKER / YELLOW | Yellow variant |
| Comparison bad | REDUCIBLE_CHARM (#FF5752) | SurroundingRectangle for issues |
| Ant dots | REDUCIBLE_YELLOW | radius=0.02, Dot |
| Distance labels | SF Mono font | scale=0.3, BLACK stroke background |
| Labels | CMU Serif, BOLD | Reducible brand font |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| LaggedStartMap tour edges (100 vertices) | run_time=14 | Dramatic build of full tour |
| LaggedStartMap MST edges | run_time=2-3 | GrowFromCenter per edge |
| ShowPassingFlash on edge | default ~1s | time_width=0.5 for quick flash |
| Side-by-side comparison shift | default | scale + shift animated together |
| Ant colony simulation iteration | varies | Multiple tours per iteration |
| Total video | ~20+ minutes | Full TSP tutorial with many scenes |

## Patterns

### Pattern: Custom Graph Class with Distance Matrix

**What**: TSPGraph extends Manim's Graph to add distance computation, tour edge generation, neighboring edge queries, and partial edge subset sampling (for very large graphs). Distance matrix auto-computed from vertex positions if not provided.

**When to use**: Any graph algorithm where you need edge weights derived from spatial positions, complete graph visualizations, or subset edge display. TSP, shortest path, MST, network flow.

```python
# Source: projects/Reducible/2022/TSPProblem/solving_tsp.py:24-169
class TSPGraph(Graph):
    def __init__(self, vertices, dist_matrix=None,
                 vertex_config={"stroke_color": REDUCIBLE_PURPLE, "stroke_width": 3,
                                "fill_color": REDUCIBLE_PURPLE_DARK_FILL, "fill_opacity": 1},
                 edge_config={"color": REDUCIBLE_VIOLET, "stroke_width": 3},
                 labels=True, label_scale=0.6, **kwargs):
        edges = []
        if labels:
            labels = {k: CustomLabel(str(k), scale=label_scale) for k in vertices}
            edge_config["buff"] = LabeledDot(list(labels.values())[0]).radius
        super().__init__(vertices, edges, vertex_config=vertex_config,
                         edge_config=edge_config, labels=labels, **kwargs)
        if dist_matrix is None:
            self.dist_matrix = np.zeros((len(vertices), len(vertices)))
            for u, v in itertools.combinations(vertices, 2):
                distance = np.linalg.norm(
                    self.vertices[u].get_center() - self.vertices[v].get_center())
                self.dist_matrix[u][v] = distance
                self.dist_matrix[v][u] = distance

    def get_tour_edges(self, tour, edge_type=Line):
        edges = get_edges_from_tour(tour)
        return {edge: self.create_edge(u, v, edge_type=edge_type) for edge in edges for u, v in [edge]}
```

### Pattern: ShowPassingFlash for Edge Selection

**What**: Highlights an edge selection by sending a bright flash along the edge path, then keeping the edge in the highlight color. Creates a clear visual signal that "this edge was chosen" vs just appearing.

**When to use**: Algorithm step visualization where an edge/path is selected from candidates, greedy algorithms picking edges, any sequential selection from a graph.

```python
# Source: projects/Reducible/2022/TSPProblem/solving_tsp.py:231-238
self.play(
    tour_edges[(prev, vertex)].animate.set_color(REDUCIBLE_YELLOW),
    ShowPassingFlash(
        tour_edges[(prev, vertex)].copy().set_stroke(width=6).set_color(REDUCIBLE_YELLOW),
    ),
)
```

### Pattern: Module Boxes for Conceptual Flow

**What**: Uses the Reducible Module class (RoundedRectangle + centered text) to build conceptual diagrams comparing abstract concepts. Different fill colors encode different roles (purple=heuristic, green=optimal, yellow=bound). Arranged with MathTex inequality symbols between them.

**When to use**: Explaining relationships between abstract concepts, approximation ratio diagrams, any comparison where you need labeled boxes with visual hierarchy via color.

```python
# Source: projects/Reducible/2022/TSPProblem/solving_tsp.py:524-573
heuristic_solution_mod = Module(["Heuristic", "Solution"], text_weight=BOLD)
optimal_solution_mod = Module(["Optimal", "Solution"],
    REDUCIBLE_GREEN_DARKER, REDUCIBLE_GREEN_LIGHTER, text_weight=BOLD)
lower_bound_mod = Module(["Lower", "Bound"],
    REDUCIBLE_YELLOW_DARKER, REDUCIBLE_YELLOW, text_weight=BOLD)
left_geq = MathTex(r"\geq").scale(2)
VGroup(heuristic_solution_mod, left_geq, optimal_solution_mod).arrange(RIGHT, buff=1)
```

### Pattern: Ant Colony Simulation with Pheromone Matrix

**What**: Models ant colony optimization by creating Ant objects that traverse the TSP graph using probability distributions weighted by inverse distance and pheromone levels. Pheromone matrix updates after each iteration with evaporation. Each ant is visualized as a small yellow Dot.

**When to use**: Swarm intelligence, metaheuristic optimization, any simulation where multiple agents make probabilistic decisions that collectively converge on a solution.

```python
# Source: projects/Reducible/2022/TSPProblem/solving_tsp.py:3361-3450
class Ant:
    def __init__(self, alpha, beta, tsp_graph, pheromone_matrix):
        self.alpha = alpha
        self.beta = beta
        self.cost_matrix = tsp_graph.get_dist_matrix()
        self.pheromone_matrix = pheromone_matrix
        self.mob = Dot(radius=0.02, color=REDUCIBLE_YELLOW)

    def get_tour(self):
        tour = [np.random.choice(list(range(self.num_nodes)))]
        while len(tour) < self.num_nodes:
            current = tour[-1]
            neighbors = get_unvisited_neighbors(current, tour, self.num_nodes)
            neighbor_distribution = self.calc_distribution(current, neighbors)
            next_to_vist = np.random.choice(neighbors, p=neighbor_distribution)
            tour.append(next_to_vist)
        return tour
```

## Scene Flow

1. **Nearest Neighbor** (0-3min): Introduce graph, glowing circle on start vertex, show neighboring edges, greedily pick shortest. Yellow flash on each chosen edge. Compare NN tour vs optimal side-by-side with distance labels.
2. **Lower Bounds** (3-7min): Module box diagram for Heuristic >= Optimal >= Lower Bound. Introduce MST via Prim's algorithm animation (visited/unvisited highlighting). Extend to 1-tree lower bound.
3. **Greedy Approach** (7-10min): Sort all edges by weight, add non-cycle-forming edges. Christofides algorithm visualization with minimum weight matching.
4. **Tour Improvement** (10-14min): 2-opt local search. Show edge swaps that improve tour cost. Demonstrate local minima problem.
5. **Ant Colony Optimization** (14-18min): Side-by-side comparison of cost-only vs reward-weighted ant decisions. Bar charts show probability distributions. Pheromone matrix visualized and updated across iterations.
6. **Simulated Annealing** (18-20min): Accept worse solutions with decreasing probability. Conclusion flow diagram with all approaches summarized.
