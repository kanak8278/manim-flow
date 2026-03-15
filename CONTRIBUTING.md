# Contributing to ManimFlow

## Dev Setup

```bash
git clone https://github.com/kanak8278/manim-flow.git
cd manim-flow
make install

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

export $(cat .env | xargs)
```

System dependencies: Python 3.11+, ffmpeg, LaTeX — see [README](README.md#prerequisites).

## Project Layout

```
manimflow/
├── preproduction/   Story writing, design system, screenplay generation
├── production/      Code generation, sanitization, rendering
├── postproduction/  Quality evaluation, voiceover, music, thumbnails
├── knowledge/       BM25 search over real Manim scene patterns
├── prompts/         All LLM prompt templates
├── reference/       Static reference data (colors, transitions, categories)
├── core/            LLM agent wrapper, tracing, TTS service
├── cli.py           CLI entry point
└── pipeline.py      Main orchestrator
```

## Common Commands

```bash
make install    # Install dependencies
make lint       # Run ruff linter
make format     # Auto-format code
make test       # Run tests
make run        # Generate a test video
make clean      # Remove caches
```

## Running a Single Stage

The full pipeline takes several minutes and costs API credits. For development, you can work with saved intermediate outputs in `output/<topic>/` — each stage writes its result as JSON.

## Code Style

- We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Run `make lint` before committing
- No strict type annotations enforced yet, but don't remove existing ones

## Submitting a PR

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run `make lint` and `make test`
4. Open a PR with a clear description of what and why
5. Keep PRs focused — one feature or fix per PR

## Good First Contributions

- **Knowledge base entries** — Add new Manim scene patterns to improve code generation
- **Prompt improvements** — Better prompts in `manimflow/prompts/` directly improve output quality
- **Voice options** — Add support for more TTS voices or providers
- **Bug fixes** — Check [Issues](https://github.com/kanak8278/manim-flow/issues)

## Reporting Bugs

Open an issue at https://github.com/kanak8278/manim-flow/issues with:
- The command you ran
- The error output
- Your Python version and OS
