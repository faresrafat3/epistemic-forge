#!/usr/bin/env python3
"""Run three domain demos and print scores."""

from pathlib import Path

from epistemic_forge.io.export import export_result
from epistemic_forge.pipeline.arsenal_run import run_pipeline

DEMOS = [
    dict(
        title="Predictive minds and blame",
        question="If the brain is a prediction machine, what happens to moral responsibility?",
        domain="philosophy",
        keywords=["predictive processing", "responsibility"],
        out="runs/demo_philosophy",
    ),
    dict(
        title="Imbalanced tabular baseline",
        question="What is an honest baseline plan for a noisy imbalanced Kaggle table?",
        domain="kaggle",
        keywords=["imbalance", "baseline", "cv", "leakage"],
        out="runs/demo_kaggle",
    ),
    dict(
        title="Climate-tech research sprint",
        question="How do I scope a 2-week research sprint for a climate-tech founder?",
        domain="freelance",
        keywords=["sprint", "scope", "founder"],
        out="runs/demo_freelance",
    ),
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for d in DEMOS:
        out = root / d.pop("out")
        result = run_pipeline(max_trials=2, **d)
        export_result(result, out)
        print(
            f"{d['domain']:12} score={result.final_score:.3f} "
            f"review={result.peer_review['verdict']} → {out}"
        )


if __name__ == "__main__":
    main()
