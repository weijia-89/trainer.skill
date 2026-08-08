#!/usr/bin/env bash
# Idempotently rerun the "Trainer PR review comment gate" job for a PR.
# Canonical copy for product repos: install beside trainer_pr_review_post.sh.
#
# Usage (repo root or from post script):
#   bash scripts/trainer_pr_review_gate_rerun.sh <pr_num> <owner/repo>
#
# Optional: omit both args on a PR branch (resolves PR via gh pr view).
# Env: TRAINER_GATE_RERUN_SKIP=1 (no-op); TRAINER_GATE_RERUN_DRY_RUN=1 (print only).

set -euo pipefail

if [[ "${TRAINER_GATE_RERUN_SKIP:-}" == "1" ]]; then
  echo "trainer_pr_review_gate_rerun: skip (TRAINER_GATE_RERUN_SKIP=1)"
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "trainer_pr_review_gate_rerun: gh CLI not found; skip rerun" >&2
  exit 0
fi

PR_NUM=${1:-}
GH_REPO=${2:-}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# ROOT fallback: scripts/.. is the repo root; no cd chain needed.
ROOT="$(dirname "$SCRIPT_DIR")"
# shellcheck source=trainer_gh_repo.sh disable=SC1091
source "$SCRIPT_DIR/trainer_gh_repo.sh"
cd "$ROOT"

# Fallback: origin remote is optional when GH_REPO is passed explicitly.
if [[ -z "$GH_REPO" ]]; then
  REMOTE=$(git remote get-url origin 2>/dev/null || true)
  if ! GH_REPO=$(trainer_gh_repo_from_remote "$REMOTE"); then
    echo "trainer_pr_review_gate_rerun: cannot infer gh repo from origin" >&2
    exit 0
  fi
fi

# trainer.skill runs the gate as workflow "Trainer PR review gate" with job
# "codereview-contract"; product repos (buds/toebeans) ship the canonical gate
# inside a workflow named "ci" with job "Trainer PR review comment gate".
# Detect instead of hardcoding so one copy of this script works in both worlds.
# Skip to the "ci" fallback when the primary workflow name is missing from the
# listing (product repos without the trainer.skill workflow); env overrides exist.
GATE_JOB_NAME="${TRAINER_GATE_RERUN_JOB:-}"
WORKFLOW_NAME="${TRAINER_GATE_RERUN_WORKFLOW:-}"
if [[ -z "$WORKFLOW_NAME" ]]; then
  if gh workflow list --repo "$GH_REPO" 2>/dev/null | grep -q "Trainer PR review gate"; then
    WORKFLOW_NAME="Trainer PR review gate"
    [[ -n "$GATE_JOB_NAME" ]] || GATE_JOB_NAME="codereview-contract"
  else
    WORKFLOW_NAME="ci"
    [[ -n "$GATE_JOB_NAME" ]] || GATE_JOB_NAME="Trainer PR review comment gate"
  fi
elif [[ -z "$GATE_JOB_NAME" ]]; then
  GATE_JOB_NAME="Trainer PR review comment gate"
fi

if [[ -z "$PR_NUM" ]]; then
  if ! PR_NUM=$(gh pr view --repo "$GH_REPO" --json number -q .number 2>/dev/null); then
    echo "trainer_pr_review_gate_rerun: no open PR for current branch; skip" >&2
    exit 0
  fi
fi

# Optional: head sha from PR; run filter falls back to latest run when absent.
# Unguarded gh here would hard-exit under set -e on transient API errors; the
# rerun is best-effort, so resolve softly and skip when the PR is unreachable.
BRANCH=$(gh pr view "$PR_NUM" --repo "$GH_REPO" --json headRefName -q .headRefName 2>/dev/null || true)
HEAD_SHA=$(gh pr view "$PR_NUM" --repo "$GH_REPO" --json headRefOid -q .headRefOid 2>/dev/null || true)
if [[ -z "$BRANCH" || -z "$HEAD_SHA" ]]; then
  echo "trainer_pr_review_gate_rerun: cannot resolve PR #${PR_NUM}; skip" >&2
  exit 0
