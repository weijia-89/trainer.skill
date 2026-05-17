# Changelog

All notable changes to the `trainer` skill will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; the specialist gym-skills list gains or loses entries; teaching-responsibility tier semantics change.
- **MINOR**: new sync target added; a specialist gym-skill's invocation pattern is updated; new section added without changing existing semantics.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

## [0.5.0] (2026-05-16): Runnable pressure-scenario harness (3 trainer scenarios in form-check shape) + soft-cap bump

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged. The v0.4.0 doc-only pressure scenarios at `tests/scenarios/S01_*.md`, `S02_*.md`, `S03_*.md` are now also instantiated as runnable harness scenarios under `tests/scenarios/harness/<name>/` matching the form-check pressure-scenario shape (`setup.md` + `prompt.md` + `pass_criteria.py` + `notes.md` + `reference_response.md`). Doc-only scenarios are retained as the human-readable spec.

### Added

- **`tests/scenarios/harness/_grading.py`** vendored from `form-check.skill/tests/pressure_scenarios/_grading.py` (same `Transcript` substantive-sentence helper; same min-words floor of 10 for `__contains__`).
- **`tests/scenarios/harness/ceremonial_routing/`** harness shape for S01. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/coaching_collapse_on_i_know/`** harness shape for S02. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/bypass_for_small_task/`** harness shape for S03. Reference response passes its own `pass_criteria.py`.

### Changed

- **`scripts/verify_trainer_sync.sh`** soft cap bumped from 140 to 180 lines. Canonical `SKILL.md` is now 157 lines after the v0.4.0 Red Flags + Rationalizations additions; the previous 140 cap fired a `WARN` on every verify. New cap leaves headroom for incremental discipline-floor scaffolding without immediately tripping the warning.

### Not changed

- `SKILL.md` content (no normative additions beyond v0.4.0).
- README scope (already updated in v0.4.0 to acknowledge documentation-skill vs behavioral-skill distinction).
- The 4 sync targets (canonical, Claude mirror, Cursor trigger, Windsurf trigger) all agree on version 0.5.0 after this entry; verify with `bash scripts/verify_trainer_sync.sh`.

### Verification

- `tests/scenarios/harness/<name>/pass_criteria.py` passes against its corresponding `reference_response.md` for all 3 scenarios (3/3 PASS).
- `bash scripts/verify_trainer_sync.sh` reports PASS on all 7 invariants (version agreement, em-dash zero, trigger config, byte-identical mirror).
- `form-check.skill/tests/pressure_scenarios/discriminate_test.py` (mutation-style probe) still reports 0/272 incorrect passes after Option C upgrade of all 34 form-check pass_criteria.

### Known follow-ups

- **Phase 11 blind audit cycle** still pending. Requires `ANTHROPIC_API_KEY` or alternate-vendor harness; not autonomously runnable.
- **Layer B (calibration log analyzer) and Layer C (mutation testing of agent behavior)** of the Phase 11 plan remain future work; v0.5.0 is Layer A only (per-scenario pass/fail harness).

## [0.4.0] (2026-05-16): Load-bearing-discipline pass (audit-gap patches + Iron Law + Red Flags + Rationalizations + pressure scenarios)

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged; coaching-stance section gains explicit operational definitions and the discipline-floor scaffolding (Iron Law, Red Flags, Rationalizations) that the other 7 gym-skills already had.

Two converging inputs drove this version:

1. **A targeted audit of the v0.3.0 trainer skill** identified 4 operationalization gaps + 1 schema gap (Iron Law, demonstrated-understanding, adversarial-review interaction, opt-out semantics, override-log schema). The audit document itself is private working notes; the gaps it surfaced are described inline below.
2. **Context-free adversarial review at v0.3.0** (chat 2026-05-16, late) added 4 more items (Red Flags section, Rationalizations table, calibration log infrastructure, README walk-back of v0.3.0 promotional phrasing), plus three doc-only pressure scenarios for the failure modes.

The v0.3.0 portfolio-bundling work made the skill *distributable*; v0.4.0 makes the skill's stated discipline more *enforceable* by surfacing the failure modes the discipline is supposed to prevent.

### Added (SKILL.md)

