"""FastAPI Backend for Epistemic Forge.

Provides a RESTful Enterprise-Ready API to integrate the Neuro-Symbolic 
engine into any larger MLOps or business workflow.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from epistemic_forge.models import ProjectSpec
from epistemic_forge.pipeline.arsenal_run import run_pipeline

app = FastAPI(
    title="Epistemic Forge API",
    description="Neuro-Symbolic State Machine API for Deterministic Reasoning.",
    version="1.0.0-rc1"
)

class ForgeRequest(BaseModel):
    title: str
    question: str
    domain: str = "hybrid"
    target_model: str = "openai/gpt-4o-mini"
    keywords: List[str] = []
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    budget_tokens: int = 15000

class ForgeResponse(BaseModel):
    status: str
    score: float
    claims: List[Dict[str, Any]]
    final_memo: str
    peer_review: Dict[str, Any]

@app.post("/api/v1/forge", response_model=ForgeResponse)
async def generate_claim_lattice(req: ForgeRequest):
    """Executes the full L0-L6 pipeline and returns a structured lattice and synthesis."""
    try:
        spec = ProjectSpec(
            title=req.title,
            question=req.question,
            domain=req.domain,
            target_model=req.target_model,
            keywords=req.keywords,
            api_key=req.api_key,
            api_base=req.api_base,
            budget_tokens=req.budget_tokens
        )
        
        result = run_pipeline(
            title=spec.title,
            question=spec.question,
            domain=spec.domain.value
        )
        
        final_memo = ""
        for art in getattr(result, "artifacts", []):
            if art.name == "Final Synthesis Memo":
                final_memo = art.content
                break
                
        # Handle claims safely
        raw_claims = getattr(result, "claims", [])
        claims_list = [c.model_dump() if hasattr(c, "model_dump") else c for c in raw_claims]
                
        return ForgeResponse(
            status="success",
            score=getattr(result, "final_score", 0.0),
            claims=claims_list,
            final_memo=final_memo,
            peer_review=getattr(result, "peer_review", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "operational", "engine": "neuro-symbolic-v1"}
