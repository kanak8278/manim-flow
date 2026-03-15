---
source: https://github.com/3b1b/videos/blob/main/custom/characters/pi_creature.py
project: videos
domain: [mathematics, geometry]
elements: [pi_creature, speech_bubble, character]
animations: [transform, fade_in, fade_out, write, draw]
layouts: [centered, edge_anchored]
techniques: [custom_mobject, custom_animation, teacher_students_scene]
purpose: [demonstration, step_by_step, exploration]
mobjects: [PiCreature, SVGMobject, VGroup, VMobject, Circle, SpeechBubble, ThoughtBubble, Eyes]
manim_animations: [AnimationGroup, FadeTransform, ReplacementTransform, ApplyMethod, Blink, DrawBorderThenFill, Write, FadeOut, MoveToTarget, LaggedStart]
scene_type: InteractiveScene
manim_version: manimlib
complexity: advanced
lines: 904
scene_classes: [PiCreatureScene, TeacherStudentsScene]
---

## Summary

The Pi Creature system is 3Blue1Brown's signature character framework: an SVG-based animated character with expressive eyes, mode-based emotional states (plain, happy, thinking, speaking, confused, shruggie, etc.), gaze tracking, speech/thought bubbles, and blinking. The system spans three files: `pi_creature.py` (the mobject), `pi_creature_animations.py` (Blink, bubble intro/removal), and `pi_creature_scene.py` (PiCreatureScene base class with auto-gaze and TeacherStudentsScene). The architecture uses SVG mode files loaded from a configurable directory, with programmatic eye construction replacing the original SVG eyes for smoother interpolation.

## Design Decisions

- **SVG-based with mode files**: Each emotional state is a separate SVG file (plain.svg, happy.svg, thinking.svg, etc.) loaded from a `pi_creature_images` directory. This allows artists to design expressions in Figma while code handles animation transitions.
- **Programmatic eyes replace SVG eyes**: Original SVG eye paths were inconsistent across modes, so eyes are reconstructed as Circles (iris + pupil with white dot highlight). This ensures smooth interpolation when transforming between modes.
- **Three-submobject structure (eyes, body, mouth)**: After init_structure(), the Pi Creature is exactly [eyes, body, mouth]. This simplifies color changes (only body gets filled) and eye manipulation.
- **insert_n_curves(100) on body**: Smooths interpolation between mode transforms by ensuring enough control points for bezier matching.
- **Gaze direction via pupil positioning**: look() maps a 2D direction vector onto each iris's local coordinate system, constraining pupil position within the iris boundary. Both pupils are vertically aligned to prevent uncanny cross-eyed appearance.
- **PiCreatureScene auto-gaze**: The scene's anims_from_play_args override automatically makes on-screen pi creatures look at whatever is being animated, creating natural "teaching" behavior without explicit look_at calls.
- **Bubble pinning with auto-flip**: Bubbles pin to the creature and auto-flip based on screen position, preventing off-screen overflow.

## Composition

- **Pi Creature sizing**: Default height=3 units. Randolph (BLUE_E) and Mortimer (GREY_BROWN, flipped) are the two main characters.
- **BabyPiCreature**: height=1.5, eyes scaled 1.2x, pupils scaled 1.3x for cute proportions.
- **PiCreatureScene default**: Primary creature placed at DL corner.
- **TeacherStudentsScene**: Teacher on right side (flipped), 3 students on left, arranged at bottom of screen.
- **Arm ranges**: Right arm at body proportion 0.55-0.7, left arm at 0.34-0.462 (used for get_arm_copies).
- **Eye proportions**: pupil_to_eye_width_ratio=0.4, pupil_dot_to_pupil_width_ratio=0.3.

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Randolph (default) | BLUE_E | Default PiCreature color |
| Mortimer | GREY_BROWN | flip_at_start=True |
| Mathematician | GREY | Academic variant |
| Body | fill_opacity=1.0 | stroke_width=0, stroke_color=BLACK |
| Pupil (black part) | BLACK | Circle, fill_opacity=1, stroke_width=0 |
| Pupil (highlight dot) | WHITE | Small circle at 3/8 position on pupil |
| Eyes (iris) | Inherited from SVG | Per-mode design |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Blink | Default run_time | squish_rate_func(there_and_back) |
| BubbleIntroduction | Default | Simultaneous: mode change + bubble draw + content write |
| RemovePiCreatureBubble | Default | MoveToTarget + FadeOut(bubble) |
| PiCreatureScene auto-blink | Every 3s | seconds_to_blink=3, random creature chosen |
| Mode change (transform) | Default | Uses .animate.change_mode() for smooth interpolation |

