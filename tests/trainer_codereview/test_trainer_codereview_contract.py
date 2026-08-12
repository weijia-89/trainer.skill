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


class TestReviewMethodologyDisclosure(unittest.TestCase):
    """Review output style rule: comments must not disclose review methodology."""

    def test_disclosure_fixture_fails(self) -> None:
        body = (FIXTURES / "methodology_disclosure_bad.md").read_text(encoding="utf-8")
        errors = validate_review_comment(body, "trainer.skill")
        joined = "\n".join(errors)
        self.assertTrue(any("methodology" in e for e in errors), msg=joined)
        self.assertIn("150 checks", joined)
        self.assertIn("5 personas", joined)

    def test_each_forbidden_term_rejected(self) -> None:
        base = (FIXTURES / "round3_good.md").read_text(encoding="utf-8")
        from lib.trainer_codereview_contract import REVIEW_METHODOLOGY_TERMS

        for term in REVIEW_METHODOLOGY_TERMS:
            with self.subTest(term=term):
                body = base + f"\n- Note: reviewed using {term}\n"
                errors = validate_review_comment(body, "trainer.skill")
                self.assertTrue(any("methodology" in e for e in errors), msg=term)

    def test_clean_comment_passes(self) -> None:
        body = (FIXTURES / "round3_good.md").read_text(encoding="utf-8")
        self.assertEqual(validate_review_comment(body, "trainer.skill"), [])

    def test_cli_full_rejects_disclosure(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_review_comment_validate.py"),
                "--repo",
                "trainer.skill",
                "--body-file",
                str(FIXTURES / "methodology_disclosure_bad.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout)


class TestTermDocParity(unittest.TestCase):
    """Enforcement term list must not drift from the canonical rule text."""

    def test_enforced_terms_present_in_both_canonical_surfaces(self) -> None:
        from lib.trainer_codereview_contract import REVIEW_METHODOLOGY_TERMS

        for rel in (
            "references/trainer-github-pr-commentary.md",
            "references/trainer-codereview.md",
            "prompts/trainer-codereview.txt",
        ):
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            for term in REVIEW_METHODOLOGY_TERMS:
                self.assertIn(term, text, msg=f"{rel} missing term {term!r}")


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


class TestPrBodyContract(unittest.TestCase):
    """PR body Test plan contract must be enforced like the review comment."""

    def test_missing_test_plan_fails(self) -> None:
        body = (FIXTURES / "pr_body_missing_test_plan.md").read_text(encoding="utf-8")
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("Test plan", errors[0])

    def test_missing_automated_section_fails(self) -> None:
        body = (FIXTURES / "pr_body_missing_automated.md").read_text(encoding="utf-8")
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("Automated", errors[0])

    def test_automated_section_outside_test_plan_fails(self) -> None:
        body = (FIXTURES / "pr_body_automated_outside_test_plan.md").read_text(
            encoding="utf-8"
        )
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("under Test plan", errors[0])

    def test_fake_headings_inside_code_fence_fail(self) -> None:
        body = (FIXTURES / "pr_body_fake_headings_in_fence.md").read_text(
            encoding="utf-8"
        )
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("Test plan", errors[0])

    def test_fake_automated_heading_inside_code_fence_fails(self) -> None:
        body = (FIXTURES / "pr_body_automated_fake_in_fence.md").read_text(
            encoding="utf-8"
        )
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("under Test plan", errors[0])

    def test_mixed_fence_spoof_fails(self) -> None:
        body = (FIXTURES / "pr_body_mixed_fence_spoof.md").read_text(
            encoding="utf-8"
        )
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("under Test plan", errors[0])

    def test_weak_grep_only_checks_fail(self) -> None:
        body = (FIXTURES / "pr_body_weak_checks.md").read_text(encoding="utf-8")
        errors = validate_pr_test_plan_body(body)
        joined = "\n".join(errors)
        self.assertTrue(any("harness" in e for e in errors), msg=joined)
        self.assertIn("grep/test -f", joined)

    def test_no_checked_box_fails(self) -> None:
        body = (FIXTURES / "pr_body_no_checked.md").read_text(encoding="utf-8")
        errors = validate_pr_test_plan_body(body)
        self.assertTrue(errors)
        self.assertIn("- [x]", errors[0])

    def test_good_body_with_require_checked_false_passes(self) -> None:
        body = (FIXTURES / "pr_body_good.md").read_text(encoding="utf-8")
        self.assertEqual(validate_pr_test_plan_body(body, require_checked=False), [])

    def test_no_checked_body_with_require_checked_false_passes(self) -> None:
        body = (FIXTURES / "pr_body_no_checked.md").read_text(encoding="utf-8")
        self.assertEqual(validate_pr_test_plan_body(body, require_checked=False), [])

    def test_cli_weak_checks_reject_exit_1(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_body_validate.py"),
                "--body-file",
                str(FIXTURES / "pr_body_weak_checks.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout)
        self.assertIn("FAIL", proc.stderr)

    def test_cli_good_body_pass_exit_0(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_body_validate.py"),
                "--body-file",
                str(FIXTURES / "pr_body_good.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_cli_missing_test_plan_reject_exit_1(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_body_validate.py"),
                "--body-file",
                str(FIXTURES / "pr_body_missing_test_plan.md"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, msg=proc.stdout)
        self.assertIn("Test plan", proc.stderr)

    def test_cli_no_require_checked_pass_exit_0(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_body_validate.py"),
                "--body-file",
                str(FIXTURES / "pr_body_no_checked.md"),
                "--no-require-checked",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_cli_stdin_good_body_pass_exit_0(self) -> None:
        body = (FIXTURES / "pr_body_good.md").read_text(encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "trainer_pr_body_validate.py"),
            ],
            input=body,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("PASS", proc.stdout)


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
