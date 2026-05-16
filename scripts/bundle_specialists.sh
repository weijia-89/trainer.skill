#!/usr/bin/env bash
# Bundle the 8 specialist gym-skills into trainer.skill/specialists/
# Excludes: .git, virtualenvs, caches, OS junk, generated test output, recovery state

set -euo pipefail

SRC_ROOT=/Users/wjia/Projects
DST_ROOT=/Users/wjia/Projects/trainer.skill/specialists

SPECIALISTS=(form-check recovery gymbuddy safetybar diet pr program warmup)

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
    --exclude='tests/output' \
    --exclude='tests/results' \
    --exclude='tests/__results__' \
    --exclude='*.pyc' \
    --exclude='.cache' \
    "$src" "$dst"
  cnt=$(find "$dst" -type f | wc -l | tr -d ' ')
  echo "[ok]   $s -> $dst ($cnt files)"
done

echo ""
echo "Bundle complete: $DST_ROOT"
find "$DST_ROOT" -maxdepth 1 -type d -not -path "$DST_ROOT" | sort
