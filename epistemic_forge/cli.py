"""CLI for Epistemic Forge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from epistemic_forge.io.export import export_result
from epistemic_forge.pipeline.arsenal_run import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epistemic-forge",
        description="ARSENAL-powered epistemic research & writing forge",
    )
    p.add_argument("--title", required=True, help="Project title")
    p.add_argument("--question", required=True, help="Core research/client question")
    p.add_argument(
        "--domain",
        default="hybrid",
        choices=["research", "philosophy", "writing", "freelance", "kaggle", "hybrid"],
    )
    p.add_argument("--audience", default="technical peer / client")
    p.add_argument("--keywords", default="", help="Comma-separated keywords")
    p.add_argument("--constraints", default="", help="Comma-separated constraints")
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--out", default="forge_output", help="Output directory")
    p.add_argument("--json-stdout", action="store_true", help="Print full JSON result")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    constraints = [c.strip() for c in args.constraints.split(",") if c.strip()]
    result = run_pipeline(
        title=args.title,
        question=args.question,
        domain=args.domain,
        audience=args.audience,
        keywords=keywords,
        constraints=constraints,
        max_trials=args.trials,
    )
    out = export_result(result, args.out)
    print(f"Epistemic Forge complete → {out.resolve()}")
    print(f"Score={result.final_score:.3f} review={result.peer_review.get('verdict')}")
    print(f"Route L1={result.route.l1_mode} L3={result.route.l3_mode}")
    print(f"Families: {', '.join(result.route.families)}")
    if args.json_stdout:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False)[:5000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
