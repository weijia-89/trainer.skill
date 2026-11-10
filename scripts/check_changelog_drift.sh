#!/usr/bin/env bash
# check_changelog_drift.sh
#
# Mechanical CHANGELOG drift check (ROADMAP Q3, D21).
# Fails when SKILL.md, scripts/, or tests/ change without CHANGELOG.md.
# Docs-only diffs are exempt (R-6); they may still include CHANGELOG.md.
#
# Base resolution:
#   - BASE_SHA or DRIFT_BASE_SHA env (CI: PR base SHA / push before SHA)
#   - fallback: merge-base origin/main HEAD, else origin/main
# Fails clearly (never passes silently) when the diff base cannot be resolved.
set -euo pipefail

base="${BASE_SHA:-${DRIFT_BASE_SHA:-}}"
# GitHub sends all-zeros for the "before" SHA on a new branch/push; treat as unset.
if [[ "$base" =~ ^0{40}$ ]]; then
  base=""
fi

if [[ -n "$base" ]]; then
  if ! git rev-parse --verify -q "${base}^{commit}" >/dev/null 2>&1; then
    echo "FAIL: CHANGELOG drift check cannot resolve BASE_SHA/DRIFT_BASE_SHA '$base' to a commit." >&2
    echo "Set a valid base commit SHA (CI: PR base SHA) or ensure the base ref is fetched." >&2
    exit 1
  fi
else
  if git rev-parse --verify -q origin/main >/dev/null 2>&1; then
    base="$(git merge-base origin/main HEAD 2>/dev/null || true)"
    if [[ -z "$base" ]]; then
      base="origin/main"
    fi
  else
    echo "FAIL: CHANGELOG drift check needs a diff base." >&2
    echo "Set BASE_SHA (or DRIFT_BASE_SHA) to the PR base commit, or fetch origin/main." >&2
    exit 1
  fi
fi

if ! changed="$(git diff --name-only "${base}...HEAD" 2>&1)"; then
  echo "FAIL: CHANGELOG drift check could not compute git diff from '$base' to HEAD." >&2
  printf '%s\n' "$changed" >&2
  exit 1
fi

# Collect triggering paths (SKILL.md, scripts/, tests/).
triggered=()
has_changelog=0
while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  if [[ "$path" == "CHANGELOG.md" ]]; then
    has_changelog=1
  fi
  if [[ "$path" == "SKILL.md" || "$path" == scripts/* || "$path" == tests/* ]]; then
    triggered+=("$path")
  fi
done <<< "$changed"

if [[ ${#triggered[@]} -eq 0 ]]; then
  echo "PASS: docs-only diff (no SKILL.md, scripts/, or tests/ changes); CHANGELOG.md not required (R-6)."
  exit 0
fi

if [[ "$has_changelog" -eq 1 ]]; then
  echo "PASS: CHANGELOG.md updated with triggering changes (${#triggered[@]} path(s))."
  exit 0
fi

# Operator-plain, actionable failure naming the rule.
first="${triggered[0]}"
echo "FAIL: ${first} changed without a CHANGELOG.md update." >&2
echo "Rule: when a PR changes SKILL.md, scripts/, or tests/, it must also update CHANGELOG.md." >&2
echo "Fix: add a dated entry under the current '## YYYY-MM-DD' section in CHANGELOG.md describing this change." >&2
echo "Triggering paths in this diff:" >&2
for p in "${triggered[@]}"; do
  echo "  - $p" >&2
done
exit 1
