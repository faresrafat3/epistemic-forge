"""Writing expert — outlines and drafts."""

from __future__ import annotations

from typing import Any, Dict, List

from epistemic_forge.models import ProjectSpec


def outline_and_draft(
    spec: ProjectSpec, claims_bundle: Dict[str, Any], instruction: str
) -> Dict[str, Any]:
    claims: List[Dict[str, Any]] = claims_bundle.get("claims", [])
    outline = [
        "Hook / stakes",
        "Core question",
        "Claim lattice",
        "Objections & steelman",
        "Working synthesis",
        "Limits",
        "Next actions",
    ]
    body_bits = []
    for c in claims:
        body_bits.append(f"### {c['id']}: {c['text']}\n")
        if c.get("support"):
            body_bits.append("Supports:\n" + "\n".join(f"- {s}" for s in c["support"]))
        if c.get("objections"):
            body_bits.append(
                "\nObjections:\n" + "\n".join(f"- {o}" for o in c["objections"])
            )
        body_bits.append("")

    draft = f"""# {spec.title}

## Core question
{spec.question}

## Instruction in force
{instruction}

## Audience
{spec.audience}

## Outline
""" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(outline)) + "\n\n## Claim lattice\n\n" + "\n".join(body_bits)

    return {"outline": outline, "draft_markdown": draft}
