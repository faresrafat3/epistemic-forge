"""L1 — Instruction Optimizer (SOTA OPRO-style dynamic prompt generation).

Replaces hardcoded static prompts with dynamic, LLM-generated 
Meta-Prompting instructions optimized for the specific task at hand.
"""
from epistemic_forge.models import ProjectSpec, OptimizedInstruction
from epistemic_forge.llm import generate_structured
from loguru import logger

def optimize_instruction(spec: ProjectSpec) -> str:
    """Uses the LLM to dynamically generate the best possible instruction for the task."""
    
    logger.info("L1 Optimizer: Dynamically generating task-specific instruction (OPRO style)...")
    
    messages = [
        {"role": "system", "content": "You are a Meta-Prompting Optimizer (OPRO). Your job is to read the user's task and generate the perfect, highly constrained, step-by-step 'System Instruction' that another LLM should follow to solve it perfectly without hallucinations."},
        {"role": "user", "content": f"Task Domain: {spec.domain}\nQuestion: {spec.question}\nKeywords: {spec.keywords}\nGenerate the optimized instruction."}
    ]
    
    # Real LLM Call
    result: OptimizedInstruction = generate_structured(
        messages=messages,
        response_model=OptimizedInstruction,
        model=spec.target_model,
        api_base=spec.api_base
    )
    
    logger.debug(f"L1 Optimization Complete. Expected failure modes mitigated: {result.expected_failure_modes}")
    return result.meta_prompt
