---
name: smoke_real_project
version: 2.0.0
parent_skill: form-check
status: integration smoke spec
---

# Integration smoke test — manual

A real-project smoke test for the skills. Manual rather than automated because:
- Skill exercise is agent-driven; harness state is hard to reproduce headlessly.
- Expected output is qualitative (a review report), not a checksum.
- Maintaining headless harness fixtures over time is high-tax.

## Procedure

### Prerequisites

- A small open-source project locally available. Recommended: any 100–1000-LOC project from your own portfolio with documented architecture.
- Agent harness with both `form-check.skill` and `recovery.skill` loaded.

### Run

1. Invoke `apply recovery on /path/to/project --engagement-type harden`.
2. Watch the agent walk: discovery → review → scoring → doc-pass → deAI-sweep → adversarial (if needed) → launch-ready → summary.
3. Verify each phase emits an expected artifact under `.recovery/`.

### Acceptance criteria

- [ ] `.recovery/discovery.md` lists language, frameworks, top-level dirs.
- [ ] `.recovery/review.md` contains P0/P1/P2 findings with file:line + severity + reproduction + fix.
- [ ] `.recovery/scoring.md` contains per-change rows with 9 component scores + tier verdict.
- [ ] `.recovery/calibration.jsonl` accumulates one row per scored change.
- [ ] `.recovery/doc_pass.md` enumerates docs created or updated.
- [ ] `.recovery/deai_sweep.md` lists per-archetype overlay results (zero base banned-vocab hits in user-facing docs after sweep).
- [ ] `.recovery/adversarial.md` (if invoked) contains 12 questions with verdict per.
- [ ] `.recovery/launch_ready.md` walks all 11 sections of the DoD with pass/fail/n-a-with-reason.
- [ ] `.recovery/summary.md` is one page (≤500 words), human-readable, with engagement-aggregate score and tier verdict.
- [ ] `.recovery/state.jsonl` has one row per phase + one final-verdict row.

### Re-run idempotency

1. Run `apply recovery` a second time on the same project without changes.
2. Acceptance: all phases skip with "completed-prior; no input change" verdicts in `state.jsonl`.

### Force re-run

1. Run `apply recovery --rerun=review,scoring`.
2. Acceptance: only those two phases re-execute; downstream phases re-run as appropriate per DAG predicates.

### Abort protocol

1. During an active engagement, signal abort (host-specific; e.g. SIGINT, "stop" message, browser close).
2. Acceptance: `.recovery/abort-<ts>/summary.md` exists with phases-completed / phases-skipped / next-steps.

## What this smoke test catches

- Workflow-DAG drift between docs and runtime
- Phase prompts that hardcode paths
- State-jsonl schema regressions
- Voice-rule overlay misapplication
- Scale-up content rendered without forcing-constraint check

## What it doesn't catch

- Subtle bug-class lens omissions (covered by per-checklist self-tests)
- Mutation-score tooling regressions (host-specific; out of skill scope)
- Citation drift (covered by `test_citations.py`)
- Cross-language tooling edge cases (covered by per-language file)

## Cadence

Run before each MAJOR or MINOR release of either skill. PATCH releases may skip.
