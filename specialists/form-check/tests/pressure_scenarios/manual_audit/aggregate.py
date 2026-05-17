#!/usr/bin/env python3
"""Aggregate manual-audit results into a model x condition pass-rate table.

Reads runs/results.jsonl (one verdict record per line, as emitted by
manual_audit.sh) and prints a 4-row qualitative summary.

Usage:
    python3 aggregate.py                # reads runs/results.jsonl
    python3 aggregate.py path/to.jsonl  # reads an explicit path

The table is intentionally qualitative: n=3 per cell across the v0.3.1
scenario set. Do not compute confidence intervals from it.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys


def main(argv: list[str]) -> int:
    default_path = pathlib.Path(__file__).resolve().parent / "runs" / "results.jsonl"
    path = pathlib.Path(argv[1]) if len(argv) > 1 else default_path
    if not path.exists():
        print(f"no results file at {path}", file=sys.stderr)
        return 1

    by_model_condition: collections.Counter[tuple[str, str]] = collections.Counter()
    totals: collections.Counter[tuple[str, str]] = collections.Counter()

    for raw in path.read_text().splitlines():
        if not raw.strip():
            continue
        r = json.loads(raw)
        key = (r["model"], r["condition"])
        totals[key] += 1
        if r["verdict"] == "PASS":
            by_model_condition[key] += 1

    if not totals:
        print(f"no records in {path}", file=sys.stderr)
        return 1

    for key in sorted(totals):
        print(f"{key[0]:20s} {key[1]:10s} {by_model_condition[key]}/{totals[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
