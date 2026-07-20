"""L2 Epistemic Synthesis Engine: Leakage & Rigor Sentinel."""
from epistemic_forge.models import ProjectSpec, RigorSentinelOutput
from epistemic_forge.llm import generate_structured
from typing import Dict, Any

def build_competition_kit(spec: ProjectSpec, claims_bundle: Dict[str, Any], skills: list) -> Dict[str, Any]:
    """Audit the premise for epistemic blind spots and target leakage."""
    
    messages = [
        {"role": "system", "content": "You are a Grandmaster ML Auditor. Your job is to look at a proposed research or data problem and identify 'target leakage'—where the answer is implicitly baked into the question—and propose strict falsification metrics."},
        {"role": "user", "content": f"Problem Statement: {spec.question}\nKeywords: {spec.keywords}\nFind the blind spots and establish a robust baseline."}
    ]
    
    # Neuro-Symbolic Call
    result: RigorSentinelOutput = generate_structured(
        messages=messages,
        response_model=RigorSentinelOutput,
        model="gpt-4o-mini"
    )
    
    return {
        "checklist": result.epistemic_blind_spots,
        "metric_alignment": result.falsification_metric,
        "baseline_architecture": result.robust_baseline,
        "experiment_log_template": {
            "status": "Audited by Rigor Sentinel",
            "notes": "Ensure no data from the future is used."
        }
    }
