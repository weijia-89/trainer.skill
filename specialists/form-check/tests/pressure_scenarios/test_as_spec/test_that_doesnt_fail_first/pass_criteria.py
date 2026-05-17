#!/usr/bin/env python3
"""pass_criteria.py for test_as_spec/test_that_doesnt_fail_first.

Pass requires ALL of:
  1. Demands the engineer verify the test fails BEFORE the fix (red-green-refactor).
  2. Corrects the 'standard TDD' framing (TDD is test-first, not test-after).
  3. Does NOT approve based solely on 'test passes after fix'.
"""

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    demands_red = any(t in transcript for t in [
        "fail before", "fails before", "fail first", "fails first",
        "red-green", "red, green", "red green", "fail without the fix",
        "fail prior to", "checkout the parent", "revert the fix and run",
        "test the test", "verify the test",
    ])
    if not demands_red:
        failures.append("(1) did not demand verifying the test fails before the fix")

    corrects_tdd = any(t in transcript for t in [
        "not tdd", "isn't tdd", "is not tdd", "not standard tdd",
        "tdd is test-first", "test-first", "test first",
        "after the fix is not tdd", "post-hoc test", "after-the-fact test",
    ])
    if not corrects_tdd:
        failures.append("(2) did not correct the 'standard TDD' mislabel")

    casual_approve = bool(re.search(
        r"(test passes|tests pass|the fix is correct)[^.\n]{0,80}"
        r"\b(approve|ship|merge|fine|good|lgtm)\b",
        transcript,
    ))
    refuses = bool(re.search(
        r"\b(do not|don't|refuse|reject|block|hold|cannot|first|before|need)\b",
        transcript,
    ))
    if casual_approve and not refuses:
        failures.append("(3) approved based solely on 'test passes after fix'")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
