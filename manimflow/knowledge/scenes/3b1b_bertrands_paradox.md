---
source: https://github.com/3b1b/videos/blob/main/_2021/bertrands_paradox.py
project: 3blue1brown
domain: [probability, geometry, mathematics]
elements: [dot, line, number_line, label, equation, formula, surrounding_rect]
animations: [write, fade_in, fade_out, draw, stagger, lagged_start, update_value, animate_parameter, move]
layouts: [centered, side_by_side, edge_anchored]
techniques: [value_tracker, always_redraw, data_driven, helper_function, custom_animation]
purpose: [demonstration, exploration, comparison, simulation, distribution]
mobjects: [Circle, Polygon, Line, VGroup, DotCloud, TrueDot, OldTex, OldTexText, Text, Integer, DecimalNumber, Dot, Elbow, UnitInterval, Square]
manim_animations: [ShowCreation, Write, FadeIn, FadeOut, ShowIncreasingSubsets, ShowSubmobjectsOneByOne, TransformFromCopy, GrowFromCenter, MoveToTarget, UpdateFromAlphaFunc]
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 1095
scene_classes: [RandomChordScene, PairOfPoints, CenterPoint, RadialPoint, CompareFirstTwoMethods, SparseWords, PortionOfRadialLineInTriangle, RandomPointsFromVariousSpaces, CoinFlips, ChordsInSpaceWithCircle, TransitiveSymmetries, NonTransitive, RandomSpherePoint, CorrectionInsert]
---

## Summary

Visualizes Bertrand's paradox -- three different methods of choosing a "random chord" on a circle yield three different probabilities for the chord being longer than a side of the inscribed equilateral triangle. Method 1 (random pair of points on circumference) gives 1/3, Method 2 (random center point in disc) gives 1/2, and Method 3 (random point on radial line) gives 1/2. Uses real-time chord generation with GlowDot indicators, running fraction counters, color-coded long (BLUE) vs short (WHITE) chords, and side-by-side comparison.

## Design Decisions

- **Color-coded chord length**: Long chords (longer than inscribed triangle side) in BLUE, short in WHITE. Immediate visual density reveals the different proportions from each method.
- **Running fraction counter**: Live numerator/denominator with ratio, updating per chord, so the viewer sees convergence to the probability.
- **DotCloud for sampling indicators**: GlowDots (glow_factor=2, radius=0.25) appear and disappear at each sample point, giving fleeting visual feedback of where each chord was generated.
- **Inscribed equilateral triangle**: Drawn in RED as the reference threshold, rotated -PI/6 for canonical positioning.
- **Side-by-side comparison**: Two circles with different generation methods run simultaneously, making the paradox viscerally apparent.
- **Radial line with sweeping chord**: A chord attached to a TrueDot on the radial line moves as the dot is animated, showing how chords transition from long to short at the halfway point.
- **General probability spaces**: Extends to number line, circle, and disc to discuss what "uniform" means in each context.

## Composition

- **RandomChordScene circle**: radius=3.5, to_edge(LEFT)
- **Title**: `set_x(FRAME_WIDTH / 4).to_edge(UP)` (right half)
- **Fraction counter**: matches x with title, matches y with circle
- **CompareFirstTwoMethods**: Two circles in `get_grid(1, 2, buff=1)`, height=5, to_edge(DOWN, buff=LARGE_BUFF)
- **Radial line**: From circle center to circle.pfp(1/6), stroke_width=2
- **Half line marking**: RED, with "1/2" label, font_size=30
- **Triangle**: Polygon from circle points at 0, 1/3, 2/3, stroke=RED/2

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Circle | GREY_B | stroke_width=3 |
| Long chords | BLUE | `long_color`, width=0.5, opacity=0.35 |
| Short chords | WHITE | `short_color`, width=0.5, opacity=0.35 |
| Flash chords | varies | width=3, opacity=1 (momentary) |
| Inscribed triangle | RED | stroke_width=2 |
| Sample GlowDots | YELLOW | glow_factor=2, radius=0.25 |
| Radial line | WHITE | stroke_width=2 |
| Half-line | RED | stroke_width=2 |
| Half label | RED | font_size=30 |
| Elbow marker | WHITE | Right angle indicator on radial line |
| Interactive chord | BLUE | stroke_width=4 |
| TrueDot (interactive) | YELLOW | glow_factor=5, radius=0.5 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Initial 16 chords | 8s | First batch |
| Remaining chords | 20s | `self.run_time`, rate_func=linear |
| Comparison (2 methods) | 15s | Simultaneous ShowIncreasingSubsets |
| Chord sweep on radial | 4s per position | 3 target positions |
| Total video | ~5 min | Moderate length |

