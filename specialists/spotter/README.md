# spotter

CI/CD failure diagnosis and fixing specialist for the trainer ecosystem.

## What the spotter does

When CI is red, the spotter reads the failure log, classifies the error, and prescribes the fix. It teaches how to avoid the same class of failure next time. The core discipline: diagnose locally before pushing.

## When to load

- CI check failed on a PR
- Shellcheck rejected a script
- Generation gate blocked merge
- Workflow YAML has syntax errors
- `verify_trainer_sync.sh` reports invariant failures
- Missing permission in GitHub Actions

## How it works

1. **Check target branch first** - if `origin/main` is also red, the PR did not cause it
2. **Read the failure log** - identify job, step, exit code, file, line
3. **Classify** - match against `references/ci-fix-patterns.md`
4. **Fix locally** - edit, verify, run full suite for regression check
5. **Push once** - iteration cap of 3 rounds; escalate if exceeded

## Files

- `SKILL.md` - full routing and discipline
- `references/ci-fix-patterns.md` - catalog of failure signatures and fixes

## Composition

- **Before:** `form-check` reviews the script or workflow change
- **During:** `spotter` (this skill) diagnoses and fixes
- **After:** `pr` verifies deploy pipeline; `form-check` generation gate re-runs
- **Production issue:** hand off to `diet`
