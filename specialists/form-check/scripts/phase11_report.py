#!/usr/bin/env python3
"""
Phase 11 combined report: aggregates Layer A (scenario suite), Layer B
(calibration log analyzer), and Layer C (mutation testing) into a single
markdown dashboard.

Defaults pull the latest artifacts from their standard locations. All
inputs are overridable so the report can be rebuilt for a specific run.

Usage:
    python3 scripts/phase11_report.py
    python3 scripts/phase11_report.py --layer-a-run tests/pressure_scenarios/runs/20260516T220836Z-SELF
    python3 scripts/phase11_report.py --layer-c-report /tmp/skill-mutation-test/mutation_report.md
    python3 scripts/phase11_report.py --out /tmp/phase11_combined.md

Exit codes:
    0  report written successfully (no judgment of pass/fail; that lives
       inside each layer)
    1  required input missing and not overridable
    2  one or more layers reported FAIL conditions worth surfacing in the
       process exit code (Layer A failures or Layer C zero-load-bearing
       sections)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
DEFAULT_LAYER_A_RUNS = SKILL_ROOT / "tests" / "pressure_scenarios" / "runs"
DEFAULT_LAYER_B_LOG = SKILL_ROOT / ".recovery" / "calibration.jsonl"
DEFAULT_LAYER_C_REPORT = Path("/tmp/skill-mutation-test/mutation_report.md")
DEFAULT_OUT = SKILL_ROOT / "tests" / "pressure_scenarios" / "phase11_report.md"


def find_latest_layer_a_run(runs_dir: Path) -> Path | None:
    if not runs_dir.is_dir():
        return None
    candidates = [p for p in runs_dir.iterdir() if p.is_dir() and (p / "summary.txt").is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.name)


def parse_layer_a_summary(summary_path: Path) -> dict:
    """Read summary.txt; count PASS/FAIL/SKIP per category and overall."""
    lines = summary_path.read_text().splitlines()
    result: dict = {
        "total": 0,
        "pass": 0,
        "fail": 0,
        "skip": 0,
        "by_category": {},
        "failures": [],
    }
    current_failure_scenario = None
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r"^(PASS|FAIL|SKIP)\s+(\S+)", line)
        if m:
            verdict, scenario = m.group(1), m.group(2)
            category = scenario.split("/", 1)[0] if "/" in scenario else "(uncategorized)"
            result["total"] += 1
            result[verdict.lower()] += 1
            cat = result["by_category"].setdefault(category, {"pass": 0, "fail": 0, "skip": 0})
            cat[verdict.lower()] += 1
            current_failure_scenario = scenario if verdict == "FAIL" else None
            continue
        if current_failure_scenario and line.lstrip().startswith("FAIL"):
            result["failures"].append({"scenario": current_failure_scenario, "reason": line.strip()})
            current_failure_scenario = None
    return result


def run_layer_b(log_path: Path) -> tuple[str, dict]:
    """Run calibration_analyze.py against log_path; capture text + JSON."""
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
    """Pull headline counts from a Layer C mutation report markdown file."""
    out: dict = {"raw": "", "mutants": 0, "load_bearing": 0, "weight_zero": 0}
    if not report_path.is_file():
        return out
    out["raw"] = report_path.read_text()
    # Heuristic header parsing; tolerate minor format drift.
    m = re.search(r"mutants?\s*:\s*(\d+)", out["raw"], re.IGNORECASE)
    if m:
        out["mutants"] = int(m.group(1))
    m = re.search(r"load.?bearing\s*:\s*(\d+)", out["raw"], re.IGNORECASE)
    if m:
        out["load_bearing"] = int(m.group(1))
    m = re.search(r"(weight.?zero|non.?load.?bearing)\s*:\s*(\d+)", out["raw"], re.IGNORECASE)
    if m:
        out["weight_zero"] = int(m.group(2))
    return out


def render_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_layer_a(layer_a_run: Path | None, layer_a: dict | None) -> str:
    if not layer_a_run or not layer_a:
        return "## Layer A: scenario suite\n\nNo run found. Execute `tests/pressure_scenarios/run.sh` first.\n"
    parts = [
        "## Layer A: scenario suite",
        "",
        f"Run: `{layer_a_run.name}`",
        f"Path: `{layer_a_run}`",
        "",
        f"**Totals**: {layer_a['total']} scenarios, "
        f"{layer_a['pass']} PASS, {layer_a['fail']} FAIL, {layer_a['skip']} SKIP.",
        "",
        "### By category",
        "",
    ]
    rows = []
    for cat, counts in sorted(layer_a["by_category"].items()):
        total = counts["pass"] + counts["fail"] + counts["skip"]
        pct = (counts["pass"] / total * 100.0) if total else 0.0
        rows.append([cat, str(counts["pass"]), str(counts["fail"]), str(counts["skip"]), f"{pct:.0f}%"])
    parts.append(render_table(["category", "pass", "fail", "skip", "pass rate"], rows))
    parts.append("")
    if layer_a["failures"]:
        parts.append("### Failures")
        parts.append("")
        for f in layer_a["failures"]:
            parts.append(f"- `{f['scenario']}` {f['reason']}")
        parts.append("")
    return "\n".join(parts)


def render_layer_b(layer_b_text: str, layer_b_json: dict) -> str:
    parts = ["## Layer B: calibration log analyzer", ""]
    if not layer_b_text or layer_b_text.startswith("calibration_analyze.py not found"):
        parts.append("Layer B analyzer not available or produced no output.")
        parts.append("")
        return "\n".join(parts)
    parts.append("```")
    parts.append(layer_b_text.rstrip())
    parts.append("```")
    parts.append("")
    if layer_b_json:
        n = layer_b_json.get("n_events", 0)
        if n > 0:
            parts.append(f"Total events: {n}.")
        else:
            parts.append("Log empty; no calibration data yet.")
        parts.append("")
    return "\n".join(parts)


def render_layer_c(layer_c: dict) -> str:
    parts = ["## Layer C: mutation testing", ""]
    if not layer_c.get("raw"):
        parts.append("No mutation report found. Execute `scripts/mutation_test_skill.py`.")
        parts.append("")
        return "\n".join(parts)
    if layer_c.get("mutants"):
        parts.append(
            f"Mutants run: **{layer_c['mutants']}**. "
            f"Load-bearing: **{layer_c['load_bearing']}**. "
            f"Weight-zero: **{layer_c['weight_zero']}**."
        )
        parts.append("")
    parts.append("### Full mutation report")
    parts.append("")
    parts.append("```markdown")
    parts.append(layer_c["raw"].rstrip())
    parts.append("```")
    parts.append("")
    return "\n".join(parts)


def render_verdict(layer_a: dict | None, layer_c: dict) -> tuple[str, int]:
    notes = []
    exit_code = 0
    if layer_a:
        if layer_a["fail"] > 0:
            notes.append(f"Layer A: {layer_a['fail']} scenario(s) FAIL.")
            exit_code = 2
        else:
            notes.append("Layer A: all scenarios PASS.")
    else:
        notes.append("Layer A: no run available.")
    if layer_c.get("raw"):
        if layer_c.get("weight_zero", 0) > 0:
            notes.append(
                f"Layer C: {layer_c['weight_zero']} weight-zero section(s) detected. "
                "Skill text in those sections may not be load-bearing."
            )
            exit_code = max(exit_code, 2)
        elif layer_c.get("load_bearing", 0) > 0:
            notes.append(f"Layer C: {layer_c['load_bearing']} load-bearing mutant(s).")
        else:
            notes.append("Layer C: report present but counts could not be parsed.")
    else:
        notes.append("Layer C: no mutation report available.")
    body = "\n".join(f"- {n}" for n in notes)
    return f"## Verdict\n\n{body}\n", exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--layer-a-run", type=Path, help="path to a specific Layer A run dir (default: latest under runs/)")
    parser.add_argument("--layer-b-log", type=Path, default=DEFAULT_LAYER_B_LOG, help="path to calibration.jsonl")
    parser.add_argument("--layer-c-report", type=Path, default=DEFAULT_LAYER_C_REPORT, help="path to mutation_report.md")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output markdown path")
    parser.add_argument("--stdout", action="store_true", help="also write report to stdout")
    args = parser.parse_args()

    layer_a_run = args.layer_a_run or find_latest_layer_a_run(DEFAULT_LAYER_A_RUNS)
    layer_a = parse_layer_a_summary(layer_a_run / "summary.txt") if layer_a_run else None

    layer_b_text, layer_b_json = run_layer_b(args.layer_b_log)

    layer_c = parse_layer_c_report(args.layer_c_report)

    now_iso = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    header = (
        f"# Phase 11 combined report\n\n"
        f"Generated: {now_iso}\n"
        f"Skill: form-check\n"
        f"Skill root: `{SKILL_ROOT}`\n\n"
        f"This report aggregates the three Phase 11 layers (scenario suite, "
        f"calibration log analyzer, mutation testing) into one view. Each layer "
        f"reports independently; the verdict at the bottom is a roll-up, not a "
        f"replacement for the per-layer detail.\n"
    )

    verdict_section, exit_code = render_verdict(layer_a, layer_c)

    body = "\n".join([
        header,
        render_layer_a(layer_a_run, layer_a),
        render_layer_b(layer_b_text, layer_b_json),
        render_layer_c(layer_c),
        verdict_section,
    ])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(body)
    print(f"wrote {args.out}", file=sys.stderr)
    if args.stdout:
        sys.stdout.write(body)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
