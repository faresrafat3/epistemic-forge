# Contributing

1. Fork and branch from `main`.
2. `pip install -e ".[dev]"`
3. Add tests for new experts or pipeline layers.
4. `pytest -q`
5. Open a PR with a clear ARSENAL-layer note (L0–L6) if you change routing or memory.

## Design rule

Prefer **explicit claims + limits** over flashy ungrounded generation. This project is an epistemic scaffold.
