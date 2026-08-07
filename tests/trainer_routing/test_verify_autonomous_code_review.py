#!/usr/bin/env python3
"""Unit tests for verify_autonomous_code_review contract gate."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "verify_autonomous_code_review.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import verify_autonomous_code_review as vacr  # noqa: E402


class TestVerifyAutonomousCodeReviewLive(unittest.TestCase):
    def test_canonical_repo_passes(self) -> None:
        errors = vacr.verify_repo(REPO_ROOT)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_cli_exit_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(REPO_ROOT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)


class TestVerifyAutonomousCodeReviewFixtures(unittest.TestCase):
    def test_missing_form_check_load_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_minimal_tree(root)
            auto = (root / "references" / "trainer-autonomous-code-review.md").read_text()
            auto = auto.replace(vacr.FORM_CHECK_SKILL_CANON, "form-check/SKILL.md")
            auto = auto.replace("file_read", "read")
            (root / "references" / "trainer-autonomous-code-review.md").write_text(auto)
            errors = vacr.verify_repo(root)
            self.assertTrue(any("file_read form-check" in e for e in errors))

    def test_skill_missing_trigger_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_minimal_tree(root)
            skill = (root / "SKILL.md").read_text()
            skill = re.sub(r"code review", "review work", skill, flags=re.I)
            (root / "SKILL.md").write_text(skill)
            errors = vacr.verify_repo(root)
            self.assertTrue(any("code review" in e.lower() for e in errors))

    def test_output_style_rule_missing_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_minimal_tree(root)
            ref = root / "references" / "trainer-github-pr-commentary.md"
            text = ref.read_text()
            text = text.replace(vacr.OUTPUT_STYLE_SECTION, "Review output")
            ref.write_text(text)
            errors = vacr.verify_repo(root)
            self.assertTrue(
                any("Review output style" in e for e in errors),
                msg="\n".join(errors),
            )

    def test_output_style_parity_marker_missing_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_minimal_tree(root)
            ref = root / "references" / "trainer-codereview.md"
            text = ref.read_text()
            text = text.replace(vacr.OUTPUT_STYLE_PARITY_MARKER, "never mention process")
            ref.write_text(text)
            errors = vacr.verify_repo(root)
            self.assertTrue(
                any("parity marker" in e for e in errors),
                msg="\n".join(errors),
            )

    def test_output_style_rule_missing_in_prompt_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_minimal_tree(root)
            prompt = root / "prompts" / "trainer-codereview.txt"
            text = prompt.read_text()
            text = text.replace(vacr.OUTPUT_STYLE_PARITY_MARKER, "never mention process")
            prompt.write_text(text)
            errors = vacr.verify_repo(root)
            self.assertTrue(
                any("trainer-codereview.txt" in e for e in errors),
                msg="\n".join(errors),
            )

    def _copy_minimal_tree(self, root: Path) -> None:
        for rel in (
            "SKILL.md",
            "references/trainer-autonomous-code-review.md",
            "references/trainer-codereview.md",
            "references/trainer-github-pr-commentary.md",
            "references/workflow-skill-router.md",
            "specialists/form-check/SKILL.md",
            "prompts/trainer-codereview.txt",
        ):
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
