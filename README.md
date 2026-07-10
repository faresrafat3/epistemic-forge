# Epistemic Forge

**An ARSENAL-powered kit for turning messy questions into claim lattices, dialectic briefs, freelance scopes, and Kaggle notebook spines.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with ARSENAL](https://img.shields.io/badge/built%20with-ARSENAL%20L0--L6-purple.svg)](https://github.com/faresrafat3/arsenal-unified-master-pipeline)

Epistemic Forge is a **local-first Python package** (no paid API required) that implements a faithful, practical slice of the [ARSENAL](https://github.com/faresrafat3/arsenal-unified-master-pipeline) unified agent pipeline:

| Layer | ARSENAL idea | In this repo |
|---|---|---|
| **L0** | Technique routing | Domain → families + layer flags |
| **L1** | APE + OPRO | Seed instructions + score-history climb |
| **L2** | Meta conductor | Claim / dialectic / writing / freelance / Kaggle experts |
| **L3** | ToT (+ LATS cascade) | Beam search over framings; optional rollout polish |
| **L4** | Self-Refine | Multi-aspect critique → revise loop |
| **L5** | Reflexion + Voyager | Verbal trial memory + skill library |
| **L6** | Stage shell | Artifacts, executive summary, peer-review rubric |

> Novel angle: a **claim lattice** as the shared intermediate representation across philosophy, research writing, freelancing, and Kaggle planning—so epistemic humility travels with the deliverable.

---

## Install

```bash
git clone https://github.com/faresrafat3/epistemic-forge.git
cd epistemic-forge
pip install -e ".[dev]"
```

## Quick start (CLI)

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

## Python API

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
| `research_memo.md` | Full lattice + framing + limits + actions |
| `client_brief.json` | Freelance pack (when domain fits) |
| `kaggle_spine.md` | Notebook spine (when domain fits) |
| `result.json` | Full machine-readable trace (route, trials, search nodes) |
| `MANIFEST.json` | Score, review, file list |

## Domains

`research` · `philosophy` · `writing` · `freelance` · `kaggle` · `hybrid`

## Why this is not “another prompt dump”

1. **Executable pipeline** with tests (`pytest`)  
2. **Shared IR** (claims) across domains  
3. **Explicit ARSENAL mapping** with a run log: [`docs/ARSENAL_RUN_LOG.md`](docs/ARSENAL_RUN_LOG.md)  
4. **Memory**: verbal lessons + reusable skills  
5. **Publishable packaging**: `pyproject.toml`, CLI entrypoint, MIT license  

## Project layout

```text
epistemic_forge/
  pipeline/     # L0–L6 orchestration
  experts/      # L2 specialist modules
  memory/       # Reflexion + skill library
  io/           # export
  data/samples/ # demo specs
tests/
docs/ARSENAL_RUN_LOG.md
examples/
```

## Tests

```bash
pytest -q
```

## Design principles (from ARSENAL)

1. Router first  
2. Optimize the instruction (APE / OPRO cascade)  
3. Conduct via experts  
4. Search framings deliberately (ToT; cascade when code-like)  
5. Refine with multi-aspect feedback  
6. Remember failures and skills  
7. Ship staged artifacts + review  

## Related work

- ARSENAL master pipeline: https://github.com/faresrafat3/arsenal-unified-master-pipeline  
- Extractions archive: https://github.com/faresrafat3/llm-agent-research-extractions  

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Epistemic Forge **scaffolds thinking and packaging**. It does not replace domain expertise, human ethics review, or competition rules. Treat outputs as **provisional** claims with explicit limits.
