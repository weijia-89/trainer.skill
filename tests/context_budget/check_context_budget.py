#!/usr/bin/env python3
"""Warn or fail when root SKILL.md exceeds context budget from budget.toml."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUDGET = Path(__file__).resolve().parent / "budget.toml"
DEFAULT_SKILL = ROOT / "SKILL.md"


def est_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def load_budget(path: Path) -> dict:
    """Parse flat key = value lines from budget.toml (stdlib only)."""
    cfg: dict = {}
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if section == "root_skill" or not section:
            if val.lower() in ("true", "false"):
                cfg[key] = val.lower() == "true"
            elif val.isdigit():
                cfg[key] = int(val)
            else:
                cfg[key] = val
    return cfg


def section_tokens(text: str) -> dict[str, int]:
    lines = text.splitlines()
    out: dict[str, int] = {}
    name = "(preamble)"
    buf: list[str] = []
    for line in lines:
        if line.startswith("## "):
            body = "\n".join(buf)
            out[name] = est_tokens(body)
            name = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    out[name] = est_tokens("\n".join(buf))
    return out


def main() -> int:
    budget_path = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].endswith(".toml") else DEFAULT_BUDGET
    skill_path = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        Path(sys.argv[1]) if len(sys.argv) > 1 and not str(sys.argv[1]).endswith(".toml") else DEFAULT_SKILL
    )
    cfg = load_budget(budget_path)
    warn_only = bool(cfg.get("warn_only", True))
    max_lines = int(cfg.get("root_skill_max_lines", 220))
    max_tokens = int(cfg.get("root_skill_max_est_tokens", 6000))
    max_section = int(cfg.get("max_section_est_tokens", 1200))
    text = skill_path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    token_count = est_tokens(text)
    sections = section_tokens(text)
    violations: list[str] = []
    if line_count > max_lines:
        violations.append(f"lines {line_count} > max {max_lines}")
    if token_count > max_tokens:
        violations.append(f"est_tokens {token_count} > max {max_tokens}")
    for sec, tok in sections.items():
        if tok > max_section:
            violations.append(f"section '{sec}' est_tokens {tok} > max {max_section}")
    print(f"BUDGET_FILE={budget_path}")
    print(f"SKILL_FILE={skill_path}")
    print(f"WARN_ONLY={warn_only}")
    print(f"LINES={line_count} MAX_LINES={max_lines}")
    print(f"EST_TOKENS={token_count} MAX_EST_TOKENS={max_tokens}")
    if violations:
        print("VIOLATIONS")
        for v in violations:
            print(f"  {v}")
        if warn_only:
            print("VERDICT=WARN")
            return 0
        print("VERDICT=FAIL")
        return 1
    print("VERDICT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
