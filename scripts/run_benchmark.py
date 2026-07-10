#!/usr/bin/env python3
"""Run claim-lattice vs baseline benchmark and write reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from epistemic_forge.benchmark.suite import write_benchmark_reports


def main() -> int:
    p = argparse.ArgumentParser(description="Epistemic Forge benchmark")
    p.add_argument("--out", default="benchmark_out", help="Output directory")
    args = p.parse_args()
    report = write_benchmark_reports(args.out)
    s = report["summary"]
    print(json.dumps(s, indent=2))
    print(f"\nWrote {Path(args.out) / 'BENCHMARK.md'}")
    print(f"Wrote {Path(args.out) / 'benchmark_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
