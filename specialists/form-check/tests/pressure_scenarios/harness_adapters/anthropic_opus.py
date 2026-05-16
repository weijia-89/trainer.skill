#!/usr/bin/env python3
"""harness_adapters/anthropic_opus.py — v0.2

Phase 11 harness adapter: Claude Opus via Anthropic API.

Simulates a Windsurf + Claude Opus session for form-check pressure scenarios.

Interpretation (per Wei 2026-05-16): option (a) API-simulated. We call the
Anthropic Messages API directly with the skill files concatenated into the
system prompt, prefaced by a Windsurf-simulating preamble. v0.3 will add a
real IDE-driven adapter and a Claude Code adapter.

Env vars (required for live mode):
  ANTHROPIC_API_KEY    API key

Env vars (optional):
  ANTHROPIC_MODEL      model id. Default: claude-opus-4-5.
                       Override to the exact "Opus 4.7 High" model id once Wei
                       confirms which Anthropic-side name maps to that.
  PHASE11_MAX_TOKENS   max output tokens. Default: 4096.
  PHASE11_OFFLINE      if set to a non-empty value, the adapter returns a
                       deterministic stub transcript without calling the API.
                       Used for smoke-testing the run.sh pipeline.

Inputs (stdin, JSON):
  {
    "scenario_dir": "/abs/path/to/category/scenario_name",
    "skill_files":  ["/abs/path/to/form-check.skill/SKILL.md", ...],
    "user_message": "the user prompt for the agent"
  }

Outputs (stdout, JSON):
  {
    "model":              "<resolved-model-id>",
    "harness":            "windsurf-sim-v0.2",
    "scenario_dir":       "...",
    "response_transcript":"...",
    "input_tokens":       int,
    "output_tokens":      int,
    "cost_usd":           float,
    "elapsed_seconds":    float,
    "timestamp_utc":      "2026-05-16T20:00:00Z",
    "offline":            bool
  }

Scoring (pass/fail) is NOT done here. The driver pipes response_transcript
to pass_criteria.py for each scenario.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


HARNESS_ID = "windsurf-sim-v0.2"
DEFAULT_MODEL = "claude-opus-4-5"

# Anthropic published Opus pricing (USD per Mtoken) as of mid-2026.
# Override per-model via env if Wei confirms a different model id.
PRICE_PER_MTOK = {
    "claude-opus-4-5":  {"input": 15.0, "output": 75.0},
    "claude-opus-4-7":  {"input": 15.0, "output": 75.0},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
}

WINDSURF_SIM_PREAMBLE = """You are an AI coding assistant running inside the Windsurf IDE.
The user has installed the following skills, and the IDE has loaded their
contents into your context. Treat each SKILL block below as authoritative
guidance for how you respond. When a skill prescribes a behavior (Iron Law,
Red Flag, Rationalization, scoring rubric, refusal protocol), follow it
exactly as written, including any required refusal language or score floors.

Do not editorialize about the skills themselves. Apply them.
""".strip()


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def build_system_prompt(skill_files: list[str]) -> str:
    parts: list[str] = [WINDSURF_SIM_PREAMBLE, ""]
    for path in skill_files:
        p = Path(path)
        if not p.is_file():
            parts.append(f"---\nSKILL FILE NOT FOUND: {path}\n---")
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except OSError as e:
            parts.append(f"---\nSKILL FILE READ ERROR ({path}): {e}\n---")
            continue
        parts.append("---")
        parts.append(f"SKILL: {path}")
        parts.append("")
        parts.append(content)
        parts.append("---")
    return "\n".join(parts)


def offline_stub(user_message: str) -> tuple[str, int, int]:
    transcript = (
        "[PHASE11_OFFLINE] Deterministic stub response. "
        "The driver is exercising the pipeline without calling the Anthropic API. "
        "This transcript intentionally does not satisfy any pass_criteria.py, "
        "so scenarios will FAIL in offline mode. That is expected.\n\n"
        f"Echoed user message (truncated to 200 chars): {user_message[:200]}"
    )
    return transcript, 0, 0


def call_anthropic_live(
    system_prompt: str,
    user_message: str,
    model: str,
    max_tokens: int,
) -> tuple[str, int, int]:
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError(
            "anthropic SDK not installed. Run: pip install anthropic\n"
            "Or set PHASE11_OFFLINE=1 to bypass the API call."
        ) from e

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY env var is empty. Set it, or set "
            "PHASE11_OFFLINE=1 to bypass the API call."
        )

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    # Concatenate all text blocks in the response.
    text_blocks: list[str] = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            text_blocks.append(block.text)
    transcript = "\n".join(text_blocks)

    input_tokens = getattr(msg.usage, "input_tokens", 0) if msg.usage else 0
    output_tokens = getattr(msg.usage, "output_tokens", 0) if msg.usage else 0
    return transcript, input_tokens, output_tokens


def compute_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = PRICE_PER_MTOK.get(model)
    if rates is None:
        return 0.0
    return round(
        (input_tokens / 1_000_000.0) * rates["input"]
        + (output_tokens / 1_000_000.0) * rates["output"],
        6,
    )


def main() -> int:
    req = load_input()
    skill_files = req.get("skill_files", [])
    user_message = req.get("user_message", "")
    scenario_dir = req.get("scenario_dir", "")

    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    max_tokens = int(os.environ.get("PHASE11_MAX_TOKENS", "4096"))
    offline = bool(os.environ.get("PHASE11_OFFLINE", "").strip())

    t0 = time.time()
    if offline:
        transcript, in_tok, out_tok = offline_stub(user_message)
    else:
        system_prompt = build_system_prompt(skill_files)
        transcript, in_tok, out_tok = call_anthropic_live(
            system_prompt=system_prompt,
            user_message=user_message,
            model=model,
            max_tokens=max_tokens,
        )
    elapsed = time.time() - t0

    out = {
        "model": model,
        "harness": HARNESS_ID,
        "scenario_dir": scenario_dir,
        "response_transcript": transcript,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cost_usd": compute_cost(model, in_tok, out_tok),
        "elapsed_seconds": round(elapsed, 3),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "offline": offline,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
