#!/usr/bin/env bash
# Mozilla-mythos-style falsifier harness driver for superset v0.4.0 daily-log manifest constraints.
#
# Treats each falsifier (H11 / H13 / H14 / H15 / freeze-list / valid-baseline) as a falsifiable
# hypothesis. For each, constructs a violating input (or a clean one for the baseline) and
# asserts the validator emits the expected outcome.
#
# Usage: bash scripts/falsifier-harness/run-all.sh
# Exit code: 0 if all hypotheses hold; non-zero with summary if any fail.

set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "$HARNESS_DIR/.." && pwd)"
VALIDATOR="$SCRIPTS_DIR/validate-daily-log.py"
FIXTURES_DIR="$HARNESS_DIR/fixtures"

if [[ ! -f "$VALIDATOR" ]]; then
  echo "FATAL: validator not found at $VALIDATOR" >&2
  exit 2
fi

pass_count=0
fail_count=0
fail_lines=()

# Each test: <name> <fixture-dir> <expected-exit> <expected-falsifier-id-or-NONE>
run_test() {
  local name="$1"
  local fixture_subdir="$2"
  local expected_exit="$3"
  local expected_falsifier="$4"

  local fixture_root="$FIXTURES_DIR/$fixture_subdir"
  local daily_log="$fixture_root/localonly/daily/2026-05-19.md"

  if [[ ! -f "$daily_log" ]]; then
    fail_count=$((fail_count + 1))
    fail_lines+=("FAIL  $name: fixture daily-log not found at $daily_log")
    return
  fi

  local stderr_file
  stderr_file=$(mktemp)
  python3 "$VALIDATOR" "$daily_log" --project-root "$fixture_root" >/dev/null 2>"$stderr_file"
  local actual_exit=$?

  local match_falsifier=0
  if [[ "$expected_falsifier" != "NONE" ]]; then
    if grep -q "\"falsifier\": \"$expected_falsifier\"" "$stderr_file"; then
      match_falsifier=1
    fi
  fi

  if [[ "$actual_exit" -eq "$expected_exit" ]]; then
    if [[ "$expected_falsifier" == "NONE" ]] || [[ $match_falsifier -eq 1 ]]; then
      pass_count=$((pass_count + 1))
      echo "PASS  $name (exit=$actual_exit, falsifier=$expected_falsifier)"
    else
      fail_count=$((fail_count + 1))
      fail_lines+=("FAIL  $name: exit matched ($actual_exit) but expected falsifier `$expected_falsifier` not found in stderr")
      fail_lines+=("      stderr: $(cat "$stderr_file" | head -5)")
    fi
  else
    fail_count=$((fail_count + 1))
    fail_lines+=("FAIL  $name: expected exit $expected_exit, got $actual_exit")
    fail_lines+=("      stderr: $(cat "$stderr_file" | head -5)")
  fi

  rm -f "$stderr_file"
}

echo "=== superset v0.4.0 falsifier harness ==="
echo ""

# Hypothesis 0: a clean valid baseline passes
run_test "valid-baseline (should PASS)" "valid-baseline" 0 "NONE"

# Hypothesis H11: same-phase owned-path overlap is caught
run_test "H11 owned-path overlap" "H11-owned-path-overlap" 1 "H11"

# Hypothesis H13: missing phase field is caught
run_test "H13 missing phase field" "H13-missing-phase" 1 "H13"

# Hypothesis H14: artifact already exists is caught
run_test "H14 artifact-existence" "H14-artifact-exists" 1 "H14"

# Hypothesis H15: producer-consumer chain break is caught
run_test "H15 missing producer" "H15-missing-producer" 1 "H15"

# Hypothesis: freeze-list intersection without precondition is caught
run_test "freeze-list precondition required" "freeze-list" 1 "freeze-list"

echo ""
echo "=== summary ==="
echo "PASS: $pass_count"
echo "FAIL: $fail_count"
if [[ $fail_count -gt 0 ]]; then
  echo ""
  for line in "${fail_lines[@]}"; do
    echo "$line"
  done
  exit 1
fi
echo ""
echo "All hypotheses hold."
exit 0
