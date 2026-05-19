# Worker prompt: agent-A4b, build secondary harness for `superset.skill`

## Role declaration

You are worker **agent-A4b-prompt-level-harness-h6** for the superset self-bootstrap batch. Operator is Wei. Two other workers running in parallel.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/superset.skill/SKILL.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (no-git exception)

The project `superset.skill` **is not a git repository**. The worktree pattern is therefore unavailable for this agent's work.

This fixture intentionally omits the parallel-collision-mitigation strategy. There is no owned-paths separation table, and no statement of how sibling-agent collisions are avoided in the absence of worktree isolation. Without that mitigation strategy, the no-git declaration alone is insufficient to resolve H5: sibling agents could still write to the same files concurrently, and the prompt offers no protocol for that case.

## Task

Build a secondary falsifier harness for **H6 alone** at `scripts/prompt-level-harness-h6/`.

## Out of scope

- `SKILL.md`, `CHANGELOG.md`, `references/falsifier-checklist.md`.
- Anything outside `scripts/prompt-level-harness-h6/`.

## Do NOT push, do NOT commit

No git in `superset.skill`. Orchestrator rsyncs your work into the trainer bundle after review.

## Decision protocol for surprises

If you discover a sibling agent overlapping your owned paths mid-flight, stop and report. Do not improvise a write-ordering.

## Session log

Write to `$HOME/Projects/superset.skill/localonly/session-logs/2026-05-19-A4b-prompt-level-harness-h6.md`.

## Return

```
Status: DONE | FAILED | BLOCKED
Files created: <count>
Session log: <full path>
PROMOTE? candidates discovered during work: <N>
```

If anything blocks, STOP and report. Do not invent files. Do not edit outside scope.
