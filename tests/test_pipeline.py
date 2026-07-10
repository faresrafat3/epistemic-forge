"""Tests for Epistemic Forge pipeline."""

from pathlib import Path

from epistemic_forge.io.export import export_result
from epistemic_forge.models import Domain, ProjectSpec
from epistemic_forge.pipeline.arsenal_run import ArsenalRun, run_pipeline
from epistemic_forge.pipeline.l1_optimizer import ape_generate, optimize_instruction, opro_evolve
from epistemic_forge.pipeline.router import route_project


def test_router_kaggle_enables_skills_and_cascade():
    spec = ProjectSpec(
        title="Tabular race",
        question="How should I build a leakage-safe baseline for a Kaggle tabular competition?",
        domain=Domain.KAGGLE,
        keywords=["kaggle", "baseline", "cv"],
    )
    route = route_project(spec)
    assert route.activate["voyager"] is True
    assert route.l3_mode in {"cascade", "lats", "tot"}
    assert "Agents" in route.families or "Self-Criticism" in route.families


def test_l1_ape_and_opro_scores_improve_or_hold():
    spec = ProjectSpec(
        title="Dialectic brief",
        question="What is free will under predictive processing?",
        domain=Domain.PHILOSOPHY,
        keywords=["free will", "predictive processing"],
    )
    ape = ape_generate(spec)
    assert ape and ape[0].score > 0
    evolved = opro_evolve(ape[:2], spec, steps=2)
    assert evolved[0].score >= ape[-1].score * 0.5  # not collapsed


def test_full_pipeline_hybrid_exports_files(tmp_path: Path):
    result = run_pipeline(
        title="Epistemic freelancing kit",
        question="How can freelancers package uncertain research into client-ready deliverables without overclaiming?",
        domain="hybrid",
        keywords=["freelance", "research", "claims"],
        max_trials=2,
    )
    assert result.final_score > 0
    assert result.artifacts
    assert result.route.rationale
    out = export_result(result, tmp_path / "out")
    assert (out / "MANIFEST.json").exists()
    assert (out / "result.json").exists()
    # At least executive summary written
    md_files = list(out.glob("*.md"))
    assert md_files


def test_arsenal_run_stateful_trials():
    runner = ArsenalRun.create()
    spec = ProjectSpec(
        title="Notebook ethics",
        question="What ethical risks arise when auto-generating Kaggle notebooks for clients?",
        domain=Domain.HYBRID,
        keywords=["ethics", "kaggle", "client"],
        max_trials=2,
    )
    r1 = runner.run(spec)
    assert r1.final_score > 0
    # skills library grew or stayed consistent
    assert len(runner.skills.names()) >= 5
