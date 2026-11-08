#!/usr/bin/env python3
"""anthropic_opus.py: trainer Phase 11 adapter (Claude Opus via Anthropic API).

Additions over the form-check adapter:
  - Fails closed on an undated model snapshot (reproducibility, Rule B.6).
  - Wraps scenario setup/user text as untrusted DATA (prompt-injection guard).

cost_usd is an INDICATIVE tracker (rough per-run spend for budgeting). It is
not authoritative pricing and nothing gates on it (Rule B.11).
Scoring is NOT done here; run.sh pipes response_transcript to pass_criteria.py.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent.parent / "tests" / "scenarios" / "harness"))

from _common import HARNESS_ID, build_system_prompt, offline_stub, wrap_untrusted  # noqa: E402
from _repro import assert_reproducible, run_metadata  # noqa: E402

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "").strip()

PRICE_PER_MTOK = {"input": 15.0, "output": 75.0}


def call_live(system_prompt: str, user_message: str, model: str, max_tokens: int, seed: int):
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY empty; set it or PHASE11_OFFLINE=1")
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": wrap_untrusted(user_message)}],
    )
    text = "\n".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    u = msg.usage
    return text, getattr(u, "input_tokens", 0), getattr(u, "output_tokens", 0)


def main() -> int:
    req = json.loads(sys.stdin.read() or "{}")
    skill_files = req.get("skill_files", [])
    user_message = req.get("user_message", "")
    scenario_dir = req.get("scenario_dir", "")
    seed = int(req.get("seed", 0))

    model = DEFAULT_MODEL
    max_tokens = int(os.environ.get("PHASE11_MAX_TOKENS", "4096"))
    offline = bool(os.environ.get("PHASE11_OFFLINE", "").strip())

    meta = run_metadata(model or "claude-opus", seed=seed, max_tokens=max_tokens)
    if not offline:
        assert_reproducible(meta)

    t0 = time.time()
    if offline:
        transcript, itok, otok = offline_stub(user_message)
    else:
        transcript, itok, otok = call_live(
            build_system_prompt(skill_files), user_message, model, max_tokens, seed
        )
    out = {
        "model": model or "OFFLINE",
        "harness": HARNESS_ID,
        "scenario_dir": scenario_dir,
        "response_transcript": transcript,
        "input_tokens": itok,
        "output_tokens": otok,
        "cost_usd": round(
            itok / 1e6 * PRICE_PER_MTOK["input"] + otok / 1e6 * PRICE_PER_MTOK["output"], 6
        ),
        "elapsed_seconds": round(time.time() - t0, 3),
        "offline": offline,
        "meta": meta,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
