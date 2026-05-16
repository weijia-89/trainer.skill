#!/usr/bin/env bash
# Check whether the given repository has an accepted forcing-constraint ADR.
# Algorithm spec: docs/forcing_constraint_check_algorithm.md
# Used by: scale-up/* (every chapter is read-locked behind exit 0 here)
#
# Exit codes:
#   0 — valid forcing-constraint ADR exists
#   1 — no ADR or status != accepted or type != forcing-constraint
#   2 — ADR exists but malformed (missing required keys)
#
# Usage: tools/check_forcing_constraint.sh <repo-path>

set -euo pipefail

REPO="${1:-.}"
ADR_DIR="${REPO}/docs/adr"

if [[ ! -d "${ADR_DIR}" ]]; then
    echo "no docs/adr/ directory in ${REPO}" >&2
    exit 1
fi

found=0
malformed=0

for adr in "${ADR_DIR}"/*.md; do
    [[ -f "${adr}" ]] || continue

    # Check the front-matter / front-of-file for the required signals.
    type_line="$(grep -E '^- Type: forcing-constraint$|^Type: forcing-constraint$|^- type: forcing-constraint$|^type: forcing-constraint$' "${adr}" | head -1 || true)"
    [[ -z "${type_line}" ]] && continue

    status_line="$(grep -E '^- Status:|^Status:|^- status:|^status:' "${adr}" | head -1 || true)"
    if [[ -z "${status_line}" ]]; then
        malformed=$((malformed + 1))
        continue
    fi

    # Lowercase the value
    status_value="$(echo "${status_line}" | sed -E 's/.*[Ss]tatus:[[:space:]]*//' | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
    if [[ "${status_value}" == "accepted" ]]; then
        # Also verify constraint_class is set
        if grep -qE '^(- )?[Cc]onstraint[_ ][Cc]lass:' "${adr}"; then
            found=$((found + 1))
            echo "valid forcing-constraint ADR: ${adr}" >&2
        else
            malformed=$((malformed + 1))
            echo "ADR has type=forcing-constraint and status=accepted but missing constraint_class: ${adr}" >&2
        fi
    fi
done

if [[ "${found}" -gt 0 ]]; then
    exit 0
elif [[ "${malformed}" -gt 0 ]]; then
    exit 2
else
    exit 1
fi
