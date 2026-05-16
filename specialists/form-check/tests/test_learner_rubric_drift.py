#!/usr/bin/env python3
"""Drift check between learner lessons and the rubric they cite.

When the rubric (`rubrics/confidence_score.md`) changes weights or component
names, the corresponding learner lesson must stay in sync. This test catches
silent drift.

Checks per lesson in `learner/lessons/`:

  1. **Frontmatter sanity** — `rubric_component:` is set and references a
     component number that actually exists in the rubric.
  2. **Filename alignment** — the lesson filename is `<N>_<slug>.md` where
     <N> matches the frontmatter `rubric_component:`, and <slug> matches the
     rubric component name when normalized (whitespace → '_', lowercased,
     non-alphanumerics stripped). Empty slug or mismatched slug fails.
  3. **Cited weight matches rubric** — if the lesson prose contains a phrase
     like "weight N" / "weight of N" / "weighted at N" / "weights ... at N",
     that N must equal the rubric weight for the lesson's component.

Drift not covered (acceptable, documented as future work):
  - Drift between full-credit / half-credit thresholds in rubric vs lesson.
  - Drift between QUICKSTART floor numbers and rubric tiers.

Exit codes: 0 PASS, 1 drift found, 2 unexpected error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
RUBRIC = SKILL / "rubrics" / "confidence_score.md"
LESSONS = SKILL / "learner" / "lessons"


# ---- Rubric parsing ----

RUBRIC_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|"
)


def parse_rubric() -> dict[int, tuple[str, int]]:
    """Return {component_number: (name, weight)} from the rubric table."""
    out: dict[int, tuple[str, int]] = {}
    if not RUBRIC.exists():
        print(f"FAIL: rubric file missing: {RUBRIC}", file=sys.stderr)
        sys.exit(2)
    for line in RUBRIC.read_text().splitlines():
        m = RUBRIC_ROW.match(line)
        if not m:
            continue
        comp = int(m.group(1))
        name = m.group(2).strip()
        # Skip header rows where weight cell is "Weight" not a number
        try:
            weight = int(m.group(3))
        except ValueError:
            continue
        # Component numbers in the rubric are 1..N; skip rows that look like
        # mutation-score percentages (e.g. ≥75 in mutation table) — those rows
        # don't match the "first cell is a small int" shape because they begin
        # with a language name. RUBRIC_ROW already requires \d+ at start, so
        # we just need to reject duplicates beyond the component table.
        if comp in out:
            continue
        out[comp] = (name, weight)
    if not out:
        print(f"FAIL: no component rows parsed from {RUBRIC}", file=sys.stderr)
        sys.exit(2)
    return out


# ---- Lesson parsing ----

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
RUBRIC_COMPONENT_LINE = re.compile(r"^rubric_component:\s*(\d+)\s*$", re.MULTILINE)
LESSON_FILENAME = re.compile(r"^(\d+)_(.+)\.md$")

# Phrases that cite a weight from the rubric in lesson prose.
# We match conservative patterns to avoid false positives.
WEIGHT_PHRASES = [
    re.compile(r"weight\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"weight\s+of\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"weighted\s+at\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"weights?\s+\w+\s+at\s+(\d+)\b", re.IGNORECASE),
]


def normalize_slug(s: str) -> str:
    """Normalize a rubric component name to its filename slug form."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def lesson_slug_matches_name(filename_slug: str, rubric_name: str) -> bool:
    """Filename slug is allowed to be the normalized rubric name OR a close variant."""
    expected = normalize_slug(rubric_name)
    actual = filename_slug
    if actual == expected:
        return True
    # Allow common variants: "test_verification" vs "test_verification",
    # "code_read" vs "code_read_depth", "hallucination" vs "hallucination_check".
    # We accept actual being a prefix of expected, or expected being a prefix of actual,
    # provided the overlap is meaningful (>=8 chars).
    if len(actual) >= 8 and (actual.startswith(expected[:8]) or expected.startswith(actual[:8])):
        return True
    return False


def check_lesson(path: Path, rubric: dict[int, tuple[str, int]]) -> list[str]:
    errors: list[str] = []
    text = path.read_text()
    fm_match = FRONTMATTER.match(text)
    if not fm_match:
        errors.append(f"{path.name}: missing frontmatter (---)")
        return errors
    fm = fm_match.group(1)
    rc_match = RUBRIC_COMPONENT_LINE.search(fm)
    if not rc_match:
        errors.append(f"{path.name}: frontmatter missing `rubric_component: N`")
        return errors
    comp = int(rc_match.group(1))
    if comp not in rubric:
        errors.append(
            f"{path.name}: rubric_component={comp} not in rubric "
            f"(known: {sorted(rubric.keys())})"
        )
        return errors

    rubric_name, rubric_weight = rubric[comp]

    # 2. Filename alignment
    fn_match = LESSON_FILENAME.match(path.name)
    if not fn_match:
        errors.append(f"{path.name}: filename should match `NN_slug.md`")
        return errors
    fn_num = int(fn_match.group(1))
    fn_slug = fn_match.group(2)
    if fn_num != comp:
        errors.append(
            f"{path.name}: filename number {fn_num} != frontmatter rubric_component {comp}"
        )
    if not lesson_slug_matches_name(fn_slug, rubric_name):
        errors.append(
            f"{path.name}: filename slug '{fn_slug}' does not match rubric "
            f"component name '{rubric_name}' (normalized: '{normalize_slug(rubric_name)}')"
        )

    # 3. Weight drift in prose
    body = text[fm_match.end():]
    cited_weights: set[int] = set()
    for pat in WEIGHT_PHRASES:
        for m in pat.finditer(body):
            cited_weights.add(int(m.group(1)))
    bad = [w for w in cited_weights if w != rubric_weight]
    if bad:
        errors.append(
            f"{path.name}: cites weight(s) {sorted(bad)} but rubric weight for "
            f"component {comp} ({rubric_name}) is {rubric_weight}"
        )

    return errors


# ---- Main ----

def main() -> int:
    if not LESSONS.is_dir():
        print(f"test_learner_rubric_drift.py: SKIP (no lessons dir at {LESSONS})")
        return 0
    rubric = parse_rubric()

    all_errors: list[str] = []
    lesson_files = sorted(LESSONS.glob("*.md"))
    for lp in lesson_files:
        all_errors.extend(check_lesson(lp, rubric))

    if all_errors:
        print(
            f"test_learner_rubric_drift.py: FAIL ({len(all_errors)} drift issue(s))",
            file=sys.stderr,
        )
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        f"test_learner_rubric_drift.py: PASS "
        f"({len(lesson_files)} lesson(s) aligned with {len(rubric)}-component rubric)"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"test_learner_rubric_drift.py: ERROR ({exc})", file=sys.stderr)
        sys.exit(2)
