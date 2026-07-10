"""L0 — Technique Router (Prompt Report taxonomy patterns)."""

from __future__ import annotations

from typing import List

from epistemic_forge.models import Domain, ProjectSpec, RouteDecision


def route_project(spec: ProjectSpec) -> RouteDecision:
    """Choose technique families and ARSENAL layer flags for this project."""
    domain = spec.domain
    families: List[str] = ["In-Context Learning"]
    activate = {
        "ape": True,
        "opro": False,
        "meta": True,
        "tot": True,
        "lats": False,
        "refine": True,
        "reflexion": True,
        "voyager": False,
        "stages": True,
    }
    l1_mode = "ape"
    l3_mode = "tot"
    rationale_bits: List[str] = []

    q = (spec.question + " " + " ".join(spec.keywords)).lower()
    hard = any(
        k in q
        for k in (
            "debate",
            "tradeoff",
            "uncertain",
            "novel",
            "philosophy",
            "ethics",
            "causal",
            "counter",
        )
    )
    needs_code = domain in {Domain.KAGGLE, Domain.FREELANCE, Domain.HYBRID} or any(
        k in q for k in ("python", "notebook", "kaggle", "baseline", "model", "pipeline")
    )
    open_ended = domain in {Domain.RESEARCH, Domain.PHILOSOPHY, Domain.HYBRID} or hard

    if domain in {Domain.PHILOSOPHY, Domain.RESEARCH, Domain.WRITING}:
        families += ["Thought Generation", "Decomposition", "Self-Criticism"]
        rationale_bits.append("conceptual work → CoT + decomposition + critique")
    if domain == Domain.KAGGLE or needs_code:
        families += ["Agents", "Self-Criticism", "Answer Engineering"]
        activate["lats"] = True  # env/test-like loops for code paths
        activate["voyager"] = True
        l3_mode = "cascade"
        rationale_bits.append("code/Kaggle → agent loops + skill memory + ToT→LATS cascade")
    if domain == Domain.FREELANCE:
        families += ["In-Context Learning", "Answer Engineering", "Self-Criticism"]
        activate["meta"] = True
        rationale_bits.append("client deliverables → structured extraction + polish")
    if open_ended:
        families += ["Ensembling"]
        activate["opro"] = spec.enable_opro_style
        l1_mode = "cascade" if activate["opro"] else "ape"
        rationale_bits.append("open-ended → optional OPRO-style instruction climb")
    if spec.enable_skills and (needs_code or domain == Domain.HYBRID):
        activate["voyager"] = True
        rationale_bits.append("skill library enabled for procedural reuse")

    # Budget clamps
    if spec.budget_tokens < 3000:
        activate["opro"] = False
        activate["lats"] = False
        l1_mode = "ape"
        l3_mode = "tot"
        rationale_bits.append("tight budget → APE + ToT only")

    # Unique families preserve order
    seen = set()
    fam_out = []
    for f in families:
        if f not in seen:
            seen.add(f)
            fam_out.append(f)

    return RouteDecision(
        families=fam_out,
        activate=activate,
        rationale="; ".join(rationale_bits) or "default hybrid route",
        l1_mode=l1_mode,
        l3_mode=l3_mode,
    )
