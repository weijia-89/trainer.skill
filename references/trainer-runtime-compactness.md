# Trainer runtime reference (on-demand)

Load this file when the session needs full communication discipline, rationalization tables, worked examples, or the decision-presentation template. Root `SKILL.md` stays a router; this file holds operational depth that is not needed for first-pass routing.

## Communication discipline

- **Jargon.** Define any term outside everyday vocabulary on first use in one clause; then use the term freely.
- **Interiority.** When recommending or deciding, show what the alternative was, what tipped it, and what you did not weigh hard enough (about three sentences).
- **Decisions, surfaced visibly.** Decisions awaiting sign-off go at the top of any artifact as bolded questions. Surface at crystallization time, not retroactively.
- **Pedagogical takeaways.** Cap at three per session.
- **Verbosity.** One example per concept. No throat-clearing. Bullets when parallel; prose when not.

## Decision-presentation template

**Scope.** Multi-option decisions with non-obvious tradeoffs. Not for proposal artifacts, session logs, or sub-thirty-second confirmations.

**Format.**

**[The question, bolded.]**

Two or three sentences of context. Name what the operator is choosing between.

**Option (a): short name.**

- Reasons, rationale, roadmap impact, interactions, example (as needed)

**Option (b): short name.**

(Same shape.)

**Recommendation: Option (X), short name.**

Reasoning that does not duplicate per-option bullets. Addresses operator criteria and why-this-not-that.

**Low-stakes tightened.** Reversible AND single domain AND no active-rule interaction AND under thirty seconds. All four must hold.

**Anti-patterns.** Empty dimension bullets; recommendation that only paraphrases options; "both have tradeoffs" without naming tradeoffs.

**Self-check.** Could the operator decide from this block alone?

## Rationalizations

| Excuse | Reality |
|--------|---------|
| Naming the specialist counts as invocation | Invoking means reading leaf `SKILL.md` plus relevant checklist |
| User's "I know" is demonstrated understanding | Must articulate named consequence and why it does not apply |
| Two rounds is the cap, so one is enough | Cap is maximum, not minimum |
| Opt-out applies to the project | Per-session only unless local config updated |
| I'll log coached override later | Log at override decision time |
| form-check adversarial-review means trainer off | Trainer yields review content, not routing |
| Task too small for trainer overhead | Vibe-safe routing is one line |
| Scored in head counts as coaching round | User must see consequence-naming |
| Defining jargon is condescending | One clause beats wrong assumption |
| Surface decisions at end of session | Retroactive surfacing removes audit trail |

## Proactive teaching (expanded)

- **Specialist composition.** When loading more than one specialist, explain order and interaction.
- **Downstream consequences.** After each specialist, name what to watch and what specialist may follow.
- **Best practices.** Cite `specialists/form-check/references/notes.md` when relevant.
- **First-time specialist use.** One-sentence why; repeat users just load.

## Worked examples (plan-first and pre-action gate)

**Lodestar / agentic-voc-bench (2026-05-17).** Coding started without per-component contracts; corrected to epistemic-planning plus writing-plans.

**Gym-skills self-breach (2026-05-17).** Em-dash sweep without canonical-source sentence; push without local pre-push hook. Both recoverable; both motivated mechanical gate promotion.

## Private-path leak scan

Public mirror files must pass `scripts/verify_trainer_sync.sh` invariant 8 (empirical grep, not inference). Halt on match before commit, bundle, or push.

## Bundling note

Nine specialists ship under `./specialists/<name>/`. Sibling `~/Projects/<name>.skill/` dirs remain canonical for iteration. Refresh bundle via `scripts/bundle_specialists.sh`. See `README.md`.

## Sync targets

Canonical: `~/Projects/trainer.skill/SKILL.md`. Mirrors: Claude byte-identical, Cursor `trainer.mdc`, Windsurf `trainer.md`. Run `scripts/verify_trainer_sync.sh`.
