"""Data Leakage and Scientific Rigor Expert Implementation."""

from typing import Any

from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.llm import generate_structured
from epistemic_forge.models import ProjectSpec, RigorSentinelOutput


class RigorSentinelExpert(EpistemicExpert):
    """Audits data science/research premises for methodological flaws and leakage."""

    @property
    def expert_name(self) -> str:
        return "Rigor_And_Leakage_Sentinel"

    def analyze(
        self, spec: ProjectSpec, context: dict[str, Any]
    ) -> RigorSentinelOutput:
        """Identifies target leakage and establishes strict falsification metrics."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Grandmaster ML Auditor. Identify 'target leakage' "
                    "or hidden assumptions in the premise, and propose strict falsification metrics."
                ),
            },
            {
                "role": "user",
                "content": f"Problem Statement: {spec.question}\nKeywords: {spec.keywords}\nFind blind spots.",
            },
        ]

        return generate_structured(
            messages=messages,
            response_model=RigorSentinelOutput,
            model=spec.target_model,
            api_base=spec.api_base,
        )
