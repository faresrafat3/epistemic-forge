"""Layer 2 (L2): The Neuro-Symbolic Conductor.

This module orchestrates the execution of multiple cognitive experts.
It uses the Strategy Pattern to dynamically load and run experts based on the domain.
"""

from typing import Dict, Any
from loguru import logger

from epistemic_forge.models import ProjectSpec
from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.experts.claim_expert import ClaimLatticeExpert
from epistemic_forge.experts.dialectic_expert import HegelianExpert
from epistemic_forge.experts.kaggle_expert import RigorSentinelExpert
from epistemic_forge.pipeline.l1_5_adas import generate_dynamic_expert


class SemanticConductor:
    """Dispatches the project specification to registered experts."""

    def __init__(self):
        # Register available experts
        self.experts: list[EpistemicExpert] = []

    def _route_experts(self, domain: str) -> list[EpistemicExpert]:
        """Determines which experts are required based on the domain."""
        active_experts = [ClaimLatticeExpert()]
        
        # 🧬 ADAS: Inject a dynamically generated expert specific to this domain!
        try:
            dynamic_expert = generate_dynamic_expert(spec)
            active_experts.append(dynamic_expert)
        except Exception as e:
            logger.warning(f"ADAS failed to generate dynamic expert, continuing with standard nodes. Error: {e}")

        if domain in ["philosophy", "research", "hybrid"]:
            active_experts.append(HegelianExpert())
        if domain in ["kaggle", "research", "hybrid"]:
            active_experts.append(RigorSentinelExpert())
        return active_experts

    def conduct(self, spec: ProjectSpec, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the active experts and aggregates their Pydantic outputs.

        Returns:
            A dictionary mapping expert names to their structured outputs.
        """
        logger.info(f"L2 Conductor: Routing inquiry for domain [{spec.domain}]")

        active_experts = self._route_experts(spec.domain)
        results = {}

        for expert in active_experts:
            logger.debug(f"Activating node: {expert.expert_name}")
            try:
                # Executes the polymophic analyze() method
                structured_output = expert.analyze(spec, context)
                results[expert.expert_name] = structured_output.model_dump()
            except Exception as e:
                logger.error(f"Cognitive fault in {expert.expert_name}: {e}")
                results[expert.expert_name] = {"error": str(e)}

        return results


# Expose a functional interface for backward compatibility with the pipeline
def conduct(spec: ProjectSpec, claims_bundle: Dict[str, Any]) -> Dict[str, Any]:
    conductor = SemanticConductor()
    return conductor.conduct(spec, claims_bundle)
