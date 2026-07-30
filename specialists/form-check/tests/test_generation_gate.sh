#!/usr/bin/env bash
# Test suite for generation_gate.sh
# Run: bash tests/test_generation_gate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE_SCRIPT="${SCRIPT_DIR}/../tools/generation_gate.sh"
TMPDIR="$(mktemp -d)"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

echo "=== Testing generation_gate.sh ==="

# Test 1: Help works
echo "Test 1: --help prints usage"
if bash "$GATE_SCRIPT" --help >/dev/null 2>&1; then
    pass "--help exits 0"
else
    fail "--help should exit 0"
fi

# Test 2: Bypass works
echo "Test 2: GENERATION_GATE_BYPASS=1 skips checks"
cd "$TMPDIR"
cat > bad.sh <<'EOF'
#!/bin/bash
# No set -euo pipefail
EOF
if GENERATION_GATE_BYPASS=1 bash "$GATE_SCRIPT" bad.sh >/dev/null 2>&1; then
    pass "Bypass works"
else
    fail "Bypass should exit 0"
fi
cd - >/dev/null

# Test 3: Missing safety header fails
echo "Test 3: Missing set -euo pipefail fails"
cd "$TMPDIR"
cat > no_header.sh <<'EOF'
#!/bin/bash
echo "hello"
EOF
if ! bash "$GATE_SCRIPT" no_header.sh >/dev/null 2>&1; then
    pass "Missing header rejected"
else
    fail "Should fail without safety header"
fi
cd - >/dev/null

# Test 4: LANG collision fails
echo "Test 4: LANG= local variable fails"
cd "$TMPDIR"
cat > lang_collision.sh <<'EOF'
#!/bin/bash
set -euo pipefail
LANG="en_US"
EOF
if ! bash "$GATE_SCRIPT" lang_collision.sh >/dev/null 2>&1; then
    pass "LANG collision rejected"
else
    fail "Should fail with LANG collision"
fi
cd - >/dev/null

# Test 5: Clean script passes
echo "Test 5: Clean script passes"
cd "$TMPDIR"
cat > clean.sh <<'EOF'
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "hello"
EOF
if bash "$GATE_SCRIPT" clean.sh >/dev/null 2>&1; then
    pass "Clean script accepted"
else
    fail "Clean script should pass"
fi
cd - >/dev/null

# Test 6: Heredoc outside usage fails
echo "Test 6: Heredoc outside usage function fails"
cd "$TMPDIR"
cat > heredoc_bad.sh <<'INNER_EOF'
#!/bin/bash
set -euo pipefail
cat <<EOF
hello world
EOF
INNER_EOF
if ! bash "$GATE_SCRIPT" heredoc_bad.sh >/dev/null 2>&1; then
    pass "Heredoc outside usage rejected"
else
    fail "Should fail with heredoc outside usage"
fi
cd - >/dev/null

# Test 7: Heredoc in usage function passes
echo "Test 7: Heredoc in usage function passes"
cd "$TMPDIR"
cat > heredoc_usage.sh <<'INNER_EOF'
#!/bin/bash
set -euo pipefail
usage() {
    cat <<EOF
Usage: hello
EOF
}
echo "hello"
INNER_EOF
if bash "$GATE_SCRIPT" heredoc_usage.sh >/dev/null 2>&1; then
    pass "Heredoc in usage accepted"
else
    fail "Heredoc in usage should pass"
fi
cd - >/dev/null

# Test 8: cd && chain fails
echo "Test 8: cd && chain fails"
cd "$TMPDIR"
cat > cd_chain.sh <<'EOF'
#!/bin/bash
set -euo pipefail
cd /tmp && echo "hello"
EOF
if ! bash "$GATE_SCRIPT" cd_chain.sh >/dev/null 2>&1; then
    pass "cd && chain rejected"
else
    fail "Should fail with cd && chain"
fi
cd - >/dev/null

# Test 9: SCRIPT_DIR pattern passes
echo "Test 9: SCRIPT_DIR pattern passes"
cd "$TMPDIR"
cat > script_dir.sh <<'EOF'
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "$SCRIPT_DIR"
EOF
if bash "$GATE_SCRIPT" script_dir.sh >/dev/null 2>&1; then
    pass "SCRIPT_DIR pattern accepted"
else
    fail "SCRIPT_DIR pattern should pass"
fi
cd - >/dev/null

# Test 10: No test file warning (not critical)
echo "Test 10: No test file is warning, not critical"
cd "$TMPDIR"
cat > no_test.sh <<'INNER_EOF'
#!/bin/bash
set -euo pipefail
echo "hello"
INNER_EOF
exit_code=0
bash "$GATE_SCRIPT" no_test.sh >/dev/null 2>&1 || exit_code=$?
if [[ "$exit_code" -eq 0 ]]; then
    pass "No test file is warning-only"
else
    fail "No test file should not fail in default mode"
fi
cd - >/dev/null

# Test 11: Strict mode fails on warnings
echo "Test 11: Strict mode fails on warnings"
cd "$TMPDIR"
exit_code=0
bash "$GATE_SCRIPT" --strict no_test.sh >/dev/null 2>&1 || exit_code=$?
if [[ "$exit_code" -eq 1 ]]; then
    pass "Strict mode fails on warnings"
else
    fail "Strict mode should fail when warnings present"
fi
cd - >/dev/null

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
