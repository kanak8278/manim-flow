"""Smoke tests — verify core modules load and basic logic works.

No LLM calls, no rendering, no API credits. Runs in seconds.
"""

import importlib
import subprocess
import sys

import pytest

# Check if manim is fully available (needs LaTeX, ffmpeg, etc.)
try:
    from manim import logger  # noqa: F401

    MANIM_AVAILABLE = True
except (ImportError, Exception):
    MANIM_AVAILABLE = False

needs_manim = pytest.mark.skipif(
    not MANIM_AVAILABLE, reason="manim not fully available"
)


# =========================================================================
# 1. CLI parses arguments correctly
# =========================================================================


class TestCLI:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from manimflow.cli import main; import sys; sys.argv = ['manimflow', '--help']; main()",
            ],
            capture_output=True,
            text=True,
        )
        # --help causes SystemExit(0), which may show as returncode 0
        # If deps aren't installed, we skip
        if "ModuleNotFoundError" in result.stderr:
            pytest.skip("runtime deps not installed")
        assert result.returncode == 0
        assert "manimflow" in (result.stdout + result.stderr).lower()

    def test_missing_topic_fails(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from manimflow.cli import main; import sys; sys.argv = ['manimflow']; main()",
            ],
            capture_output=True,
            text=True,
        )
        if "ModuleNotFoundError" in result.stderr:
            pytest.skip("runtime deps not installed")
        assert result.returncode != 0


# =========================================================================
# 2. Pure-python modules import without error
# =========================================================================


class TestImports:
    """Test modules that don't depend on manim at import time."""

    @pytest.mark.parametrize(
        "module",
        [
            "manimflow",
            "manimflow.knowledge.vocabulary",
            "manimflow.knowledge.search",
            "manimflow.production.code_sanitizer",
            "manimflow.reference.categories",
            "manimflow.reference.transitions",
            # topics.py imports from core.agent which needs anthropic
            # "manimflow.reference.topics",
            "manimflow.reference.platform",
        ],
    )
    def test_pure_module_imports(self, module):
        importlib.import_module(module)

    @needs_manim
    @pytest.mark.parametrize(
        "module",
        [
            "manimflow.cli",
            "manimflow.pipeline",
            "manimflow.core.agent",
            "manimflow.core.tracing",
            "manimflow.core.edge_tts_service",
            "manimflow.preproduction.writers_room",
            "manimflow.preproduction.design_system",
            "manimflow.preproduction.screenplay",
            "manimflow.preproduction.screenplay_validator",
            "manimflow.production.codegen",
            "manimflow.production.code_editor",
            "manimflow.production.renderer",
            "manimflow.production.scene_inspector",
            "manimflow.production.layout_checker",
            "manimflow.production.spatial_analyzer",
            "manimflow.production.wireframe",
            "manimflow.postproduction.evaluator",
            "manimflow.postproduction.voiceover",
            "manimflow.postproduction.music",
            "manimflow.postproduction.thumbnail",
            "manimflow.postproduction.timing",
            "manimflow.prompts.writers_room",
            "manimflow.prompts.design_system",
            "manimflow.prompts.screenplay",
            "manimflow.reference.domain_knowledge",
            "manimflow.reference.manim_reference",
        ],
    )
    def test_manim_module_imports(self, module):
        importlib.import_module(module)


# =========================================================================
# 3. Vocabulary loads with expected structure
# =========================================================================


class TestVocabulary:
    def test_all_categories_are_sets(self):
        from manimflow.knowledge.vocabulary import (
            DOMAINS,
            ELEMENTS,
            ANIMATIONS,
            LAYOUTS,
            TECHNIQUES,
            VISUAL_PURPOSE,
        )

        for name, vocab in [
            ("DOMAINS", DOMAINS),
            ("ELEMENTS", ELEMENTS),
            ("ANIMATIONS", ANIMATIONS),
            ("LAYOUTS", LAYOUTS),
            ("TECHNIQUES", TECHNIQUES),
            ("VISUAL_PURPOSE", VISUAL_PURPOSE),
        ]:
            assert isinstance(vocab, set), f"{name} should be a set"
            assert len(vocab) > 0, f"{name} should not be empty"

    def test_all_terms_combined(self):
        from manimflow.knowledge.vocabulary import ALL_TERMS, get_vocabulary_stats

        stats = get_vocabulary_stats()
        assert stats["total"] == len(ALL_TERMS)
        assert stats["total"] > 300

    def test_terms_are_lowercase_snake_case(self):
        import re

        from manimflow.knowledge.vocabulary import ALL_TERMS

        pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for term in ALL_TERMS:
            assert pattern.match(term), f"Term '{term}' is not lowercase snake_case"


