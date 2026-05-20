# Agent prompt template

Copy this file, replace every `<bracketed>` placeholder, run the falsifier checklist (`../references/falsifier-checklist.md`), paste into a fresh agent chat.

**Portability note:** assumes Cascade-on-Windsurf tool semantics (`run_command`, `Cwd` parameter, `read_file`/`edit` tools, gitignored-write guard). Adapt per-runner for Claude Code, Cursor, or other.

**Wall-clock estimate:** state up front (format: "Expected duration: ~N min from baseline to commit, plus ~M min for operator review").

---

## Header fields

- **Role:** `<code | sweep | prose-audit>` (default: `code`). See `references/role-overlays.md` for substitutions.
- **Phase:** `<N>` (default: `1`). Phase 2+ agents wait for the operator to confirm Phase 1 has landed before they spawn.
- **Owned-paths:** (optional; required when scope > 3 files OR sibling agents touch adjacent directories)

  | Agent | Owned paths |
  |---|---|
  | <self> | `<path1>`, `<path2>` |
  | <sibling-N> | `<path3>` (do NOT touch) |

## Context

You're working on `<PROJECT_NAME>`, located at `<ABSOLUTE_PROJECT_PATH>`. <ONE_PARAGRAPH_PROJECT_DESCRIPTION>. The operator is `<OPERATOR_NAME>`; they are <BRIEF_OPERATOR_STATE: "writing prose in X right now" / "running pipeline" / "studying" / "off-duty">.

Your working directory is `<ABSOLUTE_WORKTREE_PATH>` (set up below). Use the `Cwd` parameter on every `run_command`. Do NOT `cd a && b`; that violates safe-terminal Tier-1 #4.

**Expected duration:** ~`<N>` min from baseline capture to commit.

## Worktree setup (run first, before any other commands)

Default: every isolated agent works in a dedicated git worktree. This prevents collision with parallel agents on `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.git/index.lock`, and friends.

### Step 0: Gitignore pre-flight (project-local worktrees only)

Verify the worktree directory is gitignored before creating it. If not, add it and commit.

```bash
git -C <ABSOLUTE_PROJECT_PATH> check-ignore -q .worktrees 2>/dev/null \
  || { echo ".worktrees not gitignored; STOP and report"; exit 1; }
```

Skipping this risks polluting the main checkout's git status with worktree contents.

### Step 1: Create the worktree

```bash
git -C <ABSOLUTE_PROJECT_PATH> worktree add <ABSOLUTE_PROJECT_PATH>/.worktrees/<TASK_SLUG>
# All subsequent commands run with Cwd=<ABSOLUTE_PROJECT_PATH>/.worktrees/<TASK_SLUG>
```

### Step 2: Project-setup auto-detect

Run the install command that matches the manifest in the worktree. First match wins; only one path runs.

```bash
[ -f package.json ]      && npm install
[ -f Cargo.toml ]        && cargo build
[ -f pyproject.toml ]    && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
[ -f requirements.txt ]  && python -m venv .venv && .venv/bin/pip install -r requirements.txt
[ -f go.mod ]            && go mod download
```

For Python, the worktree-local venv is mandatory: without it your `pip install` corrupts the operator's main `.venv` mid-flight.

### Step 3: Clean-baseline verification

Run the test suite once before any edits. If it fails, STOP and report rather than attributing failures to your own work later.

**Same-tree exception (skip worktree):** ONLY if scope is single-file read-mostly AND operator confirms no parallel work in main checkout. State in your first-step output: "Skipping worktree per operator authorization; scope is `<files>`."

## First steps (mandatory, in order)

1. Invoke the `trainer` skill. Read its body in full.
2. Declare your task tier: "This task is `<vibe-safe / vibe-light / vibe-careful>` and `<mechanical / judgment-required>`. Routing: form-check `<tier>`. <Coaching-needed-or-not> for the work below."
3. Read `<PROJECT_CLAUDE_OR_AGENTS_MD>` in full.
4. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff, plus any project-specific voice rules.

## Capture the baseline (richer than count alone)

```bash
.venv/bin/pytest --timeout 30 -q 2>&1 | tee /tmp/<task-slug>-baseline-pytest.log | tail -1   # capture count
grep -E 'FAILED|ERROR' /tmp/<task-slug>-baseline-pytest.log > /tmp/<task-slug>-baseline-failing.txt || true   # capture failing-test names
.venv/bin/ruff check . 2>&1 | tail -1                  # lint state
.venv/bin/mypy <SCOPE> 2>&1 | tail -5                  # if applicable
git rev-parse HEAD                                     # baseline SHA
```

Save baseline (count + failing-test names + HEAD SHA + lint state). End-state verification:

1. Test count is same or higher than baseline
2. Failing-test names after edits == failing-test names at baseline (no swap; no pre-existing failure left while a new failure is introduced)
3. HEAD has advanced by your commit(s)
4. Lint state is clean or matches baseline

