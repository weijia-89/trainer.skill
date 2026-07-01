"""Trainer code-review PR comment + body contract (anti-theater gate).

Catches round-1 failure mode: APPROVE + placeholder Bug inventory + weak-only
automated checks (grep/test -f) without real verify harness evidence.
"""
from __future__ import annotations

import re

INV_HEADING = re.compile(r"^###\s+(Bug inventory|Findings)\b", re.M | re.I)
BUDS_P02_CAP = re.compile(r"P0\s*[-–]\s*P2\b", re.I)
SEV_ROW = re.compile(r"\|\s*[^|\n]+\|\s*P[0-4]\s*\|", re.I)
NONE_DECL = re.compile(
    r"(no\s+P0\s*[-–]\s*P4|no\s+P0-P4|zero\s+P0|P0\s*[-–]\s*P4\s+findings:\s*none|"
    r"no\s+P0\s*[-–]\s*P[0-4]\s+(findings|defects|blockers))",
    re.I,
)
VERDICT_META = re.compile(r"verdict=(APPROVE|REQUEST_CHANGES|BLOCK)", re.I)
AUTO_VERIFY_SECTION = re.compile(r"^###\s+Automated verification\b", re.M | re.I)
TRAINER_NOTES = re.compile(r"^###\s+Trainer notes\b", re.M | re.I)
FORBIDDEN_PEDAGOGY = re.compile(r"^###\s+Pedagogy\b", re.M | re.I)
PLACEHOLDER_ROW = re.compile(r"\|\s*—\s*\|\s*—\s*\|")
NO_DEFECTS_THEATER = re.compile(r"no defects in diff|no defects\b", re.I)
CHECKED_BOX = re.compile(r"^- \[x\]", re.M | re.I)
WEAK_AUTO_ONLY = re.compile(
    r"^- \[x\][^\n]*(grep\s+-q|test\s+-f)\b",
    re.M | re.I,
)
STRONG_AUTO = re.compile(
    r"^- \[x\][^\n]*("
    r"verify_[\w./-]+\.(py|sh)|"
    r"test_[\w./-]+\.(py|sh)|"
    r"bash\s+[\w./-]*(verify|test)[\w./-]*\.sh|"
    r"GITHUB_ACTIONS=true[^\n]*verify_trainer_sync"
    r")",
    re.M | re.I,
)

PR_TEST_PLAN = re.compile(r"^##\s+Test plan\b", re.M | re.I)
PR_AUTO_SECTION = re.compile(r"^###\s+Automated\b", re.M | re.I)


def extract_verdict(body: str) -> str | None:
    m = VERDICT_META.search(body)
    return m.group(1).upper() if m else None


def _automated_verification_slice(body: str) -> str:
    m = AUTO_VERIFY_SECTION.search(body)
    if not m:
        return ""
    rest = body[m.end() :]
    nxt = re.search(r"^###\s+", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def validate_bug_inventory(body: str, repo: str) -> list[str]:
    errors: list[str] = []
    if not INV_HEADING.search(body):
        errors.append(
            "missing '### Bug inventory' (preferred) or '### Findings' section"
        )
    if repo == "buds" and BUDS_P02_CAP.search(body):
        errors.append(
            "buds remediate scope is P0-P4; do not cap reviews at P0-P2 "
            "(list or waive every P0-P4 item)"
        )
    if PLACEHOLDER_ROW.search(body) and NO_DEFECTS_THEATER.search(body):
        errors.append(
            "placeholder Bug inventory (— columns) with 'no defects' is theater; "
            "use ranked P0-P4 rows or explicit 'No P0–P4 findings' with evidence"
        )
    if NO_DEFECTS_THEATER.search(body) and not NONE_DECL.search(body):
        errors.append(
            "Bug inventory 'no defects' without explicit 'No P0–P4 findings' line is forbidden"
        )
    if not (NONE_DECL.search(body) or SEV_ROW.search(body)):
        errors.append(
            "Bug inventory must table every P0-P4 item (ID | P | Finding | Status) "
            "or include an explicit 'No P0–P4 findings' line with evidence"
        )
    return errors


def validate_review_comment(body: str, repo: str) -> list[str]:
    errors = validate_bug_inventory(body, repo)
    if FORBIDDEN_PEDAGOGY.search(body):
        errors.append("forbidden '### Pedagogy' heading; use '### Trainer notes'")
    if not TRAINER_NOTES.search(body):
        errors.append("missing '### Trainer notes' section")
    else:
        for label in ("Program notes", "Your form", "Next session"):
            if label not in body:
                errors.append(f"Trainer notes missing label: {label}")

    verdict = extract_verdict(body)
    if not verdict:
        errors.append("missing verdict=APPROVE|REQUEST_CHANGES|BLOCK in meta comment")

    if verdict == "APPROVE":
        auto = _automated_verification_slice(body)
        if not AUTO_VERIFY_SECTION.search(body):
            errors.append("APPROVE requires '### Automated verification' in review comment")
        elif not CHECKED_BOX.search(auto):
            errors.append(
                "APPROVE requires at least one checked '- [x]' under Automated verification"
            )
        else:
            checked = [ln for ln in auto.splitlines() if CHECKED_BOX.match(ln)]
            if checked and not any(STRONG_AUTO.search(ln) for ln in checked):
                errors.append(
                    "APPROVE Automated verification must include at least one harness "
                    "command (verify_*.py/sh, test_*.py, bash scripts/verify|test), "
                    "not grep/test -f only"
                )
    return errors


def validate_pr_test_plan_body(body: str, *, require_checked: bool = True) -> list[str]:
    errors: list[str] = []
    if not PR_TEST_PLAN.search(body):
        errors.append("PR body missing '## Test plan'")
    if not PR_AUTO_SECTION.search(body):
        errors.append("PR body missing '### Automated' under Test plan")
    elif require_checked:
        auto_m = PR_AUTO_SECTION.search(body)
        assert auto_m is not None
        rest = body[auto_m.end() :]
        nxt = re.search(r"^###\s+", rest, re.M)
        auto_slice = rest[: nxt.start()] if nxt else rest
        if not CHECKED_BOX.search(auto_slice):
            errors.append(
                "PR body Test plan Automated section needs at least one '- [x]' "
                "(trainer runs harness before APPROVE)"
            )
        else:
            checked = [ln for ln in auto_slice.splitlines() if CHECKED_BOX.match(ln)]
            if checked and not any(STRONG_AUTO.search(ln) for ln in checked):
                errors.append(
                    "PR body Automated checks must include at least one real harness "
                    "(verify_*/test_*), not grep/test -f only"
                )
    return errors
