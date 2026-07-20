"""Abstract Interface for Neuro-Symbolic Experts.

This module enforces the Strategy Pattern (SOLID Principles).
Every expert MUST implement this interface to guarantee uniform execution
and predictable structured outputs within the L2 Conductor.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel
from epistemic_forge.models import ProjectSpec


class EpistemicExpert(ABC):
    """Base class defining the contract for all cognitive experts."""

    @property
    @abstractmethod
    def expert_name(self) -> str:
        """The formal identifier of the expert (e.g., 'RigorSentinel')."""
        pass

    @abstractmethod
    def analyze(self, spec: ProjectSpec, context: Dict[str, Any]) -> BaseModel:
        """
        Executes the expert's specific neuro-symbolic logic.

        Args:
            spec: The user's project specifications and constraints.
            context: The accumulated epistemic state (prior claims, history).

        Returns:
            A strictly typed Pydantic BaseModel representing the expert's conclusion.
        """
        pass
