#!/usr/bin/env bash
# Verify the canonical workflow DAG is single-source-of-truth.
# Acceptance:
#   exit 0 — workflow_dag.md has the canonical DAG; SKILL.md references by ID
#   exit 1 — drift detected

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"

DAG_FILE="${SKILL_DIR}/workflow/workflow_dag.md"
SKILL_FILE="${SKILL_DIR}/SKILL.md"

if [[ ! -f "${DAG_FILE}" ]]; then
    echo "FAIL: workflow_dag.md missing" >&2
    exit 1
fi

# Verify each canonical phase ID appears in workflow_dag.md
phases=("discovery" "review" "scoring" "doc-pass" "deAI-sweep" "adversarial" "launch-ready" "summary")
fail=0
for p in "${phases[@]}"; do
    if ! grep -qiE "\b${p}\b" "${DAG_FILE}"; then
        echo "FAIL: phase '${p}' missing from workflow_dag.md" >&2
        fail=1
    fi
done

# Verify SKILL.md references workflow_dag.md
if ! grep -q "workflow/workflow_dag.md" "${SKILL_FILE}"; then
    echo "FAIL: SKILL.md does not reference workflow/workflow_dag.md" >&2
    fail=1
fi

if [[ "${fail}" -eq 0 ]]; then
    echo "test_workflow_idempotent.sh: PASS"
fi
exit "${fail}"
