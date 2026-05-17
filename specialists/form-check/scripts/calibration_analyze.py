#!/usr/bin/env python3
"""
calibration_analyze.py — Phase 11 Layer B analyzer for calibration.jsonl.

Reads an append-only calibration log (default
form-check.skill/.recovery/calibration.jsonl) and produces a calibration
report with strict N-honesty discipline:

  N <  10  -> banner: (uncalibrated, N=<n>); refuses to draw any
              threshold-level conclusion. Only counts, distributions, and
              event-type summaries are emitted.
  N <  50  -> banner: [advisory] on every finding. Correlation /
              tier-rate findings are shown but explicitly labeled as
              advisory.
  N >= 50  -> banner: (calibrated, N=<n>). Threshold-rebalancing
              suggestions are produced.

This honesty contract mirrors the calibration-honesty block in
form-check.skill/SKILL.md Section 5. Layer B does NOT retroactively
legitimize the (uncalibrated) confidence-tier thresholds in SKILL.md;
it just supplies the data the calibration block already says we need.

Test isolation (RULE #4): this script accepts an explicit --log path.
Tests pass a copy under /tmp/, never the live .recovery/calibration.jsonl.

Usage:
    python3 scripts/calibration_analyze.py [--log PATH] [--format plain|json]
                                           [--out PATH] [--strict]

Exit codes:
    0  analysis emitted successfully
    1  malformed log line or other recoverable issue (logged to stderr)
    2  log file missing or unreadable
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# --- N-honesty thresholds (mirror SKILL.md Section 5) -------------------
UNCALIBRATED_MAX_N = 10  # N < 10 == uncalibrated
ADVISORY_MAX_N = 50      # 10 <= N < 50 == advisory; N >= 50 == calibrated

# Event types this analyzer recognizes; see .recovery/SCHEMA.md
KNOWN_EVENT_TYPES = {
    "score_event",
    "coached_override",
    "coaching_collapse",
    "routing_decision",
    "coached_override_revisit",
}

# Score component names from form-check.skill/templates/calibration_log_render.md
SCORE_COMPONENTS = (
    "code_read",
    "test",
    "hallucination",
    "bug_class",
    "adversarial",
    "reversibility",
    "doc",
    "blast_radius",
    "threat_model",
)

# Per-tier headline-score floors (operator-wisdom thresholds; never auto-changed)
TIER_FLOORS = {
    "vibe-dangerous": 95,
    "vibe-careful": 90,
    "vibe-safe": 80,
}


@dataclass
class CalibrationReport:
    log_path: Path
    total_lines: int = 0
    malformed_lines: int = 0
    by_event: Counter = field(default_factory=Counter)
    score_events: list[dict[str, Any]] = field(default_factory=list)
    override_events: list[dict[str, Any]] = field(default_factory=list)
    collapse_events: list[dict[str, Any]] = field(default_factory=list)
    routing_events: list[dict[str, Any]] = field(default_factory=list)
    revisit_events: list[dict[str, Any]] = field(default_factory=list)

    # Derived metrics (computed in finalize()).
    score_distribution: list[int] = field(default_factory=list)
    tier_counts: Counter = field(default_factory=Counter)
    tier_incident_counts: Counter = field(default_factory=Counter)
    component_corr: dict[str, float | None] = field(default_factory=dict)
    coaching_collapse_rate: float | None = None
    override_outcomes: Counter = field(default_factory=Counter)

    @property
    def n(self) -> int:
        """Calibration N is the count of score_events; the coaching-only
        events are not score evidence and are reported separately."""
        return len(self.score_events)

    @property
    def calibration_tier(self) -> str:
        if self.n < UNCALIBRATED_MAX_N:
            return "uncalibrated"
        if self.n < ADVISORY_MAX_N:
            return "advisory"
        return "calibrated"


def _parse_line(raw: str, lineno: int) -> dict[str, Any] | None:
    raw = raw.rstrip("\n")
    if not raw.strip():
        return None  # blank lines are skipped silently
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(
            f"WARN  line {lineno}: malformed JSON ({exc.msg}); skipped",
            file=sys.stderr,
        )
        return {"__malformed__": True}


def load_log(log_path: Path, strict: bool = False) -> CalibrationReport:
    """Stream the JSONL file once, bucket events by type, return a report."""
    if not log_path.exists():
        print(f"FAIL  log file not found: {log_path}", file=sys.stderr)
        sys.exit(2)
    if not log_path.is_file():
        print(f"FAIL  log path is not a regular file: {log_path}", file=sys.stderr)
        sys.exit(2)

    report = CalibrationReport(log_path=log_path)

    with log_path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            parsed = _parse_line(raw, lineno)
            if parsed is None:
                continue
            report.total_lines += 1
            if parsed.get("__malformed__"):
                report.malformed_lines += 1
                if strict:
                    print(
                        f"FAIL  strict mode: malformed line {lineno}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                continue

            event = parsed.get("event")
            # score_event records often omit "event" and rely on the schema in
            # calibration_log_render.md (which expects `score`, `tier`,
            # `components`). Detect by structure if "event" missing.
            if event is None and "score" in parsed and "components" in parsed:
                event = "score_event"

            if event not in KNOWN_EVENT_TYPES:
                print(
                    f"WARN  line {lineno}: unknown event type {event!r}; counted but not analyzed",
                    file=sys.stderr,
                )
                report.by_event[event or "<missing>"] += 1
                continue

            report.by_event[event] += 1
            if event == "score_event":
                report.score_events.append(parsed)
            elif event == "coached_override":
                report.override_events.append(parsed)
            elif event == "coaching_collapse":
                report.collapse_events.append(parsed)
            elif event == "routing_decision":
                report.routing_events.append(parsed)
            elif event == "coached_override_revisit":
                report.revisit_events.append(parsed)

    _finalize(report)
    return report


def _finalize(report: CalibrationReport) -> None:
    # Score distribution + tier counts + per-tier incident rates.
    for ev in report.score_events:
        score = ev.get("score")
        tier = ev.get("tier")
        incident = ev.get("incident")
        if isinstance(score, (int, float)):
            report.score_distribution.append(int(score))
        if isinstance(tier, str):
            report.tier_counts[tier] += 1
            if incident is not None:
                report.tier_incident_counts[tier] += 1

    # Per-component correlation with incident (Pearson, point-biserial style).
    # Only meaningful at N >= UNCALIBRATED_MAX_N; we compute either way and let
    # the rendering layer apply the N-honesty banner.
    for comp in SCORE_COMPONENTS:
        xs: list[float] = []
        ys: list[float] = []
        for ev in report.score_events:
            comp_val = ev.get("components", {}).get(comp)
            if not isinstance(comp_val, (int, float)):
                continue
            xs.append(float(comp_val))
            # y = 1 if incident occurred, else 0
            ys.append(1.0 if ev.get("incident") is not None else 0.0)
        report.component_corr[comp] = _pearson(xs, ys)

    # Coaching-collapse rate: collapses / (collapses + override events). High
    # rate means the trainer is failing to push back, often.
    denom = len(report.collapse_events) + len(report.override_events)
    if denom > 0:
        report.coaching_collapse_rate = len(report.collapse_events) / denom

    # Override outcomes from revisit events.
    for ev in report.revisit_events:
        outcome = ev.get("outcome")
        if isinstance(outcome, str):
            report.override_outcomes[outcome] += 1


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


# ---------------- Rendering -----------------------------------------------


def render_plain(report: CalibrationReport) -> str:
    out: list[str] = []
    tier = report.calibration_tier
    if tier == "uncalibrated":
        banner = f"(uncalibrated, N={report.n}; threshold conclusions refused)"
    elif tier == "advisory":
        banner = f"[advisory, N={report.n}; findings below are advisory only]"
    else:
        banner = f"(calibrated, N={report.n})"

    out.append(f"# calibration report -- {banner}")
    out.append("")
    out.append(f"log file:        {report.log_path}")
    out.append(f"total lines:     {report.total_lines}")
    out.append(f"malformed lines: {report.malformed_lines}")
    out.append("")
    out.append("## event counts")
    if not report.by_event:
        out.append("  (no events)")
    else:
        for evt, cnt in report.by_event.most_common():
            out.append(f"  {evt:35s} {cnt}")
    out.append("")

    out.append("## score events (Layer B headline metric)")
    if report.n == 0:
        out.append("  (no score events to summarize)")
    else:
        scores = sorted(report.score_distribution)
        out.append(f"  N             {report.n}")
        out.append(f"  min / max     {scores[0]} / {scores[-1]}")
        out.append(f"  median        {_median(scores)}")
        out.append(f"  mean          {sum(scores)/len(scores):.2f}")
        out.append("")
        out.append("  by tier:")
        for t, c in sorted(report.tier_counts.items()):
            inc = report.tier_incident_counts.get(t, 0)
            rate = (inc / c) if c else 0.0
            floor = TIER_FLOORS.get(t, "n/a")
            label = (
                ""
                if tier == "uncalibrated"
                else f"  incident rate {rate:.1%}  floor={floor}"
            )
            out.append(f"    {t:18s} N={c:<4d}  incidents={inc:<4d}{label}")
    out.append("")

    out.append("## component-vs-incident correlation (point-biserial)")
    if tier == "uncalibrated":
        out.append("  refused: N below uncalibrated floor; correlation undefined as evidence")
    else:
        any_emitted = False
        for comp, corr in report.component_corr.items():
            if corr is None:
                continue
            label = "[advisory] " if tier == "advisory" else ""
            out.append(f"  {label}{comp:18s} r={corr:+.3f}")
            any_emitted = True
        if not any_emitted:
            out.append("  (no component data with sufficient variance)")
    out.append("")

    out.append("## coaching events (trainer-side discipline signal)")
    out.append(f"  overrides:  {len(report.override_events)}")
    out.append(f"  collapses:  {len(report.collapse_events)}")
    out.append(f"  routings:   {len(report.routing_events)}")
    out.append(f"  revisits:   {len(report.revisit_events)}")
    if report.coaching_collapse_rate is not None:
        out.append(
            f"  collapse rate (collapses / (collapses + overrides)): "
            f"{report.coaching_collapse_rate:.1%}"
        )
        if report.coaching_collapse_rate > 0.20:
            out.append(
                "  WARN  collapse rate > 20%: trainer SKILL.md may need tightening or "
                "pressure scenarios need adding."
            )
    if report.override_outcomes:
        out.append("  override outcomes (from revisit events):")
        for outcome, cnt in report.override_outcomes.most_common():
            out.append(f"    {outcome:30s} {cnt}")
    out.append("")

    out.append("## re-tiering suggestions")
    if tier != "calibrated":
        out.append("  refused: N below calibrated floor; thresholds remain operator-wisdom.")
    else:
        suggested = False
        for t, c in sorted(report.tier_counts.items()):
            inc = report.tier_incident_counts.get(t, 0)
            if c < 10:
                continue
            rate = inc / c
            floor = TIER_FLOORS.get(t)
            if floor is None:
                continue
            if rate > 0.10:
                suggested = True
                out.append(
                    f"  {t}: incident rate {rate:.1%} at floor={floor}; "
                    f"consider tightening to {floor + 2} (proposed; user reviews)."
                )
        if not suggested:
            out.append("  no re-tiering suggestions; tier floors look adequate.")

    out.append("")
    out.append("## honesty contract")
    if tier == "uncalibrated":
        out.append(
            "  This report is for inventory only. Per the calibration-honesty block in\n"
            "  form-check.skill/SKILL.md Section 5, threshold-level conclusions are not\n"
            "  drawn from N < 10. To exit uncalibrated, accumulate at least 10 score\n"
            "  events with shipped + incident outcomes recorded."
        )
    elif tier == "advisory":
        out.append(
            "  Findings are [advisory] only. To promote to calibrated, accumulate to\n"
            "  N >= 50 with incident-tagged outcomes; only then do re-tiering proposals\n"
            "  become quotable evidence."
        )
    else:
        out.append(
            "  Findings are calibrated. Re-tiering proposals are presented to the\n"
            "  user; the analyzer never auto-rewrites SKILL.md thresholds."
        )
    return "\n".join(out) + "\n"


def render_json(report: CalibrationReport) -> str:
    payload: dict[str, Any] = {
        "log_path": str(report.log_path),
        "total_lines": report.total_lines,
        "malformed_lines": report.malformed_lines,
        "calibration_tier": report.calibration_tier,
        "n": report.n,
        "by_event": dict(report.by_event),
        "score_events": {
            "min": min(report.score_distribution) if report.score_distribution else None,
            "max": max(report.score_distribution) if report.score_distribution else None,
            "median": _median(sorted(report.score_distribution)) if report.score_distribution else None,
            "mean": (
                sum(report.score_distribution) / len(report.score_distribution)
                if report.score_distribution
                else None
            ),
        },
        "tier_counts": dict(report.tier_counts),
        "tier_incident_counts": dict(report.tier_incident_counts),
        "component_corr": report.component_corr,
        "coaching": {
            "overrides": len(report.override_events),
            "collapses": len(report.collapse_events),
            "routings": len(report.routing_events),
            "revisits": len(report.revisit_events),
            "collapse_rate": report.coaching_collapse_rate,
            "override_outcomes": dict(report.override_outcomes),
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _median(sorted_xs: list[int]) -> float | None:
    if not sorted_xs:
        return None
    n = len(sorted_xs)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_xs[mid])
    return (sorted_xs[mid - 1] + sorted_xs[mid]) / 2


# ---------------- Entry point ---------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Phase 11 Layer B: calibration log analyzer (form-check)."
    )
    default_log = (
        Path(__file__).resolve().parent.parent / ".recovery" / "calibration.jsonl"
    )
    ap.add_argument(
        "--log",
        type=Path,
        default=default_log,
        help=f"path to calibration.jsonl (default: {default_log})",
    )
    ap.add_argument(
        "--format",
        choices=("plain", "json"),
        default="plain",
        help="output format (default: plain)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="optional output path; default: stdout",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit nonzero on any malformed log line (default: warn and skip)",
    )
    args = ap.parse_args()

    report = load_log(args.log, strict=args.strict)
    text = render_plain(report) if args.format == "plain" else render_json(report)

    if args.out is None:
        sys.stdout.write(text)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
