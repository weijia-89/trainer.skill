#!/usr/bin/env python3
"""Validate trainer PR review comment bodies (Bug inventory + anti-theater gate)."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.trainer_codereview_contract import (  # noqa: E402
    validate_bug_inventory,
    validate_review_comment,
)


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "usage: trainer_review_bug_inventory_validate.py <repo_slug> <body_file> "
            "[--full]",
            file=sys.stderr,
        )
        return 2
    repo = sys.argv[1].strip().lower()
    body_path = sys.argv[2]
    full = "--full" in sys.argv[3:]
    try:
        body = Path(body_path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"FAIL  cannot read body: {exc}", file=sys.stderr)
        return 2

    errors = (
        validate_review_comment(body, repo)
        if full
        else validate_bug_inventory(body, repo)
    )
    if errors:
        for err in errors:
            print(f"FAIL  {err}", file=sys.stderr)
        return 1
    label = "review comment contract" if full else "bug inventory declaration"
    print(f"PASS  {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
