"""L1 — Instruction Optimizer (APE + OPRO fallback friendly)."""

from dataclasses import dataclass
from typing import List

from epistemic_forge.llm import generate_structured
from epistemic_forge.models import OptimizedInstruction, ProjectSpec
from loguru import logger


@dataclass
class InstructionCandidate:
    instruction: str
    score: float


def _seed_instructions(spec: ProjectSpec) -> list[str]:
    domain = str(spec.domain.value if hasattr(spec.domain, "value") else spec.domain)
    keyword_hint = ", ".join(spec.keywords) if spec.keywords else "core constraints"
    return [
        (
            "Build a structured response with: core question, claims, supports, objections, "
            "confidence qualifiers, limits, and next actions. Keep assumptions explicit."
        ),
        (
            f"Target domain={domain}. Provide a pragmatic baseline first, then controlled "
            f"improvements. Integrate keywords: {keyword_hint}. Avoid overclaiming."
        ),
        (
            "Use a staged plan: define falsifiable criteria, propose 2 alternatives, compare "
            "trade-offs, then deliver a concise action checklist."
        ),
    ]


def _score_instruction(spec: ProjectSpec, instruction: str, generation: int = 0) -> float:
    score = 0.4 + 0.05 * generation
    q_tokens = {t.lower() for t in spec.question.split() if len(t) > 3}
    i_tokens = {t.lower().strip(".,:;!?") for t in instruction.split()}
    overlap = len(q_tokens & i_tokens)
    score += min(0.35, overlap * 0.03)
    if spec.keywords:
        kw_overlap = sum(1 for kw in spec.keywords if kw.lower() in instruction.lower())
        score += min(0.2, kw_overlap * 0.04)
    return round(max(0.01, min(score, 0.99)), 4)


def ape_generate(spec: ProjectSpec) -> List[InstructionCandidate]:
    """Generate deterministic APE-style instruction seeds with heuristic scoring."""
    seeds = _seed_instructions(spec)
    ranked = [InstructionCandidate(instruction=s, score=_score_instruction(spec, s)) for s in seeds]
    ranked.sort(key=lambda c: c.score, reverse=True)
    return ranked


def opro_evolve(
    candidates: List[InstructionCandidate], spec: ProjectSpec, steps: int = 2
) -> List[InstructionCandidate]:
    """Deterministically evolve instructions OPRO-style while preserving stability."""
    pool = list(candidates) if candidates else ape_generate(spec)
    for step in range(max(1, steps)):
        base = pool[step % len(pool)]
        evolved = (
            f"{base.instruction} Validate each major claim with an explicit warrant and "
            f"include one falsifier check before final recommendations."
        )
        pool.append(
            InstructionCandidate(
                instruction=evolved,
                score=_score_instruction(spec, evolved, generation=step + 1),
            )
        )
    pool.sort(key=lambda c: c.score, reverse=True)
    return pool


def optimize_instruction(spec: ProjectSpec) -> str:
    """Generate best instruction via LLM, with deterministic fallback for CI/offline runs."""
    logger.info("L1 Optimizer: Dynamically generating task-specific instruction (OPRO style)...")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Meta-Prompting Optimizer (OPRO). Read the user's task and generate "
                "a constrained, step-by-step system instruction that minimizes hallucinations."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Task Domain: {spec.domain}\nQuestion: {spec.question}\nKeywords: {spec.keywords}\n"
                "Generate the optimized instruction."
            ),
        },
    ]

    try:
        result: OptimizedInstruction = generate_structured(
            messages=messages,
            response_model=OptimizedInstruction,
            model=spec.target_model,
            api_base=spec.api_base,
            api_key=spec.api_key,
        )
        logger.debug(
            "L1 Optimization Complete. Expected failure modes mitigated: "
            f"{result.expected_failure_modes}"
        )
        return result.meta_prompt
    except Exception as exc:
        logger.warning(f"L1 Optimizer fallback engaged due to LLM failure: {exc}")
        return opro_evolve(ape_generate(spec), spec, steps=2)[0].instruction
