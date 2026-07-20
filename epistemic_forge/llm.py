"""Universal LLM Engine (Hermes-style Router).

Absolute flexibility: Use ANY model from ANY provider with zero code changes.
Supports standard formats: 'openai/gpt-4o', 'anthropic/claude-3-sonnet', 'ollama/llama3', 'azure/...', etc.
"""
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import instructor
from litellm import completion

# We patch instructor to use LiteLLM's universal completion directly!
# This is the "Hermes" way: we don't switch clients, we use one universal proxy.
try:
    client = instructor.from_litellm(completion)
except Exception as e:
    logger.warning(f"LiteLLM/Instructor initialization failed: {e}")
    client = None

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
            call_params["api_key"] = api_key
            
        # Add any extra kwargs (like top_p, max_tokens) dynamically
        call_params.update(kwargs)
            
        # Seed is standard in LiteLLM for supported models
        if "gpt" in model or "llama" in model:
            call_params["seed"] = seed
            
        response = client.chat.completions.create(**call_params)
        return response
        
    except Exception as e:
        logger.error(f"🌐 [Hermes Router] Critical Failure for model '{model}': {str(e)}")
        raise
