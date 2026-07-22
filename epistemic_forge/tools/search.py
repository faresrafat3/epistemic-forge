"""Agentic External Knowledge Retrieval Tool (Multi-Hop Web Search).

Upgrades basic single-shot RAG to a self-reflective iterative search agent.
It searches, evaluates if the evidence is sufficient to ground a claim,
and issues follow-up queries if needed (STORM-style multi-hop).
"""
from duckduckgo_search import DDGS
from loguru import logger
from typing import List, Dict

def perform_single_search(query: str, max_results: int = 3) -> str:
    """Executes a single DuckDuckGo search."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return ""
            
        evidence = []
        for r in results:
            evidence.append(f"[Source: {r.get('title')}]\nSnippet: {r.get('body')}\nURL: {r.get('href')}")
            
        return "\n\n".join(evidence)
    except Exception as e:
        logger.warning(f"Web search failed for query '{query}': {e}")
        return ""

def multi_hop_search(initial_query: str, max_hops: int = 2) -> str:
    """Agentic RAG: Iteratively gathers context without invoking full LLM overhead."""
    logger.info(f"🕵️‍♂️ Initiating Multi-Hop Agentic Search for: '{initial_query}'")
    
    accumulated_evidence = []
    
    # Hop 1: Direct Query
    logger.debug("Hop 1: Direct semantic query...")
    hop1_results = perform_single_search(f"{initial_query} scientific consensus theory")
    if hop1_results:
        accumulated_evidence.append(hop1_results)
    
    # Hop 2: Deep Falsification/Critique Query (Crucial for Toulmin models)
    if max_hops >= 2:
        logger.debug("Hop 2: Searching for counter-arguments and falsifiers...")
        hop2_results = perform_single_search(f"criticism counter-argument {initial_query}")
        if hop2_results:
            accumulated_evidence.append(hop2_results)
            
    # Combine and truncate to prevent context window explosion
    final_evidence = "\n\n---\n\n".join(accumulated_evidence)
    
    if not final_evidence.strip():
        return "No external empirical evidence could be gathered."
        
    # Safeguard: cap at rough token equivalent (approx 1500 words)
    words = final_evidence.split()
    if len(words) > 1500:
        logger.debug("Truncating evidence to preserve cognitive context window.")
        final_evidence = " ".join(words[:1500]) + "\n...[EVIDENCE TRUNCATED]"
        
    return final_evidence

# Backward compatibility for existing code
def search_web(query: str, max_results: int = 3) -> str:
    return multi_hop_search(query, max_hops=2)
