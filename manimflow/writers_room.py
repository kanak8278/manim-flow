"""Writers Room — parallel story exploration with cross-pollinating review.

Level 1 of video creation: generate the complete free-form story BEFORE any
structured specification (design system, screenplay, code).

Flow:
  topic → N parallel story writers → reviewer picks best + feedback → revise → approved story

Output is free-form text describing EVERYTHING that happens in the video:
every motion, every appearance, every exit, every position — in natural language.
No JSON structure at this level. The story IS the artifact.

Config: n = parallel writers (default 3), t = feedback rounds (default 1)
"""

import asyncio
import re
from dataclasses import dataclass
from .agent import Agent
from .prompts.writers_room import (
    WRITER_PERSONAS,
    STORY_WRITER_SYSTEM,
    STORY_REVIEWER_SYSTEM,
)


# ─── DATA CLASSES ───

@dataclass
class ApprovedStory:
    """A story that passed review."""
    title: str
    story_text: str  # free-form detailed prose
    revision_count: int = 0


# ─── XML PARSING HELPERS ───

def _extract_xml_tag(text: str, tag: str) -> str:
    """Extract content between <tag>...</tag>."""
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_story_output(response: str) -> tuple[str, str]:
    """Extract title and story from writer response."""
    title = _extract_xml_tag(response, "title")
    story = _extract_xml_tag(response, "story")

    # Fallback: if no XML tags, treat whole response as story
    if not story:
        story = response.strip()
    if not title:
        lines = story.split("\n")
        if lines and len(lines[0]) < 80:
            title = lines[0].strip("# ").strip()

    return title, story


def _extract_selected_story(response: str) -> str:
    """Extract <selected_story>STORY_N</selected_story> from reviewer response."""
    return _extract_xml_tag(response, "selected_story").strip()


# ─── CORE FUNCTIONS ───

async def _write_single_story(topic: str, audience: str, persona: str) -> Agent:
    """Write one story with a specific creative persona.

    Returns the Agent (with conversation history) so we can continue it for revision.
    """
    agent = Agent(system_prompt=STORY_WRITER_SYSTEM)
    agent.add_user_message(
        f"YOUR CREATIVE LENS: {persona}\n\n"
        f"Write a detailed story for this educational animation video:\n\n"
        f"TOPIC: {topic}\n"
        f"AUDIENCE: {audience}\n\n"
        f"Describe EVERY moment in exhaustive detail — what appears, where, what color, "
        f"how it moves, what the narrator says, how it disappears. "
        f"The animation team should make ZERO creative decisions.\n\n"
        f"Output: <title>...</title><story>...</story>"
    )

    content, _, _ = await agent.call()
    agent.add_assistant_message(content)

    return agent


async def write_stories(
    topic: str, audience: str = "general", n: int = 3
) -> list[Agent]:
    """Run N independent story writers in parallel.

    Returns list of Agent objects (with conversation history) for potential revision.
    """
    tasks = [
        _write_single_story(topic, audience, WRITER_PERSONAS[i % len(WRITER_PERSONAS)])
        for i in range(n)
    ]
    agents = await asyncio.gather(*tasks)
    return list(agents)


async def review_stories(
    writer_agents: list[Agent], topic: str
) -> tuple[Agent, int, str, Agent]:
    """Reviewer reads all stories, picks the best, gives detailed feedback.

    Returns: (reviewer_agent, winning_index, feedback_text, winning_writer_agent)
    """
    stories_block = ""
    for i, agent in enumerate(writer_agents):
        response_text = Agent.extract_text(agent.messages[-1]["content"])
        stories_block += f"\n<STORY_{i+1}>\n{response_text}\n</STORY_{i+1}>\n"

    reviewer = Agent(system_prompt=STORY_REVIEWER_SYSTEM)
    reviewer.add_user_message(
        f"TOPIC: {topic}\n\n"
        f"Review these {len(writer_agents)} stories. For each, evaluate narrative quality "
        f"and Manim feasibility.\n\n"
        f"{stories_block}\n\n"
        f"Pick the BEST story. Then give DETAILED, SPECIFIC feedback for how to improve it.\n\n"
        f"If any ideas from the other stories would strengthen the winner, describe those "
        f"ideas IN FULL (the writer won't see the other stories).\n\n"
        f"Your feedback must be SELF-CONTAINED and explain WHY each change matters.\n\n"
        f"Start your response with: <selected_story>STORY_N</selected_story>\n"
        f"Then write your detailed feedback."
    )

    content, _, _ = await reviewer.call()
    reviewer.add_assistant_message(content)
    feedback_text = Agent.extract_text(content)

    selected = _extract_selected_story(feedback_text)

    winning_index = 0
    if selected:
        try:
            num = int(re.search(r"\d+", selected).group())
            winning_index = max(0, min(num - 1, len(writer_agents) - 1))
        except (AttributeError, ValueError):
            pass

    winning_agent = writer_agents[winning_index]

    return reviewer, winning_index, feedback_text, winning_agent


