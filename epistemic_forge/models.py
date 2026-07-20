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
    
    # Hermes Universal Routing Overrides
    target_model: str = "gpt-4o-mini"
    api_base: str = None
    api_key: str = None



class Claim(BaseModel):
    """Atomic epistemic unit with absolute grounding."""
    id: str = Field(description="Unique identifier, e.g., C1")
    text: str = Field(description="The core claim or premise.")
    epistemic_warrant: str = Field(description="MANDATORY: The exact logical deduction, explanation, or evidence that proves this claim. NO UNSUBSTANTIATED CLAIMS.")
    potential_falsifier: str = Field(description="What specific evidence or scenario would prove this claim wrong?")
    support: List[str] = Field(default_factory=list, description="Sub-arguments supporting this claim.")
    objections: List[str] = Field(default_factory=list, description="Valid counter-arguments against this claim.")
    confidence: Confidence = Field(default=Confidence.LIKELY)



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


# ==========================================
# NEURO-SYMBOLIC EXPERT SCHEMAS (L2)
# Enforcing deterministic outputs from LLMs
# ==========================================

class KaggleExpertOutput(BaseModel):
    """Strict schema for the Kaggle Expert to prevent hallucinations."""
    leakage_risk_score: float = Field(ge=0.0, le=1.0, description="Risk of data leakage in the proposed approach.")
    validation_strategy: str = Field(description="Strict CV strategy (e.g., StratifiedKFold).")
    baseline_architecture: str = Field(description="Simple, robust baseline model recommendation.")
    critical_flaws: List[str] = Field(description="Potential pitfalls in the feature engineering.")

class DialecticExpertOutput(BaseModel):
    """Strict schema for Philosophical/Dialectic reasoning."""
    core_thesis: str
    antithesis: str
    synthesis: str
    logical_fallacies_avoided: List[str]

class WritingExpertOutput(BaseModel):
    """Strict schema for the Writing Expert."""
    tone_consistency_score: float
    structural_flow: str
    draft_paragraphs: List[str]


# ==========================================
# L2 SYNTHESIS ENGINE SCHEMAS (NEURO-SYMBOLIC)
# ==========================================
from pydantic import BaseModel, Field
from typing import List

class RigorSentinelOutput(BaseModel):
    """Strict schema for the Leakage & Rigor Sentinel (formerly Kaggle Expert)."""
    epistemic_blind_spots: List[str] = Field(description="Hidden assumptions or target leakage risks in the user's premise.")
    falsification_metric: str = Field(description="The exact mathematical or logical metric that would prove this premise wrong.")
    robust_baseline: str = Field(description="A highly resilient, low-complexity baseline approach.")

class HegelianDialecticOutput(BaseModel):
    """Strict schema for the Hegelian Synthesis Engine."""
    steelmanned_antithesis: str = Field(description="The absolute strongest possible argument against the core thesis.")
    synthesis_resolution: str = Field(description="The nuanced truth that reconciles the thesis and the antithesis.")
    remaining_uncertainties: List[str] = Field(description="Questions that still lack sufficient evidence.")
    epistemic_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the synthesis based on available evidence.")
    source_warrant: str = Field(description="The exact logical warrant or grounded theory that justifies this synthesis.")

class ChainOfDensityOutput(BaseModel):
    """Strict schema for the Chain of Density Architect."""
    information_density_score: float = Field(ge=0.0, le=10.0, description="Score of how dense the signal-to-noise ratio is.")
    crystallized_claim: str = Field(description="The final, hyper-dense output stripped of all filler words.")

class ClaimLatticeOutput(BaseModel):
    """A strict output schema containing multiple grounded claims."""
    claims: List[Claim]
    lattice_summary: str = Field(description="A short summary of how these claims interlock.")
