# Academic framework: Claim lattices and Toulmin’s model of argument

Epistemic Forge treats a **claim lattice** as a lightweight, multi-domain intermediate representation. The design is deliberately aligned with classical **argumentation theory**, especially Stephen Toulmin’s model of argument.

## Primary citation

> Toulmin, S. E. (1958/2003). *The Uses of Argument* (Updated ed.). Cambridge University Press.

Toulmin proposed that everyday and scientific arguments are better analyzed as **functional roles** than as pure syllogisms. The core layout (commonly taught in writing & critical reasoning) is:

| Toulmin element | Role | Epistemic Forge mapping |
|---|---|---|
| **Claim** | The conclusion being advanced | `Claim.text` (thesis node) |
| **Data / Grounds** | Evidence supporting the claim | `Claim.support[]` |
| **Warrant** | Principle linking data → claim | Instruction + expert integration narrative (“why this structure improves decisions”) |
| **Backing** | Support for the warrant | Domain experts (methods notes, baselines, client constraints) |
| **Qualifier** | Strength / modality of the claim | `Claim.confidence` (`sure` / `likely` / `possible` / `weak`) |
| **Rebuttal** | Conditions of exception / objections | `Claim.objections[]` + dialectic antithesis/steelman |

## Why this fits the product

1. **Portable across domains** — The same slots structure a philosophy thesis, a freelance acceptance criterion, or a Kaggle “honest baseline” claim.  
2. **Humility is first-class** — Qualifiers and rebuttals are not optional decoration; they are scored in the benchmark.  
3. **Compatible with modern AI scaffolding** — Self-critique loops (Self-Refine / Reflexion) naturally *fill* rebuttal and qualifier slots rather than only polishing style.

## Related academic threads (secondary)

- **Argumentation schemes & critical questions** — Walton, Reed, Macagno (*Argumentation Schemes*, 2008): each scheme comes with defeaters; our objections list is a practical subset.  
- **IBIS / design rationale** — Kunz & Rittel (1970): issues–positions–arguments; our lattice is a compressed position/argument graph for delivery, not a full IBIS database.  
- **Computational argumentation** — Dung’s abstract argumentation frameworks (1995) formalize attack relations; we stay at the *informal-logic packaging* layer for human-readable deliverables.

## How the benchmark uses Toulmin

The benchmark metrics in `epistemic_forge/benchmark/metrics.py` score documents for presence of:

- claim, grounds, warrant, rebuttal, qualifier  

plus packaging features (structure, actionability, humility).  
**Toulmin coverage** = fraction of the five core slots detected at score ≥ 0.5.

This is an **automatic, deterministic proxy**—useful for regression testing and portfolio evidence—not a substitute for human argument evaluation.

## Practical reading

- Toulmin (2003), ch. on the layout of arguments.  
- Introductory teaching notes on Toulmin in composition studies (claim–evidence–warrant).  
- For AI context: connect to self-critique / debate papers only as *process*, while Toulmin remains the *structure* of the artifact.

## One-sentence thesis

> Epistemic Forge operationalizes Toulmin’s layout as a **shared claim lattice IR**, then runs an ARSENAL-style pipeline to fill, stress-test, and package those slots for research, freelancing, and applied ML planning.
