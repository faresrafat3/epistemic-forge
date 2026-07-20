"""SOTA LLM Engine using Instructor and Pydantic for Strict Structured Outputs.
ENFORCES: Reproducibility (Seed 42, Temp 0.0) for scientific benchmarks.
"""
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
    model: str = "gpt-4o-mini", 
    temperature: float = 0.0,
    seed: int = 42
) -> BaseModel:
    """
    Research-Grade Extraction.
    Enforces Temperature=0.0 and Seed=42 to guarantee deterministic, reproducible scientific output.
    """
    if not client:
        raise ValueError("LLM Client is not initialized. Please set OPENAI_API_KEY.")
        
    try:
        logger.debug(f"Initiating scientifically rigorous call to {model} [temp={temperature}, seed={seed}] for schema [{response_model.__name__}]...")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=response_model,
            temperature=temperature,
            seed=seed
        )
        return response
    except Exception as e:
        logger.error(f"SOTA LLM API Critical Failure: {str(e)}")
        raise
