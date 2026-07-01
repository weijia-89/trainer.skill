#!/usr/bin/env python3
"""mutation_test_skill.py: Phase 11 Layer C for trainer.skill.

Drops one SKILL.md level-2 section at a time, runs the scenario suite via
scripts/run.sh --skill-file <mutant>, and reports a load-bearing heat map.
Prod SKILL.md is never touched (mutants live under /tmp). RULE #4 re-checked.

Tiny-N caution: at k and scenario counts this small, only a drop that flips a
scenario to a hard FAIL is reported load-bearing. Sub-threshold pass-rate
deltas are within the run-noise band and are NOT labeled load-bearing.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "SKILL.md"
MUT_DIR = Path("/tmp/skill-mutation-test")
NOISE_BAND_NOTE = (
    "NOTE: at trainer N, only section drops that flip a scenario to hard FAIL "
    "are load-bearing; sub-threshold pass-rate deltas are within run-noise."
)


def sections(text: str) -> list[tuple[str, int, int]]:
    idxs = [m.start() for m in re.finditer(r"(?m)^##\s+.+$", text)]
    out = []
    for i, start in enumerate(idxs):
        end = idxs[i + 1] if i + 1 < len(idxs) else len(text)
        header = text[start : text.index("\n", start)]
        out.append((header.strip(), start, end))
    return out


def run_suite(skill_file: Path, run_dir: Path) -> int:
    return subprocess.run(
        [
            "bash",
            str(REPO / "scripts" / "run.sh"),
            "--offline",
            "--k",
            "3",
            "--skill-file",
            str(skill_file),
            "--run-dir",
            str(run_dir),
        ],
    ).returncode


def main() -> int:
    MUT_DIR.mkdir(parents=True, exist_ok=True)
    text = SKILL.read_text()
    base_rc = run_suite(SKILL, MUT_DIR / "baseline")
    report = [
        "# Layer C mutation heat map",
        "",
        NOISE_BAND_NOTE,
        "",
        f"baseline suite rc={base_rc}",
        "",
        "| dropped section | suite rc | load-bearing? |",
        "|---|---|---|",
    ]
    for header, start, end in sections(text):
        mutant = MUT_DIR / (re.sub(r"\W+", "_", header)[:40] + ".md")
        mutant.write_text(text[:start] + text[end:])
        rc = run_suite(mutant, MUT_DIR / ("run_" + mutant.stem))
        lb = "yes (flipped to FAIL)" if rc != base_rc else "no (within noise)"
        report.append(f"| {header} | {rc} | {lb} |")
    (MUT_DIR / "mutation_report.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
