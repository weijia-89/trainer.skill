#!/usr/bin/env python3
"""Permanent cross-file reference checker for form-check.skill and recovery.skill.

Promoted from a wave-9 session artifact (`code-skills-overhaul/wave9-…/ref_check.py`)
to a permanent test in v2.1.1 — fixes the maintainability gap where the ref-check
lived outside the skill and could go stale.

Scans every backticked .md/.py/.sh/.json/.yaml reference in form-check.skill and
recovery.skill markdown, verifies the target exists. Resolution order:

  1. relative to the citing file
  2. relative to each skill root
  3. relative to the skills' parent directory (cross-skill refs)

Skips:
  - references/, examples/, tests/fixtures/, .bak/, __pycache__/
  - paths under templates/, README_archetypes/, runbooks/, tests/integration/
    (template content is full of placeholder filenames by design)
  - generic prefixes (/etc/, /tmp/, .recovery/, src/, lib/, etc.)
  - consumer-side bare filenames (package.json, README.md, etc.)
  - numbered ADR placeholders (e.g. 0001-use-sqlite.md)

Exit codes: 0 PASS, 1 broken refs found, 2 unexpected error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ---- Paths ----
HERE = Path(__file__).resolve().parent
CODE_HELPER = HERE.parent
CODEIT = CODE_HELPER.parent / "recovery.skill"
SKILLS_PARENT = CODE_HELPER.parent
SKILLS = [CODE_HELPER]
if CODEIT.exists():
    SKILLS.append(CODEIT)

# ---- Regex ----
REF_RE = re.compile(r"`([a-zA-Z0-9_./-]+\.(?:md|py|sh|json|yaml|yml))`")

# ---- Skip rules ----
EXCLUDE_DIR_PARTS = (
    "/references/",
    "/tests/fixtures/",
    "/.bak/",
    "/__pycache__/",
)

# Folders where every ref is a *template placeholder* (consumer creates it).
TEMPLATE_DIR_PARTS = (
    "/templates/",
    "/examples/",
    "/tests/integration/",
    "/README_archetypes/",
    "/runbooks/",
)

SKIP_PREFIX = (
    "/docs/adr/", "docs/adr/",
    "/etc/", "/var/", "/tmp/",
    ".recovery/",         # runtime state, consumer-side
    ".github/",         # CI configs, consumer-side
    "config/",          # consumer config
    "docs/",            # consumer docs (skill content uses full skill-relative paths)
    "src/", "lib/", "app/", "tests/", "test/",  # consumer code
    "../", "./",        # relative refs to consumer paths
)

# Bare filenames the consumer creates (not skill files).
SKIP_EXACT = {
    # Common ecosystem manifests
    "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "requirements.txt",
    "tsconfig.json", "application.yml", "pnpm-lock.yaml",
    "package-lock.json", "poetry.lock", "Cargo.lock",
    # Generic CI / config
    "fitness.yml", "ci.yml", "release.yml", "eval_baseline.json",
    # Project-level docs the consumer maintains
    "AGENTS.md", "CLAUDE.md", "SECURITY.md", "README.md", "CHANGELOG.md",
    "ARCHITECTURE.md", "ROADMAP.md", "CODEOWNERS",
    "conftest.py", "__init__.py", "/CLAUDE.md", "/AGENTS.md",
    # Consumer-side example filenames in learner prose
    ".form-check.yaml", "my_cli.py", "learnings.md",
    # Common entry-point filenames cited as examples in checklists/codebase_scan.md
    "app.py", "index.js", "main.go", "server.ts",
    # Scan-output artifact filename cited in checklists/codebase_scan.md
    "codebase_scan_notes.md",
}

# Numbered ADR files (e.g. 0001-use-sqlite.md) are always placeholders.
ADR_RE = re.compile(r"^\d{4}-[a-z0-9-]+\.md$")


def should_skip(ref: str, citing: Path) -> bool:
    cit = str(citing)
    if any(part in cit for part in TEMPLATE_DIR_PARTS):
        return True
    if ref in SKIP_EXACT:
        return True
    if any(ref.startswith(p) for p in SKIP_PREFIX):
        return True
    base = ref.split("/")[-1]
    if ADR_RE.match(base):
        return True
    return False


def normalize_ref(ref: str) -> str:
    """The skill tree is deployed as `form-check` / `recovery` (no `.skill`
    suffix), but historical docs reference `form-check.skill` / `recovery.skill`.
    Strip a trailing `.skill` from the first path component so the checker
    resolves against the real on-disk layout instead of failing on naming drift.
    """
    head, sep, tail = ref.partition("/")
    if head.endswith(".skill"):
        head = head[: -len(".skill")]
    return head + sep + tail


def resolve(ref: str, citing: Path) -> bool:
    """Return True if any candidate path exists."""
    ref = normalize_ref(ref)
    candidates = [(citing.parent / ref).resolve()]
    for root in SKILLS:
        candidates.append((root / ref).resolve())
    candidates.append((SKILLS_PARENT / ref).resolve())
    return any(c.exists() for c in candidates)


def scan(root: Path) -> list[tuple[Path, int, str]]:
    missing: list[tuple[Path, int, str]] = []
    for md in root.rglob("*.md"):
        path_str = str(md)
        if any(part in path_str for part in EXCLUDE_DIR_PARTS):
            continue
        # CHANGELOG.md is a historical record. Path references in past entries
        # describe what existed AT THE TIME. After renames (e.g. the 2026-05-15
        # gym-metaphor migration), historical paths may no longer resolve. That
        # is expected; do not rewrite history to keep the test passing.
        if md.name == "CHANGELOG.md":
            continue
        try:
            text = md.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in REF_RE.finditer(line):
                ref = m.group(1)
                if should_skip(ref, md):
                    continue
                if not resolve(ref, md):
                    missing.append((md, lineno, ref))
    return missing


def main() -> int:
    all_missing: list[tuple[Path, int, str]] = []
    for root in SKILLS:
        all_missing.extend(scan(root))

    if not all_missing:
        print(f"test_cross_refs.py: PASS (0 broken refs across {len(SKILLS)} skill(s))")
        return 0

    by_file: dict[Path, list[tuple[int, str]]] = {}
    for f, ln, ref in all_missing:
        by_file.setdefault(f, []).append((ln, ref))

    print(
        f"test_cross_refs.py: FAIL ({len(all_missing)} broken refs in {len(by_file)} file(s))",
        file=sys.stderr,
    )
    for f in sorted(by_file):
        for ln, ref in by_file[f]:
            print(f"  {f}:{ln}: {ref}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"test_cross_refs.py: ERROR ({exc})", file=sys.stderr)
        sys.exit(2)
