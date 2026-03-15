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

ManimFlow's knowledge base (`manimflow/knowledge/scenes/`) was built by
studying animation patterns and techniques from publicly available Manim
projects. Each document contains structured analysis (summaries, design
decisions, composition notes, timing tables) along with short code excerpts
illustrating specific patterns. These excerpts are included for educational
reference with attribution — each document's `source:` field links to the
original file on GitHub.

We gratefully acknowledge the following projects and their authors:

| Project | Author | License |
|---------|--------|---------|
| [Manim Community Edition](https://github.com/ManimCommunity/manim) | Manim Community | MIT |
| [3Blue1Brown videos](https://github.com/3b1b/videos) | Grant Sanderson | CC BY-NC-SA 4.0 |
| [how-sound-works](https://github.com/adamisntdead/how-sound-works) | Sam Enright & Adam Kelly | MIT |
| [manim-animations](https://github.com/kelvinleandro/manim-animations) | kelvinleandro | Unlicensed |
| [manim-interactive](https://github.com/pprunty/manim-interactive) | Patrick Prunty | MIT |
| [manim-projects](https://github.com/tharun0x/manim-projects) | tharun0x | Unlicensed |
| [manim-scripts](https://github.com/gauravmeena0708/manim-scripts) | gauravmeena0708 | Unlicensed |
| [manim-videos](https://github.com/KainaniD/manim-videos) | KainaniD | Unlicensed |
| [manim-with-ease](https://github.com/behackl/manim-with-ease) | Benjamin Hackl | Unlicensed |
| [manim (far1din)](https://github.com/far1din/manim) | far1din | Unlicensed |
| [manim (mashaan14)](https://github.com/mashaan14/manim) | mashaan14 | Unlicensed |
| [ML-Manim_Animations](https://github.com/Kaos599/ML-Manim_Animations) | Harsh Dayal | MIT |
| [ragibson/manim-videos](https://github.com/ragibson/manim-videos) | Ryan Gibson | MIT |
| [Reducible](https://github.com/nipunramk/Reducible) | Nipun Ramakrishnan | Unlicensed |
| [vivek3141/videos](https://github.com/vivek3141/videos) | Vivek Verma | Unlicensed |

Projects marked "Unlicensed" had no license file at the time of study.
If you are an author of one of these projects and would like to be removed
or have your license updated, please open an issue.

## Note on edge-tts

edge-tts is licensed under GPL-3.0. ManimFlow invokes edge-tts as a
separate subprocess for text-to-speech generation. ManimFlow itself is
licensed under Apache-2.0. If GPL-3.0 compatibility is a concern for your
use case, you can use the `--voice none` flag to skip TTS entirely.
