# Claim Lattice vs Baseline Q&A — Benchmark Report

Cases: **10**

## Summary

| Metric | Baseline | Epistemic Forge | Lift |
|---|---:|---:|---:|
| Overall quality (0–1) | 0.319 | 0.951 | **+0.633 (199%)** |
| Toulmin coverage (0–1) | 0.260 | 0.860 | **+0.600 (231%)** |
| Wins (overall) | — | **10/10** | — |
| Wins (Toulmin) | — | **10/10** | — |

## Per-case results

| ID | Domain | Baseline | Forge | Δ Overall | Δ Toulmin |
|---|---|---:|---:|---:|---:|
| p1 | philosophy | 0.375 | 1.000 | +0.625 | +0.600 |
| p2 | philosophy | 0.361 | 0.999 | +0.637 | +0.600 |
| p3 | philosophy | 0.361 | 1.000 | +0.639 | +0.600 |
| k1 | kaggle | 0.329 | 0.935 | +0.606 | +0.600 |
| k2 | kaggle | 0.229 | 0.935 | +0.706 | +0.600 |
| k3 | kaggle | 0.329 | 0.935 | +0.606 | +0.600 |
| f1 | freelance | 0.131 | 0.837 | +0.706 | +0.600 |
| f2 | freelance | 0.236 | 0.935 | +0.699 | +0.600 |
| f3 | freelance | 0.329 | 0.935 | +0.606 | +0.600 |
| h1 | hybrid | 0.504 | 1.000 | +0.496 | +0.600 |

## Method

Overall = weighted Toulmin completeness + structure/actionability/humility. Toulmin coverage = fraction of {claim, grounds, warrant, rebuttal, qualifier} present at score>=0.5. Deterministic, no external LLM judge.

Baseline = short unstructured Q&A template (no lattice, no objections section, no staged packaging).
Forge = full ARSENAL-mapped pipeline output (`research_memo`).

## Academic anchor

Metrics map to Toulmin's argument model (claim, data/grounds, warrant, rebuttal, qualifier).
See `docs/ACADEMIC_FRAMEWORK.md`.
