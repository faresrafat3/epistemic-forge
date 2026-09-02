"""Deterministic quality metrics for epistemic packaging.

These metrics operationalize Toulmin-style argument completeness and
delivery hygiene without requiring an external LLM judge.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class QualityScores:
    """Per-document epistemic quality scores in [0, 1]."""

    has_claim: float
    has_grounds: float
    has_warrant: float
    has_rebuttal: float
    has_qualifier: float
    structure: float
    actionability: float
    humility: float
    length_balance: float
    domain_cues: float

    def overall(self) -> float:
        weights = {
            "has_claim": 0.14,
            "has_grounds": 0.14,
            "has_warrant": 0.10,
            "has_rebuttal": 0.14,
            "has_qualifier": 0.12,
            "structure": 0.10,
            "actionability": 0.10,
            "humility": 0.08,
            "length_balance": 0.04,
            "domain_cues": 0.04,
        }
        total = 0.0
        for k, w in weights.items():
            total += getattr(self, k) * w
        return round(total, 4)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["overall"] = self.overall()
        return d


def _hit(text: str, patterns: list[str]) -> float:
    t = text.lower()
    return 1.0 if any(p in t for p in patterns) else 0.0


def _count_hits(text: str, patterns: list[str]) -> int:
    t = text.lower()
    return sum(1 for p in patterns if p in t)


def score_document(
    text: str,
    domain: str = "hybrid",
    keywords: list[str] | None = None,
) -> QualityScores:
    """Score a free-text answer for Toulmin completeness + packaging quality."""
    keywords = keywords or []
    t = text or ""
    words = len(t.split())

    # Toulmin elements (approximate via linguistic cues)
    has_claim = _hit(
        t,
        [
            "thesis",
            "claim",
            "core thesis",
            "we argue",
            "the answer is",
            "core question",
            "main claim",
            "i recommend",
            "recommendation",
        ],
    )
    # If text restates a clear stance sentence, partial credit
    if has_claim == 0 and re.search(r"\b(should|must|is that|means that)\b", t.lower()):
        has_claim = 0.5

    has_grounds = _hit(
        t,
        [
            "support",
            "evidence",
            "because",
            "data",
            "example",
            "metric",
            "observation",
            "study",
            "baseline",
        ],
    )
    if has_grounds == 0 and words > 40:
        has_grounds = 0.3  # bare elaboration

    has_warrant = _hit(
        t,
        [
            "therefore",
            "so that",
            "which implies",
            "this means",
            "warrant",
            "aligned with",
            "in order to",
            "reduces",
            "improves decision",
        ],
    )
    if has_warrant == 0 and has_grounds and has_claim:
        has_warrant = 0.35

    has_rebuttal = _hit(
        t,
        [
            "objection",
            "counter",
            "steelman",
            "antithesis",
            "however",
            "risk",
            "but ",
            "limitation of this",
            "opposing",
        ],
    )

    has_qualifier = _hit(
        t,
        [
            "likely",
            "possible",
            "uncertain",
            "provisional",
            "confidence",
            "unknown",
            "assumption",
            "may ",
            "might ",
            "limit",
        ],
    )

    # Packaging
    structure = 0.0
    if "##" in t or re.search(r"(?m)^\d+\.\s", t) or re.search(r"(?m)^[-*]\s", t):
        structure = 0.7
    if t.strip().startswith("#"):
        structure = min(1.0, structure + 0.3)
    if structure == 0 and words > 30:
        structure = 0.25

    actionability = _hit(
        t,
        [
            "next action",
            "next steps",
            "checklist",
            "deliverable",
            "milestone",
            "acceptance",
            "baseline",
            "todo",
            "this week",
            "schedule",
        ],
    )
    if actionability == 0 and re.search(r"(?m)^\d+\.\s", t):
        actionability = 0.4

    humility = _hit(
        t,
        [
            "limit",
            "unknown",
            "assumption",
            "falsif",
            "confidence",
            "residual",
            "uncertain",
            "provisional",
            "disclaimer",
        ],
    )

    # Prefer neither tweet nor novel
    if 80 <= words <= 900:
        length_balance = 1.0
    elif 40 <= words < 80 or 900 < words <= 1400:
        length_balance = 0.6
    elif words < 40:
        length_balance = 0.25
    else:
        length_balance = 0.45

    domain_patterns = {
        "philosophy": [
            "concept",
            "dialect",
            "objection",
            "agency",
            "moral",
            "definition",
        ],
        "kaggle": ["cv", "baseline", "leak", "metric", "feature", "split", "notebook"],
        "freelance": [
            "client",
            "scope",
            "milestone",
            "acceptance",
            "deliverable",
            "timeline",
        ],
        "research": ["hypothesis", "method", "evidence", "contribution", "experiment"],
        "writing": ["audience", "paragraph", "arc", "draft"],
        "hybrid": ["claim", "brief", "experiment", "next"],
    }
    cues = domain_patterns.get(domain, domain_patterns["hybrid"])
    domain_cues = min(1.0, _count_hits(t, cues) / 3.0)
    # keyword overlap bonus
    kw_hits = sum(1 for k in keywords if k.lower() in t.lower())
    if keywords:
        domain_cues = min(1.0, domain_cues + 0.1 * kw_hits)

    return QualityScores(
        has_claim=has_claim,
        has_grounds=has_grounds,
        has_warrant=has_warrant,
        has_rebuttal=has_rebuttal,
        has_qualifier=has_qualifier,
        structure=structure,
        actionability=actionability,
        humility=humility,
        length_balance=length_balance,
        domain_cues=domain_cues,
    )


def toulmin_coverage(scores: QualityScores) -> float:
    """Fraction of core Toulmin slots present at >= 0.5."""
    slots = [
        scores.has_claim,
        scores.has_grounds,
        scores.has_warrant,
        scores.has_rebuttal,
        scores.has_qualifier,
    ]
    return round(sum(1 for s in slots if s >= 0.5) / len(slots), 4)
