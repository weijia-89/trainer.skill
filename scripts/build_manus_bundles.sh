#!/bin/bash
# build_manus_bundles.sh — build import bundles for the Manus skill harness.
#
# Source of truth : ~/.config/opencode/skills   (gated by gate_skill_tree.sh)
# Manus           : ~/Projects/skill-dist/manus/<skill>.zip  (Settings > Skills > Upload)
#
# Pre-action gate (trainer mechanical gate):
#   source of truth = $SRC ; rollback = re-run from $SRC (idempotent) ;
#   verify = gate_skill_tree.sh GREEN + count/fidelity checks below.
#
# Idempotent, lock-guarded, self-verifying, fail-closed. Paths are env-overridable
# (SYNC_SRC / SYNC_DIST / SYNC_LOCK / SYNC_MIN_DIRS) for hermetic tests.
set -euo pipefail

SRC="${SYNC_SRC:-$HOME/.config/opencode/skills}"
DIST="${SYNC_DIST:-$HOME/Projects/skill-dist/manus}"
LOCK="${SYNC_LOCK:-/tmp/opencode/build_manus_bundles.lock}"
MIN_DIRS="${SYNC_MIN_DIRS:-50}"

[ -d "$SRC" ] || { echo "FATAL: source tree missing: $SRC" >&2; exit 1; }
[ -n "$DIST" ] || { echo "FATAL: DIST is empty (would rm -rf a relative .staging)" >&2; exit 1; }

# Fail-closed: never publish a tree the gate has not certified.
if [ "${SYNC_SKIP_GATE:-0}" != "1" ]; then
  echo "[pre] gate: gate_skill_tree.sh"
  if ! bash "$(dirname "$0")/../specialists/form-check/tools/gate_skill_tree.sh" >/dev/null 2>&1; then
    echo "FATAL: gate_skill_tree.sh is RED — refusing to build bundles (run it to see findings)" >&2
    exit 1
  fi
fi

echo "[0/3] lock"
acquire_lock() {
  if mkdir "$LOCK" 2>/dev/null; then
    trap 'rmdir "$LOCK" 2>/dev/null || true; rm -rf "${STAGE:-}" 2>/dev/null || true' EXIT
    return 0
  fi
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then
    echo "  stealing stale lock (>30min)"
    rmdir "$LOCK" && acquire_lock && return 0
  fi
  echo "FATAL: another build is running (lock: $LOCK)" >&2
  exit 3
}
acquire_lock

src_dirs=$(find "$SRC" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
if [ "$src_dirs" -lt "$MIN_DIRS" ]; then
  echo "FATAL: source has only $src_dirs dirs (< SYNC_MIN_DIRS=$MIN_DIRS) — refusing build (blast-radius guard)" >&2
  exit 1
fi

echo "[1/3] building Manus import bundles -> $DIST (atomic staging)"
STAGE="$DIST/.staging"
rm -rf "$STAGE"
mkdir -p "$STAGE"
# Defense-in-depth: `zip` follows symlinks and would silently archive whatever
# they point at. Refuse any symlink in $SRC so the bundle can never contain
# unintended files (the gate also flags escaping symlinks as S12/P2).
if [ -n "$(find "$SRC" -type l -print -quit 2>/dev/null)" ]; then
  echo "FATAL: symlink found in source tree ($SRC) — zip would follow it; remove symlinks before build" >&2
  exit 1
fi
for d in "$SRC"/*/; do
  n=$(basename "$d")
  (cd "$d" && zip -qr "$STAGE/$n.zip" . -x '.git/*' -x '.git/' -x '.DS_Store' -x 'node_modules/*')
done

stage_zips=$(find "$STAGE" -maxdepth 1 -name '*.zip' | wc -l | tr -d ' ')
if [ "$stage_zips" -ne "$src_dirs" ]; then
  echo "GATE RED: bundle build produced $stage_zips zips for $src_dirs skills" >&2
  exit 1
fi

echo "[2/3] Manus import bundle fidelity spot-check"
# NOTE: no `grep -q` here -- under pipefail it SIGPIPEs the producer (exit 141)
# and flips the condition false on large archives. Consume the stream instead.
# Verify EVERY bundle is non-empty, and that each skill which has a nested
# subdirectory in $SRC kept that subtree in its zip (no hardcoding of a single
# skill name, so trees without 'trainer' still build cleanly).
bad=0
for z in "$STAGE"/*.zip; do
  [ -e "$z" ] || continue
  n="$(basename "$z" .zip)"
  entries=$(unzip -l "$z" 2>/dev/null | tail -n +4 | grep -c '^ *[0-9]')
  if [ "${entries:-0}" -lt 1 ]; then
    echo "  GATE RED: $n.zip is empty"; bad=1; continue
  fi
  for sub in "$SRC/$n"/*/; do
    [ -d "$sub" ] || continue
    sn="$(basename "$sub")"
    if ! unzip -l "$z" 2>/dev/null | grep "$sn/" >/dev/null; then
      echo "  GATE RED: $n.zip lost nested dir $sn/"; bad=1
    fi
  done
done
[ "$bad" -eq 0 ] || { echo "GATE RED: bundle fidelity failed" >&2; exit 1; }
echo "  all $stage_zips bundles non-empty + nested dirs preserved"

# Atomic swap: move the freshly built bundles into $DIST FIRST (overwriting the
# existing skill-stem zips in place — no window where a current skill is absent),
# THEN warn on any zip that is not a current skill bundle. We never delete a zip
# whose stem still has a directory in $SRC, so an interrupted run can only ever
# leave a stale-but-present bundle, never a missing current one.
mv "$STAGE"/*.zip "$DIST"/
rmdir "$STAGE"

# Surface (warn, do not delete) any non-skill zip in $DIST — an operator-placed
# or stale bundle that Manus would also load; review before import.
for z in "$DIST"/*.zip; do
  [ -e "$z" ] || continue
  b="$(basename "$z" .zip)"
  [ -d "$SRC/$b" ] || echo "WARN: non-skill zip preserved in DIST (review before Manus import): $b.zip" >&2
done

echo "[3/3] verification"
zips=0
for d in "$SRC"/*/; do
  [ -f "$DIST/$(basename "$d").zip" ] && zips=$((zips + 1))
done
echo "skills      src=$src_dirs"
echo "manus zips  $zips (skill-stem)"
if [ "$src_dirs" != "$zips" ]; then
  echo "GATE RED: count mismatch (src_dirs=$src_dirs zips=$zips)" >&2
  exit 1
fi
echo "BUILD GREEN"
