"""SOTA Artifact Exporter (I/O).

Transforms internal representations into Enterprise-Ready Deliverables:
- 📊 Mermaid.js embedded Markdown for visual Claim Lattices.
- 📓 Jupyter Notebooks (.ipynb) for Kaggle Baselines.
- 🧠 Obsidian-compatible JSON graphs for Personal Knowledge Management (PKM).
"""
import os
import json
from pathlib import Path
from loguru import logger
import nbformat as nbf
from epistemic_forge.models import ForgeResult

def _generate_mermaid_graph(claims) -> str:
    """Generates a Mermaid.js flowchart from the Claim Lattice."""
    lines = ["graph TD"]
    for c in claims:
        # Pydantic safety
        c_dict = c.model_dump() if hasattr(c, "model_dump") else c
        c_id = c_dict.get("id", "Unknown")
        c_text = c_dict.get("text", "").replace('"', "'")[:50] + "..."
        lines.append(f'    {c_id}["{c_id}: {c_text}"]')
        
        for s in c_dict.get("support", []):
            lines.append(f'    {c_id} -->|Supports| S_{hash(s) % 1000}["{s[:40]}..."]')
        for o in c_dict.get("objections", []):
            lines.append(f'    {c_id} -.->|Objects| O_{hash(o) % 1000}["{o[:40]}..."]')
    return "\n".join(lines)

def _export_jupyter_notebook(artifact, out_path: Path):
    """Converts a python/markdown artifact into a runnable Jupyter Notebook."""
    nb = nbf.v4.new_notebook()
    cells = []
    
    # Split artifact content heuristically (Markdown vs Code)
    chunks = artifact.content.split("```python")
    cells.append(nbf.v4.new_markdown_cell(chunks[0]))
    
    for chunk in chunks[1:]:
        if "```" in chunk:
            code, md = chunk.split("```", 1)
            cells.append(nbf.v4.new_code_cell(code.strip()))
            if md.strip():
                cells.append(nbf.v4.new_markdown_cell(md.strip()))
        else:
            cells.append(nbf.v4.new_code_cell(chunk.strip()))
            
    nb.cells = cells
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

def export_result(result: ForgeResult, out_dir: str):
    """Main SOTA Export router."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    logger.info(f"💾 SOTA I/O: Exporting Enterprise Artifacts to {out.resolve()}...")

    # 1. Executive Summary & Memo (with Mermaid Graph)
    memo_path = out / "executive_summary.md"
    mermaid_code = _generate_mermaid_graph(result.claims)
    
    memo_content = f"""---
title: {result.spec.title}
domain: {result.spec.domain}
score: {result.final_score}
---
# Executive Synthesis
**Inquiry:** {result.spec.question}

## Epistemic Claim Lattice (Visual)
```mermaid
{mermaid_code}
```

## AI Peer Review Verdict
**Verdict:** `{result.peer_review.get('verdict', 'Unknown').upper()}`
**Critique:** {result.peer_review.get('final_comments', '')}
"""
    
    # Add final synthesized text
    for art in result.artifacts:
        if art.name == "Final Synthesis Memo":
            memo_content += f"\n\n## Deep Synthesis\n\n{art.content}"

    with open(memo_path, "w", encoding="utf-8") as f:
        f.write(memo_content)

    # 2. Machine-Readable Knowledge Graph (Obsidian/JSON)
    json_path = out / "claim_lattice_graph.json"
    with open(json_path, "w", encoding="utf-8") as f:
        # Convert claims to a node-edge graph format
        nodes = []
        edges = []
        for c in result.claims:
            c_dict = c.model_dump() if hasattr(c, "model_dump") else c
            nodes.append({"id": c_dict.get("id"), "label": c_dict.get("text"), "warrant": c_dict.get("epistemic_warrant")})
        
        graph_data = {"nodes": nodes, "edges": edges, "metadata": result.peer_review}
        json.dump(graph_data, f, indent=2)

    # 3. Dynamic Artifacts (Jupyter Notebooks for Kaggle/Code)
    for art in result.artifacts:
        if art.kind in ["python", "notebook", "kaggle"]:
            nb_path = out / (art.path_hint or "baseline.ipynb")
            if not str(nb_path).endswith(".ipynb"):
                nb_path = nb_path.with_suffix(".ipynb")
            _export_jupyter_notebook(art, nb_path)
            
    logger.success(f"💾 Export Complete. Files ready in {out.resolve()}")
