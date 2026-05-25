# trainer

An entrypoint and coaching skill for a 9-specialist agent toolkit. The trainer is text the agent reads at the start of every coding / prompt-engineering / agent-skill session. It points the agent to the right specialist for the work, asks the agent to read that specialist's leaf content before responding, and pushes back when the agent (or the user) tries to skip the routing.

> A trainer helps the user find the program that works for them, teaches them how to do it along the way, and adjusts to the user's wishes. The trainer is a coach: the goal is moving the user toward better patterns, more skills, more experience.

This repo distributes `trainer` together with the 9 specialist skill directories at `./specialists/`. Each specialist is independently usable. The trainer is the routing prose that connects them; it does not make the specialists work together at runtime, and it does not do the specialists' work itself.

**Honest scope (per an internal audit and the context-free adversarial review at v0.4.0):** as of v0.4.0 the trainer is a *documentation skill* with discipline scaffolding (Iron Law, Red Flags, Rationalizations, three doc-only pressure scenarios). It is not yet a *behavioral* skill in the sense that no runnable harness measures whether an agent loaded with the trainer actually behaves differently. A Phase 11 validation-infrastructure plan exists in private working notes and covers building that harness; this skill is not yet a portfolio claim that the harness exists.

---

## Why this exists

When you give an AI coding agent a library of specialist skills (`form-check`, `recovery`, `safetybar`, `program`, `warmup`, `gymbuddy`, `diet`, `pr`, `superset`), the bootstrap problem is real: which one to load, in what order, for what kind of work? The agent does not know unless something tells it. That bootstrap context lived nowhere in the codebase before this skill existed.

`trainer` is the entrypoint. Load it first; it routes to the right specialist; the specialist does the work; the trainer coaches the surrounding decisions. Loaded once per session, persistent throughout.

The decision to build a standalone bootstrap skill (rather than fold the routing into `warmup`) was driven by an internal gym-skills evidence audit; the summary rationale is captured in the v0.2.0 entry of [`CHANGELOG.md`](./CHANGELOG.md).

---

## The 9 specialists (bundled at `./specialists/`)

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
| [`superset`](./specialists/superset/) | parallel-agent dispatch discipline (worktree isolation, prompt templates, falsifier checklist, batch aggregation, status-check and closeout doc hygiene) | Spawning 2+ fresh-context agents on the same repo; orchestrator-handoff when the coordination chat hits context-window pressure; status refresh or job closeout when each touched repo's CHANGELOG, README, and roadmap must match shipped work |

Sibling-directory canonicals at `~/Projects/<name>.skill/` remain the editing home for each specialist. Run `scripts/bundle_specialists.sh` to refresh `./specialists/` for distribution.

---

## How the routing decision works

1. **What is the user doing right now?** Planning new code → `form-check plan-new-app`. Reviewing a diff → `form-check code-review`. Fixing after a bad ship → `recovery`. Pairing → `gymbuddy`. Multi-week plan → `program`. Just opened the workspace → `warmup`. Spawning 2+ parallel agents on the same repo → `superset`.
2. **What is the stakes tier?** Vibe-safe / vibe-careful / vibe-dangerous, classified per `form-check` Section 5. Vibe-dangerous → also load `safetybar`. Vibe-dangerous AND post-incident → also load `recovery`. Token budget tight → load `diet`. Parallel-agent dispatch at any tier → load `superset`.
3. **Adapt as the session evolves.** A planning session that uncovers an incident routes to `recovery` mid-session. A review that surfaces a runtime concern routes to `safetybar`. A multi-day push that hits IDE-slow or accumulated-context routes to `superset` for an orchestrator-handoff. Routing is not locked at start.

Specialists compose. The trainer explains the order and what to watch for between handoffs.

---

## Coaching stance: push back vs. defer

The trainer is not a doormat. It is also not an authority that overrides. The model is *coach with audit trail*.

**Push back when:**

- The decision has an identifiable, concrete deleterious downstream consequence. Name it with probability and severity.
- The decision veers from established best practice without articulated reason. Cite the specific practice.
- The user is missing a skill, pattern, or experience that would change their decision if they had it. Name what's missing.

**How:** one round (consequence + practice + alternative + cost / benefit). If the user pushes through, a second round with the strongest counter-evidence. After two rounds, defer and log the *coached override* with the user's rationale at `.recovery/calibration.jsonl` in the engagement repo (create `.recovery/` if absent; same path `form-check` uses; JSON shape in `references/trainer-runtime-compactness.md`).

**Do not push back when:** the user has demonstrated tradeoff understanding; the decision is genuinely subjective; the change is vibe-safe and reversible.

