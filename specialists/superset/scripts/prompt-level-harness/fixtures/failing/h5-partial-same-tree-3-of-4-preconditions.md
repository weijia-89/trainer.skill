# Worker prompt: agent-4, audit row in `application_index.html`

## Role declaration

You are worker **agent-4-applyindex-audit-v2** for the career-help row-audit batch. Operator is Wei.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/toren/CLAUDE.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (same-tree exception)

Per superset v0.5.0 Proposal 2, this dispatch uses the **same-tree exception**. The preconditions:

- **Single-file scope:** only `applications/application_index.html` is read.
- **Read-mostly task:** task is an audit; no edits planned.
- **No parallel work:** operator confirmed no sibling agents touching this checkout.

This fixture intentionally omits the fourth precondition from the bullet list above. The fourth bullet would normally constrain the agent against touching review-gated artifacts (the kind that live under `docs/specs/` or any other operator-frozen-doc directory), and its absence is what the H5 validator should detect.

The mandatory baseline-state captures:

```bash
git -C $HOME/Projects/career-help branch --show-current
git -C $HOME/Projects/career-help status --short
```

### Escalation-void clause

If the task escalates mid-flight from read-mostly to edit, the same-tree exception voids. The agent halts and escalates to the operator.

## Task

Audit `applications/application_index.html` against the master apply list.

## Out of scope

- All edits to `applications/application_index.html`.

## Session log

Write to `$HOME/Projects/toren/localonly/session-logs/2026-05-19-agent4-applyindex-audit.md`.
