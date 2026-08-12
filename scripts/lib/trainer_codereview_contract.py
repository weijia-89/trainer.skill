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
# Review output style rule (trainer-github-pr-commentary.md § Review output style):
# PR comments must not disclose review methodology / posture / check counts.
REVIEW_METHODOLOGY_TERMS = (
    "multi-posture",
    "personas",
    "postures",
    "loop 1",
    "loop 2",
    "150 checks",
    "75 checks",
    "5 personas",
)
FORBIDDEN_REVIEW_METHODOLOGY = [
    re.compile(rf"\b{re.escape(term)}\b", re.I) for term in REVIEW_METHODOLOGY_TERMS
]
PLACEHOLDER_ROW = re.compile(r"\|\s*—\s*\|\s*—\s*\|")
NO_DEFECTS_THEATER = re.compile(r"no defects in diff|no defects\b", re.I)
CHECKED_BOX = re.compile(r"^- \[x\]", re.M | re.I)
WEAK_AUTO_ONLY = re.compile(
    r"^- \[x\][^\n]*(grep\s+-q|test\s+-f)\b",
    re.M | re.I,
)
# Verbatim shell output dumped into PR comments (anti-theater)
VERBOSITY_DUMP = re.compile(
    r"(zsh:\d+:|command not found|FAIL:.*verify_|"
    r"^rm\s+'|^delete mode |^create mode |^\+\+\+ |^--- |"
    r"Ran \d+ tests? in|OK\s*$|PASS\s+user-facing docs|"
    r"# verify_source_ingest_contract summary|^# /Users/)",
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

PR_TEST_PLAN = re.compile(r"^##[ \t]+Test plan[ \t]*$", re.I)
PR_AUTO_SECTION = re.compile(r"^###[ \t]+Automated\b", re.I)
PR_TOP_LEVEL_SECTION = re.compile(r"^##[ \t]+", re.I)
PR_SUBSECTION = re.compile(r"^###[ \t]+", re.I)
MARKDOWN_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")

# R-6 user-facing docs gate (operator prose must track code changes)
R6_CODE_EXACT = frozenset({"SKILL.md", "mirrors/windsurf-trainer.md"})
R6_CODE_PREFIXES = (
    "scripts/",
    "references/",
    "prompts/",
    ".github/",
    "specialists/",
    "mirrors/",
)
R6_DOC_EXACT = frozenset({"CHANGELOG.md", "README.md", "ROADMAP.md", "SECURITY.md"})
R6_DOC_PREFIXES = ("docs/",)
R6_WAIVE = re.compile(
    r"(R-6|user-facing doc).{0,120}waived|waived.{0,120}(R-6|user-facing doc)",
    re.I | re.S,
)
R6_CLOSURE = re.compile(
    r"\bR-6\b|deai|CHANGELOG\.md|README\.md|ROADMAP\.md|SECURITY\.md|user-facing doc",
    re.I,
)


def is_r6_code_path(path: str) -> bool:
    p = path.strip().replace("\\", "/")
    if not p or p.startswith("tests/"):
        return False
    if p in R6_CODE_EXACT:
        return True
    return any(p.startswith(prefix) for prefix in R6_CODE_PREFIXES)


def is_r6_doc_path(path: str) -> bool:
    p = path.strip().replace("\\", "/")
    if not p:
        return False
    if p in R6_DOC_EXACT:
        return True
    return any(p.startswith(prefix) for prefix in R6_DOC_PREFIXES)


def classify_r6_files(changed_files: list[str]) -> tuple[list[str], list[str]]:
    code_paths: list[str] = []
    doc_paths: list[str] = []
    for raw in changed_files:
        p = raw.strip()
        if not p:
            continue
        if is_r6_code_path(p):
            code_paths.append(p)
        if is_r6_doc_path(p):
            doc_paths.append(p)
    return code_paths, doc_paths


def validate_r6_user_facing_docs(
    changed_files: list[str],
    review_body: str = "",
    *,
    verdict: str | None = None,
) -> list[str]:
    """R-6: operator-facing code changes require doc updates or explicit waive."""
    code_paths, doc_paths = classify_r6_files(changed_files)
    if not code_paths:
        return []

    errors: list[str] = []
    sample = ", ".join(code_paths[:4])
    if len(code_paths) > 4:
        sample += f", +{len(code_paths) - 4} more"

    if not doc_paths and not R6_WAIVE.search(review_body):
        errors.append(
            "R-6: PR changes operator-facing code "
            f"({sample}) without CHANGELOG.md, README.md, ROADMAP.md, SECURITY.md, "
            "or docs/ update — add doc deltas or Bug inventory waive row citing R-6"
        )

    if verdict and verdict.upper() == "APPROVE" and review_body:
        if doc_paths and not R6_CLOSURE.search(review_body) and not R6_WAIVE.search(
            review_body
        ):
            errors.append(
                "APPROVE requires R-6 closure in review comment "
                "(name updated doc paths, deai pass, or explicit R-6 waive row)"
            )
    return errors


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
    for term, rx in zip(REVIEW_METHODOLOGY_TERMS, FORBIDDEN_REVIEW_METHODOLOGY):
        if rx.search(body):
            errors.append(
                "PR comment discloses review methodology or posture "
                f"(forbidden term: {term!r}); see "
                "trainer-github-pr-commentary.md § Review output style"
            )
    if not TRAINER_NOTES.search(body):
        errors.append("missing '### Trainer notes' section")
    else:
        for label in ("Program notes", "Your form", "Next session"):
            if label not in body:
                errors.append(f"Trainer notes missing label: {label}")

    # Anti-theater: verbatim shell output dumps (zsh errors, rm logs, test output)
    if VERBOSITY_DUMP.search(body):
        errors.append(
            "PR comment contains verbatim shell output / command-not-found errors / "
            "CI log dumps. Summarize at high level only. "
            "See trainer-github-pr-commentary.md self-check #1."
        )

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


def _markdown_section(
    body: str, heading: re.Pattern[str], next_heading: re.Pattern[str]
) -> str | None:
    """Return a real Markdown section, ignoring headings inside fenced code."""
    lines = body.splitlines(keepends=True)
    fence: tuple[str, int] | None = None
    start: int | None = None
    for index, line in enumerate(lines):
        fence_match = MARKDOWN_FENCE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence is not None:
            continue
        if start is None:
            if heading.match(line.rstrip("\r\n")):
                start = index + 1
        elif next_heading.match(line.rstrip("\r\n")):
            return "".join(lines[start:index])
    return "".join(lines[start:]) if start is not None else None


def validate_pr_test_plan_body(body: str, *, require_checked: bool = True) -> list[str]:
    errors: list[str] = []
    test_plan = _markdown_section(body, PR_TEST_PLAN, PR_TOP_LEVEL_SECTION)
    if test_plan is None:
        errors.append("PR body missing '## Test plan'")
    else:
        automated = _markdown_section(test_plan, PR_AUTO_SECTION, PR_SUBSECTION)
        if automated is None:
            errors.append("PR body missing '### Automated' under Test plan")
        elif require_checked:
            if not CHECKED_BOX.search(automated):
                errors.append(
                    "PR body Test plan Automated section needs at least one '- [x]' "
                    "(trainer runs harness before APPROVE)"
                )
            else:
                checked = [ln for ln in automated.splitlines() if CHECKED_BOX.match(ln)]
                if checked and not any(STRONG_AUTO.search(ln) for ln in checked):
                    errors.append(
                        "PR body Automated checks must include at least one real harness "
                        "(verify_*/test_*), not grep/test -f only"
                    )
    return errors
