"""L1.5 — Automated Design of Agentic Systems (ADAS).

Self-Evolving Architecture: If the static experts (Hegelian, Rigor Sentinel) 
are insufficient for a highly specific query, this layer dynamically writes 
a custom Pydantic Schema and instantiates a new Expert Node on the fly.
"""
from typing import Dict, Any, Type
from pydantic import BaseModel, create_model, Field
from loguru import logger

from epistemic_forge.models import ProjectSpec, DynamicExpertSchema
from epistemic_forge.llm import generate_structured
from epistemic_forge.experts.base import EpistemicExpert

def generate_dynamic_expert(spec: ProjectSpec) -> EpistemicExpert:
    """Uses LLM to design a custom expert class and Pydantic schema."""
    
    logger.info("🧬 L1.5 ADAS: Generating a custom Self-Evolving Expert tailored to this query...")
    
    messages = [
        {"role": "system", "content": "You are a Meta-Architect (ADAS). Your job is to design a highly specialized 'AI Expert Node' that is perfectly tailored to solve the user's specific problem. Define its output schema and its system prompt."},
        {"role": "user", "content": f"Problem: {spec.question}\nKeywords: {spec.keywords}\n\nDesign the perfect expert to analyze this."}
    ]
    
    blueprint: DynamicExpertSchema = generate_structured(
        messages=messages,
        response_model=DynamicExpertSchema,
        model=spec.target_model,
        api_base=spec.api_base
    )
    
    logger.debug(f"🧬 Blueprint acquired: {blueprint.expert_class_name}")
    
    # Dynamically create the Pydantic Model based on the LLM's design
    field_definitions = {}
    for f in blueprint.fields_to_extract:
        for fname, fdesc in f.items():
            # Clean field name to be a valid python identifier
            safe_fname = "".join(c for c in fname if c.isalnum() or c == "_").lower()
            if safe_fname:
                field_definitions[safe_fname] = (str, Field(description=fdesc))
                
    DynamicModel = create_model(f"{blueprint.expert_class_name}Output", **field_definitions)
    
    # Create the Expert Class dynamically
    class DynamicallyGeneratedExpert(EpistemicExpert):
        @property
        def expert_name(self) -> str:
            return blueprint.expert_class_name
            
        def analyze(self, spec: ProjectSpec, context: Dict[str, Any]) -> BaseModel:
            logger.debug(f"Activating dynamically generated expert: {self.expert_name}")
            msgs = [
                {"role": "system", "content": blueprint.system_prompt},
                {"role": "user", "content": f"Problem: {spec.question}\nContext: {context}\nAnalyze this."}
            ]
            return generate_structured(
                messages=msgs,
                response_model=DynamicModel,
                model=spec.target_model,
                api_base=spec.api_base
            )
            
    return DynamicallyGeneratedExpert()
