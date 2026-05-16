#!/usr/bin/env python3
"""Verify rubric component weights sum to 100; no component <=0; max <=50.

Acceptance:
  exit 0 — rubric arithmetic OK
  exit 1 — sums don't add up
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_weights(path: Path) -> list[int]:
    """Extract integer weights from a markdown table column labeled 'Weight'."""
    in_table = False
    header_cols: list[str] = []
    weight_idx = -1
    weights: list[int] = []
    for line in path.read_text().splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                # First header row of a candidate weights table
                if "Weight" in cells:
                    header_cols = cells
                    weight_idx = cells.index("Weight")
                    in_table = True
                    continue
            else:
                # Skip separator row
                if all(set(c) <= set("- ") for c in cells):
                    continue
                if weight_idx < len(cells):
                    cell = cells[weight_idx]
                    m = re.match(r"^(\d+)$", cell)
                    if m:
                        weights.append(int(m.group(1)))
        elif in_table and not line.startswith("|"):
            # Out of table on first non-pipe line; stop on this table
            in_table = False
            header_cols = []
            weight_idx = -1
    return weights


def check(path: Path) -> int:
    weights = parse_weights(path)
    if not weights:
        print(f"FAIL: no weights table found in {path}", file=sys.stderr)
        return 1
    fail = 0
    if any(w <= 0 for w in weights):
        print(f"FAIL: non-positive weight in {path}: {weights}", file=sys.stderr)
        fail = 1
    if any(w > 50 for w in weights):
        print(f"FAIL: weight > 50 in {path}: {weights}", file=sys.stderr)
        fail = 1
    s = sum(weights)
    if s != 100:
        print(f"FAIL: weights in {path} sum to {s}, expected 100. Weights: {weights}", file=sys.stderr)
        fail = 1
    if fail == 0:
        print(f"test_rubric_arithmetic.py: PASS ({path}, weights={weights}, sum=100)")
    return fail


def main() -> int:
    here = Path(__file__).resolve().parent
    skill = here.parent
    rubric_files = [
        skill / "rubrics" / "confidence_score.md",
    ]
    fail = 0
    for f in rubric_files:
        if f.exists():
            fail |= check(f)
        else:
            print(f"FAIL: missing rubric file: {f}", file=sys.stderr)
            fail = 1
    return fail


if __name__ == "__main__":
    sys.exit(main())
