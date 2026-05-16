# trainer

The bootstrap and routing skill for Wei's gym-skills family.

> A trainer helps the user find the program that works for them, teaches them how to do it along the way, and adjusts to the user's wishes. The trainer is a coach: the goal is moving the user toward better patterns, more skills, more experience.

## What this is

`trainer` is loaded first on every coding, prompt-engineering, or agent-skill session. It is the always-on entrypoint that routes work to the right specialist gym-skill at the right moment, explains why, names downstream consequences, and adapts as the session evolves.

It is a **coach**. It pushes back when user decisions have deleterious downstream consequences or veer from best practices without articulated reason. After two rounds of coached pushback, it respects the user's call and logs the override.

It does not do the work itself. The specialists do.

## Specialists routed by the trainer

| Skill | Role |
|---|---|
| [`form-check`](../form-check.skill/) | the form-verification moment (code review, plan-new-app, adversarial review, harden, deprecate) |
| [`program`](../program.skill/) | the multi-session training plan (roadmaps, sprint planning, multi-week initiatives) |
| [`warmup`](../warmup.skill/) | pre-session context priming |
| [`safetybar`](../safetybar.skill/) | agent-runtime guardrails (allow-list, ledger, rollback) |
| [`recovery`](../recovery.skill/) | post-incident protocol |
| [`gymbuddy`](../gymbuddy.skill/) | the pairing peer (co-coding, walkthroughs) |
| [`diet`](../diet.skill/) | context / token-budget management |
| [`pr`](../pr.skill/) | milestone celebration and retro |

## Files

- `SKILL.md`: canonical body (v0.2.0; ≤100 lines).
- `CHANGELOG.md`: version history with SemVer rules.
- `scripts/verify_trainer_sync.sh`: asserts the four sync targets remain consistent (canonical ≡ Claude mirror byte-identical; Cursor and Windsurf triggers reference the canonical path; all four agree on version; canonical stays under line cap).

## Sync targets

| Target | Path | Role |
|---|---|---|
| Canonical | `~/Projects/trainer.skill/SKILL.md` | Source of truth |
| Claude mirror | `~/.claude/skills/trainer/SKILL.md` | Byte-identical copy |
| Cursor trigger | `~/Projects/.cursor/rules/trainer.mdc` | `alwaysApply: true`; points to canonical |
| Windsurf trigger | `~/Projects/.windsurf/rules/trainer.md` | `trigger: always_on`; points to canonical |

Cross-IDE sync is automated by [`skill-sync`](https://github.intuit.com/wjia/skill-sync) v0.2+ (Claude, Cursor, Windsurf all supported). Manual sync also works: edit canonical, copy to Claude, then run `scripts/verify_trainer_sync.sh`.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; specialist gym-skills list gains or loses entries; the coaching stance (push back vs. defer) changes its criteria.
- **MINOR**: new sync target added; a specialist's invocation pattern updated; a new teaching responsibility added.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

## Why this exists

The 8 gym-skills (form-check, recovery, gymbuddy, safetybar, diet, pr, program, warmup) had no entrypoint. An agent that wanted to use them had to already know they existed, when to invoke each, and how they compose. That bootstrap context lived nowhere in the codebase.

`trainer` is the entrypoint: load it first, and it tells the agent where to go next.

The decision to build a standalone bootstrap skill (rather than fold the routing into `warmup`) is documented in the Phase 10 section of `~/Projects/reviews/GYM_SKILLS_EVIDENCE_AUDIT_2026-05-16.md`.

## License

MIT.
