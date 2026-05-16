# Changelog

All notable changes to the `trainer` skill will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; the specialist gym-skills list gains or loses entries; teaching-responsibility tier semantics change.
- **MINOR**: new sync target added; a specialist gym-skill's invocation pattern is updated; new section added without changing existing semantics.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

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
- **README.md added** documenting all four sync targets, SemVer rules, and the link to the Phase 10 decision in `~/Projects/reviews/GYM_SKILLS_EVIDENCE_AUDIT_2026-05-16.md`.

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
