#!/usr/bin/env bash
# Verify SKILL.md has frontmatter, ≤240 lines, required H2 sections present, all referenced files exist.
# Cap raised from 220→240 in v2.0.1 to accommodate the learner onboarding-paths section.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "${SCRIPT_DIR}")"
SKILL_FILE="${SKILL_DIR}/SKILL.md"

fail=0

if [[ ! -f "${SKILL_FILE}" ]]; then
    echo "FAIL: SKILL.md missing" >&2
    exit 1
fi

# Frontmatter: starts with ---
if [[ "$(head -1 "${SKILL_FILE}")" != "---" ]]; then
    echo "FAIL: SKILL.md missing frontmatter (no leading ---)" >&2
    fail=1
fi

# Line count cap
lines=$(wc -l < "${SKILL_FILE}")
if [[ "${lines}" -gt 240 ]]; then
    echo "FAIL: SKILL.md is ${lines} lines (cap 240)" >&2
    fail=1
fi

# Required H2 sections (in any order). The "Section N <separator> Title" form
# accepts either em-dash or period as the separator, so the em-dash discipline
# sweep (2026-05-17) does not break this contract.
required_h2_re=(
    "^## Section 1[.—] Vibe-coding guardrails"
    "^## Section 2[.—] Stack decision rule"
    "^## Section 5[.—] Confidence-score rule"
    "^## Section 7[.—] Workflow for adversarial code reviews"
)
for re in "${required_h2_re[@]}"; do
    if ! grep -qE "${re}" "${SKILL_FILE}"; then
        echo "FAIL: missing required H2 section matching: ${re}" >&2
        fail=1
    fi
done

# Referenced files exist (relative paths starting with checklists/, rubrics/, templates/, multi-language/, scale-up/, agent-runtime/, references/, tools/, docs/)
while IFS= read -r ref; do
    full="${SKILL_DIR}/${ref}"
    if [[ ! -e "${full}" ]]; then
        echo "FAIL: referenced file missing: ${ref}" >&2
        fail=1
    fi
done < <(grep -oE '`(checklists|rubrics|templates|multi-language|scale-up|agent-runtime|references|tools|docs|learner)/[A-Za-z0-9_./-]+`' "${SKILL_FILE}" | tr -d '`' | sort -u)

if [[ "${fail}" -eq 0 ]]; then
    echo "test_skill_format.sh: PASS"
fi
exit "${fail}"
