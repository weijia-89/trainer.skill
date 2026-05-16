# Changelog

All notable changes to the `trainer` skill will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; the specialist gym-skills list gains or loses entries; teaching-responsibility tier semantics change.
- **MINOR**: new sync target added; a specialist gym-skill's invocation pattern is updated; new section added without changing existing semantics.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

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
