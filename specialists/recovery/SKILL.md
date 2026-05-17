---
name: recovery
description: |
  Use when running a multi-day quality engagement on a whole project, vibe-coded to shippable, hardening before launch, end-to-end review with scorecard. Symptoms: project that "needs hardening," launch-ready check, full engagement vs single PR review.
type: project-skill
version: 3.0.0
authors: Wei Jia (1.0, 2026-04); rewrite 2026-05-14; v3 Iron Law layering + composes-pin to form-check@>=3 2026-05-16
license: MIT
required_tools: [file_read, grep]
recommended_tools: [shell, git, web_search]
optional_tools: [browser]
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    pinned_components:
      - rubrics/confidence_score.md@3.0.0
      - rubrics/vibe_safety_map.md@2.0.0
      - checklists/INDEX.md@2.0.0
      - references/notes.md@3.0.0
---

# recovery, vibe-coded → shippable; the conditioning back to form

```
IRON LAW: NO LAUNCH-READY VERDICT WITHOUT TIER-FLOOR MET *AND* `.recovery/state.jsonl` COMPLETE.
```

Violating the letter of this rule is violating the spirit of this rule. "Mostly launch-ready, just one phase short" is not launch-ready. The state.jsonl entries and the tier-floor are independent gates; both must pass. **Below `form-check`'s calibration N=10, the engagement renders `advisory` only, not launch-ready** (per `form-check §5` honest-precision warning).

## Red Flags. STOP

- "We're at engagement-end and one phase didn't run, but we're close enough."
- "Tier-floor isn't met but the team needs to ship Friday."
- "I'll skip the deAI sweep, docs are internal-only."
- "The adversarial 12 questions are overkill for this engagement."
- "Re-running recovery on the same project produces different results, that's fine."
- "Voice integrity is voice rules, not engineering, drop the sweep."

Each red flag means: stop. State.jsonl + tier-floor + deAI sweep + adversarial review. All four. No exceptions.

## Rationalizations, what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "We need to ship Friday, launch-ready can be advisory" | Then declare `advisory`, not `launch-ready`. The verdict is structured; do not blur it. |
| "The 12 adversarial questions are repetitive" | They are axis-segmented for a reason. Skipping any axis is a coverage gap that incident reports later confirm. |
| "Idempotent re-runs are nice-to-have" | Idempotency is the test that the engagement state is captured, not in your head. If re-runs differ, the engagement isn't done. |
| "Doc-pass is doc-pass, not engineering" | Per `KIRSCHNER-SWELLER-CLARK-2006`, structured documentation reduces cognitive load for downstream learners; for AI agents, it's the spec the agent reads. The doc-pass is engineering. |
| "Calibration N is < 50, the score is approximate, so accept advisory as launch-ready" | No. Below N=10 it is *not* a numeric verdict at all. Until you've run 10 engagements and logged outcomes, do not gate on the headline. |

## Keywords for discovery

For trigger-keyword indexing: recovery, harden this, vibe-coded to shippable, ship it review, launch ready, prepare for prod, end-to-end review, full engagement, doc pass + scorecard, harden + ship.

## Scope

This is a *full-project quality engagement*, not a single-bug fix. "Fixer" reads as one-issue-at-a-time, but the actual scope is multi-day: discovery → review → scoring → doc-pass → deAI-sweep → launch-ready → summary. If you want to fix one specific issue or score one specific PR, use `form-check` directly, it's the cheaper invocation.

Posture: take a project (vibe-coded or greenfield) from "needs hardening" to shippable. Compose `form-check` (review/scoring) with a deAI sweep (voice cleanup) under a single DAG workflow. Same posture-adaptive rules: default-anti-enterprise, scale-up annex behind forcing-constraint ADR.

This skill is **not a code generator**. It guides agents through an opinionated engagement; it does not write feature code on its own.

## How to invoke

`apply recovery on /path/to/project [--engagement-type {harden|new-app|review|deprecate}]`

Default engagement type: `harden`. The skill discovers, reviews, scores, doc-passes, deAI-sweeps, declares launch-ready (or escalates a gap report), and writes a one-page summary.

## Section 1. DAG workflow (single source of truth)

Canonical workflow lives in `workflow/workflow_dag.md`. Phases:

```
discovery ─┐
           ├─→ scoring ─→ doc-pass ─→ deAI-sweep ─→ launch-ready ─→ summary
review ────┘                                       ↑
                                                   └── adversarial (loops if score < tier-floor)
```

Activation criteria per phase (full set in `workflow/workflow_dag.md`):
- **discovery**: always
- **review**: if existing code path provided
- **scoring**: always (requires review or planning artifact)
- **doc-pass**: if writes_code OR writes_docs
- **deAI-sweep**: if writes_docs
- **adversarial**: if confidence < tier_threshold (loops up to 2; then escalate)
- **launch-ready**: if engagement_type == "harden"
- **summary**: always

Each phase emits one artifact and one structured-verdict JSON entry to `.recovery/state.jsonl`. Re-running `recovery` skips completed phases (idempotency-by-state).

## Section 2. Composition with form-check

`recovery` does **not** duplicate `form-check`'s rubrics or checklists. It pins a version range (frontmatter `composes`) and references files by path. If `form-check`'s pinned components change MAJOR version, `recovery`'s self-test fails (`tests/test_skill_version_compat.py`).

