"""Knowledge base search engine for ManimFlow.

Multi-field BM25 search over scene documentation. The LLM calls this
as a tool — it decides when to search and what to search for.

Each MD document has multiple fields (tags, pattern names, when_to_use,
summary, visual approach, scene flow, code). BM25 runs independently
on each field, then scores are combined with field-specific weights.

Usage:
    from manimflow.knowledge.search import KnowledgeSearch, search_knowledge

    ks = KnowledgeSearch()
    results = ks.search(query="arc swap sorting", domain=["sorting"])
    print(ks.format_for_llm(results))

    # Or use the tool function directly:
    print(search_knowledge(query="dynamic line updating", techniques=["value_tracker"]))
"""

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Pattern:
    """A single visual pattern extracted from a scene document."""
    name: str
    what: str
    when_to_use: str
    code: str
    source_line: str


@dataclass
class SceneDoc:
    """A parsed scene documentation file."""
    file: str
    source: str
    project: str
    summary: str
    design_decisions: str
    composition: str
    color_styling: str
    timing: str
    scene_flow: str

    domain: list[str] = field(default_factory=list)
    elements: list[str] = field(default_factory=list)
    animations: list[str] = field(default_factory=list)
    layouts: list[str] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    purpose: list[str] = field(default_factory=list)
    mobjects: list[str] = field(default_factory=list)
    manim_animations: list[str] = field(default_factory=list)
    patterns: list[Pattern] = field(default_factory=list)

    def all_tags(self) -> list[str]:
        return (
            self.domain + self.elements + self.animations +
            self.layouts + self.techniques + self.purpose
        )

    def tag_set(self, field_name: str) -> set[str]:
        return set(getattr(self, field_name, []))


@dataclass
class SearchResult:
    """A search result returned to the LLM."""
    file: str
    source: str
    project: str
    score: float
    summary: str
    matched_patterns: list[Pattern]
    matched_tags: list[str]
    field_scores: dict  # field_name → score (for debugging)


# ---------------------------------------------------------------------------
# BM25 Engine
# ---------------------------------------------------------------------------

class BM25Field:
    """BM25 index for a single field across all documents.

    BM25 scoring: for each query term in a document field,
      score = IDF × (tf × (k1 + 1)) / (tf + k1 × (1 - b + b × dl/avgdl))

    Where:
      tf    = term frequency in this document's field
      dl    = document field length (word count)
      avgdl = average field length across all docs
      IDF   = log((N - df + 0.5) / (df + 0.5) + 1)
      N     = total documents
      df    = documents containing this term
      k1    = term frequency saturation (1.5 default)
      b     = length normalization (0.75 default)
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_dl = 0.0
        self.doc_freqs: dict[str, int] = {}       # term → num docs containing it
        self.doc_term_freqs: list[Counter] = []    # per-doc term frequencies
        self.doc_lengths: list[int] = []           # per-doc field lengths

    def add_document(self, doc_idx: int, text: str):
        """Index a document's field text."""
        tokens = _tokenize_for_index(text)
        tf = Counter(tokens)

        # Extend lists if needed
        while len(self.doc_term_freqs) <= doc_idx:
            self.doc_term_freqs.append(Counter())
            self.doc_lengths.append(0)

        self.doc_term_freqs[doc_idx] = tf
        self.doc_lengths[doc_idx] = len(tokens)

        for term in set(tokens):
            self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

    def finalize(self, total_docs: int):
        """Compute average document length after all docs are indexed."""
        self.doc_count = total_docs
        total_len = sum(self.doc_lengths)
        self.avg_dl = total_len / total_docs if total_docs > 0 else 1.0

    def score(self, doc_idx: int, query_tokens: list[str]) -> float:
        """Compute BM25 score for a query against one document."""
        if doc_idx >= len(self.doc_term_freqs):
            return 0.0

        tf_map = self.doc_term_freqs[doc_idx]
        dl = self.doc_lengths[doc_idx]
        total = 0.0

        for term in query_tokens:
            tf = tf_map.get(term, 0)
            if tf == 0:
                continue

            df = self.doc_freqs.get(term, 0)
            # IDF with floor to avoid negative scores
            idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1.0)

            # BM25 term score
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
            total += idf * numerator / denominator

        return total


