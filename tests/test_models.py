"""Tests for the core Pydantic data models and their constraints."""

import pytest
from pydantic import ValidationError

from epistemic_forge.models import (
    Claim,
    ClaimLatticeOutput,
    Confidence,
    Domain,
    FinalPeerReview,
    ForgeResult,
    PeerReviewScores,
    ProjectSpec,
    RouteDecision,
    Skill,
)


def test_domain_coercion_and_default():
    spec = ProjectSpec(title="t", question="q", domain="research")
    assert spec.domain is Domain.RESEARCH
    default = ProjectSpec(title="t", question="q")
    assert default.domain is Domain.HYBRID


def test_domain_invalid_string_rejected():
    with pytest.raises(ValidationError):
        ProjectSpec(title="t", question="q", domain="not_a_domain")


def test_claim_requires_warrant_and_falsifier():
    with pytest.raises(ValidationError):
        Claim(id="C1", text="a claim")


def test_claim_valid():
    c = Claim(
        id="C1",
        text="x",
        epistemic_warrant="because y",
        potential_falsifier="if z",
        confidence=Confidence.LIKELY,
    )
    assert c.confidence is Confidence.LIKELY


def test_route_decision_constraints():
    rd = RouteDecision(
        families=["a"], activate={"l3_search": True}, rationale="r"
    )
    assert rd.l1_mode == "ape"
    assert rd.l3_mode == "tot"


def test_peer_review_scores_bounded():
    with pytest.raises(ValidationError):
        PeerReviewScores(clarity=2.0, structure=0.0, soundness=0.0, actionability=0.0, humility=0.0)


def test_final_peer_review_overall_bounded():
    with pytest.raises(ValidationError):
        FinalPeerReview(
            scores=PeerReviewScores(
                clarity=0.1, structure=0.1, soundness=0.1, actionability=0.1, humility=0.1
            ),
            overall_score=1.5,
            verdict="accept",
            final_comments="ok",
        )


def test_forge_result_roundtrip():
    spec = ProjectSpec(title="t", question="q")
    res = ForgeResult(
        spec=spec,
        route=RouteDecision(families=["a"], activate={}, rationale="r"),
        instruction="do it",
        claims=[],
        search_trace=[],
        reflections=[],
        skills_used=[],
        artifacts=[],
        peer_review={},
        final_score=0.5,
    )
    dumped = res.model_dump()
    assert dumped["final_score"] == 0.5
    assert isinstance(ClaimLatticeOutput(claims=[], lattice_summary="s"), ClaimLatticeOutput)


def test_skill_model():
    s = Skill(name="x", description="d", code="c", tags=["t1"])
    assert s.name == "x"
