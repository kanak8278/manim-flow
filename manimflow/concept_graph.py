"""Concept Graph — builds a knowledge graph for video planning.

Replaces flat story generation with structured concept analysis.
The graph drives: scene order, visual consistency, narration flow.

Based on Knowledge Space Theory (Doignon & Falmagne, 1985) and
ConceptNet relationship types.
"""

from dataclasses import dataclass, field, asdict
from .llm import call_llm, extract_json


@dataclass
class ConceptNode:
    """A single concept in the knowledge graph."""
    id: str
    label: str
    type: str  # concept, formula, constant, metaphor, misconception, example, application
    description: str = ""
    visual_intuition: str = ""  # how to SHOW this (not explain in words)
    difficulty: float = 0.5  # 0=trivial, 1=advanced
    is_target: bool = False  # is this the main concept being explained?
    is_assumed: bool = False  # do we assume the audience already knows this?


@dataclass
class ConceptEdge:
    """A relationship between two concepts."""
    source: str  # concept id
    target: str  # concept id
    relation: str  # requires, explains, uses, contradicts, leads_to, transforms_into
    label: str = ""  # human-readable description of the relationship


@dataclass
class ConceptGraph:
    """The full knowledge graph for a video topic."""
    topic: str
    target_concept: str  # the main concept being explained
    nodes: dict[str, ConceptNode] = field(default_factory=dict)
    edges: list[ConceptEdge] = field(default_factory=list)
    teaching_order: list[str] = field(default_factory=list)  # topologically sorted concept ids
    key_insight: str = ""  # the "aha" moment
    misconceptions: list[str] = field(default_factory=list)

    def get_prerequisites(self, concept_id: str) -> list[str]:
        """Get all direct prerequisites of a concept."""
        return [e.source for e in self.edges
                if e.target == concept_id and e.relation == "requires"]

    def get_novel_concepts(self) -> list[str]:
        """Get concepts that need to be taught (not assumed known)."""
        return [nid for nid, n in self.nodes.items() if not n.is_assumed]

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "target_concept": self.target_concept,
            "nodes": {k: asdict(v) for k, v in self.nodes.items()},
            "edges": [asdict(e) for e in self.edges],
            "teaching_order": self.teaching_order,
            "key_insight": self.key_insight,
            "misconceptions": self.misconceptions,
        }


GRAPH_PROMPT = """You are an expert educational content designer. Given a topic, build a knowledge graph
that maps out EVERY concept needed to explain it, their relationships, and the optimal teaching order.

Think like a great teacher:
- What does the learner ALREADY know? (mark as assumed)
- What MUST be introduced first? (prerequisites)
- What's the key INSIGHT that makes it click? (the aha moment)
- What MISCONCEPTIONS might the learner have? (address them)
- How can each concept be SHOWN visually? (not just explained in words)

For the visual_intuition field, describe what VISUAL ELEMENT represents this concept:
- NOT "explain that pi is the ratio" → "show a circle unrolling into a line 3.14x its diameter"
- NOT "demonstrate the formula" → "animate slicing a circle into rings that flatten into a triangle"
Think in terms of shapes, motion, transformation, comparison — what would you DRAW?

Return JSON:
{
  "target_concept": "concept_id of the main thing being explained",
  "key_insight": "the single aha moment that makes everything click",
  "misconceptions": ["common wrong ideas to address"],
  "nodes": [
    {
      "id": "short_snake_case_id",
      "label": "Human Readable Name",
      "type": "concept|formula|constant|metaphor|misconception|example|application",
      "description": "what this concept IS",
      "visual_intuition": "how to SHOW this visually (shapes, motion, transformation)",
      "difficulty": 0.3,
      "is_target": false,
      "is_assumed": false
    }
  ],
  "edges": [
    {
      "source": "concept_a",
      "target": "concept_b",
      "relation": "requires|explains|uses|contradicts|leads_to|transforms_into",
      "label": "human readable description"
    }
  ],
  "teaching_order": ["concept_id_1", "concept_id_2", "..."]
}

The teaching_order must be a valid topological sort: no concept appears before its prerequisites.
Include 5-12 concepts (not too few, not too many for a single video)."""


def build_concept_graph(topic: str, audience: str = "general") -> ConceptGraph:
    """Build a concept graph from a topic description."""
    user_prompt = (
        f"Build a knowledge graph for this educational video topic:\n\n"
        f"TOPIC: {topic}\n"
        f"AUDIENCE: {audience} (what they likely already know)\n\n"
        f"Return ONLY valid JSON."
    )

    response = call_llm(GRAPH_PROMPT, user_prompt)
    data = extract_json(response)

    # Build the graph
    graph = ConceptGraph(
        topic=topic,
        target_concept=data.get("target_concept", ""),
        key_insight=data.get("key_insight", ""),
        misconceptions=data.get("misconceptions", []),
    )

    for node_data in data.get("nodes", []):
        node = ConceptNode(
            id=node_data["id"],
            label=node_data.get("label", node_data["id"]),
            type=node_data.get("type", "concept"),
            description=node_data.get("description", ""),
            visual_intuition=node_data.get("visual_intuition", ""),
            difficulty=node_data.get("difficulty", 0.5),
            is_target=node_data.get("is_target", False),
            is_assumed=node_data.get("is_assumed", False),
        )
        graph.nodes[node.id] = node

    for edge_data in data.get("edges", []):
        edge = ConceptEdge(
            source=edge_data["source"],
            target=edge_data["target"],
            relation=edge_data.get("relation", "requires"),
            label=edge_data.get("label", ""),
        )
        graph.edges.append(edge)

    graph.teaching_order = data.get("teaching_order", list(graph.nodes.keys()))

    return graph


def print_concept_graph(graph: ConceptGraph):
    """Pretty-print a concept graph."""
    print(f"\n--- Concept Graph: {graph.topic} ---")
    print(f"Target: {graph.target_concept}")
    print(f"Key insight: {graph.key_insight}")
    if graph.misconceptions:
        print(f"Misconceptions: {', '.join(graph.misconceptions)}")

    print(f"\nConcepts ({len(graph.nodes)}):")
    for cid in graph.teaching_order:
        node = graph.nodes.get(cid)
        if not node:
            continue
        assumed = " [assumed]" if node.is_assumed else ""
        target = " [TARGET]" if node.is_target else ""
        print(f"  {node.id:25s} ({node.type:12s}){assumed}{target}")
        if node.visual_intuition:
            print(f"  {'':25s} Visual: {node.visual_intuition[:70]}")

    print(f"\nRelationships ({len(graph.edges)}):")
    for edge in graph.edges:
        print(f"  {edge.source} --[{edge.relation}]--> {edge.target}")
        if edge.label:
            print(f"  {'':25s} {edge.label}")

    print(f"\nTeaching order: {' → '.join(graph.teaching_order)}")
