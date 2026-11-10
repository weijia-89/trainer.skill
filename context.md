# context.md — trainer.skill

> Skill-level context for `trainer.skill`. Regenerated 2026-08-12 during L2 integration
> (emilkowalski/skills → `references/frontend-eng.md`); refreshed 2026-11-06 for v1.0.0
> (the `logbook` specialist). This file is the durable memory of what the skill is, what it must
> not break, and where the evidence lives. Update it on every behavior change; stale coverage
> numbers are worse than absent ones.

## Contract

trainer.skill is a process/quality coaching skill for coding, prompt-engineering, and agent-skill
sessions. It **routes** to specialists, **coaches** with an audit trail, and **steps back** — it
does not do the work. Specialists execute.

- **Routing iron law (#4):** trainer core routing (the `SKILL.md` workflow-routing flow and the 11
  routed specialist gym-skills) must not be altered to accommodate added content. Additions surface
  via `references/` files, not routing changes. Operator decisions have extended the specialist list
  twice so far (`spotter` at v0.16.0, `logbook` at v1.0.0); each addition is a MAJOR bump under the
  SemVer rules in `CHANGELOG.md` because the gym-skills list gains an entry.
- **Self-testing iron law (#5):** any implementation session must run the trainer test suite
  (incl. `tests/context_budget/check_context_budget.py`) before/after changes.
- **No runtime from vendored content (non_negotiable #7 analog):** ported/referenced content
  introduces no package dependencies, hooks, or execution surface.

## Invariants (relevant to L2)

- INV: adding `references/frontend-eng.md` changed zero routing rules (verified: `git show --stat`
  of the implementation commit touches only that one file; root `SKILL.md` line count unchanged at
  201/220).
- INV: the reference is Markdown-only; no deps, no hooks, no `node_modules`.
- INV: provenance is retained — content ported from `emilkowalski/skills@de33dbe` (MIT), cited in
  the reference file header and the implementation commit.
- INV: trainer remains a process/quality skill, **not** a frontend skill (see Non-goals).

## L2 acquisition — `references/frontend-eng.md`

| Field | Value |
|---|---|
| Source | `emilkowalski/skills@de33dbe` (MIT, 17 files, 100% Markdown, zero runtime) |
| Disposition | **Port** (logic valuable; upstream diverges from our conventions) — rewritten in our idiom, provenance retained, no upstream tracking |
| Structure decision | Reference file (D11), **not** a specialist routing trigger |
| Versioning | MINOR bump 0.16.0 → 0.17.0 (additive reference, no routing change) (D13) |
| Scope decision | All 52 gaps: 42 upstream behaviors (`UP-B01..B42`) + 10 uncovered domains (`N01..N10`) (D10) |
| Tooling | Static-decline lifted for Phase 5+ (D12); trainer suite runs locally during implementation |
| Risk tier | 9 (watch, accept with mitigation) — RISK-emilkowalski-skills.md, Gate B PASS |
| Phase 6 scorecard | 7-dim sum +12, band *adopt*, disposition *Port* — rubric/L2-acquisition.md |

### What the reference contains

- A catalog of 52 frontend gaps (the absence IS the gap, not a design decision — trainer had
  **zero** frontend coverage).
- Design principles, anti-patterns, and routing/versioning rules for trainer-facing frontend
  guidance.
- It does **not** inline the actual frontend guidance; that is delivered as 50 kickoff prompts in
  `L2-GAP-PROMPTS.md` (integration-artifacts), one (or a coupled pair) per gap.

### Behavioral contract of the reference

- Loadable on demand by any specialist; never auto-injected as a routing branch.
- Framed as **guidance, not commands**; never overrides trainer's routing/coaching stance.
- Kill-switch = remove the reference (revert commit); no migration, no persisted state.

## Decisions (L2)

| ID | Decision | Date |
|---|---|---|
| D10 | Scope: all 52 gaps (42 upstream + 10 uncovered domains) | 2026-08-11 |
| D11 | Structure: `references/frontend-eng.md` (reference file, not specialist) | 2026-08-11 |
| D12 | Tooling: lift static-decline for Phase 5+ (same posture as L3) | 2026-08-11 |
| D13 | Versioning: MINOR bump (additive reference, no routing change) | 2026-08-11 |

## Non-goals

- trainer.skill does **not** become a frontend/animation skill. The reference makes trainer
  *consultive* on frontend motion questions; it does not own frontend implementation.
- The reference does **not** add a routing trigger, a specialist, or runtime dependencies.
- The 52 kickoff prompts are a backlog, not inlined guidance; they scope follow-up work.

## Test and eval locations

- **Track 2 behavioral eval corpus:** `integration-artifacts/evals/L2/scenarios.md`
  - 9 change-set behaviors (B-CAT, B-PROV, B-REF, B-PROMPT, B-LOAD, B-NORUN, B-VERS, B-ROUTE,
    B-FRAME). Scenario coverage = 100%.
- **Coverage figures (2026-08-12):**
  - 9/9 behaviors evidenced PASS (deterministic + tooling + structural).
  - B-ROUTE / B-FRAME model-run ×5 pass rates: **not captured** (no eval harness this session);
    shortfall explicitly accepted per META Gate C. A clean-context Verifier may capture later.
- **Trainer tooling gate:** `tests/context_budget/check_context_budget.py` → PASS (root SKILL.md
  201/220 lines, 4544/5500 est tokens) after adding the reference.

## v1.0.0 - the `logbook` specialist (2026-11-01)

| Field | Value |
|---|---|
| Deliverable | `specialists/logbook/` (native to this repo, not a bundled sibling copy) |
| Structure decision | Specialist + CLI, and a routing row; **not** a reference file (D14) |
| Versioning | MAJOR bump 0.17.0 → 1.0.0 (the gym-skills list gains an entry) (D15) |
| Tooling | `specialists/logbook/scripts/logbook.py`, Python standard library only, no network (D16) |
| Tests | `tests/logbook/test_logbook.py`, 31 unit tests, wired to CI via `.github/workflows/logbook-tests.yml` (D17) |
| Evidence | PR **#40** (`feat/logbook-specialist`), review comment round 1 on head `fd8589a` |

### Decisions (v1.0.0)

| ID | Decision | Date |
|---|---|---|
| D14 | Structure: specialist + CLI + routing row; not a reference file (a ledger needs a tool, not prose) | 2026-11-01 |
| D15 | Versioning: MAJOR 0.17.0 → 1.0.0 (the gym-skills list gains an entry) | 2026-11-01 |
| D16 | Tooling: standard-library Python only; no installs, no network, no dependency | 2026-11-01 |
| D17 | Tests live in their own workflow (`.github/workflows/logbook-tests.yml`) because the generation-gate job runs strict mode on every changed `.sh` file | 2026-11-01 |

### What the logbook does

One append-only record per project at `<project>/.workledger/`: the objective, every work slice with
a proof path, its outcome, and the next slice on the bar. `verify` is the form check and fails
closed: a slice whose proof file is gone is `EV_MISSING`, a slice logged without proof is
`EV_UNVERIFIED`, and an empty logbook never passes (exit 2).

### Behavioral contract of the logbook

- Append-only. History is never rewritten; a missed slice is logged as missed.
- Output cost is proportional to the failures, not to the length of the log: `verify` prints one
  line on a clean log and lists failing sets in full; `--all` is the only mode that grows with the log.
- The generated `ACTIVE_STATE.md` caps every displayed field, so its size does not grow with the project.
- Evidence fields carry paths, never file contents.
- Not a spec-execution loop (`spec-loop` owns that route) and not a replacement for
  `.agent/scratchpad.md` (session working memory vs durable per-project record).
- Kill-switch = revert the commit; the ledger folder is gitignored and project-local.

## 2026-11-08 - model-agnostic Phase 11 adapter (PR #45)

| Field | Value |
|---|---|
| Decision | Phase 11 live runs must be model agnostic; the operator retired the Anthropic-only requirement (2026-11-08) |
| Deliverable | `scripts/harness_adapters/openai_compatible.py`: any OpenAI-compatible endpoint, stdlib urllib, no provider SDK, no new dependency (D18) |
| Shared guard | Preamble, untrusted-data wrapper, prompt builder, and offline stub live in `scripts/harness_adapters/_common.py`; both adapters import them, so the injection guard has one source of truth (D19) |
| Gates | `verify_phase11_synthesis_gates.sh` is strict-clean (8 pre-existing warnings fixed); adapter unit tests 7/7; offline smoke clean; production tree byte-identical |
| Live runs | Operator-driven via `OPENAI_BASE_URL`, a dated `OPENAI_MODEL`, and `OPENAI_API_KEY`; the key never enters the repo or chat |

## 2026-11-08 - root SKILL.md token diet (PR #44)

| Field | Value |
|---|---|
| Change | Prose-only compression of root `SKILL.md`; routing, trigger tokens, Iron Laws, Red Flags, and the reference map stay intact |
| Measured | 4690 to 4468 est tokens; 203 to 192 lines (`check_context_budget.py`); `budget.toml` snapshot updated to the measured values |
| Verification | Local and CI sync verify PASS; deai 23 to 21 signals, no new hits; added-line em-dash zero; QA verdict APPROVE (trigger tokens set-identical, 23 of 23) |

## 2026-11-09 - dead pointers realized + adapter tests in CI (PR #48)

| Field | Value |
|---|---|
| Decision D20 | Dead pointers that SKILL.md names get created files, not dropped rows; content stays grounded in existing prose (operator, 2026-11-09) |
| Deliverable | `references/chatprd-opus-implementation-plan-gate.md`, `references/chatprd-plan-adversarial-template.md`, `references/trainer-phase-implementation-gate.md` created and mirrored |
| Decision D21 | CI wiring topology: the OpenAI adapter unit suite runs inside `verify_trainer_sync.sh` (both blocks); the synthesis-gate smoke runs as its own workflow step and must NEVER run inside the script - the gate's Gate 5 calls that script, so the placement recurses infinitely (the first wiring attempt hung full verify and later failed the smoke at its 300s subprocess timeout) |
| Verification | Adapter unit tests 7/7; gate smoke PASS ~11s after the fix; full verify ~9s (inside the CI 30s script timeout); strict generation gate + shellcheck clean on both edited scripts |

## 2026-11-09 - CHANGELOG drift CI wave (PR #50)

| Field | Value |
|---|---|
| Deliverable | `scripts/check_changelog_drift.sh` + `tests/test_check_changelog_drift.sh`, wired as a separate `Check CHANGELOG drift` step in `.github/workflows/python-package-conda.yml` |
| Rule | A diff that changes `SKILL.md`, `scripts/`, or `tests/` must also change `CHANGELOG.md`; docs-only diffs are exempt (R-6) and may still update it |
| Decision D22 | Base resolution fails closed: the CI-supplied `BASE_SHA` must resolve to a commit. GitHub sends an all-zero `before` SHA for a new branch push; the script treats that as unset instead of failing on it. An unresolvable base is FAIL, never silent pass. Local fallback: `merge-base origin/main HEAD`, then `origin/main` |
| Placement | Outside `verify_trainer_sync.sh` per D21; step order in the workflow is `bash -n`, then the drift check, then the verify job. PR #50 also moved that checkout to `fetch-depth: 0`, which pulls the base commit for the diff |
| Verification | Temp-dir git fixtures cover the triggering paths and the docs-only exemption. Another fixture covers the pass case where `CHANGELOG.md` ships with the triggering work. The check is its own CI step |

## Current coverage / open watch items

- L2 implementation: commits `1dc2085` + `201b4c8` on `integration/L2-trainer`.
- **L2 CLOSED:** PR #34 merged (along with #35–#39, which carried the PR-body test coverage, the
  skill-tree audit tooling, the code_shape checklist, the reference-fence repairs, and the
  `spec-loop` route). The 14-day watch window on `references/frontend-eng.md` has no open findings.
- **v1.0.0 CLOSED (merged):** the `logbook` specialist shipped via squash PRs
  **#40** (`0da6f93`, 2026-11-06) and **#41** (`59b386e`, 2026-11-07, output-cost
  and docs waves). Follow-ups for this repo now live in its own PR lane.
- **Watch item retired (2026-11-10):** the two generation-gate-deferred `.sh`
  fixes shipped in PR #42 (2026-11-07) alongside the gate's precision pass.
  `scripts/verify_trainer_sync.sh` version-stamp greps run `|| true`, so a
  missing stamp prints a proper FAIL instead of a silent abort (lines 371-377),
  and `scripts/bundle_specialists.sh` carries the honest header (logbook and
  cruft native, out of the bundle array). Touching either script no longer
  turns CI red; the gate passes both in strict mode.
- L3 (palamedes+piranesi) remains operator-blocked on the Track-2 prose-scenario decision.
