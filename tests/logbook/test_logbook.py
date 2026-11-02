#!/usr/bin/env python3
"""Unit tests for the logbook CLI (trainer.skill specialist).

Run: python3 tests/logbook/test_logbook.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "specialists" / "logbook" / "scripts" / "logbook.py"

EXIT_OK = 0
EXIT_VERIFY_FAILED = 1
EXIT_EMPTY = 2
EXIT_TORN = 3
EXIT_DUPLICATE = 4
EXIT_ALREADY = 5
EXIT_NOT_INITIALIZED = 6
EXIT_REFUSED = 7
EXIT_TOO_LONG = 9


def load_cli():
    spec = importlib.util.spec_from_file_location("logbook_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LogbookBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        self.cli = load_cli()

    def run_cli(self, *args: str) -> int:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.cli.main(["--project", str(self.root), *args])
        self.last_out = out.getvalue()
        self.last_err = err.getvalue()
        return code

    def capture(self, *args: str) -> tuple[int, str, str]:
        code = self.run_cli(*args)
        return code, self.last_out, self.last_err

    def init(self) -> int:
        return self.run_cli("init", "--objective", "ship the thing")

    def ledger_path(self) -> Path:
        return self.root / ".workledger" / "ledger.jsonl"

    def ledger_lines(self) -> list[str]:
        return self.ledger_path().read_text().splitlines()

    def events(self) -> list[dict]:
        return [json.loads(line) for line in self.ledger_lines()]

    def slice_events(self) -> list[dict]:
        return [e for e in self.events() if e["kind"] == "slice"]


class TestInit(LogbookBase):
    def test_init_creates_ledger_state_and_self_ignoring_gitignore(self) -> None:
        code, out, _ = self.capture("init", "--objective", "ship the thing")
        self.assertEqual(code, EXIT_OK, msg=out)
        self.assertTrue(self.ledger_path().is_file())
        self.assertTrue((self.root / ".workledger" / "ACTIVE_STATE.md").is_file())
        self.assertEqual(
            (self.root / ".workledger" / ".gitignore").read_text(), "*\n"
        )
        goal = self.events()[0]
        self.assertEqual(goal["kind"], "goal_registered")
        self.assertEqual(goal["objective"], "ship the thing")
        self.assertEqual(len(goal["id"]), 16)
        self.assertIn("ship the thing", (self.root / ".workledger" / "ACTIVE_STATE.md").read_text())

    def test_second_init_refuses_and_keeps_the_ledger(self) -> None:
        self.assertEqual(self.init(), EXIT_OK)
        self.run_cli("record", "slice", "--what", "wrote a parser", "--scope", "one file")
        before = self.ledger_lines()
        code, out, _ = self.capture("init", "--objective", "second try")
        self.assertEqual(code, EXIT_ALREADY, msg=out)
        self.assertEqual(self.ledger_lines(), before)

    def test_init_refuses_a_non_git_directory_without_force(self) -> None:
        plain = Path(self._tmp.name) / "plain"
        plain.mkdir()
        code = self.cli.main(["--project", str(plain), "init", "--objective", "x"])
        self.assertEqual(code, EXIT_REFUSED)
        self.assertFalse((plain / ".workledger").exists())

    def test_init_refuses_the_home_directory(self) -> None:
        home = Path.home()
        existed = (home / ".workledger").exists()
        code = self.cli.main(["--project", str(home), "init", "--objective", "x"])
        self.assertEqual(code, EXIT_REFUSED)
        if not existed:
            self.assertFalse((home / ".workledger").exists())


class TestRecord(LogbookBase):
    def test_slice_appends_an_event_with_id_and_goal_id(self) -> None:
        self.init()
        code, out, _ = self.capture(
            "record", "slice", "--what", "wrote the parser", "--scope", "one function"
        )
        self.assertEqual(code, EXIT_OK, msg=out)
        event = self.slice_events()[0]
        self.assertEqual(event["what"], "wrote the parser")
        self.assertEqual(event["scope"], "one function")
        self.assertEqual(len(event["id"]), 16)
        self.assertEqual(event["goal_id"], self.events()[0]["id"])

    def test_duplicate_slice_is_refused(self) -> None:
        self.init()
        args = ("record", "slice", "--what", "same set", "--scope", "same weight")
        self.assertEqual(self.run_cli(*args), EXIT_OK)
        before = self.ledger_lines()
        code, out, _ = self.capture(*args)
        self.assertEqual(code, EXIT_DUPLICATE, msg=out)
        self.assertEqual(self.ledger_lines(), before)

    def test_outcome_attaches_to_the_named_slice(self) -> None:
        self.init()
        self.run_cli("record", "slice", "--what", "first set", "--scope", "light")
        self.run_cli("record", "slice", "--what", "second set", "--scope", "heavy")
        first = self.slice_events()[0]["id"]
        code, out, _ = self.capture(
            "record", "outcome", "--outcome", "logged", "--id", first
        )
        self.assertEqual(code, EXIT_OK, msg=out)
        outcomes = [e for e in self.events() if e["kind"] == "outcome"]
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["slice_id"], first)
        self.assertEqual(outcomes[0]["outcome"], "logged")

    def test_second_outcome_for_the_same_slice_is_refused(self) -> None:
        self.init()
        self.run_cli("record", "slice", "--what", "one set", "--scope", "light")
        slice_id = self.slice_events()[0]["id"]
        self.assertEqual(
            self.run_cli("record", "outcome", "--outcome", "logged", "--id", slice_id),
            EXIT_OK,
        )
        code, out, _ = self.capture(
            "record", "outcome", "--outcome", "missed", "--id", slice_id
        )
        self.assertEqual(code, EXIT_DUPLICATE, msg=out)

    def test_unknown_slice_id_is_refused(self) -> None:
        self.init()
        code, out, _ = self.capture(
            "record", "outcome", "--outcome", "logged", "--id", "0123456789abcdef"
        )
        self.assertEqual(code, EXIT_DUPLICATE, msg=out)

    def test_naming_both_a_slice_id_and_latest_is_refused(self) -> None:
        self.init()
        self.run_cli("record", "slice", "--what", "one set", "--scope", "light")
        slice_id = self.slice_events()[0]["id"]
        code, out, _ = self.capture(
            "record", "outcome", "--outcome", "logged", "--id", slice_id, "--latest"
        )
        self.assertEqual(code, EXIT_DUPLICATE, msg=out)
        self.assertEqual(
            [e for e in self.events() if e["kind"] == "outcome"], []
        )

    def test_record_next_appears_in_the_state_page(self) -> None:
        self.init()
        code, out, _ = self.capture("record", "next", "--what", "wire the test")
        self.assertEqual(code, EXIT_OK, msg=out)
        state = (self.root / ".workledger" / "ACTIVE_STATE.md").read_text()
        self.assertIn("Next set on the bar", state)
        self.assertIn("wire the test", state)

    def test_overlong_summary_is_refused(self) -> None:
        self.init()
        code, out, _ = self.capture(
            "record", "slice", "--what", "x" * 241, "--scope", "long"
        )
        self.assertEqual(code, EXIT_TOO_LONG, msg=out)
        self.assertEqual(self.slice_events(), [])

    def test_evidence_is_stored_relative_to_the_project(self) -> None:
        self.init()
        (self.root / "out.txt").write_text("proof\n")
        code, out, _ = self.capture(
            "record", "slice", "--what", "wrote proof", "--scope", "one file",
            "--evidence", "out.txt",
        )
        self.assertEqual(code, EXIT_OK, msg=out)
        self.assertEqual(self.slice_events()[0]["evidence"], "out.txt")


class TestState(LogbookBase):
    def test_state_page_regenerates_after_each_mutating_command(self) -> None:
        self.init()
        self.run_cli("record", "slice", "--what", "wrote the parser", "--scope", "one function")
        state = (self.root / ".workledger" / "ACTIVE_STATE.md").read_text()
        self.assertIn("wrote the parser", state)
        self.assertIn("ship the thing", state)

    def test_state_page_says_when_no_next_set_is_set(self) -> None:
        self.init()
        state = (self.root / ".workledger" / "ACTIVE_STATE.md").read_text()
        self.assertIn("Next set on the bar", state)
        self.assertIn("not set", state)


class TestVerify(LogbookBase):
    def test_verify_on_an_empty_logbook_exits_two(self) -> None:
        self.init()
        code, out, _ = self.capture("verify")
        self.assertEqual(code, EXIT_EMPTY, msg=out)
        self.assertIn("no sets", out)

    def test_verify_passes_when_the_evidence_file_exists(self) -> None:
        self.init()
        (self.root / "out.txt").write_text("proof\n")
        self.run_cli(
            "record", "slice", "--what", "wrote proof", "--scope", "one file",
            "--evidence", "out.txt",
        )
        code, out, _ = self.capture("verify")
        self.assertEqual(code, EXIT_OK, msg=out)
        self.assertIn("EV_OK", out)

    def test_verify_fails_when_the_evidence_file_is_missing(self) -> None:
        self.init()
        self.run_cli(
            "record", "slice", "--what", "wrote proof", "--scope", "one file",
            "--evidence", "gone.txt",
        )
        code, out, _ = self.capture("verify")
        self.assertEqual(code, EXIT_VERIFY_FAILED, msg=out)
        self.assertIn("EV_MISSING", out)

    def test_verify_flags_a_slice_logged_without_evidence(self) -> None:
        self.init()
        self.run_cli(
            "record", "slice", "--what", "thought about it", "--scope", "no proof",
            "--no-evidence", "nothing to point at",
        )
        code, out, _ = self.capture("verify")
        self.assertEqual(code, EXIT_VERIFY_FAILED, msg=out)
        self.assertIn("EV_UNVERIFIED", out)


class TestTornTail(LogbookBase):
    def _tear_tail(self) -> None:
        with self.ledger_path().open("a") as handle:
            handle.write('{"kind":"sli')

    def test_status_refuses_to_guess_on_a_torn_tail(self) -> None:
        self.init()
        self._tear_tail()
        code, out, err = self.capture("status")
        self.assertEqual(code, EXIT_TORN, msg=out)
        self.assertIn("checkpoint-tail-unknown", err)

    def test_the_next_write_repairs_the_torn_tail(self) -> None:
        self.init()
        self._tear_tail()
        code, out, err = self.capture(
            "record", "slice", "--what", "after the crash", "--scope", "one file"
        )
        self.assertEqual(code, EXIT_OK, msg=out)
        self.assertIn("repaired", err)
        for line in self.ledger_lines():
            json.loads(line)
        self.assertEqual(len(self.slice_events()), 1)


class TestConcurrency(LogbookBase):
    def _spawn(self, command: list[str]) -> subprocess.Popen:
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_two_concurrent_writers_keep_every_record_intact(self) -> None:
        self.init()
        procs = []
        for index in range(5):
            for tag in ("left", "right"):
                procs.append(
                    self._spawn(
                        [
                            sys.executable, str(SCRIPT), "--project", str(self.root),
                            "record", "slice", "--what", f"set from {tag} {index}",
                            "--scope", tag,
                        ]
                    )
                )
        for proc in procs:
            _, err = proc.communicate()
            self.assertEqual(proc.returncode, 0, msg=err.decode())
        lines = self.ledger_lines()
        for line in lines:
            json.loads(line)
        self.assertEqual(len(self.slice_events()), 10)
        ids = [e["id"] for e in self.slice_events()]
        self.assertEqual(len(set(ids)), 10)

    def test_the_same_set_raced_by_two_writers_is_logged_once(self) -> None:
        self.init()
        command = [
            sys.executable, str(SCRIPT), "--project", str(self.root),
            "record", "slice", "--what", "the same set", "--scope", "same weight",
        ]
        procs = [self._spawn(command) for _ in range(2)]
        codes = []
        for proc in procs:
            proc.communicate()
            codes.append(proc.returncode)
        self.assertEqual(sorted(codes), [0, EXIT_DUPLICATE])
        self.assertEqual(len(self.slice_events()), 1)


if __name__ == "__main__":
    unittest.main()