- **Iron Law banner** at the top of the Coaching stance section. Form: *"coach, do not do. Push back when warranted. Defer when the user has demonstrated understanding. Log coached overrides."* Trainer was the only gym-skill without one as of v0.3.0; closes audit Gap 1.
- **Coached-override log entry schema inline.** Schema: `{ts, event, subject, trainer_position, user_decision, user_rationale, residual_concern, rounds}`. Closes audit Gap 5 (override log was prescribed in v0.2.0 but schema-undefined).
- **Red Flags section.** 10 verbatim agent-thoughts that should trigger STOP and re-route (e.g. "I named the specialist; that counts as invoking it", "User said 'I know'; I'll defer"). Matches form-check's structural pattern; sourced from the dominant failure modes in the adversarial review.
- **Rationalizations table.** 8 excuse / reality pairs covering ceremonial routing, coaching collapse, framing-based bypass, hidden-state coaching.
- **Adversarial-review deference** added to "What the trainer is NOT". During `form-check adversarial-review`, the trainer steps back on review content but stays engaged on routing decisions (which specialist next, when to stop). Closes audit Gap 3.
- **Opt-out semantics** as a new section. Per-session opt-out via "no coaching this session"; routing questions still answered, pushback paused. Persistent opt-outs are themselves a signal logged at the start of the next non-opted-out session. Closes audit Gap 4.

### Added (filesystem)

- **`form-check.skill/.recovery/calibration.jsonl`** (empty, append-only). Backs the pointer in `SKILL.md` which was previously dangling (verified by `ls` before the fix: directory did not exist).
- **`form-check.skill/.recovery/SCHEMA.md`** documenting event types: `coached_override`, `coaching_collapse`, `routing_decision`, `score_event`, `coached_override_revisit`. Append-only, UTC timestamps, no-PII discipline stated.
- **Three doc-only pressure scenarios** under `trainer.skill/tests/scenarios/`:
  - `S01_ceremonial_routing.md`, tests Iron Law + Red Flag "I named the specialist; that counts as invoking it"
  - `S02_coaching_collapse_on_i_know.md`, tests the tightened defer-clause against vague approval
  - `S03_bypass_for_small_task.md`, tests the always-on claim against user-framed-small tasks that hide tier-relevant context
  - Each follows the Phase 11 plan schema (Setup, Forcing function, Pass criteria, Fail criteria, Trapdoor). Manually testable by a human; runnable harness deferred to Phase 11 implementation.
- **`tests/scenarios/README.md`** documenting the manual test protocol and pass/fail mapping back to `SKILL.md` clauses.

### Changed

- **"Demonstrated understanding" clause tightened.** Previously: *"User has demonstrated understanding of the tradeoff and has a reasoned position."* Now: *"User has articulated the specific consequence the trainer named AND the specific reason it does not apply or is acceptable. Vague approval ('yes I know', 'I've got this', 'trust me') does not count as demonstrated understanding."* Closes audit Gap 2 (was the most exploitable clause in v0.3.0).
- **`README.md` honest-scope paragraph added.** Walks back v0.3.0 promotional phrasing ("8-skill agent ecosystem", "makes the ecosystem coherent"). New framing: documentation skill with discipline scaffolding, not yet a behavioral skill with a runnable harness. References the audit and the Phase 11 plan.
- **`README.md` repo-layout diagram** updated to include `tests/scenarios/`.
- **Soft line cap** bumped from 100 to 140 in `scripts/verify_trainer_sync.sh`. Canonical `SKILL.md` is now 157 lines. The cap will need another tune-up at next discipline-pass; see open items.

### Why MINOR not MAJOR

- 8 specialists unchanged.
- Routing decision flow byte-identical.
- Push-back triggers unchanged in category (still 3 triggers: concrete consequence, best-practice deviation, missing skill).
- New operational definitions and discipline scaffolding are clarifications + enforcement aids, not new behaviors. Any v0.3.0-compliant trainer is already v0.4.0-compliant; the v0.4.0 version is harder to game.

### Verification done

