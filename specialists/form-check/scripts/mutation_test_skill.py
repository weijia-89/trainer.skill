#!/usr/bin/env python3
"""
mutation_test_skill.py -- Phase 11 Layer C driver.

Falsifies the operator-wisdom claim that specific sections of form-check
SKILL.md are load-bearing. The premise: if dropping a section does not
materially change the agent's pass rate on the Phase 11 scenario suite,
that section is not load-bearing. If dropping it DOES drop pass rate,
the original text was load-bearing and the magnitude of the drop is its
load-bearingness.

Procedure (per Phase 11 plan):
  1. Snapshot the production tree SHA (RULE #4 isolation).
  2. Read the production SKILL.md; parse into section blocks by '## '.
  3. Generate mutants by removing one section at a time. Each mutant is
     written to /tmp/skill-mutation-test/SKILL.md.mut-<N>. Production
     SKILL.md is NEVER modified.
  4. Run the baseline scenario suite once (production SKILL.md, all
     scenarios) and record per-category pass rates. This is the
     reference.
  5. For each mutant: run the scenario suite with --skill-file pointing
     at that mutant. Record per-category pass rates and the aggregate.
  6. Output a heat map: per section, the delta in pass rate between the
     mutant (section removed) and the baseline. Negative delta == the
     section is load-bearing; near-zero delta == not load-bearing.
  7. Re-check the production tree SHA. Any mutation fails the run.

Cost model (v0): the plan budgets 5 mutants x 30 scenarios x 3 runs =
~450 LLM calls per audit. This driver fires N (mutants+1) x S (scenarios)
calls, one run each. For form-check at v3.1.0 the run is N=5+1 x 34 =
204 calls, comfortably inside the v0 budget.

Offline mode (PHASE11_OFFLINE=1 / --offline): the driver runs end-to-end
against the deterministic stub adapter so the plumbing can be verified
without spending API tokens. Pass rates will all be 0% in offline mode
because the stub adapter returns dummy content; the load-bearing-ness
column is therefore noise. Only the structure check is meaningful.

Usage:
    python3 scripts/mutation_test_skill.py [--offline] [--mutants N]
                                           [--sections-only LIST]
                                           [--out /tmp/mutation-report.md]

Exit codes:
    0  report emitted successfully
    1  recoverable failure (e.g. mutant generation produced fewer than
       requested mutants); partial report emitted
    2  RULE #4 violation: production tree SHA changed across the run.
       Investigate immediately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

PROD_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = PROD_ROOT / "SKILL.md"
RUN_SH = PROD_ROOT / "tests" / "pressure_scenarios" / "run.sh"
MUTANT_ROOT = Path("/tmp/skill-mutation-test")
DEFAULT_REPORT = MUTANT_ROOT / "mutation_report.md"
DEFAULT_MAX_MUTANTS = 5


@dataclass
class Section:
    """A level-2 (##) section of SKILL.md identified by its heading line.

    The 'span' is the (start, end) line index range in the original file.
    """

    heading: str
    start: int  # inclusive line index where '## ...' lives
    end: int    # exclusive line index where the next section starts
    is_load_bearing_candidate: bool = True

    @property
    def slug(self) -> str:
        s = re.sub(r"[^a-z0-9]+", "_", self.heading.lower()).strip("_")
        return s[:60]


@dataclass
class RunResult:
    label: str  # 'baseline' or 'mut-<N>'
    skill_file: Path
    run_dir: Path
    total: int = 0
    passed: int = 0
    failed: int = 0
    per_category: dict[str, tuple[int, int]] = field(default_factory=dict)
    section_dropped: str | None = None  # which section was removed (mutants only)

    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total) if self.total else 0.0


# ---------------- Production-tree SHA snapshot (RULE #4) ---------------------

def snapshot_tree(prod_root: Path) -> dict[str, str]:
    """Return {relative_path: sha256} for every regular file under prod_root,
    excluding runs/ outputs and .git internals."""
    shas: dict[str, str] = {}
    for p in prod_root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(prod_root)
        rel_str = str(rel)
        if rel_str.startswith("tests/pressure_scenarios/runs/"):
            continue
        if rel_str.startswith(".git/"):
            continue
        with p.open("rb") as fh:
            shas[rel_str] = hashlib.sha256(fh.read()).hexdigest()
    return shas


def diff_shas(pre: dict[str, str], post: dict[str, str]) -> list[str]:
    added = sorted(set(post) - set(pre))
    removed = sorted(set(pre) - set(post))
    changed = sorted(p for p in pre.keys() & post.keys() if pre[p] != post[p])
    lines: list[str] = []
    for p in added:    lines.append(f"  ADDED    {p}")
    for p in removed:  lines.append(f"  REMOVED  {p}")
    for p in changed:  lines.append(f"  CHANGED  {p}")
    return lines


# ---------------- Section parsing -------------------------------------------

def parse_sections(skill_text: str) -> list[Section]:
    """Split a SKILL.md into level-2 (##) sections.

    Only '## ' at the start of a line is considered a section boundary; ###
    sub-headings stay inside their parent section. Sections before the first
    '## ' (e.g. YAML frontmatter and the title H1) are not mutated; we want
    structural mutations that target the operator-wisdom claims, not the
    frontmatter.
    """
    lines = skill_text.splitlines(keepends=True)
    sections: list[Section] = []
    starts: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("### "):
            heading = line[3:].strip()
            starts.append((i, heading))

    for j, (start, heading) in enumerate(starts):
        end = starts[j + 1][0] if j + 1 < len(starts) else len(lines)
        sections.append(Section(heading=heading, start=start, end=end))

    return sections


def generate_mutants(
    skill_text: str,
    sections: Sequence[Section],
    target_n: int,
    sections_only: list[str] | None = None,
) -> list[tuple[Section, str]]:
    """Return up to target_n (section_dropped, mutant_text) pairs.

    If sections_only is supplied, only sections whose slug appears in that
    list are mutated. Otherwise we pick the first target_n sections of the
    parsed list in source order, preferring sections plausibly load-bearing
    (the analyzer treats this as 'all are candidates' by default).
    """
    lines = skill_text.splitlines(keepends=True)
    picked = []
    for sec in sections:
        if sections_only is not None:
            if sec.slug not in sections_only and sec.heading not in sections_only:
                continue
        picked.append(sec)
        if len(picked) >= target_n:
            break

    mutants: list[tuple[Section, str]] = []
    for sec in picked:
        mut_lines = list(lines[: sec.start]) + list(lines[sec.end :])
        # Insert a stub note where the section used to live so an agent
        # reading the mutant cannot accidentally infer "the section is
        # genuinely supposed to be absent here". The stub makes mutation
        # detectable but does not restore the load-bearing content.
        stub = f"## {sec.heading}\n\n[mutation: section content removed for Layer C testing]\n\n"
        mut_text = "".join(mut_lines[: sec.start]) + stub + "".join(mut_lines[sec.start :])
        mutants.append((sec, mut_text))
    return mutants


# ---------------- Run-suite invocation --------------------------------------

def parse_results_jsonl(path: Path) -> tuple[int, int, int, dict[str, tuple[int, int]]]:
    """Return (total, passed, failed, per_category) from a results.jsonl."""
    total = passed = failed = 0
    per_cat_total: dict[str, int] = {}
    per_cat_pass: dict[str, int] = {}
    if not path.exists():
        return 0, 0, 0, {}
    with path.open("r") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            cat = ev.get("category") or ev.get("scenario", "?").split("/")[0]
            per_cat_total[cat] = per_cat_total.get(cat, 0) + 1
            if ev.get("verdict") == "PASS":
                passed += 1
                per_cat_pass[cat] = per_cat_pass.get(cat, 0) + 1
            else:
                failed += 1
    per_category = {
        cat: (per_cat_pass.get(cat, 0), per_cat_total[cat])
        for cat in per_cat_total
    }
    return total, passed, failed, per_category


def run_suite(
    label: str,
    skill_file: Path,
    run_dir: Path,
    offline: bool,
) -> RunResult:
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "bash",
        str(RUN_SH),
        "--skill-file", str(skill_file),
        "--run-dir",    str(run_dir),
    ]
    if offline:
        cmd.append("--offline")

    env = os.environ.copy()
    # Re-affirm PHASE11_OFFLINE for stub adapter (run.sh sets it too in --offline).
    if offline:
        env["PHASE11_OFFLINE"] = "1"

    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        print(f"  WARN  run.sh exited {result.returncode} for {label}", file=sys.stderr)
        print(f"        stderr: {result.stderr.strip()[:400]}", file=sys.stderr)

    total, passed, failed, per_cat = parse_results_jsonl(run_dir / "results.jsonl")
    return RunResult(
        label=label,
        skill_file=skill_file,
        run_dir=run_dir,
        total=total,
        passed=passed,
        failed=failed,
        per_category=per_cat,
    )


# ---------------- Report rendering ------------------------------------------

def render_report(
    baseline: RunResult,
    mutant_runs: list[RunResult],
    offline: bool,
) -> str:
    out: list[str] = []
    out.append("# Phase 11 Layer C -- load-bearing-ness heat map")
    out.append("")
    out.append(f"baseline skill file:   {baseline.skill_file}")
    out.append(f"baseline pass rate:    {baseline.passed}/{baseline.total} "
               f"({baseline.pass_rate:.1%})")
    out.append("")
    if offline:
        out.append(
            "**MODE: OFFLINE.** All scenarios will fail because the stub adapter "
            "returns dummy content. This report validates the plumbing, not the "
            "load-bearing-ness of any section. Re-run with `ANTHROPIC_API_KEY` "
            "set (and without `--offline`) for a real heat map."
        )
        out.append("")

    out.append("## per-mutant pass rate vs baseline")
    out.append("")
    header = (
        "| mutant | section dropped | passed | total | pass rate | delta vs baseline |"
    )
    out.append(header)
    out.append("|---|---|---|---|---|---|")

    for r in mutant_runs:
        delta = r.pass_rate - baseline.pass_rate
        sign = "+" if delta >= 0 else ""
        out.append(
            f"| {r.label} | `{r.section_dropped}` | {r.passed} | {r.total} | "
            f"{r.pass_rate:.1%} | {sign}{delta:.1%} |"
        )
    out.append("")

    out.append("## interpretation")
    out.append("")
    if offline:
        out.append(
            "Offline-mode results are not informative; rerun live before drawing\n"
            "load-bearing-ness conclusions about any section."
        )
    else:
        # Classify each mutant
        load_bearing: list[RunResult] = []
        neutral: list[RunResult] = []
        for r in mutant_runs:
            delta = r.pass_rate - baseline.pass_rate
            if delta <= -0.10:  # 10 percentage points drop
                load_bearing.append(r)
            else:
                neutral.append(r)
        if load_bearing:
            out.append("Sections that appear LOAD-BEARING (>10pp drop when removed):")
            for r in load_bearing:
                d = r.pass_rate - baseline.pass_rate
                out.append(f"  - `{r.section_dropped}` ({d:+.1%})")
            out.append("")
        if neutral:
            out.append("Sections that appear NOT load-bearing (<=10pp delta):")
            for r in neutral:
                d = r.pass_rate - baseline.pass_rate
                out.append(f"  - `{r.section_dropped}` ({d:+.1%})")
            out.append("")
        if not load_bearing:
            out.append(
                "Note: no section drop produced a >10pp pass-rate decline. Either\n"
                "(a) the scenario suite is too lenient to discriminate, or (b) the\n"
                "skill text is mostly redundant under this LLM. Investigate before\n"
                "trimming."
            )

    out.append("")
    out.append("## per-category breakdown")
    out.append("")
    cats = sorted({c for r in [baseline, *mutant_runs] for c in r.per_category.keys()})
    header2 = "| category | baseline | " + " | ".join(r.label for r in mutant_runs) + " |"
    out.append(header2)
    out.append("|---|---|" + "|".join("---" for _ in mutant_runs) + "|")
    for cat in cats:
        b_p, b_t = baseline.per_category.get(cat, (0, 0))
        b_str = f"{b_p}/{b_t}" if b_t else "0/0"
        cells = []
        for r in mutant_runs:
            p, t = r.per_category.get(cat, (0, 0))
            cells.append(f"{p}/{t}" if t else "0/0")
        out.append(f"| {cat} | {b_str} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("## honesty contract")
    out.append("")
    out.append(
        "This is a falsifiability harness, not a randomized controlled trial.\n"
        "Pass-rate deltas reflect (a) the model under test, (b) the scenario\n"
        "set, and (c) the specific mutation strategy chosen by the generator.\n"
        "A section that survives one mutation cycle is not proven load-bearing;\n"
        "it is just not yet falsified. Run across multiple models and multiple\n"
        "scenario-paraphrasings before drawing portable conclusions."
    )
    return "\n".join(out) + "\n"


# ---------------- Entry point -----------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Phase 11 Layer C: mutation testing of skill text."
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="run the stub adapter; smoke-tests plumbing without LLM cost",
    )
    ap.add_argument(
        "--mutants",
        type=int,
        default=DEFAULT_MAX_MUTANTS,
        help=f"max number of mutants to generate (default {DEFAULT_MAX_MUTANTS})",
    )
    ap.add_argument(
        "--sections-only",
        type=str,
        default=None,
        help="comma-separated list of section slugs or headings to mutate (default: first --mutants sections)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"output report path (default {DEFAULT_REPORT})",
    )
    ap.add_argument(
        "--skip-baseline",
        action="store_true",
        help="skip the baseline run; only generate mutants and write fixtures",
    )
    args = ap.parse_args()

    # RULE #4: snapshot before any work.
    pre_shas = snapshot_tree(PROD_ROOT)

    if not SKILL_PATH.exists():
        print(f"FAIL  expected SKILL.md at {SKILL_PATH}", file=sys.stderr)
        return 2

    # Prepare mutant root (always /tmp/, never production).
    if MUTANT_ROOT.exists():
        shutil.rmtree(MUTANT_ROOT)
    MUTANT_ROOT.mkdir(parents=True)

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    sections = parse_sections(skill_text)
    print(f"  parsed {len(sections)} level-2 sections from SKILL.md", file=sys.stderr)
    for s in sections:
        print(f"    -- {s.slug:50s} (lines {s.start}..{s.end})", file=sys.stderr)

    sections_only_list: list[str] | None = None
    if args.sections_only:
        sections_only_list = [s.strip() for s in args.sections_only.split(",") if s.strip()]

    mutants = generate_mutants(
        skill_text=skill_text,
        sections=sections,
        target_n=args.mutants,
        sections_only=sections_only_list,
    )
    if not mutants:
        print("FAIL  no mutants produced; check --sections-only filter", file=sys.stderr)
        return 1

    # Write mutants to disk (always under MUTANT_ROOT).
    for i, (sec, text) in enumerate(mutants, start=1):
        mutant_path = MUTANT_ROOT / f"SKILL.md.mut-{i}"
        mutant_path.write_text(text, encoding="utf-8")
        meta = MUTANT_ROOT / f"SKILL.md.mut-{i}.meta.json"
        meta.write_text(
            json.dumps(
                {
                    "mutant_id": i,
                    "section_slug": sec.slug,
                    "section_heading": sec.heading,
                    "section_lines": [sec.start, sec.end],
                },
                indent=2,
            )
            + "\n"
        )
        print(f"  wrote {mutant_path.name} (dropped: {sec.heading!r})", file=sys.stderr)

    runs: list[RunResult] = []
    baseline_result: RunResult | None = None

    if not args.skip_baseline:
        print("\n[baseline] running scenario suite against production SKILL.md", file=sys.stderr)
        baseline_result = run_suite(
            label="baseline",
            skill_file=SKILL_PATH,
            run_dir=MUTANT_ROOT / "run-baseline",
            offline=args.offline,
        )
        print(
            f"[baseline] {baseline_result.passed}/{baseline_result.total} PASS "
            f"({baseline_result.pass_rate:.1%})",
            file=sys.stderr,
        )

    for i, (sec, _text) in enumerate(mutants, start=1):
        label = f"mut-{i}"
        print(f"\n[{label}] running scenario suite without {sec.heading!r}", file=sys.stderr)
        r = run_suite(
            label=label,
            skill_file=MUTANT_ROOT / f"SKILL.md.mut-{i}",
            run_dir=MUTANT_ROOT / f"run-{label}",
            offline=args.offline,
        )
        r.section_dropped = sec.heading
        runs.append(r)
        print(f"[{label}] {r.passed}/{r.total} PASS ({r.pass_rate:.1%})", file=sys.stderr)

    # RULE #4: re-snapshot and compare.
    post_shas = snapshot_tree(PROD_ROOT)
    if pre_shas != post_shas:
        diff_lines = diff_shas(pre_shas, post_shas)
        print("FAIL  RULE #4 VIOLATION: production tree changed during run!", file=sys.stderr)
        for line in diff_lines:
            print(line, file=sys.stderr)
        # Still write the report so the test trail is preserved.
        if baseline_result is not None:
            text = render_report(baseline_result, runs, offline=args.offline)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text)
        return 2

    if baseline_result is None:
        # --skip-baseline: emit a minimal note so the human knows the run was partial.
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            "# Phase 11 Layer C -- mutants generated (baseline skipped)\n\n"
            f"{len(runs)} mutant scenario runs completed. Re-run without "
            "--skip-baseline for the heat map.\n"
        )
        print(f"\nWrote partial report -> {args.out}", file=sys.stderr)
        return 0

    text = render_report(baseline_result, runs, offline=args.offline)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(f"\nWrote report -> {args.out}", file=sys.stderr)
    print("PASS  production tree byte-identical before and after run (RULE #4 satisfied)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
