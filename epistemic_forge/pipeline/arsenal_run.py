from __future__ import annotations
from loguru import logger
from dataclasses import dataclass
from typing import List, Optional

from epistemic_forge.memory.reflexion_store import ReflexionStore
from epistemic_forge.memory.skill_library import SkillLibrary
from epistemic_forge.models import Domain, ForgeResult, ProjectSpec
from epistemic_forge.pipeline.l1_optimizer import optimize_instruction
from epistemic_forge.pipeline.l2_conductor import conduct
from epistemic_forge.pipeline.l3_search import explore
from epistemic_forge.pipeline.l6_stages import produce_artifacts


@dataclass
class ArsenalRun:
    """Stateful runner with L5 memory across trials."""

    skills: SkillLibrary
    reflexion: ReflexionStore

    @classmethod
    def create(cls) -> "ArsenalRun":
        return cls(skills=SkillLibrary(), reflexion=ReflexionStore(window=3))

    def run(self, spec: ProjectSpec, out_dir: Optional[str] = None) -> ForgeResult:
        logger.info(f"Starting ArsenalRun for: {spec.title}")
        from epistemic_forge.models import RouteDecision
        
        # L0: Semantic Router
        route = route_project(spec)
        logger.info(f"Pipeline dynamically configured: {route.rationale}")
        
        # L1: OPRO Optimizer
        instruction = optimize_instruction(spec)
        
        # L2: Conductor & Experts
        conducted = conduct(spec, {'instruction': instruction, 'skills': []})
        
        # L3: Tree Search with PRM (Only if activated by L0)
        search_nodes = []
        best_thought = str(conducted)
        final_score = 0.5
        
        if route.activate.get("l3_search", True):
            search = explore(spec, conducted, beam=3, steps=2)
            search_nodes = search.nodes
            best_thought = search.best_thought
            final_score = search.score
        
        # L6: Stage Artifacts and Review (incorporates L4 Self-Refine internally)
        artifacts, review, score = produce_artifacts(spec, best_thought, conducted, final_score)
        
        return ForgeResult(
            spec=spec,
            route=route,
            instruction=instruction,
            claims=conducted.get('ClaimLatticeExpert', {}).get('claims', []),
            search_trace=search_nodes,
            reflections=self.reflexion.all(),
            skills_used=[],
            artifacts=artifacts,
            peer_review=review,
            final_score=score
        )

        instruction = optimize_instruction(spec)
        conducted = conduct(spec, {"instruction": instruction, "skills": []})
        search = explore(spec, conducted, beam=3, steps=2)
        artifacts, review, score = produce_artifacts(
            spec, search.best_thought, conducted, search.score
        )

        return ForgeResult(
            spec=spec,
            route=RouteDecision(families=["mock"], activate={}, rationale="mock"),
            instruction=instruction,
            claims=conducted.get('ClaimLatticeExpert', {}).get('claims', []),
            search_trace=search.nodes,
            reflections=self.reflexion.all(),
            skills_used=[],
            artifacts=artifacts,
            peer_review=review,
            final_score=score,
        )


def run_pipeline(
    title: str,
    question: str,
    domain: str = "hybrid",
    audience: str = "technical peer / client",
    keywords: Optional[List[str]] = None,
    constraints: Optional[List[str]] = None,
    max_trials: int = 3,
) -> ForgeResult:
    """Convenience API."""
    try:
        dom = Domain(domain)
    except ValueError:
        dom = Domain.HYBRID
    spec = ProjectSpec(
        title=title,
        question=question,
        domain=dom,
        audience=audience,
        keywords=keywords or [],
        constraints=constraints or [],
        max_trials=max_trials,
    )
    try:
        logger.info(f"Starting Epistemic Forge Pipeline for: '{title}'")
        result = ArsenalRun.create().run(spec)
        logger.success("Pipeline execution completed successfully.")
        return result
    except Exception as e:
        logger.exception(f"Critical Pipeline Failure: {str(e)}")
        raise SystemExit(1)
