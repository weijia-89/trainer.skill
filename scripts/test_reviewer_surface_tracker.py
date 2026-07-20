#!/usr/bin/env python3
"""Tests for reviewer_surface_tracker.py."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "reviewer_surface_tracker.py")


def _run(cmd, root):
    return subprocess.run(
        [sys.executable, SCRIPT, "--root", root] + cmd,
        capture_output=True,
        text=True,
    )


class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.branch = "feat-x"

    def test_novelty_below_threshold_fails(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
              "--surface", "a.py", "b.py"], self.root)
        _run(["--branch", self.branch, "--pass", "2", "record",
              "--surface", "a.py", "b.py"], self.root)
        c = _run(["--branch", self.branch, "--pass", "2", "check",
                  "--novelty-min", "0.50"], self.root)
        self.assertEqual(c.returncode, 2)

    def test_novelty_above_threshold_passes(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
              "--surface", "a.py"], self.root)
        _run(["--branch", self.branch, "--pass", "2", "record",
              "--surface", "b.py"], self.root)
        c = _run(["--branch", self.branch, "--pass", "2", "check",
                  "--novelty-min", "0.50"], self.root)
        self.assertEqual(c.returncode, 0)

    def test_empty_surface_rejected(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
              "--surface", "a.py"], self.root)
        _run(["--branch", self.branch, "--pass", "2", "record",
              "--surface"], self.root)
        c = _run(["--branch", self.branch, "--pass", "2", "check"], self.root)
        self.assertEqual(c.returncode, 2)

    def test_unexplored_reported_when_seed_declared(self):
        # Seed declares the universe; after one pass covering it all,
        # unexplored must be 0 (the loop's primary stop branch).
        _run(["--branch", self.branch, "--pass", "1", "record",
               "--surface", "a.py", "b.py", "--seed", "a.py", "b.py"], self.root)
        c = _run(["--branch", self.branch, "--pass", "1", "check"], self.root)
        self.assertEqual(c.returncode, 0)
        self.assertIn("unexplored 0", c.stderr)

    def test_unexplored_nonzero_when_seed_partial(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
               "--surface", "a.py", "--seed", "a.py", "b.py"], self.root)
        c = _run(["--branch", self.branch, "--pass", "1", "check"], self.root)
        self.assertEqual(c.returncode, 0)
        self.assertIn("unexplored 1", c.stderr)

    def test_unexplored_absent_when_no_seed(self):
        # Without a seed the universe is unknown; the script must NOT fabricate
        # an unexplored count (avoids a false stop on a guessed universe).
        _run(["--branch", self.branch, "--pass", "1", "record",
               "--surface", "a.py"], self.root)
        c = _run(["--branch", self.branch, "--pass", "1", "check"], self.root)
        self.assertEqual(c.returncode, 0)
        self.assertNotIn("unexplored", c.stderr)

    def test_record_refuses_overwrite_of_existing_pass(self):
        # B2: re-recording an existing pass must not silently corrupt the
        # novelty baseline other passes depend on.
        r1 = _run(["--branch", self.branch, "--pass", "1", "record",
                   "--surface", "a.py", "b.py"], self.root)
        self.assertEqual(r1.returncode, 0)
        r2 = _run(["--branch", self.branch, "--pass", "1", "record",
                   "--surface", "Z.py"], self.root)
        self.assertEqual(r2.returncode, 2)
        # Baseline intact.
        path = os.path.join(self.root, "localonly", "reviewer",
                            self.branch, "pass1.json")
        with open(path) as fh:
            m = json.load(fh)
        self.assertEqual(m["surface"], ["a.py", "b.py"])

    def test_record_allows_idempotent_rerun(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
               "--surface", "a.py"], self.root)
        r2 = _run(["--branch", self.branch, "--pass", "1", "record",
                   "--surface", "a.py"], self.root)
        self.assertEqual(r2.returncode, 0)

    def test_idempotent_check(self):
        _run(["--branch", self.branch, "--pass", "1", "record",
              "--surface", "a.py"], self.root)
        c1 = _run(["--branch", self.branch, "--pass", "1", "check"], self.root)
        c2 = _run(["--branch", self.branch, "--pass", "1", "check"], self.root)
        self.assertEqual(c1.returncode, c2.returncode)

    def test_cli_arg_parsing(self):
        r1 = _run(["--pass", "1", "record", "--surface", "a.py"], self.root)
        self.assertEqual(r1.returncode, 2)
        r2 = _run(["--branch", self.branch, "record", "--surface", "a.py"], self.root)
        self.assertEqual(r2.returncode, 2)

    def test_manifest_roundtrip(self):
        r = _run(["--branch", self.branch, "--pass", "1", "record",
                  "--surface", "src/a.py", "src/b.py",
                  "--verify", "0", "1"], self.root)
        self.assertEqual(r.returncode, 0)
        path = os.path.join(self.root, "localonly", "reviewer",
                            self.branch, "pass1.json")
        with open(path) as fh:
            m = json.load(fh)
        self.assertEqual(m["pass"], 1)
        self.assertEqual(m["verify_exit_codes"], [0, 1])
        self.assertIn(os.path.normpath("src/a.py"), m["surface"])


if __name__ == "__main__":
    unittest.main()
