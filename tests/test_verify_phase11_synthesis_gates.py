#!/usr/bin/env python3
"""Smoke test for verify_phase11_synthesis_gates.sh: the offline gate passes.

Runs the real offline synthesis gate and asserts its verdict line. This is
the per-script test file the generation gate expects (test_<script>.py).
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
GATE = REPO / "scripts" / "verify_phase11_synthesis_gates.sh"


class TestSynthesisGatesSmoke(unittest.TestCase):
    def test_offline_gate_passes(self) -> None:
        proc = subprocess.run(
            ["bash", str(GATE)],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        self.assertEqual(
            proc.returncode, 0, proc.stdout[-2000:] + proc.stderr[-2000:]
        )
        self.assertIn("VERDICT: PASS (offline synthesis gates)", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
