"""L5 procedural memory — Voyager-style skill library (in-process)."""

from __future__ import annotations

from typing import Dict, List

from epistemic_forge.models import Skill


# Built-in skills (curriculum seeds)
_BUILTIN: List[Skill] = [
    Skill(
        name="claim_lattice_v1",
        description="Extract thesis, supports, objections, residual uncertainty into structured claims.",
        code="def claim_lattice(question): ...",
        tags=["research", "philosophy", "writing"],
    ),
    Skill(
        name="client_scope_box",
        description="Produce in/out scope, assumptions, milestones, acceptance criteria for freelancing.",
        code="def client_scope_box(brief): ...",
        tags=["freelance", "writing"],
    ),
    Skill(
        name="kaggle_baseline_spine",
        description="EDA → baseline → CV → error analysis notebook spine with leakage checklist.",
        code="def kaggle_baseline_spine(problem): ...",
        tags=["kaggle", "python"],
    ),
    Skill(
        name="dialectic_chain",
        description="Build thesis/antithesis/synthesis with steelman opposition.",
        code="def dialectic_chain(claim): ...",
        tags=["philosophy", "research"],
    ),
    Skill(
        name="peer_review_rubric",
        description="Score clarity, novelty, soundness, actionability; return revision bullets.",
        code="def peer_review_rubric(doc): ...",
        tags=["research", "writing"],
    ),
]


class SkillLibrary:
    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {s.name: s for s in _BUILTIN}

    def retrieve(self, query: str, top_k: int = 3) -> List[Skill]:
        q = query.lower()
        scored = []
        for s in self._skills.values():
            blob = (s.description + " " + " ".join(s.tags)).lower()
            score = sum(1 for tok in q.split() if len(tok) > 3 and tok in blob)
            for tag in s.tags:
                if tag in q:
                    score += 2
            scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for sc, s in scored[:top_k] if sc > 0] or list(self._skills.values())[
            :top_k
        ]

    def add(self, skill: Skill) -> None:
        name = skill.name
        if name in self._skills:
            i = 2
            while f"{name}_v{i}" in self._skills:
                i += 1
            name = f"{name}_v{i}"
            skill = Skill(name, skill.description, skill.code, skill.tags)
        self._skills[name] = skill

    def names(self) -> List[str]:
        return list(self._skills.keys())
