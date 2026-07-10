# Epistemic Forge

**Stop shipping confident mush.**  
Turn messy research, philosophy, freelance, and Kaggle questions into **claim lattices**—structured arguments with evidence slots, objections, confidence, and next actions.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-6%20passed-brightgreen.svg)](tests/)
[![Built with ARSENAL](https://img.shields.io/badge/built%20with-ARSENAL%20L0--L6-purple.svg)](https://github.com/faresrafat3/arsenal-unified-master-pipeline)
[![Benchmark](https://img.shields.io/badge/Toulmin%20coverage-+231%25%20vs%20baseline-orange.svg)](docs/benchmark/BENCHMARK.md)

Local-first Python package (**no paid API required**). Implements a practical slice of the [ARSENAL](https://github.com/faresrafat3/arsenal-unified-master-pipeline) L0–L6 pipeline.

---

## The problem

Experts and freelancers constantly answer hard questions under uncertainty:

- a founder wants a **2-week research sprint** scoped *now*
- a Kaggle teammate wants a **leakage-safe baseline**, not vibes
- a seminar needs a **dialectic**, not a blog take

Default LLM / one-shot Q&A style fails the same way every time:

| Failure mode | What you get |
|---|---|
| Hidden assumptions | Smooth prose, no load-bearing claims listed |
| No objections | One-sided answers that collapse in review |
| False precision | Confident tone without confidence labels |
| Weak packaging | No acceptance criteria, checklist, or next action |

**Epistemic Forge** forces a shared intermediate representation—a **claim lattice**—then packages it for the domain you’re in.

Academic anchor: **Toulmin’s model of argument** (claim · grounds · warrant · rebuttal · qualifier).  
See [`docs/ACADEMIC_FRAMEWORK.md`](docs/ACADEMIC_FRAMEWORK.md) · Toulmin, *The Uses of Argument* (1958/2003).

---

## Before / after (real run)

**Question:** *If the brain is a prediction machine, what happens to moral responsibility?*

### Before — baseline one-shot Q&A
**Overall 0.37** · **Toulmin coverage 0.40**

```text
Predictive processing and moral responsibility: On the question «If the brain
is a prediction machine, what happens to moral responsibility?», a reasonable
view is that responsibility still applies when agents can track norms, even if
cognition is predictive. Keywords: predictive processing, responsibility, agency.
In short, keep blame practices but update the metaphysics of agency.
```

### After — Epistemic Forge claim lattice
**Overall 1.00** · **Toulmin coverage 1.00** on this memo  
(full folder: [`examples/worked/01_philosophy_predictive_responsibility/`](examples/worked/01_philosophy_predictive_responsibility/))

The forge memo adds: explicit **claim IDs**, **supports**, **objections**, **confidence**, **dialectic (thesis/antithesis/steelman/synthesis)**, **limits & unknowns**, and **next actions**—the slots baseline Q&A skips.

Side-by-side writeup: [`examples/worked/BEFORE_AFTER_philosophy.md`](examples/worked/BEFORE_AFTER_philosophy.md)

---

## Benchmark (10 examples, measurable)

We compare **claim-lattice pipeline output** vs a **simple Q&A baseline** on **10 fixed cases** (philosophy ×3, kaggle ×3, freelance ×3, hybrid ×1).

Scoring is **deterministic** (no paid judge model): weighted Toulmin completeness + structure / actionability / humility.

| Metric | Baseline Q&A | Epistemic Forge | Lift |
|---|---:|---:|---:|
| **Overall quality (0–1)** | 0.319 | **0.951** | **+0.633 (~+199%)** |
| **Toulmin coverage (0–1)** | 0.260 | **0.860** | **+0.600 (~+231%)** |
| **Wins (overall)** | — | **10 / 10** | — |
| **Wins (Toulmin)** | — | **10 / 10** | — |

Per-case table and method notes: [`docs/benchmark/BENCHMARK.md`](docs/benchmark/BENCHMARK.md) · raw JSON: [`docs/benchmark/benchmark_results.json`](docs/benchmark/benchmark_results.json)

```bash
python scripts/run_benchmark.py --out docs/benchmark
```

| ID | Domain | Baseline | Forge | Δ Overall |
|---|---|---:|---:|---:|
| p1–p3 | philosophy | ~0.37 | ~1.00 | ~+0.63 |
| k1–k3 | kaggle | ~0.30 | ~0.94 | ~+0.64 |
| f1–f3 | freelance | ~0.23 | ~0.90 | ~+0.67 |
| h1 | hybrid | 0.50 | 1.00 | +0.50 |

> Interpretation for portfolio readers: the gain is not “smarter vibes”—it is **argument slot coverage + packaging**. That is what clients, reviewers, and hiring managers can inspect.

---

## Worked examples (full outputs)

| Domain | Example | Score / review |
|---|---|---|
| **Philosophy** | [Predictive processing & responsibility](examples/worked/01_philosophy_predictive_responsibility/) | 0.66 · minor revisions |
| **Kaggle** | [Imbalanced tabular baseline](examples/worked/02_kaggle_imbalanced_baseline/) | 0.71 · minor revisions |
| **Freelance** | [Climate-tech 2-week sprint](examples/worked/03_freelance_climate_sprint/) | 0.71 · minor revisions |

Index: [`examples/worked/README.md`](examples/worked/README.md)

Each folder includes `executive_summary.md`, `research_memo.md`, domain packs (`client_brief.json` / `kaggle_spine.md`), and full `result.json` (route, trials, search nodes).

---

## Install

```bash
git clone https://github.com/faresrafat3/epistemic-forge.git
cd epistemic-forge
pip install -e ".[dev]"
pytest -q
```

## Quick start

```bash
epistemic-forge \
  --title "Predictive minds and blame" \
  --question "If the brain is a prediction machine, what happens to moral responsibility?" \
  --domain philosophy \
  --keywords "predictive processing,agency,responsibility" \
  --out runs/philosophy_demo
```

```bash
epistemic-forge \
  --title "Imbalanced tabular baseline" \
  --question "What is an honest baseline plan for a noisy imbalanced Kaggle table?" \
  --domain kaggle \
  --keywords "imbalance,cv,leakage,baseline" \
  --out runs/kaggle_demo
```

```bash
epistemic-forge \
  --title "Climate-tech research sprint" \
  --question "How do I scope a 2-week research sprint for a climate-tech founder?" \
  --domain freelance \
  --keywords "sprint,scope,founder" \
  --out runs/freelance_demo
```

### Python API

```python
from epistemic_forge import run_pipeline
from epistemic_forge.io.export import export_result

result = run_pipeline(
    title="Epistemic freelancing",
    question="How can freelancers package uncertain research without overclaiming?",
    domain="hybrid",
    keywords=["freelance", "research", "claims"],
)
print(result.final_score, result.peer_review["verdict"])
export_result(result, "runs/hybrid_demo")
```

## What you get in `--out`

| File | Purpose |
|---|---|
| `executive_summary.md` | One-pager |
| `research_memo.md` | Claim lattice + framing + limits + actions |
| `client_brief.json` | Freelance pack (when domain fits) |
| `kaggle_spine.md` | Notebook spine (when domain fits) |
| `result.json` | Full trace (route, trials, search nodes) |
| `MANIFEST.json` | Score, review, file list |

## Domains

`research` · `philosophy` · `writing` · `freelance` · `kaggle` · `hybrid`

---

## ARSENAL mapping (how the sausage is made)

| Layer | ARSENAL idea | In this repo |
|---|---|---|
| **L0** | Technique routing | Domain → families + layer flags |
| **L1** | APE + OPRO | Seed instructions + score-history climb |
| **L2** | Meta conductor | Claim / dialectic / writing / freelance / Kaggle experts |
| **L3** | ToT (+ LATS cascade) | Beam search over framings; optional rollout polish |
| **L4** | Self-Refine | Multi-aspect critique → revise loop |
| **L5** | Reflexion + Voyager | Verbal trial memory + skill library |
| **L6** | Stage shell | Artifacts, executive summary, peer-review rubric |

Design log: [`docs/ARSENAL_RUN_LOG.md`](docs/ARSENAL_RUN_LOG.md)

## Project layout

```text
epistemic_forge/
  pipeline/      # L0–L6 orchestration
  experts/       # domain specialists
  memory/        # Reflexion + skills
  benchmark/     # baseline vs forge metrics
  io/            # export
examples/worked/ # full philosophy / kaggle / freelance runs
docs/benchmark/  # numbers + method
docs/ACADEMIC_FRAMEWORK.md
tests/
```

## Tests & regenerate portfolio assets

```bash
pytest -q
python scripts/run_benchmark.py --out docs/benchmark
python scripts/generate_worked_examples.py
```

## Related

- ARSENAL: https://github.com/faresrafat3/arsenal-unified-master-pipeline  
- Extractions archive: https://github.com/faresrafat3/llm-agent-research-extractions  

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Epistemic Forge **scaffolds thinking and packaging**. It does not replace domain expertise, ethics review, or competition rules. Benchmark scores are **automatic structural metrics**, not human truth judgments. Treat outputs as **provisional** claims with explicit limits.
