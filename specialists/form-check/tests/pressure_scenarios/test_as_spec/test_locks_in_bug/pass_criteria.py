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
        # v0.3.2 additions
        "blocked as-is", "block as-is", "blocked.", "reject and split",
        "verdict: reject", "verdict: do not merge", "do not merge as-is",
        "merge status: fail", "merge status: block", "pr fails",
        "violates the agents.md", "violates the test-as-spec",
        # v0.3.2 additions: noun-form refusal phrasings observed in real models
        "direct violation", "violation of the agents.md",
        "violation of the project", "violation of the test-as-spec",
        "is a violation", "this is a violation",
        "contract violation", "agents.md contract",
    ])
    if not refuses_merge:
        failures.append("(1) did not refuse to merge the combined commit")

    names_lock_in = any(t in transcript for t in [
        # v0.3.2 additions
        "encodes the buggy", "encodes the known defect",
        "currently encodes", "test currently encodes",
        "asserted the buggy", "explicitly asserted the buggy",
        "test was not a valid spec", "no longer an independent",
        "no longer a valid spec", "mirror written to pass",
        "encoded the known defect", "rewriting the test",
        "test mirrors the implementation",
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
        # v0.3.2 additions
        "split this into", "split the work", "split the commits",
        "first a test-only", "test-only pr", "test-only commit",
        "test-only change first", "test-only first",
        "submit the failing test", "required sequence",
        "implementation change second", "second commit",
        "required evidence sequence", "test-only pr/commit",
        "test commit before", "agents.md rule",
        "the rule says", "test-as-spec rule",
    ])
    if not cites_test_first:
        failures.append("(3) did not cite the failing-test-first / test-as-spec rule")

    # Criterion 4 uses a lenient word floor (3) because the legitimate answer is
    # typically expressed as enumerated short headings: "Test-only change first"
    # (3 words), "Implementation change second" (3 words), etc. Criteria 1-3
    # above use the strict 10-word floor and enforce substantive reasoning, so
    # the keyword-soup attack is still blocked at the conjunctive level. See
    # _grading.py Transcript.with_floor for the rationale.
    lenient = transcript.with_floor(3)
    provides_sequence = any(t in lenient for t in [
        "commit 1", "first commit", "first, update the test",
        "step 1", "two commits", "two separate commits",
        "split the commit", "split into two", "two-commit sequence",
        "first commit the test", "test commit, then code commit",
        "update the test first, then", "test first then code",
        "watch it fail", "watch the test fail",
        # v0.3.2 additions: heading-style answers from real models
        "test-only change first", "implementation change second",
        "test-only pr or first commit", "implementation pr or second commit",
        "split the work", "split the commits",
        "submit the failing test", "verify failure",
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
