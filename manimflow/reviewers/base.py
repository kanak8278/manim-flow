"""Base reviewer class — all domain-specific reviewers extend this."""

from dataclasses import dataclass, field
from ..llm import call_llm, extract_json


@dataclass
class ReviewResult:
    """Standard result from any reviewer."""
    stage: str              # which stage this reviews
    score: float            # 1-10
    verdict: str            # "approve", "revise", "reject"
    strengths: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)    # specific, actionable
    domain_notes: str = ""  # expert perspective


class BaseReviewer:
    """Base class for domain-specific reviewers."""

    stage_name: str = "base"
    domain_knowledge: str = ""  # Injected expertise from research

    def review(self, artifact: dict, context: dict = None) -> ReviewResult:
        """Review an artifact from this pipeline stage."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(artifact, context or {})

        response = call_llm(system_prompt, user_prompt)
        data = extract_json(response)

        return ReviewResult(
            stage=self.stage_name,
            score=data.get("score", 5),
            verdict=data.get("verdict", "revise"),
            strengths=data.get("strengths", []),
            issues=data.get("issues", []),
            fixes=data.get("fixes", []),
            domain_notes=data.get("domain_notes", ""),
        )

    def _build_system_prompt(self) -> str:
        return (
            f"You are a {self.stage_name} reviewer with deep domain expertise.\n\n"
            f"DOMAIN KNOWLEDGE:\n{self.domain_knowledge}\n\n"
            f"Review the artifact and return JSON:\n"
            f'{{"score": 7.5, "verdict": "approve|revise|reject", '
            f'"strengths": ["..."], "issues": ["..."], '
            f'"fixes": ["specific actionable fix 1", "..."], '
            f'"domain_notes": "expert perspective on what could be better"}}\n\n'
            f"Score >= 7.5 = approve. 5-7.5 = revise. < 5 = reject.\n"
            f"Every issue MUST have a corresponding fix. No vague feedback."
        )

    def _build_user_prompt(self, artifact: dict, context: dict) -> str:
        raise NotImplementedError


def print_review(result: ReviewResult):
    """Pretty-print a review result."""
    marker = {"approve": "PASS", "revise": "REVISE", "reject": "REJECT"}.get(result.verdict, "?")
    print(f"\n--- {result.stage} Review [{marker}] {result.score}/10 ---")
    for s in result.strengths[:3]:
        print(f"  [+] {s}")
    for i in result.issues[:3]:
        print(f"  [-] {i}")
    for f in result.fixes[:3]:
        print(f"  [fix] {f}")
    if result.domain_notes:
        print(f"  [expert] {result.domain_notes[:100]}")
