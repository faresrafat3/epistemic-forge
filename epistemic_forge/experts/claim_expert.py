"""Claim Lattice Expert Implementation (Grounded with Real-World Search)."""

from typing import Any

from loguru import logger

from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.llm import generate_structured
from epistemic_forge.models import ClaimLatticeOutput, ProjectSpec
from epistemic_forge.tools.search import search_web


class ClaimLatticeExpert(EpistemicExpert):
    """Deconstructs the question into a structured, epistemically grounded claim lattice."""
    
    @property
    def expert_name(self) -> str:
        return "Grounded_Claim_Lattice_Generator"

    def analyze(self, spec: ProjectSpec, context: dict[str, Any]) -> ClaimLatticeOutput:
        """Uses Live Web Search to ground the LLM's claims in reality."""

        # 1. Fetch real-world context before asking the LLM to build claims
        logger.debug("Gathering live empirical data to prevent hallucination...")
        search_query = f"{spec.question} scientific consensus"
        live_evidence = search_web(search_query, max_results=3)


        messages = [
            {
                "role": "system", 
                "content": (
                    "You are a rigorous analytical philosopher and empirical scientist. Your task is to break down the user's premise into a 'Claim Lattice'. "
                    "CRITICAL RULE: You MUST ground your claims using the 'Live Evidence' provided. Do not hallucinate. "
                    "You are strictly forbidden from making ANY claim without providing an 'epistemic_warrant' (a clear logical explanation quoting the evidence) "
                    "and a 'potential_falsifier'. No confident mush allowed."
                )
            },
            {
                "role": "user", 
                "content": f"Core Premise: {spec.question}\nKeywords: {spec.keywords}\n\n=== LIVE EMPIRICAL EVIDENCE ===\n{live_evidence}\n=====================\n\nDeconstruct this into rigorously grounded claims, citing the evidence where applicable."
            }
        ]
        
        logger.debug("Dispatching to LLM for Grounded Claim Lattice Generation...")
        return generate_structured(
            messages=messages,
            response_model=ClaimLatticeOutput,
            model=spec.target_model,
            api_base=spec.api_base
        )
