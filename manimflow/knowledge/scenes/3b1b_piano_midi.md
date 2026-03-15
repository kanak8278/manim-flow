---
source: https://github.com/3b1b/videos/blob/main/_2022/piano/midi_animations.py
project: 3blue1brown
domain: [music, signal_processing]
elements: [surface_3d, label]
animations: [move, color_change, add_updater]
layouts: [centered]
techniques: [three_d_camera, add_updater, data_driven]
purpose: [simulation, demonstration]
mobjects: [Piano3D, Rectangle, VGroup, Line]
manim_animations: []
scene_type: Scene
manim_version: manimlib
complexity: intermediate
lines: 155
scene_classes: [AnimatedMidi, AnimatedMidiTrapped5m, STFTAlgorithmOnTrapped, HelpLongOnlineConverter]
---

## Summary

Visualizes MIDI piano performance as a 3D scrolling animation with a Piano3D object and falling note rectangles. MIDI data is parsed from `.mid` files using the `mido` library, creating rectangles whose height encodes note duration and opacity encodes velocity. Keys physically depress and change color when hit, synchronized to audio playback.

## Design Decisions

- **3D camera at 70-degree phi angle**: Shows the piano keyboard in perspective while note rectangles scroll downward toward the keys, mimicking popular piano visualization software.
- **Rectangle height = note duration**: Longer notes produce taller rectangles, giving immediate visual feedback about sustained vs staccato playing.
- **Opacity maps to velocity (0.25 + velocity/100)**: Louder notes appear more opaque, softer notes more translucent. The 0.25 floor ensures even quiet notes remain visible.
- **Keys depress on hit (z-offset of 0.025)**: Subtle physical feedback that a key is being struck, reinforcing the connection between visual rectangles and sound.
- **Black masking rectangle over piano**: Hides rectangles that have already scrolled past the keys, maintaining visual clarity.
- **Data-driven from MIDI parsing**: No manual keyframing; the animation is entirely driven by MIDI event timing and velocity data.

## Composition

- **Screen regions**:
  - Piano3D: `set_width(9)`, moved to `5 * DOWN`
  - Camera frame: phi = 70 degrees
  - Note rectangles: spawned above keys, scroll downward
  - Black mask: `piano.get_width()` wide, height=5, positioned at piano top edge
- **Element sizing**: Note rectangles width = `0.5 * key.get_width()`, height computed from tick duration
- **Scroll speed**: `dist_per_sec = 4.0` units per second downward

## Color and Styling

| Element | Color | Details |
|---------|-------|---------|
| Note rectangles | BLUE | `note_color`, stroke_width=0, fill opacity varies by velocity |
| Hit key color | TEAL | `hit_color`, interpolated at 0.5 with original key color |
| Black mask | BLACK | fill_opacity=1, stroke_width=0 |

## Timing

| Animation | Duration | Notes |
|-----------|----------|-------|
| Total video | `note_rects.get_height() / dist_per_sec + 3.0` | Entire scroll + 3s buffer |
| Scroll rate | 4.0 units/sec | `dist_per_sec` parameter |
| Sound offset | 0.3s | `sound_file_time_offset` for audio sync |

## Patterns

### Pattern: MIDI-Driven Data Visualization with mido

**What**: Parses MIDI file events (note_on, note_off, set_tempo) to create positioned rectangles whose placement, height, and opacity directly encode musical data (pitch, duration, velocity).

**When to use**: Any data-driven visualization where external time-series data (audio, sensor readings, stock ticks) needs to be mapped to visual properties of Manim objects. Music visualizations, event timeline displays, or any scenario where object properties are derived from parsed file data.

```python
# Source: projects/videos/_2022/piano/midi_animations.py:42-93
def add_note_rects(self):
    mid = mido.MidiFile(mid_file, clip=True)
    track = mido.merge_tracks(mid.tracks)
    sec_per_tick = tempo * 1e-6 / mid.ticks_per_beat
    dist_per_tick = self.dist_per_sec * sec_per_tick

    note_rects = VGroup()
    for msg in track:
        time_in_ticks += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            pending_notes[msg.note] = (time_in_ticks, msg.velocity)
        elif msg.type == 'note_off':
            start_time, velocity = pending_notes.pop(msg.note)
            key = self.piano[msg.note - offset]
            rect = Rectangle(
                width=self.note_to_key_width_ratio * key.get_width(),
                height=(time_in_ticks - start_time) * dist_per_tick
            )
            rect.next_to(key, UP, buff=start_time * dist_per_tick)
            rect.set_fill(self.note_color, opacity=clip(0.25 + velocity / 100, 0, 1))
            note_rects.add(rect)
```

### Pattern: Piano Key Depression Updater

**What**: An updater that checks each piano key against active time spans, physically depressing the key (z-offset) and changing its fill color when a note is active, then restoring it afterward.

**When to use**: Interactive instrument visualizations, button-press feedback animations, or any scenario where objects need to change state based on time-window lookups during continuous playback.

```python
# Source: projects/videos/_2022/piano/midi_animations.py:116-132
def update_piano(piano, dt):
    piano.time += dt
    for note, key in zip(piano_midi_range, piano):
        hit = any(
            start - 1/60 < piano.time < end + 1/60
            for start, end in notes_to_time_spans[note]
        )
        if hit:
            key.set_z(key.original_z - self.hit_depth)
            key.set_fill(interpolate_color(
                key[0].get_fill_color(), self.hit_color, 0.5
            ))
        else:
            key.set_z(key.original_z)
            key.set_fill(key.original_color)
piano.add_updater(update_piano)
```

### Pattern: Continuous Scroll with Time-Based Updater

**What**: Scrolls a group of mobjects at a constant rate using `self.time` within a lambda updater, while a black masking rectangle hides objects that have passed the viewing area.

**When to use**: Scrolling timelines, ticker-tape animations, any visualization requiring continuous linear motion synchronized with audio or real-time data.

```python
# Source: projects/videos/_2022/piano/midi_animations.py:133-143
note_rects_start = note_rects.get_center().copy()
note_rects.add_updater(lambda m: m.move_to(
    note_rects_start + self.dist_per_sec * self.time * DOWN
))
black_rect = Rectangle(width=piano.get_width(), height=5)
black_rect.set_fill(BLACK, 1)
black_rect.set_stroke(width=0)
black_rect.move_to(piano, UP)
self.add(note_rects, black_rect, piano)  # Layer order matters
```

## Scene Flow

1. **Setup** (0-1s): Piano3D placed at bottom, camera angled at 70 degrees.
2. **MIDI parsing** (instant): Note rectangles generated from MIDI data, positioned above corresponding keys.
3. **Audio sync** (0.3s offset): Piano sound file added with time offset for synchronization.
4. **Scrolling playback** (variable): Note rectangles scroll downward at 4 units/sec. Keys depress and change to TEAL when hit. Black mask hides passed rectangles.
5. **End** (+3s): Buffer wait after last note scrolls past.
