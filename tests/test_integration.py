"""Integration + architecture (machine) + CLI + async tests."""

import asyncio

from epistemic_forge.cli import build_parser
from epistemic_forge.models import ProjectSpec, RouteDecision
from epistemic_forge.pipeline import arsenal_run
from epistemic_forge.pipeline.l2_conductor import conduct_async
from epistemic_forge.pipeline.machine import PipelineContext, execute_pipeline, planned_stages


def test_full_pipeline_offline_runs():
    result = arsenal_run.run_pipeline(
        title="Integration", question="Does this work end to end?", domain="research"
    )
    assert result.spec.title == "Integration"
    assert isinstance(result.final_score, float)
    assert 0.0 <= result.final_score <= 1.0
    assert result.peer_review
    assert len(result.artifacts) >= 1
    # Claims come back as dicts from the offline fallback; ensure shape is sane.
    assert isinstance(result.claims, list)


def test_planned_stages_includes_heavy_layers():
    stages = planned_stages(ProjectSpec(title="t", question="q", domain="research"))
    assert "L3_search" in stages
    assert "L6_review" in stages


def test_execute_pipeline_respects_l3_toggle():
    ctx = PipelineContext(
        spec=ProjectSpec(title="t", question="q", domain="research"),
        route=RouteDecision(
            families=["mock"], activate={"l3_search": False}, rationale="disable search"
        ),
    )
    out = execute_pipeline(ctx)
    assert "L3_search" not in out.stages_run
    assert out.search_result is None
    assert "L6_review" in out.stages_run


def test_async_pipeline_runs():
    result = arsenal_run.run_pipeline(
        title="Async", question="Async end to end?", domain="philosophy", async_run=True
    )
    assert isinstance(result.final_score, float)
    assert 0.0 <= result.final_score <= 1.0


def test_conduct_async_runs_experts_concurrently():
    spec = ProjectSpec(title="t", question="q", domain="research")
    results = asyncio.run(
        conduct_async(spec, {"instruction": "x", "skills": []})
    )
    assert "Grounded_Claim_Lattice_Generator" in results
    assert "Hegelian_Dialectic_Engine" in results


def test_cli_parser_requires_args():
    parser = build_parser()
    args = parser.parse_args(["--title", "T", "--question", "Q?"])
    assert args.title == "T"
    assert args.question == "Q?"
    assert args.domain == "hybrid"


def test_cli_parser_custom_model():
    parser = build_parser()
    args = parser.parse_args(
        ["--title", "T", "--question", "Q?", "--model", "anthropic/claude-3-opus"]
    )
    assert args.model == "anthropic/claude-3-opus"
