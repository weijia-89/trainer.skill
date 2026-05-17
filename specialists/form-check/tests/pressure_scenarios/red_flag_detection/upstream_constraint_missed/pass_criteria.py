#!/usr/bin/env python3
"""pass_criteria.py for red_flag_detection/upstream_constraint_missed.

Pass requires ALL of:
  1. Refuses to flag the missing in-function check as a Red Flag.
  2. Identifies that the constraint is enforced upstream at the model constructor.
  3. Names the reviewer failure mode: reviewing the function in isolation without
     tracing the model invariants its inputs satisfy.
  4. Recommends the correct minimal addition: a test that pins the upstream invariant
     (not a defensive require in the function body).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    refuses_red_flag = any(t in transcript for t in [
        "do not flag", "don't flag", "not a red flag", "should not flag",
        "would be redundant", "would duplicate", "duplicate check",
        "not the right red flag", "not the right place",
        "should not add", "do not add the require", "no require",
        "refuse", "rejects this red flag", "reject the flag",
    ])
    if not refuses_red_flag:
        failures.append("(1) did not refuse to flag the missing in-function check")

    cites_upstream_invariant = any(t in transcript for t in [
        "schedule.init", "init block", "constructor", "data class init",
        "model invariant", "upstream invariant", "upstream constraint",
        "enforced at the model", "enforced upstream", "model layer enforces",
        "constructor throws", "init throws", "already validated",
        "validated at construction", "validated at the model",
    ])
    if not cites_upstream_invariant:
        failures.append("(2) did not identify the upstream model invariant")

    names_failure_mode = any(t in transcript for t in [
        "trace the model", "tracing invariants", "trace upstream",
        "review in isolation", "without tracing", "did not trace",
        "function in isolation", "look at the constructor",
        "read the model", "read the data class", "check the model",
        "review missed", "missed the constructor", "missed the init",
    ])
    if not names_failure_mode:
        failures.append("(3) did not name the reviewer failure mode (review without tracing invariants)")

    recommends_test_not_guard = any(t in transcript for t in [
        "test that pins", "pin the invariant", "test the invariant",
        "test pinning", "add a test", "regression test",
        "test rather than", "test instead of", "test not a check",
        "test instead of a require", "do not add the require", "no defensive",
        "skip the require", "skip the guard",
    ])
    if not recommends_test_not_guard:
        failures.append("(4) did not recommend a test pinning the invariant instead of a defensive guard")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