## Patterns

### Pattern: SVG-Based Character with Mode System

**What**: A character mobject loaded from SVG files, where each emotional expression is a separate SVG. Mode changes create smooth transforms between expressions by reconstructing the character from a new SVG and using become().

**When to use**: Any scenario needing an expressive animated character - educational narrators, tutorial guides, characters that react to on-screen math. The mode system lets the character show confusion when something is wrong, happiness when a proof completes, thinking when pondering.

```python
# Source: projects/videos/custom/characters/pi_creature.py:147-158
def change_mode(self, mode):
    new_self = self.__class__(mode=mode)
    new_self.match_style(self)
    new_self.match_height(self)
    if self.is_flipped() != new_self.is_flipped():
        new_self.flip()
    new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
    if hasattr(self, "purposeful_looking_direction"):
        new_self.look(self.purposeful_looking_direction)
    self.become(new_self)
    self.mode = mode
    return self
```

### Pattern: Programmatic Eye Gaze Tracking

**What**: Maps a 2D direction vector onto each iris's local coordinate system to position pupils, creating natural gaze that follows any point or mobject. Constrains pupils to stay within iris bounds and aligns both pupils vertically.

**When to use**: Any character or avatar that needs to "look at" objects on screen - following a moving equation, watching a graph being drawn, making eye contact with another character. Critical for the "teaching" feel of 3B1B videos.

```python
# Source: projects/videos/custom/characters/pi_creature.py:163-177
def look(self, direction):
    direction = normalize(direction)
    self.purposeful_looking_direction = direction
    for eye in self.eyes:
        iris, pupil = eye
        iris_center = iris.get_center()
        right = iris.get_right() - iris_center
        up = iris.get_top() - iris_center
        vect = direction[0] * right + direction[1] * up
        v_norm = get_norm(vect)
        pupil_radius = 0.5 * pupil.get_width()
        vect *= (v_norm - 0.75 * pupil_radius) / v_norm
        pupil.move_to(iris_center + vect)
    self.eyes[1].pupil.align_to(self.eyes[0].pupil, DOWN)
    return self
```

### Pattern: Speech/Thought Bubble with Character Mode Binding

**What**: Creates a bubble (speech or thought) pinned to the character, simultaneously changing the character's expression to match (speaking mode for speech, thinking mode for thought). The bubble auto-flips based on character position. Supports chained bubble replacement and removal.

**When to use**: Narrator commentary, internal monologue, posing questions to the viewer, showing character reactions to mathematical results. The bubble system is the primary way 3B1B characters "speak" in videos.

```python
# Source: projects/videos/custom/characters/pi_creature.py:253-271
def says(self, content, mode="speaking", look_at=None, **kwargs) -> Animation:
    from custom.characters.pi_creature_animations import PiCreatureBubbleIntroduction
    return PiCreatureBubbleIntroduction(
        self, content,
        target_mode=mode,
        look_at=look_at,
        bubble_type=SpeechBubble,
        **kwargs,
    )

def thinks(self, content, mode="thinking", look_at=None, **kwargs) -> Animation:
    from custom.characters.pi_creature_animations import PiCreatureBubbleIntroduction
    return PiCreatureBubbleIntroduction(
        self, content,
        target_mode=mode,
        look_at=look_at,
        bubble_type=ThoughtBubble,
        **kwargs,
    )
```

### Pattern: Auto-Gaze Scene (PiCreatureScene)