- `ls $HOME/Projects/form-check.skill/.recovery/` returns `calibration.jsonl` + `SCHEMA.md`.
- Em-dash audit: zero across `SKILL.md`, all three mirrors, this CHANGELOG entry, `SCHEMA.md`, the three scenarios, `README.md`, and `scripts/bundle_specialists.sh`.
- Bundle script re-run confirms 280 files across 8 specialists at `./specialists/`.
- `verify_trainer_sync.sh` invariants pass (canonical, Claude mirror, Cursor and Windsurf triggers all agree on version 0.4.0; zero em-dashes; `alwaysApply: true`; `trigger: always_on`).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (Iron Law, log-schema-inline, Red Flags, Rationalizations, defer tightening, adversarial-review carve-out, opt-out semantics; 103 → 157 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror, re-synced to v0.4.0 on second pass; first pass missed the Red Flags + Rationalizations block, caught by `verify_trainer_sync.sh`)
- `~/Projects/.cursor/rules/trainer.mdc` (heading bumped to v0.4)
- `~/Projects/.windsurf/rules/trainer.md` (same)
- `~/Projects/trainer.skill/README.md` (honest-scope paragraph, layout diagram updated)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (line cap 100 → 140)
- `~/Projects/trainer.skill/tests/scenarios/` (new dir, 4 files)
- `~/Projects/form-check.skill/.recovery/calibration.jsonl` (new, empty)
- `~/Projects/form-check.skill/.recovery/SCHEMA.md` (new)
- a private trainer-skill audit (working notes) (source audit doc; not in the skill repo)

### Open items deferred to next version

- **Phase 11 runnable harness** for the three pressure scenarios: doc-only at v0.4.0. The scenarios are testable manually; no automation submits them to an agent and scores behavior. Estimated 4-8 hr; deferred until external pressure (interview, public release, third party using the skill) makes the runnable case load-bearing.
- **`SKILL.md` line count at 157 already pushes the 140 cap** added in this version. Next discipline-pass should either re-tune the cap or split Red Flags + Rationalizations into a separate `discipline.md` companion. Splitting trades token efficiency (some agents skip companions) for the cap.
- ~~**Re-run `verify_trainer_sync.sh`**~~ Done. All 7 hard invariants PASS; the only WARN is the documented `SKILL.md` line count (157) over the bumped soft cap (140), tracked above.

---

## [0.3.0] (2026-05-16): Bundle the 8 specialists into the repo; rewrite README for portfolio distribution

**MINOR per SemVer rules.** Routing flow and coaching stance unchanged; new packaging mechanic added so the repo distributes the full 8-skill ecosystem rather than only the trainer entrypoint.

### Added

- **`specialists/` directory** with all 8 specialist gym-skills bundled in. Contents:
  - `specialists/form-check/` (243 files: SKILL.md, README, CHANGELOG, agent-runtime, checklists, docs, examples, learner, multi-language, references, rubrics, scale-up, templates, tests, tools)
  - `specialists/recovery/` (18 files: checklists, examples, references, rubrics, templates, tests, workflow)
  - `specialists/warmup/` (4 files, includes `graduation_checklist.md`)
  - `specialists/gymbuddy/`, `specialists/safetybar/`, `specialists/diet/`, `specialists/pr/`, `specialists/program/` (3 files each: SKILL.md, README, CHANGELOG)
  - Total bundled: 280 files across 8 specialists.
- **`scripts/bundle_specialists.sh`** refreshes the bundle from sibling-dir canonicals. Excludes `.git`, virtualenvs, `__pycache__`, `node_modules`, `.DS_Store`, `.pytest_cache`, `.recovery` state, generated test output. Idempotent via `rsync --delete`.
- **`composes:` frontmatter populated** in `SKILL.md` with the 8 specialist names.
- **"Bundled specialists" section in `SKILL.md`** explaining the relationship between sibling-dir canonicals (editing home) and bundle (distribution artifact).

### Changed

- **`README.md` rewritten** as public-portfolio-facing document. Was internal-skill-doc style; now opens with the "8-skill agent ecosystem" framing, includes install/use snippets, repository-layout diagram, and explicit separation between SKILL.md sync (canonical-to-mirrors, four locations) and bundle (canonical-to-`./specialists/`, one operation).
- **`SKILL.md` references** to specialist paths kept as `<name>.skill/` (sibling convention) in routing/teaching sections because the canonical operating environment is the home directory with sibling skill dirs; the bundle is for clones / distribution, not for local editing.
- **SemVer rules updated** to clarify that introducing the bundle mechanic is a MINOR change.

### Why this version is MINOR not MAJOR

- The 8 specialists in the `composes:` list are the same 8 specialists already documented in v0.2.0's body. No specialist added or removed.
- Routing decision flow is byte-identical to v0.2.0.
- Coaching stance criteria unchanged.
- The bundle is additive: agents that operate against sibling-dir canonicals continue to work unchanged.

### Hard-rule compliance

