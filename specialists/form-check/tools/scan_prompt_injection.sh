#!/usr/bin/env bash
# Scan markdown files for prompt-injection patterns.
# Algorithm spec: docs/prompt_injection_scan_algorithm.md
# Used by: agent-runtime/prompt_injection.md, harness_contract.md (load-time scan)
#
# Exit codes:
#   0 — no hits in scanned content
#   1 — hits found (each printed as file:line: pattern)
#   2 — invocation error

set -euo pipefail

ROOT="${1:-.}"
EXCLUDE_DIRS=("references" "examples" "tests/fixtures" ".git" "node_modules" ".venv")

# Patterns (case-insensitive). Tuned for current attack literature.
PATTERNS=(
    'ignore (previous|prior|all|above) (instructions|rules|guidance|constraints)'
    'disregard (previous|prior|all|above) (instructions|rules)'
    'forget (previous|prior|all|above) (instructions|rules)'
    'you are now (a |an )?'
    '^system: '
    '\[INST\]'
    '<\|im_start\|>'
    '<\|im_end\|>'
    'act as (a |an )?(jailbroken|unrestricted|developer)'
    '(disregard|override|bypass) (your |the )?(safety|alignment|guidelines|rules)'
    'pretend (you|to be) (a|an|are)'
)

if [[ ! -d "${ROOT}" ]]; then
    echo "error: ${ROOT} is not a directory" >&2
    exit 2
fi

# Build an extended-regex alternation
joined=""
for p in "${PATTERNS[@]}"; do
    if [[ -z "${joined}" ]]; then
        joined="${p}"
    else
        joined="${joined}|${p}"
    fi
done

# Build the find expression to exclude directories
find_args=("${ROOT}" "-type" "f" "-name" "*.md")
for d in "${EXCLUDE_DIRS[@]}"; do
    find_args+=("-not" "-path" "*/${d}/*")
done

hits=0
while IFS= read -r file; do
    if grep -niE "${joined}" "${file}" 2>/dev/null; then
        hits=$((hits + 1))
    fi
done < <(find "${find_args[@]}" 2>/dev/null)

if [[ "${hits}" -gt 0 ]]; then
    exit 1
fi
exit 0
