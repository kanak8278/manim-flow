# ManimFlow Architecture

ManimFlow is an AI animation production pipeline that turns a text topic into a complete educational video with voiceover, music, and thumbnails. It uses Manim (3Blue1Brown's animation engine) for rendering and Claude for creative and technical generation.

```
"How does bubble sort work?"  ──►  60-second animated explainer with voiceover
```

## Pipeline Overview

```
Topic (text)
    │
    ▼
┌──────────────────────────────┐
│  1. WRITERS ROOM             │  5 LLM calls, 0 tools
│     explore → evaluate →     │  Generates the STORY
│     draft → review → revise  │
└──────────────┬───────────────┘
               │  story.json
               ▼
┌──────────────────────────────┐
│  2. DESIGN SYSTEM            │  1-2 LLM calls, 0 tools
│     colors, typography,      │  Visual specification
│     camera, persistent elems │
└──────────────┬───────────────┘
               │  design_system.json
               ▼
┌──────────────────────────────┐
│  3. SCREENPLAY               │  1 LLM call + knowledge search
│     shot-by-shot spec with   │  Exact Manim objects per shot
│     elements, animations     │
└──────────────┬───────────────┘
               │  screenplay.json
               ▼
┌──────────────────────────────┐
│  4. CODE GENERATION          │  1 LLM call + knowledge search
│     Manim Python code with   │  VoiceoverScene + bookmark sync
│     voiceover sync           │
└──────────────┬───────────────┘
               │  scene.py
               ▼
┌──────────────────────────────┐
│  5. SANITIZE + ANALYZE       │  0 LLM calls (deterministic)
│     Fix rate_funcs, ASCII,   │  Catch issues before render
│     overlap, off-screen      │
└──────────────┬───────────────┘
               │  scene.py (fixed)
               ▼
┌──────────────────────────────┐
│  6. RENDER LOOP              │  0-5 LLM fix calls
│     manim → video            │  Auto-fix on failure
│     retry up to 5 times      │
└──────────────┬───────────────┘
               │  GeneratedScene.mp4
               ▼
┌──────────────────────────────┐
│  7. QUALITY EVAL LOOP        │  2 LLM calls per round
│     vision (frames) + code   │  Surgical fix if < 7/10
│     analysis scoring         │
└──────────────┬───────────────┘
               │  scene.py (improved)
               ▼
┌──────────────────────────────┐
│  8. AUDIO + THUMBNAIL        │  0 LLM calls (ffmpeg)
│     background music mixing  │
│     best-frame extraction    │
└──────────────┬───────────────┘
               │
               ▼
         {title}_FINAL.mp4
         thumbnail.png
```

Typical run: **~10-12 LLM calls**, 1-2 knowledge base searches, 1 Manim render.

---

## Stage 1: Writers Room

**File:** `manimflow/writers_room.py`
**Purpose:** Find the best story angle and write a complete, Manim-aware narrative.
**LLM calls:** 5 (explore, evaluate, draft, review, revise)

The writers room is the most critical stage. It produces the **source of truth** that everything downstream implements. Every visual description is written in terms of what Manim can actually render — no cinema, no 3D, no photography.

### 1a. Explore Angles

```
Input:  topic ("How does bubble sort work?"), audience
Output: 3-4 StoryAngle objects
```

The LLM brainstorms 3-4 completely different creative approaches. Each angle has:
- **hook**: First 5 seconds that grab attention
- **approach**: How the explanation unfolds
- **visual_metaphor**: The central animation idea (must be Manim-implementable)
- **emotional_arc**: What the viewer feels throughout
- **aha_moment**: When everything clicks
- **manim_elements**: What Manim types are needed (card, arrow, number_line, etc.)

The prompt includes `MANIM_MEDIUM` — a 3.5K char document listing exactly what Manim can and cannot render. This prevents the LLM from writing cinematic descriptions like "camera pans across a stadium crowd."

### 1b. Evaluate Angles

```
Input:  3-4 StoryAngle objects
Output: Ranked list with scores, winner, runner-up
```

Each angle scored on 5 dimensions (10 points each, 50 total):
- Hook Power
- Visual Potential
- Clarity
- Surprise
- **Manim Feasibility** — penalizes anything that can't be built with 2D Manim elements

### 1c. Draft Story

```
Input:  Winning angle + topic + duration
Output: Complete story with structured scenes
```

This is where the real specification happens. The prompt includes:
- `MANIM_MEDIUM`: What you can/can't put on screen
- `BEAT_STRUCTURE`: Educational arc (hook → misconception → disruption → build → aha → resolution)
- `VISUAL_VOCABULARY`: Cards, arrows, axes, number lines, etc.

Each scene in the output has ALL of these fields:

```json
{
  "id": 1,
  "name": "hook",
  "beat": "hook",
  "duration": 12,
  "narration": "What if two different-looking numbers are secretly the same?",
  "visual_elements": [
    {
      "name": "question_text",
      "type": "text",
      "label": "Does 0.999... = 1?",
      "position": "UP * 1",
      "color": "#f39c12",
      "font_size": 42
    },
    {
      "name": "number_line",
      "type": "number_line",
      "position": "DOWN * 1",
      "color": "WHITE"
    }
  ],
  "animations": [
    {"action": "write", "target": "question_text", "run_time": 2.0},
    {"action": "create", "target": "number_line", "run_time": 1.5}
  ],
  "cleanup": ["question_text"],
  "persists": ["number_line"],
  "teaching_goal": "The viewer is hooked by a surprising claim",
  "emotion": "surprise and disbelief"
}
```

**Valid element types:** text, card, arrow, line, circle, dot, number_line, axes, graph, brace, table, vgroup

**Valid animation actions:** write, create, fade_in, fade_out, transform, indicate, grow_from_center, move_to, circumscribe, flash

### 1d. Director Review

```
Input:  Story draft + angle
Output: DirectorNotes (score, verdict, fixes, feasibility_issues)
```

The director reviews both **narrative quality** and **Manim feasibility**:
- Hook grab in 3 seconds?
- Natural scene flow?
- Aha moment dramatic enough?
- Every visual_element a valid Manim type?
- Max 4 elements per scene?
- Every element cleaned up or persisted?

Produces a score (1-10) and verdict:
- **approve** (score >= 8): Move to design system
- **revise**: Apply specific fixes, loop back
- **restart**: Try the runner-up angle

### 1e. Revise Story (if needed)

```
Input:  Original draft + director feedback
Output: Revised story
```

Max 2 revision rounds. After revision, `validate_story()` checks both versions — **rejects the revision if it has more issues than the original** (prevents LLM degradation on rewrite).

### Story Validation

`validate_story()` runs deterministic checks:
- Every scene has narration, visual_elements, animations, teaching_goal
- Element types are from the allowed set
- Max 4 elements per scene
- All elements tracked in cleanup or persists
- No duplicate element names
- **Cinema detection**: Flags terms like "crowd", "camera pan", "3D", "photograph", "explosion"

**Saved:** `output/story.json`

---

## Stage 2: Design System

**File:** `manimflow/design_system.py`
**Purpose:** Make every visual design decision before code generation.
**LLM calls:** 1 (+ 1 if design review fails)

```
Input:  Approved story + angle mood
Output: DesignSystem (palette, color_roles, typography, animations, camera_plan, persistent_elements, scene_designs)
```

The design system specifies:
- **palette**: Exact hex colors for primary, secondary, accent, highlight, neutral, background
- **color_roles**: Which concept maps to which palette color (consistent throughout video)
- **typography**: Font sizes and positions for title, body, label, equation
- **animations**: Which Manim animation class to use for enter, exit, emphasis, reveal
- **camera_plan**: Zoom targets and timing per scene
- **persistent_elements**: Objects that appear across multiple scenes with transform tracking
- **scene_designs**: Per-scene layouts with element positions

A `DesignReviewer` scores the design on Gestalt principles, Tufte's rules, and 3Blue1Brown patterns. Score < 5 triggers regeneration with feedback.

**Saved:** `output/design_system.json`

---

## Stage 3: Screenplay

**File:** `manimflow/screenplay.py`
**Purpose:** Translate story into exact shot-by-shot specifications.
**LLM calls:** 1 agent call with knowledge tool access (max 2 tool rounds)

```
Input:  Story + design system context + topic
Output: Screenplay (8-12 Shots with screen_elements, animations, camera, teaching_point)
```

The screenplay is the bridge between "what happens" (story) and "exact Manim code" (codegen). Each shot specifies:
- **screen_elements**: Name, type, label, position, color, width, height, font_size
- **animations**: Action, target, style, run_time
- **narration**: Exact words with sync planning
- **camera**: static, zoom_in, zoom_out, pan
- **teaching_point**: What the viewer learns
- **transition_to_next**: How this connects to the next shot

### Knowledge Base Search

The screenplay agent can search a knowledge base of **140 real Manim scene documents** with **436 tested code patterns** from 14 production video projects.

The search uses BM25 multi-field ranking across 11 fields with structured filters:
- **domain**: mathematics, physics, computer_science, etc.
- **elements**: card, arrow, axes, number_line, etc.
- **animations**: fade_in, transform, indicate, etc.
- **layouts**: centered, grid, side_by_side, etc.
- **techniques**: progressive_disclosure, color_coding, etc.
- **purpose**: demonstration, comparison, revelation, etc.

Example tool call:
```
search_knowledge("pi irrational number fraction cards",
                 domain=["mathematics"],
                 elements=["card", "arrow", "text"],
                 layouts=["centered", "hierarchy"])
→ 3 docs, 9793 chars of real scene examples
```

**Saved:** `output/screenplay.json` (full shot data — elements, animations, narration, camera)

---

## Stage 4: Code Generation

**File:** `manimflow/codegen.py`
**Purpose:** Generate executable Manim Python code.
**LLM calls:** 1 agent call with knowledge tool access (max 3 tool rounds)

```
Input:  Story JSON + screenplay context + design context
Output: Python code (VoiceoverScene)
```

The system prompt includes:
- **MANIM_API_REFERENCE**: Correct API patterns, parameter signatures
- **TECHNICAL_RULES**: VoiceoverScene boilerplate, imports, bookmark sync, rate_func whitelist
- **Design knowledge**: Layout, color, animation, typography, anti-pattern rules
- **Transition guide**: 10 semantic transition types
- **Knowledge base context**: Vocabulary hints for searching

The generated code follows this pattern:

```python
from manim import *
from manim_voiceover import VoiceoverScene
from manimflow.edge_tts_service import EdgeTTSService
import numpy as np

class GeneratedScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(EdgeTTSService(transcription_model="base"))
        self.camera.background_color = BLACK

        def make_card(text, color, width=3, height=1.2):
            rect = RoundedRectangle(width=width, height=height, corner_radius=0.2,
                                    color=color, fill_color=color, fill_opacity=0.15)
            label = Text(text, font_size=24, color=WHITE).move_to(rect.get_center())
            return VGroup(rect, label)

        # Scene 1: Hook
        with self.voiceover(text="<bookmark mark='start'/>What if...") as tracker:
            title = Text("Title", font_size=42, color=WHITE).move_to(UP * 2.5)
            self.play(Write(title), run_time=2.0)
            self.wait_until_bookmark("start")
            # ... animations synced to narration bookmarks
        self.play(FadeOut(title), run_time=1.0)
```

Key patterns:
- `with self.voiceover(text="...") as tracker:` wraps each scene's narration
- `<bookmark mark="X"/>` in narration text marks sync points
- `self.wait_until_bookmark("X")` pauses animation until narrator reaches that point
- `make_card()` helper creates labeled rounded rectangles (the atomic visual unit)
- `FadeOut(*)` between scenes prevents element accumulation

**Saved:** `output/scene.py`

---

## Stage 5: Sanitize + Analyze (No LLM)

**Files:** `manimflow/code_sanitizer.py`, `manimflow/evaluator.py`, `manimflow/spatial_analyzer.py`
**Purpose:** Fix known LLM mistakes and catch layout issues before expensive rendering.
**LLM calls:** 0 (deterministic)

### Code Sanitizer

Fixes applied automatically:
- **rate_func**: ease_in_cubic → smooth (LLM hallucinates non-existent rate functions)
- **Positions**: CENTER → ORIGIN
- **Colors**: CYAN → "#00FFFF", named colors to hex
- **MathTex → Text**: LLM sometimes uses LaTeX despite instructions
- **Non-ASCII removal**: Unicode chars render as grey boxes in Manim
- **API fixes**: .bottom_right → .get_corner(DR)
- **Scene cleanup injection**: Auto-inserts FadeOut between scene boundaries
- **Import validation**: Ensures required imports present

### Static Code Checks

Quick structural validation:
- Syntax valid?
- Scene structure present?
- Duration estimate (sum of run_time + wait values)

If checks fail → `fix_manim_code()` (1 LLM call)

### Spatial Analysis

Parses the code to build a spatial model:
- **Overlap detection**: Elements at similar positions with overlapping bounding boxes
- **Off-screen detection**: Elements outside frame bounds (x: [-7,7], y: [-4,4])
- **Text accumulation**: Elements created but never FadeOut'd
- **Screen utilization**: Too sparse or too dense

If issues found → `fix_manim_code()` with specific spatial fix prompt

---

## Stage 6: Render Loop

**File:** `manimflow/renderer.py`
**Purpose:** Compile Manim code to video with auto-error-recovery.
**LLM calls:** 0-5 (only on failure)

```
Loop (max 5 attempts):
    1. Write code to scene.py
    2. Run: manim -q{quality} scene.py GeneratedScene
    3. Success? → Return video path
    4. Error? → fix_manim_code(code, error) → re-sanitize → retry
```

Quality levels: l=480p15fps, m=720p30fps, h=1080p60fps, k=4K60fps

Error enhancement: The renderer parses Manim error messages and adds context:
- LaTeX errors → reads auxiliary log files for details
- NameError → suggests correct rate_func or class names
- Bookmark mismatch → identifies which bookmark is missing

**Output:** `output/videos/scene/{quality}/GeneratedScene.mp4`

---

## Stage 7: Quality Evaluation Loop

**File:** `manimflow/evaluator.py`, `manimflow/code_editor.py`
**Purpose:** Score rendered output, improve if below threshold.
**LLM calls:** 2 per round (vision + code analysis), max 2 rounds

### Vision Evaluation

```
Input:  6 keyframes extracted from video + story
Output: Visual score (1-10) + visual_issues[] + semantic_issues[]
```

Extracts 6 evenly-spaced frames from the video and sends them to Claude's vision API. Checks for:
- Text overlap, readability
- Grey boxes (font rendering failures)
- Off-screen content
- Visual composition quality
- Semantic correctness (does the visual match the story?)

### Code-Based Evaluation

```
Input:  Manim code + story
Output: 8-dimension scores + overall score + verdict
```

Scores 8 dimensions:
1. Visual Clarity (1-10)
2. Pacing (1-10)
3. Progressive Build (1-10)
4. Color Usage (1-10)
5. Text Management (1-10)
6. Math Accuracy (1-10)
7. Engagement (1-10)
8. Animation Variety (1-10)

### Combined Score

```
Combined = 0.4 * vision_score + 0.6 * code_score
Vision veto: if vision_score < 5 → cap combined at 6.0
```

- Combined >= 7 → **PASS** (exit loop)
- Combined < 7 → **FIX** (surgical edit or full rewrite, then re-render)

### Surgical Fix

`code_editor.py` makes targeted edits instead of full rewrites:
- LLM receives numbered code + issues
- Returns JSON array of edits: REPLACE (lines X-Y), INSERT (after line Z), DELETE (lines X-Y)
- Edits applied in reverse order to preserve line numbers
- Falls back to full `fix_manim_code()` if surgical fix has no effect

---

## Stage 8: Audio + Thumbnail

**Files:** `manimflow/music.py`, `manimflow/voiceover.py`, `manimflow/thumbnail.py`
**Purpose:** Add background music and generate marketing thumbnail.
**LLM calls:** 0 (all ffmpeg)

### Voiceover

Already baked into the render via manim-voiceover + EdgeTTSService. The voiceover plays during rendering, synced to `<bookmark>` tags in the narration text.

### Background Music

```
1. Select mood based on content category (formula → contemplative, mind_blown → dramatic)
2. Generate ambient pad using ffmpeg synth (different frequencies per mood)
3. Extract voiceover audio from rendered video
4. Mix voiceover + background music (music at lower volume)
5. Merge mixed audio back into video
```

### Thumbnail

```
1. Extract 10 candidate frames (skip first/last 10% of video)
2. Pick frame with largest file size (most visual content)
3. Overlay title text using ffmpeg
```

**Saved:** `output/{title}_FINAL.mp4`, `output/thumbnail/thumbnail_titled.png`

---

## The Knowledge System

**Files:** `manimflow/knowledge/tool.py`, `manimflow/knowledge/search.py`, `manimflow/knowledge/vocabulary.py`

### What It Contains

- **140 scene documents** extracted from 14 real Manim video projects
- **436 tested code patterns** with working Manim code
- **343-term controlled vocabulary** across 6 categories

### How It Works

The knowledge base is exposed as a tool that the LLM can call during screenplay writing, code generation, and code fixing.

**Tool definition:**
```json
{
  "name": "search_knowledge",
  "input_schema": {
    "properties": {
      "query": "Free text search",
      "domain": ["mathematics", "physics", ...],
      "elements": ["card", "arrow", "axes", ...],
      "animations": ["fade_in", "transform", ...],
      "layouts": ["centered", "grid", ...],
      "techniques": ["progressive_disclosure", ...],
      "purpose": ["demonstration", "comparison", ...],
      "limit": 3
    }
  }
}
```

**Search engine:** BM25 multi-field ranking with 11 fields at different weights:
- Tags: 5.0x (highest signal)
- Title, description: 3.0x
- Patterns, design notes: 2.0x
- Code: 0.5x (lowest — code matches are noisy)

### Which Stages Use It

| Stage | Max tool rounds | Why |
|---|---|---|
| Screenplay | 2 | Find similar visual approaches from real videos |
| Code generation | 3 | Find working code patterns for the techniques needed |
| Code fix | 2 | Find patterns to fix specific render errors |
| Surgical fix | 2 | Find patterns for targeted code edits |

The LLM decides IF and WHAT to search. System prompt says "search once before writing" with vocabulary hints so the LLM knows what filter terms are available.

---

## The Agent System

**File:** `manimflow/agent.py`

All LLM calls go through the `Agent` class, which provides:
- **Retry with backoff**: 4 attempts on API errors
- **Token tracking**: Input/output/cache token counts per call
- **Tool use loop**: Call → tool_use → execute → feed back → call again
- **Prompt caching**: Reuses cached system prompts across calls
- **Model routing**: Default claude-sonnet-4, configurable via MODEL env var

### Agentic Loop

```python
agent = Agent(system_prompt="...", tools=TOOLS)
agent.add_user_message("Generate code for...")
response = await agent.run(max_tool_rounds=3)
```

The `run()` method:
```
for round in range(max_tool_rounds):
    call LLM
    if stop_reason != "tool_use":
        return text response     ← LLM is done
    execute each tool_use block
    feed results back as tool_result messages
    continue loop

force one final call without tools  ← safety net
```

### Backward Compatibility

`call_llm(system, user)` is a convenience wrapper for stages that don't need tools (writers room, design system, evaluation). It creates a one-shot Agent without tools.

---

## Module Map

```
manimflow/
├── cli.py                  Entry point (argument parsing)
├── pipeline.py             Main orchestrator (Stage 1-8)
│
├── writers_room.py         Stage 1: Story generation (explore/evaluate/draft/review/revise)
├── design_system.py        Stage 2: Visual design specification
├── screenplay.py           Stage 3: Shot-by-shot visual script
├── codegen.py              Stage 4: Manim code generation
├── code_sanitizer.py       Stage 5a: Deterministic code fixes
├── spatial_analyzer.py     Stage 5b: Layout analysis
├── renderer.py             Stage 6: Manim rendering
├── evaluator.py            Stage 7: Quality scoring (vision + code)
├── code_editor.py          Stage 7: Surgical code fixes
├── voiceover.py            Stage 8: Audio utilities
├── music.py                Stage 8: Background music generation
├── thumbnail.py            Stage 8: Thumbnail extraction
│
├── agent.py                LLM wrapper (retry, tools, caching, tracking)
├── domain_knowledge.py     Hardcoded design rules (layout, color, animation, typography)
├── manim_reference.py      Manim API reference for codegen prompts
├── transitions.py          10 semantic transition types
├── categories.py           7 content categories with style hints
├── engagement.py           Research-backed storytelling structures
├── timing.py               Video duration utilities
├── platform.py             Platform presets (YouTube, TikTok)
├── story.py                Legacy story generator (replaced by writers_room)
│
├── knowledge/
│   ├── __init__.py
│   ├── tool.py             Tool definition + execute_tool dispatch
│   ├── search.py           BM25 multi-field search engine
│   └── vocabulary.py       343-term controlled vocabulary
│
└── reviewers/
    ├── base.py             BaseReviewer + ReviewResult
    └── design_reviewer.py  Design system quality gate
```

## Output Directory Structure

```
output/
├── story.json              Complete story with structured scenes
├── design_system.json      Visual design specification
├── screenplay.json         Full shot data (elements, animations, narration)
├── scene.py                Final working Manim code
├── {title}_FINAL.mp4       Video with voiceover + background music
├── videos/                 Raw rendered video
├── voiceovers/             Voiceover audio files + cache
├── frames/                 Extracted keyframes (for vision eval)
├── thumbnail/              Generated thumbnail
├── images/                 Frame images
└── texts/                  Subtitle/text files
```

## Data Flow

The key architectural insight: information flows through **three levels of specificity**, each constraining the next.

```
STORY (what happens)
  "Show a dot sliding toward 1 on a number line, with a shrinking gap"
  Elements: [dot, number_line, brace, text]
  Beat: misconception → disruption → aha

      ▼  constrains

SCREENPLAY (how it looks)
  Shot 3: dot at LEFT*2 color=#3498db, number_line at DOWN*1,
          brace between dot and 1 marker, text "Gap = ?" at UP*1
  Animation: move_to(dot, RIGHT*2, run_time=3.0), transform(brace, smaller_brace)

      ▼  constrains

CODE (the implementation)
  dot = Dot(color="#3498db").move_to(LEFT*2 + DOWN*1)
  self.play(dot.animate.move_to(RIGHT*2 + DOWN*1), run_time=3.0)
```

By the time code generation runs, there are minimal creative decisions left — just API translation. This is why videos render on first attempt: the upstream story is already in the language of the medium.
