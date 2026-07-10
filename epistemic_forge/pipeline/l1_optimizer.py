"""L1 — Instruction Optimizer (APE baseline + OPRO-style iterative climb)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from epistemic_forge.models import ProjectSpec, RouteDecision


@dataclass
class InstructionCandidate:
    text: str
    score: float
    source: str  # ape | opro | seed


# Seed instruction bank (APE-like forward generation from demos/patterns)
_SEED_BANK: Dict[str, List[str]] = {
    "research": [
        "Map the claim lattice: state the core thesis, 3 supports, 3 objections, and a residual uncertainty.",
        "Write a methods-aware brief: question → hypotheses → evidence plan → falsifiers → next experiment.",
        "Produce a literature-shaped outline with gaps, tensions, and a single sharp contribution sentence.",
    ],
    "philosophy": [
        "Clarify the concept: define terms, distinguish near-neighbors, then test edge cases dialectically.",
        "Run a steelman-then-critique: strongest opposing view first, then precise fracture points.",
        "Build a dialectic chain: thesis → antithesis → synthesis, naming what remains unresolved.",
    ],
    "writing": [
        "Draft for a skeptical expert: lead with the claim, then evidence, then limits, then action.",
        "Use a problem–stakes–insight–proof–so-what arc with one vivid concrete example.",
        "Write tight: one idea per paragraph; every paragraph ends with a move that advances the thesis.",
    ],
    "freelance": [
        "Client brief mode: goal, constraints, deliverables, timeline, risks, acceptance criteria, open questions.",
        "Scope like a pro: in-scope / out-of-scope / assumptions / dependencies / revision policy.",
        "Proposal mode: problem reframed in client language, approach, milestones, price logic, next step.",
    ],
    "kaggle": [
        "Competition notebook spine: EDA → baseline → CV → error analysis → one honest improvement.",
        "Leakage-aware plan: validate splits, target definition, feature hygiene, metric alignment.",
        "Ship a reproducible baseline first; only then ablate one idea with clear lift measurement.",
    ],
    "hybrid": [
        "Hybrid research kit: claim lattice + client-ready summary + optional code/experiment next step.",
        "Translate insight into three artifacts: memo, checklist, and executable skeleton.",
        "Epistemic forge mode: extract claims, stress-test them, refine language, package for action.",
    ],
}


def _domain_key(spec: ProjectSpec) -> str:
    return spec.domain.value if spec.domain.value in _SEED_BANK else "hybrid"


def _score_instruction(text: str, spec: ProjectSpec) -> float:
    """Heuristic scorer (stand-in for LLM likelihood / task accuracy)."""
    score = 0.4
    t = text.lower()
    q_tokens = set(spec.question.lower().replace("?", " ").split())
    overlap = sum(1 for w in q_tokens if len(w) > 3 and w in t)
    score += min(0.25, overlap * 0.03)
    for kw in spec.keywords:
        if kw.lower() in t:
            score += 0.05
    # Structure bonuses (APE-like preference for general, actionable instructions)
    for cue in ("claim", "evidence", "object", "baseline", "deliverable", "limit", "next"):
        if cue in t:
            score += 0.03
    if 40 <= len(text) <= 220:
        score += 0.08
    if len(text) > 280:
        score -= 0.1
    # Domain fit
    d = _domain_key(spec)
    if d == "kaggle" and any(x in t for x in ("cv", "baseline", "leak", "metric", "eda")):
        score += 0.1
    if d == "freelance" and any(x in t for x in ("client", "scope", "deliverable", "milestone")):
        score += 0.1
    if d == "philosophy" and any(x in t for x in ("dialect", "concept", "steelman", "edge")):
        score += 0.1
    return max(0.0, min(1.0, score))


def ape_generate(spec: ProjectSpec, k: int = 5) -> List[InstructionCandidate]:
    """APE-style: generate candidates from seed bank + light mutations."""
    seeds = list(_SEED_BANK[_domain_key(spec)])
    # Mutations (forward generation stand-in)
    mutations = [
        f"For the question «{spec.question[:80]}»: " + s for s in seeds[:2]
    ]
    tailored = [
        f"Audience={spec.audience}. Focus keywords={', '.join(spec.keywords[:5]) or 'n/a'}. " + seeds[0]
    ]
    pool = seeds + mutations + tailored
    cands = [
        InstructionCandidate(text=p, score=_score_instruction(p, spec), source="ape")
        for p in pool
    ]
    # Dedup
    seen = set()
    uniq: List[InstructionCandidate] = []
    for c in cands:
        key = c.text.strip().lower()
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    uniq.sort(key=lambda x: x.score, reverse=True)
    return uniq[:k]


def opro_evolve(
    seeds: Sequence[InstructionCandidate],
    spec: ProjectSpec,
    steps: int = 3,
    per_step: int = 2,
) -> List[InstructionCandidate]:
    """OPRO-style: climb using score history in a textual meta-prompt state."""
    history: List[InstructionCandidate] = list(seeds)
    for step in range(steps):
        ranked = sorted(history, key=lambda x: x.score)[-5:]
        # Meta-prompt conditioning (textual state) → propose variants of best
        best = ranked[-1]
        proposals = [
            best.text.replace("Write", "Synthesize").replace("Produce", "Forge"),
            best.text + " Explicitly separate knowns, unknowns, and bets.",
            "Using prior high-scoring instructions, " + best.text[0].lower() + best.text[1:],
        ]
        for prop in proposals[:per_step]:
            # Filters inspired by OPRO (length, leak tokens)
            if len(prop) > 500 or "INS" in prop:
                continue
            sc = _score_instruction(prop, spec) + 0.02 * step  # slight climb bias
            sc = min(1.0, sc)
            history.append(InstructionCandidate(text=prop, score=sc, source="opro"))
    # Dedupe + rank
    best_by_text: Dict[str, InstructionCandidate] = {}
    for c in history:
        k = c.text.strip().lower()
        if k not in best_by_text or c.score > best_by_text[k].score:
            best_by_text[k] = c
    out = sorted(best_by_text.values(), key=lambda x: x.score, reverse=True)
    return out


def optimize_instruction(
    spec: ProjectSpec, route: RouteDecision
) -> Tuple[str, List[InstructionCandidate]]:
    """L1 entry: ape | opro | cascade | off."""
    mode = route.l1_mode
    if mode == "off" or not route.activate.get("ape", True) and not route.activate.get(
        "opro", False
    ):
        default = (
            f"Answer carefully for {spec.audience}: {spec.question} "
            "Separate claims, evidence, limits, and next actions."
        )
        return default, [InstructionCandidate(default, 0.5, "seed")]

    ape_cands = ape_generate(spec)
    if mode == "ape" or not route.activate.get("opro", False):
        return ape_cands[0].text, ape_cands

    if mode == "opro":
        seeds = ape_cands[:2] or [
            InstructionCandidate("Solve the problem carefully.", 0.3, "seed")
        ]
        evolved = opro_evolve(seeds, spec)
        return evolved[0].text, evolved

    # cascade
    evolved = opro_evolve(ape_cands[:3], spec)
    return evolved[0].text, evolved
