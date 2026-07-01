#!/usr/bin/env python3
"""Unit tests for trainer code-review anti-theater contract."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.trainer_codereview_contract import (  # noqa: E402
    classify_r6_files,
    validate_pr_test_plan_body,
    validate_r6_user_facing_docs,
    validate_review_comment,
)


class TestRound1TheaterRejected(unittest.TestCase):
    def test_round1_fixture_fails(self) -> None:
        body = (FIXTURES / "round1_theater_bad.md").read_text(encoding="utf-8")
        errors = validate_review_comment(body, "trainer.skill")
        self.assertTrue(errors, "round1 theater comment must fail")
        joined = "\n".join(errors)
        self.assertIn("no defects", joined.lower())
        self.assertIn("harness", joined.lower())

    def test_round1_bug_inventory_only_fails(self) -> None:
        body = (FIXTURES / "round1_theater_bad.md").read_text(encoding="utf-8")
        from lib.trainer_codereview_contract import validate_bug_inventory

        self.assertTrue(validate_bug_inventory(body, "trainer.skill"))


class TestRound3GoodPasses(unittest.TestCase):
    def test_round3_fixture_passes(self) -> None:
        body = (FIXTURES / "round3_good.md").read_text(encoding="utf-8")
        self.assertEqual(validate_review_comment(body, "trainer.skill"), [])

    def test_pr_body_good_passes(self) -> None:
        body = (FIXTURES / "pr_body_good.md").read_text(encoding="utf-8")
        self.assertEqual(validate_pr_test_plan_body(body), [])


class TestCliHarness(unittest.TestCase):
    def test_comment_validate_cli_round1_fails(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_review_comment_validate.py"),
                "--repo",
                "trainer.skill",
                "--body-file",
                str(FIXTURES / "round1_theater_bad.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout)


class TestR6UserFacingDocs(unittest.TestCase):
    def test_code_without_docs_fails(self) -> None:
        files = (FIXTURES / "r6_files_code_no_docs.txt").read_text().splitlines()
        errors = validate_r6_user_facing_docs(files, "", verdict="APPROVE")
        self.assertTrue(errors)
        self.assertIn("R-6", errors[0])

    def test_code_with_docs_and_closure_passes(self) -> None:
        files = (FIXTURES / "r6_files_code_with_docs.txt").read_text().splitlines()
        review = (FIXTURES / "r6_review_good.md").read_text(encoding="utf-8")
        self.assertEqual(validate_r6_user_facing_docs(files, review, verdict="APPROVE"), [])

    def test_code_with_docs_no_closure_fails_approve(self) -> None:
        files = (FIXTURES / "r6_files_code_with_docs.txt").read_text().splitlines()
        review = (FIXTURES / "r6_review_no_closure.md").read_text(encoding="utf-8")
        errors = validate_r6_user_facing_docs(files, review, verdict="APPROVE")
        self.assertTrue(any("R-6 closure" in e for e in errors))

    def test_tests_only_exempt(self) -> None:
        code_paths, doc_paths = classify_r6_files(
            ["tests/trainer_codereview/test_foo.py"]
        )
        self.assertEqual(code_paths, [])
        self.assertEqual(doc_paths, [])

    def test_r6_cli_code_no_docs_fails(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_r6_validate.py"),
                "--files-file",
                str(FIXTURES / "r6_files_code_no_docs.txt"),
                "--review-file",
                str(FIXTURES / "r6_review_no_closure.md"),
                "--verdict",
                "APPROVE",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout)


if __name__ == "__main__":
    unittest.main()
