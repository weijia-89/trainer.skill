#!/usr/bin/env python3
# sdk-review F4: cover load_budget, section_tokens, warn-only vs fail, snapshot drift
"""Unit tests for check_context_budget helpers and exit paths."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check_context_budget.py"
sys.path.insert(0, str(HERE))

import check_context_budget as cb  # noqa: E402


class TestLoadBudget(unittest.TestCase):
    def test_parses_bool_int_and_snapshot_fields(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write(
                "[root_skill]\n"
                "warn_only = true\n"
                "root_skill_max_lines = 100\n"
                "current_lines = 42\n"
            )
            path = Path(f.name)
        try:
            cfg = cb.load_budget(path)
            self.assertTrue(cfg["warn_only"])
            self.assertEqual(cfg["root_skill_max_lines"], 100)
            self.assertEqual(cfg["current_lines"], 42)
        finally:
            path.unlink()


class TestSectionTokens(unittest.TestCase):
    def test_splits_on_h2_headings(self) -> None:
        text = "# title\n\n## One\nalpha\n\n## Two\nbeta gamma\n"
        sections = cb.section_tokens(text)
        self.assertIn("One", sections)
        self.assertIn("Two", sections)
        self.assertGreater(sections["Two"], sections["One"])


class TestCheckerExitPaths(unittest.TestCase):
    def _run_checker(self, budget: Path, skill: Path) -> tuple[int, str]:
        proc = subprocess.run(
            [sys.executable, str(CHECKER), str(budget), str(skill)],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def test_warn_only_returns_zero_on_cap_exceed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget = root / "budget.toml"
            skill = root / "SKILL.md"
            budget.write_text(
                "[root_skill]\nwarn_only = true\nroot_skill_max_lines = 1\n",
                encoding="utf-8",
            )
            skill.write_text("line one\nline two\n", encoding="utf-8")
            code, out = self._run_checker(budget, skill)
            self.assertEqual(code, 0)
            self.assertIn("VERDICT=WARN", out)

    def test_fail_mode_returns_one_on_cap_exceed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget = root / "budget.toml"
            skill = root / "SKILL.md"
            budget.write_text(
                "[root_skill]\nwarn_only = false\nroot_skill_max_lines = 1\n",
                encoding="utf-8",
            )
            skill.write_text("line one\nline two\n", encoding="utf-8")
            code, out = self._run_checker(budget, skill)
            self.assertEqual(code, 1)
            self.assertIn("VERDICT=FAIL", out)

    def test_section_cap_violation_respects_warn_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget = root / "budget.toml"
            skill = root / "SKILL.md"
            budget.write_text(
                "[root_skill]\nwarn_only = true\nmax_section_est_tokens = 1\n",
                encoding="utf-8",
            )
            skill.write_text("## Big\n" + ("word " * 50) + "\n", encoding="utf-8")
            code, out = self._run_checker(budget, skill)
            self.assertEqual(code, 0)
            self.assertIn("section 'Big'", out)

    def test_snapshot_mismatch_emits_verdict_warn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            budget = root / "budget.toml"
            skill = root / "SKILL.md"
            budget.write_text(
                "[root_skill]\nwarn_only = true\ncurrent_lines = 99\n",
                encoding="utf-8",
            )
            skill.write_text("only one line\n", encoding="utf-8")
            code, out = self._run_checker(budget, skill)
            self.assertEqual(code, 0)
            self.assertIn("snapshot current_lines 99 != measured 1", out)


class TestMainIntegration(unittest.TestCase):
    def test_live_budget_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CHECKER)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("VERDICT=PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
