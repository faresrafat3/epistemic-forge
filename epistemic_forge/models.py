"""Core data models for Epistemic Forge."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Domain(str, Enum):
    RESEARCH = "research"
    PHILOSOPHY = "philosophy"
    WRITING = "writing"
    FREELANCE = "freelance"
    KAGGLE = "kaggle"
    HYBRID = "hybrid"


class Confidence(str, Enum):
    SURE = "sure"
    LIKELY = "likely"
    POSSIBLE = "possible"
    WEAK = "weak"


@dataclass
class ProjectSpec:
    """User-facing project request."""

    title: str
    question: str
    domain: Domain = Domain.HYBRID
    audience: str = "technical peer / client"
    constraints: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    budget_tokens: int = 8000
    max_trials: int = 3
    enable_opro_style: bool = True
    enable_skills: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["domain"] = self.domain.value
        return d


@dataclass
class Claim:
    """Atomic epistemic unit."""

    id: str
    text: str
    support: List[str] = field(default_factory=list)
    objections: List[str] = field(default_factory=list)
    confidence: Confidence = Confidence.LIKELY
    sources: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["confidence"] = self.confidence.value
        return d


@dataclass
class RouteDecision:
    """L0 router output."""

    families: List[str]
    activate: Dict[str, bool]
    rationale: str
    l1_mode: str = "ape"  # ape | opro | cascade | off
    l3_mode: str = "tot"  # tot | lats | cascade | off

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SearchNode:
    """L3 deliberate-search node."""

    id: str
    thought: str
    value: float
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Reflection:
    """L5 verbal memory unit (Reflexion-style)."""

    trial: int
    failure_summary: str
    lesson: str
    next_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Skill:
    """L5 procedural memory unit (Voyager-style)."""

    name: str
    description: str
    code: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StageArtifact:
    name: str
    content: str
    kind: str  # markdown | python | json | notebook-md
    path_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ForgeResult:
    """Full pipeline output."""

    spec: ProjectSpec
    route: RouteDecision
    instruction: str
    claims: List[Claim]
    search_trace: List[SearchNode]
    reflections: List[Reflection]
    skills_used: List[str]
    artifacts: List[StageArtifact]
    peer_review: Dict[str, Any]
    trial_log: List[Dict[str, Any]] = field(default_factory=list)
    final_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec.to_dict(),
            "route": self.route.to_dict(),
            "instruction": self.instruction,
            "claims": [c.to_dict() for c in self.claims],
            "search_trace": [n.to_dict() for n in self.search_trace],
            "reflections": [r.to_dict() for r in self.reflections],
            "skills_used": self.skills_used,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "peer_review": self.peer_review,
            "trial_log": self.trial_log,
            "final_score": self.final_score,
        }
