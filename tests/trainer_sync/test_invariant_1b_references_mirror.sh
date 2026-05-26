#!/usr/bin/env bash
# test_invariant_1b_references_mirror.sh
#
# sdk-review F2: isolated temp-dir fixture for Invariant 1b references/ rsync + per-file diff loop.
# CI cannot exercise Claude mirror paths; this guards regression in the sync/assert pattern.

set -euo pipefail

assert_refs_mirror() {
  local canonical_refs="$1"
  local claude_refs="$2"
  local ref_fail=0

  if [[ ! -d "$claude_refs" ]]; then
    echo "FAIL  missing Claude references mirror: $claude_refs"
    return 1
  fi

  while IFS= read -r -d '' ref_file; do
    local rel="${ref_file#"$canonical_refs"/}"
    local claude_file="$claude_refs/$rel"
    if [[ ! -f "$claude_file" ]] || ! diff -q "$ref_file" "$claude_file" >/dev/null; then
      echo "FAIL  references mirror diverge: $rel"
      ref_fail=1
    fi
  done < <(find "$canonical_refs" -type f -print0)

  if [[ "$ref_fail" -ne 0 ]]; then
    return 1
  fi
  return 0
}

assert_no_mirror_orphans() {
  local canonical_refs="$1"
  local claude_refs="$2"
  local orphan_fail=0

  while IFS= read -r -d '' claude_file; do
    local rel="${claude_file#"$claude_refs"/}"
    local canonical_file="$canonical_refs/$rel"
    if [[ ! -f "$canonical_file" ]]; then
      echo "FAIL  orphan in mirror: $rel"
      orphan_fail=1
    fi
  done < <(find "$claude_refs" -type f -print0)

  if [[ "$orphan_fail" -ne 0 ]]; then
    return 1
  fi
  return 0
}

ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT

CANONICAL_REFS="$ROOT/canonical/references"
CLAUDE_REFS="$ROOT/claude/references"

mkdir -p "$CANONICAL_REFS"
printf 'pre-action gate\n' > "$CANONICAL_REFS/trainer-pre-action-gates.md"
printf 'dispatch gate\n' > "$CANONICAL_REFS/trainer-dispatch-gates.md"

mkdir -p "$CLAUDE_REFS"
rsync -a --delete "$CANONICAL_REFS/" "$CLAUDE_REFS/"

if ! assert_refs_mirror "$CANONICAL_REFS" "$CLAUDE_REFS"; then
  echo "FAIL  expected byte-identical mirror after rsync"
  exit 1
fi
echo "PASS  byte-identical mirror after rsync"

printf 'stale mirror\n' > "$CLAUDE_REFS/trainer-pre-action-gates.md"
if assert_refs_mirror "$CANONICAL_REFS" "$CLAUDE_REFS"; then
  echo "FAIL  expected divergence detection"
  exit 1
fi
echo "PASS  divergence detected"

printf 'orphan only in mirror\n' > "$CLAUDE_REFS/orphan-only-in-mirror.md"
if assert_no_mirror_orphans "$CANONICAL_REFS" "$CLAUDE_REFS"; then
  echo "FAIL  expected orphan in mirror before rsync --delete"
  exit 1
fi
rsync -a --delete "$CANONICAL_REFS/" "$CLAUDE_REFS/"
if ! assert_refs_mirror "$CANONICAL_REFS" "$CLAUDE_REFS" \
  || ! assert_no_mirror_orphans "$CANONICAL_REFS" "$CLAUDE_REFS"; then
  echo "FAIL  expected rsync --delete to evict mirror orphans"
  exit 1
fi
echo "PASS  rsync --delete evicts mirror orphans"

echo "PASS  invariant 1b references mirror fixture"
