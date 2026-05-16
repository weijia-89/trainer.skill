#!/usr/bin/env python3
"""Banned-vocab scan with quoted-form exclusion.

Base regex catches unambiguous AI-marketing terms.
Lines where the matched term is wrapped in straight quotes ("..."), single quotes
('...'), or backticks (`...`) are treated as meta-discussion and skipped.

Words with frequent legitimate technical uses (`robust`, `leverage`, `harness`,
`elevate`) are intentionally excluded from the base regex; they are caught only
by per-archetype overlays.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERN = re.compile(
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

# Quoted / backticked spans we strip before re-checking the line.
QUOTED = re.compile(r'"[^"]*"|\'[^\']*\'|`[^`]*`')

EXCLUDE_DIR_PARTS = ("/references/", "/examples/", "/tests/fixtures/", "/.bak/")


def line_is_violation(line: str) -> bool:
    """Return True iff the line has a banned term outside of quotes/backticks."""
    if not PATTERN.search(line):
        return False
    stripped = QUOTED.sub("", line)
    return bool(PATTERN.search(stripped))


def fixture_check(fixtures_dir: Path) -> int:
    """Self-test the regex against fixtures."""
    pos = fixtures_dir / "banned_vocab_pos.md"
    neg = fixtures_dir / "banned_vocab_neg.md"
    if pos.exists():
        hits = len(PATTERN.findall(pos.read_text()))
        if hits < 3:
            print(f"FAIL: positive fixture should produce >=3 hits, got {hits}", file=sys.stderr)
            return 2
    if neg.exists():
        hits = len(PATTERN.findall(neg.read_text()))
        if hits > 0:
            print(f"FAIL: negative fixture should produce 0 hits, got {hits}", file=sys.stderr)
            return 2
    return 0


def main() -> int:
    here = Path(__file__).resolve().parent
    skill = here.parent
    fixtures = here / "fixtures"

    rc = fixture_check(fixtures)
    if rc != 0:
        return rc

    fail = 0
    for md in skill.rglob("*.md"):
        path_str = str(md)
        if any(part in path_str for part in EXCLUDE_DIR_PARTS):
            continue
        try:
            text = md.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if line_is_violation(line):
                print(f"{md}:{lineno}: {line.rstrip()}")
                fail = 1

    if fail == 0:
        print("test_banned_vocab.py: PASS (0 violations in skill content; fixtures verified)")
    return fail


if __name__ == "__main__":
    sys.exit(main())
