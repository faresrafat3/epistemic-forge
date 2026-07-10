"""L3 — Tree search (ToT baseline + LATS-like escalation hooks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from epistemic_forge.models import ProjectSpec, SearchNode


@dataclass
class SearchResult:
    best_thought: str
    nodes: List[SearchNode]
    mode_used: str
    score: float


def _value_label(text: str, spec: ProjectSpec) -> float:
    """ToT-like sure/likely/impossible mapped to floats."""
    t = text.lower()
    score = 0.35
    if any(w in t for w in ("because", "evidence", "therefore", "tradeoff", "metric")):
        score += 0.2
    if any(w in t for w in ("unknown", "risk", "limit", "bias", "leak")):
        score += 0.15  # epistemic humility is valuable
    overlap = sum(1 for k in spec.keywords if k.lower() in t)
    score += min(0.2, overlap * 0.05)
    if "todo" in t or "vague" in t:
        score -= 0.2
    return max(0.05, min(0.99, score))


def tot_search(spec: ProjectSpec, bundle: Dict[str, Any], beam: int = 3, steps: int = 3) -> SearchResult:
    """Offline deliberate search over framings (ToT-style)."""
    seeds = [
        f"Frame as claim lattice: {spec.question}",
        f"Frame as experiment plan: {spec.question}",
        f"Frame as client narrative: {spec.question}",
        f"Frame as dialectic tension: {spec.question}",
        f"Frame as Kaggle baseline+ablation: {spec.question}",
    ]
    # Domain bias
    d = spec.domain.value
    if d == "philosophy":
        seeds = [seeds[3], seeds[0], seeds[2]] + seeds
    elif d == "kaggle":
        seeds = [seeds[4], seeds[1], seeds[0]] + seeds
    elif d == "freelance":
        seeds = [seeds[2], seeds[0], seeds[1]] + seeds

    nodes: List[SearchNode] = []
    frontier: List[SearchNode] = []
    for i, s in enumerate(seeds[:beam]):
        n = SearchNode(id=f"n0_{i}", thought=s, value=_value_label(s, spec), meta={"step": 0})
        nodes.append(n)
        frontier.append(n)

    for step in range(1, steps):
        candidates: List[SearchNode] = []
        for parent in frontier:
            expansions = [
                parent.thought + " → add falsifiers and residual unknowns.",
                parent.thought + " → prioritize one high-leverage next action.",
                parent.thought + " → stress-test with a steelman objection.",
            ]
            for j, e in enumerate(expansions):
                cid = f"n{step}_{parent.id}_{j}"
                child = SearchNode(
                    id=cid,
                    thought=e,
                    value=_value_label(e, spec),
                    parent_id=parent.id,
                    meta={"step": step},
                )
                parent.children.append(cid)
                nodes.append(child)
                candidates.append(child)
        # Greedy beam select
        candidates.sort(key=lambda x: x.value, reverse=True)
        frontier = candidates[:beam]

    best = max(nodes, key=lambda x: x.value)
    return SearchResult(best_thought=best.thought, nodes=nodes, mode_used="tot", score=best.value)


def lats_polish(spec: ProjectSpec, tot: SearchResult) -> SearchResult:
    """Lightweight LATS-like escalation: env/test-aware refinement of best path."""
    # Simulate rollout with "executor feedback"
    feedback = []
    if spec.domain.value in {"kaggle", "hybrid"}:
        feedback.append("Check CV leakage and metric alignment before fancy models.")
    if spec.domain.value in {"freelance", "hybrid"}:
        feedback.append("Add acceptance criteria and revision policy.")
    if not feedback:
        feedback.append("Add one concrete example and one measurable success signal.")

    improved = tot.best_thought + " | rollout: " + " ".join(feedback)
    node = SearchNode(
        id="lats_best",
        thought=improved,
        value=min(0.99, tot.score + 0.08),
        parent_id=None,
        meta={"mode": "lats_rollout", "feedback": feedback},
    )
    nodes = list(tot.nodes) + [node]
    return SearchResult(
        best_thought=improved, nodes=nodes, mode_used="cascade_tot_lats", score=node.value
    )


def explore(spec: ProjectSpec, bundle: Dict[str, Any], l3_mode: str) -> SearchResult:
    tot = tot_search(spec, bundle)
    if l3_mode in {"lats", "cascade"}:
        return lats_polish(spec, tot)
    return tot
