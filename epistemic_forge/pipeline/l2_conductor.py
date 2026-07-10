"""L2 — Meta Conductor (Meta-Prompting style expert dispatch)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from epistemic_forge.experts import (
    claim_expert,
    dialectic_expert,
    freelance_expert,
    kaggle_expert,
    writing_expert,
)
from epistemic_forge.models import ProjectSpec


@dataclass
class ExpertCall:
    name: str
    instruction: str
    output: Dict[str, Any]


@dataclass
class ConductorResult:
    final_bundle: Dict[str, Any]
    log: List[ExpertCall] = field(default_factory=list)


def conduct(spec: ProjectSpec, instruction: str, skills: List[str] | None = None) -> ConductorResult:
    """Decompose work into expert subcalls and integrate outputs."""
    log: List[ExpertCall] = []
    skills = skills or []
    bundle: Dict[str, Any] = {
        "instruction": instruction,
        "skills_used": skills,
    }

    # Expert 1: always extract claims
    claims = claim_expert.extract_claims(spec, instruction)
    log.append(ExpertCall("ClaimLatticeExpert", "Extract atomic claims with supports/objections", claims))
    bundle["claims"] = claims

    # Expert 2: domain specialists
    domain = spec.domain.value
    if domain in {"philosophy", "research", "hybrid"}:
        dial = dialectic_expert.run_dialectic(spec, claims)
        log.append(ExpertCall("DialecticExpert", "Thesis / antithesis / synthesis", dial))
        bundle["dialectic"] = dial
    if domain in {"writing", "research", "philosophy", "hybrid"}:
        essay = writing_expert.outline_and_draft(spec, claims, instruction)
        log.append(ExpertCall("WritingExpert", "Outline + draft sections", essay))
        bundle["writing"] = essay
    if domain in {"freelance", "hybrid"}:
        brief = freelance_expert.build_client_pack(spec, claims)
        log.append(ExpertCall("FreelanceExpert", "Client brief + scope + proposal spine", brief))
        bundle["freelance"] = brief
    if domain in {"kaggle", "hybrid"}:
        kg = kaggle_expert.build_competition_kit(spec, claims, skills)
        log.append(ExpertCall("KaggleExpert", "EDA/baseline plan + notebook skeleton", kg))
        bundle["kaggle"] = kg

    # Integration note (meta-model style)
    bundle["integration"] = {
        "summary": (
            f"Integrated {len(log)} expert outputs for domain={domain}. "
            f"Primary question: {spec.question}"
        ),
        "next_bridge": "Pass bundle to L3 search for alternative framings, then L4 polish.",
    }
    return ConductorResult(final_bundle=bundle, log=log)
