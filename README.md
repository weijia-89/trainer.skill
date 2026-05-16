# trainer

A routing and coaching layer for an 8-skill agent ecosystem. The trainer is always-on, routes work to the right specialist at the right moment, explains why, names downstream consequences, and pushes back when user decisions veer from best practice without an articulated reason.

> A trainer helps the user find the program that works for them, teaches them how to do it along the way, and adjusts to the user's wishes. The trainer is a coach: the goal is moving the user toward better patterns, more skills, more experience.

This repo bundles `trainer` plus its 8 specialist skills as a single distribution. Each specialist is independently usable; `trainer` is the entrypoint that makes the ecosystem coherent.

---

## Why this exists

When you give an AI coding agent a library of specialist skills (`form-check`, `recovery`, `safetybar`, `program`, `warmup`, `gymbuddy`, `diet`, `pr`), the bootstrap problem is real: which one to load, in what order, for what kind of work? The agent does not know unless something tells it. That bootstrap context lived nowhere in the codebase before this skill existed.

`trainer` is the entrypoint. Load it first; it routes to the right specialist; the specialist does the work; the trainer coaches the surrounding decisions. Loaded once per session, persistent throughout.

The decision to build a standalone bootstrap skill (rather than fold the routing into `warmup`) is documented in the Phase 10 section of [`GYM_SKILLS_EVIDENCE_AUDIT_2026-05-16.md`](https://github.com/weijia-89/trainer.skill/blob/main/docs/PHASE_10_ROUTING_DECISION.md) (local-only reference for now; see CHANGELOG).

---

## The 8 specialists (bundled at `./specialists/`)

| Skill | Role | When to load |
|---|---|---|
| [`form-check`](./specialists/form-check/) | code-review and form-verification across 6 modes (plan-new-app, code-review, adversarial-review, refactor-prep, harden, deprecate) | Before any code change. The most-developed specialist; carries the checklists, rubrics, and scoring rules the rest of the ecosystem references. |
| [`program`](./specialists/program/) | multi-session training plan | Roadmaps, sprint planning, multi-week tech-debt initiatives |
| [`warmup`](./specialists/warmup/) | pre-session context priming | Beginning of any session |
| [`safetybar`](./specialists/safetybar/) | agent-runtime guardrails (allow-list, ledger, rollback) | Agent runtime needs hard guardrails; vibe-dangerous changes |
| [`recovery`](./specialists/recovery/) | post-incident protocol | After a bad ship, incident, regression, audit-block |
| [`gymbuddy`](./specialists/gymbuddy/) | the pairing peer | Co-coding, pair-on-vibe-dangerous, walkthroughs |
| [`diet`](./specialists/diet/) | context / token-budget management | Output volume needs trimming, tokens are the constraint |
| [`pr`](./specialists/pr/) | personal-record celebration | Milestones, retros, achievements |

Sibling-directory canonicals at `~/Projects/<name>.skill/` remain the editing home for each specialist. The `./specialists/` copies are refreshed by `scripts/bundle_specialists.sh` for distribution.

---

## How the routing decision works

1. **What is the user doing right now?** Planning new code → `form-check plan-new-app`. Reviewing a diff → `form-check code-review`. Fixing after a bad ship → `recovery`. Pairing → `gymbuddy`. Multi-week plan → `program`. Just opened the workspace → `warmup`.
2. **What is the stakes tier?** Vibe-safe / vibe-careful / vibe-dangerous, classified per `form-check` Section 5. Vibe-dangerous → also load `safetybar`. Vibe-dangerous AND post-incident → also load `recovery`. Token budget tight → load `diet`.
3. **Adapt as the session evolves.** A planning session that uncovers an incident routes to `recovery` mid-session. A review that surfaces a runtime concern routes to `safetybar`. Routing is not locked at start.

Specialists compose. The trainer explains the order and what to watch for between handoffs.

---

## Coaching stance: push back vs. defer

The trainer is not a doormat. It is also not an authority that overrides. The model is *coach with audit trail*.

**Push back when:**

- The decision has an identifiable, concrete deleterious downstream consequence. Name it with probability and severity.
- The decision veers from established best practice without articulated reason. Cite the specific practice.
- The user is missing a skill, pattern, or experience that would change their decision if they had it. Name what's missing.

**How:** one round (consequence + practice + alternative + cost / benefit). If the user pushes through, a second round with the strongest counter-evidence. After two rounds, defer and log the *coached override* with the user's rationale at `form-check/.recovery/calibration.jsonl`.

**Do not push back when:** the user has demonstrated tradeoff understanding; the decision is genuinely subjective; the change is vibe-safe and reversible.

Full SKILL.md body: [`./SKILL.md`](./SKILL.md).

---

## Install / use

### As a Claude / Cursor / Windsurf skill

```bash
git clone https://github.com/weijia-89/trainer.skill ~/trainer.skill
ln -s ~/trainer.skill/SKILL.md ~/.claude/skills/trainer/SKILL.md
```

The skill triggers loading on every coding / prompt-engineering / agent-skill session. The 8 specialists at `./specialists/` are available to the trainer once they're either symlinked into the agent's skill directory or copied alongside.

### As a reference / methodology read

Read `SKILL.md` for the routing flow and coaching stance. Read each specialist's `SKILL.md` for what that specialist does and how it scores work. Start with `form-check` if you only read one specialist.

---

## Repository layout

```
trainer.skill/
├── SKILL.md                   # canonical trainer body (≤100 lines)
├── README.md                  # this file
├── CHANGELOG.md               # version history per SemVer below
├── LICENSE                    # MIT
├── scripts/
│   ├── bundle_specialists.sh  # refreshes ./specialists/ from sibling-dir canonicals
│   └── verify_trainer_sync.sh # asserts cross-IDE mirror consistency
└── specialists/
    ├── form-check/    # 243 files: checklists, rubrics, templates, tests, tools, docs
    ├── program/       # multi-session planning
    ├── warmup/        # context priming
    ├── safetybar/     # runtime guardrails
    ├── recovery/      # post-incident
    ├── gymbuddy/      # pairing
    ├── diet/          # token budget
    └── pr/            # milestone retro
```

---

## Sync targets (canonical-to-mirrors, separate from the bundle)

The `SKILL.md` body is mirrored across four locations so every IDE-resident agent loads the same routing logic:

| Target | Path | Role |
|---|---|---|
| Canonical | `~/Projects/trainer.skill/SKILL.md` | Source of truth |
| Claude mirror | `~/.claude/skills/trainer/SKILL.md` | Byte-identical copy |
| Cursor trigger | `~/Projects/.cursor/rules/trainer.mdc` | `alwaysApply: true`; points to canonical |
| Windsurf trigger | `~/Projects/.windsurf/rules/trainer.md` | `trigger: always_on`; points to canonical |

Cross-IDE sync is automated by [`skill-sync`](https://github.com/weijia-89/skill-sync) v0.2+ (Claude, Cursor, Windsurf all supported). Manual sync also works: edit canonical, copy to Claude, then run `scripts/verify_trainer_sync.sh`.

The **bundle** at `./specialists/` is a separate mechanic: it's refreshed by `scripts/bundle_specialists.sh` from the sibling `~/Projects/<name>.skill/` canonicals. The bundle is for distribution; the canonicals are for editing.

---

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; specialist list gains or loses entries; coaching-stance criteria change.
- **MINOR**: new sync target added; specialist invocation pattern updated; new teaching responsibility added; bundle mechanic introduced.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

---

## License

MIT. See `LICENSE`. Specialists are MIT-licensed individually; see each specialist's `LICENSE` file.
