"""External Knowledge Retrieval Tool (Web Search).

Provides live grounding for Claim Lattices without requiring paid API keys
(using DuckDuckGo Search).
"""

from duckduckgo_search import DDGS
from loguru import logger


def search_web(query: str, max_results: int = 3) -> str:
    """Performs a web search and returns concatenated evidence."""
    logger.info(f"🔍 Executing Live Web Search for: '{query}'")
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No external evidence found."

        evidence = []
        for r in results:
            evidence.append(
                f"[Source: {r.get('title')}]\nSnippet: {r.get('body')}\nURL: {r.get('href')}"
            )

        return "\n\n".join(evidence)
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return "Search tool temporarily unavailable."
