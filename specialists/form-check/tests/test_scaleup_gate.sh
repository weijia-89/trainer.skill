#!/usr/bin/env bash
# Verify check_forcing_constraint.sh behavior on synthetic fixtures.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
TOOL="${SKILL_DIR}/tools/check_forcing_constraint.sh"
FIXTURE_DIR="${SCRIPT_DIR}/fixtures"

if [[ ! -x "${TOOL}" ]]; then
    echo "FAIL: ${TOOL} not executable" >&2
    exit 1
fi

fail=0

# Scenario 1: repo without forcing-constraint ADR → exit 1
if "${TOOL}" "${FIXTURE_DIR}/repo-without-fc-adr" >/dev/null 2>&1; then
    echo "FAIL: repo-without-fc-adr should exit 1 but exited 0" >&2
    fail=1
fi
ec=$?
if [[ "${ec}" -ne 1 ]]; then
    : # Already accounted for above; no-op
fi

# Scenario 2: repo WITH valid ADR → exit 0
if ! "${TOOL}" "${FIXTURE_DIR}/repo-with-fc-adr" >/dev/null 2>&1; then
    echo "FAIL: repo-with-fc-adr should exit 0 but did not" >&2
    fail=1
fi

# Scenario 3: repo with pending ADR (Status: proposed) → exit 1
if "${TOOL}" "${FIXTURE_DIR}/repo-with-pending-fc-adr" >/dev/null 2>&1; then
    echo "FAIL: repo-with-pending-fc-adr should exit 1 but exited 0" >&2
    fail=1
fi

if [[ "${fail}" -eq 0 ]]; then
    echo "test_scaleup_gate.sh: PASS"
fi
exit "${fail}"
