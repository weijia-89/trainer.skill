#!/usr/bin/env bash
# check_pr_merged.sh
# Abort push if the current branch already has a merged PR.
#
# Reads the pre-push stdin (local_ref remote_ref) to determine the branch.
# If gh is available, queries gh pr list --state merged --head <branch>.
# Exits non-zero (blocking the push) when a merged PR is found.
set -euo pipefail

# Read the first line of pre-push input (local_ref is enough for branch name)
read -r local_ref || exit 0

# Extract branch name from the local ref
branch="${local_ref#refs/heads/}"

if [[ -z "$branch" ]]; then
  echo "WARNING: Unable to determine branch from pre-push input; allowing push." >&2
  exit 0
fi

# Use gh CLI to check for a merged PR; if gh is not available, allow the push.
if command -v gh >/dev/null 2>&1; then
  merged_prs=$(gh pr list --state merged --head "$branch" --json number --limit 1 2>/dev/null || true)
  if [[ -n "$merged_prs" ]]; then
    echo "ERROR: Branch '$branch' has a merged PR. Push aborted. Create a new branch for further work." >&2
    exit 1
  fi
fi

# If no merged PR found or gh not installed, allow the push.
exit 0