**What**: A scene base class that overrides anims_from_play_args to automatically make all on-screen pi creatures look at whatever mobject is being animated. Creates the natural "teacher watching the board" effect without explicit look_at calls on every animation.

**When to use**: Any scene with a persistent character who should appear to be paying attention to the math being presented. Eliminates boilerplate look_at calls and makes the character feel alive. The TeacherStudentsScene variant adds a teacher + 3 students for classroom-style explanations.

```python
# Source: projects/videos/custom/characters/pi_creature_scene.py:156-185
def anims_from_play_args(self, *args, **kwargs):
    animations = super().anims_from_play_args(*args, **kwargs)
    anim_mobjects = Group(*[a.mobject for a in animations])
    all_movers = anim_mobjects.get_family()
    if not self.any_pi_creatures_on_screen():
        return animations
    pi_creatures = self.get_on_screen_pi_creatures()
    non_pi_creature_anims = [
        anim for anim in animations
        if len(set(anim.mobject.get_family()).intersection(pi_creatures)) == 0
    ]
    if len(non_pi_creature_anims) == 0:
        return animations
    first_anim = non_pi_creature_anims[0]
    if hasattr(first_anim, "target_mobject") and first_anim.target_mobject is not None:
        main_mobject = first_anim.target_mobject
    else:
        main_mobject = first_anim.mobject
    for pi_creature in pi_creatures:
        if pi_creature not in all_movers:
            animations.append(ApplyMethod(pi_creature.look_at, main_mobject))
    return animations
```

### Pattern: Standalone Eyes Mobject

**What**: An Eyes class that can be attached to any VMobject body, not just PiCreature. Creates pi-creature-style eyes positioned at the top of any shape, with mode changes and gaze tracking.

**When to use**: Adding personality to non-character mobjects - giving "eyes" to a function graph, a matrix, a neural network node. Useful for comedic or pedagogical effect when you want an object to appear sentient.

```python
# Source: projects/videos/custom/characters/pi_creature.py:368-398
class Eyes(VGroup):
    def __init__(self, body: VMobject, height: float = 0.3, mode: str = "plain", **kwargs):
        super().__init__(**kwargs)
        self.create_eyes(mode, height, body.get_top())

    def create_eyes(self, mode, height, bottom, look_at=None):
        self.mode = mode
        pi = PiCreature(mode=mode)
        pi.eyes.set_height(height)
        pi.eyes.move_to(bottom, DOWN)
        if look_at is not None:
            pi.look_at(look_at)
        self.set_submobjects(list(pi.eyes))

    def change_mode(self, mode, look_at=None):
        self.create_eyes(mode, self.get_height(), self.get_bottom(), look_at)
        return self
```

## Scene Flow

1. **Character creation** (0s): PiCreature loads SVG for initial mode, reconstructs eyes as circles, sets color on body, inserts curves for smooth interpolation.
2. **Scene setup**: PiCreatureScene places creature(s) at start corners, begins auto-blink timer.
3. **Teaching interaction**: As animations play, pi creatures automatically look at animated mobjects. Teacher changes mode to match emotional context (happy, confused, pondering).
4. **Bubble dialogue**: Character says/thinks content with simultaneous mode change + bubble creation. Bubbles pin to character and auto-flip.
5. **Bubble transitions**: replace_bubble() transforms between bubble contents. debubble() removes bubble and returns to plain mode.

## Character Variants

| Class | Color | Notes |
|-------|-------|-------|
| PiCreature / Randolph | BLUE_E | Default protagonist |
| Mortimer | GREY_BROWN | Flipped, often plays foil/questioner |
| Mathematician | GREY | Academic variant |
| BabyPiCreature | Any | height=1.5, enlarged eyes/pupils |
| TauCreature | Any | Uses TauCreatures SVG set, no init_structure override |

## manimlib Notes

- Uses `SVGMobject` (not community `SVGMobject` which has different internals)
- `_AnimationBuilder` for `.animate` syntax
- `get_directories()["pi_creature_images"]` for SVG path resolution
- `insert_n_curves()` for smooth mode-to-mode transforms
- `align_data_and_family` override ensures mode state transfers during Transform
