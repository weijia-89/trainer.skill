# PR — max-effort day; passes-tests → in-production

A skill for going from "passes tests on my machine" to "running in production."

## What it does

`pr` covers the deploy phase. The gap between `recovery/launch-ready` and `diet/steady-state`.

Seven sections:

1. Pre-deploy checklist (env vars documented, secrets not in repo, lockfile committed, clean build, health-check endpoint, log access)
2. Platform-specific patterns (static sites, Node services, Python services, containerized services)
3. The deploy itself
4. Post-deploy verification (the 30-minute checklist after pressing deploy)
5. Rollback procedure (platform-rollback and code-rollback paths)
6. When the deploy is failing (common failure modes and their fixes)
7. Anti-patterns

The pre-deploy checklist and post-deploy verification are the load-bearing parts. Beginners who skip them ship broken deploys; beginners who walk them produce reliable deploys regardless of which platform they use.

## When to invoke

- You are about to do your first deploy of a new project.
- You are about to do a routine re-deploy and want a sanity check.
- Your deploy is failing and you need triage.
- You need to roll back and want the right path (platform or code-level).

## When to skip

- You are pre-deploy. Use `recovery` for the quality engagement that gets you ready.
- You are post-deploy and in steady state. Use `diet` for instrumentation and cadence.

## Composes with

- `form-check` — the reversibility and blast-radius rubric components inform deploy decisions.
- `diet` — handoff after a successful deploy (steady state) or during an incident (rollback).
- `safetybar` — code-level rollback uses `git revert` per `safetybar §2.2`.

## What this skill protects against

The "works on my machine" failure mode. The pre-deploy checklist (§1) makes the most common reasons for it visible before you press deploy: missing env vars, lockfile drift, missing health check, no log access.

The Friday-afternoon deploy failure mode. The skill makes the underlying rule explicit: do not deploy when you cannot roll back in the next hour. Day-of-week is a heuristic; rollback-window availability is the rule.

## Files

- `SKILL.md` — the seven sections
- `CHANGELOG.md` — version history
- This file

## License

MIT.
