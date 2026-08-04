---
name: spotter
description: |
  Use when CI is red, a PR check failed, GitHub Actions is broken, or a deploy pipeline won't pass. Symptoms: "why is CI failing," "the check is red," "shellcheck rejected my script," "verify_trainer_sync.sh failed," "generation gate blocked the PR," "workflow syntax error," "missing permission in Actions." The spotter diagnoses the failure, prescribes the fix, and teaches how to avoid the same class of failure next time. Composes with pr (deploy-time pipeline) and form-check (code-level correctness).
type: project-skill
version: 1.0.0
authors: Wei Jia (2026-08-03)
license: LicenseRef-IronLaw-NC-1.0
required_tools: [file_read, shell]
recommended_tools: [git, grep]
optional_tools: [web_search]
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: validates bash correctness, shellcheck compliance, and generation gate rules
  - skill: pr
    version: ">=2.0.0,<3.0.0"
    role: deploy pipeline rollback and post-merge verification
---

# spotter: when CI is red, find the fix fast

```
IRON LAW: NEVER PUSH TO FIX CI WITHOUT RUNNING THE FAILING CHECK LOCALLY FIRST.
```

Violating the letter of this rule is violating the spirit of this rule. "I'll just push and see if it passes" is the rationalization that turns a one-line fix into a five-commit noise spiral. Every push consumes CI minutes, pollutes the git history, and trains the operator to ignore red checks. Run it locally. Fix it locally. Then push once.

## Red Flags. STOP and diagnose

- "It's just a flaky test, I'll re-run." - Flaky tests are bugs. Track them; do not normalize them.
- "The check passed on my machine." - Your machine is not CI. Environment drift is the first suspect.
- "I'll add a quick commit to fix it." - Quick commits without local verification are gambling.
- "CI is red but the change is trivial." - Trivial changes break CI when they touch paths the check guards.
- "I'll skip the dry-run, the script looks fine." - Looks fine is not `bash -n` clean.

## Rationalizations, what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "Re-running CI usually fixes it" | If re-running fixes it, the test or check is flaky. Flaky checks erode trust and hide real failures. |
| "I don't have time to run the full suite locally" | A five-minute local run beats a twenty-minute push-fix-push cycle. |
| "The error is in CI infrastructure, not my code" | CI infrastructure is part of the shipping path. If it breaks, you still cannot merge. |
| "Shellcheck is too picky" | Shellcheck catches real bugs (word-splitting, unquoted variables, exit-code swallowing). Its warnings are cheaper than production incidents. |
| "I'll fix the lint errors in a follow-up PR" | Follow-up PRs for lint are theater. Fix before merge. |

## Keywords for discovery

CI failed, GitHub Actions broken, workflow error, check red, shellcheck failed, bash syntax error, generation gate blocked, verify script failed, pipeline broken, deploy check failed, lint error in CI, permission denied in Actions, missing secret in CI, checkout failed, concurrency conflict, job timeout.

## Scope

Diagnose and fix CI/CD failures for the trainer.skill ecosystem and downstream product repos. Covers GitHub Actions workflows, shell scripts, Python verification scripts, and pre-commit gates.

**Not for:** production incident response (use `diet`), code review (use `form-check`), deploy execution (use `pr`).

## How to invoke

1. **CI is red on a PR:** First check if `origin/main` (or target branch) is also red. If main is red, the failure is not caused by this PR. If main is green, read the failing job log. Match the error to a pattern in `references/ci-fix-patterns.md`. Run the matching verification locally. Fix. Re-run locally until green. Push.
2. **Shell script rejected by generation gate:** Read `specialists/form-check/tools/generation_gate.sh --help`. Run with `--strict`. Fix every failure class. Re-run until exit 0.
3. **Workflow YAML syntax error:** Run `python3 -c "import yaml, sys; f=open(sys.argv[1]); yaml.safe_load(f); f.close()" .github/workflows/...`. Fix the parse error. Validate structure against `references/ci-fix-patterns.md` § Workflow YAML.
4. **verify_trainer_sync.sh failed:** Read the invariant that failed. Fix the source file, not the verify script. Re-run until PASS.

## Diagnosis flow

### Step 1: Read the failure log exactly

Do not guess. Copy the last 30 lines of the failing job log. Identify:
- **Which job** failed (name in `jobs:`)
- **Which step** failed (name in `steps:`)
- **Exit code** (0, 1, 2, 3, or signal)
- **File and line** if reported

### Step 2: Classify the failure

Use the table in `references/ci-fix-patterns.md`. Common classes:

