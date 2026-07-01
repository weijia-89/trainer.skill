#!/usr/bin/env python3
"""trainer_pr_body_validate.py — PR body Test plan gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.trainer_codereview_contract import validate_pr_test_plan_body  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate PR body Test plan section")
    ap.add_argument("--body-file", type=Path)
    ap.add_argument(
        "--no-require-checked",
        action="store_true",
        help="Only require sections exist, not [x] checks",
    )
    args = ap.parse_args()

    if args.body_file:
        body = args.body_file.read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()

    errors = validate_pr_test_plan_body(
        body,
        require_checked=not args.no_require_checked,
    )
    if errors:
        print(f"# trainer_pr_body_validate: FAIL ({len(errors)})", file=sys.stderr)
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("# trainer_pr_body_validate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
