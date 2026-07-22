"""L0 — Semantic Technique Router (SOTA LLM-Based Routing).

Replaces rigid heuristics with a Semantic Router that analyzes the 
epistemic complexity of the query to dynamically toggle architectural layers 
(L1-L6) to save tokens (Cognitive Economy) while maintaining rigor.
"""
from epistemic_forge.models import ProjectSpec, RouteDecision
from epistemic_forge.llm import generate_structured
from loguru import logger

def route_project(spec: ProjectSpec) -> RouteDecision:
    """Dynamically routes the project through the optimal cognitive layers."""
    
    logger.info("L0 Router: Analyzing epistemic complexity to dynamically route execution...")
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are an Elite L0 Architectural Router. Analyze the user's inquiry and determine exactly which cognitive layers are required to solve it. "
                "If it's a simple query, turn off heavy layers (like L3 Tree Search) to save compute. "
                "If it's deeply complex or philosophical, activate L3 and L4 (Self-Refine)."
            )
        },
        {"role": "user", "content": f"Inquiry: {spec.question}\nDomain: {spec.domain}\n\nDetermine the optimal routing architecture."}
    ]
    
    try:
        decision: RouteDecision = generate_structured(
            messages=messages,
            response_model=RouteDecision,
            model=spec.target_model,  # We use the fast/cheap model for routing
            api_base=spec.api_base
        )
        logger.debug(f"L0 Routing Complete. Activation map: {decision.activate}")
        return decision
    except Exception as e:
        logger.warning(f"L0 Semantic Routing failed: {e}. Falling back to default heavy architecture.")
        # Failsafe routing ensuring maximum rigor if the LLM fails
        return RouteDecision(
            families=["Heuristic Fallback"],
            activate={"l3_search": True, "l4_refine": True, "l6_stages": True},
            l1_mode="opro",
            l3_mode="tot",
            rationale="Fallback to maximum rigor due to routing failure."
        )