Full SKILL.md body: [`./SKILL.md`](./SKILL.md).

---

## Install / use

### As a Claude / Cursor / Windsurf skill

```bash
git clone https://github.com/weijia-89/trainer.skill ~/trainer.skill
ln -s ~/trainer.skill/SKILL.md ~/.claude/skills/trainer/SKILL.md
```

The skill triggers loading on every coding / prompt-engineering / agent-skill session. The 9 specialists at `./specialists/` are available to the trainer once they're either symlinked into the agent's skill directory or copied alongside.

### As a reference / methodology read

Read `SKILL.md` for the routing flow and coaching stance. Read each specialist's `SKILL.md` for what that specialist does and how it scores work. Start with `form-check` if you only read one specialist.

---

## Repository layout

```
trainer.skill/
├── SKILL.md                            # canonical trainer body (~141 lines / ~2089 est tokens as of v0.11.0 compact router)
├── README.md                           # this file
├── CHANGELOG.md                        # version history per SemVer below
├── SECURITY.md                         # vulnerability reporting and supported versions
├── LICENSE                             # PolyForm NC 1.0.0 + Iron Law
├── docs/
│   └── BRANCH_PROTECTION.md            # main branch protection policy and gh api commands
├── references/
│   ├── trainer-runtime-compactness.md  # communication, rationalizations, decision template, coached-override shape
│   ├── trainer-pre-action-gates.md     # mechanical three-facts gate, triggers, adversarial-review pass
│   └── trainer-dispatch-gates.md       # dispatch manifest, three-layer orch/meta/worker, status closeout
├── scripts/
│   ├── apply_branch_protection.sh      # idempotent protection PUT (DRY_RUN=1 default)
│   ├── bundle_specialists.sh           # refreshes ./specialists/ from sibling-dir canonicals
│   ├── verify_github_hardening.sh      # SECURITY.md layout + apply script dry-run smoke
│   └── verify_trainer_sync.sh          # asserts cross-IDE mirror consistency
├── tests/
│   ├── context_budget/                 # root SKILL.md size gate (Invariant 11)
│   │   ├── budget.toml
│   │   ├── check_context_budget.py
│   │   ├── measure_context.py
│   │   └── README.md
│   └── scenarios/                      # doc-only pressure scenarios (v0.4.0)
│       ├── README.md
│       ├── S01_ceremonial_routing.md
│       ├── S02_coaching_collapse_on_i_know.md
│       └── S03_bypass_for_small_task.md
└── specialists/
    ├── form-check/    # 243 files: checklists, rubrics, templates, tests, tools, docs
    ├── program/       # multi-session planning
    ├── warmup/        # context priming
    ├── safetybar/     # runtime guardrails
    ├── recovery/      # post-incident
    ├── gymbuddy/      # pairing
    ├── diet/          # token budget
    ├── pr/            # milestone retro
    └── superset/      # parallel-agent dispatch + orchestrator handoff (added v0.7.0 as `ancillary`, renamed v0.7.1)
```

---

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; specialist list gains or loses entries; coaching-stance criteria change.
- **MINOR**: new sync target added; specialist invocation pattern updated; new teaching responsibility added; bundle mechanic introduced.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

---

## Security

See [`SECURITY.md`](./SECURITY.md) for vulnerability reporting, supported versions, and scope (documentation skill bundle, not a runtime product). Do not paste secrets into public issues. Branch protection policy and apply script: [`docs/BRANCH_PROTECTION.md`](./docs/BRANCH_PROTECTION.md), [`scripts/apply_branch_protection.sh`](./scripts/apply_branch_protection.sh).

---

## Related portfolio repos

- **`weijia-89/palamedes`**: rigorous-research skill plus multi-agent synthesis prompt. The trainer's routing logic loads `palamedes/skill/SKILL.md` whenever the agent hits research triggers (`research`, `investigate`, `audit`, `fact-check`).
- **`weijia-89/playwrighter`**: production Playwright pattern library. The trainer loads it on Playwright file triggers; the `form-check` specialist references its quality scorecard.
- **`weijia-89/vibe-check`**: PR diff scanner for LLM-tell patterns. Composes with this repo's `form-check` specialist during code-review and adversarial-review modes.
- **`weijia-89/skill-sync`**: cross-IDE sync utility; see `SKILL.md` and `scripts/verify_trainer_sync.sh` for mirror targets.

---

## License

PolyForm Noncommercial 1.0.0 + Iron Law Addendum. See `LICENSE`. Specialists are individually licensed under the same terms; see each specialist's `LICENSE` file.
