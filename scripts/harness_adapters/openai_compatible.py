#!/usr/bin/env python3
"""openai_compatible.py: trainer Phase 11 adapter (OpenAI-compatible endpoints).

Works with any provider that serves POST {base_url}/chat/completions with an
OpenAI-style body and response: OpenAI, nvidia/NIM, DeepSeek, OpenRouter,
Together, vLLM, llama.cpp, and similar. No provider SDK and no new
dependency: the live call is stdlib urllib.

Env contract:
  OPENAI_MODEL     required for live runs; must be a DATED model snapshot
                   (enforced by _repro.assert_reproducible, Rule B.6).
  OPENAI_API_KEY   required for live runs; never logged, never committed.
  OPENAI_BASE_URL  default https://api.openai.com/v1; point it at any
                   OpenAI-compatible endpoint.
  OPENAI_PRICE_IN_MTOK / OPENAI_PRICE_OUT_MTOK
                   optional indicative pricing (default 0). cost_usd is an
                   INDICATIVE tracker and nothing gates on it (Rule B.11);
                   provider-specific pricing belongs to the operator env.
  PHASE11_MAX_TOKENS / PHASE11_OFFLINE
                   shared with the anthropic adapter (see run.sh).

Scoring is NOT done here; run.sh pipes response_transcript to
pass_criteria.py.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent.parent / "tests" / "scenarios" / "harness"))

from _common import HARNESS_ID, build_system_prompt, offline_stub, wrap_untrusted  # noqa: E402
from _repro import assert_reproducible, run_metadata  # noqa: E402

DEFAULT_BASE_URL = "https://api.openai.com/v1"


def build_request_body(system_prompt: str, user_message: str, model: str, max_tokens: int) -> dict:
    return {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": wrap_untrusted(user_message)},
        ],
    }


def call_live(system_prompt: str, user_message: str, model: str, max_tokens: int, seed: int):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY empty; set it or PHASE11_OFFLINE=1")
    base = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    body = build_request_body(system_prompt, user_message, model, max_tokens)
    request = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = payload["choices"][0]["message"]["content"] or ""
    usage = payload.get("usage", {})
    return text, int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))


def main() -> int:
    req = json.loads(sys.stdin.read() or "{}")
    skill_files = req.get("skill_files", [])
    user_message = req.get("user_message", "")
    scenario_dir = req.get("scenario_dir", "")
    seed = int(req.get("seed", 0))

    model = os.environ.get("OPENAI_MODEL", "").strip()
    max_tokens = int(os.environ.get("PHASE11_MAX_TOKENS", "4096"))
    offline = bool(os.environ.get("PHASE11_OFFLINE", "").strip())

    meta = run_metadata(model or "openai-compatible", seed=seed, max_tokens=max_tokens)
    if not offline:
        assert_reproducible(meta)

    t0 = time.time()
    if offline:
        transcript, itok, otok = offline_stub(user_message)
    else:
        transcript, itok, otok = call_live(
            build_system_prompt(skill_files), user_message, model, max_tokens, seed
        )
    price_in = float(os.environ.get("OPENAI_PRICE_IN_MTOK", "0") or 0)
    price_out = float(os.environ.get("OPENAI_PRICE_OUT_MTOK", "0") or 0)
    out = {
        "model": model or "OFFLINE",
        "harness": HARNESS_ID,
        "scenario_dir": scenario_dir,
        "response_transcript": transcript,
        "input_tokens": itok,
        "output_tokens": otok,
        "cost_usd": round(itok / 1e6 * price_in + otok / 1e6 * price_out, 6),
        "elapsed_seconds": round(time.time() - t0, 3),
        "offline": offline,
        "meta": meta,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
