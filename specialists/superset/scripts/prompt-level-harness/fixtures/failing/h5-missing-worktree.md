# Worker prompt: agent-2, add retry wrapper to `api/client.py`

## Role declaration

You are worker **agent-2-api-retry-wrapper** for the resilience batch. Operator is Wei.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/example-app/CLAUDE.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Setup

Run the test suite once before any edits to confirm a green baseline.

```bash
.venv/bin/pytest --timeout 30 -q 2>&1 | tee /tmp/agent-2-baseline.log | tail -1
```

This prompt does NOT contain any worktree setup, does NOT declare a same-tree exception, and is NOT for a no-git project. This is the H5 failure mode: the worker has no instructions about isolation and will collide with sibling agents on `.pytest_cache` and `.git/index.lock`.

## Task

Add an exponential-backoff retry wrapper around the HTTP client in `api/client.py`. Tests under `tests/api/test_client_retry.py`.

## Out of scope

- `docs/specs/`
- `api/auth.py` (sibling agent owns)

## Commit + DO NOT PUSH

Single commit, conventional title. Operator pushes at end of batch.

## Session log

Write to `$HOME/Projects/example-app/localonly/session-logs/2026-05-19-agent2-api-retry-wrapper.md`.

## Decision protocol for surprises

If the retry wrapper interacts with an existing circuit-breaker library, stop and report rather than refactoring around it.

## Return

```
Baseline HEAD SHA: <sha>
Baseline test count: <N> passed
Tests after: <N> passed, 0 new failures
Ruff: clean
Commit SHA(s): <list>
Pushed: NO
Session log: <full path>
```

If anything blocks, STOP and report. Do not invent files. Do not edit outside scope.
