#!/usr/bin/env python3
"""Fixture tests for trainer_pr_review_gate_rerun.sh (no gh API calls).

Python (not .sh) so the generation gate's test-coexistence check is satisfied
without the tests/-of-tests recursion a sibling .sh would trigger.
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RERUN = REPO_ROOT / "scripts" / "trainer_pr_review_gate_rerun.sh"


class TestRerunScriptFixtures(unittest.TestCase):
    def test_syntax_ok(self) -> None:
        proc = subprocess.run(["bash", "-n", str(RERUN)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_skip_env_mode(self) -> None:
        env = {"TRAINER_GATE_RERUN_SKIP": "1", "PATH": "/usr/bin:/bin"}
        proc = subprocess.run(
            ["bash", str(RERUN), "1", "owner/repo"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("TRAINER_GATE_RERUN_SKIP", proc.stdout)

    def test_fake_repo_exits_zero(self) -> None:
        proc = subprocess.run(
            ["bash", str(RERUN), "999999", "nonexistent/fake-repo"],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)


if __name__ == "__main__":
    unittest.main()
