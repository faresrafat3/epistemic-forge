"""Additional coverage: memory helpers, I/O export, standalone experts, CLI, errors."""


import pytest

from epistemic_forge.errors import PipelineError
from epistemic_forge.experts import freelance_expert, semitic_expert, writing_expert
from epistemic_forge.memory.reflexion_store import ReflexionStore
from epistemic_forge.models import (
    Claim,
    Confidence,
    ForgeResult,
    ProjectSpec,
    RouteDecision,
    StageArtifact,
)
from epistemic_forge.pipeline import arsenal_run

# ----------------------------- reflexion store -----------------------------


def test_reflexion_windowing():
    store = ReflexionStore(window=3)
    for i in range(5):
        store.add(store.reflect_on_failure(trial=i, score=0.1, notes=f"fail {i}"))
    assert len(store.all()) == 3
    assert store.all()[-1].trial == 4


def test_reflexion_prompt_block_empty():
    assert "No prior" in ReflexionStore().as_prompt_block()


def test_reflexion_reflect_on_failure():
    store = ReflexionStore()
    r = store.reflect_on_failure(trial=1, score=0.2, notes="bad")
    assert r.lesson
    assert r in store.all()


# ------------------------------- I/O export --------------------------------


def _sample_result():
    spec = ProjectSpec(title="Sample", question="Q?", domain="research")
    claims = [
        Claim(
            id="C1",
            text="A baseline-first plan is reliable.",
            epistemic_warrant="Baselines expose errors early.",
            potential_falsifier="If baseline fails while alt succeeds.",
            confidence=Confidence.LIKELY,
        )
    ]
    artifacts = [
        StageArtifact(name="Final Synthesis Memo", content="memo body", kind="markdown"),
        StageArtifact(
            name="Baseline Notebook",
            content="```python\nprint('hi')\n```",
            kind="python",
            path_hint="baseline",
        ),
    ]
    return ForgeResult(
        spec=spec,
        route=RouteDecision(families=["mock"], activate={}, rationale="r"),
        instruction="do",
        claims=claims,
        search_trace=[],
        reflections=[],
        skills_used=[],
        artifacts=artifacts,
        peer_review={
            "verdict": "accept",
            "final_comments": "looks good",
            "overall_score": 0.8,
        },
        final_score=0.8,
    )


def test_export_writes_files(tmp_path):
    from epistemic_forge.io.export import export_result

    export_result(_sample_result(), str(tmp_path))
    assert (tmp_path / "executive_summary.md").exists()
    assert (tmp_path / "claim_lattice_graph.json").exists()
    assert (tmp_path / "baseline.ipynb").exists()


def test_export_mermaid_contains_claim(tmp_path):
    from epistemic_forge.io.export import _generate_mermaid_graph

    graph = _generate_mermaid_graph(_sample_result().claims)
    assert "C1" in graph
    assert "graph TD" in graph


# --------------------------- standalone experts ----------------------------


def test_freelance_pack():
    spec = ProjectSpec(title="Pitch", question="Help me price", domain="freelance")
    pack = freelance_expert.build_client_pack(spec, {})
    assert pack["client_brief"]["title"] == "Pitch"
    assert pack["acceptance_criteria"]


def test_writing_expert_offline():
    spec = ProjectSpec(title="t", question="q")
    out = writing_expert.outline_and_draft(spec, {"claims": []}, "instr")
    assert "draft_markdown" in out
    assert "Density Score" in out["draft_markdown"]


def test_semitic_expert_offline():
    spec = ProjectSpec(title="t", question="q")
    out = semitic_expert.run_semitic_dialectic(spec, {})
    assert out["thesis"] == "q"
    assert "synthesis_arabic" in out


# ------------------------------- CLI / errors ------------------------------


def test_cli_main_runs(monkeypatch, capsys):
    from epistemic_forge.cli import main

    class FakeResult:
        claims = []

    monkeypatch.setattr("epistemic_forge.cli.run_pipeline", lambda **k: FakeResult())
    monkeypatch.setattr("epistemic_forge.io.export.export_result", lambda *a, **k: None)
    monkeypatch.setattr("sys.argv", ["ef", "--title", "T", "--question", "Q?"])
    main()  # must not raise (and must not call sys.exit)
    captured = capsys.readouterr()
    assert "Pipeline Execution Successful" in captured.out


def test_run_pipeline_raises_typed_error_not_systemexit(monkeypatch):
    def boom(ctx):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(arsenal_run, "execute_pipeline", boom)
    with pytest.raises(PipelineError):
        arsenal_run.run_pipeline(title="t", question="q")
