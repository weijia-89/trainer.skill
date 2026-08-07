#!/usr/bin/env python3
"""verify_autonomous_code_review.py — contract gate for default code review loop routing.

Ensures trainer SKILL + trainer-autonomous-code-review.md wire **code review** to
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
COMMENTARY_REF = REPO_ROOT / "references" / "trainer-github-pr-commentary.md"
FORM_CHECK_SKILL = REPO_ROOT / "specialists" / "form-check" / "SKILL.md"
CODEREVIEW_PROMPT = REPO_ROOT / "prompts" / "trainer-codereview.txt"

FORM_CHECK_SKILL_CANON = "~/Projects/trainer.skill/specialists/form-check/SKILL.md"
ROUTER_REF = REPO_ROOT / "references" / "workflow-skill-router.md"

# Review output style rule (mandatory): PR comments must never disclose review
# methodology / posture / check counts. Guarded on both canonical surfaces so a
# silent deletion in either file fails the contract gate.
OUTPUT_STYLE_SECTION = "Review output style"
OUTPUT_STYLE_PARITY_MARKER = 'never mention "multi-posture"'
FORBIDDEN_OPERATOR_PHRASES = (
    "operator says autonomous code review",
    "operator says **autonomous code review**",
    "say autonomous code review",
)


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def verify_skill_md(text: str, errors: list[str]) -> None:
    lower = text.lower()
    if "autonomous code review" in lower:
        _fail(
            errors,
            "SKILL.md must not list 'autonomous code review' as an operator trigger "
            "(use code review only)",
        )
    if "code review" not in lower:
        _fail(errors, "SKILL.md description missing trigger 'code review'")
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, "SKILL.md missing route to trainer-autonomous-code-review.md")
    if not re.search(
        r"code review.*trainer-autonomous-code-review\.md",
        text,
        re.I | re.S,
    ):
        _fail(
            errors,
            "SKILL.md Activity must route code review → trainer-autonomous-code-review.md",
        )
    if not re.search(
        r"Code review loop.*trainer-autonomous-code-review\.md",
        text,
        re.I,
    ):
        _fail(
            errors,
            "SKILL.md reference map missing Code review loop → trainer-autonomous-code-review.md",
        )


def verify_autonomous_ref(text: str, errors: list[str]) -> None:
    lower = text.lower()
    for phrase in FORBIDDEN_OPERATOR_PHRASES:
        if phrase in lower:
            _fail(errors, f"{AUTONOMOUS_REF.name}: forbidden operator phrase: {phrase!r}")
    if "operator requests **code review**" not in text and "operator requests code review" not in lower:
        _fail(errors, f"{AUTONOMOUS_REF.name}: must trigger on operator code review request")
    if "form-check" not in lower:
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
    if "file_read" not in lower:
        _fail(errors, f"{AUTONOMOUS_REF.name}: must mandate file_read before form-check review")
    if "two consecutive" not in lower and "zero new findings" not in lower:
        _fail(errors, f"{AUTONOMOUS_REF.name}: missing code review loop stop condition")


def verify_codereview_ref(text: str, errors: list[str]) -> None:
    if "form-check" not in text.lower():
        _fail(errors, f"{CODEREVIEW_REF.name}: missing form-check in routing")
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, f"{CODEREVIEW_REF.name}: must reference default loop doc")


def verify_output_style_rule(text: str, errors: list[str], source: str) -> None:
    """Review output style rule must exist and stay in parity on both surfaces."""
    if OUTPUT_STYLE_SECTION not in text:
        _fail(
            errors,
            f"{source}: missing '{OUTPUT_STYLE_SECTION}' rule "
            "(PR comments must not disclose review methodology)",
        )
    if OUTPUT_STYLE_PARITY_MARKER.lower() not in text.lower():
        _fail(
            errors,
            f"{source}: missing parity marker {OUTPUT_STYLE_PARITY_MARKER!r} "
            "(keep the forbidden-term list in sync with the canonical section)",
        )


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
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, f"{CODEREVIEW_PROMPT.name}: must reference default code review loop doc")


def verify_workflow_router(text: str, errors: list[str]) -> None:
    lower = text.lower()
    if "autonomous code review" in lower:
        _fail(
            errors,
            f"{ROUTER_REF.name}: must not use 'autonomous code review' as router trigger",
        )
    if "code review" not in lower:
        _fail(errors, f"{ROUTER_REF.name}: missing code review router row")
    if "trainer-autonomous-code-review.md" not in text:
        _fail(errors, f"{ROUTER_REF.name}: must route to trainer-autonomous-code-review.md")
    if "verify_trainer_codereview.sh" not in text:
        _fail(errors, f"{ROUTER_REF.name}: must list verify_trainer_codereview.sh in Verify column")


def verify_repo(repo_root: Path | None = None) -> list[str]:
    root = repo_root or REPO_ROOT
    errors: list[str] = []

    skill_path = root / "SKILL.md"
    autonomous_path = root / "references" / "trainer-autonomous-code-review.md"
    codereview_path = root / "references" / "trainer-codereview.md"
    commentary_path = root / "references" / "trainer-github-pr-commentary.md"
    form_check_path = root / "specialists" / "form-check" / "SKILL.md"
    prompt_path = root / "prompts" / "trainer-codereview.txt"
    router_path = root / "references" / "workflow-skill-router.md"

    for path in (
        skill_path,
        autonomous_path,
        codereview_path,
        commentary_path,
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
    verify_output_style_rule(
        codereview_path.read_text(encoding="utf-8"),
        errors,
        CODEREVIEW_REF.name,
    )
    verify_output_style_rule(
        commentary_path.read_text(encoding="utf-8"),
        errors,
        COMMENTARY_REF.name,
    )
    verify_output_style_rule(
        prompt_path.read_text(encoding="utf-8"),
        errors,
        CODEREVIEW_PROMPT.name,
    )
    verify_form_check_skill(form_check_path.read_text(encoding="utf-8"), errors)
    verify_codereview_prompt(prompt_path.read_text(encoding="utf-8"), errors)
    verify_workflow_router(router_path.read_text(encoding="utf-8"), errors)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify default code review loop trainer contract")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args()

    errors = verify_repo(args.repo_root.resolve())
    if errors:
        print(f"# verify_autonomous_code_review: FAIL ({len(errors)})", file=sys.stderr)
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"# verify_autonomous_code_review: PASS — {args.repo_root.resolve()}")
    print("  code review loop + form-check routing: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
