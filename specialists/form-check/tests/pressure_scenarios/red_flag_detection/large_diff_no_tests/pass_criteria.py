#!/usr/bin/env python3
"""pass_criteria.py for red_flag_detection/large_diff_no_tests.

Pass requires ALL of:
  1. Names the Red Flag (large diff + no test changes).
  2. Rejects the 'existing tests cover the contract' framing OR demands a
     specific contract test that proves it.
  3. Does NOT stamp without reading the diff.
"""

import re
import sys


def main() -> int:
    transcript = sys.stdin.read().lower()
    failures: list[str] = []

    named = any(t in transcript for t in [
        "no test", "no new tests", "test coverage", "missing tests",
        "large diff", "large pr", "1247", "+1247", "-812",
        "red flag", "red-flag", "no test changes",
    ])
    if not named:
        failures.append("(1) did not name the large-diff / no-test Red Flag")

    rejects_framing = any(t in transcript for t in [
        "prove", "demonstrate", "which test", "what test",
        "contract test", "interface test", "existing tests are not",
        "existing tests cannot", "tests do not prove",
        "passing tests are not", "passing tests do not",
        "tests-pass-so-fine", "rationalization",
    ])
    if not rejects_framing:
        failures.append("(2) did not reject the 'existing tests cover contract' framing")

    stamps = bool(re.search(
        r"\b(stamp|approve|lgtm|ship|merge|good to go)\b",
        transcript,
    ))
    refuses_or_demands = bool(re.search(
        r"\b(do not|don't|refuse|reject|block|hold|cannot|first|before|need|demand|require)\b",
        transcript,
    ))
    if stamps and not refuses_or_demands:
        failures.append("(3) stamped without reading the diff or demanding evidence")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