# ---------------------------------------------------------------------------
# Multi-Field Search Engine
# ---------------------------------------------------------------------------

# Field definitions: name → (weight, description)
FIELD_WEIGHTS = {
    "tags":           5.0,   # Controlled vocabulary tags — highest intent signal
    "pattern_names":  4.0,   # Curated pattern names like "Arc-Based Swap"
    "when_to_use":    3.0,   # Intent descriptions — closest to LLM query language
    "summary":        2.0,   # Natural language overview
    "design":         2.0,   # Design decisions — WHY choices were made
    "composition":    1.5,   # Spatial layout, positions, sizes, spacing
    "color_styling":  1.5,   # Colors, opacity, fonts, visual styling
    "timing":         1.0,   # Animation durations, run_time values
    "scene_flow":     1.0,   # Step-by-step narrative structure
    "code":           0.5,   # Catches method/class names but noisy
    "manim_classes":  1.0,   # Manim mobject and animation class names
}


class KnowledgeSearch:
    """Multi-field BM25 search over the ManimFlow knowledge base."""

    def __init__(self, scenes_dir: str = None):
        if scenes_dir is None:
            scenes_dir = os.path.join(os.path.dirname(__file__), "scenes")
        self.scenes_dir = scenes_dir
        self.docs: list[SceneDoc] = []
        self.fields: dict[str, BM25Field] = {}
        self._build_index()

    def _build_index(self):
        """Load all .md files and build BM25 indices per field."""
        if not os.path.isdir(self.scenes_dir):
            return

        # Load documents
        for fname in sorted(os.listdir(self.scenes_dir)):
            if not fname.endswith(".md"):
                continue
            doc = self._parse_md(os.path.join(self.scenes_dir, fname), fname)
            if doc:
                self.docs.append(doc)

        if not self.docs:
            return

        # Initialize BM25 fields
        for field_name in FIELD_WEIGHTS:
            self.fields[field_name] = BM25Field()

        # Index each document into each field
        for idx, doc in enumerate(self.docs):
            field_texts = self._extract_field_texts(doc)
            for field_name, text in field_texts.items():
                self.fields[field_name].add_document(idx, text)

        # Finalize (compute avgdl)
        for bm25 in self.fields.values():
            bm25.finalize(len(self.docs))

    def _extract_field_texts(self, doc: SceneDoc) -> dict[str, str]:
        """Extract searchable text for each field from a SceneDoc."""
        return {
            "tags": " ".join(doc.all_tags()),
            "pattern_names": " ".join(p.name for p in doc.patterns),
            "when_to_use": " ".join(p.when_to_use for p in doc.patterns),
            "summary": doc.summary,
            "design": doc.design_decisions,
            "composition": doc.composition,
            "color_styling": doc.color_styling,
            "timing": doc.timing,
            "scene_flow": doc.scene_flow,
            "code": " ".join(p.code for p in doc.patterns),
            "manim_classes": " ".join(doc.mobjects + doc.manim_animations),
        }

    # ------------------------------------------------------------------
    # Public API — this is the LLM tool
    # ------------------------------------------------------------------

    def search(
        self,
        query: str = None,
        domain: list[str] = None,
        elements: list[str] = None,
        animations: list[str] = None,
        layouts: list[str] = None,
        techniques: list[str] = None,
        purpose: list[str] = None,
        limit: int = 5,
    ) -> list[SearchResult]:
        """
        Search the knowledge base.

        Args:
            query: Free text search (natural language or keywords)
            domain: Filter by topic domain tags
            elements: Filter by visual element tags
            animations: Filter by animation type tags
            layouts: Filter by layout pattern tags
            techniques: Filter by Manim technique tags
            purpose: Filter by visual purpose tags
            limit: Max results to return

        Returns:
            Ranked list of SearchResult objects
        """
        if not self.docs:
            return []

        # Combine all inputs into query tokens
        all_query_parts = []
        if query:
            all_query_parts.append(query)

        # Structured tags become additional query terms
        tag_terms = []
        for vals in [domain, elements, animations, layouts, techniques, purpose]:
            if vals:
                tag_terms.extend(vals)

        if tag_terms:
            all_query_parts.append(" ".join(tag_terms))

        if not all_query_parts:
            return []

        combined_query = " ".join(all_query_parts)
        query_tokens = _tokenize_for_query(combined_query)

        if not query_tokens:
            return []

        # Score each document across all fields
        results = []
        for idx, doc in enumerate(self.docs):
            total_score = 0.0
            field_scores = {}
            matched_tags = []

            for field_name, bm25 in self.fields.items():
                weight = FIELD_WEIGHTS[field_name]
                raw_score = bm25.score(idx, query_tokens)
                weighted = raw_score * weight
                field_scores[field_name] = round(weighted, 2)
                total_score += weighted

            # Bonus: exact tag filter match
            # When LLM passes structured tags, exact matches in the
            # corresponding field get an extra boost
            tag_filters = {
                "domain": domain, "elements": elements,
                "animations": animations, "layouts": layouts,
                "techniques": techniques, "purpose": purpose,
            }
            for field_name, filter_vals in tag_filters.items():
                if not filter_vals:
                    continue
                doc_tags = doc.tag_set(field_name)
                for tag in filter_vals:
                    if tag in doc_tags:
                        total_score += 10  # Strong bonus for exact tag match
                        matched_tags.append(f"{field_name}:{tag}")

            if total_score > 0:
                # Find which patterns matched
                matched_patterns = self._match_patterns(doc, query_tokens)

                results.append(SearchResult(
                    file=doc.file,
                    source=doc.source,
                    project=doc.project,
                    score=total_score,
                    summary=doc.summary[:300],
                    matched_patterns=matched_patterns,
                    matched_tags=matched_tags,
                    field_scores=field_scores,
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def _match_patterns(self, doc: SceneDoc, tokens: list[str]) -> list[Pattern]:
        """Find which patterns in a doc are most relevant to the query."""
        scored = []
        for p in doc.patterns:
            s = 0
            searchable = (p.name + " " + p.when_to_use + " " + p.what).lower()
            for t in tokens:
                if t in searchable:
                    s += 1
            scored.append((s, p))

        scored.sort(key=lambda x: -x[0])

        # Return patterns that matched, or all if none specifically matched
        matched = [p for s, p in scored if s > 0]
        return matched if matched else doc.patterns

    def format_for_llm(
        self,
        results: list[SearchResult],
        include_code: bool = True,
        max_patterns: int = 3,
    ) -> str:
        """Format results as text for LLM consumption."""
        if not results:
            return "No relevant patterns found in knowledge base."

        parts = []
        for r in results:
            lines = [
                f"## {r.file} (relevance: {r.score:.1f})",
                f"Source: `{r.source}`",
            ]
            if r.matched_tags:
                lines.append(f"Matched tags: {', '.join(r.matched_tags)}")
            lines.append(f"Summary: {r.summary}")
            lines.append("")

            for p in r.matched_patterns[:max_patterns]:
                lines.append(f"### {p.name}")
                if p.when_to_use:
                    lines.append(f"When to use: {p.when_to_use}")
                if include_code and p.code:
                    lines.append(f"```python\n{p.code}\n```")
                lines.append("")

            parts.append("\n".join(lines))

        return "\n---\n\n".join(parts)

    def format_debug(self, results: list[SearchResult]) -> str:
        """Format with field-level score breakdown for debugging."""
        lines = []
        for r in results:
            lines.append(f"{r.file} (total={r.score:.1f})")
            for fname, fscore in sorted(r.field_scores.items(), key=lambda x: -x[1]):
                if fscore > 0:
                    lines.append(f"  {fname:20s} → {fscore:.2f} (weight={FIELD_WEIGHTS[fname]}x)")
            if r.matched_tags:
                lines.append(f"  {'exact_tag_bonus':20s} → {', '.join(r.matched_tags)}")
            pats = ", ".join(p.name for p in r.matched_patterns[:3])
            lines.append(f"  Patterns: {pats}")
            lines.append("")
        return "\n".join(lines)

    def get_tool_description(self) -> str:
        """Return the tool description to include in LLM system prompt."""
        from .vocabulary import DOMAINS, ELEMENTS, ANIMATIONS, LAYOUTS, TECHNIQUES, VISUAL_PURPOSE

        def top(s, n=15):
            return ", ".join(sorted(s)[:n]) + ", ..."

        return f"""## Knowledge Base Search Tool

You have access to a knowledge base of {len(self.docs)} real Manim video examples
with {sum(len(d.patterns) for d in self.docs)} tested code patterns extracted from
production YouTube channels (3Blue1Brown, Reducible, vcubingx, and others).

Call `search_knowledge()` when you need:
- Visual pattern examples (how to animate a swap, show a hierarchy, etc.)
- Working Manim code snippets for specific techniques
- Layout and composition references
- Domain-specific visualization approaches

### Parameters (all optional, combine freely):

- **query** (str): Free text search. Use natural language.
  Examples: "arc swap sorting", "dynamic line updating with value tracker",
  "pipeline stages connected by arrows", "show a hierarchy of concepts"

- **domain** (list[str]): Filter by topic domain.
  Values: {top(DOMAINS)}

- **elements** (list[str]): Filter by visual elements needed.
  Values: {top(ELEMENTS)}

- **animations** (list[str]): Filter by animation types.
  Values: {top(ANIMATIONS)}

- **layouts** (list[str]): Filter by layout pattern.
  Values: {top(LAYOUTS)}

- **techniques** (list[str]): Filter by Manim technique.
  Values: {top(TECHNIQUES)}

- **purpose** (list[str]): Filter by visual purpose.
  Values: {top(VISUAL_PURPOSE)}

### Example calls:
```
search_knowledge(query="swap elements sorting", domain=["sorting"])
search_knowledge(techniques=["value_tracker", "always_redraw"])
search_knowledge(query="compare two approaches", layouts=["side_by_side"])
search_knowledge(elements=["pipeline", "arrow"], purpose=["process"])
search_knowledge(query="how to show a hierarchy with cards and arrows")
```
"""

    def stats(self) -> dict:
        field_stats = {}
        for fname, bm25 in self.fields.items():
            field_stats[fname] = {
                "unique_terms": len(bm25.doc_freqs),
                "avg_length": round(bm25.avg_dl, 1),
            }
        return {
            "total_docs": len(self.docs),
            "total_patterns": sum(len(d.patterns) for d in self.docs),
            "fields": field_stats,
        }

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_md(self, path: str, fname: str) -> SceneDoc | None:
        try:
            with open(path) as f:
                content = f.read()
        except Exception:
            return None

        fm = {}
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                for line in content[3:end].strip().split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key, val = key.strip(), val.strip()
                        if val.startswith("[") and val.endswith("]"):
                            val = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
                        fm[key] = val
                content = content[end + 3:].strip()

        def tags(key):
            v = fm.get(key, [])
            return v if isinstance(v, list) else []

        return SceneDoc(
            file=fname, source=fm.get("source", ""),
            project=fm.get("project", ""),
            summary=self._section(content, "## Summary"),
            design_decisions=self._section(content, "## Design Decisions"),
            composition=self._section(content, "## Composition"),
            color_styling=self._section(content, "## Color and Styling"),
            timing=self._section(content, "## Timing"),
            scene_flow=self._section(content, "## Scene Flow"),
            domain=tags("domain"), elements=tags("elements"),
            animations=tags("animations"), layouts=tags("layouts"),
            techniques=tags("techniques"), purpose=tags("purpose"),
            mobjects=tags("mobjects"), manim_animations=tags("manim_animations"),
            patterns=self._patterns(content),
        )

    def _section(self, content: str, heading: str) -> str:
        start = content.find(heading)
        if start < 0:
            return ""
        start += len(heading)
        end = content.find("\n## ", start)
        return (content[start:end] if end > 0 else content[start:]).strip()

    def _patterns(self, content: str) -> list[Pattern]:
        results = []
        regex = re.compile(r'### Pattern:\s*(.+?)(?=\n)')
        matches = list(regex.finditer(content))
        for i, m in enumerate(matches):
            name = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else (
                content.find("\n## ", start) if content.find("\n## ", start) > 0 else len(content)
            )
            block = content[start:end]
            what_m = re.search(r'\*\*What\*\*:\s*(.+)', block)
            when_m = re.search(r'\*\*When to use\*\*:\s*(.+)', block)
            code_m = re.search(r'```python\n(.+?)```', block, re.DOTALL)
            src_m = re.search(r'# Source:\s*(.+)', block)
            results.append(Pattern(
                name=name,
                what=what_m.group(1).strip() if what_m else "",
                when_to_use=when_m.group(1).strip() if when_m else "",
                code=code_m.group(1).strip() if code_m else "",
                source_line=src_m.group(1).strip() if src_m else "",
            ))
        return results


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

_STOP_WORDS = {
    "a", "an", "the", "is", "to", "for", "in", "of", "and",
    "or", "with", "how", "do", "i", "my", "it", "on", "at",
    "that", "this", "can", "should", "need", "want", "use",
    "show", "make", "create", "using", "like", "from", "be",
    "any", "each", "all", "when", "where", "what", "which",
    "are", "was", "were", "been", "being", "have", "has",
    "but", "not", "so", "if", "then", "than", "no", "by",
}


def _tokenize_for_index(text: str) -> list[str]:
    """Tokenize document text for BM25 indexing.

    Preserves underscored terms (value_tracker) and generates
    both the compound form and individual words.
    """
    text = text.lower()
    words = re.findall(r'[a-z0-9_]+', text)
    tokens = []
    for w in words:
        if w in _STOP_WORDS or len(w) <= 1:
            continue
        tokens.append(w)
        # If word has underscore, also index individual parts
        # "value_tracker" → also index "value", "tracker"
        if "_" in w:
            for part in w.split("_"):
                if part and part not in _STOP_WORDS and len(part) > 1:
                    tokens.append(part)
    return tokens


def _tokenize_for_query(query: str) -> list[str]:
    """Tokenize a query string.

    Generates individual words, underscore-joined bigrams,
    and splits any underscored terms into parts.
    """
    query = query.lower()
    words = re.findall(r'[a-z0-9_]+', query)
    clean = [w for w in words if w not in _STOP_WORDS and len(w) > 1]

    tokens = list(clean)

    # Bigrams: "machine learning" → "machine_learning"
    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        if a not in _STOP_WORDS and b not in _STOP_WORDS and len(a) > 1 and len(b) > 1:
            tokens.append(f"{a}_{b}")

    # Split underscored terms: "value_tracker" → "value", "tracker"
    for w in clean:
        if "_" in w:
            for part in w.split("_"):
                if part and part not in _STOP_WORDS and len(part) > 1:
                    tokens.append(part)

    return tokens


# ---------------------------------------------------------------------------
# Module-level tool function
# ---------------------------------------------------------------------------

_instance: KnowledgeSearch | None = None


def get_search() -> KnowledgeSearch:
    global _instance
    if _instance is None:
        _instance = KnowledgeSearch()
    return _instance


def search_knowledge(
    query: str = None,
    domain: list[str] = None,
    elements: list[str] = None,
    animations: list[str] = None,
    layouts: list[str] = None,
    techniques: list[str] = None,
    purpose: list[str] = None,
    limit: int = 5,
) -> str:
    """
    LLM tool function. Returns formatted text with matched patterns and code.
    """
    ks = get_search()
    results = ks.search(
        query=query, domain=domain, elements=elements,
        animations=animations, layouts=layouts,
        techniques=techniques, purpose=purpose, limit=limit,
    )
    return ks.format_for_llm(results)


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ks = KnowledgeSearch()
    print(f"Index stats: {ks.stats()}\n")

    # Test suite
    tests = [
        # (kwargs, expected_top_file, description)
        (dict(query="swap elements", domain=["sorting"]),
         "bubble_sort.md", "structured + text"),
        (dict(query="dynamic updating line plot", techniques=["value_tracker"]),
         "linear_regression.md", "technique filter + text"),
        (dict(query="compare approaches", layouts=["side_by_side"]),
         "deepseek_r1.md", "layout filter + text"),
        (dict(elements=["pipeline", "arrow"], purpose=["process"]),
         "deepseek_r1.md", "pure structured tags"),
        (dict(domain=["machine_learning"]),
         "linear_regression.md OR deepseek_r1.md", "domain only"),
        (dict(domain=["sorting"]),
         "bubble_sort.md", "domain only"),

        # Free text queries
        (dict(query="swap two elements sorting animation"),
         "bubble_sort.md", "text: swap sorting"),
        (dict(query="value_tracker always_redraw dynamic line"),
         "linear_regression.md", "text: value_tracker"),
        (dict(query="pipeline flow diagram arrows stages"),
         "deepseek_r1.md", "text: pipeline"),
        (dict(query="highlight current element algorithm"),
         "bubble_sort.md", "text: highlight algorithm"),
        (dict(query="bar chart benchmark performance"),
         "deepseek_r1.md", "text: bar chart"),
        (dict(query="scatter plot data points"),
         "linear_regression.md", "text: scatter plot"),
        (dict(query="equation formula emphasis box"),
         "deepseek_r1.md", "text: equation box"),
        (dict(query="training progress machine learning"),
         "linear_regression.md", "text: training ML"),
        (dict(query="step by step algorithm walkthrough"),
         "bubble_sort.md", "text: step by step"),
        (dict(query="research paper explainer multiple sections"),
         "deepseek_r1.md", "text: paper explainer"),

        # Mixed
        (dict(query="training progress line", domain=["machine_learning"]),
         "linear_regression.md", "mixed: training + ML domain"),
        (dict(query="step by step walkthrough", domain=["algorithms"]),
         "bubble_sort.md", "mixed: walkthrough + algorithms"),
    ]

    correct = 0
    for kwargs, expected, desc in tests:
        results = ks.search(**kwargs, limit=1)
        if results:
            top = results[0].file
            ok = any(e.strip() in top for e in expected.split(" OR "))
            if ok:
                correct += 1
            status = "OK" if ok else "WRONG"
            print(f"  {status}: [{desc}] → {top} (score={results[0].score:.1f})")
            if not ok:
                print(f"        Expected: {expected}")
                print(f"        Debug:\n{ks.format_debug(results[:2])}")
        else:
            print(f"  MISS: [{desc}] → No results (expected {expected})")

    print(f"\nAccuracy: {correct}/{len(tests)} ({100*correct/len(tests):.0f}%)")

    # Show detailed score breakdown for one query
    print("\n=== Score breakdown: 'swap elements sorting' ===\n")
    results = ks.search(query="swap elements sorting")
    print(ks.format_debug(results))
