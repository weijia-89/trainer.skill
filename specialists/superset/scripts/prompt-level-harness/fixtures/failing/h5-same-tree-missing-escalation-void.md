# Worker prompt: agent-6, audit row in `application_index.html`

## Role declaration

You are worker **agent-6-applyindex-audit-v4** for the career-help row-audit batch. Operator is Wei.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/toren/CLAUDE.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (same-tree exception)

Per superset v0.5.0 Proposal 2, this dispatch uses the **same-tree exception**. All four preconditions hold:

- **Single-file scope:** only `applications/application_index.html` is read.
- **Read-mostly task:** task is an audit; no edits planned.
- **No parallel work:** operator confirmed no sibling agents touching this checkout.
- **No gated-doc edits:** the file is the audit target, not a `docs/specs/*` review-gated artifact, and no gated-doc edits are in scope.

The first two `run_command` calls in this dispatch are the v0.5.0 Proposal 3 mandatory baseline-state captures:

```bash
git -C $HOME/Projects/toren branch --show-current
git -C $HOME/Projects/toren status --short
```

This fixture is intentionally missing the escalation-void clause. Without it, an audit that surfaces a discrepancy requiring an edit could silently commit the edit from the same-tree checkout, defeating the purpose of the four preconditions.

## Task

Audit `applications/application_index.html` against the master apply list.

## Out of scope

- All edits to `applications/application_index.html`.

## Session log

Write to `$HOME/Projects/toren/localonly/session-logs/2026-05-19-agent6-applyindex-audit.md`.

## Return

```
Status: DONE | FAILED | BLOCKED
Audit findings: <count>
Rows in index missing from master: <list>
Rows in master missing from index: <list>
Session log: <full path>
```

If anything blocks, STOP and report. Do not invent files. Do not edit outside scope.
