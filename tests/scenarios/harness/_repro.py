"""_repro.py: reproducibility metadata and assertion for Phase 11 runs."""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_DATED = re.compile(r".+-\d{4}-?\d{2}-?\d{2}$")


def harness_git_sha() -> str:
    try:
        here = Path(__file__).resolve().parent
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def run_metadata(model: str, seed: int, max_tokens: int, temperature: float = 0.0) -> dict:
    return {
        "model_snapshot": model,
        "seed": seed,
        "decode_params": {"max_tokens": max_tokens, "temperature": temperature},
        "harness_version": harness_git_sha(),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def assert_reproducible(meta: dict) -> None:
    model = meta.get("model_snapshot", "")
    if not _DATED.match(model):
        raise ValueError(
            f"non-reproducible model snapshot {model!r}: must be dated, "
            "e.g. claude-opus-4-5-20260601. Refusing to record an undated run."
        )
    if meta.get("seed") is None:
        raise ValueError("missing seed: run is not reproducible")
    for k in ("harness_version", "timestamp_utc", "decode_params"):
        if not meta.get(k):
            raise ValueError(f"missing reproducibility field: {k}")


if __name__ == "__main__":
    import json
    import sys

    try:
        m = run_metadata("claude-opus", seed=0, max_tokens=4096)
        assert_reproducible(m)
        print("UNEXPECTED PASS", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        m = run_metadata("claude-opus-4-5-20260601", seed=7, max_tokens=4096)
        assert_reproducible(m)
        print(json.dumps(m, indent=2))
        sys.exit(0)
