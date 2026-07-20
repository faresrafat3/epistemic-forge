"""Core data models for Epistemic Forge."""

from __future__ import annotations

from pydantic import BaseModel, Field
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


class ProjectSpec(BaseModel):
    """User-facing project request."""

    title: str
    question: str
    domain: Domain = Domain.HYBRID
    audience: str = "technical peer / client"
    constraints: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    budget_tokens: int = 8000
    max_trials: int = 3
    enable_opro_style: bool = True
    enable_skills: bool = True



class Claim(BaseModel):
    """Atomic epistemic unit."""

    id: str
    text: str
    support: List[str] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.LIKELY
    sources: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)



class RouteDecision(BaseModel):
    """L0 router output."""

    families: List[str]
    activate: Dict[str, bool]
    rationale: str
    l1_mode: str = "ape"  # ape | opro | cascade | off
    l3_mode: str = "tot"  # tot | lats | cascade | off



class SearchNode(BaseModel):
    """L3 deliberate-search node."""

    id: str
    thought: str
    value: float
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)



class Reflection(BaseModel):
    """L5 verbal memory unit (Reflexion-style)."""

    trial: int
    failure_summary: str
    lesson: str
    next_action: str



class Skill(BaseModel):
    """L5 procedural memory unit (Voyager-style)."""

    name: str
    description: str
    code: str
    tags: List[str] = Field(default_factory=list)



class StageArtifact(BaseModel):
    name: str
    content: str
    kind: str  # markdown | python | json | notebook-md
    path_hint: str = ""



class ForgeResult(BaseModel):
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
    trial_log: List[Dict[str, Any]] = Field(default_factory=list)
    final_score: float = 0.0

