"""L4 — Local polisher (Self-Refine + Voyager-style critique patterns)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from epistemic_forge.models import ProjectSpec


@dataclass
class RefineStep:
    draft: str
    feedback: str
    score: float


def _multi_aspect_feedback(draft: str, spec: ProjectSpec) -> Tuple[str, float, bool]:
    aspects = {
        "clarity": 0.0,
        "structure": 0.0,
        "epistemic_humility": 0.0,
        "actionability": 0.0,
        "domain_fit": 0.0,
    }
    t = draft.lower()
    if len(draft.split()) >= 80:
        aspects["clarity"] += 0.6
    if any(h in t for h in ("##", "1.", "claim", "evidence", "next")):
        aspects["structure"] += 0.7
    if any(h in t for h in ("limit", "unknown", "risk", "assumption", "confidence")):
        aspects["epistemic_humility"] += 0.8
    if any(h in t for h in ("deliverable", "checklist", "baseline", "milestone", "metric")):
        aspects["actionability"] += 0.7
    d = spec.domain.value
    domain_cues = {
        "kaggle": ("cv", "baseline", "feature", "notebook"),
        "freelance": ("client", "scope", "acceptance", "timeline"),
        "philosophy": ("concept", "objection", "dialect", "definition"),
        "research": ("hypothesis", "method", "evidence", "contribution"),
        "writing": ("audience", "paragraph", "arc", "example"),
        "hybrid": ("claim", "brief", "experiment", "next"),
    }
    cues = domain_cues.get(d, domain_cues["hybrid"])
    aspects["domain_fit"] = min(1.0, sum(0.25 for c in cues if c in t))

    # Normalize partial scores
    for k, v in list(aspects.items()):
        aspects[k] = max(0.1, min(1.0, v if v else 0.25))

    total = sum(aspects.values()) / len(aspects)
    fb_lines = [f"- {k}: {v:.2f}" for k, v in aspects.items()]
    missing = [k for k, v in aspects.items() if v < 0.45]
    if missing:
        fb_lines.append("Improve: " + ", ".join(missing))
    stop = total >= 0.72 and not missing
    if stop:
        fb_lines.append("STOP: quality threshold met.")
    return "\n".join(fb_lines), total, stop


def _apply_feedback(draft: str, feedback: str, spec: ProjectSpec) -> str:
    addenda = []
    fl = feedback.lower()
    if "epistemic_humility" in fl or "improve: epistemic" in fl:
        addenda.append(
            "\n\n### Limits & unknowns\n"
            "- What would falsify the main claim?\n"
            "- Which assumptions are load-bearing?\n"
            f"- Audience-specific risk for {spec.audience}."
        )
    if "actionability" in fl or "improve: actionability" in fl:
        addenda.append(
            "\n\n### Next actions\n"
            "1. One measurement or artifact to produce this week.\n"
            "2. One conversation or review to schedule.\n"
            "3. One scope cut if time is short."
        )
    if "structure" in fl or "improve: structure" in fl:
        if not draft.strip().startswith("#"):
            draft = f"# {spec.title}\n\n## Core question\n{spec.question}\n\n" + draft
    if "domain_fit" in fl and spec.domain.value == "kaggle":
        addenda.append(
            "\n\n### Validation note\n"
            "Report metric mean±std under a leakage-safe split before claiming lift."
        )
    if "domain_fit" in fl and spec.domain.value == "freelance":
        addenda.append(
            "\n\n### Acceptance criteria\n"
            "- Deliverable format\n- Revision rounds\n- Definition of done"
        )
    return draft + "".join(addenda)


def refine_document(
    draft: str, spec: ProjectSpec, max_iters: int = 3
) -> Tuple[str, List[RefineStep]]:
    history: List[RefineStep] = []
    current = draft
    for i in range(max_iters):
        fb, score, stop = _multi_aspect_feedback(current, spec)
        history.append(RefineStep(draft=current, feedback=fb, score=score))
        if stop:
            break
        current = _apply_feedback(current, fb, spec)
    return current, history