fi

RUN_ID=$(gh run list --repo "$GH_REPO" --branch "$BRANCH" --workflow "$WORKFLOW_NAME" \
  --limit 20 --json databaseId,headSha,event | jq -r --arg sha "$HEAD_SHA" '
    [.[] | select(.headSha == $sha and .event == "pull_request")]
    | sort_by(.databaseId) | reverse | .[0].databaseId // empty
  ')

if [[ -z "$RUN_ID" ]]; then
  RUN_ID=$(gh run list --repo "$GH_REPO" --branch "$BRANCH" --workflow "$WORKFLOW_NAME" \
    --limit 5 --json databaseId | jq -r 'sort_by(.databaseId) | reverse | .[0].databaseId // empty')
fi

if [[ -z "$RUN_ID" ]]; then
  echo "trainer_pr_review_gate_rerun: no ci workflow run for PR #${PR_NUM} (${BRANCH}); skip"
  exit 0
fi

JOB_JSON=$(gh run view "$RUN_ID" --repo "$GH_REPO" --json jobs --jq \
  ".jobs[] | select(.name == \"${GATE_JOB_NAME}\") | {id: .databaseId, status: .status, conclusion: .conclusion}" \
  | head -1)

JOB_ID=$(echo "$JOB_JSON" | jq -r '.id // empty')
JOB_STATUS=$(echo "$JOB_JSON" | jq -r '.status // empty')
JOB_CONCLUSION=$(echo "$JOB_JSON" | jq -r '.conclusion // empty')

if [[ -z "$JOB_ID" ]]; then
  echo "trainer_pr_review_gate_rerun: job \"${GATE_JOB_NAME}\" not in run ${RUN_ID}; skip"
  exit 0
fi

if [[ "$JOB_CONCLUSION" == "success" ]]; then
  echo "trainer_pr_review_gate_rerun: gate already green (run ${RUN_ID}); skip"
  exit 0
fi

if [[ "$JOB_STATUS" == "in_progress" || "$JOB_STATUS" == "queued" ]]; then
  echo "trainer_pr_review_gate_rerun: gate ${JOB_STATUS} (run ${RUN_ID}); skip"
  exit 0
fi

# Skip re-rerun while the workflow run is still queued or pending.
RUN_STATUS=$(gh run view "$RUN_ID" --repo "$GH_REPO" --json status -q .status)
if [[ "$RUN_STATUS" == "in_progress" || "$RUN_STATUS" == "queued" || "$RUN_STATUS" == "pending" ]]; then
  echo "trainer_pr_review_gate_rerun: workflow run ${RUN_ID} still ${RUN_STATUS}; retry after it finishes:"
  echo "  bash scripts/trainer_pr_review_gate_rerun.sh ${PR_NUM} ${GH_REPO}"
  exit 0
fi

if [[ "${TRAINER_GATE_RERUN_DRY_RUN:-}" == "1" ]]; then
  echo "trainer_pr_review_gate_rerun: dry-run would rerun run=${RUN_ID} job=${JOB_ID} (${GATE_JOB_NAME})"
  exit 0
fi

if gh run rerun "$RUN_ID" --repo "$GH_REPO" --job "$JOB_ID" 2>/dev/null; then
  echo "trainer_pr_review_gate_rerun: rerun triggered run=${RUN_ID} job=${JOB_ID} (${GATE_JOB_NAME})"
elif gh run rerun "$RUN_ID" --repo "$GH_REPO" --failed 2>/dev/null; then
  echo "trainer_pr_review_gate_rerun: rerun triggered failed jobs on run=${RUN_ID}"
else
  echo "trainer_pr_review_gate_rerun: could not rerun (run may be too old or locked); push empty commit or re-run gate from Actions UI" >&2
  exit 0
fi
