"""Claim Lattice Expert Implementation (Agentic RAG Grounded)."""
from typing import Dict, Any
from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.models import ProjectSpec, ClaimLatticeOutput
from epistemic_forge.llm import generate_structured
from epistemic_forge.tools.search import multi_hop_search
from loguru import logger

class ClaimLatticeExpert(EpistemicExpert):
    """Deconstructs the question into a structured, epistemically grounded claim lattice."""
    
    @property
    def expert_name(self) -> str:
        return "Grounded_Claim_Lattice_Generator"

    def analyze(self, spec: ProjectSpec, context: Dict[str, Any]) -> ClaimLatticeOutput:
        """Uses Agentic Multi-Hop Web Search to ground the LLM's claims in reality."""
        
        # 1. Fetch real-world context using Multi-Hop Agentic RAG
        logger.debug("Gathering multi-hop empirical data (Thesis + Antithesis) from the web...")
        live_evidence = multi_hop_search(spec.question, max_hops=2)
        
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