# =========================================================================
# 4. Reference data is valid
# =========================================================================


class TestReferenceData:
    def test_categories_have_required_fields(self):
        from manimflow.reference.categories import CATEGORIES

        assert len(CATEGORIES) > 0
        for cat_id, cat in CATEGORIES.items():
            assert cat.id == cat_id
            assert cat.name
            assert cat.description
            assert len(cat.example_topics) > 0
            assert cat.recommended_duration > 0

    def test_suggest_category_returns_valid(self):
        from manimflow.reference.categories import suggest_category, CATEGORIES

        result = suggest_category("Why is 0.999... equal to 1?")
        assert result in CATEGORIES

        result = suggest_category("How does GPS work?")
        assert result in CATEGORIES

    def test_list_categories(self):
        from manimflow.reference.categories import list_categories

        cats = list_categories()
        assert len(cats) > 0
        for cat in cats:
            assert "id" in cat
            assert "name" in cat

    def test_transition_vocabulary_structure(self):
        from manimflow.reference.transitions import TRANSITION_VOCABULARY

        assert len(TRANSITION_VOCABULARY) > 0
        for name, t in TRANSITION_VOCABULARY.items():
            assert "description" in t
            assert "manim_code" in t
            assert "example" in t

    def test_transition_guide_generates(self):
        from manimflow.reference.transitions import get_transition_guide

        guide = get_transition_guide()
        assert "TRANSITION VOCABULARY" in guide
        assert len(guide) > 100


# =========================================================================
# 5. Code sanitizer catches known patterns
# =========================================================================


class TestCodeSanitizer:
    def test_fixes_invalid_rate_functions(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = "from manim import *\nself.play(FadeIn(obj), rate_func=ease_in_cubic, run_time=1)"
        fixed, fixes = sanitize_code(code)
        assert "ease_in_cubic" not in fixed
        assert "smooth" in fixed
        assert len(fixes) > 0

    def test_fixes_position_constants(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = "from manim import *\nobj.move_to(CENTER)"
        fixed, fixes = sanitize_code(code)
        assert "ORIGIN" in fixed

    def test_fixes_corner_access(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = "from manim import *\npos = rect.bottom_right"
        fixed, fixes = sanitize_code(code)
        assert "get_corner(DR)" in fixed

    def test_replaces_gtts_with_edge_tts(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = (
            "from manim import *\nfrom manim_voiceover.services.gtts import GTTSService"
        )
        fixed, fixes = sanitize_code(code)
        assert "EdgeTTSService" in fixed
        assert "GTTSService" not in fixed

    def test_adds_missing_imports(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = "class MyScene(Scene):\n    def construct(self):\n        c = Circle()"
        fixed, fixes = sanitize_code(code)
        assert "from manim import" in fixed

    def test_converts_mathtex_to_text(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = 'from manim import *\neq = MathTex("\\\\pi r^2")'
        fixed, fixes = sanitize_code(code)
        assert "MathTex" not in fixed
        assert "Text(" in fixed

    def test_guards_empty_mobjects(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = "from manim import *\nself.play(*[FadeOut(m) for m in self.mobjects])"
        fixed, fixes = sanitize_code(code)
        assert "if self.mobjects" in fixed

    def test_clean_code_passes_through(self):
        from manimflow.production.code_sanitizer import sanitize_code

        code = (
            "from manim import *\n"
            "import numpy as np\n\n"
            "class MyScene(Scene):\n"
            "    def construct(self):\n"
            "        c = Circle()\n"
            "        self.play(Create(c), run_time=1)\n"
        )
        fixed, fixes = sanitize_code(code)
        assert "from manim import" in fixed


# =========================================================================
# 6. Knowledge search handles empty/populated index
# =========================================================================


class TestKnowledgeSearch:
    def test_search_engine_initializes(self):
        from manimflow.knowledge.search import KnowledgeSearch

        ks = KnowledgeSearch()
        stats = ks.stats()
        assert "total_docs" in stats or "docs" in stats
        assert "total_patterns" in stats or "patterns" in stats

    def test_search_returns_list(self):
        from manimflow.knowledge.search import KnowledgeSearch

        ks = KnowledgeSearch()
        results = ks.search(query="fade in text")
        assert isinstance(results, list)

    def test_format_for_llm_returns_string(self):
        from manimflow.knowledge.search import KnowledgeSearch

        ks = KnowledgeSearch()
        results = ks.search(query="sorting algorithm")
        formatted = ks.format_for_llm(results)
        assert isinstance(formatted, str)
