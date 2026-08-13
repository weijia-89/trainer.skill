# context.md — trainer.skill

> Skill-level context for `trainer.skill`. Regenerated 2026-08-12 during L2 integration
> (emilkowalski/skills → `references/frontend-eng.md`). This file is the durable memory of what
> the skill is, what it must not break, and where the evidence lives. Update it on every behavior
> change; stale coverage numbers are worse than absent ones.

## Contract

trainer.skill is a process/quality coaching skill for coding, prompt-engineering, and agent-skill
sessions. It **routes** to specialists, **coaches** with an audit trail, and **steps back** — it
does not do the work. Specialists execute.

- **Routing iron law (#4):** trainer core routing (the `SKILL.md` workflow-routing flow and the 10
  specialist gym-skills) must not be altered to accommodate added content. Additions surface via
  `references/` files, not routing changes.
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

## Current coverage / open watch items

- L2 implementation: commits `1dc2085` + `201b4c8` on `integration/L2-trainer`.
- **Phase 10–12 COMPLETE:** `context.md` regenerated (this file); 3 review postures PASS;
  PR **#34 OPEN** against `main` with the trainer review-comment gate posted
  (APPROVE, validators PASS — both bug-inventory + R-6). Gate I (per-lane gap audit)
  COMPLETE (verdict COMPLETE, conditional on merge).
- **Forward obligation (on merge):** attach a 14-day watch window (owner Wei Jia; revert trigger
  = remove `references/frontend-eng.md`) and close the lane's terminal disposition as *merged*.
- L3 (palamedes+piranesi) remains operator-blocked on the Track-2 prose-scenario decision.
