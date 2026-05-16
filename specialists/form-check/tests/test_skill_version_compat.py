#!/usr/bin/env python3
"""Verify recovery.skill's composition pin against form-check.skill.

Checks performed:

1. recovery/SKILL.md declares `composes: form-check@<range>` and form-check's
   actual SKILL.md frontmatter version falls within that range.
2. Every file under recovery/SKILL.md's `pinned_components:` block:
   - exists at the expected path under form-check/
   - has frontmatter `version:` that matches the pinned `@version`

The wave-9 review found that the old version of this test only did check 1,
which let an INDEX.md frontmatter version-mismatch slip through. Check 2
exercises the actual composition contract.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_top_frontmatter(path: Path) -> tuple[dict, str]:
    """Return (flat-key dict, raw-frontmatter-text). Flat parse only — top-level keys."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}, ""
    end = text.find("\n---", 4)
    if end < 0:
        return {}, ""
    fm_text = text[4:end]
    out: dict[str, str] = {}
    for line in fm_text.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m and not line.startswith(" "):  # top-level only
            out[m.group(1)] = m.group(2).strip()
    return out, fm_text


def parse_version(s: str) -> tuple[int, int, int]:
    s = s.strip().strip('"').strip("'")
    parts = s.split(".")
    while len(parts) < 3:
        parts.append("0")
    return tuple(int(p) for p in parts[:3])  # type: ignore[return-value]


def extract_composes_block(fm_text: str) -> str:
    """Extract the `composes:` YAML block (greedy until next top-level key)."""
    lines = fm_text.splitlines()
    in_block = False
    block: list[str] = []
    for line in lines:
        if line.startswith("composes:"):
            in_block = True
            continue
        if in_block:
            if line and not line.startswith(" "):
                break  # next top-level key
            block.append(line)
    return "\n".join(block)


def extract_pinned_components(composes_block: str) -> list[tuple[str, str]]:
    """Return list of (path, version) from `pinned_components:` entries."""
    pins: list[tuple[str, str]] = []
    capture = False
    for line in composes_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("pinned_components:"):
            capture = True
            continue
        if capture:
            # entries look like:  - rubrics/confidence_score.md@2.0.0
            m = re.match(r"^\s*-\s+(\S+?)@(\S+)\s*$", line)
            if m:
                pins.append((m.group(1), m.group(2)))
            elif line and not line.startswith(" "):
                break
            elif stripped and not stripped.startswith("-"):
                # ran out of list items
                break
    return pins


def main() -> int:
    here = Path(__file__).resolve().parent
    code_inspector = here.parent
    code_fixer = code_inspector.parent / "recovery.skill"

    if not code_fixer.exists():
        print("test_skill_version_compat.py: SKIP (no sibling recovery.skill)")
        return 0

    ci_fm, _ = parse_top_frontmatter(code_inspector / "SKILL.md")
    cf_fm, cf_fm_text = parse_top_frontmatter(code_fixer / "SKILL.md")

    failures: list[str] = []

    # ---- Check 1: form-check version is in recovery's declared range -------
    ci_version = ci_fm.get("version", "")
    if not ci_version:
        failures.append("form-check.skill/SKILL.md missing top-level `version:`")
    else:
        m = re.search(r'version:\s*"?>=([0-9.]+),<([0-9.]+)"?', cf_fm_text)
        if not m:
            failures.append(
                "recovery/SKILL.md does not declare a composes version range "
                "matching `version: \">=X,<Y\"`"
            )
        else:
            ci_v = parse_version(ci_version)
            min_v = parse_version(m.group(1))
            max_v = parse_version(m.group(2))
            if not (min_v <= ci_v < max_v):
                failures.append(
                    f"form-check version {ci_version} outside recovery's "
                    f"composes range [{m.group(1)}, {m.group(2)})"
                )

    # ---- Check 2: every pinned component exists at the pinned version -----
    composes_block = extract_composes_block(cf_fm_text)
    pins = extract_pinned_components(composes_block)
    if not pins:
        failures.append(
            "recovery/SKILL.md declares no `pinned_components:` entries — "
            "the composition contract is empty"
        )

    for rel_path, pinned_version in pins:
        target = code_inspector / rel_path
        if not target.exists():
            failures.append(
                f"pinned component missing: {rel_path}@{pinned_version} "
                f"(expected at {target})"
            )
            continue
        target_fm, _ = parse_top_frontmatter(target)
        target_version = target_fm.get("version", "")
        if not target_version:
            failures.append(
                f"pinned component {rel_path} has no `version:` in its frontmatter "
                f"(recovery pins it at @{pinned_version})"
            )
            continue
        if parse_version(target_version) != parse_version(pinned_version):
            failures.append(
                f"pinned component {rel_path}: recovery expects @{pinned_version}, "
                f"file declares @{target_version}"
            )

    # ---- Report ----------------------------------------------------------
    if failures:
        print(f"test_skill_version_compat.py: FAIL ({len(failures)} issue(s))", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print(
        f"test_skill_version_compat.py: PASS "
        f"(form-check@{ci_version} in recovery's pinned range; "
        f"{len(pins)} pinned component(s) verified)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
