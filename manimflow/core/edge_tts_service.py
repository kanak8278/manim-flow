"""EdgeTTS SpeechService for manim-voiceover.

Wraps Microsoft's edge-tts (free neural voices) as a proper manim-voiceover
SpeechService, so you can use it with VoiceoverScene and get bookmark sync,
caching, speed adjustment, and Whisper transcription for free.

Usage:
    from manimflow.edge_tts_service import EdgeTTSService

    class MyScene(VoiceoverScene):
        def construct(self):
            self.set_speech_service(EdgeTTSService(voice="en-US-GuyNeural"))
            with self.voiceover(text="Hello world") as tracker:
                self.play(Write(text), run_time=tracker.duration)
"""

import asyncio
import os
import ssl
from pathlib import Path

from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService

# ---------------------------------------------------------------------------
# SSL fix: uv-managed Python often lacks system certs, which makes edge-tts
# fail on HTTPS connections. truststore injects the OS cert store into ssl;
# certifi is the fallback.
# ---------------------------------------------------------------------------
try:
    import truststore

    truststore.inject_into_ssl()
except Exception:
    try:
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Available voices (all neural, all free via edge-tts)
# ---------------------------------------------------------------------------
EDGE_TTS_VOICES = {
    "en-US-GuyNeural": "Male, US English",
    "en-US-JennyNeural": "Female, US English",
    "en-GB-RyanNeural": "Male, British English",
    "en-GB-SoniaNeural": "Female, British English",
    "en-IN-PrabhatNeural": "Male, Indian English",
    "en-IN-NeerjaNeural": "Female, Indian English",
}

DEFAULT_VOICE = "en-US-GuyNeural"


class EdgeTTSService(SpeechService):
    """SpeechService that uses Microsoft Edge TTS (edge-tts) for synthesis.

    Produces high-quality neural speech for free — no API key required.
    Supports all voices listed in ``EDGE_TTS_VOICES`` and any other valid
    edge-tts voice string.
    """

    def __init__(
        self,
        voice: str = DEFAULT_VOICE,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        **kwargs,
    ):
        """
        Args:
            voice: Edge TTS voice name. Defaults to ``en-US-GuyNeural``.
            rate: Speech rate adjustment, e.g. ``"+10%"`` or ``"-5%"``.
            volume: Volume adjustment, e.g. ``"+0%"``.
            pitch: Pitch adjustment, e.g. ``"+0Hz"``.
            **kwargs: Forwarded to :class:`SpeechService` (``global_speed``,
                ``cache_dir``, ``transcription_model``, etc.).
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        SpeechService.__init__(self, **kwargs)

    # ------------------------------------------------------------------
    # Core TTS generation
    # ------------------------------------------------------------------

    def generate_from_text(
        self,
        text: str,
        cache_dir: str = None,
        path: str = None,
        **kwargs,
    ) -> dict:
        """Generate speech from *text* using edge-tts.

        This method is called by the base class's ``_wrap_generate_from_text``.
        It handles caching, file naming, and returns the dict that
        manim-voiceover expects.

        Args:
            text: Raw input text (may contain bookmark tags).
            cache_dir: Override for the cache directory.
            path: Explicit output filename (relative to *cache_dir*).

        Returns:
            dict with at least ``input_text``, ``input_data``, and
            ``original_audio`` keys.
        """
        if cache_dir is None:
            cache_dir = self.cache_dir

        # Strip bookmark tags for the actual TTS input and cache key
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "edge_tts",
            "voice": self.voice,
            "rate": self.rate,
            "volume": self.volume,
            "pitch": self.pitch,
        }

        # Check cache first
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        # Determine output path (relative to cache_dir)
        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = path

        output_file = str(Path(cache_dir) / audio_path)

        # Run the async edge-tts synthesis
        try:
            self._synthesize(input_text, output_file)
        except Exception as e:
            logger.error(f"edge-tts synthesis failed: {e}")
            raise

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _synthesize(self, text: str, output_path: str) -> None:
        """Run edge-tts async synthesis in a sync context."""
        import edge_tts

        async def _run():
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate,
                volume=self.volume,
                pitch=self.pitch,
            )
            await communicate.save(output_path)

        # If there's already a running event loop (e.g. Jupyter), use
        # nest_asyncio or create a new thread. Otherwise just asyncio.run().
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside an existing event loop (Jupyter, etc.)
            import threading

            exception = None

            def _thread_target():
                nonlocal exception
                try:
                    asyncio.run(_run())
                except Exception as exc:
                    exception = exc

            t = threading.Thread(target=_thread_target)
            t.start()
            t.join()
            if exception is not None:
                raise exception
        else:
            asyncio.run(_run())
