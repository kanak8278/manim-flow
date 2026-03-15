"""Langfuse tracing — observability via @observe decorators.

Activates only when LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are set.
Zero overhead otherwise — the observe decorator becomes a passthrough.

Uses Langfuse v4 API:
- @observe() on pipeline functions for automatic call tree tracing
- @observe(as_type='generation') on LLM calls for model/token tracking
- lf.update_current_generation() to log model, usage, metadata
- lf.update_current_span() to log outputs and metadata

Setup:
    1. Sign up at https://cloud.langfuse.com
    2. Create a project, grab the keys
    3. Add to .env:
        LANGFUSE_PUBLIC_KEY=pk-lf-...
        LANGFUSE_SECRET_KEY=sk-lf-...
        LANGFUSE_BASE_URL=https://cloud.langfuse.com
"""

import logging
import os

logger = logging.getLogger(__name__)

_langfuse = None
_enabled = None


def is_enabled() -> bool:
    """Check if Langfuse tracing is configured."""
    global _enabled
    if _enabled is None:
        _enabled = bool(
            os.environ.get("LANGFUSE_PUBLIC_KEY")
            and os.environ.get("LANGFUSE_SECRET_KEY")
        )
    return _enabled


def get_langfuse():
    """Get or create the Langfuse client singleton."""
    global _langfuse
    if _langfuse is None and is_enabled():
        try:
            from langfuse import Langfuse

            _langfuse = Langfuse()
            logger.info("Langfuse client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            global _enabled
            _enabled = False
    return _langfuse


def flush():
    """Flush pending events to Langfuse."""
    if _langfuse is not None:
        try:
            _langfuse.flush()
        except Exception:
            pass


def observe(*args, **kwargs):
    """Wrapper around langfuse.observe that falls back to passthrough when disabled."""
    if is_enabled():
        try:
            from langfuse import observe as lf_observe

            return lf_observe(*args, **kwargs)
        except ImportError:
            pass

    # Fallback: passthrough decorator
    def passthrough(func):
        return func

    if args and callable(args[0]):
        return args[0]
    return passthrough


def update_generation(model: str = "", usage: dict = None, metadata: dict = None):
    """Update the current generation span with model/usage info."""
    lf = get_langfuse()
    if lf is None:
        return
    try:
        kwargs = {}
        if model:
            kwargs["model"] = model
        if usage:
            kwargs["usage_details"] = {
                "input": usage.get("input_tokens", 0),
                "output": usage.get("output_tokens", 0),
            }
            if usage.get("cache_read_input_tokens"):
                kwargs.setdefault("metadata", {})["cache_read"] = usage[
                    "cache_read_input_tokens"
                ]
        if metadata:
            kwargs["metadata"] = {**kwargs.get("metadata", {}), **metadata}
        lf.update_current_generation(**kwargs)
    except Exception as e:
        logger.debug(f"Failed to update generation: {e}")


def update_span(output=None, metadata: dict = None):
    """Update the current span with output/metadata."""
    lf = get_langfuse()
    if lf is None:
        return
    try:
        kwargs = {}
        if output is not None:
            kwargs["output"] = output
        if metadata:
            kwargs["metadata"] = metadata
        lf.update_current_span(**kwargs)
    except Exception as e:
        logger.debug(f"Failed to update span: {e}")


def score_trace(name: str, value: float):
    """Score the current trace."""
    lf = get_langfuse()
    if lf is None:
        return
    try:
        lf.score_current_trace(name=name, value=value)
    except Exception as e:
        logger.debug(f"Failed to score trace: {e}")
