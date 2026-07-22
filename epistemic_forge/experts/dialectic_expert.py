"""Hegelian Synthesis Expert Implementation."""

from typing import Any

from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.llm import generate_structured
from epistemic_forge.models import HegelianDialecticOutput, ProjectSpec


class HegelianExpert(EpistemicExpert):
    """Applies Hegelian dialectic (Thesis -> Antithesis -> Synthesis) to premises."""

    @property
    def expert_name(self) -> str:
        return "Hegelian_Dialectic_Engine"

    def analyze(
        self, spec: ProjectSpec, context: dict[str, Any]
    ) -> HegelianDialecticOutput:
        """Synthesizes the core question by forcing a steelmanned antithesis."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a ruthless Hegelian philosopher. Take the user's premise, "
                    "construct the most devastating 'Steelman' antithesis possible, "
                    "and forge a synthesis that represents the nuanced truth."
                ),
            },
            {
                "role": "user",
                "content": f"Core Thesis: {spec.question}\nDomain: {spec.domain}\nDestroy and synthesize.",
            },
        ]

        # The universal Hermes router handles the LLM complexity internally
        return generate_structured(
            messages=messages,
            response_model=HegelianDialecticOutput,
            model=spec.target_model,
            api_base=spec.api_base,
        )
