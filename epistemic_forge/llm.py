"""SOTA LLM Engine using Instructor and Pydantic for Strict Structured Outputs."""
import instructor
from openai import OpenAI
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    client = instructor.from_openai(OpenAI())
except Exception as e:
    logger.warning(f"OpenAI client init failed (missing key?): {e}")
    client = None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_structured(
    messages: list, 
    response_model: type[BaseModel], 
    model: str = "gpt-4o-2024-08-06", 
    temperature: float = 0.0
) -> BaseModel:
    """
    State-of-the-Art Structured Extraction.
    Guarantees the output strictly matches the Pydantic schema using JSON Mode / Tool Calls.
    """
    if not client:
        raise ValueError("LLM Client is not initialized. Please set OPENAI_API_KEY.")
        
    try:
        logger.debug(f"Initiating strict structured call to {model} for schema [{response_model.__name__}]...")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=response_model,
            temperature=temperature,
        )
        return response
    except Exception as e:
        logger.error(f"SOTA LLM API Critical Failure: {str(e)}")
        raise
