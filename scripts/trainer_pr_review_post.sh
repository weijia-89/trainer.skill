#!/usr/bin/env bash
# Post or PATCH the canonical trainer code-review comment on an open PR.
# Canonical copy for product repos (toebeans, buds): install under <repo>/scripts/.
#
# Usage (product repo root):
#   bash scripts/trainer_pr_review_post.sh <pr_num> <verdict> <round> <body.md>
#
# verdict: APPROVE | REQUEST_CHANGES | BLOCK
#
# Order: post/PATCH before push when CI should pass on that SHA (trainer-codereview-gate.md).
# After posting on an already-pushed PR, re-run the failed "Trainer PR review comment gate"
# workflow (or push an empty commit) so CI picks up the comment without waiting on Gradle.

set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "usage: $0 <pr_num> <verdict> <round> <body.md>" >&2
  exit 2
fi

PR_NUM=$1
VERDICT=$2
ROUND=$3
BODY_FILE=$4
[[ -f "$BODY_FILE" ]] || { echo "missing body file: $BODY_FILE" >&2; exit 2; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=trainer_gh_repo.sh
source "$SCRIPT_DIR/trainer_gh_repo.sh"
cd "$ROOT"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
HEAD_SHA=$(git rev-parse HEAD)
HEAD_SHORT=${HEAD_SHA:0:7}
BRANCH_SLUG=${BRANCH//\//-}
REMOTE=$(git remote get-url origin 2>/dev/null || true)
if ! GH_REPO=$(trainer_gh_repo_from_remote "$REMOTE"); then
  echo "cannot infer gh repo from origin: $REMOTE" >&2
  exit 2
fi
REPO_SLUG="${GH_REPO##*/}"

_validate_review_body_for_repo() {
  local body_file=$1
  local repo=$2
  local body
  body=$(<"$body_file")
  # Match launch instructions (numbered steps / backticks), not "do not use …" disclaimers.
  local launch_lines
  launch_lines=$(printf '%s\n' "$body" | grep -E '^[0-9]+\. `|^[0-9]+\. cd |`cd ~/Projects/' || true)
  case "$repo" in
    buds)
      if printf '%s\n' "$launch_lines" | grep -qE '\./gradlew|:androidApp:installDebug|app\.toebeans\.android|cd ~/Projects/toebeans|cd /Projects/toebeans'; then
        echo "trainer_pr_review_post: buds PR Manual QA lists toebeans-only launch commands" >&2
        echo "  Use: cd ~/Projects/buds/app && flutter run (AVD buds-pixel7 is OK)" >&2
        exit 1
      fi
      if ! printf '%s' "$body" | grep -qE 'Projects/buds.*flutter run|flutter run.*Projects/buds'; then
        echo "trainer_pr_review_post: buds PR comment should include ~/Projects/buds and flutter run" >&2
        exit 1
      fi
      ;;
    toebeans)
      if printf '%s\n' "$launch_lines" | grep -qE 'Projects/buds|verify_buds\.sh|flutter run'; then
        echo "trainer_pr_review_post: toebeans PR Manual QA lists buds-only launch commands" >&2
        exit 1
      fi
      if ! printf '%s' "$body" | grep -qE '\./gradlew|app\.toebeans\.android|Projects/toebeans'; then
        echo "trainer_pr_review_post: toebeans PR comment should include gradlew installDebug or app.toebeans.android" >&2
        exit 1
      fi
      ;;
  esac
}

_validate_review_body_for_repo "$BODY_FILE" "$REPO_SLUG"

MARKER="<!-- trainer-codereview-${REPO_SLUG}-${BRANCH_SLUG} -->"
META="<!-- head=${HEAD_SHORT} verdict=${VERDICT} round=${ROUND} -->"

# Body file must not include markers (script owns them); strip if pasted from a prior round.
STRIPPED=$(mktemp)
python3 - "$BODY_FILE" "$STRIPPED" <<'PY'
import re
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
lines = src.read_text(encoding="utf-8").splitlines()
while lines and re.match(
    r"^\s*<!--\s*(trainer-codereview-|head=)", lines[0], re.I
):
    lines.pop(0)
