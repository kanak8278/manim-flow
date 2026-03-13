# ManimFlow

ManimFlow generates educational math/physics explainer videos from a text prompt — you type a topic like "Why is 0.999... = 1?" and it produces a complete animated video with
voiceover, background music, and a thumbnail, using Manim (3Blue1Brown's animation engine) and Claude for story/code generation.
```bash
uv run manimflow "Why is 0.999... exactly equal to 1?"
```

## What it does

ManimFlow takes a math/physics question and produces a complete video:

1. **Story** -- LLM generates a narrative script with hook, build, climax, resolve
2. **Narrative review** -- Scores the story (hook quality, pacing, visual plan) and improves it if weak
3. **Voiceover** -- Text-to-speech with timing sync (edge-tts, 5 voice options)
4. **Animation code** -- Generates Manim Python code with shapes, curves, diagrams
5. **Quality checks** -- Spatial overlap detection, code sanitization, frame-by-frame vision analysis
6. **Rendering** -- Auto-fix loop retries up to 5 times on failure
7. **Music** -- Background ambient pad with auto-ducking under narration
8. **Thumbnail** -- Extracts the most visually striking frame

Output: `{title}_FINAL.mp4` with voiceover + background music.

## Install

```bash
git clone https://github.com/kanak8278/manim-flow.git
cd manim-flow

# Install dependencies
uv sync

# Set your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run (prefix all commands with `uv run`)
export $(cat .env | xargs)
uv run manimflow "Why is 0.999... equal to 1?"
```

### System dependencies

```bash
# macOS
brew install ffmpeg

# LaTeX (for MathTex support -- optional, Text() works without it)
# If you have TeX Live installed, ManimFlow auto-configures dvisvgm
```

## Usage

### Generate a video

```bash
# Basic -- 2-minute explainer with voiceover
uv run manimflow "Why is the area of a circle pi*r^2?"

# Specify duration
manimflow "The Monty Hall Problem" --duration 120

# Short-form (60s TikTok/Reel style)
manimflow "Why can't you divide by zero?" --duration 60

# Deep dive (5 minutes)
manimflow "How does GPS use relativity?" --duration 300

# Pick a content category
manimflow "0.999... = 1" --category mind_blown

# Change voice
manimflow "E = mc^2 explained" --voice female_uk

# No voiceover
manimflow "The butterfly curve" --voice none

# High quality render
manimflow "Euler's identity" --quality h
```

### Browse topics and categories

```bash
# List suggested topics ranked by engagement potential
manimflow topics

# Filter by category
manimflow topics --category mind_blown

# List all content categories
manimflow categories
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--duration`, `-d` | 120 | Target video length in seconds (60/120/300/480) |
| `--quality`, `-q` | l | Render quality: l=480p, m=720p, h=1080p, k=4K |
| `--category`, `-c` | auto | Content category (auto-detected from topic) |
| `--voice`, `-v` | male_us | Voiceover: male_us, female_us, male_uk, female_uk, male_au, none |
| `--output`, `-o` | output | Output directory |
| `--max-fix-attempts` | 5 | Max auto-fix attempts per render |
| `--max-quality-loops` | 2 | Max quality improvement rounds |
| `--preview`, `-p` | off | Open video after rendering |

### Content categories

| Category | Best for | Duration |
|----------|----------|----------|
| `mind_blown` | Paradoxes, surprising results (0.999=1, Monty Hall) | 120s |
| `proof` | Visual proofs and derivations (Pythagorean, circle area) | 180s |
| `formula` | Famous equations decoded (E=mc^2, F=ma) | 120s |
| `how_it_works` | Mechanism explainers (GPS, Fourier, encryption) | 180s |
| `what_if` | Thought experiments (What if pi=3?) | 120s |
| `visual_beauty` | Mathematical art (butterfly curve, Mandelbrot) | 90s |
| `quick_fact` | 60-second explainers (divide by zero, golden ratio) | 60s |

## Architecture

```
topic
  |
  v
Story Generation (LLM + engagement patterns + category hints)
  |
  v
Narrative Review (score hook/arc/pacing, improve if <6/10)
  |
  v
Voiceover Pre-gen (edge-tts, get per-scene timing)
  |
  v
Code Generation (Manim + API reference + transition vocabulary)
  |
  v
Code Sanitizer (fix rate_funcs, MathTex, non-ASCII, Cross())
  |
  v
Spatial Analysis (text overlap, off-screen, text accumulation)
  |
  v
Render Loop (up to 5 auto-fix attempts)
  |
  v
Vision Evaluation (frame extraction + Claude vision API)
  |
  v
Quality Loop (surgical fixes + re-render, vision veto if frames <5/10)
  |
  v
Audio Production (background music + voiceover + ducking)
  |
  v
Thumbnail Generation (best frame + title overlay)
  |
  v
{title}_FINAL.mp4
```

### Modules (22 files)

| Module | Purpose |
|--------|---------|
| `pipeline.py` | Main orchestrator |
| `story.py` | LLM story generation with duration presets |
| `narrative_reviewer.py` | Pre-code story quality gate |
| `codegen.py` | Manim code generation |
| `code_sanitizer.py` | Auto-fix common LLM mistakes |
| `code_editor.py` | Surgical targeted edits |
| `spatial_analyzer.py` | Pre-render layout analysis |
| `evaluator.py` | Post-render quality scoring (code + vision) |
| `renderer.py` | Manim rendering with auto-fix |
| `voiceover.py` | Text-to-speech (edge-tts) |
| `music.py` | Background music generation + ducking |
| `thumbnail.py` | Best-frame thumbnail extraction |
| `categories.py` | 7 content categories |
| `engagement.py` | Research-backed storytelling structures |
| `transitions.py` | 10 semantic transition types |
| `topics.py` | 30+ curated topics with scoring |
| `platform.py` | Platform presets (YouTube, TikTok, Reels) |
| `project.py` | Project model + content types |
| `editor.py` | Natural language video editing |
| `manim_reference.py` | Full Manim API reference for codegen |
| `llm.py` | Unified LLM backend (API + CLI + vision) |
| `cli.py` | CLI entry point |

## Quality scores

Average quality across tested topics: ~7.5-8.5/10

| Topic | Score |
|-------|-------|
| Birthday Paradox | 8.8 |
| Euler's Formula | 8.5 |
| Monty Hall Problem | 8.4 |
| 0.999... = 1 | 8.1 |
| GPS + Relativity | 8.3 |
| What if pi = 3? | 7.8 |
| Derivatives | 7.6 |
| Gauss Sum (1+2+...+n) | 7.3 |

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- ffmpeg (for audio/video processing)
- Anthropic API key (Claude Sonnet)
- Optional: TeX Live (for MathTex rendering)
