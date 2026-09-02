# Review Remediation Plan — Epistemic Forge

This document maps every finding from the July 22, 2026 technical review to a
concrete fix that has been (or will be) applied. The goal is to address the
**legitimate engineering issues** raised, while being honest about scope:
formal epistemic-logic research (Kripke models, AGM belief revision, trained
PRMs, true MCTS-UCB) is a multi-month research program and is documented here
as a roadmap item rather than overclaimed as "done".

## Priority 1 — CI/CD is broken & non-enforcing (CRITICAL)
- [x] Rewrite `.github/workflows/ci.yml`: remove `|| echo`, make `pytest` blocking.
- [x] Add coverage reporting (`pytest-cov`) with a floor.
- [x] Make `ruff` a **blocking** lint gate (was `--exit-zero` warning only).
- [x] Add `mypy` (type checking) and `bandit` (security scan) to CI.
- [x] Fix `tests.yml` matrix + blocking tests + coverage.

## Priority 2 — Critical correctness bugs
- [x] Fix `test_l2_conductor_routing`: it passed `spec.domain.value` (str) where
      `SemanticConductor._route_experts(spec: ProjectSpec)` is expected.
- [x] `arsenal_run.py`: move `route_project` import to module top (was imported
      inside `run()`).
- [x] `arsenal_run.py`: remove unreachable dead code after `return`.
- [x] `arsenal_run.py`: `run_pipeline` used `raise SystemExit(1)` in library code →
      replaced with a re-raised `PipelineError` (CLI still does `sys.exit`).

## Priority 3 — Code integrity (RED FLAG)
- [x] Delete `patch_run.py` (string-replacement hack). Its *intended* logging was
      folded into `arsenal_run.py` properly via a normal edit.

## Priority 4 — Error handling hygiene
- [x] `memory/economy.py`: bare `except: pass` → `except Exception`.
- [x] `memory/skill_library.py`: bare `except:` in `get_all_skills` → `except Exception`.
- [x] General: no new bare excepts introduced; ruff `E722` enforced in CI.

## Priority 5 — Security
- [x] `llm.py`: stop writing API keys into `os.environ` globally (redundant — the
      key is already passed per-call via `call_params["api_key"]`).
- [x] `llm.py`: add input validation (`validate_messages`) — reject empty/oversized
      prompts before dispatch, capping token blow-up.
- [x] `l1_5_adas.py`: harden dynamic schema generation — bound field count, validate
      identifiers, reject empty/unsafe blueprints (no arbitrary code execution; only
      Pydantic `create_model` from sanitized names).

## Priority 6 — Dependency hygiene
- [x] Add `ruff`, `pytest-cov`, `mypy`, `bandit`, `types-requests` to `dev`.
- [x] Move `streamlit` out of core deps into an optional `ui` extra (non-UI users
      no longer pull a heavy web framework).
- [ ] Lock file (`uv.lock` / `pip-compile`) — tracked as follow-up; see CHANGELOG.

## Priority 7 — Testing (was <10% coverage)
- [x] Fix existing test + big expansion: `llm` offline fallback, `router`,
      `l1_optimizer`, `l2_conductor`, `l1_5_adas`, `l3_search`, `l4_refine`,
      `l6_stages`, `skill_library` (with injected fake client), `economy`,
      `models` (Pydantic constraints), `cli` arg parsing, and a **full offline
      pipeline integration test**.
- [x] Coverage floor enforced in CI (start modest, raise as suite grows).

## Priority 8 — Architecture honesty
- [x] `pipeline/machine.py`: explicit, data-driven **stage registry** (`L0→L6`)
      with per-stage enable predicates, plus a typed `PipelineContext`
      (replaces ad-hoc `Dict[str, Any]`), so routing is inspectable, not hidden
      in `if` statements.
- [x] Async: `llm.agenerate_structured` (real `litellm.acompletion` + instructor),
      parallel `conduct_async` (experts run concurrently via `asyncio.gather`),
      and `arun_pipeline` entrypoint — addresses "no async / sequential experts".

## Priority 9 — Documentation honesty
- [x] README: mark the "85% cost / 80% fewer tokens" figures as **illustrative
      targets, not independently benchmarked**; add a "What 'Epistemic' Means
      Here" section clarifying it is structured Toulmin prompting, not formal
      logic; add architecture diagram.
- [x] `docs/ARCHITECTURE.md` with Mermaid diagram + data contracts.
- [x] `docs/BENCHMARKS.md` describing methodology + current caveats.
- [x] `CHANGELOG.md`.

## Out of scope / roadmap (documented honestly, NOT overclaimed)
- Formal Dynamic Epistemic Logic / Kripke structures / AGM belief revision.
- Trained Process Reward Model (current "PRM" is LLM-as-Judge prompting).
- True MCTS with UCB / value backpropagation (current L3 is bounded beam enumeration).
- Full multi-agent message-passing communication layer (current "experts" are
  sequential strategy-pattern nodes).
- These remain research roadmap items; the naming is now qualified in docs.