while lines and lines[0].strip() == "":
    lines.pop(0)
dst.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
PY

OUT=$(mktemp)
{
  echo "$MARKER"
  echo "$META"
  cat "$STRIPPED"
} >"$OUT"
rm -f "$STRIPPED"

BUG_INV="${SCRIPT_DIR}/trainer_review_bug_inventory_validate.py"
if [[ ! -f "$BUG_INV" ]]; then
  echo "trainer_pr_review_post: missing $BUG_INV" >&2
  exit 1
fi
python3 "$BUG_INV" "$REPO_SLUG" "$OUT" --full || exit 1

R6_VALIDATE="${SCRIPT_DIR}/trainer_pr_r6_validate.py"
if [[ -f "$R6_VALIDATE" ]]; then
  CHANGED_FILES=$(mktemp)
  if [[ -n "${TRAINER_R6_FILES_FIXTURE:-}" ]]; then
    cp "$TRAINER_R6_FILES_FIXTURE" "$CHANGED_FILES"
  elif command -v gh >/dev/null 2>&1; then
    gh api "repos/${GH_REPO}/pulls/${PR_NUM}/files" --paginate \
      --jq '.[].filename' >"$CHANGED_FILES" 2>/dev/null || true
  fi
  if [[ ! -s "$CHANGED_FILES" ]]; then
    git diff --name-only origin/main...HEAD >"$CHANGED_FILES" 2>/dev/null \
      || git diff --name-only main...HEAD >"$CHANGED_FILES" 2>/dev/null \
      || true
  fi
  if [[ -s "$CHANGED_FILES" ]]; then
    python3 "$R6_VALIDATE" --files-file "$CHANGED_FILES" \
      --review-file "$OUT" --verdict "$VERDICT" || {
      rm -f "$CHANGED_FILES"
      exit 1
    }
  fi
  rm -f "$CHANGED_FILES"
fi

MARKER_NEEDLE="trainer-codereview-${REPO_SLUG}-${BRANCH_SLUG}"
COMMENT_IDS=$(gh api "repos/${GH_REPO}/issues/${PR_NUM}/comments" --paginate \
  --jq ".[] | select(.body | contains(\"${MARKER_NEEDLE}\")) | .id" 2>/dev/null | sort -n)

COMMENT_ID=$(printf '%s\n' "$COMMENT_IDS" | head -1)
DUPLICATE_IDS=$(printf '%s\n' "$COMMENT_IDS" | tail -n +2)

if [[ -n "$COMMENT_ID" ]]; then
  jq -n --rawfile b "$OUT" '{body: $b}' \
    | gh api -X PATCH "repos/${GH_REPO}/issues/comments/${COMMENT_ID}" --input - >/dev/null
  echo "PATCHED comment id=${COMMENT_ID} on PR #${PR_NUM} (${GH_REPO}) head=${HEAD_SHORT} verdict=${VERDICT}"
  if [[ -n "$DUPLICATE_IDS" ]]; then
    while IFS= read -r dup_id; do
      [[ -z "$dup_id" ]] && continue
      gh api -X DELETE "repos/${GH_REPO}/issues/comments/${dup_id}" >/dev/null
      echo "DELETED duplicate trainer comment id=${dup_id} (canonical id=${COMMENT_ID})"
    done <<<"$DUPLICATE_IDS"
  fi
else
  gh pr comment "$PR_NUM" --repo "$GH_REPO" --body-file "$OUT"
  echo "POSTED new comment on PR #${PR_NUM} (${GH_REPO}) head=${HEAD_SHORT} verdict=${VERDICT}"
fi

rm -f "$OUT"

RERUN="${SCRIPT_DIR}/trainer_pr_review_gate_rerun.sh"
if [[ -f "$RERUN" ]]; then
  bash "$RERUN" "$PR_NUM" "$GH_REPO" || {
    echo "trainer_pr_review_post: comment posted; gate rerun failed (re-run: bash scripts/trainer_pr_review_gate_rerun.sh ${PR_NUM} ${GH_REPO})" >&2
  }
fi
