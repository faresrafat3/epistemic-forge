"""L1.5 — Automated Design of Agentic Systems (ADAS).

Self-Evolving Architecture: If the static experts (Hegelian, Rigor Sentinel)
are insufficient for a highly specific query, this layer dynamically writes
a custom Pydantic Schema and instantiates a new Expert Node on the fly.

Safety
------
The LLM-designed blueprint is **not** executed as code. We only use it to build
a Pydantic model via ``pydantic.create_model`` from *sanitized* field names, and
we bound the number of fields and validate every identifier. A malformed
blueprint raises instead of silently producing a broken expert.
"""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, create_model

from epistemic_forge.errors import InvalidInputError
from epistemic_forge.experts.base import EpistemicExpert
from epistemic_forge.llm import agenerate_structured, generate_structured
from epistemic_forge.models import DynamicExpertSchema, ProjectSpec

# Hard caps to keep a dynamically generated expert cheap and safe.
MAX_DYNAMIC_FIELDS = 12


def _safe_identifier(name: str) -> str:
    """Return a valid Python identifier derived from ``name``, or '' if none."""
    cleaned = "".join(c for c in name if c.isalnum() or c == "_").lower()
    if not cleaned:
        return ""
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def _build_field_definitions(blueprint: DynamicExpertSchema) -> dict[str, Any]:
    """Sanitize the LLM-provided field list into Pydantic field definitions."""
    field_definitions: dict[str, Any] = {}
    seen: set[str] = set()
    raw = blueprint.fields_to_extract or []
    if len(raw) > MAX_DYNAMIC_FIELDS:
        logger.warning(
            f"ADAS blueprint had {len(raw)} fields; truncating to {MAX_DYNAMIC_FIELDS}."
        )
        raw = raw[:MAX_DYNAMIC_FIELDS]

    for f in raw:
        for fname, fdesc in f.items():
            safe = _safe_identifier(fname)
            if not safe or safe in seen:
                continue
            seen.add(safe)
            field_definitions[safe] = (str, Field(description=fdesc or fname))

    if not field_definitions:
        raise InvalidInputError("ADAS blueprint produced no valid fields.")
    return field_definitions


def generate_dynamic_expert(spec: ProjectSpec) -> EpistemicExpert:
    """Uses LLM to design a custom expert class and Pydantic schema."""
    logger.info(
        "🧬 L1.5 ADAS: Generating a custom Self-Evolving Expert tailored to this query..."
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Meta-Architect (ADAS). Your job is to design a highly "
                "specialized 'AI Expert Node' that is perfectly tailored to solve the "
                "user's specific problem. Define its output schema and its system prompt."
            ),
        },
        {
            "role": "user",
            "content": f"Problem: {spec.question}\nKeywords: {spec.keywords}\n\nDesign the perfect expert to analyze this.",
        },
    ]

    blueprint: DynamicExpertSchema = generate_structured(
        messages=messages,
        response_model=DynamicExpertSchema,
        model=spec.target_model,
        api_base=spec.api_base,
    )

    logger.debug(f"🧬 Blueprint acquired: {blueprint.expert_class_name}")

    class_name = _safe_identifier(blueprint.expert_class_name) or "DynamicExpert"
    field_definitions = _build_field_definitions(blueprint)

    DynamicModel = create_model(f"{class_name}Output", **field_definitions)
    system_prompt = blueprint.system_prompt or "Analyze the problem rigorously."

    # Create the Expert Class dynamically
    class DynamicallyGeneratedExpert(EpistemicExpert):
        @property
        def expert_name(self) -> str:
            return class_name

        def analyze(self, spec: ProjectSpec, context: dict[str, Any]) -> BaseModel:
            logger.debug(f"Activating dynamically generated expert: {self.expert_name}")
            msgs = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Problem: {spec.question}\nContext: {context}\nAnalyze this.",
                },
            ]
            return generate_structured(
                messages=msgs,
                response_model=DynamicModel,
                model=spec.target_model,
                api_base=spec.api_base,
            )

        async def analyze_async(
            self, spec: ProjectSpec, context: dict[str, Any]
        ) -> BaseModel:
            logger.debug(
                f"Activating dynamically generated expert (async): {self.expert_name}"
            )
            msgs = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Problem: {spec.question}\nContext: {context}\nAnalyze this.",
                },
            ]
            return await agenerate_structured(
                messages=msgs,
                response_model=DynamicModel,
                model=spec.target_model,
                api_base=spec.api_base,
            )

    return DynamicallyGeneratedExpert()
