"""Explicit pipeline stage machine (L0–L6).

The original pipeline was a linear chain of function calls with the layer
activation logic hidden inside ``if`` statements in ``arsenal_run.py``. This
module makes the *state machine* explicit and inspectable:

* :class:`PipelineContext` is a single typed object that carries state between
  stages (replacing ad-hoc ``Dict[str, Any]`` context passing).
* :data:`STAGES` is a registry describing every stage, its function, and the
  predicate that decides whether it runs for a given context. This is what lets
  the L0 router *actually* toggle layers instead of the activation map being
  ignored.
* :func:`execute_pipeline` runs only the enabled stages, in order, recording
  which ran.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from epistemic_forge.errors import PipelineError
from epistemic_forge.models import (
    ProjectSpec,
    RouteDecision,
    SearchResult,
    StageArtifact,
)
from epistemic_forge.pipeline.l1_optimizer import optimize_instruction
from epistemic_forge.pipeline.l2_conductor import conduct
from epistemic_forge.pipeline.l3_search import explore
from epistemic_forge.pipeline.l6_stages import produce_artifacts
from epistemic_forge.pipeline.router import route_project


@dataclass
class PipelineContext:
    """Typed, versioned carrier of intermediate pipeline state."""

    spec: ProjectSpec
    route: RouteDecision | None = None
    instruction: str = ""
    conducted: dict[str, Any] = field(default_factory=dict)
    search_result: SearchResult | None = None
    artifacts: list[StageArtifact] = field(default_factory=list)
    review: dict[str, Any] | None = None
    final_score: float = 0.0
    stages_run: list[str] = field(default_factory=list)

    def assert_route(self) -> RouteDecision:
        if self.route is None:
            raise PipelineError("PipelineContext has no RouteDecision.", stage="L0")
        return self.route


# Each entry: (stage_name, callable(ctx) -> ctx, enabled?(ctx) -> bool)
_STAGE_FN = Callable[["PipelineContext"], "PipelineContext"]

STAGES: list[dict[str, Any]] = [
    {
        "name": "L0_router",
        "run": lambda ctx: _set(ctx, "route", route_project(ctx.spec)),
        "enabled": lambda ctx: ctx.route is None,
    },
    {
        "name": "L1_optimizer",
        "run": lambda ctx: _set(ctx, "instruction", optimize_instruction(ctx.spec)),
        "enabled": lambda ctx: True,
    },
    {
        "name": "L2_conductor",
        "run": lambda ctx: _set(
            ctx,
            "conducted",
            conduct(ctx.spec, {"instruction": ctx.instruction, "skills": []}),
        ),
        "enabled": lambda ctx: True,
    },
    {
        "name": "L3_search",
        "run": lambda ctx: _set(
            ctx, "search_result", explore(ctx.spec, ctx.conducted, beam=3, steps=2)
        ),
        "enabled": lambda ctx: ctx.assert_route().activate.get("l3_search", True),
    },
    {
        "name": "L6_review",
        "run": lambda ctx: _finalize(ctx),
        "enabled": lambda ctx: True,
    },
]


def _set(ctx: PipelineContext, attr: str, value: Any) -> PipelineContext:
    setattr(ctx, attr, value)
    return ctx


def _finalize(ctx: PipelineContext) -> PipelineContext:
    best = ctx.search_result.best_thought if ctx.search_result else str(ctx.conducted)
    prior = ctx.search_result.score if ctx.search_result else 0.5
    artifacts, review, score = produce_artifacts(
        ctx.spec, best, ctx.conducted, prior
    )
    ctx.artifacts = artifacts
    ctx.review = review
    ctx.final_score = score
    return ctx


def planned_stages(spec: ProjectSpec) -> list[str]:
    """Return the ordered list of stage names that *would* run for a spec.

    Useful for introspection, tests, and honest documentation of what the
    router actually activated.
    """
    ctx = PipelineContext(spec=spec)
    ctx.route = route_project(spec)
    return [s["name"] for s in STAGES if s["enabled"](ctx)]


def execute_pipeline(ctx: PipelineContext) -> PipelineContext:
    """Run every enabled stage in order, mutating and returning ``ctx``."""
    for stage in STAGES:
        if stage["enabled"](ctx):
            try:
                ctx = stage["run"](ctx)
                ctx.stages_run.append(stage["name"])
            except Exception as exc:  # pragma: no cover - surfaced to caller
                raise PipelineError(
                    f"Stage {stage['name']} failed: {exc}", stage=stage["name"]
                ) from exc
    return ctx
