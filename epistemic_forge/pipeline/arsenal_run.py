from __future__ import annotations

import asyncio
from dataclasses import dataclass

from loguru import logger

from epistemic_forge.errors import PipelineError
from epistemic_forge.memory.reflexion_store import ReflexionStore
from epistemic_forge.memory.skill_library import SkillLibrary
from epistemic_forge.models import Domain, ForgeResult, ProjectSpec, RouteDecision
from epistemic_forge.pipeline.l1_optimizer import optimize_instruction
from epistemic_forge.pipeline.l2_conductor import conduct_async
from epistemic_forge.pipeline.l3_search import explore
from epistemic_forge.pipeline.l6_stages import produce_artifacts
from epistemic_forge.pipeline.machine import PipelineContext, execute_pipeline
from epistemic_forge.pipeline.router import route_project


@dataclass
class ArsenalRun:
    """Stateful runner with L5 memory across trials."""

    skills: SkillLibrary
    reflexion: ReflexionStore

    @classmethod
    def create(cls) -> ArsenalRun:
        return cls(skills=SkillLibrary(), reflexion=ReflexionStore(window=3))

    def run(self, spec: ProjectSpec, out_dir: str | None = None) -> ForgeResult:
        logger.info(f"Starting ArsenalRun for: {spec.title}")
        ctx = PipelineContext(spec=spec)
        try:
            ctx = execute_pipeline(ctx)
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(
                f"Pipeline failed for '{spec.title}': {exc}", stage="run"
            ) from exc

        route = ctx.route or RouteDecision(
            families=["mock"], activate={}, rationale="mock"
        )
        return ForgeResult(
            spec=spec,
            route=route,
            instruction=ctx.instruction,
            claims=ctx.conducted.get("Grounded_Claim_Lattice_Generator", {}).get(
                "claims", []
            ),
            search_trace=list(ctx.search_result.nodes) if ctx.search_result else [],
            reflections=self.reflexion.all(),
            skills_used=[],
            artifacts=ctx.artifacts,
            peer_review=ctx.review or {},
            final_score=ctx.final_score,
        )


    async def arun(self, spec: ProjectSpec) -> ForgeResult:
        """Async variant: runs L2 experts concurrently via asyncio.gather."""
        logger.info(f"Starting async ArsenalRun for: {spec.title}")
        ctx = PipelineContext(spec=spec)
        try:
            ctx.route = await asyncio.to_thread(route_project, spec)
            ctx.instruction = await asyncio.to_thread(optimize_instruction, spec)
            ctx.conducted = await conduct_async(
                spec, {"instruction": ctx.instruction, "skills": []}
            )
            if ctx.route.activate.get("l3_search", True):
                ctx.search_result = await asyncio.to_thread(
                    explore, spec, ctx.conducted, 3, 2
                )

            best = ctx.search_result.best_thought if ctx.search_result else str(ctx.conducted)
            prior = ctx.search_result.score if ctx.search_result else 0.5
            artifacts, review, score = await asyncio.to_thread(
                produce_artifacts, spec, best, ctx.conducted, prior
            )
            ctx.artifacts, ctx.review, ctx.final_score = artifacts, review, score
        except Exception as exc:
            raise PipelineError(
                f"Async pipeline failed for '{spec.title}': {exc}", stage="arun"
            ) from exc

        return ForgeResult(
            spec=spec,
            route=ctx.route,
            instruction=ctx.instruction,
            claims=ctx.conducted.get("Grounded_Claim_Lattice_Generator", {}).get(
                "claims", []
            ),
            search_trace=list(ctx.search_result.nodes) if ctx.search_result else [],
            reflections=self.reflexion.all(),
            skills_used=[],
            artifacts=ctx.artifacts,
            peer_review=ctx.review or {},
            final_score=ctx.final_score,
        )


async def run_pipeline(
    title: str,
    question: str,
    domain: str = "hybrid",
    audience: str = "technical peer / client",
    keywords: list[str] | None = None,
    constraints: list[str] | None = None,
    max_trials: int = 3,
    target_model: str = "gpt-4o-mini",
    api_base: str | None = None,
    async_run: bool = False,
) -> ForgeResult:
    """Convenience API for library and CLI users.

    Library code must not call ``sys.exit``; on failure we raise a typed
    :class:`PipelineError` so callers decide how to surface it.
    """
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
        target_model=target_model,
        api_base=api_base,
    )
    logger.info(f"Starting Epistemic Forge Pipeline for: '{title}'")
    runner = ArsenalRun.create()
    try:
        result = asyncio.run(runner.arun(spec)) if async_run else runner.run(spec)
    except PipelineError:
        raise
    except Exception as exc:
        logger.exception(f"Critical Pipeline Failure: {exc}")
        raise PipelineError(f"Pipeline failed: {exc}") from exc
    logger.success("Pipeline execution completed successfully.")
    return result
