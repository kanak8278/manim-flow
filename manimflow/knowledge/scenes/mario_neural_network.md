---
source: https://github.com/vivek3141/videos/blob/main/mario.py
project: vivek3141_videos
domain: [computer_science, machine_learning, neural_networks, reinforcement_learning]
elements: [network, neuron, layer, weight_connection, axes, function_plot, dot, label, equation, circle_node, arrow]
animations: [write, transform, fade_in]
layouts: [centered, side_by_side, horizontal_row, grid]
techniques: [custom_mobject, progressive_disclosure, data_driven]
purpose: [demonstration, step_by_step, overview]
mobjects: [VGroup, Circle, Line, Axes, FunctionGraph, TexMobject, TextMobject, Dot, Arrow, Brace, Rectangle, ScreenRectangle]
manim_animations: [Write, Transform, TransformFromCopy, FadeInFromDown, ShowCreation, Uncreate, ApplyMethod]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 486
scene_classes: [NeuralNetworkMobject, LinReg, LogReg, LayerToLayer, NeuralNetwork, NeuroEvolution, PartOneTitle, PartTwoTitle, PartThreeTitle]
---

## Summary

Visualizes the NEAT (NeuroEvolution of Augmenting Topologies) algorithm for training neural networks to play Mario. Features a reusable NeuralNetworkMobject that renders layered circle-and-line diagrams with configurable layer sizes, neuron radii, and edge connections. The video progresses from linear regression (scatter plot + fitted line) through logistic regression (sigmoid function) to full neural networks, ending with neuroevolution (6 networks in a grid, scored, selected, and evolved). Uses scipy.optimize.curve_fit for real data fitting.

## Design Decisions

- **NeuralNetworkMobject with full API**: Supports add_neurons(), add_edges(), add_input_labels(), add_y(), add_weight_labels(). Neurons are Circles arranged vertically per layer, layers arranged horizontally. Edges connect all neurons between adjacent layers. Large layers get Brace with count label.
- **Progression from simple to complex**: LinReg -> LogReg -> NeuralNetwork -> NeuroEvolution. Each scene builds on the previous concept, adding complexity incrementally.
- **Real data fitting**: LinReg uses scipy curve_fit on generated noisy data, showing actual fitted parameters in the equation label. This grounds the visualization in real computation.
- **6-network grid for evolution**: Six NeuralNetworkMobjects arranged in a 3x2 grid with score labels. Green circles highlight the two fittest. The grid shows the population concept visually.
- **Logistic regression with sigmoid**: Transition from scatter plot to decision boundary to sigmoid function. The equation builds in parts: first the linear part, then the sigma() wrapper.

## Composition

