#!/usr/bin/env bash
# Bundle the wired specialist bundle-array members into trainer.skill/specialists/
# SPECIALISTS lists the ten sibling-synced names ("form-check recovery gymbuddy
# safetybar diet pr program warmup superset spotter"); gymbuddy and spotter have a
# slot in the array but no sibling repo on disk today, so they skip. logbook and
# cruft are native to this repo and stay out of the array.
# Excludes: .git, virtualenvs, caches, OS junk, generated test output, recovery state

set -euo pipefail

command -v rsync &>/dev/null || { echo "[FAIL] rsync is required but not installed"; exit 1; }
command -v find &>/dev/null || { echo "[FAIL] find is required but not installed"; exit 1; }
command -v rm &>/dev/null || { echo "[FAIL] rm is required but not installed"; exit 1; }

# Override SRC_ROOT to point at the directory that contains the sibling
# `<specialist>.skill/` directories. Defaults to "$HOME/Projects".
SRC_ROOT="${SRC_ROOT:-$HOME/Projects}"
# DST_ROOT defaults to the `specialists/` directory next to this script.
DST_ROOT="${DST_ROOT:-$(cd "$(dirname "$0")/.." && pwd)/specialists}"

SPECIALISTS=(form-check recovery gymbuddy safetybar diet pr program warmup superset spotter)

mkdir -p "$DST_ROOT"

for s in "${SPECIALISTS[@]}"; do
  src="$SRC_ROOT/$s.skill/"
  dst="$DST_ROOT/$s/"
  if [ ! -d "$src" ]; then
    echo "[skip] $s.skill not found at $src"
    continue
  fi
  mkdir -p "$dst"
  rsync -a --delete \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='.venv-*' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    --exclude='.pytest_cache' \
    --exclude='.recovery' \
    --exclude='localonly' \
    --exclude='tests/output' \
    --exclude='tests/results' \
    --exclude='tests/__results__' \
    --exclude='*.pyc' \
    --exclude='.cache' \
    --exclude='phase11_report.md' \
    --exclude='.gitignore' \
    "$src" "$dst"
  # Post-rsync cleanup: strip timestamped test-run output directories
  # that should never be distributed in the bundled artifact.
  find "$dst" -type d -name "runs" -path "*tests/pressure_scenarios/runs" -exec rm -rf {} + 2>/dev/null || true
  rm -rf "$dst/localonly"
  cnt=$(find "$dst" -type f | wc -l | tr -d ' ')
  echo "[ok]   $s -> $dst ($cnt files)"
done

echo ""
echo "Bundle complete: $DST_ROOT"
find "$DST_ROOT" -maxdepth 1 -type d -not -path "$DST_ROOT" | sort
