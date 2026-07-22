"""10-example benchmark: claim lattice (forge) vs baseline Q&A."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from epistemic_forge.benchmark.baseline import baseline_answer
from epistemic_forge.benchmark.metrics import score_document, toulmin_coverage
from epistemic_forge.pipeline.arsenal_run import run_pipeline


@dataclass
class BenchCase:
    id: str
    title: str
    question: str
    domain: str
    keywords: List[str]


BENCHMARK_CASES: List[BenchCase] = [
    BenchCase(
        "p1",
        "Predictive processing and blame",
        "If the brain is a prediction machine, what happens to moral responsibility?",
        "philosophy",
        ["predictive processing", "responsibility", "agency"],
    ),
    BenchCase(
        "p2",
        "Personal identity online",
        "Does a continuous social-media persona strengthen or erode personal identity?",
        "philosophy",
        ["identity", "narrative", "self"],
    ),
    BenchCase(
        "p3",
        "Explainability vs performance",
        "When should a public agency prefer an interpretable model over a stronger black box?",
        "philosophy",
        ["explainability", "ethics", "tradeoff"],
    ),
    BenchCase(
        "k1",
        "Imbalanced tabular baseline",
        "What is an honest baseline plan for a noisy imbalanced Kaggle table?",
        "kaggle",
        ["imbalance", "baseline", "cv", "leakage"],
    ),
    BenchCase(
        "k2",
        "Time-series leakage",
        "How do I avoid leakage when validating a forecasting model for store sales?",
        "kaggle",
        ["forecasting", "leakage", "split", "metric"],
    ),
    BenchCase(
        "k3",
        "NLP toxicity cup",
        "What is a solid first pipeline for a multilingual toxicity classification competition?",
        "kaggle",
        ["nlp", "baseline", "cv", "metric"],
    ),
    BenchCase(
        "f1",
        "Climate-tech research sprint",
        "How do I scope a 2-week research sprint for a climate-tech founder?",
        "freelance",
        ["sprint", "scope", "founder"],
    ),
    BenchCase(
        "f2",
        "AI policy brief for NGO",
        "How should I package an AI policy brief for a small NGO board with mixed technical literacy?",
        "freelance",
        ["policy", "brief", "client", "scope"],
    ),
    BenchCase(
        "f3",
        "Data audit for marketplace",
        "How do I propose a fixed-price data quality audit for an online marketplace?",
        "freelance",
        ["audit", "deliverable", "acceptance", "timeline"],
    ),
    BenchCase(
        "h1",
        "Research without overclaiming",
        "How can freelancers package uncertain research into client-ready deliverables without overclaiming?",
        "hybrid",
        ["research", "client", "claims", "uncertainty"],
    ),
]


@dataclass
class CaseResult:
    id: str
    domain: str
    title: str
    baseline_overall: float
    forge_overall: float
    baseline_toulmin: float
    forge_toulmin: float
    lift_overall: float
    lift_toulmin: float
    baseline_scores: Dict[str, Any]
    forge_scores: Dict[str, Any]


def _forge_text(case: BenchCase) -> str:
    result = run_pipeline(
        title=case.title,
        question=case.question,
        domain=case.domain,
        keywords=case.keywords,
        max_trials=2,
    )
    # Prefer full memo; fall back to concatenation
    for art in result.artifacts:
        if art.name == "research_memo":
            return art.content
    return "\n\n".join(a.content for a in result.artifacts)


def run_benchmark(cases: Optional[List[BenchCase]] = None) -> Dict[str, Any]:
    cases = cases or BENCHMARK_CASES
    rows: List[CaseResult] = []
    for case in cases:
        base_txt = baseline_answer(
            case.title, case.question, case.domain, case.keywords
        )
        forge_txt = _forge_text(case)
        b = score_document(base_txt, case.domain, case.keywords)
        f = score_document(forge_txt, case.domain, case.keywords)
        b_t = toulmin_coverage(b)
        f_t = toulmin_coverage(f)
        rows.append(
            CaseResult(
                id=case.id,
                domain=case.domain,
                title=case.title,
                baseline_overall=b.overall(),
                forge_overall=f.overall(),
                baseline_toulmin=b_t,
                forge_toulmin=f_t,
                lift_overall=round(f.overall() - b.overall(), 4),
                lift_toulmin=round(f_t - b_t, 4),
                baseline_scores=b.to_dict(),
                forge_scores=f.to_dict(),
            )
        )

    n = len(rows)
    avg_base = sum(r.baseline_overall for r in rows) / n
    avg_forge = sum(r.forge_overall for r in rows) / n
    avg_bt = sum(r.baseline_toulmin for r in rows) / n
    avg_ft = sum(r.forge_toulmin for r in rows) / n
    wins = sum(1 for r in rows if r.forge_overall > r.baseline_overall)
    toulmin_wins = sum(1 for r in rows if r.forge_toulmin > r.baseline_toulmin)

    summary = {
        "n_cases": n,
        "avg_baseline_overall": round(avg_base, 4),
        "avg_forge_overall": round(avg_forge, 4),
        "avg_lift_overall": round(avg_forge - avg_base, 4),
        "avg_lift_overall_pct": round(
            100 * (avg_forge - avg_base) / max(avg_base, 1e-6), 1
        ),
        "avg_baseline_toulmin": round(avg_bt, 4),
        "avg_forge_toulmin": round(avg_ft, 4),
        "avg_lift_toulmin": round(avg_ft - avg_bt, 4),
        "avg_lift_toulmin_pct": round(100 * (avg_ft - avg_bt) / max(avg_bt, 1e-6), 1),
        "forge_wins_overall": wins,
        "forge_wins_toulmin": toulmin_wins,
        "metric_notes": (
            "Overall = weighted Toulmin completeness + structure/actionability/humility. "
            "Toulmin coverage = fraction of {claim, grounds, warrant, rebuttal, qualifier} "
            "present at score>=0.5. Deterministic, no external LLM judge."
        ),
    }
    return {
        "summary": summary,
        "cases": [asdict(r) for r in rows],
    }


def write_benchmark_reports(out_dir: str | Path) -> Dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = run_benchmark()
    (out / "benchmark_results.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    s = report["summary"]
    lines = [
        "# Claim Lattice vs Baseline Q&A — Benchmark Report",
        "",
        f"Cases: **{s['n_cases']}**",
        "",
        "## Summary",
        "",
        "| Metric | Baseline | Epistemic Forge | Lift |",
        "|---|---:|---:|---:|",
        f"| Overall quality (0–1) | {s['avg_baseline_overall']:.3f} | {s['avg_forge_overall']:.3f} | **+{s['avg_lift_overall']:.3f} ({s['avg_lift_overall_pct']:.0f}%)** |",
        f"| Toulmin coverage (0–1) | {s['avg_baseline_toulmin']:.3f} | {s['avg_forge_toulmin']:.3f} | **+{s['avg_lift_toulmin']:.3f} ({s['avg_lift_toulmin_pct']:.0f}%)** |",
        f"| Wins (overall) | — | **{s['forge_wins_overall']}/{s['n_cases']}** | — |",
        f"| Wins (Toulmin) | — | **{s['forge_wins_toulmin']}/{s['n_cases']}** | — |",
        "",
        "## Per-case results",
        "",
        "| ID | Domain | Baseline | Forge | Δ Overall | Δ Toulmin |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for c in report["cases"]:
        lines.append(
            f"| {c['id']} | {c['domain']} | {c['baseline_overall']:.3f} | "
            f"{c['forge_overall']:.3f} | +{c['lift_overall']:.3f} | +{c['lift_toulmin']:.3f} |"
        )
    lines += [
        "",
        "## Method",
        "",
        s["metric_notes"],
        "",
        "Baseline = short unstructured Q&A template (no lattice, no objections section, no staged packaging).",
        "Forge = full ARSENAL-mapped pipeline output (`research_memo`).",
        "",
        "## Academic anchor",
        "",
        "Metrics map to Toulmin's argument model (claim, data/grounds, warrant, rebuttal, qualifier).",
        "See `docs/ACADEMIC_FRAMEWORK.md`.",
        "",
    ]
    (out / "BENCHMARK.md").write_text("\n".join(lines), encoding="utf-8")
    return report
