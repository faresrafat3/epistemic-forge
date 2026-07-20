"""L2 Epistemic Synthesis Engine: Chain of Density Architect."""
from epistemic_forge.models import ProjectSpec, ChainOfDensityOutput
from epistemic_forge.llm import generate_structured
from typing import Dict, Any

def outline_and_draft(spec: ProjectSpec, claims_bundle: Dict[str, Any], instruction: str) -> Dict[str, Any]:
    """Compress the dialectic into a hyper-dense, falsifiable artifact."""
    
    # Gather previous context to compress
    raw_context = f"Question: {spec.question}\nClaims: {claims_bundle.get('claims', [])}"
    
    messages = [
        {"role": "system", "content": "You are a Chain-of-Density Architect. Your goal is to take raw thoughts and compress them into a highly dense, signal-rich artifact stripped of all rhetorical fluff and confident mush. Every word must carry epistemic weight."},
        {"role": "user", "content": f"Raw Context:\n{raw_context}\nCompress this."}
    ]
    
    # Neuro-Symbolic Call
    result: ChainOfDensityOutput = generate_structured(
        messages=messages,
        response_model=ChainOfDensityOutput,
        model="gpt-4o-mini"
    )
    
    return {
        "density_score": result.information_density_score,
        "draft_markdown": f"# Crystallized Artifact\n\n{result.crystallized_claim}\n\n*Density Score: {result.information_density_score}/10*",
        "outline": ["Crystallized Core"]
    }
