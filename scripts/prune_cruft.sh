#!/usr/bin/env bash
# prune_cruft.sh — deterministic cleanup of *.cruft.md session artifacts.
# Deletes ONLY when the adversarial-review gate is GREEN and an explicit apply is given.
# No gate => no deletion. Symlink-safe, never crosses into trainer.skill.
set -euo pipefail

ROOT="$(pwd)"
APPLY=0
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --force-after-review) FORCE=1; shift ;;
    --dry-run) APPLY=0; shift ;;
    -h|--help) echo "usage: prune_cruft.sh --root <dir> [--apply|--dry-run] [--force-after-review]"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Never let the script eat its own skill tree.
TRAINER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)"
if [[ "$ROOT" == "$TRAINER_ROOT"* ]]; then
  echo "REFUSED: will not prune inside trainer.skill ($ROOT)" >&2
  exit 2
fi

# --- Candidate scan (suffix-only trust; -print0 handles any filename) --------
files=()
while IFS= read -r -d '' f; do
  files+=("$f")
done < <(find "$ROOT" -type f \( -name '*.cruft.md' -o -name '*.cruft.*' \) -print0 2>/dev/null)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "clean — no *.cruft.md artifacts under $ROOT"
  exit 0
fi

# --- Review gate -------------------------------------------------------------
gate_green=0
if [[ -f "$ROOT/.trainer/reviews-complete" ]]; then
  gate_green=1
elif [[ -x "$TRAINER_ROOT/scripts/verify_trainer_codereview.sh" ]]; then
  if "$TRAINER_ROOT/scripts/verify_trainer_codereview.sh" >/dev/null 2>&1; then
    gate_green=1
  fi
fi

if [[ "$APPLY" -eq 0 ]]; then
  echo "dry-run — found ${#files[@]} cruft artifact(s) under $ROOT:"
  printf '  %s\n' "${files[@]}"
  if [[ "$gate_green" -eq 0 && "$FORCE" -eq 0 ]]; then
    echo "NOTE: --apply will be REFUSED until the review gate is GREEN (or --force-after-review)."
  else
    echo "gate: GREEN — pass --apply to delete."
  fi
  exit 0
fi

if [[ "$gate_green" -eq 0 && "$FORCE" -eq 0 ]]; then
  echo "REFUSED: review gate not satisfied (no .trainer/reviews-complete, verify_trainer_codereview.sh not green)." >&2
  echo "         Re-run with --force-after-review ONLY after a human has confirmed the review passed." >&2
  exit 2
fi

count=0
for f in "${files[@]}"; do
  rm -f "$f" && { echo "deleted: ${f#$ROOT/}"; count=$((count+1)); }
done
echo "done — $count cruft artifact(s) removed."
exit 0
