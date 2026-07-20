<div align="center">

# 🧠 Epistemic Forge

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Built with ARSENAL](https://img.shields.io/badge/built%20with-ARSENAL%20L0--L6-6c5ce7.svg?style=for-the-badge)](https://github.com/faresrafat3/arsenal-unified-master-pipeline)
[![Benchmark](https://img.shields.io/badge/Toulmin%20Coverage-+231%25%20vs%20baseline-orange.svg?style=for-the-badge)](docs/benchmark/BENCHMARK.md)

**Stop shipping confident mush.**  
Turn messy research, philosophy, freelance, and Kaggle questions into **claim lattices** — structured arguments with evidence slots, objections, confidence, and next actions.

</div>

---

## 🛑 The Problem

Experts and freelancers constantly answer hard questions under uncertainty:
- A founder wants a **2-week research sprint** scoped *now*.
- A Kaggle teammate wants a **leakage-safe baseline**, not vibes.
- A seminar needs a **dialectic**, not a blog take.

Default LLM / one-shot Q&A style fails the same way every time: smooth prose with hidden assumptions, no objections, and false precision.

## 🛠️ The Solution: Epistemic Forge
A local-first Python package (**no paid API required**) that implements a practical slice of the [ARSENAL](https://github.com/faresrafat3/arsenal-unified-master-pipeline) L0–L6 pipeline. It forces the LLM to construct a **Toulmin-anchored claim lattice** before generating an answer.

### Key Features
- 📊 **Toulmin-Anchored Benchmark**: +199% overall quality vs baseline Q&A on 10 edge cases.
- 🔗 **Claim Lattices**: Maps claims, warrants, backing, and rebuttals automatically.
- ⚡ **Local-First CLI**: Fully functional directly from your terminal.

## 🚀 Getting Started

```bash
git clone https://github.com/faresrafat3/epistemic-forge.git
cd epistemic-forge
pip install -r requirements.txt
python main.py --query "Is RAG strictly better than Long-Context LLMs?"
```
