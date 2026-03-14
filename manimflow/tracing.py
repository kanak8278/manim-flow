"""Langfuse tracing — optional observability for the manimflow pipeline.

Activates only when LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are set.
Zero overhead otherwise — all decorators and helpers become no-ops.

Setup:
    1. Sign up at https://cloud.langfuse.com (free tier)
    2. Create a project, grab the keys
    3. Add to .env:
        LANGFUSE_PUBLIC_KEY=pk-lf-...
        LANGFUSE_SECRET_KEY=sk-lf-...
        LANGFUSE_HOST=https://cloud.langfuse.com  # optional, this is the default
"""

import functools
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Lazy singleton
_langfuse = None
_enabled: Optional[bool] = None


def is_enabled() -> bool:
    """Check if Langfuse is configured."""
    global _enabled
    if _enabled is None:
        _enabled = bool(
            os.environ.get("LANGFUSE_PUBLIC_KEY")
            and os.environ.get("LANGFUSE_SECRET_KEY")
        )
        if _enabled:
            logger.info("Langfuse tracing enabled")
        else:
            logger.debug("Langfuse tracing disabled (no keys)")
    return _enabled


def get_langfuse():
    """Get or create the Langfuse client singleton."""
    global _langfuse
    if _langfuse is None and is_enabled():
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse()
            logger.info(f"Langfuse client initialized (host={_langfuse.base_url})")
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            global _enabled
            _enabled = False
    return _langfuse


def flush():
    """Flush pending events to Langfuse. Call at process exit."""
    if _langfuse is not None:
        try:
            _langfuse.flush()
        except Exception:
            pass


# ── Trace context (thread-local stack) ──────────────────────────

import threading

_trace_stack = threading.local()


def _get_stack() -> list:
    if not hasattr(_trace_stack, "items"):
        _trace_stack.items = []
    return _trace_stack.items


def current_trace():
    """Get the current active trace, or None."""
    stack = _get_stack()
    return stack[0] if stack else None


def current_span():
    """Get the innermost active span/trace."""
    stack = _get_stack()
    return stack[-1] if stack else None


@contextmanager
def trace(name: str, metadata: dict | None = None, **kwargs):
    """Start a top-level trace (e.g., one full pipeline run).

    Usage:
        with trace("generate_video", metadata={"topic": topic}) as t:
            # pipeline steps...
            t.update(output={"score": 8.5})
    """
    lf = get_langfuse()
    if lf is None:
        yield _NoOpSpan()
        return

    t = lf.trace(name=name, metadata=metadata or {}, **kwargs)
    stack = _get_stack()
    stack.append(t)
    try:
        yield t
    except Exception as e:
        t.update(metadata={**(metadata or {}), "error": str(e)})
        raise
    finally:
        stack.pop()


@contextmanager
def span(name: str, metadata: dict | None = None, **kwargs):
    """Start a span within the current trace.

    Usage:
        with span("writers_room") as s:
            result = await run_writers_room(...)
            s.update(output={"score": 7})
    """
    parent = current_span()
    if parent is None:
        yield _NoOpSpan()
        return

    s = parent.span(name=name, metadata=metadata or {}, **kwargs)
    stack = _get_stack()
    stack.append(s)
    start = time.time()
    try:
        yield s
    except Exception as e:
        s.update(
            metadata={**(metadata or {}), "error": str(e)},
            end_time=time.time(),
        )
        raise
    finally:
        stack.pop()


def generation(
    name: str,
    model: str,
    input: Any,
    output: Any,
    usage: dict | None = None,
    metadata: dict | None = None,
    **kwargs,
):
    """Log a single LLM generation (call).

    This is called from Agent.call() to record every API call.
    """
    parent = current_span()
    if parent is None:
        # No active trace — try creating a standalone one
        lf = get_langfuse()
        if lf is None:
            return
        parent = lf.trace(name=f"standalone_{name}")

    langfuse_usage = None
    if usage:
        langfuse_usage = {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "total": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            "unit": "TOKENS",
        }
        # Add cache info to metadata
        if usage.get("cache_read_input_tokens"):
            metadata = metadata or {}
            metadata["cache_read_input_tokens"] = usage["cache_read_input_tokens"]
        if usage.get("cache_creation_input_tokens"):
            metadata = metadata or {}
            metadata["cache_creation_input_tokens"] = usage["cache_creation_input_tokens"]

    parent.generation(
        name=name,
        model=model,
        input=input,
        output=output,
        usage=langfuse_usage,
        metadata=metadata or {},
        **kwargs,
    )


# ── No-op fallback ──────────────────────────────────────────────

class _NoOpSpan:
    """Stand-in when Langfuse is disabled. All methods are silent no-ops."""

    def update(self, **kwargs):
        pass

    def span(self, **kwargs):
        return _NoOpSpan()

    def generation(self, **kwargs):
        pass

    def end(self, **kwargs):
        pass

    def score(self, **kwargs):
        pass