async def revise_story(writer_agent: Agent, feedback: str) -> str:
    """Send feedback to the winning writer for revision.

    Continues the writer's conversation history so it has full context.
    """
    writer_agent.add_user_message(
        f"Here is feedback from the creative director. Apply ALL changes.\n\n"
        f"{feedback}\n\n"
        f"Rewrite the complete story with these improvements. Keep everything that works. "
        f"Fix everything flagged. Be just as detailed as before — every motion, "
        f"every appearance, every color, every position.\n\n"
        f"Output: <title>...</title><story>...</story>"
    )

    content, _, _ = await writer_agent.call()
    writer_agent.add_assistant_message(content)

    return Agent.extract_text(content)


# ─── ORCHESTRATOR ───

async def run_writers_room(
    topic: str,
    audience: str = "general",
    n: int = 3,
    t: int = 1,
    verbose: bool = True,
) -> ApprovedStory:
    """Run the full writers room: N parallel writers → review → revise (t rounds).

    Args:
        topic: The video topic
        audience: Target audience
        n: Number of parallel story writers
        t: Number of review-revise rounds
        verbose: Print progress
    """
    _log = print if verbose else lambda *a: None

    # Phase 1: N parallel story writers
    _log(f"\n--- Writers Room: {n} writers drafting stories ---")
    writer_agents = await write_stories(topic, audience, n)

    for i, agent in enumerate(writer_agents):
        response = Agent.extract_text(agent.messages[-1]["content"])
        title, story = _extract_story_output(response)
        _log(f"  Writer {i+1}: \"{title}\"")
        preview = story.split("\n")[0][:80] if story else "(empty)"
        _log(f"    {preview}...")

    # Phase 2-3: Review + revise loop
    reviewer_agent = None
    winning_agent = None

    for round_num in range(t):
        _log(f"\n--- Writers Room: Review round {round_num + 1}/{t} ---")

        if round_num == 0:
            reviewer_agent, winning_index, feedback_text, winning_agent = (
                await review_stories(writer_agents, topic)
            )
        else:
            revised_response = Agent.extract_text(winning_agent.messages[-1]["content"])
            reviewer_agent.add_user_message(
                f"Here is the revised story after your feedback:\n\n"
                f"{revised_response}\n\n"
                f"Review it again. Has the writer addressed your feedback? "
                f"What still needs improvement? Be specific."
            )
            content, _, _ = await reviewer_agent.call()
            reviewer_agent.add_assistant_message(content)
            feedback_text = Agent.extract_text(content)

        selected = _extract_selected_story(feedback_text)
        if selected:
            _log(f"  Selected: {selected}")

        feedback_lines = feedback_text.split("\n")
        for line in feedback_lines[:5]:
            line = line.strip()
            if line and not line.startswith("<"):
                _log(f"  {line[:100]}")

        _log(f"\n--- Writers Room: Revising story ---")
        revised_text = await revise_story(winning_agent, feedback_text)
        title, story = _extract_story_output(revised_text)
        _log(f"  Revised: \"{title}\"")
        preview = story.split("\n")[0][:80] if story else "(empty)"
        _log(f"    {preview}...")

    # Extract final story
    final_response = Agent.extract_text(winning_agent.messages[-1]["content"])
    title, story_text = _extract_story_output(final_response)

    if not title:
        title = topic

    _log(f"\n  Final story: \"{title}\" ({len(story_text)} chars)")

    return ApprovedStory(
        title=title,
        story_text=story_text,
        revision_count=t,
    )
