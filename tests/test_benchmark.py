"""Benchmark metrics and suite smoke tests."""

from epistemic_forge.benchmark.baseline import baseline_answer
from epistemic_forge.benchmark.metrics import score_document, toulmin_coverage
from epistemic_forge.benchmark.suite import BENCHMARK_CASES, run_benchmark


def test_metrics_prefer_structured_lattice_like_text():
    weak = baseline_answer("T", "What should we do?", "kaggle", ["baseline"])
    strong = """
# Title
## Core question
What should we do?
## Claim
We should ship a baseline first.
Supports:
- Evidence from prior competitions shows simple models rank well early.
Objections:
- However, a weak baseline can anchor the team too low.
Confidence: provisional / likely
### Limits & unknowns
Assumptions about metric alignment remain.
### Next actions
1. Run CV baseline this week.
"""
    sw = score_document(weak, "kaggle", ["baseline"])
    ss = score_document(strong, "kaggle", ["baseline", "cv"])
    assert ss.overall() > sw.overall()
    assert toulmin_coverage(ss) >= toulmin_coverage(sw)


def test_benchmark_suite_small_smoke():
    # Run first 3 cases only for speed in unit tests
    report = run_benchmark(BENCHMARK_CASES[:3])
    assert report["summary"]["n_cases"] == 3
    assert report["summary"]["avg_forge_overall"] >= report["summary"]["avg_baseline_overall"]
    assert report["summary"]["forge_wins_overall"] >= 2
