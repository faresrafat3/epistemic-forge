#!/usr/bin/env python3
"""Generate 3 full worked examples (philosophy, kaggle, freelance)."""

from __future__ import annotations

from pathlib import Path

from epistemic_forge.io.export import export_result
from epistemic_forge.pipeline.arsenal_run import run_pipeline

EXAMPLES = [
    {
        "slug": "01_philosophy_predictive_responsibility",
        "title": "Predictive processing and moral responsibility",
        "question": (
            "If the brain is a prediction machine, what happens to moral responsibility?"
        ),
        "domain": "philosophy",
        "keywords": ["predictive processing", "responsibility", "agency", "blame"],
        "audience": "philosophy seminar + curious technologists",
    },
    {
        "slug": "02_kaggle_imbalanced_baseline",
        "title": "Honest baseline for imbalanced tabular Kaggle",
        "question": (
            "What is an honest baseline plan for a noisy imbalanced Kaggle table "
            "where leakage is a real risk?"
        ),
        "domain": "kaggle",
        "keywords": ["imbalance", "baseline", "cv", "leakage", "metric"],
        "audience": "competition teammate / hiring manager reading a notebook",
    },
    {
        "slug": "03_freelance_climate_sprint",
        "title": "2-week climate-tech research sprint",
        "question": (
            "How do I scope a 2-week research sprint for a climate-tech founder "
            "who needs decision-ready clarity, not an academic tome?"
        ),
        "domain": "freelance",
        "keywords": ["sprint", "scope", "founder", "deliverable", "acceptance"],
        "audience": "startup founder (non-technical board pressure)",
    },
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_root = root / "examples" / "worked"
    out_root.mkdir(parents=True, exist_ok=True)
    index_lines = [
        "# Worked examples",
        "",
        "Full pipeline outputs for three domains. Each folder contains the same "
        "artifact set a user gets from the CLI (`executive_summary.md`, "
        "`research_memo.md`, domain packs, `result.json`).",
        "",
    ]
    for ex in EXAMPLES:
        slug = ex["slug"]
        result = run_pipeline(
            title=ex["title"],
            question=ex["question"],
            domain=ex["domain"],
            audience=ex["audience"],
            keywords=ex["keywords"],
            max_trials=2,
        )
        dest = out_root / slug
        export_result(result, dest)
        # Human-friendly wrap
        readme = dest / "README.md"
        readme.write_text(
            f"# {ex['title']}\n\n"
            f"**Domain:** `{ex['domain']}`\n\n"
            f"**Question:** {ex['question']}\n\n"
            f"**Score:** {result.final_score:.3f}  \n"
            f"**Review:** {result.peer_review.get('verdict')}  \n"
            f"**L1 mode:** {result.route.l1_mode} · **L3 mode:** {result.route.l3_mode}\n\n"
            f"**Instruction used:** {result.instruction}\n\n"
            f"## Files\n\n"
            + "\n".join(f"- `{p.name}`" for p in sorted(dest.iterdir()) if p.name != "README.md")
            + "\n\n## Start here\n\nRead `executive_summary.md`, then `research_memo.md`.\n",
            encoding="utf-8",
        )
        index_lines.append(
            f"- [{ex['title']}](./{slug}/) — `{ex['domain']}` · "
            f"score={result.final_score:.3f} · {result.peer_review.get('verdict')}"
        )
        print(f"wrote {dest} score={result.final_score:.3f}")

    (out_root / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"index → {out_root / 'README.md'}")


if __name__ == "__main__":
    main()
