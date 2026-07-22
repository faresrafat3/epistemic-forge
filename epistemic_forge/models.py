"""Core data models for Epistemic Forge."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    constraints: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    budget_tokens: int = 8000
    max_trials: int = 3
    enable_opro_style: bool = True
    enable_skills: bool = True

    # Hermes Universal Routing Overrides
    target_model: str = "gpt-4o-mini"
    api_base: str | None = None
    api_key: str | None = None


class Claim(BaseModel):
    """Atomic epistemic unit with absolute grounding."""

    id: str = Field(description="Unique identifier, e.g., C1")
    text: str = Field(description="The core claim or premise.")
    epistemic_warrant: str = Field(
        description="MANDATORY: The exact logical deduction, explanation, or evidence that proves this claim. NO UNSUBSTANTIATED CLAIMS."
    )
    potential_falsifier: str = Field(
        description="What specific evidence or scenario would prove this claim wrong?"
    )
    support: list[str] = Field(
        default_factory=list, description="Sub-arguments supporting this claim."
    )
    objections: list[str] = Field(
        default_factory=list, description="Valid counter-arguments against this claim."
    )
    confidence: Confidence = Field(default=Confidence.LIKELY)


class RouteDecision(BaseModel):
    """L0 router output."""

    families: list[str]
    activate: dict[str, bool]
    rationale: str
    l1_mode: str = "ape"  # ape | opro | cascade | off
    l3_mode: str = "tot"  # tot | lats | cascade | off


class SearchNode(BaseModel):
    """L3 deliberate-search node."""

    id: str
    thought: str
    value: float
    parent_id: str | None = None
    children: list[str] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


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
    tags: list[str] = Field(default_factory=list)


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
    claims: list[Claim]
    search_trace: list[SearchNode]
    reflections: list[Reflection]
    skills_used: list[str]
    artifacts: list[StageArtifact]
    peer_review: dict[str, Any]
    trial_log: list[dict[str, Any]] = Field(default_factory=list)
    final_score: float = 0.0


# ==========================================
# NEURO-SYMBOLIC EXPERT SCHEMAS (L2)
# Enforcing deterministic outputs from LLMs
# ==========================================


class KaggleExpertOutput(BaseModel):
    """Strict schema for the Kaggle Expert to prevent hallucinations."""

    leakage_risk_score: float = Field(
        ge=0.0, le=1.0, description="Risk of data leakage in the proposed approach."
    )
    validation_strategy: str = Field(
        description="Strict CV strategy (e.g., StratifiedKFold)."
    )
    baseline_architecture: str = Field(
        description="Simple, robust baseline model recommendation."
    )
    critical_flaws: list[str] = Field(
        description="Potential pitfalls in the feature engineering."
    )


class DialecticExpertOutput(BaseModel):
    """Strict schema for Philosophical/Dialectic reasoning."""

    core_thesis: str
    antithesis: str
    synthesis: str
    logical_fallacies_avoided: list[str]


class WritingExpertOutput(BaseModel):
    """Strict schema for the Writing Expert."""

    tone_consistency_score: float
    structural_flow: str
    draft_paragraphs: list[str]


# ==========================================
# L2 SYNTHESIS ENGINE SCHEMAS (NEURO-SYMBOLIC)
# ==========================================


class RigorSentinelOutput(BaseModel):
    """Strict schema for the Leakage & Rigor Sentinel (formerly Kaggle Expert)."""

    epistemic_blind_spots: list[str] = Field(
        description="Hidden assumptions or target leakage risks in the user's premise."
    )
    falsification_metric: str = Field(
        description="The exact mathematical or logical metric that would prove this premise wrong."
    )
    robust_baseline: str = Field(
        description="A highly resilient, low-complexity baseline approach."
    )


class HegelianDialecticOutput(BaseModel):
    """Strict schema for the Hegelian Synthesis Engine."""

    steelmanned_antithesis: str = Field(
        description="The absolute strongest possible argument against the core thesis."
    )
    synthesis_resolution: str = Field(
        description="The nuanced truth that reconciles the thesis and the antithesis."
    )
    remaining_uncertainties: list[str] = Field(
        description="Questions that still lack sufficient evidence."
    )
    epistemic_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the synthesis based on available evidence.",
    )
    source_warrant: str = Field(
        description="The exact logical warrant or grounded theory that justifies this synthesis."
    )


class ChainOfDensityOutput(BaseModel):
    """Strict schema for the Chain of Density Architect."""

    information_density_score: float = Field(
        ge=0.0, le=10.0, description="Score of how dense the signal-to-noise ratio is."
    )
    crystallized_claim: str = Field(
        description="The final, hyper-dense output stripped of all filler words."
    )


class ClaimLatticeOutput(BaseModel):
    """A strict output schema containing multiple grounded claims."""

    claims: list[Claim]
    lattice_summary: str = Field(
        description="A short summary of how these claims interlock."
    )


class OptimizedInstruction(BaseModel):
    """Strict schema for the L1 Instruction Optimizer (OPRO)."""

    meta_prompt: str = Field(
        description="The optimized, hyper-specific instruction for the task."
    )
    rationale: str = Field(
        description="Why this instruction will yield better results than a generic prompt."
    )
    expected_failure_modes: list[str] = Field(
        description="What the LLM might get wrong if not guided properly."
    )


class ThoughtProposal(BaseModel):
    """A single reasoning path proposed during Tree Search."""

    thought_text: str = Field(description="The proposed logical step or framing.")


class ThoughtProposalsOutput(BaseModel):
    """Collection of proposed thoughts for branching."""

    proposals: list[ThoughtProposal]


class ThoughtEvaluation(BaseModel):
    """LLM-as-a-Judge evaluation of a specific thought branch."""

    epistemic_score: float = Field(
        ge=0.0,
        le=1.0,
        description="How epistemically sound and logically rigorous this thought is.",
    )
    critique: str = Field(description="Why this thought deserves this score.")


class RefinementFeedback(BaseModel):
    """Strict schema for the L4 Adversarial Critique."""

    clarity_score: float = Field(
        ge=0.0, le=1.0, description="How clear and logically flowing the artifact is."
    )
    epistemic_humility_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Presence of explicit boundaries, assumptions, and falsifiers.",
    )
    critical_flaws: list[str] = Field(
        description="List of logical leaps, hallucinations, or unsupported claims."
    )
    passes_threshold: bool = Field(
        description="True if scores are high enough and no critical flaws exist."
    )


class RefinedArtifact(BaseModel):
    """Strict schema for the L4 Rewritten Output."""

    improved_text: str = Field(
        description="The heavily revised, flawless version of the text."
    )
    changes_made: list[str] = Field(description="What was fixed based on the critique.")


class PeerReviewScores(BaseModel):
    clarity: float = Field(ge=0.0, le=1.0)
    structure: float = Field(ge=0.0, le=1.0)
    soundness: float = Field(ge=0.0, le=1.0)
    actionability: float = Field(ge=0.0, le=1.0)
    humility: float = Field(ge=0.0, le=1.0)


class FinalPeerReview(BaseModel):
    """Strict schema for the L6 AI Scientist Wrap-up."""

    scores: PeerReviewScores
    overall_score: float = Field(ge=0.0, le=1.0, description="Average of all metrics.")
    revision_needed: list[str] = Field(description="Areas that still need work if any.")
    verdict: str = Field(
        description="Must be one of: 'accept', 'accept_with_minor_revisions', 'major_revisions', 'reject'"
    )
    final_comments: str = Field(description="A formal peer-review summary.")


class DynamicExpertSchema(BaseModel):
    """Schema for ADAS (Automated Design of Agentic Systems).
    The LLM designs a new Pydantic schema structure for a novel expert.
    """

    expert_class_name: str = Field(
        description="Name of the expert, e.g., 'QuantumMechanicsExpert'"
    )
    expert_description: str = Field(description="What this expert analyzes.")
    fields_to_extract: list[dict[str, str]] = Field(
        description="List of fields the expert must extract. Format: {'field_name': 'description'}"
    )
    system_prompt: str = Field(
        description="The ruthless, highly specific prompt guiding this new expert."
    )


class SearchResult(BaseModel):
    best_thought: str
    nodes: list[SearchNode]
    mode_used: str
    score: float
