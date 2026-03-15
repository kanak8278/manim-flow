"""ManimFlow - End-to-end math/physics explainer video generation."""


def __getattr__(name):
    # Lazy import — EdgeTTSService depends on manim which needs system deps
    if name == "EdgeTTSService":
        from .core.edge_tts_service import EdgeTTSService

        return EdgeTTSService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