## Task

<SPECIFIC_TASK_DESCRIPTION>

- <CONCRETE_DELIVERABLE_1>
- <CONCRETE_DELIVERABLE_2>
- <CONCRETE_DELIVERABLE_3>

## Out of scope (do NOT touch)

- <REVIEW_GATED_FILES_OR_DIRS>
- <OPERATOR_PROSE_FILES_IF_ANY>
- <FILES_OTHER_AGENTS_ARE_TOUCHING>
- <ANYTHING_ELSE_OUT_OF_SCOPE>

## Decision protocol for surprises

If you encounter <SPECIFIC_AMBIGUITY_OR_BLOCKER_THE_OPERATOR_ANTICIPATES>: <stop-and-report / use-this-default / ask-via-output>.

**Stop-and-report channel (explicit):** you have no synchronous channel to the operator. "STOP and report" means: stop the work, emit a clear chat message stating what blocked you, and wait. The operator checks chat at batch review. Do NOT loop to escalate; do NOT silently work around the blocker.

## Vibe-careful protocol (source-edit definition)

Applies to any task tier above vibe-safe. "Source edit" is sharp:

**Allowed without operator review:**

- `# type: ignore[<error-code>]  # TODO: <reason>` at the offending line (comment-only suppression with auditable error code)
- New `# noqa: <error-code>` comments
- Pure comment edits, docstring edits
- Whitespace-only changes (trailing-whitespace cleanup, line endings)

**STOP and report (do NOT commit):**

- Adding new type annotations to functions that lacked them
- Changing parameter types or return types
- Renaming variables, functions, classes (rename affects import names if exported)
- Default-value changes
- Decorator changes
- Bare `# type: ignore` without error code (hides future regressions)
- Adding new imports for the purpose of fixing types
- Logic changes of any kind, even "obviously equivalent" refactors

## Verification

**Scope-match rule:** verification commands must check ONLY files in the Task in-scope list above, OR include explicit expected-residual notes for any broader checks. A grep over `docs/ tests/ voc/` when the task only swept `docs/ tests/` is either a false-failure (voc/ has residuals you didn't touch) or scope-creep (you decided to touch voc/ to make verification pass).

```bash
<TASK_SPECIFIC_VERIFICATION_COMMANDS>

.venv/bin/pytest --timeout 30 -q 2>&1 | tee /tmp/<task-slug>-after-pytest.log | tail -1
grep -E 'FAILED|ERROR' /tmp/<task-slug>-after-pytest.log > /tmp/<task-slug>-after-failing.txt || true
diff /tmp/<task-slug>-baseline-failing.txt /tmp/<task-slug>-after-failing.txt
# Expected: no diff (failing-test names unchanged); count same or higher

.venv/bin/ruff check .                                 # clean or matches baseline
```

## Structured-file validation (if task edits TOML, YAML, or JSON)

Before committing any structured-file edit, parse-and-validate:

```bash
# TOML:
python -c "import tomllib; tomllib.loads(open('pyproject.toml','rb').read())" && echo "TOML valid"

# YAML:
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "YAML valid"

# JSON:
python -m json.tool <file> > /dev/null && echo "JSON valid"
```

If validation fails, fix the edit before committing. A botched structured-file edit leaves the project un-buildable until rollback.

## Commit + DO NOT PUSH

One or more commits. Title format (single-line `-m` for titles only; multi-line bodies require `git commit -F /tmp/<project>_<task>_msg.txt` per safe-terminal Tier-1 #1):

```
<conventional-commit-type>(<scope>): <imperative title>
```

**Do not push.** The operator pushes at end of the batch after reviewing all parallel agent commits.

## Write session log (after commit, before return)

Write to `<ABSOLUTE_PROJECT_PATH>/localonly/session-logs/<DATE>-agent<N>-<task-slug>.md` using the shape at `~/.claude/skills/superset.skill/templates/session-log.md`. The `localonly/` directory must be gitignored (verify: `grep '^localonly' <project>/.gitignore`). The log is for periodic harness review; never enters version control.

## Return

```
Baseline HEAD SHA: <sha>
Baseline test count: <N> passed
<TASK_SPECIFIC_METRICS>
Tests after: <N> passed, 0 new failures
Ruff: clean
Commit SHA(s): <list>
Pushed: NO
Session log: <full path>
```

If anything blocks, STOP and report (emit a clear chat message and wait; no auto-escalation). Do not invent files. Do not edit outside scope. Do not push.

## Operator merge-back (for reference; not your job)

At end of batch, the operator runs:

```bash
cd <ABSOLUTE_PROJECT_PATH>
git merge <agent-branch>          # fast-forward or merge commit
git worktree remove <ABSOLUTE_PROJECT_PATH>/.worktrees/<TASK_SLUG>
```

You do NOT do this. Stay in your worktree until the operator confirms merge.
