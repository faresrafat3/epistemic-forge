"""Export forge results to a project directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from epistemic_forge.models import ForgeResult


def export_result(result: ForgeResult, out_dir: Union[str, Path]) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result_dict = result.model_dump() if hasattr(result, "model_dump") else result.to_dict()
    (out / "result.json").write_text(
        json.dumps(result_dict, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for art in result.artifacts:
        # path_hint like outputs/foo.md → use name + suffix
        name = art.path_hint.split("/")[-1] if art.path_hint else f"{art.name}.txt"
        (out / name).write_text(art.content, encoding="utf-8")
    # Manifest
    manifest = {
        "title": result.spec.title,
        "domain": result.spec.domain.value,
        "score": result.final_score,
        "review": result.peer_review,
        "files": [a.path_hint or a.name for a in result.artifacts],
        "route": result.route.model_dump() if hasattr(result.route, "model_dump") else result.route.to_dict(),
        "instruction": result.instruction,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out
