"""LLM-as-a-Judge for Automated, Scientific Epistemic Evaluation (G-Eval style)."""

from typing import Any

from pydantic import BaseModel, Field

from epistemic_forge.llm import generate_structured


class JudgeEvaluation(BaseModel):
    """Strict schema for the AI Judge."""

    logical_coherence_score: int = Field(
        ge=1,
        le=5,
        description="1-5 score on how well the premises support the conclusion.",
    )
    hallucination_detected: bool = Field(
        description="True if the text makes empirical claims without warrants."
    )
    critique: str = Field(
        description="Academic peer-review style critique of the artifact."
    )


def evaluate_artifact_quality(question: str, artifact_text: str) -> dict[str, Any]:
    """Uses a stronger model (e.g., GPT-4o) to judge the output of the cheaper pipeline."""
    messages = [
        {
            "role": "system",
            "content": "You are a highly critical, NeurIPS-level peer reviewer. Evaluate the following research artifact for logical coherence and hallucination.",
        },
        {
            "role": "user",
            "content": f"Research Question: {question}\n\nArtifact Output:\n{artifact_text}",
        },
    ]

    # We use a heavier model for judging, but keep temp 0.0 for deterministic grading
    evaluation = generate_structured(
        messages=messages, response_model=JudgeEvaluation, model="gpt-4o-2024-08-06"
    )

    return {
        "score": evaluation.logical_coherence_score,
        "hallucination": evaluation.hallucination_detected,
        "critique": evaluation.critique,
    }
