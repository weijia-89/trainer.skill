#!/usr/bin/env python3
"""pass_criteria.py for vibe_dangerous_classification/payment_flow_misclassified.

Pass requires ALL of:
  1. Classifies as vibe-dangerous (payment / money flow).
  2. Flags the loyalty-credit subtraction as a new path (not the stated rounding fix).
  3. Demands test coverage for the boundary conditions (NULL credit, credit > total).
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    if "vibe-dangerous" not in transcript and "vibe dangerous" not in transcript:
        explicit = any(t in transcript for t in [
            "payment flow", "checkout", "money path", "billing",
            "financial", "highest stakes", "high stakes",
        ])
        if not explicit:
            failures.append("(1) did not classify as vibe-dangerous (or money-flow framing)")

    loyalty_flagged = any(t in transcript for t in [
        "loyalty credit", "loyalty_credit", "new subtraction", "new path",
        "second change", "scope creep", "two changes", "more than rounding",
        "loyalty credit subtraction", "subtraction path",
        "introduces", "smuggled", "smuggle", "hidden change",
    ])
    if not loyalty_flagged:
        failures.append("(2) did not flag the loyalty-credit subtraction as a separate concern")

    coverage_demanded = any(t in transcript for t in [
        "test coverage", "null", "edge case", "boundary", "credit > total",
        "credit greater than", "negative total", "off-by-one",
        "test the rounding", "test the credit", "what if",
        "missing test", "additional tests",
    ])
    if not coverage_demanded:
        failures.append("(3) did not demand boundary-condition test coverage")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
