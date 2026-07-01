#!/usr/bin/env python3
"""
Phase 11 combined report for trainer.skill: Layer A (scenario suite pass^k),
Layer B (calibration log), Layer C (mutation testing).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
DEFAULT_LAYER_A_RUNS = SKILL_ROOT / "tests" / "scenarios" / "harness" / "runs"
DEFAULT_LAYER_B_LOG = SKILL_ROOT / ".recovery" / "calibration.jsonl"
DEFAULT_LAYER_C_REPORT = Path("/tmp/skill-mutation-test/mutation_report.md")
DEFAULT_OUT = SKILL_ROOT / "tests" / "scenarios" / "harness" / "phase11_report.md"


def find_latest_layer_a_run(runs_dir: Path) -> Path | None:
    if not runs_dir.is_dir():
        return None
    candidates = [p for p in runs_dir.iterdir() if p.is_dir() and (p / "summary.txt").is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.name)


def parse_layer_a_summary(summary_path: Path) -> dict:
    """Parse trainer summary.txt: lines like '  scenario: 2/3 (0.67)'."""
    result: dict = {"total": 0, "scenarios": [], "any_below_1": False}
    for line in summary_path.read_text().splitlines():
        m = re.match(r"\s+(\S+):\s+(\d+)/(\d+)\s+\(([\d.]+)\)", line)
        if m:
            name, p, k, rate = m.group(1), int(m.group(2)), int(m.group(3)), float(m.group(4))
            result["total"] += 1
            result["scenarios"].append({"scenario": name, "passes": p, "k": k, "rate": rate})
            if rate < 1.0:
                result["any_below_1"] = True
    return result


def run_layer_b(log_path: Path) -> tuple[str, dict]:
    analyze = SKILL_ROOT / "scripts" / "calibration_analyze.py"
    text = ""
    parsed: dict = {}
    if not analyze.is_file():
        return ("calibration_analyze.py not found at " + str(analyze), {})
    try:
        text_proc = subprocess.run(
            [sys.executable, str(analyze), "--log", str(log_path), "--format", "plain"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = text_proc.stdout or text_proc.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        text = "(calibration_analyze.py timed out)"
    try:
        json_proc = subprocess.run(
            [sys.executable, str(analyze), "--log", str(log_path), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if json_proc.returncode == 0 and json_proc.stdout.strip():
            parsed = json.loads(json_proc.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        parsed = {}
    return text, parsed


def parse_layer_c_report(report_path: Path) -> dict:
    out: dict = {"raw": "", "mutants": 0, "load_bearing": 0, "weight_zero": 0}
    if not report_path.is_file():
        return out
    out["raw"] = report_path.read_text()
    for row in out["raw"].splitlines():
        if row.startswith("| ##"):
            out["mutants"] += 1
        if "yes (flipped to FAIL)" in row:
            out["load_bearing"] += 1
        if "no (within noise)" in row:
            out["weight_zero"] += 1
    return out


def render_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_layer_a(layer_a_run: Path | None, layer_a: dict | None) -> str:
    if not layer_a_run or not layer_a or not layer_a.get("scenarios"):
        return (
            "## Layer A: scenario suite\n\n"
            "No run found. Execute `bash scripts/run.sh --offline --k 3` first.\n"
        )
    parts = [
        "## Layer A: scenario suite",
        "",
        f"Run: `{layer_a_run.name}`",
        f"Path: `{layer_a_run}`",
        "",
        f"**Scenarios**: {layer_a['total']}. "
        f"Any pass-rate below 1.0: **{'yes' if layer_a['any_below_1'] else 'no'}**.",
        "",
        "### Per-scenario pass-rate",
        "",
    ]
    rows = [
        [s["scenario"], str(s["passes"]), str(s["k"]), f"{s['rate']:.2f}"]
        for s in layer_a["scenarios"]
    ]
    parts.append(render_table(["scenario", "passes", "k", "rate"], rows))
    parts.append("")
    return "\n".join(parts)


def render_layer_b(layer_b_text: str, layer_b_json: dict) -> str:
    parts = ["## Layer B: calibration log analyzer", ""]
    parts.append("```")
    parts.append(layer_b_text.rstrip())
    parts.append("```")
    parts.append("")
    if layer_b_json:
        parts.append(f"Tier: {layer_b_json.get('tier', '?')} (N={layer_b_json.get('n_events', 0)}).")
        parts.append("")
    return "\n".join(parts)


def render_layer_c(layer_c: dict) -> str:
    parts = ["## Layer C: mutation testing", ""]
    if not layer_c.get("raw"):
        parts.append("No mutation report found. Execute `python3 scripts/mutation_test_skill.py`.")
        parts.append("")
        return "\n".join(parts)
    parts.append(
        f"Sections tested: **{layer_c.get('mutants', 0)}**. "
        f"Load-bearing flips: **{layer_c.get('load_bearing', 0)}**."
    )
    parts.append("")
    parts.append("```markdown")
    parts.append(layer_c["raw"].rstrip())
    parts.append("```")
    parts.append("")
    return "\n".join(parts)


def render_verdict(layer_a: dict | None, layer_c: dict) -> tuple[str, int]:
    notes = []
    exit_code = 0
    if layer_a and layer_a.get("scenarios"):
        if layer_a["any_below_1"]:
            notes.append("Layer A: at least one scenario pass-rate below 1.0 across k repeats.")
            exit_code = 2
        else:
            notes.append("Layer A: all scenarios 100% pass-rate across k.")
    else:
        notes.append("Layer A: no run available.")
    if layer_c.get("load_bearing", 0) > 0:
        notes.append(f"Layer C: {layer_c['load_bearing']} load-bearing section drop(s).")
        exit_code = max(exit_code, 2)
    elif layer_c.get("raw"):
        notes.append("Layer C: report present.")
    else:
        notes.append("Layer C: no mutation report.")
    body = "\n".join(f"- {n}" for n in notes)
    return f"## Verdict\n\n{body}\n", exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer-a-run", type=Path)
    parser.add_argument("--layer-b-log", type=Path, default=DEFAULT_LAYER_B_LOG)
    parser.add_argument("--layer-c-report", type=Path, default=DEFAULT_LAYER_C_REPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    layer_a_run = args.layer_a_run or find_latest_layer_a_run(DEFAULT_LAYER_A_RUNS)
    layer_a = parse_layer_a_summary(layer_a_run / "summary.txt") if layer_a_run else None
    layer_b_text, layer_b_json = run_layer_b(args.layer_b_log)
    layer_c = parse_layer_c_report(args.layer_c_report)

    now_iso = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    header = (
        f"# Phase 11 combined report\n\n"
        f"Generated: {now_iso}\n"
        f"Skill: trainer\n"
        f"Skill root: `{SKILL_ROOT}`\n\n"
    )
    verdict_section, exit_code = render_verdict(layer_a, layer_c)
    body = "\n".join(
        [
            header,
            render_layer_a(layer_a_run, layer_a),
            render_layer_b(layer_b_text, layer_b_json),
            render_layer_c(layer_c),
            verdict_section,
        ]
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body)
    print(f"wrote {args.out}", file=sys.stderr)
    if args.stdout:
        sys.stdout.write(body)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