What `recovery` adds beyond `form-check`:
- The DAG workflow itself (`workflow/workflow_dag.md`)
- Engagement-level confidence rubric (composes form-check rubric + per-phase weights) (`rubrics/code_fixer_confidence.md`)
- Voice-segregated deAI rules per archetype (`templates/deai_rules.md`, `templates/doc_voice.md`)
- 12 axis-segmented adversarial questions (`workflow/adversarial_questions.md`)
- Engagement-launch-ready DoD (`checklists/launch_ready.md`)
- Phase prompts (env-agnostic, parameterized output paths) (`workflow/phase_prompts.md`)
- Full engagement trace example (`examples/full-engagement-trace.md`)

## Section 3. Engagement-level confidence rubric

Inherits all 9 components from `form-check` (rubrics/confidence_score.md). Adds 2 engagement-specific:

| # | Component | Weight | Full credit |
|---|---|---|---|
| 10 | Workflow completeness | 7 | every required phase ran; verdicts logged to `.recovery/state.jsonl`; abort protocol available |
| 11 | Voice integrity | 3 | deAI-sweep clean across docs (no banned vocab outside `references/`/`examples/`); per-archetype overlay applied |

Inherited components are rebalanced **0.9× from `form-check`** (sum=90); add 7+3=10 → **100 total**. Tier thresholds inherited from `form-check`. See `rubrics/code_fixer_confidence.md` for the full table, per-component minima, and worked examples.

## Section 4. Posture rules (engagement-level)

- **Engagement output is structured**: every phase emits `.recovery/state.jsonl` row; final summary is human-readable + machine-parseable verdict.
- **Idempotent re-runs**: `recovery` on the same project twice produces identical DAG state if no inputs changed.
- **Abort protocol** (`Section 9`): explicit clean exit on user signal or scope mismatch.
- **Multi-language**: `recovery` does not assume a stack. Each phase consults `form-check.skill/multi-language/matrix.md` to pick tooling.
- **Posture-adaptive**: scale-up content reachable only via `form-check.skill/scale-up/when_to_activate.md` gate.

## Section 5. Refusal list

Refuse to:
- Run `recovery` on a project where the user has not granted file-write authority (degrade to advisory mode).
- Skip the deAI sweep on docs that will be published.
- Mark launch-ready when `form-check`'s tier-floor is unmet.
- Rewrite source files based on adversarial-review findings without `vibe-dangerous` per-component minima met.

## Section 6. Adversarial review (12 axis-segmented questions)

Run all 12 (`workflow/adversarial_questions.md`):
1. Severity inflation
2. Coverage gap
3. Reversibility
4. Score gaming
5. Month-3 projection
6. Threat model (STRIDE + applicable OWASP Top 10)
7. Blast radius
8. Hallucination integrity
9. Fitness functions
10. Accessibility
11. Privacy / LINDDUN
12. Agent self-attack (prompt injection in inputs?)

Each must produce a verdict (`pass`, `fail`, `n/a-with-reason`).

## Section 7. Voice and docs

Per-archetype voice rules (`templates/doc_voice.md`):

| Archetype | Voice | Docstring rule |
|---|---|---|
| API reference | impersonal, descriptive | uniform shape required (Sphinx/typedoc/JSDoc compat) |
| README | conversational, archetype-driven | n/a |
| SECURITY | imperative for ops; descriptive for threat model | n/a |
| CHANGELOG | impersonal factual (Keep-a-Changelog) | n/a |
| ARCHITECTURE | descriptive third-person | n/a |
| ROADMAP | dated, blunt; "won't-do" load-bearing | n/a |
| Runbook | imperative, role-segregated | n/a |
| Glossary | precise definitions, no examples | n/a |
| Source comments (non-API-doc) | mixed density; deAI base rules apply | mixed |

Banned-vocab base + per-archetype overlays in `templates/deai_rules.md`.

## Section 8. Engagement output spec

Every engagement produces:

```
<project>/
  .recovery/
    state.jsonl         # structured per-phase verdicts
    calibration.jsonl   # one row per scored change (feeds form-check's calibration log)
    summary.md          # one-page human summary
  docs/
    [archetype-specific docs created/updated per engagement type]
```

`state.jsonl` schema (one object per phase):
```json
{"phase": "scoring", "ts": "...", "verdict": "pass|fail|advisory", "score": 92, "tier": "vibe-careful", "artifacts": ["..."], "notes": "..."}
```

## Section 9. Abort protocol

If the engagement should abort (user signal, scope mismatch, security concerns, time exhaustion):

1. Save partial state to `.recovery/abort-<timestamp>/`
2. Emit one-page summary (`.recovery/abort-<timestamp>/summary.md`): what ran, what didn't, what's next, uncommitted-change disposition
3. Append abort verdict row to `state.jsonl`
4. Exit with non-zero structured verdict
5. Do **not** auto-cleanup, user owns disposition

## Section 10. Anti-scope

- Not a feature-implementation tool. Reviews, scores, hardens, doc-passes, deAI-sweeps. Does not write feature code.
- Not a substitute for security audit on vibe-dangerous surfaces.
- Not for projects without form-check context (host must have `form-check@>=2.0.0,<3.0.0` available).

## Section 11. Mini-runbook

```text
1. apply recovery /path/to/project --engagement-type harden
2. discovery: read tree, frameworks, languages, current state
3. review: walk form-check checklists/INDEX.md → leaf checklists
4. scoring: per-finding score; aggregate engagement score
5. doc-pass: ensure CLAUDE.md, README, CHANGELOG, SECURITY.md, ARCHITECTURE.md, ADR baseline exist
6. deAI-sweep: voice-rule pass per archetype
7. adversarial: 12 questions; loop on fail (max 2 loops; then escalate)
8. launch-ready: walk checklists/launch_ready.md
9. summary: emit .recovery/summary.md + final state.jsonl
```

Full worked example: `examples/full-engagement-trace.md`.
