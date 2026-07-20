from __future__ import annotations
from loguru import logger
"""Full ARSENAL-inspired pipeline orchestration for Epistemic Forge."""


from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from epistemic_forge.memory.reflexion_store import ReflexionStore
from epistemic_forge.memory.skill_library import SkillLibrary
from epistemic_forge.models import (
    Domain,
    ForgeResult,
    ProjectSpec,
)
from epistemic_forge.pipeline.l1_optimizer import optimize_instruction
from epistemic_forge.pipeline.l2_conductor import conduct
from epistemic_forge.pipeline.l3_search import explore
from epistemic_forge.pipeline.l4_refine import refine_document
from epistemic_forge.pipeline.l6_stages import produce_artifacts
from epistemic_forge.pipeline.router import route_project


@dataclass
class ArsenalRun:
    """Stateful runner with L5 memory across trials."""

    skills: SkillLibrary
    reflexion: ReflexionStore

    @classmethod
    def create(cls) -> "ArsenalRun":
        return cls(skills=SkillLibrary(), reflexion=ReflexionStore(window=3))

    def run(self, spec: ProjectSpec) -> ForgeResult:
        route = route_project(spec)
        trial_log: List[Dict[str, Any]] = []
        best: Optional[ForgeResult] = None

        for trial in range(1, spec.max_trials + 1):
            # L1
            instruction, candidates = optimize_instruction(spec, route)
            # Inject reflexion lessons into instruction context
            lessons = self.reflexion.as_prompt_block()
            if "No prior" not in lessons:
                instruction = instruction + f" Prior lessons: {lessons}"

            # L5 skills retrieve (Voyager-style)
            skills_used: List[str] = []
            if route.activate.get("voyager") and spec.enable_skills:
                retrieved = self.skills.retrieve(
                    spec.question + " " + spec.domain.value, top_k=3
                )
                skills_used = [s.name for s in retrieved]

            # L2
            conducted = conduct(spec, instruction, skills_used)

            # L3
            search = explore(spec, conducted.final_bundle, route.l3_mode)

            # L6 production (includes L4 refine inside)
            artifacts, review, score = produce_artifacts(
                spec=spec,
                instruction=instruction,
                bundle=conducted.final_bundle,
                best_thought=search.best_thought,
                search_score=search.score,
                skills_used=skills_used,
                reflections_block=self.reflexion.as_prompt_block(),
            )

            # Optional extra polish on executive summary
            if artifacts:
                polished, _ = refine_document(artifacts[0].content, spec, max_iters=1)
                artifacts[0].content = polished

            claims_raw = conducted.final_bundle.get("claims", {}).get("claims", [])
            from epistemic_forge.models import Claim, Confidence

            claims = []
            for c in claims_raw:
                claims.append(
                    Claim(
                        id=c["id"],
                        text=c["text"],
                        support=c.get("support", []),
                        objections=c.get("objections", []),
                        confidence=Confidence(c.get("confidence", "likely")),
                        sources=c.get("sources", []),
                        tags=c.get("tags", []),
                    )
                )

            result = ForgeResult(
                spec=spec,
                route=route,
                instruction=instruction,
                claims=claims,
                search_trace=search.nodes,
                reflections=self.reflexion.all(),
                skills_used=skills_used,
                artifacts=artifacts,
                peer_review=review,
                trial_log=trial_log.copy(),
                final_score=score,
            )

            trial_log.append(
                {
                    "trial": trial,
                    "score": score,
                    "review": review["verdict"],
                    "instruction_preview": instruction[:160],
                    "l1_mode": route.l1_mode,
                    "l3_mode": search.mode_used,
                    "n_candidates": len(candidates),
                }
            )
            result.trial_log = trial_log.copy()

            if best is None or score > best.final_score:
                best = result

            # Success threshold
            if score >= 0.72 and review["overall"] >= 0.65:
                # Voyager-like skill add on success
                if route.activate.get("voyager") and spec.enable_skills:
                    from epistemic_forge.models import Skill

                    self.skills.add(
                        Skill(
                            name=f"success_{spec.domain.value}_{trial}",
                            description=f"Successful packaging pattern for {spec.title}",
                            code="# captured as narrative skill\n",
                            tags=[spec.domain.value, "success"],
                        )
                    )
                break

            # L5 reflect on failure
            self.reflexion.reflect_on_failure(
                trial=trial,
                score=score,
                notes=f"verdict={review['verdict']}; missing={review.get('revision_needed')}",
            )

        assert best is not None
        best.reflections = self.reflexion.all()
        return best


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
