# Worker prompt: agent-7, refactor `auth/session.py` for token rotation

## Role declaration

You are worker **agent-7-session-token-rotation** for the auth-cleanup batch. Operator is Wei.

## First steps (mandatory, in order)

1. Invoke `trainer` skill. Read body in full.
2. Declare tier: vibe-careful, judgment-required.
3. Read `$HOME/Projects/example-app/CLAUDE.md`.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff.

## Worktree setup (run first, before any other commands)

Default isolated-agent posture. Prevents collision with sibling agents on `.pytest_cache`, `.ruff_cache`, and `.git/index.lock`.

### Step 0: Gitignore pre-flight

```bash
git -C $HOME/Projects/example-app check-ignore -q .worktrees 2>/dev/null \
  || { echo ".worktrees not gitignored; STOP and report"; exit 1; }
```

### Step 1: Create the worktree

```bash
git -C $HOME/Projects/example-app worktree add $HOME/Projects/example-app/.worktrees/session-token-rotation
```

All subsequent commands run with `Cwd=$HOME/Projects/example-app/.worktrees/session-token-rotation`.

### Step 2: Project setup auto-detect

```bash
[ -f pyproject.toml ] && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

### Step 3: Clean-baseline verification

```bash
.venv/bin/pytest --timeout 30 -q 2>&1 | tee /tmp/agent-7-baseline.log | tail -1
```

## Task

Refactor `auth/session.py` to support sliding-window token rotation. Add tests under `tests/auth/`.

## Out of scope

- `docs/specs/`
- `auth/oauth.py` (sibling agent owns)

## Commit + DO NOT PUSH

Single commit, conventional title. Operator pushes at end of batch.

## Session log

Write to `$HOME/Projects/example-app/localonly/session-logs/2026-05-19-agent7-session-token-rotation.md`.
