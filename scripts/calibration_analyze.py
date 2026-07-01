#!/usr/bin/env python3
"""calibration_analyze.py: Phase 11 Layer B (honest-empty at trainer N).

Reads .recovery/calibration.jsonl and reports counts. N-honesty contract:
  N<10     -> (uncalibrated, N=<n>), refuse threshold conclusions.
  10<=N<50 -> advisory labels only.
  N>=50    -> calibrated proposals permitted.

Explicitly NO sequential / anytime-valid / mSPRT logic: trainer Layer B is
N<10 non-IID transcript pass/fail, outside that method's stated regime.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(log_path: Path) -> list[dict]:
    if not log_path.is_file():
        return []
    rows = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def analyze(rows: list[dict]) -> dict:
    n = len(rows)
    if n < 10:
        tier, note = "uncalibrated", "refuse threshold conclusions"
    elif n < 50:
        tier, note = "advisory", "advisory labels only"
    else:
        tier, note = "calibrated", "calibrated proposals permitted"
    return {"n_events": n, "tier": tier, "note": note}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--log",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".recovery" / "calibration.jsonl",
    )
    ap.add_argument("--format", choices=["plain", "json"], default="plain")
    args = ap.parse_args()
    res = analyze(load(args.log))
    if args.format == "json":
        print(json.dumps(res))
    else:
        print(f"Layer B calibration: ({res['tier']}, N={res['n_events']}) - {res['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
