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

## Current coverage / open watch items

- L2 implementation: commits `1dc2085` + `201b4c8` on `integration/L2-trainer`.
- **L2 CLOSED:** PR #34 merged (along with #35–#39, which carried the PR-body test coverage, the
  skill-tree audit tooling, the code_shape checklist, the reference-fence repairs, and the
  `spec-loop` route). The 14-day watch window on `references/frontend-eng.md` has no open findings.
- **v1.0.0 OPEN:** PR **#40** (`feat/logbook-specialist`) awaits operator review. Do not merge until
  the operator says so. All four CI jobs pass on head `fd8589a`.
- **Deferred, both blocked by the generation gate:** (a) `scripts/verify_trainer_sync.sh:364-365`
  aborts silently when a trigger file carries no version stamp (remedy `|| true` per grep);
  (b) `scripts/bundle_specialists.sh:2` still says "the 10 specialist gym-skills" and its
  `SRC_ROOT` comment says "ten sibling" directories. Touching either `.sh` file turns CI red today,
  because the generation-gate job runs strict mode on every changed `.sh` file and
  `bundle_specialists.sh` already fails it with 1 critical (`cd &&` chain) on `main`.
- L3 (palamedes+piranesi) remains operator-blocked on the Track-2 prose-scenario decision.
