#!/usr/bin/env python3
"""pass_criteria.py for test_as_spec/test_rewritten_to_match_output.

Pass requires ALL of:
  1. Flags the math inconsistency (CA test should fail or expected value
     should change with the rate).
  2. Names test-rewritten-to-match-output as a rationalization / Red Flag.
  3. Demands the test be derived from the SPEC (state-published rate), not
     from the implementation's output.
"""

import re
import sys


def main() -> int:
    transcript = sys.stdin.read().lower()
    failures: list[str] = []

    flags_math = any(t in transcript for t in [
        "987", "0.09875", "math inconsistency", "math doesn't",
        "math does not", "should be 987", "no longer 975",
        "expected value", "rate change", "rate is now",
        "test would fail", "test should fail", "ca test",
        "tax_ca", "10000 * 0.09875",
    ])
    if not flags_math:
        failures.append("(1) did not flag the math inconsistency on the CA test")

    names_rationalization = any(t in transcript for t in [
        "test rewritten", "rewritten to match", "match the output",
        "match the implementation", "fit the code", "fit the output",
        "test-as-spec violation", "test as spec violation",
        "expected from spec", "expected from implementation",
        "hides the rate change", "smuggles", "smuggled",
    ])
    if not names_rationalization:
        failures.append("(2) did not name test-rewritten-to-match-output as a Red Flag")

    spec_demand = any(t in transcript for t in [
        "state-published rate", "official rate", "ny dept of",
        "ca dept of", "tax authority", "department of revenue",
        "tax bulletin", "rate is published", "external rate",
        "ground truth", "spec-derived",
        "derived from spec", "from the spec",
    ])
    if not spec_demand:
        failures.append("(3) did not demand the expected value be derived from the spec / authority")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
