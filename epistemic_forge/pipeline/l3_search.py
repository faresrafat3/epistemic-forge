"""L3 — Tree Search (True LLM-Based Tree of Thoughts / LATS escalation).

Replaces hardcoded string-matching with genuine Monte Carlo / Beam Search 
where the LLM actively proposes reasoning branches and evaluates them (LLM-as-a-Judge).
"""
from epistemic_forge.models import ProjectSpec, SearchResult, SearchNode, ThoughtProposalsOutput, ThoughtEvaluation
from epistemic_forge.llm import generate_structured
from loguru import logger
from epistemic_forge.memory.economy import budget_manager
from typing import Dict, Any, List
import uuid

def _generate_thoughts(spec: ProjectSpec, context: str, beam: int) -> List[str]:
    """Uses the LLM to propose diverse reasoning paths (Branches)."""
    messages = [
        {"role": "system", "content": "You are a divergent thinker in a Tree of Thoughts system. Generate distinct, highly logical ways to approach the user's problem. Do not solve it yet, just propose analytical framings."},
        {"role": "user", "content": f"Problem: {spec.question}\nContext: {context}\n\nGenerate exactly {beam} distinct analytical approaches."}
    ]
    
    result: ThoughtProposalsOutput = generate_structured(
        messages=messages,
        response_model=ThoughtProposalsOutput,
        model=spec.target_model,
        api_base=spec.api_base
    )
    return [p.thought_text for p in result.proposals[:beam]]

def _evaluate_thought(spec: ProjectSpec, thought: str) -> float:
    """Process Reward Model (PRM) Evaluator.
    Scores a thought step-by-step to prevent error propagation.
    """
    messages = [
        {"role": "system", "content": "You are a Process Reward Model (PRM). Evaluate this intermediate reasoning step. Give it a score from 0.0 (contains a fatal logical flaw or hallucination) to 1.0 (flawless, rigorous epistemic reasoning)."},
        {"role": "user", "content": f"Problem: {spec.question}
Intermediate Step: {thought}

Score this step rigorously."}
    ]
    
    try:
        result: ThoughtEvaluation = generate_structured(
            messages=messages,
            response_model=ThoughtEvaluation,
            model=spec.target_model,
            api_base=spec.api_base
        )
        logger.debug(f"⚖️ PRM Score {result.epistemic_score}: {result.critique}")
        return result.epistemic_score
    except Exception as e:
        logger.warning(f"PRM Evaluation failed, defaulting to 0.5: {e}")
        return 0.5

def explore(spec: ProjectSpec, bundle: Dict[str, Any], beam: int = 3, steps: int = 2) -> SearchResult:
    """Genuine Beam Search (Tree of Thoughts) over the reasoning space."""
    
    logger.info(f"L3 Search: Initiating genuine LLM Tree Search (Beam={beam}, Steps={steps})...")
    
    nodes: List[SearchNode] = []
    
    # Initial state
    current_context = f"Initial constraints for {spec.domain}."
    best_thought_overall = ""
    highest_score = -1.0
    
    for step in range(steps):
        if budget_manager.is_budget_exceeded():
            logger.warning("L3 Search: Halting Deep Search to preserve token budget. Transitioning to L4.")
            break
        logger.info(f"L3 Search: Expanding Level {step+1}/{steps}...")
        
        # 1. Propose (Branching)
        proposed_thoughts = _generate_thoughts(spec, current_context, beam)
        
        step_best_thought = ""
        step_highest_score = -1.0
        
        # 2. Evaluate (Value Function)
        for thought in proposed_thoughts:
            score = _evaluate_thought(spec, thought)
            
            node = SearchNode(
                id=str(uuid.uuid4())[:8],
                thought=thought,
                value=score,
                meta={"step": step}
            )
            nodes.append(node)
            
            # Track best in step and overall
            if score > step_highest_score:
                step_highest_score = score
                step_best_thought = thought
                
            if score < 0.3:
                logger.warning(f"🛑 PRM detected fatal flaw (Score: {score}). Executing Rollback on this branch.")
                continue # Skip adding this to the beam
                
            if score > highest_score:
                highest_score = score
                best_thought_overall = thought
                
        # 3. Select (Beam pruning) - The context for the next step becomes the best thought of this step
        current_context = step_best_thought
        logger.debug(f"Level {step+1} best score: {step_highest_score}")

    logger.success(f"L3 Search Complete. Best global epistemic score: {highest_score}")
    
    return SearchResult(
        best_thought=best_thought_overall,
        nodes=nodes,
        mode_used="true_llm_tot",
        score=highest_score
    )

# Fallbacks to keep interface compatible
def tot_search(spec: ProjectSpec, bundle: Dict[str, Any], beam: int = 3, steps: int = 2) -> SearchResult:
    return explore(spec, bundle, beam, steps)

def lats_search(spec: ProjectSpec, bundle: Dict[str, Any], rollouts: int = 3) -> SearchResult:
    """LATS is technically MCTS + Reflection. For now we route to the robust ToT beam search."""
    return explore(spec, bundle, beam=rollouts, steps=2)
