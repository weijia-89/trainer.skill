#!/usr/bin/env python3
"""Every checklist must be routed from checklists/INDEX.md, and every checklist
that declares a version must declare a valid one.

Without this, a checklist can lose its INDEX route (or ship with a broken
version string) and the rest of the suite still passes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def problems(checklists: Path) -> list[str]:
    index = (checklists / "INDEX.md").read_text()
    bad: list[str] = []
    for md in sorted(checklists.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        if md.name not in index:
            bad.append(f"{md.name}: not routed from INDEX.md")
        name = frontmatter(md.read_text()).get("name")
        if name is not None and name != md.stem:
            bad.append(f"{md.name}: name {name!r} does not match filename")
        version = frontmatter(md.read_text()).get("version")
        if version is not None and not SEMVER.match(version):
            bad.append(f"{md.name}: version {version!r} is not MAJOR.MINOR.PATCH")
    return bad


def shape_problems(text: str) -> list[str]:
    """code_shape.md: every item's confidence stays under its tier cap (70/60/45),
    and the opinion-only items 3 to 7 never claim P1 or merge-blocking."""
    bad: list[str] = []
    caps = {1: 70, 2: 60}
    for m in re.finditer(r"^(\d+)\. .*?confidence (\d+)", text, re.M):
        item, conf = int(m.group(1)), int(m.group(2))
        if conf > caps.get(item, 45):
            bad.append(f"code_shape item {item}: confidence {conf} exceeds cap {caps.get(item, 45)}")
    for m in re.finditer(r"^(\d+)\. (.*?)(?=^\d+\. |^## |\Z)", text, re.M | re.S):
        if int(m.group(1)) >= 3 and re.search(r"Severity: P[01]\b|merge.blocking", m.group(2)):
            bad.append(f"code_shape item {m.group(1)}: opinion item must not be P0/P1 or merge-blocking")
    return bad


def self_check() -> list[str]:
    """The linter must catch the faults it exists for."""
    bad: list[str] = []
    if not shape_problems("1. **x** (confidence 99).\n"):
        bad.append("self-check: confidence over cap not caught")
    if not shape_problems("5. **x** (confidence 45).\n   - Severity: P1\n"):
        bad.append("self-check: P1 on opinion item not caught")
    if shape_problems("5. **x** (confidence 45).\n   - Severity: P2\n"):
        bad.append("self-check: clean item flagged")
    return bad


def main() -> int:
    checklists = Path(__file__).resolve().parent.parent / "checklists"
    bad = problems(checklists) + shape_problems((checklists / "code_shape.md").read_text()) + self_check()
    for line in bad:
        print(f"FAIL: {line}", file=sys.stderr)
    if not bad:
        print("test_checklist_index.py: PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
