"""Universal LLM Engine (Hermes-style Router).

Absolute flexibility: Use ANY model from ANY provider with zero code changes.
Supports standard formats: 'openai/gpt-4o', 'anthropic/claude-3-sonnet', 'ollama/llama3', 'azure/...', etc.
"""
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import instructor
from litellm import completion
from epistemic_forge.memory.economy import budget_manager
import os

# We patch instructor to use LiteLLM's universal completion directly!
# This is the "Hermes" way: we don't switch clients, we use one universal proxy.
try:
    client = instructor.from_litellm(completion)
except Exception as e:
    logger.warning(f"LiteLLM/Instructor initialization failed: {e}")
    client = None


def _offline_fallback(response_model: type[BaseModel], messages: list) -> BaseModel:
    """Deterministic fallback for CI/offline runs without provider credentials."""
    prompt = ""
    if messages:
        prompt = str(messages[-1].get("content", ""))
    lower = prompt.lower()
    model_name = response_model.__name__

    if model_name == "OptimizedInstruction":
        return response_model(
            meta_prompt=(
                "## Core question\nRestate the problem as a falsifiable claim.\n"
                "## Claim\nProvide a clear recommendation.\n"
                "## Supports\nGround with evidence/metric or concrete rationale.\n"
                "## Objections\nSteelman the strongest risk/counterpoint.\n"
                "## Confidence and limits\nState assumptions and uncertainty explicitly.\n"
                "## Next actions\nList 3 concrete steps with acceptance criteria."
            ),
            rationale="Structured Toulmin-style prompt improves rigor and actionability.",
            expected_failure_modes=["overclaiming", "missing counterarguments", "unclear next steps"],
        )
    if model_name == "ThoughtProposalsOutput":
        return response_model(
            proposals=[
                {
                    "thought_text": (
                        "# Working thesis\nWe should start with a transparent baseline, then iterate.\n"
                        "## Evidence\nUse domain cues and explicit metrics to justify choices.\n"
                        "## Objection\nComplexity may hide leakage or weak assumptions.\n"
                        "## Qualifier\nThis is likely effective but should be validated.\n"
                        "## Next steps\n1. Define metric\n2. Run baseline\n3. Compare alternatives"
                    )
                }
            ]
        )
    if model_name == "ThoughtEvaluation":
        return response_model(epistemic_score=0.78, critique="Grounded, cautious, and testable.")
    if model_name == "RefinementFeedback":
        return response_model(
            clarity_score=0.86,
            epistemic_humility_score=0.9,
            critical_flaws=[],
            passes_threshold=True,
        )
    if model_name == "RefinedArtifact":
        return response_model(
            improved_text=(
                "# Final synthesis\n## Core question\nA clear stance with explicit bounds.\n"
                "## Claim\nRecommendation with rationale.\n## Supports\nEvidence and baseline metrics.\n"
                "## Objections\nRisks and counterarguments.\n## Confidence\nProvisional, assumption-aware.\n"
                "## Next actions\n- Ship baseline\n- Audit failure cases\n- Decide next experiment"
            ),
            changes_made=["added explicit objections", "added assumptions", "added action checklist"],
        )
    if model_name == "FinalPeerReview":
        return response_model(
            scores={"clarity": 0.82, "structure": 0.84, "soundness": 0.79, "actionability": 0.86, "humility": 0.88},
            overall_score=0.84,
            revision_needed=[],
            verdict="accept_with_minor_revisions",
            final_comments="Coherent, actionable, and appropriately qualified.",
        )
    if model_name == "DynamicExpertSchema":
        return response_model(
            expert_class_name="PragmaticRiskExpert",
            expert_description="Extracts risks, assumptions, and validation checks.",
            fields_to_extract=[{"risk": "Main failure mode"}, {"check": "Validation action"}],
            system_prompt="Extract concrete risks and validation steps only.",
        )
    if model_name == "ClaimLatticeOutput":
        return response_model(
            claims=[
                {
                    "id": "C1",
                    "text": "A staged baseline-first plan is the most reliable starting point.",
                    "epistemic_warrant": "Simple baselines reduce hidden complexity and expose key errors early.",
                    "potential_falsifier": "If baseline fails under robust validation while alternatives succeed.",
                    "support": ["Transparent metrics", "Reproducible splits"],
                    "objections": ["May underfit initially"],
                    "confidence": "likely",
                }
            ],
            lattice_summary="One grounded claim with explicit warrant and falsifier.",
        )
    if model_name == "HegelianDialecticOutput":
        return response_model(
            steelmanned_antithesis="A baseline-first plan may delay superior approaches.",
            synthesis_resolution="Use baseline for calibration, then escalate only with measured gains.",
            remaining_uncertainties=["Data leakage risk", "Metric sensitivity"],
            epistemic_confidence=0.74,
            source_warrant="Decision quality improves when comparisons share a common validated baseline.",
        )
    if model_name == "RigorSentinelOutput":
        return response_model(
            epistemic_blind_spots=["Hidden leakage pathways", "Untracked distribution shift"],
            falsification_metric="Out-of-fold score stability across robust split schemes.",
            robust_baseline="Simple regularized model with strict CV and leakage audit.",
        )

    return response_model()


def _missing_credentials(model: str, api_key: str | None) -> bool:
    if api_key:
        return False
    model_l = model.lower()
    if "gpt" in model_l or "openai" in model_l:
        return not os.getenv("OPENAI_API_KEY")
    if "openrouter" in model_l:
        return not os.getenv("OPENROUTER_API_KEY")
    if "gemini" in model_l:
        return not os.getenv("GEMINI_API_KEY")
    return False

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_structured(
    messages: list, 
    response_model: type[BaseModel], 
    model: str = "gpt-4o-mini",  # Can be ANY litellm supported string, e.g., 'ollama/llama3'
    temperature: float = 0.0,
    seed: int = 42,
    api_base: str = None,
    api_key: str = None,
    **kwargs
) -> BaseModel:
    """
    Universal Hermes-style Structured Extraction.
    You can pass the provider in the model string (e.g., 'anthropic/claude-3-opus-20240229').
    """
    if _missing_credentials(model, api_key):
        logger.warning(f"🌐 [Hermes Router] Missing credentials for [{model}], using deterministic fallback.")
        return _offline_fallback(response_model, messages)

    if not client:
        raise ValueError("Universal LLM Router is not initialized.")
        
    try:
        logger.debug(f"🌐 [Hermes Router] Dispatching to [{model}] for schema [{response_model.__name__}]...")
        
        call_params = {
            "model": model,
            "messages": messages,
            "response_model": response_model,
            "temperature": temperature,
        }
        
        # Inject optional routing Overrides
        if api_base:
            call_params["api_base"] = api_base
        if api_key:
            # Force it into environment for litellm
            if "openrouter" in model:
                os.environ["OPENROUTER_API_KEY"] = api_key
            elif "gemini" in model:
                os.environ["GEMINI_API_KEY"] = api_key
            else:
                os.environ["OPENAI_API_KEY"] = api_key
            call_params["api_key"] = api_key
            
        # Add any extra kwargs (like top_p, max_tokens) dynamically
        call_params.update(kwargs)
            
        # Seed is standard in LiteLLM for supported models
        if "gpt" in model or "llama" in model:
            call_params["seed"] = seed
            
        response = client.chat.completions.create(**call_params)
        budget_manager.add_usage(response._raw_response, model)
        return response
        
    except Exception as e:
        logger.error(f"🌐 [Hermes Router] Critical Failure for model '{model}': {str(e)}")
        raise
