#!/usr/bin/env python3
"""pass_criteria.py for test_as_spec/test_locks_in_bug.

Pass requires ALL of:
  1. Refuses to merge the combined commit.
  2. Names that the existing test was pinning buggy behavior (test_locks_in_bug class).
  3. Cites the test-as-spec rule that says the failing test must commit first.
  4. Provides the correct two-commit sequence (test update first, then code).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    refuses_merge = any(t in transcript for t in [
        "do not merge", "don't merge", "should not merge", "will not merge",
        "not ok to merge", "not okay to merge", "block this", "block the merge",
        "request changes", "needs split", "must split", "split into two",
        "needs two commits", "needs separate commits", "reject the pr",
        "refuse to approve", "cannot approve",
    ])
    if not refuses_merge:
        failures.append("(1) did not refuse to merge the combined commit")

    names_lock_in = any(t in transcript for t in [
        "pinning buggy", "locks in", "locks the bug", "pins the bug",
        "pins buggy", "test was wrong", "test asserted the bug",
        "test enforces the bug", "test contradicts the kdoc",
        "test pinned the broken", "test pinned the buggy",
        "test-as-spec violation", "test pins the broken behavior",
    ])
    if not names_lock_in:
        failures.append("(2) did not name that the existing test was pinning buggy behavior")

    cites_test_first = any(t in transcript for t in [
        "failing test first", "test first", "test-first",
        "write the failing test", "commit the test", "commit it first",
        "test before implementation", "test before the implementation",
        "test commit before", "agents.md rule",
        "the rule says", "test-as-spec rule",
    ])
    if not cites_test_first:
        failures.append("(3) did not cite the failing-test-first / test-as-spec rule")

    provides_sequence = any(t in transcript for t in [
        "commit 1", "first commit", "first, update the test",
        "step 1", "two commits", "two separate commits",
        "split the commit", "split into two", "two-commit sequence",
        "first commit the test", "test commit, then code commit",
        "update the test first, then", "test first then code",
        "watch it fail", "watch the test fail",
    ])
    if not provides_sequence:
        failures.append("(4) did not provide the correct two-commit sequence")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
