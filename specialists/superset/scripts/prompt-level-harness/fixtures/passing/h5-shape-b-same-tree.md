# Worker prompt: agent-3, audit row in `application_index.html`

## Role declaration

You are worker **agent-3-applyindex-audit** for the career-help row-audit batch. Operator is Wei. No sibling agents touching this checkout right now.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/toren/CLAUDE.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (same-tree exception)

Per superset v0.5.0 Proposal 2, this dispatch uses the **same-tree exception** (skip worktree). All four preconditions hold:

- **Single-file scope:** only `applications/application_index.html` is read.
- **Read-mostly task:** task is an audit; no edits planned until findings surfaced and operator authorizes.
- **No parallel work:** operator confirmed no sibling agents touching this checkout.
- **No gated-doc edits:** the file is the audit target, not a `docs/specs/*` review-gated artifact, and no gated-doc edits are in scope.

The first two `run_command` calls in this dispatch are the v0.5.0 Proposal 3 mandatory baseline-state captures:

```bash
git -C $HOME/Projects/career-help branch --show-current
git -C $HOME/Projects/career-help status --short
```

These confirm the branch and dirty-state before any work begins.

### Escalation-void clause

If the task escalates mid-flight from read-mostly to edit (the audit discovers a row that needs adding, fixing, or removing), the same-tree exception voids. The agent halts and escalates to the operator. No edits commit until a worktree is set up and the operator authorizes the escalation.

## Task

Audit `applications/application_index.html` against the master apply list. Report rows present in one but not the other.

## Out of scope

- All edits to `applications/application_index.html`.
- All other `applications/` files.

## Decision protocol for surprises

Stop-and-report if you find a discrepancy that requires an edit. Do not commit.

## Session log

Write to `$HOME/Projects/toren/localonly/session-logs/2026-05-19-agent3-applyindex-audit.md`.
