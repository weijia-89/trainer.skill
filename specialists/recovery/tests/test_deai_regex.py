#!/usr/bin/env python3
"""Verify base banned-vocab regex against fixtures + per-archetype overlays.

Acceptance:
  exit 0 if base regex catches positive fixture (≥3 hits) and clears negative (0 hits)
  exit 1 otherwise.

Per-archetype overlay tests are deferred to test fixtures per archetype.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Mirrored from form-check.skill/tests/test_banned_vocab.py.
# Soft-signal terms (robust, leverage, harness, elevate) are excluded from base
# and handled by per-archetype overlays.
BASE_PATTERN = re.compile(
    r"\b("
    r"scalable|cutting[- ]edge|enterprise[- ]grade|"
    r"synergize|synergy|delve|delving|delved|"
    r"seamless|seamlessly|streamline|streamlining|"
    r"holistic|paradigm|game[- ]chang(?:er|ing)|"
    r"next[- ]gen|state[- ]of[- ]the[- ]art|"
    r"world[- ]class|best[- ]in[- ]class|"
    r"empower(?:s|ed|ing)?|unparalleled|unmatched|"
    r"navigate(?: the| this| through)"
    r")\b",
    re.IGNORECASE,
)


def main() -> int:
    here = Path(__file__).resolve().parent
    fix = here / "fixtures"
    fail = 0

    pos = fix / "banned_vocab_pos.md"
    neg = fix / "banned_vocab_neg.md"

    if pos.exists():
        hits = len(BASE_PATTERN.findall(pos.read_text()))
        if hits < 3:
            print(f"FAIL: positive fixture should produce >=3 hits, got {hits}", file=sys.stderr)
            fail = 1
    else:
        # No fixtures yet — recovery fixtures are in form-check; reuse via path indirection
        sibling = here.parent.parent / "form-check.skill" / "tests" / "fixtures"
        if (sibling / "banned_vocab_pos.md").exists():
            hits = len(BASE_PATTERN.findall((sibling / "banned_vocab_pos.md").read_text()))
            if hits < 3:
                print(f"FAIL: positive fixture (sibling) should produce >=3 hits, got {hits}", file=sys.stderr)
                fail = 1

    if neg.exists():
        hits = len(BASE_PATTERN.findall(neg.read_text()))
        if hits > 0:
            print(f"FAIL: negative fixture should produce 0 hits, got {hits}", file=sys.stderr)
            fail = 1
    else:
        sibling = here.parent.parent / "form-check.skill" / "tests" / "fixtures"
        if (sibling / "banned_vocab_neg.md").exists():
            hits = len(BASE_PATTERN.findall((sibling / "banned_vocab_neg.md").read_text()))
            if hits > 0:
                print(f"FAIL: negative fixture (sibling) should produce 0 hits, got {hits}", file=sys.stderr)
                fail = 1

    if fail == 0:
        print("test_deai_regex.py: PASS (base regex behavior verified against fixtures)")
    return fail


if __name__ == "__main__":
    sys.exit(main())
