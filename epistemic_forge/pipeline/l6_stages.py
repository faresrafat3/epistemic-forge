"""L6 — Progressive stage shell (AI Scientist v2-inspired packaging)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from epistemic_forge.models import ProjectSpec, StageArtifact
from epistemic_forge.pipeline.l4_refine import refine_document


def _peer_review(doc: str, score: float) -> Dict[str, Any]:
    checks = {
        "clarity": 0.7 if len(doc) > 400 else 0.4,
        "structure": 0.8 if "##" in doc else 0.45,
        "soundness": min(0.9, 0.5 + score / 2),
        "actionability": 0.75 if "Next" in doc or "action" in doc.lower() else 0.4,
        "humility": 0.8 if "limit" in doc.lower() or "unknown" in doc.lower() else 0.35,
    }
    overall = sum(checks.values()) / len(checks)
    revisions = [k for k, v in checks.items() if v < 0.5]
    return {
        "scores": checks,
        "overall": round(overall, 3),
        "revision_needed": revisions,
        "verdict": "accept_with_minor_revisions" if overall >= 0.65 else "major_revisions",
    }


def produce_artifacts(
    spec: ProjectSpec,
    instruction: str,
    bundle: Dict[str, Any],
    best_thought: str,
    search_score: float,
    skills_used: List[str],
    reflections_block: str,
) -> Tuple[List[StageArtifact], Dict[str, Any], float]:
    """Stage-style production: draft → refine → review → package."""
    writing = bundle.get("writing", {})
    draft = writing.get("draft_markdown") or f"# {spec.title}\n\n{spec.question}\n"

    # Merge search framing + reflections
    draft += f"\n\n## Deliberate framing (L3)\n{best_thought}\n"
    draft += f"\n## Trial memory (L5)\n{reflections_block}\n"
    if skills_used:
        draft += "\n## Skills invoked\n" + "\n".join(f"- {s}" for s in skills_used) + "\n"

    # Domain packs
    if "dialectic" in bundle:
        d = bundle["dialectic"]
        draft += (
            "\n## Dialectic\n"
            f"**Thesis:** {d['thesis']}\n\n"
            f"**Antithesis:** {d['antithesis']}\n\n"
            f"**Steelman:** {d['steelman']}\n\n"
            f"**Synthesis:** {d['synthesis']}\n"
        )
    if "freelance" in bundle:
        f = bundle["freelance"]
        draft += (
            "\n## Client pack\n"
            f"**Proposal spine:** {f['proposal_spine']}\n\n"
            f"**In scope:** {', '.join(f['scope']['in_scope'])}\n\n"
            f"**Acceptance:** {', '.join(f['acceptance_criteria'])}\n"
        )
    if "kaggle" in bundle:
        draft += "\n## Kaggle plan\n" + ", ".join(bundle["kaggle"]["checklist"]) + "\n"

    refined, hist = refine_document(draft, spec, max_iters=3)
    final_score = hist[-1].score if hist else search_score
    review = _peer_review(refined, final_score)

    artifacts = [
        StageArtifact(
            name="research_memo",
            content=refined,
            kind="markdown",
            path_hint="outputs/research_memo.md",
        ),
        StageArtifact(
            name="instruction_used",
            content=instruction,
            kind="markdown",
            path_hint="outputs/instruction.md",
        ),
    ]

    if "freelance" in bundle:
        import json

        artifacts.append(
            StageArtifact(
                name="client_brief_json",
                content=json.dumps(bundle["freelance"], indent=2),
                kind="json",
                path_hint="outputs/client_brief.json",
            )
        )
    if "kaggle" in bundle:
        artifacts.append(
            StageArtifact(
                name="kaggle_notebook_md",
                content=bundle["kaggle"]["notebook_markdown"],
                kind="notebook-md",
                path_hint="outputs/kaggle_spine.md",
            )
        )
        # Minimal executable helper module content
        artifacts.append(
            StageArtifact(
                name="baseline_snippet_py",
                content=(
                    '"""Generated baseline snippet for local experimentation."""\n'
                    "def describe_plan():\n"
                    "    return ['EDA', 'baseline', 'CV', 'error analysis', 'one ablation']\n"
                ),
                kind="python",
                path_hint="outputs/baseline_plan.py",
            )
        )

    # Executive one-pager
    exec_summary = (
        f"# Executive summary — {spec.title}\n\n"
        f"**Question:** {spec.question}\n\n"
        f"**Framing:** {best_thought}\n\n"
        f"**Score:** {final_score:.2f} · **Review:** {review['verdict']}\n\n"
        f"**Instruction:** {instruction}\n"
    )
    artifacts.insert(
        0,
        StageArtifact(
            name="executive_summary",
            content=exec_summary,
            kind="markdown",
            path_hint="outputs/executive_summary.md",
        ),
    )

    return artifacts, review, final_score
