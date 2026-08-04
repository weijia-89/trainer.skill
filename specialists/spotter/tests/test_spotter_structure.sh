#!/usr/bin/env bash
# Test spotter specialist structure and basic correctness

set -euo pipefail

SPOTTER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0

echo "=== spotter structure tests ==="

# Test 1: SKILL.md exists and has required frontmatter
if [[ ! -f "$SPOTTER_ROOT/SKILL.md" ]]; then
  echo "FAIL: SKILL.md missing"
  ((ERRORS++))
else
  echo "PASS: SKILL.md exists"
fi

# Test 2: README.md exists
if [[ ! -f "$SPOTTER_ROOT/README.md" ]]; then
  echo "FAIL: README.md missing"
  ((ERRORS++))
else
  echo "PASS: README.md exists"
fi

# Test 3: ci-fix-patterns.md exists
if [[ ! -f "$SPOTTER_ROOT/references/ci-fix-patterns.md" ]]; then
  echo "FAIL: references/ci-fix-patterns.md missing"
  ((ERRORS++))
else
  echo "PASS: references/ci-fix-patterns.md exists"
fi

# Test 4: SKILL.md has iron law
if grep -q 'IRON LAW' "$SPOTTER_ROOT/SKILL.md"; then
  echo "PASS: Iron law present"
else
  echo "FAIL: Iron law missing"
  ((ERRORS++))
fi

# Test 5: No em-dashes in spotter files
if grep -r '—' "$SPOTTER_ROOT/"/*.md "$SPOTTER_ROOT/references/"/*.md 2>/dev/null; then
  echo "FAIL: em-dash found in spotter markdown"
  ((ERRORS++))
else
  echo "PASS: zero em-dashes"
fi

# Test 6: SKILL.md has composes section
if grep -q 'composes:' "$SPOTTER_ROOT/SKILL.md"; then
  echo "PASS: composes section present"
else
  echo "FAIL: composes section missing"
  ((ERRORS++))
fi

# Test 7: ci-fix-patterns.md has bash section
if grep -q '## Bash scripts' "$SPOTTER_ROOT/references/ci-fix-patterns.md"; then
  echo "PASS: Bash patterns section present"
else
  echo "FAIL: Bash patterns section missing"
  ((ERRORS++))
fi

# Test 8: ci-fix-patterns.md has workflow section
if grep -q '## GitHub Actions workflows' "$SPOTTER_ROOT/references/ci-fix-patterns.md"; then
  echo "PASS: Workflow patterns section present"
else
  echo "FAIL: Workflow patterns section missing"
  ((ERRORS++))
fi

# Test 9: Pre-flight checklist mentions iteration cap
if grep -q 'Iteration cap' "$SPOTTER_ROOT/SKILL.md"; then
  echo "PASS: Iteration cap present"
else
  echo "FAIL: Iteration cap missing"
  ((ERRORS++))
fi

# Test 10: Pre-flight checklist uses portable commands (no xargs -r)
if grep -q 'xargs -r' "$SPOTTER_ROOT/SKILL.md"; then
  echo "FAIL: GNU-specific xargs -r found"
  ((ERRORS++))
else
  echo "PASS: No GNU-specific xargs -r"
fi

echo ""
if [[ "$ERRORS" -eq 0 ]]; then
  echo "=== ALL TESTS PASS ==="
  exit 0
else
  echo "=== $ERRORS TEST(S) FAILED ==="
  exit 1
fi
