"""L4 — The Adversarial Crucible (True LLM-Based Self-Refine).

Implements the SOTA Reflection & Self-Correction pattern.
The system generates a critique of the draft, and if it fails the threshold,
it rewrites the draft iteratively until perfection or max retries are reached.
"""

from epistemic_forge.models import ProjectSpec, RefinementFeedback, RefinedArtifact
from epistemic_forge.llm import generate_structured
from loguru import logger
from typing import Tuple


def _generate_critique(spec: ProjectSpec, draft: str) -> RefinementFeedback:
    """Uses LLM-as-a-Judge to brutally critique the draft."""
    messages = [
        {
            "role": "system",
            "content": "You are a merciless Peer Reviewer (NeurIPS level). Critique the artifact for logical leaps, lack of epistemic grounding, and clarity. Be brutal.",
        },
        {
            "role": "user",
            "content": f"Core Question: {spec.question}\nArtifact Draft:\n{draft}\n\nCritique this rigorously.",
        },
    ]

    return generate_structured(
        messages=messages,
        response_model=RefinementFeedback,
        model=spec.target_model,
        api_base=spec.api_base,
    )


def _rewrite_draft(
    spec: ProjectSpec, draft: str, critique: RefinementFeedback
) -> RefinedArtifact:
    """Uses LLM to rewrite the draft based on the strict critique."""
    messages = [
        {
            "role": "system",
            "content": "You are a Master Synthesizer. You have received a brutal critique of a draft. Your job is to rewrite the draft perfectly, fixing all flaws without losing the core message.",
        },
        {
            "role": "user",
            "content": f"Original Draft:\n{draft}\n\nFlaws to Fix:\n{critique.critical_flaws}\n\nRewrite the draft to perfection.",
        },
    ]

    return generate_structured(
        messages=messages,
        response_model=RefinedArtifact,
        model=spec.target_model,
        api_base=spec.api_base,
    )


def refine_document(
    spec: ProjectSpec, draft: str, max_iterations: int = 2
) -> Tuple[str, float]:
    """Iterative Self-Refine Loop (Generate -> Critique -> Rewrite)."""

    logger.info(
        f"L4 Refine: Entering Adversarial Crucible (Max iterations: {max_iterations})..."
    )

    current_draft = draft
    final_score = 0.0

    for i in range(max_iterations):
        logger.debug(f"L4 Refine: Iteration {i + 1} - Critiquing...")
        critique = _generate_critique(spec, current_draft)

        # Calculate an overall composite score
        overall_score = (
            critique.clarity_score + critique.epistemic_humility_score
        ) / 2.0
        final_score = overall_score

        if critique.passes_threshold and not critique.critical_flaws:
            logger.success(
                f"L4 Refine: Draft passed threshold with score {overall_score:.2f}!"
            )
            break

        logger.warning(
            f"L4 Refine: Draft failed. Flaws found: {len(critique.critical_flaws)}. Rewriting..."
        )
        rewritten = _rewrite_draft(spec, current_draft, critique)
        current_draft = rewritten.improved_text
        logger.debug(
            f"L4 Refine: Rewrite complete. Changes made: {rewritten.changes_made}"
        )

    logger.info("L4 Refine: Exiting Crucible.")
    return current_draft, final_score
