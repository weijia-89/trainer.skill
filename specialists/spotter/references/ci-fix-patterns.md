# CI fix patterns

Catalog of CI failure signatures, root causes, and fixes for the trainer.skill ecosystem and downstream repos.

## Bash scripts

### Syntax error: `bash: syntax error near unexpected token`

**Root cause:** Unclosed `if`, `for`, `while`, `case`, or quote. Missing space after `[` in tests.

**Fix:**
```bash
bash -n script.sh
```
Fix the exact line the parser names.

**Prevention:** Run `bash -n` before every commit that touches `.sh` files.

### `SC2086: Double quote to prevent globbing and word splitting`

**Root cause:** Unquoted variable expansion: `$VAR` instead of `"$VAR"`.

**Fix:** Quote every variable that holds a path, filename, or user input.

**Example:**
```bash
# Bad
rm $FILE

# Good
rm "$FILE"
```

### `SC2046: Quote this to prevent word splitting`

**Root cause:** Unquoted `$(...)` or backtick output used as argument list.

**Fix:** Use `while read` loop or array.

**Example:**
```bash
# Bad
for f in $(find . -name "*.sh"); do ... done

# Good
while IFS= read -r f; do
  [[ -n "$f" ]] && ...
done <<< "$(find . -name "*.sh")"
```

### `SC2164: Use 'cd ... || exit' in case cd fails`

**Root cause:** `cd` without failure handling.

**Fix:**
```bash
cd dir || exit 1
```

### Generation gate: missing `set -euo pipefail`

**Root cause:** Script lacks safety header.

**Fix:** Add as the first line after shebang:
```bash
#!/usr/bin/env bash
set -euo pipefail
```

### Generation gate: `cd &&` chain

**Root cause:** `cd dir && cmd` silently ignores `cd` failure.

**Fix:**
```bash
cd dir || exit 1
cmd
```

### Generation gate: heredoc outside usage/help

**Root cause:** Here-document used for inline data instead of usage block.

**Fix:** Move data to a file or use `printf`. If the heredoc is usage/help, ensure it is inside a `usage()` function.

## Python scripts

### `SyntaxError: invalid syntax`

**Root cause:** Python version mismatch (f-strings in 3.5, walrus in 3.7), missing colon, unclosed paren.

**Fix:**
```bash
python3 -m py_compile script.py
```

### `ModuleNotFoundError: No module named '...'`

**Root cause:** Missing dependency in CI environment.

**Fix:** Add to `requirements.txt`, `pyproject.toml`, or CI `pip install` step. Do not rely on system packages.

### `json.tool` fails on `results/schema.json`

**Root cause:** Trailing comma, unclosed brace, or single quotes in JSON.

**Fix:**
```bash
python3 -m json.tool results/schema.json > /dev/null
```

## GitHub Actions workflows

### Secret leakage in CI logs

**Root cause:** Environment variables, tokens, or keys printed in job output.

**Fix:**
1. Immediately rotate any exposed secret.
2. Add `::add-mask::` for workflow-generated values.
3. Audit `env:` and `with:` blocks for accidental exposure.
4. Check if `set -x` or debug flags are enabled in scripts.

### `mapping values are not allowed here`

**Root cause:** YAML indentation error. Tabs instead of spaces. Missing colon.

**Fix:**
```bash
python3 -c "import yaml, sys; f=open(sys.argv[1]); yaml.safe_load(f); f.close()" .github/workflows/file.yml
```

### `Resource not accessible by integration`

**Root cause:** Workflow lacks `permissions:` block or requests scope it does not have.

**Fix:** Add explicit permissions:
```yaml
permissions:
  pull-requests: read
  contents: read
```

### Unpinned action version

**Root cause:** `uses: actions/checkout@v4` instead of commit SHA.

**Fix:** Pin to SHA:
```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.1.2
```

### Job cancelled by concurrency group

**Root cause:** `concurrency: group` with `cancel-in-progress: true` and a newer push triggered.

**Fix:** This is expected behavior. If you need the old run to finish, push less frequently or remove `cancel-in-progress: true`.

### `Error: Input required and not supplied: TOKEN`

**Root cause:** `env:` or `with:` references a secret that is not set in the repository.

**Fix:** Add the secret in repository Settings > Secrets. Or use `github.token` for built-in permissions.

## Trainer-specific checks

### `verify_trainer_sync.sh` invariant failure

Read the invariant number and description printed by the script. Common ones:

| Invariant | Failure | Fix |
|---|---|---|
| 1 | Canonical vs mirror divergence | `cp SKILL.md ~/.cursor/skills/trainer/SKILL.md` (or appropriate mirror path) |
| 6 | Em-dash found in tracked Markdown | Replace Unicode em-dash with " - " |
| 11 | Context budget exceeded | Trim SKILL.md or bump budget.toml cap with justification |
| 12 | Code-review loop routing wrong | Check `references/trainer-codereview.md` matches `verify_autonomous_code_review.py` |
| 14 | R-6 docs gate missing | Add doc updates to PR |

### `generation_gate.sh --strict` failure

Run the gate with the failing file. The gate prints the rule violated. Fix and re-run.

### `ci-trainer-pr-review-gate.sh` failure

**Root cause:** Missing canonical trainer comment on PR, or comment `head=` does not match PR HEAD.

**Fix:** Run `scripts/trainer_pr_review_post.sh` to post or PATCH the comment. Ensure `head=` matches the current commit SHA.

## Cross-repo patterns (buds / toebeans)

### Flutter test fails in CI but passes locally

**Root cause:** Different Flutter version, missing `flutter pub get`, or goldens mismatch.

**Fix:** Pin Flutter version in CI. Run `flutter pub get` in workflow. Check golden file platform differences.

### Gradle build fails in CI

**Root cause:** Missing JDK, wrong Gradle version, or cached state.

**Fix:** Pin JDK and Gradle versions. Run `./gradlew clean` in workflow if caches are stale.

### Cross-repo path leak

**Root cause:** Script hardcodes `~/Projects/buds/...` in a toebeans PR, or vice versa.

**Fix:** Use relative paths or repo-root detection. `trainer_pr_review_post.sh` rejects cross-repo paths.

## Emergency bypasses

Every gate has a bypass. Bypasses are logged, not hidden.

| Gate | Bypass | Log location |
|---|---|---|
| generation_gate.sh | `GENERATION_GATE_BYPASS=1` | `.recovery/calibration.jsonl` |
| verify_trainer_sync.sh | Edit script (not recommended) | Commit message |
| CI workflow | Admin force-merge | GitHub audit log |

Bypass without logging is a policy violation. Log it.
