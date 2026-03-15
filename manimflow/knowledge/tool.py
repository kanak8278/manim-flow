"""Knowledge base tool — Claude tool_use schema + executor.

This module defines the search_knowledge tool in the format the Anthropic API
expects, and provides the executor that dispatches tool calls to the actual
search engine.

Usage:
    from manimflow.knowledge.tool import TOOLS, execute_tool

    agent = Agent(system_prompt=..., tools=TOOLS)
    # ... in the agentic loop:
    result = execute_tool(tool_name, tool_input)
"""

from .search import search_knowledge, get_search


# ─── Tool JSON Schema (Anthropic tool_use format) ─────────────────────

SEARCH_KNOWLEDGE_TOOL = {
    "name": "search_knowledge",
    "description": (
        "Search a knowledge base of real Manim video examples with tested code "
        "patterns extracted from production YouTube channels (3Blue1Brown, "
        "Reducible, vcubingx, and others). Use this to find working code "
        "patterns, layout references, animation techniques, and visual "
        "approaches from real videos.\n\n"
        "Call this when you need:\n"
        "- Working Manim code for a specific visual technique\n"
        "- Layout and composition references for a type of diagram\n"
        "- Animation patterns (how to animate swaps, transforms, progressive disclosure)\n"
        "- Domain-specific visualization approaches (ML, algorithms, physics, etc.)\n\n"
        "Combine query (free text) with structured filters for best results."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Free text search. Use natural language or keywords. "
                    "Examples: 'arc swap sorting', 'dynamic line updating "
                    "with value tracker', 'pipeline stages connected by arrows'"
                ),
            },
            "domain": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by topic domain. Examples: sorting, machine_learning, "
                    "calculus, transformers, compression, graph_theory"
                ),
            },
            "elements": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by visual elements on screen. Examples: array, "
                    "matrix, pipeline, arrow, tree, bar_chart, vector_field"
                ),
            },
            "animations": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by animation types. Examples: arc_swap, transform, "
                    "fade_in, lagged_start, color_change, highlight"
                ),
            },
            "layouts": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by spatial layout. Examples: side_by_side, grid, "
                    "hierarchy, flow_left_right, centered"
                ),
            },
            "techniques": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by Manim technique. Examples: value_tracker, "
                    "always_redraw, custom_mobject, color_gradient, zoomed_scene"
                ),
            },
            "purpose": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by visual purpose. Examples: comparison, "
                    "decomposition, step_by_step, process, demonstration"
                ),
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 3)",
                "default": 3,
            },
        },
        "required": [],
    },
}

# All tools the knowledge module provides
TOOLS = [SEARCH_KNOWLEDGE_TOOL]


# ─── Tool executor ─────────────────────────────────────────────────────


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a knowledge tool call and return the result as text.

    Args:
        tool_name: The tool name from the API response
        tool_input: The input dict from the API response

    Returns:
        Text result to feed back to the LLM
    """
    if tool_name == "search_knowledge":
        return _execute_search(tool_input)

    return f"Unknown tool: {tool_name}"


def _execute_search(params: dict) -> str:
    """Execute search_knowledge with the LLM's parameters."""
    return search_knowledge(
        query=params.get("query"),
        domain=params.get("domain"),
        elements=params.get("elements"),
        animations=params.get("animations"),
        layouts=params.get("layouts"),
        techniques=params.get("techniques"),
        purpose=params.get("purpose"),
        limit=params.get("limit", 3),
    )


# ─── System prompt context ─────────────────────────────────────────────


def _get_vocab_block() -> str:
    """Get vocabulary hints for structured filters."""
    from .vocabulary import (
        DOMAINS,
        ELEMENTS,
        ANIMATIONS,
        LAYOUTS,
        TECHNIQUES,
        VISUAL_PURPOSE,
    )

    def sample(s, n=20):
        return ", ".join(sorted(s)[:n])

    return (
        f"**domain**: {sample(DOMAINS)}\n"
        f"**elements**: {sample(ELEMENTS)}\n"
        f"**animations**: {sample(ANIMATIONS)}\n"
        f"**layouts**: {sample(LAYOUTS)}\n"
        f"**techniques**: {sample(TECHNIQUES)}\n"
        f"**purpose**: {sample(VISUAL_PURPOSE)}"
    )


def get_knowledge_system_context() -> str:
    """Knowledge context for codegen — search once, get patterns."""
    ks = get_search()
    stats = ks.stats()

    return f"""## Knowledge Base

You have a `search_knowledge` tool with {stats["total_docs"]} real Manim video examples
and {stats["total_patterns"]} tested code patterns from production channels.

Search ONCE before writing code. One well-crafted query is better than multiple vague ones.
Look for:
- Working code patterns for the technique you need
- Layout/composition that actually renders correctly

After searching, write your response. Do NOT search again unless the first search returned nothing useful.

### Vocabulary for structured filters

{_get_vocab_block()}

Use these exact terms in the structured filter arrays. Combine with free text query for best results.
"""


def get_knowledge_context_screenplay() -> str:
    """Knowledge context for screenplay — multiple targeted searches encouraged."""
    ks = get_search()
    stats = ks.stats()

    return f"""## Knowledge Base

You have a `search_knowledge` tool with {stats["total_docs"]} real Manim video examples
and {stats["total_patterns"]} tested code patterns from production channels.

Search for SPECIFIC things — one technique or one visual pattern per query. Examples of good queries:
- "number line with converging dots approaching a limit"
- "card comparison layout side by side with arrows"
- "transform equation step by step algebraic manipulation"
- "progressive disclosure build up diagram piece by piece"

Search as many times as you need. Each query should be NARROW and SPECIFIC.
Broad queries like "math animation" return noise. Instead search for the exact visual
technique you're trying to specify.

Think about what you need, search for it, examine the results, then search for the next
thing you need. Use results to inform your specifications — real examples show what
positions, sizes, and animation timings actually work.

### Vocabulary for structured filters

{_get_vocab_block()}

Use these exact terms in the structured filter arrays. Combine with free text query for best results.
"""
