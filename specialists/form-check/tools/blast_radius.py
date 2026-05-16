#!/usr/bin/env python3
"""Compute blast-radius score for a code change.

Algorithm spec: docs/blast_radius_algorithm.md
Used by: rubrics/confidence_score.md (component 8, weight 7)

Usage:
    python tools/blast_radius.py <repo-root>
    python tools/blast_radius.py <repo-root> --since=HEAD~1

Outputs JSON: {"score": 42, "components": {...}}
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

PRIVILEGE_PATTERNS = [
    (re.compile(r"(^|/)api(/|$)|(^|/)public/"), "public-api", 30),
    (re.compile(r"(^|/)(db|migrations|schema)(/|$)"), "write-effect", 30),
    (re.compile(r"(^|/)auth(/|$)|password|secret|token|crypto"), "secret-handling", 30),
    (re.compile(r"(^|/)admin(/|$)"), "write-effect", 25),
    (re.compile(r"\.css$|\.scss$|(^|/)styles?(/|$)"), "internal", 5),
    (re.compile(r"(^|/)docs?(/|$)|\.md$"), "internal", 5),
]
ENV_VAR_PATTERN = re.compile(r"(env\[|getenv|os\.environ|process\.env|System\.getenv)")


def changed_files(repo: Path, since: str) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", since],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        return []
    return [repo / f.strip() for f in out.stdout.splitlines() if f.strip()]


def privilege_for(path: Path) -> tuple[str, int]:
    rel = str(path).replace(str(path.anchor), "")
    for pattern, label, weight in PRIVILEGE_PATTERNS:
        if pattern.search(rel):
            return label, weight
    return "internal", 5


def call_paths_estimate(repo: Path, paths: list[Path]) -> int:
    """Cheap heuristic: count grep hits across repo for changed-file basenames."""
    if not paths:
        return 0
    basenames = {p.stem for p in paths if p.suffix in {".py", ".ts", ".js", ".java", ".kt", ".go", ".rs"}}
    if not basenames:
        return 0
    pattern = "|".join(re.escape(b) for b in basenames)
    out = subprocess.run(
        ["git", "-C", str(repo), "grep", "-c", "-E", pattern],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode not in (0, 1):
        return 0
    total = 0
    for line in out.stdout.splitlines():
        try:
            count = int(line.split(":")[-1])
            total += count
        except ValueError:
            continue
    return max(0, total - len(basenames))


def env_var_bonus(paths: list[Path]) -> int:
    for p in paths:
        try:
            content = p.read_text(errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        if ENV_VAR_PATTERN.search(content):
            return 20
    return 0


def compute(repo: Path, since: str) -> dict:
    paths = [p for p in changed_files(repo, since) if p.exists()]
    n_files = len(paths)
    if n_files == 0:
        return {"score": 0, "components": {"files": 0, "privilege": 0, "call_paths": 0, "env_var_bonus": 0}}
    privilege_label, privilege_weight = "internal", 5
    for p in paths:
        label, weight = privilege_for(p)
        if weight > privilege_weight:
            privilege_label, privilege_weight = label, weight
    paths_count = call_paths_estimate(repo, paths)
    secret_bonus = env_var_bonus(paths)
    files_term = math.log10(n_files + 1) * 20
    paths_term = math.log10(paths_count + 1) * 15
    raw = files_term + privilege_weight + paths_term + secret_bonus
    score = min(100, int(round(raw)))
    return {
        "score": score,
        "components": {
            "files": n_files,
            "privilege": privilege_label,
            "privilege_weight": privilege_weight,
            "call_paths": paths_count,
            "env_var_bonus": secret_bonus,
            "files_term": round(files_term, 2),
            "paths_term": round(paths_term, 2),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("repo", type=Path, help="Repository root")
    p.add_argument("--since", default="HEAD~1", help="Git rev to diff against (default: HEAD~1)")
    args = p.parse_args()
    if not args.repo.is_dir():
        print(f"error: {args.repo} is not a directory", file=sys.stderr)
        return 2
    result = compute(args.repo.resolve(), args.since)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
