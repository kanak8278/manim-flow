# Third-Party Notices

## Runtime Dependencies

ManimFlow depends on the following open-source libraries, installed
automatically via `uv sync`. See `pyproject.toml` for version constraints.

| Library | License | Link |
|---------|---------|------|
| Manim Community Edition | MIT | https://github.com/ManimCommunity/manim |
| manim-voiceover | MIT | https://github.com/ManimCommunity/manim-voiceover |
| Anthropic Python SDK | MIT | https://github.com/anthropics/anthropic-sdk-python |
| edge-tts | GPL-3.0 | https://github.com/rany2/edge-tts |
| openai-whisper | MIT | https://github.com/openai/whisper |
| Langfuse | MIT | https://github.com/langfuse/langfuse-python |
| tenacity | Apache-2.0 | https://github.com/jd/tenacity |
| stable-ts | MIT | https://github.com/jianfch/stable-ts |

## Knowledge Base Sources

ManimFlow's knowledge base was built by studying animation patterns and
techniques from publicly available Manim projects. **No source code from
these projects is included in or distributed with ManimFlow.** The knowledge
base contains abstracted patterns, technique descriptions, and API usage
examples derived from reading these works.

We gratefully acknowledge the following projects and their authors:

| Project | Author | License |
|---------|--------|---------|
| [Manim Community Edition](https://github.com/ManimCommunity/manim) | Manim Community | MIT |
| [3Blue1Brown videos](https://github.com/3b1b/videos) | Grant Sanderson | CC BY-NC-SA 4.0 |
| [chanim](https://github.com/raghavg123/chanim) | raghavg123 | MIT |
| [manim-slides](https://github.com/jeertmans/manim-slides) | Jérome Eertmans | MIT |
| [manim-physics](https://github.com/Matheart/manim-physics) | Matheart | Unlicensed |
| [quantum-animation-toolbox](https://github.com/willzeng/quantum-animation-toolbox) | Will Zeng et al. | Apache-2.0 |
| [ML-Manim_Animations](https://github.com/harshdayal/ML-Manim_Animations) | Harsh Dayal | MIT |
| [ragibson/manim-videos](https://github.com/ragibson/manim-videos) | Ryan Gibson | MIT |
| [Reducible](https://github.com/Reducible) | Reducible | Unlicensed |
| [vivek3141 videos](https://github.com/vivek3141) | Vivek Verma | Unlicensed |
| [how-sound-works](https://github.com/samenright/how-sound-works) | Sam Enright & Adam Kelly | MIT |
| [manim-interactive](https://github.com/patrickprunty/manim-interactive) | Patrick Prunty | MIT |

Projects marked "Unlicensed" had no license file at the time of study.
If you are an author of one of these projects and would like to be removed
or have your license updated, please open an issue.

## Note on edge-tts

edge-tts is licensed under GPL-3.0. ManimFlow invokes edge-tts as a
separate subprocess for text-to-speech generation. ManimFlow itself is
licensed under Apache-2.0. If GPL-3.0 compatibility is a concern for your
use case, you can use the `--voice none` flag to skip TTS entirely.
