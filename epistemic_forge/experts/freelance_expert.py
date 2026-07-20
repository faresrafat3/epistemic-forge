"""Freelance packaging expert."""

from __future__ import annotations

from typing import Any, Dict

from epistemic_forge.models import ProjectSpec


def build_client_pack(
    spec: ProjectSpec, claims_bundle: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "client_brief": {
            "goal": spec.question,
            "title": spec.title,
            "audience": spec.audience,
            "constraints": spec.constraints or ["TBD with client"],
            "keywords": spec.keywords,
        },
        "scope": {
            "in_scope": [
                "Discovery memo with claim lattice",
                "One primary deliverable draft",
                "Revision checklist",
            ],
            "out_of_scope": [
                "Unlimited revisions",
                "Unrelated brand strategy",
                "Production deployment without separate SOW",
            ],
            "assumptions": [
                "Client provides access to source materials within 48h",
                "Primary language is English unless specified",
            ],
        },
        "milestones": [
            {"name": "Kickoff + intake", "days": 2},
            {"name": "Claim lattice + outline", "days": 4},
            {"name": "Draft v1", "days": 7},
            {"name": "Revision + handoff", "days": 10},
        ],
        "acceptance_criteria": [
            "Answers the core question in plain language",
            "Lists assumptions and risks explicitly",
            "Includes next actions the client can execute",
        ],
        "proposal_spine": (
            f"You need clarity on «{spec.title}». I will turn the fog into a claim lattice, "
            "a decision-ready memo, and a scoped next step—so you can act without false certainty."
        ),
    }
