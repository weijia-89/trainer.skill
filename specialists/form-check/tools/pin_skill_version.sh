#!/usr/bin/env bash
# Verify the SKILL.md frontmatter version for form-check / recovery pinning.
# Used by: recovery's tests/test_skill_version_compat.py (cross-checks pinned components)
#
# Usage: tools/pin_skill_version.sh <skill-dir>
# Output: prints the version line; exit 0 if found, 1 otherwise.

set -euo pipefail

DIR="${1:-.}"
SKILL_FILE="${DIR}/SKILL.md"

if [[ ! -f "${SKILL_FILE}" ]]; then
    echo "no SKILL.md at ${DIR}" >&2
    exit 1
fi

ver="$(awk '/^version:/{print $2; exit}' "${SKILL_FILE}")"
if [[ -z "${ver}" ]]; then
    echo "no version in ${SKILL_FILE} frontmatter" >&2
    exit 1
fi

echo "${ver}"
