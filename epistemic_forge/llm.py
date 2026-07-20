"""Robust LLM Wrapper with Retry Logic and Logging."""
from litellm import completion
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(messages: list, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """Call an LLM with automatic retries, fallback, and tracking."""
    try:
        logger.debug(f"Initiating neural call to {model}...")
        response = completion(model=model, messages=messages, temperature=temperature)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM API Critical Failure: {str(e)}")
        raise
