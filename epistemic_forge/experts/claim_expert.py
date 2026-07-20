"""Claim Lattice Expert Implementation."""
from typing import Dict, Any
from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.models import ProjectSpec, ClaimLatticeOutput
from epistemic_forge.llm import generate_structured
from loguru import logger

class ClaimLatticeExpert(EpistemicExpert):
    """Deconstructs the question into a structured, epistemically grounded claim lattice."""
    
    @property
    def expert_name(self) -> str:
        return "Epistemic_Claim_Lattice_Generator"

    def analyze(self, spec: ProjectSpec, context: Dict[str, Any]) -> ClaimLatticeOutput:
        """Forces the LLM to generate claims ONLY if it can provide a warrant/explanation."""
        
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are a rigorous analytical philosopher and scientist. Your task is to break down the user's premise into a 'Claim Lattice'. "
                    "CRITICAL RULE: You are strictly forbidden from making ANY claim without providing an 'epistemic_warrant' (a clear logical explanation or evidence) "
                    "and a 'potential_falsifier' (what would prove it wrong). No confident mush allowed."
                )
            },
            {
                "role": "user", 
                "content": f"Core Premise: {spec.question}\nKeywords: {spec.keywords}\nDeconstruct this into rigorously grounded claims."
            }
        ]
        
        logger.debug("Dispatching to LLM for Claim Lattice Generation (Enforcing Truthfulness)...")
        return generate_structured(
            messages=messages,
            response_model=ClaimLatticeOutput,
            model=spec.target_model,
            api_base=spec.api_base
        )
