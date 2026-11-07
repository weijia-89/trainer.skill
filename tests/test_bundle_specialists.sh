#!/usr/bin/env bash
# Smoke tests for scripts/bundle_specialists.sh (existence-check contract,
# bundle-array contents) co-required by the generation gate (check 5).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUNDLE="$HERE/../scripts/bundle_specialists.sh"
fails=0

assert_eq() { # label expected actual
  if [[ "$2" == "$3" ]]; then
    echo "PASS  $1"
  else
    echo "FAIL  $1 (expected '$2', got '$3')"
    fails=$((fails + 1))
  fi
}

# 1. The script guards the one bundled dependency that is not everywhere
# (rsync) before it does any bundling work.
if grep -q 'command -v rsync' "$BUNDLE"; then
  echo "PASS  guarded: command -v rsync"
else
  echo "FAIL  rsync guard missing"
  fails=$((fails + 1))
fi

# 2. The bundle array holds exactly the ten wired names; the native folders
#    (logbook, cruft) stay out of it. After stripping parens, the line renders
#    as 10 tokens: "SPECIALISTS=form-check" plus the other nine names.
array_line=$(grep -A1 '^SPECIALISTS=' "$BUNDLE" | head -1 | tr -d '()' | tr ' ' '\n' | grep -c . || true)
assert_eq "ten array tokens" "10" "$array_line"

bundle_slice="$(grep -A1 '^SPECIALISTS=' "$BUNDLE" | head -1)"
for name in form-check recovery gymbuddy safetybar diet pr program warmup superset spotter; do
  if echo "$bundle_slice" | grep -qw "$name"; then
    echo "PASS  in array: $name"
  else
    echo "FAIL  in array: $name"
    fails=$((fails + 1))
  fi
done

for native in logbook cruft; do
  if echo "$bundle_slice" | grep -qw "$native"; then
    echo "FAIL  native folder must not be in the array: $native"
    fails=$((fails + 1))
  else
    echo "PASS  not in array: $native"
  fi
done

# 3. Behavior: with a nonexistent SRC_ROOT every sibling skips and the script
#    still exits 0, because the run expects missing-sibling array slots to skip.
dst="$(mktemp -d)"
if SRC_ROOT="/tmp/empty-src-root-bundle-test" DST_ROOT="$dst" bash "$BUNDLE" > /dev/null 2>&1; then
  echo "PASS  skips gracefully when sibling repos absent"
else
  echo "FAIL  bundle aborts when sibling repos absent"
  fails=$((fails + 1))
fi
rm -rf "$dst"

if [[ "$fails" -eq 0 ]]; then
  echo "OK test_bundle_specialists"
else
  echo "FAILED test_bundle_specialists ($fails failures)" >&2
  exit 1
fi
