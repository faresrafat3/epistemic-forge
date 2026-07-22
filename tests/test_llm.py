"""Tests for the universal LLM router (offline fallback, validation, async)."""

import pytest

from epistemic_forge.errors import InvalidInputError
from epistemic_forge.llm import (
    _offline_fallback,
    agenerate_structured,
    generate_structured,
    validate_messages,
)
from epistemic_forge.models import (
    ClaimLatticeOutput,
    DynamicExpertSchema,
    FinalPeerReview,
    HegelianDialecticOutput,
    OptimizedInstruction,
    RefinedArtifact,
    RefinementFeedback,
    RigorSentinelOutput,
    RouteDecision,
    ThoughtEvaluation,
    ThoughtProposalsOutput,
)

OFFLINE_MODELS = [
    OptimizedInstruction,
    ThoughtProposalsOutput,
    ThoughtEvaluation,
    RefinementFeedback,
    RefinedArtifact,
    FinalPeerReview,
    DynamicExpertSchema,
    ClaimLatticeOutput,
    HegelianDialecticOutput,
    RigorSentinelOutput,
    RouteDecision,
]


@pytest.mark.parametrize("model", OFFLINE_MODELS)
def test_offline_fallback_builds_every_model(model):
    out = _offline_fallback(model, [{"role": "user", "content": "test prompt"}])
    assert isinstance(out, model)


def test_offline_fallback_fills_unknown_required_fields():
    from pydantic import BaseModel

    class WeirdModel(BaseModel):
        a: str
        b: float
        c: int
        d: bool
        e: list

    out = _offline_fallback(WeirdModel, [{"role": "user", "content": "x"}])
    assert out.a
    assert out.b == 0.5
    assert out.c == 0
    assert out.d is False
    assert out.e == []


def test_validate_messages_rejects_empty():
    with pytest.raises(InvalidInputError):
        validate_messages([])


def test_validate_messages_rejects_non_mapping():
    with pytest.raises(InvalidInputError):
        validate_messages(["not a dict"])


def test_validate_messages_rejects_oversized(monkeypatch):
    monkeypatch.setattr(
        "epistemic_forge.llm.MAX_PROMPT_CHARS", 10
    )
    with pytest.raises(InvalidInputError):
        validate_messages([{"role": "user", "content": "x" * 50}])


def test_validate_messages_accepts_valid():
    validate_messages(
        [
            {"role": "system", "content": "be good"},
            {"role": "user", "content": "hello"},
        ]
    )


def test_generate_structured_offline_returns_fallback():
    out = generate_structured(
        messages=[{"role": "user", "content": "hi"}],
        response_model=OptimizedInstruction,
        model="gpt-4o-mini",
    )
    assert isinstance(out, OptimizedInstruction)
    assert "Toulmin" in out.meta_prompt or "claim" in out.meta_prompt.lower()


@pytest.mark.asyncio
async def test_agenerate_structured_offline_returns_fallback():
    out = await agenerate_structured(
        messages=[{"role": "user", "content": "hi"}],
        response_model=ClaimLatticeOutput,
        model="gpt-4o-mini",
    )
    assert isinstance(out, ClaimLatticeOutput)
    assert out.claims
