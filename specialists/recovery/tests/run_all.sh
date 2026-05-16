#!/usr/bin/env bash
# Single entry point for all form-check.skill tests + cross-skill ref check.
#
# Use this rather than invoking tests individually:
#   - It clears stale __pycache__ first (we hit silent pycache poisoning in v2.1.0
#     where test_citations imported test helpers and saw stale tag sets).
#   - It runs every test in tests/test_*.{sh,py} regardless of name.
#   - It reports an exact PASS/FAIL line for each test plus a summary.
#   - Exit code is 0 iff every test passes.
#
# This script is hermetic: it discovers tests by glob, so dropping a new
# test_*.{sh,py} file into tests/ wires it in automatically.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
SKILLS_PARENT="$(dirname "${SKILL_DIR}")"

# 1. Pycache cleanup. Pycache poisoning has bitten us in v2.1.0; always start clean.
find "${SKILLS_PARENT}/form-check.skill" "${SKILLS_PARENT}/recovery.skill" \
    -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 2. Discover and run every test in this skill.
pass=0
fail=0
failed_tests=()

shopt -s nullglob
tests=("${SCRIPT_DIR}"/test_*.sh "${SCRIPT_DIR}"/test_*.py)
shopt -u nullglob

if [[ ${#tests[@]} -eq 0 ]]; then
    echo "run_all.sh: ERROR (no tests found in ${SCRIPT_DIR})" >&2
    exit 2
fi

for t in "${tests[@]}"; do
    name="$(basename "${t}")"
    if [[ "${t}" == *.py ]]; then
        if python3 "${t}" > /dev/null 2>&1; then
            pass=$((pass + 1))
            echo "  PASS  ${name}"
        else
            fail=$((fail + 1))
            failed_tests+=("${name}")
            echo "  FAIL  ${name}"
        fi
    else
        if bash "${t}" > /dev/null 2>&1; then
            pass=$((pass + 1))
            echo "  PASS  ${name}"
        else
            fail=$((fail + 1))
            failed_tests+=("${name}")
            echo "  FAIL  ${name}"
        fi
    fi
done

echo ""
echo "run_all.sh: ${pass} passed, ${fail} failed"

if [[ ${fail} -gt 0 ]]; then
    echo ""
    echo "Re-run failures with full output:"
    for ft in "${failed_tests[@]}"; do
        if [[ "${ft}" == *.py ]]; then
            echo "  python3 ${SCRIPT_DIR}/${ft}"
        else
            echo "  bash ${SCRIPT_DIR}/${ft}"
        fi
    done
    exit 1
fi

exit 0