| Class | Signature | Local verify |
|---|---|---|
| Bash syntax | `bash: syntax error near unexpected token` | `bash -n script.sh` |
| Shellcheck | `SC2086: Double quote to prevent globbing` | `shellcheck script.sh` |
| Generation gate | `FAIL: missing set -euo pipefail` | `bash specialists/form-check/tools/generation_gate.sh --strict script.sh` |
| Verify sync | `Invariant N FAIL` | `bash scripts/verify_trainer_sync.sh` |
| YAML syntax | `mapping values are not allowed here` | `python3 -c "import yaml; yaml.safe_load(open('file'))"` |
| Missing permission | `Resource not accessible by integration` | Read workflow `permissions:` block |
| Unpinned action | `actions/checkout@v4` without SHA | Check `uses:` line for commit SHA |
| Path drift | `No such file or directory` in CI only | Compare `pwd` in CI vs local |
| Secret missing | `Error: Input required and not supplied: TOKEN` | Check `env:` and repository secrets |
| Concurrency cancel | `cancelled` after `concurrency: group` | Check if another run triggered the cancel |

### Step 3: Fix locally with regression check

Edit the file. Run the local verify command from the table. Then run the repo's full test suite or verify command to ensure the fix did not break anything else. Do not push until both the original failure and the full suite pass.

**Iteration cap:** If you have gone through Steps 1-3 more than 3 times for the same failure, stop and escalate to the operator. You may be chasing a flaky test, an external dependency issue, or a failure mode outside this catalog.

### Step 4: Push and confirm

Push the fix. Wait for CI. If still red, return to Step 1 with the new log.

## Common fix patterns (quick reference)

### Bash script fails `bash -n`

- Missing `fi`, `done`, or `}`
- `$(...)` not closed
- Heredoc delimiter mismatch
- Fix: run `bash -n script.sh`, fix the line it names

### Shellcheck warnings

- `SC2086` - double-quote variables: `"$VAR"` not `$VAR`
- `SC2046` - quote `find` results: `while IFS= read -r f; do ... done <<< "$(find ...)"`
- `SC2002` - useless cat: use `< file cmd` or `cmd file`
- Fix: run `shellcheck script.sh`, apply every warning

### Generation gate strict mode

- Missing `set -euo pipefail` at top
- `cd dir && cmd` chain - use `cd dir || exit; cmd`
- Heredoc outside usage/help block
- Missing tool existence check (`command -v tool`)
- Fix: run `generation_gate.sh --strict script.sh`

### verify_trainer_sync.sh invariant failure

- Invariant 1: canonical vs mirror divergence - re-sync mirror
- Invariant 6: em-dash found - replace with " - "
- Invariant 11: context budget exceeded - trim SKILL.md
- Fix: read the invariant description in the script, fix the root cause

### Workflow YAML errors

- Bad indentation (spaces, not tabs)
- `on:` trigger syntax (e.g., `pull_request:` needs sub-keys)
- `env:` at job level vs step level
- Missing `permissions:` block
- Fix: validate with Python yaml parser, then read `references/ci-fix-patterns.md` § Workflow

## Pre-flight checklist (before any push)

Run these on every branch that will become a PR. Adapt commands to the repo's actual structure:

```bash
# Bash syntax
find scripts -name "*.sh" -exec bash -n {} \;

# Shellcheck (if available)
if command -v shellcheck &>/dev/null; then
  find scripts -name "*.sh" -exec shellcheck {} \;
fi

# Generation gate on modified .sh files (if generation gate exists)
changed=$(git diff --name-only origin/main 2>/dev/null | grep '\.sh$' || true)
if [[ -n "$changed" ]] && [[ -f specialists/form-check/tools/generation_gate.sh ]]; then
  file_args=()
  while IFS= read -r f; do
    [[ -n "$f" ]] && file_args+=("$f")
  done <<< "$changed"
  bash specialists/form-check/tools/generation_gate.sh --strict "${file_args[@]}"
fi

# verify_trainer_sync.sh (trainer.skill only)
if [[ -f scripts/verify_trainer_sync.sh ]]; then
  bash scripts/verify_trainer_sync.sh
fi

# Context budget (trainer.skill only)
if [[ -f tests/context_budget/check_context_budget.py ]]; then
  python3 tests/context_budget/check_context_budget.py
fi
```

If any of these fail, fix before push. This is the spotter's core teaching: local verification is cheaper than CI roulette.

## Composition with other skills

- **Before CI fix:** `form-check` reviews the script or workflow change.
- **During CI fix:** spotter (this skill) diagnoses and fixes.
- **After CI fix:** `pr` verifies the deploy pipeline is still valid; `form-check` generation gate re-runs.
- **If CI failure reveals a production issue:** hand off to `diet` for incident response.

## Related files

- `references/ci-fix-patterns.md` - full catalog of failure signatures and fixes
- `specialists/form-check/tools/generation_gate.sh` - bash validation gate
- `specialists/form-check/tools/llm_code_gate.sh` - language-agnostic correctness gate
- `scripts/verify_trainer_sync.sh` - trainer invariants
- `.github/workflows/trainer-pr-review-gate.yml` - this repo's CI