- **NeuralNetworkMobject**: layer_to_layer_buff=LARGE_BUFF, neuron_to_neuron_buff=MED_SMALL_BUFF, neuron_radius=0.15, edge_stroke_width=2
- **LinReg scatter**: Axes x=[0,6], y=[0,5], 15 dots at noisy linear data, red fitted line, shifted 0.5*UP
- **LogReg scatter**: Axes x=[0,6], y=[0,6], 100 random points colored by class (#99EDCC vs #B85C8C), decision boundary y=x
- **Sigmoid curve**: Axes x=[-3,3], y=[0,2], scaled 2x, centered, shifted DOWN
- **Evolution grid**: 6 networks at shifts [m*UP+n*LEFT, ...] where m=1, n=3; scores next to each
- **Neural network display**: NeuralNetworkMobject([3, 4, 3], 0.15), scaled 2.5x

## Color and Styling

| Element | Color | Details |
| ------- | ----- | ------- |
| Background | BLACK | Default |
| Neurons stroke | BLUE | Circle stroke_width=3 |
| Neurons fill | GREEN | fill_opacity=0 (empty) |
| Edges | LIGHT_GREY | Line stroke_width=2 |
| Data points (LinReg) | BLUE | Dot radius=0.75*DEFAULT |
| Fitted line | RED | FunctionGraph |
| Class 1 points | #99EDCC | Dot |
| Class 2 points | #B85C8C | Dot |
| Decision boundary | WHITE | FunctionGraph y=x |
| Sigmoid curve | GOLD | FunctionGraph 2/(1+e^{-2x}) |
| Sigma function | YELLOW | tex_to_color_map |
| Input x | GREEN | tex_to_color_map |
| Output y | GOLD | tex_to_color_map |
| Weight labels | RED | b_n labels |
| Selection circles | GREEN | Circle(color=GREEN) |
| Neuroevolution title | RED | TextMobject |
| Part titles | RED/PURPLE/BLUE | Vary by part |

## Timing

| Animation | Duration | Notes |
| --------- | -------- | ----- |
| Write(nn) | ~1s | Neural network appears |
| Write(points) | ~1s | Scatter plot |
| Transform equations | ~1s each | Standard |
| Evolution grid write | ~1s | All 6 networks |
| Score labels | ~0.5s | Write |
| Selection circles | ~0.5s | Write |
| Total | ~3 minutes | 9 scenes |

## Patterns

### Pattern: NeuralNetworkMobject with Labels and Weights

**What**: A VGroup-based neural network diagram. Constructor takes a list of layer sizes (e.g., [3, 4, 3]). Neurons are Circles arranged vertically per layer with configurable buff. Layers are arranged horizontally. Edges are Lines connecting all neurons between adjacent layers. Supports input labels (x_1, x_2...), output labels (y_hat), and weight labels (b_1, b_2...) positioned on edges. Large layers (>16 neurons) get a vertical ellipsis and a Brace with count.

**When to use**: Any neural network visualization -- feedforward networks, classification models, regression models, network architecture diagrams. Also adaptable for any layered graph structure.

```python
# Source: projects/vivek3141_videos/mario.py:16-115
class NeuralNetworkMobject(VGroup):
    CONFIG = {
        "neuron_radius": 0.15,
        "neuron_to_neuron_buff": MED_SMALL_BUFF,
        "layer_to_layer_buff": LARGE_BUFF,
        "neuron_stroke_color": BLUE,
        "neuron_stroke_width": 3,
        "neuron_fill_color": GREEN,
        "edge_color": LIGHT_GREY,
        "edge_stroke_width": 2,
        "max_shown_neurons": 16,
    }

    def __init__(self, neural_network, size=0.15):
        VGroup.__init__(self)
        self.layer_sizes = neural_network
        self.neuron_radius = size
        self.add_neurons()
        self.add_edges()

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = Line(n1.get_center(), n2.get_center(),
                           buff=self.neuron_radius,
                           stroke_color=self.edge_color,
                           stroke_width=self.edge_stroke_width)
                edge_group.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)
```

### Pattern: Neuroevolution Grid with Selection

**What**: Six neural networks arranged in a 3x2 grid, each with a score label. Green circles highlight the two fittest individuals. After selection, the population transforms into a new generation with new scores. The "survival of the fittest" concept is shown by removing low-scoring networks and duplicating high-scoring ones.

**When to use**: Evolutionary algorithms, genetic algorithms, population-based optimization, any scenario showing selection from a group based on fitness/score. Also applicable to tournament selection in ML.

```python
# Source: projects/vivek3141_videos/mario.py:337-446
shift = [m * UP + n * LEFT, m * UP, m * UP + n * RIGHT,
         m * DOWN + n * LEFT, m * DOWN, m * DOWN + n * RIGHT]
scores = ["312", "434", "145", "254", "332", "521"]

net_group, text_group = VGroup(), VGroup()
for i in range(6):
    net = NeuralNetworkMobject([2, 3, 2])
    net.shift(shift[i])
    net_group.add(net)
    text = TextMobject(scores[i]).shift(shift[i]).scale(1.5)
    text_group.add(text)

self.play(Write(net_group))
self.play(Write(text_group))

# Highlight best two
circle1 = Circle(color=GREEN).shift(shift[5])  # score 521
circle2 = Circle(color=GREEN).shift(shift[1])  # score 434
self.play(Write(circle1), Write(circle2))

# Evolve to next generation
self.play(Transform(circle1, net_group),
          Uncreate(circle2), Uncreate(text_group))
```

### Pattern: Real Data Scatter + Fitted Line with scipy

**What**: Generate noisy data from a known function, fit with scipy.optimize.curve_fit, display scatter plot with fitted line. The equation label includes the actual fitted parameters (rounded). Data points are Dots, fitted line is a FunctionGraph. Axes have labeled dimensions.

**When to use**: Linear regression, curve fitting, any data visualization where you want to show actual computed fit parameters, statistics demonstrations, model evaluation.

```python
# Source: projects/vivek3141_videos/mario.py:146-209
from scipy.optimize import curve_fit

xdata = np.linspace(0.25, 5.75, 15)
ydata = [self.func(i) + 2 * (np.random.random() - 0.5) for i in xdata]

def f(x, a, b): return a * x + b
theta, _ = curve_fit(f, xdata, ydata)

points = VGroup(*[Dot([xdata[i], ydata[i], 0], color=BLUE,
                      radius=0.75 * DEFAULT_DOT_RADIUS)
                  for i in range(15)])
line = FunctionGraph(lambda x: f(x, *theta), x_min=0, x_max=6, color=RED)

lbl = TexMobject(
    f"\\hat{{\\text{{price}}}} = {round(theta[0], 2)} + "
    f"{round(theta[1], 2)} \\ \\text{{size}}", color=RED)
```

## Scene Flow

1. **PartOneTitle** (0-5s): "Part 1: Building on From Linear Regression"
2. **LinReg** (5-20s): Scatter plot of house prices vs plot size. Red fitted line. Equation with fitted parameters. Dashed prediction lines.
3. **LogReg** (20-40s): 2-class scatter plot. Decision boundary y=x. Transition to sigmoid equation. Sigmoid curve plotted.
4. **LayerToLayer** (40-50s): 5-input, 1-output network with input labels x_1..x_5 and weight labels b_1..b_5. Full equation below.
5. **NeuralNetwork** (50-55s): [3,4,3] network at 2.5x scale. Arrow pointing to neurons. "Each of these circles is a model."
6. **PartTwoTitle** (55-60s): "Part 2: Still too simple :("
7. **PartThreeTitle** (60-65s): "Part 3: Applications of NEAT"
8. **NeuroEvolution** (65-85s): "1994" -> "Neuroevolution" title. "Survival of the fittest." 6 networks in grid with scores. Green circles select best two. New generation with new scores. "This process is repeated."

> Full file: `projects/vivek3141_videos/mario.py` (486 lines)