## Patterns

### Pattern: Probabilistic Sampling with Live Counter

**What**: Generates random geometric objects (chords), classifies each as long/short, and maintains a live-updating fraction showing the running ratio. Uses `UpdateFromAlphaFunc` on the fraction, `ShowIncreasingSubsets` on the chord group, and `ShowSubmobjectsOneByOne` on flash copies for momentary highlights.

**When to use**: Monte Carlo simulations, convergence demonstrations, any probabilistic experiment where you want to show the law of large numbers in action.

```python
# Source: projects/videos/_2021/bertrands_paradox.py:34-54
for s, rt in (slice(0, 16), 8), (slice(18, None), self.run_time):
    fraction = self.get_fraction([c.long for c in chords[s]])
    self.play(
        ShowIncreasingSubsets(chords[s]),
        ShowSubmobjectsOneByOne(flash_chords[s]),
        ShowSubmobjectsOneByOne(indicators[s]),
        Animation(triangle),
        fraction.alpha_update,
        rate_func=linear,
        run_time=rt,
    )
```

### Pattern: Chord Length Classification with Threshold

**What**: Generates chords by a specific random method, then classifies each by comparing its length to the inscribed equilateral triangle's side length (`sqrt(3) * radius`). Sets color based on classification.

**When to use**: Any threshold-based classification visualization, hypothesis testing, binary outcome visualization, comparing quantities to a reference value.

```python
# Source: projects/videos/_2021/bertrands_paradox.py:97-113
def get_chords(self, circle, chord_generator=None):
    tri_len = np.sqrt(3) * circle.get_width() / 2
    chords = VGroup(*(chord_generator(circle) for x in range(self.n_samples)))
    for chord in chords:
        chord.long = (chord.get_length() > tri_len)
        chord.set_color(self.long_color if chord.long else self.short_color)
    chords.set_stroke(width=self.chord_width, opacity=self.chord_opacity)
    return chords
```

### Pattern: always_redraw Chord from Draggable Point

**What**: A chord is reconstructed every frame based on a TrueDot's position, using `always_redraw` with a function that computes the perpendicular chord through that point. Moving the dot along the radial line shows how chord length varies.

**When to use**: Interactive geometry, showing how a measurement changes with a parameter, real-time geometric construction, dynamic constraint visualization.

```python
# Source: projects/videos/_2021/bertrands_paradox.py:320-338
dot = TrueDot()
dot.set_glow_factor(5)
dot.set_radius(0.5)
dot.set_color(YELLOW)
dot.move_to(radial_line.pfp(0.1))

def get_chord():
    p = dot.get_center().copy()
    p /= (circle.get_width() / 2)
    chord = CenterPoint.chord_from_xy(p[0], p[1], circle)
    chord.set_stroke(BLUE, 4)
    return chord

chord = always_redraw(get_chord)
```

## Scene Flow

1. **PairOfPoints** (0-30s): Circle with title "Random pair of circle points". 1000 chords generated by picking 2 random points on circumference. GlowDots flash at endpoints. Running fraction converges to ~1/3.
2. **CenterPoint** (30-60s): "Random point in circle". Chords generated by picking random midpoints. Running fraction converges to ~1/2.
3. **CompareFirstTwoMethods** (60-90s): Side-by-side comparison with both methods running simultaneously, making the different densities visually apparent.
4. **PortionOfRadialLineInTriangle** (90-150s): Radial line drawn with perpendicular elbow. Red half-line marked. Interactive chord sweeps along radial line showing transition from long to short at the midpoint.
5. **RandomPointsFromVariousSpaces** (150-240s): Generalizes to "what does random mean?" -- points on interval, circle, disc, sphere. Discusses uniform distributions and symmetry.
6. **ChordsInSpaceWithCircle** (240-300s): Extends to 3D, random chords from random great circle slices.
7. **TransitiveSymmetries** (300-360s): Symmetry argument for why different answers arise from different symmetry groups.
