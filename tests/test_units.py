"""Unit tests for individual pipeline stages (L0–L6)."""


import pytest

from epistemic_forge.errors import InvalidInputError
from epistemic_forge.models import (
    DynamicExpertSchema,
    FinalPeerReview,
    PeerReviewScores,
    ProjectSpec,
    RefinedArtifact,
    RefinementFeedback,
    ThoughtEvaluation,
    ThoughtProposalsOutput,
)
from epistemic_forge.pipeline.l1_5_adas import _safe_identifier, generate_dynamic_expert
from epistemic_forge.pipeline.l1_optimizer import optimize_instruction
from epistemic_forge.pipeline.l2_conductor import SemanticConductor
from epistemic_forge.pipeline.l3_search import explore
from epistemic_forge.pipeline.l4_refine import refine_document
from epistemic_forge.pipeline.l6_stages import produce_artifacts
from epistemic_forge.pipeline.router import route_project


@pytest.fixture
def spec():
    return ProjectSpec(title="T", question="Is this testable?", domain="research")


def test_l0_router_fallback_on_failure(mocker):
    mocker.patch(
        "epistemic_forge.pipeline.router.generate_structured",
        side_effect=Exception("API Down"),
    )
    decision = route_project(ProjectSpec(title="t", question="q", domain="research"))
    assert decision.l3_mode == "tot"
    assert decision.activate["l4_refine"] is True


def test_l0_router_offline_returns_decision():
    d = route_project(ProjectSpec(title="t", question="q", domain="philosophy"))
    assert isinstance(d, type(d))
    assert "l3_search" in d.activate


def test_l1_optimizer_offline_returns_string(spec):
    inst = optimize_instruction(spec)
    assert isinstance(inst, str) and len(inst) > 0


def test_l1_optimizer_fallback_on_error(mocker, spec):
    mocker.patch(
        "epistemic_forge.pipeline.l1_optimizer.generate_structured",
        side_effect=RuntimeError("boom"),
    )
    inst = optimize_instruction(spec)
    assert isinstance(inst, str) and len(inst) > 0


def test_l2_conductor_routing_research(spec):
    conductor = SemanticConductor()
    active = conductor._route_experts(spec)
    names = [e.expert_name for e in active]
    assert "Hegelian_Dialectic_Engine" in names
    assert "Rigor_And_Leakage_Sentinel" in names


def test_l2_conductor_routing_kaggle():
    spec = ProjectSpec(title="t", question="q", domain="kaggle")
    names = [e.expert_name for e in SemanticConductor()._route_experts(spec)]
    assert "Rigor_And_Leakage_Sentinel" in names
    assert "Hegelian_Dialectic_Engine" not in names


def test_l2_conductor_routing_writing_has_no_hegelian_or_rigor():
    spec = ProjectSpec(title="t", question="q", domain="writing")
    names = [e.expert_name for e in SemanticConductor()._route_experts(spec)]
    assert "Hegelian_Dialectic_Engine" not in names
    assert "Rigor_And_Leakage_Sentinel" not in names


def test_l2_conductor_type_contract():
    # The router test originally passed a string; the contract requires a ProjectSpec.
    with pytest.raises(AttributeError):
        SemanticConductor()._route_experts("research")  # type: ignore[arg-type]


def test_safe_identifier():
    assert _safe_identifier("My Expert!") == "myexpert"
    assert _safe_identifier("9bad") == "_9bad"
    assert _safe_identifier("") == ""


def test_adas_creates_working_expert(mocker):
    def fake_gen(messages, response_model, **kwargs):
        if response_model.__name__ == "DynamicExpertSchema":
            return DynamicExpertSchema(
                expert_class_name="RiskExpert",
                expert_description="risk analysis",
                fields_to_extract=[{"risk": "main risk"}, {"check": "validation"}],
                system_prompt="analyze risks",
            )
        return response_model(risk="r", check="c")

    mocker.patch(
        "epistemic_forge.pipeline.l1_5_adas.generate_structured", side_effect=fake_gen
    )
    expert = generate_dynamic_expert(
        ProjectSpec(title="t", question="q", domain="research")
    )
    assert expert.expert_name == "riskexpert"
    out = expert.analyze(
        ProjectSpec(title="t", question="q", domain="research"), {"instruction": "x"}
    )
    assert out.risk == "r"


def test_adas_rejects_empty_blueprint(mocker):
    mocker.patch(
        "epistemic_forge.pipeline.l1_5_adas.generate_structured",
        return_value=DynamicExpertSchema(
            expert_class_name="X", expert_description="d", fields_to_extract=[], system_prompt="p"
        ),
    )
    with pytest.raises(InvalidInputError):
        generate_dynamic_expert(ProjectSpec(title="t", question="q"))


def test_l3_search_evaluates_and_rolls_back(mocker):
    scores = iter([0.2, 0.9, 0.5])
    calls = {"n": 0}

    def fake_gen(messages, response_model, **kwargs):
        calls["n"] += 1
        if response_model.__name__ == "ThoughtProposalsOutput":
            return ThoughtProposalsOutput(
                proposals=[
                    {"thought_text": "weak thought"},
                    {"thought_text": "strong thought"},
                ]
            )
        return ThoughtEvaluation(epistemic_score=next(scores), critique="c")

    mocker.patch("epistemic_forge.pipeline.l3_search.generate_structured", side_effect=fake_gen)
    result = explore(ProjectSpec(title="t", question="q"), {"x": 1}, beam=2, steps=1)
    assert result.mode_used
    assert len(result.nodes) == 2  # both thoughts become nodes
    # best thought is the strong one (0.9)
    assert "strong" in result.best_thought
    assert result.score == 0.9


def test_l4_refine_iterates_until_pass(mocker):
    state = {"i": 0}

    def fake_gen(messages, response_model, **kwargs):
        state["i"] += 1
        if response_model.__name__ == "RefinementFeedback":
            if state["i"] == 1:
                return RefinementFeedback(
                    clarity_score=0.4,
                    epistemic_humility_score=0.4,
                    critical_flaws=["vague"],
                    passes_threshold=False,
                )
            return RefinementFeedback(
                clarity_score=0.9,
                epistemic_humility_score=0.9,
                critical_flaws=[],
                passes_threshold=True,
            )
        return RefinedArtifact(improved_text="FINAL", changes_made=["fixed vagueness"])

    mocker.patch("epistemic_forge.pipeline.l4_refine.generate_structured", side_effect=fake_gen)
    text, score = refine_document(ProjectSpec(title="t", question="q"), "draft", max_iterations=3)
    assert text == "FINAL"
    assert score > 0.8


def test_l6_stages_produces_artifacts(mocker):
    mocker.patch(
        "epistemic_forge.pipeline.l6_stages.generate_structured",
        return_value=FinalPeerReview(
            scores=PeerReviewScores(
                clarity=0.8, structure=0.8, soundness=0.8, actionability=0.8, humility=0.8
            ),
            overall_score=0.8,
            revision_needed=[],
            verdict="accept",
            final_comments="good",
        ),
    )
    artifacts, review, score = produce_artifacts(
        ProjectSpec(title="t", question="q"), "final draft", {}, 0.5
    )
    assert len(artifacts) >= 1
    assert review["overall_score"] == 0.8
    assert score == 0.8
