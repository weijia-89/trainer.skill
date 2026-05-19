# Worker prompt: agent-A4a, build prompt-level harness for `superset.skill`

## Role declaration

You are worker **agent-A4a-prompt-level-harness** for the superset self-bootstrap batch. Operator is Wei. Two other workers running in parallel (A1, A2-A3).

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/superset.skill/SKILL.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (no-git exception)

The project `superset.skill` **is not a git repository**. The worktree pattern is therefore unavailable for this agent's work.

Parallel-collision risk is mitigated by **disjoint owned_paths** across all three sibling agents in this batch. The owned-paths table below confirms no two agents touch the same directory:

| Agent | Owned paths |
|---|---|
| A4a (this agent) | `scripts/prompt-level-harness/` |
| A1 (sibling) | `templates/meta-handoff-prompt.md` |
| A2-A3 (sibling) | `templates/orchestrator-handoff-prompt.md` |

Disjoint owned_paths means no two sibling agents write to the same file or directory, so concurrent edits cannot collide even without worktree isolation. State this in your session log.

## Task

Build a prompt-level falsifier harness for **H5 alone** at `scripts/prompt-level-harness/`. Three components: validator, fixtures, driver script.

## Out of scope

- `SKILL.md`, `CHANGELOG.md`, `references/falsifier-checklist.md`.
- `templates/meta-handoff-prompt.md` (A1 owns).
- `templates/orchestrator-handoff-prompt.md` (A2-A3 owns).
- Anything outside `scripts/prompt-level-harness/`.

## Do NOT push, do NOT commit

No git in `superset.skill`. Orchestrator rsyncs your work into the trainer bundle after review.

## Session log

Write to `$HOME/Projects/superset.skill/localonly/session-logs/2026-05-19-A4a-prompt-level-harness-h5.md`.
