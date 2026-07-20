"""Claim lattice expert."""

from __future__ import annotations

from typing import Any, Dict, List

from epistemic_forge.models import Claim, Confidence, ProjectSpec


def extract_claims(spec: ProjectSpec, instruction: str) -> Dict[str, Any]:
    q = spec.question.strip()
    title = spec.title.strip()
    # Deterministic structured extraction (no external LLM required)
    core = Claim(
        id="C1",
        text=f"Core thesis addressing: {q}",
        support=[
            f"Aligned with instruction: {instruction[:120]}...",
            f"Keywords in play: {', '.join(spec.keywords) or 'general domain cues'}",
        ],
        objections=[
            "The framing may smuggle unstated assumptions about the audience.",
            "Evidence quality is not yet measured; confidence should stay provisional.",
        ],
        confidence=Confidence.LIKELY,
        sources=["user-question", "instruction"],
        tags=["thesis"],
    )
    support_c = Claim(
        id="C2",
        text=f"Working support: a structured approach to «{title}» improves decision quality under uncertainty.",
        support=[
            "Decomposition reduces hidden tradeoffs.",
            "Explicit objections prevent one-sided writing.",
        ],
        objections=["Structure without domain data can become cargo-cult rigor."],
        confidence=Confidence.POSSIBLE,
        tags=["support"],
    )
    residual = Claim(
        id="C3",
        text="Residual uncertainty: which single metric or stakeholder criterion should dominate tradeoffs?",
        support=["Multi-objective problems need a declared primary criterion."],
        objections=["Premature metric fixation can distort the inquiry."],
        confidence=Confidence.WEAK,
        tags=["uncertainty"],
    )
    claims: List[Claim] = [core, support_c, residual]
    return {
        "claims": [c.to_dict() for c in claims],
        "lattice_summary": (
            "Three-node lattice: thesis, support, residual uncertainty. "
            "Ready for dialectic stress-test and packaging."
        ),
    }
