"""L2 Epistemic Synthesis Engine: Hegelian Dialectic."""
from epistemic_forge.models import ProjectSpec, HegelianDialecticOutput
from epistemic_forge.llm import generate_structured
from typing import Dict, Any

def run_dialectic(spec: ProjectSpec, claims_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Hegelian Synthesis to destroy weak assumptions."""
    thesis = spec.question
    
    messages = [
        {"role": "system", "content": "You are a ruthless Hegelian philosopher and logician. Your goal is to take a premise, construct the most devastating 'Steelman' antithesis possible, and forge a synthesis that represents the nuanced truth."},
        {"role": "user", "content": f"Core Premise/Thesis: {thesis}\nProject Domain: {spec.domain.value}\nDestroy this premise with logic, then synthesize."}
    ]
    
    # Neuro-Symbolic Call: Forcing GPT to return the strict Hegelian schema
    result: HegelianDialecticOutput = generate_structured(
        messages=messages,
        response_model=HegelianDialecticOutput,
        model="gpt-4o-mini" # Cost-aware baseline
    )
    
    return {
        "thesis": thesis,
        "antithesis": result.steelmanned_antithesis,
        "synthesis": result.synthesis_resolution,
        "open_questions": result.remaining_uncertainties,
    }
