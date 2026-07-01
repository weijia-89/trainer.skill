#!/usr/bin/env python3
"""verify_autonomous_code_review.py — contract gate for autonomous code review routing.

Ensures trainer SKILL + trainer-autonomous-code-review.md wire the trigger to
form-check code-review (specialist leaf load), not documentation-only theater.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "SKILL.md"
AUTONOMOUS_REF = REPO_ROOT / "references" / "trainer-autonomous-code-review.md"
CODEREVIEW_REF = REPO_ROOT / "references" / "trainer-codereview.md"
FORM_CHECK_SKILL = REPO_ROOT / "specialists" / "form-check" / "SKILL.md"
CODEREVIEW_PROMPT = REPO_ROOT / "prompts" / "trainer-codereview.txt"

FORM_CHECK_SKILL_CANON = "~/Projects/trainer.skill/specialists/form-check/SKILL.md"
ROUTER_REF = REPO_ROOT / "references" / "workflow-skill-router.md"


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def verify_skill_md(text: str, errors: list[str]) -> None:
    if "autonomous code review" not in text:
        _fail(errors, "SKILL.md description missing trigger 'autonomous code review'")
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, "SKILL.md missing route to trainer-autonomous-code-review.md")
    if not re.search(
        r"\*\*autonomous code review\*\*.*trainer-autonomous-code-review\.md",
        text,
        re.I | re.S,
    ):
        _fail(
            errors,
            "SKILL.md Activity table must route **autonomous code review** → trainer-autonomous-code-review.md",
        )
    if not re.search(
        r"Autonomous code review.*trainer-autonomous-code-review\.md",
        text,
        re.I,
    ):
        _fail(
            errors,
            "SKILL.md reference map missing Autonomous code review → trainer-autonomous-code-review.md",
        )


def verify_autonomous_ref(text: str, errors: list[str]) -> None:
    if "form-check" not in text.lower():
        _fail(errors, f"{AUTONOMOUS_REF.name}: missing form-check routing")
    if not re.search(r"code-review|adversarial-review", text):
        _fail(errors, f"{AUTONOMOUS_REF.name}: missing form-check mode (code-review / adversarial-review)")
    if "trainer-codereview.md" not in text:
        _fail(errors, f"{AUTONOMOUS_REF.name}: must reference trainer-codereview.md")
    if "trainer-github-pr-commentary.md" not in text:
        _fail(errors, f"{AUTONOMOUS_REF.name}: must reference trainer-github-pr-commentary.md")
    if FORM_CHECK_SKILL_CANON not in text and "specialists/form-check/SKILL.md" not in text:
        _fail(
            errors,
            f"{AUTONOMOUS_REF.name}: must require file_read form-check SKILL "
            f"({FORM_CHECK_SKILL_CANON})",
        )
    if "file_read" not in text.lower():
        _fail(errors, f"{AUTONOMOUS_REF.name}: must mandate file_read before form-check review")
    if "two consecutive" not in text.lower() and "zero new findings" not in text.lower():
        _fail(errors, f"{AUTONOMOUS_REF.name}: missing autonomous loop stop condition")


def verify_codereview_ref(text: str, errors: list[str]) -> None:
    if "form-check" not in text.lower():
        _fail(errors, f"{CODEREVIEW_REF.name}: missing form-check in routing")


def verify_form_check_skill(text: str, errors: list[str]) -> None:
    if 'name: form-check' not in text:
        _fail(errors, f"{FORM_CHECK_SKILL}: missing name: form-check frontmatter")
    if "code-review" not in text and "code review" not in text.lower():
        _fail(errors, f"{FORM_CHECK_SKILL}: must mention code review in description or body")


def verify_codereview_prompt(text: str, errors: list[str]) -> None:
    if "trainer-codereview.md" not in text:
        _fail(errors, f"{CODEREVIEW_PROMPT.name}: must reference trainer-codereview.md")
    if "form-check" not in text.lower():
        _fail(errors, f"{CODEREVIEW_PROMPT.name}: must reference form-check routing")


def verify_workflow_router(text: str, errors: list[str]) -> None:
    if "autonomous code review" not in text.lower():
        _fail(errors, f"{ROUTER_REF.name}: missing autonomous code review router row")
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, f"{ROUTER_REF.name}: must route to trainer-autonomous-code-review.md")
    if "verify_autonomous_code_review.py" not in text:
        _fail(errors, f"{ROUTER_REF.name}: must list verify_autonomous_code_review.py in Verify column")


def verify_repo(repo_root: Path | None = None) -> list[str]:
    root = repo_root or REPO_ROOT
    errors: list[str] = []

    skill_path = root / "SKILL.md"
    autonomous_path = root / "references" / "trainer-autonomous-code-review.md"
    codereview_path = root / "references" / "trainer-codereview.md"
    form_check_path = root / "specialists" / "form-check" / "SKILL.md"
    prompt_path = root / "prompts" / "trainer-codereview.txt"
    router_path = root / "references" / "workflow-skill-router.md"

    for path in (
        skill_path,
        autonomous_path,
        codereview_path,
        form_check_path,
        prompt_path,
        router_path,
    ):
        if not path.is_file():
            errors.append(f"missing required file: {path}")
            return errors

    verify_skill_md(skill_path.read_text(encoding="utf-8"), errors)
    verify_autonomous_ref(autonomous_path.read_text(encoding="utf-8"), errors)
    verify_codereview_ref(codereview_path.read_text(encoding="utf-8"), errors)
    verify_form_check_skill(form_check_path.read_text(encoding="utf-8"), errors)
    verify_codereview_prompt(prompt_path.read_text(encoding="utf-8"), errors)
    verify_workflow_router(router_path.read_text(encoding="utf-8"), errors)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify autonomous code review trainer contract")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args()

    errors = verify_repo(args.repo_root.resolve())
    if errors:
        print(f"# verify_autonomous_code_review: FAIL ({len(errors)})", file=sys.stderr)
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"# verify_autonomous_code_review: PASS — {args.repo_root.resolve()}")
    print("  form-check code-review routing: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
