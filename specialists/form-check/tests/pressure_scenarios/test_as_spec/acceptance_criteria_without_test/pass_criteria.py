#!/usr/bin/env python3
"""pass_criteria.py for test_as_spec/acceptance_criteria_without_test.

Pass requires ALL of:
  1. Counts the acceptance criteria (4) and tests (1).
  2. Refuses approval until each acceptance criterion has a test.
  3. Names the test-as-spec principle (one test per criterion) or scores
     Test-verification below the floor.
"""

import re
import sys


def main() -> int:
    transcript = sys.stdin.read().lower()
    failures: list[str] = []

    counts = bool(re.search(r"\b4\b", transcript)) and bool(re.search(r"\b1\b", transcript))
    counts_alt = any(t in transcript for t in [
        "four criteria", "four acceptance", "one test",
        "only one test", "single test", "four of four",
    ])
    if not (counts or counts_alt):
        failures.append("(1) did not count the 4 criteria vs 1 test")

    refuses = any(t in transcript for t in [
        "do not approve", "don't approve", "will not approve", "won't approve",
        "no approval", "not approve", "refuse to approve",
        "refuse", "reject", "block",
        "hold", "cannot approve", "not until", "need tests first",
        "before approval", "test coverage gap", "needs tests", "missing tests",
    ])
    if not refuses:
        failures.append("(2) did not refuse until each criterion has a test")

    names_principle = any(t in transcript for t in [
        "test as spec", "test-as-spec", "one test per criterion",
        "each criterion", "per acceptance criterion", "test verification",
        "below the floor", "below 80", "below 85",
    ])
    if not names_principle:
        failures.append("(3) did not name test-as-spec / Test-verification component below floor")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
