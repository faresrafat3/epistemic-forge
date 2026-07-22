"""Classic pipeline smoke tests (mirrors the original suite, now corrected).

Uses Pytest and Mocks to ensure CI/CD passes without requiring
live API keys or consuming credits.
"""

import pytest

from epistemic_forge.models import (
    ProjectSpec,
)
from epistemic_forge.pipeline.l2_conductor import SemanticConductor


@pytest.fixture
def dummy_spec():
    return ProjectSpec(
        title="Test Project",
        question="Is this a test?",
        domain="research",
        target_model="mock-model",
    )


def test_l0_router_fallback(dummy_spec, mocker):
    """Ensure L0 Router falls back safely if LLM fails."""
    mocker.patch(
        "epistemic_forge.pipeline.router.generate_structured",
        side_effect=Exception("API Down"),
    )
    from epistemic_forge.pipeline.router import route_project

    decision = route_project(dummy_spec)
    assert decision.l3_mode == "tot"
    assert decision.activate["l4_refine"] is True


def test_l2_conductor_routing(dummy_spec, mocker):
    """Ensure L2 Conductor routes to the correct experts for the research domain."""
    conductor = SemanticConductor()
    # NOTE: the contract requires a ProjectSpec, not a bare domain string.
    active = conductor._route_experts(dummy_spec)

    names = [e.expert_name for e in active]
    assert "Hegelian_Dialectic_Engine" in names
    assert "Rigor_And_Leakage_Sentinel" in names


def test_economy_manager():
    """Ensure the Token Budget Manager correctly halts operations."""
    from epistemic_forge.memory.economy import budget_manager

    budget_manager.reset()
    budget_manager.set_budget(100)

    class MockResponse:
        class Usage:
            total_tokens = 150

        usage = Usage()

    budget_manager.add_usage(MockResponse(), "mock-model")
    assert budget_manager.is_budget_exceeded() is True
