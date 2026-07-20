# Contributing to Epistemic Forge

Welcome! **Epistemic Forge** is not just another LLM Q&A wrapper. We are building a local-first, structurally rigorous engine that maps fuzzy research into **Toulmin-anchored claim lattices**. If you're tired of "confident mush" from LLMs, you're in the right place.

## 🧠 Architectural Philosophy
Before contributing, understand our core components:
1. **The Toulmin Model:** Every answer must be broken down into: Claim, Data, Warrant, Backing, Rebuttal, and Qualifier.
2. **Claim Lattices:** Arguments are graphs, not linear text.
3. **Local-First:** We prioritize executing without paid API dependencies wherever possible.

## 🛠️ How to Contribute

### Adding or Modifying Argument Logic
- If you are tweaking the prompt that generates the claim lattice, you must ensure it does not break the JSON/Structured output parsers.
- Any change to the reasoning engine MUST be benchmarked against our 10 edge cases.

### Running the Benchmark
We boast a `+199%` quality improvement over baseline Q&A. If you submit a PR that alters the core logic, you must run the evaluation suite:
```bash
# Example (adjust based on actual test script)
pytest tests/test_toulmin_logic.py
```

### Pull Requests
Please use the provided PR template. Describe exactly how your change impacts the lattice generation or the benchmark score.
