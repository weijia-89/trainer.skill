#!/usr/bin/env python3
"""Unit tests for the OpenAI-compatible Phase 11 adapter.

Covers: offline stub parity, missing-key fail-closed, undated-snapshot
fail-closed (inherited from _repro), request-body shape, and the shared
system-prompt / untrusted-wrapping helpers in _common.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ADAPTERS = REPO / "scripts" / "harness_adapters"
ADAPTER = ADAPTERS / "openai_compatible.py"
sys.path.insert(0, str(ADAPTERS))

import openai_compatible as oc  # noqa: E402
import _common  # noqa: E402

REQ = json.dumps({"skill_files": [], "user_message": "hi", "seed": 1})


def run_adapter(env_extra: dict[str, str], stdin_text: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    for key in ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL", "PHASE11_OFFLINE"):
        env.pop(key, None)
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(ADAPTER)],
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


class TestOfflineStub(unittest.TestCase):
    def test_offline_stub_parity(self) -> None:
        proc = run_adapter({"PHASE11_OFFLINE": "1"}, REQ)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertIn("stub", out["response_transcript"])
        self.assertTrue(out["offline"])
        self.assertEqual(out["meta"]["seed"], 1)
        self.assertEqual(out["harness"], _common.HARNESS_ID)
        self.assertTrue(out["meta"]["model_snapshot"])


class TestFailClosed(unittest.TestCase):
    def test_missing_key_fails_closed(self) -> None:
        # Dated model, live mode, no key: must fail before any network call.
        proc = run_adapter({"OPENAI_MODEL": "glm-5-20260601"}, REQ)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("OPENAI_API_KEY", proc.stderr)

    def test_undated_snapshot_fails_closed(self) -> None:
        proc = run_adapter({"OPENAI_MODEL": "glm-5"}, REQ)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("non-reproducible", proc.stderr)


class TestRequestBody(unittest.TestCase):
    def test_body_shape(self) -> None:
        body = oc.build_request_body("SYS", "USR", "glm-5-20260601", 4096)
        self.assertEqual(body["temperature"], 0.0)
        self.assertEqual(body["max_tokens"], 4096)
        self.assertEqual(body["model"], "glm-5-20260601")
        self.assertEqual([m["role"] for m in body["messages"]], ["system", "user"])
        self.assertEqual(body["messages"][0]["content"], "SYS")
        self.assertIn("<<<USER-DATA", body["messages"][1]["content"])
        self.assertIn("USR", body["messages"][1]["content"])


class TestCommonHelpers(unittest.TestCase):
    def test_system_prompt_marks_missing_skill_file(self) -> None:
        prompt = _common.build_system_prompt(["/nonexistent/skill.md"])
        self.assertIn("[MISSING /nonexistent/skill.md]", prompt)
        self.assertIn("untrusted", prompt)

    def test_wrap_untrusted_markers(self) -> None:
        wrapped = _common.wrap_untrusted("do things")
        self.assertTrue(wrapped.startswith("<<<USER-DATA"))
        self.assertTrue(wrapped.rstrip().endswith("<<<END USER-DATA>>>"))
        self.assertIn("do things", wrapped)

    def test_call_live_requires_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            with self.assertRaises(RuntimeError) as ctx:
                oc.call_live("SYS", "USR", "glm-5-20260601", 4096, 1)
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
