"""L6 — AI Scientist v2 Progressive Stage Shell & Peer Review.

Replaces hardcoded scoring with a true LLM-as-a-Judge Peer Reviewer
that evaluates the final crystallized artifact against scientific standards.
"""

from epistemic_forge.models import ProjectSpec, FinalPeerReview, StageArtifact
from epistemic_forge.llm import generate_structured
from epistemic_forge.pipeline.l4_refine import refine_document
from loguru import logger
from typing import Dict, Any, List


def _peer_review(spec: ProjectSpec, doc: str, prior_score: float) -> FinalPeerReview:
    """Uses LLM-as-a-Judge to conduct a formal, multi-metric peer review."""

    logger.info("L6 Stages: Conducting final AI Peer Review...")

    messages = [
        {
            "role": "system",
            "content": "You are a distinguished Academic Editor for a high-impact journal. You must review the submitted artifact across 5 dimensions: clarity, structure, soundness, actionability, and epistemic humility. Issue a final verdict.",
        },
        {
            "role": "user",
            "content": f"Core Question: {spec.question}\nPrior Stage Score: {prior_score:.2f}\n\nSubmitted Artifact:\n{doc}\n\nConduct the peer review.",
        },
    ]

    return generate_structured(
        messages=messages,
        response_model=FinalPeerReview,
        model=spec.target_model,
        api_base=spec.api_base,
    )


def produce_artifacts(
    spec: ProjectSpec,
    final_draft: str,
    claims_bundle: Dict[str, Any],
    prior_score: float,
) -> tuple[List[StageArtifact], Dict[str, Any], float]:
    """Wraps the pipeline in progressive evaluation stages and produces the final deliverables."""

    logger.info("L6 Stages: Initializing final crystallization and review sequence.")

    # Optional: Run L4 refinement if it hasn't been perfected yet
    refined_doc, ref_score = refine_document(spec, final_draft, max_iterations=1)

    # Conduct LLM-based peer review
    review: FinalPeerReview = _peer_review(spec, refined_doc, ref_score)

    logger.success(
        f"L6 Stages: Verdict received -> [{review.verdict.upper()}] with score {review.overall_score:.2f}"
    )

    artifacts = [
        StageArtifact(
            name="Final Synthesis Memo",
            content=refined_doc,
            kind="markdown",
            path_hint="memo.md",
        ),
        StageArtifact(
            name="Claim Lattice Export",
            content=str(claims_bundle),
            kind="json",
            path_hint="lattice.json",
        ),
    ]

    return artifacts, review.model_dump(), review.overall_score
