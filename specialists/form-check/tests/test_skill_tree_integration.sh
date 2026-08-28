#!/usr/bin/env bash
# tests/test_skill_tree_integration.sh [tools_dir] [work_dir]
# Hermetic integration tests for gate_skill_tree.sh + build_manus_bundles.sh.
# Uses a SMALL SYNTHETIC skills tree (not the 52M real one) so the suite is
# fast and hermetic; it exercises pipeline logic (gate, atomicity, guards,
# scoped delete), not the content of the real skills.
set -uo pipefail
TOOLS="${1:-$(cd "$(dirname "$0")/../tools" && pwd)}"
WORK="${2:-$(mktemp -d)}"
trap 'rm -rf "$WORK"' EXIT
SRC="$WORK/src"; DIST="$WORK/dist"; LOCK="$WORK/lock"
RC=0

mk_skill() { mkdir -p "$1"; printf -- '---\nname: %s\ndescription: x\n---\nbody\n' "$(basename "$1")" > "$1/SKILL.md"; }

mkdir -p "$SRC" "$DIST"
mk_skill "$SRC/a"; mk_skill "$SRC/b"; mk_skill "$SRC/c"
# trainer is the one skill with nested specialists; the bundle fidelity check
# scans nested dirs, so it must exist in the fixture.
mkdir -p "$SRC/trainer/specialists/x"
printf -- '---\nname: trainer\ndescription: x\n---\n' > "$SRC/trainer/SKILL.md"
echo "nested" > "$SRC/trainer/specialists/x/f.md"

export SYNC_SRC="$SRC" SYNC_DIST="$DIST" SYNC_LOCK="$LOCK" SYNC_MIN_DIRS=2
export GATE_ROOT="$SRC" GATE_AUDIT="$TOOLS/.."
export SKILL_TREE_ROOT="$SRC" SKILL_TREE_OUT="$WORK/findings-skill-tree.json"

echo "  [int] gate GREEN on clean synthetic tree"
if ! bash "$TOOLS/gate_skill_tree.sh" >/dev/null 2>&1; then
  echo "    FAIL: gate not GREEN on clean tree"; RC=1
fi

echo "  [int] clean build first (establish published set)"
bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >"$WORK/build0.log" 2>&1 || { echo "    FAIL: seed build rc=$?"; RC=1; }
expect=4
pub_before=$(ls "$DIST"/*.zip 2>/dev/null | wc -l | tr -d ' ')
[ "$pub_before" -eq "$expect" ] || { echo "    FAIL: seed publish mismatch $pub_before/$expect"; RC=1; }

echo "  [int] atomic build: zip fault -> rc=3, published set intact, staging gone"
printf '#!/bin/bash\nfor a in "$@"; do case "$a" in *c*) exit 3;; esac; done\nexec /usr/bin/zip "$@"\n' > "$WORK/shimzip"
chmod +x "$WORK/shimzip"; mkdir -p "$WORK/shimdir"; cp "$WORK/shimzip" "$WORK/shimdir/zip"
PATH="$WORK/shimdir:$PATH" bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >/dev/null 2>&1
fr=$?
pub=$(ls "$DIST"/*.zip 2>/dev/null | wc -l | tr -d ' ')
if [ "$fr" -ne 3 ]; then echo "    FAIL: expected rc=3 got $fr"; RC=1; fi
if [ "$pub" -ne "$expect" ]; then echo "    FAIL: published set changed under fault pub=$pub expect=$expect"; RC=1; fi
if [ -d "$DIST/.staging" ]; then echo "    FAIL: staging residue left"; RC=1; fi
rm -rf "$WORK/shimdir"

echo "  [int] clean build: BUILD GREEN + counts equal"
bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >"$WORK/build.log" 2>&1 || { echo "    FAIL: build rc=$?"; RC=1; }
grep -q "BUILD GREEN" "$WORK/build.log" || { echo "    FAIL: no BUILD GREEN"; RC=1; }
echo "  [int] idempotent re-run: identical counts"
bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >"$WORK/build2.log" 2>&1 || { echo "    FAIL: build2 rc=$?"; RC=1; }
grep -E 'skills|manus zips' "$WORK/build.log" > "$WORK/a.txt"
grep -E 'skills|manus zips' "$WORK/build2.log" > "$WORK/b.txt"
if ! diff -q "$WORK/a.txt" "$WORK/b.txt" >/dev/null; then echo "    FAIL: non-idempotent"; RC=1; fi

echo "  [int] min-count guard: tiny SRC (1 skill < SYNC_MIN_DIRS=2) -> refuse (rc=1)"
tiny="$WORK/tiny"; mkdir -p "$tiny/onlyone"; mk_skill "$tiny/onlyone"
SYNC_SRC="$tiny" bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >/dev/null 2>&1; trc=$?
if [ "$trc" -ne 1 ]; then echo "    FAIL: min-count guard did not abort rc=$trc"; RC=1; fi

echo "  [int] destructive delete scoped: operator zip in DIST survives + build GREEN"
echo junk > "$DIST/operator-kept.zip"
bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >/dev/null 2>&1 || { echo "    FAIL: build rc=$?"; RC=1; }
if [ ! -f "$DIST/operator-kept.zip" ]; then echo "    FAIL: unscoped delete removed operator file"; RC=1; fi
# 4 skill-stem zips + the preserved operator file = 5 total.
if [ "$(ls "$DIST"/*.zip 2>/dev/null | wc -l | tr -d ' ')" -ne 5 ]; then echo "    FAIL: zip count wrong after scoped delete (expected 5 = 4 skill + operator)"; RC=1; fi
rm -f "$DIST/operator-kept.zip"

echo "  [int] gate enforced before build: break a skill -> build refuses"
mkdir -p "$SRC/broken_skill"
printf -- 'no frontmatter here\n' > "$SRC/broken_skill/SKILL.md"
bash "$TOOLS/../../../scripts/build_manus_bundles.sh" >/dev/null 2>&1; grc=$?
if [ "$grc" -ne 1 ]; then echo "    FAIL: build proceeded with RED gate rc=$grc"; RC=1; fi
rm -rf "$SRC/broken_skill"

exit $RC
