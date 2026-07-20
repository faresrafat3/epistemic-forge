"""L2 Epistemic Synthesis Engine: Semitic NLP & Arabic Logic Expert."""
from epistemic_forge.models import ProjectSpec, HegelianDialecticOutput
from epistemic_forge.llm import generate_structured
from typing import Dict, Any

def run_semitic_dialectic(spec: ProjectSpec, claims_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Execute dialectic reasoning specifically optimized for Arabic/Semitic morphological logic."""
    thesis = spec.question
    
    messages = [
        {"role": "system", "content": "You are a master of Semitic NLP, Arabic logic, and the Scattering Law. Your goal is to analyze the premise in its native Arabic/Semitic context, find morphological or logical blind spots, and synthesize a culturally and logically grounded truth."},
        {"role": "user", "content": f"الفرضية الأساسية (Thesis): {thesis}\n\nقم بنسف هذه الفرضية بالمنطق السامي/العربي، ثم استخرج الحقيقة المركبة."}
    ]
    
    # Using Claude 3.5 Sonnet or GPT-4o which are great at Arabic logic
    result: HegelianDialecticOutput = generate_structured(
        messages=messages,
        response_model=HegelianDialecticOutput,
        model="gpt-4o" 
    )
    
    return {
        "thesis": thesis,
        "antithesis_arabic": result.steelmanned_antithesis,
        "synthesis_arabic": result.synthesis_resolution,
        "open_questions": result.remaining_uncertainties,
    }
