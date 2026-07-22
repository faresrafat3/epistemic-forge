"""LLM-as-a-Judge for Automated, Scientific Epistemic Evaluation (Toulmin Model)."""
from typing import Dict, Any
from epistemic_forge.models import JudgeEvaluation
from epistemic_forge.llm import generate_structured
from loguru import logger

def evaluate_artifact_quality(question: str, artifact_text: str) -> Dict[str, Any]:
    """Uses a stronger model to judge the output based strictly on Toulmin's Model of Argumentation."""
    logger.info("⚖️ Initiating strict Toulmin-based evaluation of the final artifact...")
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are an Elite Academic Peer Reviewer specializing in the Toulmin Model of Argumentation. "
                "Do NOT judge the artifact based on prose or formatting. You must ONLY evaluate the strength of the 'Warrants' (do they bridge the data to the claim?) "
                "and the validity of the 'Rebuttals/Falsifiers' (are they real weaknesses or just strawmen?)."
            )
        },
        {"role": "user", "content": f"Core Inquiry: {question}\n\nSubmitted Artifact:\n{artifact_text}\n\nExecute the Toulmin Evaluation."}
    ]
    
    # We use a robust model for judging, maintaining temp 0.0 for deterministic grading
    evaluation: JudgeEvaluation = generate_structured(
        messages=messages,
        response_model=JudgeEvaluation,
        model="openai/gpt-4o-mini", # Standardizing to openrouter/openai model format
        api_base="https://openrouter.ai/api/v1" # Enforce OpenRouter for testing consistency
    )
    
    return {
        "score": evaluation.logical_coherence_score,
        "hallucination": evaluation.hallucination_detected,
        "critique": evaluation.critique
    }
