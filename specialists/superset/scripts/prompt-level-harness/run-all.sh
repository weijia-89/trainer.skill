#!/usr/bin/env bash
# Prompt-level falsifier harness driver for H5 (worktree first command).
#
# Iterates over fixtures/passing/*.md and fixtures/failing/*.md, running the
# validator against each and asserting the expected verdict. Mirrors the
# style of scripts/falsifier-harness/run-all.sh (the manifest harness).
#
# Usage: bash scripts/prompt-level-harness/run-all.sh
# Exit code: 0 if all fixtures match expectation; non-zero on first mismatch.

set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$HARNESS_DIR/validate-worker-prompt.py"
FIXTURES_DIR="$HARNESS_DIR/fixtures"
PASSING_DIR="$FIXTURES_DIR/passing"
FAILING_DIR="$FIXTURES_DIR/failing"

if [[ ! -f "$VALIDATOR" ]]; then
  echo "FATAL: validator not found at $VALIDATOR" >&2
  exit 2
fi
if [[ ! -d "$PASSING_DIR" ]]; then
  echo "FATAL: passing-fixtures dir not found at $PASSING_DIR" >&2
  exit 2
fi
if [[ ! -d "$FAILING_DIR" ]]; then
  echo "FATAL: failing-fixtures dir not found at $FAILING_DIR" >&2
  exit 2
fi

passing_verified=0
failing_rejected=0
fail_lines=()

# Detect --project-type hint from fixture filename. Shape C fixtures (h5-shape-c-*
# and h5-no-git-*) pass --project-type=no-git so the validator scopes to Shape C only.
detect_project_type() {
  local fixture_path="$1"
  local base
  base="$(basename "$fixture_path")"
  case "$base" in
    h5-shape-c-* | h5-no-git-*)
      echo "no-git"
      ;;
    *)
      echo "git"
      ;;
  esac
}

run_one_passing() {
  local fixture="$1"
  local project_type
  project_type="$(detect_project_type "$fixture")"
  local stderr_file
  stderr_file=$(mktemp)
  python3 "$VALIDATOR" "$fixture" --project-type "$project_type" >/dev/null 2>"$stderr_file"
  local actual_exit=$?
  if [[ "$actual_exit" -eq 0 ]]; then
    passing_verified=$((passing_verified + 1))
    echo "PASS  passing fixture verified: $(basename "$fixture") (project-type=$project_type)"
  else
    fail_lines+=("FAIL  passing fixture rejected unexpectedly: $(basename "$fixture") (exit=$actual_exit)")
    fail_lines+=("      stderr: $(cat "$stderr_file" | head -10)")
  fi
  rm -f "$stderr_file"
}

run_one_failing() {
  local fixture="$1"
  local project_type
  project_type="$(detect_project_type "$fixture")"
  local stderr_file
  stderr_file=$(mktemp)
  python3 "$VALIDATOR" "$fixture" --project-type "$project_type" >/dev/null 2>"$stderr_file"
  local actual_exit=$?
  if [[ "$actual_exit" -ne 0 ]]; then
    failing_rejected=$((failing_rejected + 1))
    echo "PASS  failing fixture correctly rejected: $(basename "$fixture") (exit=$actual_exit, project-type=$project_type)"
  else
    fail_lines+=("FAIL  failing fixture passed unexpectedly: $(basename "$fixture") (exit=0)")
  fi
  rm -f "$stderr_file"
}

echo "=== superset H5 prompt-level harness ==="
echo ""

# Iterate passing fixtures.
for fixture in "$PASSING_DIR"/*.md; do
  [[ -f "$fixture" ]] || continue
  run_one_passing "$fixture"
done

echo ""

# Iterate failing fixtures.
for fixture in "$FAILING_DIR"/*.md; do
  [[ -f "$fixture" ]] || continue
  run_one_failing "$fixture"
done

echo ""
echo "=== summary ==="

if [[ ${#fail_lines[@]} -gt 0 ]]; then
  echo "MISMATCHES:"
  for line in "${fail_lines[@]}"; do
    echo "$line"
  done
  exit 1
fi

echo "H5 prompt-level harness: $passing_verified passing fixtures verified, $failing_rejected failing fixtures correctly rejected"
exit 0
