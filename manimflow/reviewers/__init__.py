"""Stage-specific reviewers with domain expertise.

Each reviewer evaluates one stage of the pipeline using real domain knowledge
(not generic LLM judgment). They score, give specific feedback, and the
generator at that stage revises until the reviewer approves.

Architecture:
  story_reviewer.py     — Film/screenwriting knowledge
  design_reviewer.py    — Visual design principles (Gestalt, Tufte, color theory)
  animation_reviewer.py — Animation principles (12 principles, meaningful motion)
  layout_reviewer.py    — Composition and spatial design
  engagement_reviewer.py — Content retention and attention science
"""
