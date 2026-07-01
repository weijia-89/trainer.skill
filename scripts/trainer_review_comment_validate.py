#!/usr/bin/env python3
"""trainer_review_comment_validate.py — full PR review comment gate (local/CI)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.trainer_codereview_contract import validate_review_comment  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate trainer PR review comment body")
    ap.add_argument("--repo", required=True, help="Repo slug (e.g. trainer.skill)")
    ap.add_argument("--body-file", type=Path, required=True)
    args = ap.parse_args()

    body = args.body_file.read_text(encoding="utf-8")
    errors = validate_review_comment(body, args.repo.strip().lower())
    if errors:
        print(f"# trainer_review_comment_validate: FAIL ({len(errors)})", file=sys.stderr)
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("# trainer_review_comment_validate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
