#!/usr/bin/env bash
# verify_bundle_sync.sh -- assert that each bundled specialist under
# trainer.skill/specialists/<name>/ matches the standalone source at
# $HOME/Projects/<name>.skill/. Catches drift from one-sided edits.
#
# Exits 0 if every paired file is byte-identical (or expected-to-differ).
# Exits 1 if any pair differs, listing the divergent files.
#
# Excludes test-run artifacts and bytecode caches.
#
# Override the standalone root with SRC_ROOT env var.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_ROOT="${SRC_ROOT:-$HOME/Projects}"
SPECIALISTS_ROOT="$REPO_ROOT/specialists"

SPECIALISTS=(form-check recovery gymbuddy safetybar diet pr program warmup)

# Expected-divergence patterns. `diff -rq --exclude=PAT` matches PAT against
# the basename at each tree level, so paths with slashes do not work.
# Listed here: runtime state, build artifacts, and generated reports that
# the bundle deliberately strips.
EXCLUDE_GLOBS=(
  "runs"
  "__pycache__"
  ".pytest_cache"
  ".DS_Store"
  ".recovery"
  "phase11_report.md"
  ".git"
  ".gitignore"
)

excludes_args=()
for glob in "${EXCLUDE_GLOBS[@]}"; do
  excludes_args+=(--exclude="$glob")
done

DRIFT=0
TOTAL=0

for name in "${SPECIALISTS[@]}"; do
  src="$SRC_ROOT/$name.skill"
  dst="$SPECIALISTS_ROOT/$name"
  if [[ ! -d "$src" ]]; then
    echo "WARN  standalone missing: $src (skipping $name)"
    continue
  fi
  if [[ ! -d "$dst" ]]; then
    echo "FAIL  bundled specialist missing: $dst"
    DRIFT=$((DRIFT + 1))
    continue
  fi
  TOTAL=$((TOTAL + 1))
  # diff -rq returns 0 on identical, 1 on differ, 2 on error
  if drift_output=$(diff -rq "${excludes_args[@]}" "$src" "$dst" 2>&1); then
    echo "PASS  $name (standalone ≡ bundle)"
  else
    DRIFT=$((DRIFT + 1))
    echo "FAIL  $name: drift detected"
    echo "$drift_output" | sed 's/^/        /'
  fi
done

if [[ "$DRIFT" -eq 0 ]]; then
  echo ""
  echo "VERDICT: PASS ($TOTAL specialist(s) in sync)"
  exit 0
fi

echo ""
echo "VERDICT: FAIL ($DRIFT specialist(s) drifted)"
echo ""
echo "Fix paths:"
echo "  - if the standalone is canonical: re-run scripts/bundle_specialists.sh"
echo "  - if the bundle is canonical: copy the corrected file back to the standalone"
echo "  - if the drift is intentional: add an entry to EXCLUDE_GLOBS"
exit 1