- Zero em-dashes across `SKILL.md`, `README.md`, this CHANGELOG entry, and the new bundle script.
- Bundle script uses single-quoted exclude patterns (no shell-glob surprises) and `set -euo pipefail` for fail-fast.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version bump 0.2.0 → 0.3.0; composes field populated; bundled-specialists section added)
- `~/Projects/trainer.skill/README.md` (rewrite, 60 → ~135 lines)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (new)
- `~/Projects/trainer.skill/specialists/` (new directory, 280 files across 8 specialists)

### Open questions

- **Mirror updates:** the `~/.claude/skills/trainer/SKILL.md` mirror needs a re-sync to pick up the v0.3.0 composes field and the new section. Run `scripts/verify_trainer_sync.sh` after mirror update.
- **Sync of bundled specialists:** the bundle currently lives only inside `trainer.skill`. If `~/.claude/skills/trainer/` should also carry the bundle (so Claude can read specialists without leaving its skill dir), that's a separate sync step worth deciding on before pushing public.
- **Public push:** repo is not yet pushed to GitHub. When ready, decide on repo visibility (public for portfolio vs private), tags / release for v0.3.0, and whether `LICENSE` and `CONTRIBUTING.md` need adding at the top level (currently only inside specialists like `form-check`).

---

## [0.2.0] (2026-05-16): Coaching stance correction; always-on triggers

**Breaking-semantic change.** v0.1.0 said "user wishes are the final say." Wei corrected this: the trainer is a coach, not a doormat. The trainer should push back when user decisions have deleterious downstream consequences or veer from best practices without articulated reason. After two rounds of coached pushback, the trainer respects the decision and logs it as a *coached override* with the user's rationale.

### Changed

- **Coaching stance section added.** Three push-back triggers (concrete downstream consequence; veers from best practice without articulated reason; user missing a skill that would change the decision). Procedure: name consequence, cite practice, offer alternative; two rounds max; log coached override.
- **Proactive teaching responsibilities expanded.** Trainer now explicitly explains: specialist composition (which order, why, how they interact), downstream consequences (what to watch for after a change), best practices (cited from `form-check.skill/references/notes.md` at the moment of relevance).
- **Triggers changed to always-on.** Cursor trigger: `alwaysApply: true`. Windsurf trigger: `trigger: always_on`. Loaded first on every coding / prompt-engineering / agent-skill session.
- **Removed "user wishes are the final say"** language entirely. Replaced with the coaching-with-audit-trail model.
- **README.md added** documenting all four sync targets and SemVer rules. The Phase 10 routing decision (whether to fold trainer into `warmup` or stand it up separately) was driven by a private gym-skills evidence audit; the decision and rationale are summarized in `docs/PHASE_10_ROUTING_DECISION.md` when that doc exists.

### Hard-rule compliance

- Zero em-dashes in `SKILL.md`, both triggers, README, and this CHANGELOG entry (matches Wei's writing-style hard rule from 2026-05-15).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (rewrite; 88 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror)
- `~/Projects/.cursor/rules/trainer.mdc` (always-apply, updated body)
- `~/Projects/.windsurf/rules/trainer.md` (always-on, updated body)
- `~/Projects/trainer.skill/README.md` (new)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (bumped expected version to 0.2.0; bumped soft line cap from 80 to 100)

### Companion: `skill-sync` gains Windsurf support

`skill-sync` v0.2+ adds Windsurf as a sync target alongside Claude and Cursor. The trainer skill is the first to use it. See `~/.claude/skills/skill-sync/CHANGELOG.md` for the implementation detail.

## [0.1.0] (2026-05-16): Initial scaffold

- Created as the bootstrap / entrypoint skill for the gym-skills family (Phase 10 of the gym-skills evidence-base audit, 2026-05-16).
- Role defined: "helps the user find the program that works for them, teaches them how to do it along the way, and adjusts according to the user's wishes." Authored by Wei Jia.
- Sync targets established at four locations:
  - `~/Projects/trainer.skill/SKILL.md` (canonical)
  - `~/.claude/skills/trainer/SKILL.md` (Claude mirror, byte-identical)
  - `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger)
  - `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger)
- `scripts/verify_trainer_sync.sh` added to assert sync invariants.
- Lists the 8 specialist gym-skills (`form-check`, `program`, `warmup`, `safetybar`, `recovery`, `gymbuddy`, `diet`, `pr`) with one-line invocation criteria.
- Names "user wishes are the final say" as the trainer's behavioral anchor: overrides are respected and noted, never argued. (Reversed in v0.2.0.)
- No checklists, no rubrics, no scoring. Pure routing + teaching + adapting.
