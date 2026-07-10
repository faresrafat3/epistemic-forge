"""Dialectic expert — philosophy/research tension mapping."""

from __future__ import annotations

from typing import Any, Dict

from epistemic_forge.models import ProjectSpec


def run_dialectic(spec: ProjectSpec, claims_bundle: Dict[str, Any]) -> Dict[str, Any]:
    claims = claims_bundle.get("claims", [])
    thesis = claims[0]["text"] if claims else spec.question
    return {
        "thesis": thesis,
        "antithesis": (
            f"Counter: the best path on «{spec.title}» may be local craft and tacit skill, "
            "not explicit lattices—over-formalization can freeze inquiry."
        ),
        "steelman": (
            "Steelman of the counter: experts often succeed with pattern recognition under time "
            "pressure; forcing explicit structure can slow delivery and invent false precision."
        ),
        "synthesis": (
            "Use a *light* claim lattice as a scaffold, not a cage: make assumptions and "
            "objections legible, then ship the smallest artifact that can be falsified in the world."
        ),
        "open_questions": [
            "What is the cheapest falsifying observation?",
            "Who is harmed if we are wrong?",
            "What would count as enough certainty to act?",
        ],
    }
