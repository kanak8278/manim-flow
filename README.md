# ManimFlow

ManimFlow generates educational explainer videos from a text prompt — you type a topic and it produces a complete animated video with voiceover, background music, and a thumbnail, using Manim (3Blue1Brown's animation engine) and Claude for story/code generation.

```bash
uv run manimflow "Why is 0.999... exactly equal to 1?"
```

## What it does

ManimFlow takes any educational topic and produces a complete video through a multi-stage pipeline:

1. **Writers Room** — 3 parallel AI writers create story drafts, a reviewer picks the best and cross-pollinates ideas, then the writer revises based on feedback
2. **Design System** — A visual designer reads the story and adds every visual specification: colors, typography, positions, animation types, transitions
3. **Screenplay** — Converts the visual story into structured shot specifications with semantic positioning, bookmark sync, and knowledge base search for real Manim patterns
4. **Code Generation** — Translates the screenplay into executable Manim Python code
5. **Layout Inspection** — Scene inspector executes the code without rendering to extract exact geometry, then the layout checker compares against screenplay intent
6. **Rendering** — Manim renders the animation, with auto-fix loop on failure
7. **Quality Evaluation** — Vision + code analysis scoring with surgical fix loop
8. **Audio + Thumbnail** — Background music mixing and thumbnail generation

## Install

```bash
git clone https://github.com/kanak8278/manim-flow.git
cd manim-flow
uv sync

echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
# Optional: Langfuse observability
echo "LANGFUSE_PUBLIC_KEY=pk-lf-..." >> .env
echo "LANGFUSE_SECRET_KEY=sk-lf-..." >> .env

export $(cat .env | xargs)
uv run manimflow "Why is 0.999... equal to 1?"
```

### System dependencies

```bash
# macOS
brew install ffmpeg
```

## Usage

```bash
# Basic — 2-minute explainer
uv run manimflow "Why is the area of a circle pi*r^2?"

# Short-form (60s)
uv run manimflow "Why can't you divide by zero?" --duration 60

# Deep dive (5 minutes)
uv run manimflow "How does GPS use relativity?" --duration 300

# High quality render
uv run manimflow "Euler's identity" --quality h

# No voiceover
uv run manimflow "The butterfly curve" --voice none
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--duration`, `-d` | 120 | Target video length in seconds |
| `--quality`, `-q` | l | Render quality: l=480p, m=720p, h=1080p, k=4K |
| `--category`, `-c` | auto | Content category (auto-detected) |
| `--voice`, `-v` | male_us | Voiceover voice (or `none`) |
| `--output`, `-o` | output/ | Output directory |
| `--max-fix-attempts` | 5 | Max render fix attempts |
| `--max-quality-loops` | 2 | Max quality improvement rounds |

## Architecture

```
Topic (text)
    │
    ▼
┌─────────────────────────────────┐
│  PREPRODUCTION                  │
│                                 │
│  Writers Room ─── 3 parallel    │
│  writers + reviewer + revise    │
│  Output: free-form story prose  │
│                                 │
│  Design System ─── visual       │
│  specs added to prose           │
│  Output: design rules +         │
│          visual story            │
│                                 │
│  Screenplay ─── structured      │
│  shots with knowledge search    │
│  + validation fix loop          │
│  Output: shots JSON with        │
│  semantic positions             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  PRODUCTION                     │
│                                 │
│  Codegen → Manim Python code    │
│  Sanitizer → fix LLM mistakes   │
│  Scene Inspector → exact        │
│    geometry without rendering    │
│  Layout Checker → compare       │
│    screenplay intent vs code    │
│  Render Loop → auto-fix on fail │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  POSTPRODUCTION                 │
│                                 │
│  Quality Eval (vision + code)   │
│  Background Music               │
│  Thumbnail Generation           │
└────────────┬────────────────────┘
             │
             ▼
        {title}_FINAL.mp4
```

## Project Structure

```
manimflow/
├── cli.py                  CLI entry point
├── pipeline.py             Main orchestrator
│
├── core/                   Infrastructure
│   ├── agent.py            LLM wrapper (retry, caching, thinking, tools)
│   ├── tracing.py          Langfuse v4 observability (@observe)
│   └── edge_tts_service.py Text-to-speech service
│
├── preproduction/          Story → Design → Screenplay
│   ├── writers_room.py     Parallel writers + reviewer + revise
│   ├── design_system.py    Visual specs in prose
│   ├── screenplay.py       Structured shots + validation loop
│   └── screenplay_validator.py  Structural checks
│
├── production/             Code → Inspect → Render
│   ├── codegen.py          Manim code generation
│   ├── code_sanitizer.py   Fix common LLM mistakes
│   ├── code_editor.py      Surgical targeted edits
│   ├── renderer.py         Manim rendering + auto-fix
│   ├── scene_inspector.py  Extract geometry without rendering
│   ├── layout_checker.py   Screenplay intent vs code geometry
│   ├── spatial_analyzer.py Pre-render layout analysis
│   └── wireframe.py        Static PNG renderer
│
├── postproduction/         Eval → Audio → Thumbnail
│   ├── evaluator.py        Quality scoring (vision + code)
│   ├── voiceover.py        TTS utilities
│   ├── music.py            Background music
│   ├── thumbnail.py        Thumbnail extraction
│   └── timing.py           Duration utilities
│
├── knowledge/              Knowledge base
│   ├── tool.py             Search tool for LLM agents
│   ├── search.py           BM25 multi-field search engine
│   └── vocabulary.py       343-term controlled vocabulary
│
├── prompts/                All prompt templates
│   ├── writers_room.py
│   ├── design_system.py
│   └── screenplay.py
│
├── reference/              Static reference data
│   ├── domain_knowledge.py Layout, color, animation rules
│   ├── manim_reference.py  Manim API reference
│   ├── categories.py       Content categories
│   ├── transitions.py      Transition types
│   ├── platform.py         Platform presets
│   └── topics.py           Suggested topics
│
└── reviewers/              Review systems
    ├── base.py
    └── design_reviewer.py
```

## Knowledge Base

ManimFlow includes a knowledge base of **140 real Manim scene documents** with **436 tested code patterns** from 14 production video projects. The screenplay agent searches this during generation to find real examples of how specific visual techniques were implemented.

The search uses BM25 multi-field ranking with a **343-term controlled vocabulary** across domains, elements, animations, layouts, techniques, and visual purpose.

## Observability

ManimFlow integrates with [Langfuse](https://langfuse.com) for tracing. Set `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in your `.env` to see the full call tree: every LLM call, tool search, and pipeline stage with timing and token usage.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- ffmpeg
- Anthropic API key (Claude Sonnet)
