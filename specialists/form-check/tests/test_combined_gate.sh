#!/usr/bin/env bash
# Integration test: combined gate (generation + LLM-code)
# Verifies both gates work together on a sample project

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== Integration Test: Combined Gate ==="

# Test 1: Sample Python project with generation gate
echo "Test 1: Sample Python project passes generation gate"
cd "$TMPDIR"
mkdir -p sample_py_project
cd sample_py_project

cat > run.sh <<'EOF'
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -c "print('hello')"
EOF

# Create matching test file
cat > tests/test_run.sh <<'EOF'
#!/bin/bash
set -euo pipefail
test_hello() {
    [[ "$(echo hello)" == "hello" ]] || return 1
}
test_hello
echo "PASS: test_hello"
EOF

chmod +x run.sh tests/test_run.sh

GATE_SCRIPT="$SCRIPT_DIR/../tools/generation_gate.sh"
if bash "$GATE_SCRIPT" run.sh >/dev/null 2>&1; then
    pass "Sample Python project passes generation gate"
else
    fail "Sample Python project should pass generation gate"
fi

# Test 2: Pre-commit combined hook dry-run
echo "Test 2: Pre-commit hook handles empty staging area"
cd "$TMPDIR"
mkdir -p empty_repo && cd empty_repo
git init >/dev/null 2>&1
HOOK="$SCRIPT_DIR/../templates/pre-commit-combined"
if bash "$HOOK" 2>/dev/null; then
    pass "Pre-commit hook handles empty staging area"
else
    fail "Pre-commit hook should pass with no staged files"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
