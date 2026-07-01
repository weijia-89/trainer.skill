#!/usr/bin/env python3
"""trainer_pr_r6_validate.py — R-6 user-facing docs coverage gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.trainer_codereview_contract import (  # noqa: E402
    classify_r6_files,
    validate_r6_user_facing_docs,
)


def _read_paths(path: Path | None) -> list[str]:
    if path is None:
        return [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate R-6 user-facing doc coverage for a PR")
    ap.add_argument("--files-file", type=Path, help="Newline-separated changed paths")
    ap.add_argument("--review-file", type=Path, help="Review comment body (assembled)")
    ap.add_argument("--verdict", choices=("APPROVE", "REQUEST_CHANGES", "BLOCK"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    files = _read_paths(args.files_file)
    review = ""
    if args.review_file:
        review = args.review_file.read_text(encoding="utf-8")

    code_paths, doc_paths = classify_r6_files(files)
    errors = validate_r6_user_facing_docs(
        files,
        review,
        verdict=args.verdict,
    )

    if errors:
        if not args.quiet:
            print(f"# trainer_pr_r6_validate: FAIL ({len(errors)})", file=sys.stderr)
            for err in errors:
                print(f"FAIL: {err}", file=sys.stderr)
        return 1

    if not args.quiet:
        print("# trainer_pr_r6_validate: PASS")
        if code_paths:
            print(f"  code paths: {len(code_paths)}; doc paths: {len(doc_paths)}")
        else:
            print("  no R-6 code paths in diff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
