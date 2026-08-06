#!/usr/bin/env bash
# test-harness-selftest.sh — Self-tests for test-pr-format.sh.
# Validates that the harness correctly accepts valid PR content and rejects invalid content.
# Usage: bash test-harness-selftest.sh
# Exit: 0 = all self-tests pass, 1 = one or more self-tests fail

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HARNESS="$SCRIPT_DIR/test-pr-format.sh"
PASS=0
FAIL=0
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

run_test() {
    local name="$1"
    local expect_exit="$2"
    shift 2
    
    local exit_code=0
    if [[ $# -gt 0 ]]; then
        bash "$HARNESS" "$@" > /dev/null 2>&1 || exit_code=$?
    else
        bash "$HARNESS" > /dev/null 2>&1 || exit_code=$?
    fi
    
    if [[ "$exit_code" -eq "$expect_exit" ]]; then
        echo "PASS: $name (exit $exit_code)"
        PASS=$((PASS + 1))
    else
        echo "FAIL: $name — expected exit $expect_exit, got $exit_code"
        FAIL=$((FAIL + 1))
    fi
}

# --- Valid PR body ---
cat > "$TMPDIR/valid-body.md" << 'EOF'
## Summary

Fixes traffic attribution in decode-traffic.sh to handle real-world host shapes. Adds --version and --check flags for cross-script parity.

## Changes

- **scripts/decode-traffic.sh**: Fixed attribution to match label, header, and body shapes.
- **scripts/compare-apps.sh**: Extended trap to catch INT and TERM signals.

## Test plan

The agent ran these tests and confirms all pass:

- [x] `bash -n scripts/decode-traffic.sh` — syntax check passed
- [x] `bash tests/test-decode-traffic.sh` — 17/17 PASS

**Coverage notes:** Unit tests cover all changed scripts. No integration tests exist for the harness itself.

## Notes

- Dark pattern heuristics produced false positives on real APKs.
EOF

# --- Valid review comment ---
cat > "$TMPDIR/valid-comment.md" << 'EOF'
## Code Review

5 checks targeting CLI interface consistency and signal handling.

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | P4 NIT | usage() doesn't document --version | No change needed — self-documenting |

**Result:** 0 CRITICAL, 0 MAJOR, 0 MINOR. All findings are P4 NITs.

### Edge case verification

- --version with extra args: correctly ignores extras
EOF

# --- Invalid: missing Summary ---
cat > "$TMPDIR/no-summary.md" << 'EOF'
## Changes

- **file.sh**: Something changed.

## Test plan

- [x] `command` — passed

**Coverage notes:** Covers everything.

## Notes

- None.
EOF

# --- Invalid: no checked boxes ---
cat > "$TMPDIR/no-checkboxes.md" << 'EOF'
## Summary

This is a test summary with enough sentences to pass the count. It describes the changes made.

## Changes

- **file.sh**: Something changed.

## Test plan

- [ ] `command` — not yet run

**Coverage notes:** Not yet tested.

## Notes

- None.
EOF

# --- Invalid: has Gate Evidence ---
cat > "$TMPDIR/gate-evidence.md" << 'EOF'
## Summary

This is a test summary with enough sentences to pass the count. It describes the changes made.

## Changes

- **file.sh**: Something changed.

## Test plan

- [x] `command` — passed

**Coverage notes:** Covers everything.

## Notes

- None.

## Gate Evidence

| Gate | Command | Result |
|------|---------|--------|
| P1.1 | `command` | exit 0 |
EOF

# --- Invalid: filler words ---
cat > "$TMPDIR/filler-words.md" << 'EOF'
## Summary

This is simply a test. It is worth noting that the changes are important. Just a placeholder.

## Changes

- **file.sh**: Something changed.

## Test plan

- [x] `command` — passed

**Coverage notes:** Covers everything.

## Notes

- None.
EOF

# --- Invalid: internal names ---
cat > "$TMPDIR/internal-names.md" << 'EOF'
## Summary

This PR routes through the toren skill and invokes breq for job fit scoring.

## Changes

- **file.sh**: Something changed.

## Test plan

- [x] `command` — passed

**Coverage notes:** Covers everything.

## Notes

- None.
EOF

# --- Review comment: missing Result line ---
cat > "$TMPDIR/no-result.md" << 'EOF'
## Code Review

3 checks targeting script consistency.

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | P4 NIT | Minor style issue | No change needed |

### Edge case verification

- All checks passed
EOF

# --- Review comment: posture column ---
cat > "$TMPDIR/with-posture.md" << 'EOF'
## Code Review

3 checks targeting script consistency.

| # | Posture | Severity | Finding | Fix |
|---|---------|----------|---------|-----|
| 1 | SWE | P4 NIT | Minor style issue | No change needed |

**Result:** 0 CRITICAL, 0 MAJOR, 0 MINOR.

### Edge case verification

- All checks passed
EOF

# --- Review comment: empty Fix column ---
cat > "$TMPDIR/empty-fix.md" << 'EOF'
## Code Review

1 check.

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | P1 CRITICAL | Security hole | |

**Result:** 1 CRITICAL.

### Edge case verification

- None
EOF

# --- Run tests ---

echo "=== Valid inputs ==="
run_test "Valid body passes" 0 "$TMPDIR/valid-body.md"
run_test "Valid comment passes" 0 "$TMPDIR/valid-body.md" "$TMPDIR/valid-comment.md"
run_test "Valid body without comment passes" 0 "$TMPDIR/valid-body.md"

echo ""
echo "=== Invalid PR body ==="
run_test "Missing Summary fails" 1 "$TMPDIR/no-summary.md"
run_test "No checked boxes fails" 1 "$TMPDIR/no-checkboxes.md"
run_test "Gate Evidence present fails" 1 "$TMPDIR/gate-evidence.md"
run_test "Filler words fails" 1 "$TMPDIR/filler-words.md"
run_test "Internal names fails" 1 "$TMPDIR/internal-names.md"

echo ""
echo "=== Invalid review comment ==="
run_test "Missing Result line fails" 1 "$TMPDIR/valid-body.md" "$TMPDIR/no-result.md"
run_test "Posture column fails" 1 "$TMPDIR/valid-body.md" "$TMPDIR/with-posture.md"
run_test "Empty Fix column fails" 1 "$TMPDIR/valid-body.md" "$TMPDIR/empty-fix.md"

echo ""
echo "=== Edge cases ==="
run_test "Missing file exits 2" 2 "$TMPDIR/nonexistent.md"
run_test "Empty args exits 2" 2

echo ""
echo "=== Self-test Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [[ "$FAIL" -gt 0 ]]; then
    echo "SELF-TEST FAILED"
    exit 1
else
    echo "ALL SELF-TESTS PASSED"
    exit 0
fi
