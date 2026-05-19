# Worker prompt: agent-5, audit row in `application_index.html`

## Role declaration

You are worker **agent-5-applyindex-audit-v3** for the career-help row-audit batch. Operator is Wei.

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

This fixture intentionally omits the v0.5.0 Proposal 3 baseline-state commands. Normally a same-tree dispatch starts with two read-only git invocations that capture the current branch and the dirty-state of the working tree, and these are required by Proposal 3 to be the very first two `run_command` calls. Their absence is what the H5 validator should detect.

### Escalation-void clause

If the task escalates mid-flight from read-mostly to edit, the same-tree exception voids. The agent halts and escalates to the operator.

## Task

Audit `applications/application_index.html` against the master apply list.

## Out of scope

- All edits to `applications/application_index.html`.

## Session log

Write to `$HOME/Projects/toren/localonly/session-logs/2026-05-19-agent5-applyindex-audit.md`.

## Return

```
Status: DONE | FAILED | BLOCKED
Audit findings: <count>
Rows in index missing from master: <list>
Rows in master missing from index: <list>
Session log: <full path>
```

If anything blocks, STOP and report. Do not invent files. Do not edit outside scope.
