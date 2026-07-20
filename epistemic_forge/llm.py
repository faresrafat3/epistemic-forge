"""Omni-Provider LLM Engine for Absolute Flexibility.
Supports: OpenAI, Anthropic, Gemini, Ollama, vLLM, Azure, etc.
Enforces: Strict Pydantic JSON Schemas.
"""
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import instructor
from litellm import completion

def get_instructor_client(model: str):
    """Dynamically route the instructor client based on the model provider."""
    import openai
    import anthropic
    import google.generativeai as genai
    
    if model.startswith("claude"):
        return instructor.from_anthropic(anthropic.Anthropic())
    elif model.startswith("gemini"):
        return instructor.from_gemini(genai.GenerativeModel(model))
    else:
        # Default to OpenAI / LiteLLM proxy / Ollama Local
        return instructor.from_openai(openai.OpenAI())

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_structured(
    messages: list, 
    response_model: type[BaseModel], 
    model: str = "gpt-4o-mini", 
    temperature: float = 0.0,
    seed: int = 42,
    api_base: str = None
) -> BaseModel:
    """
    Omni-Provider Structured Extraction.
    Allows passing ANY model (local Ollama, Claude, GPT, Groq).
    """
    try:
        logger.debug(f"Routing neural call to [{model}] for schema [{response_model.__name__}]...")
        
        # We use instructor's dynamic client routing
        client = get_instructor_client(model)
        
        kwargs = {
            "model": model,
            "messages": messages,
            "response_model": response_model,
            "temperature": temperature,
        }
        
        # Only inject seed if the provider supports it (like OpenAI)
        if "gpt" in model or "llama" in model:
            kwargs["seed"] = seed
            
        if api_base: # For Local Ollama or vLLM routing
            kwargs["base_url"] = api_base
            
        response = client.chat.completions.create(**kwargs)
        return response
        
    except Exception as e:
        logger.error(f"Omni-Provider API Failure for {model}: {str(e)}")
        raise
