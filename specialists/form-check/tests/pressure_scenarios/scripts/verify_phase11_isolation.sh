#!/usr/bin/env bash
# verify_phase11_isolation.sh
#
# RULE #4 enforcer: assert that pressure-scenario runs never mutate production
# files in form-check.skill/.
#
# Usage:
#   bash verify_phase11_isolation.sh             # baseline snapshot only
#   bash verify_phase11_isolation.sh --check     # compare current to baseline
#
# The baseline lives at /tmp/phase11-isolation-baseline.sha256. It is a sorted
# shasum -a 256 of every file under ~/Projects/form-check.skill/ EXCEPT
# tests/pressure_scenarios/runs/ (where outputs land) and .git/.
#
# Typical flow:
#   1. bash verify_phase11_isolation.sh            # snapshot pre-run
#   2. bash tests/pressure_scenarios/run.sh        # run scenarios
#   3. bash verify_phase11_isolation.sh --check    # confirm production untouched

set -euo pipefail

PROD_ROOT="$HOME/Projects/form-check.skill"
BASELINE="/tmp/phase11-isolation-baseline.sha256"

if [[ ! -d "$PROD_ROOT" ]]; then
  echo "FAIL  production root not found: $PROD_ROOT" >&2
  exit 1
fi

snapshot() {
  (
    cd "$PROD_ROOT"
    find . -type f \
      -not -path './tests/pressure_scenarios/runs/*' \
      -not -path './.git/*' \
      -print0 \
    | xargs -0 shasum -a 256 2>/dev/null \
    | sort
  )
}

case "${1:-}" in
  --check)
    if [[ ! -f "$BASELINE" ]]; then
      echo "FAIL  no baseline at $BASELINE; run without --check first" >&2
      exit 1
    fi
    CURRENT="$(mktemp)"
    trap 'rm -f "$CURRENT"' EXIT INT TERM
    snapshot > "$CURRENT"
    if diff -q "$BASELINE" "$CURRENT" >/dev/null; then
      echo "PASS  production tree byte-identical to baseline"
      exit 0
    else
      echo "FAIL  production tree differs from baseline:"
      diff "$BASELINE" "$CURRENT" | head -40 | sed 's/^/  /'
      exit 1
    fi
    ;;
  ""|--snapshot)
    snapshot > "$BASELINE"
    LINES=$(wc -l < "$BASELINE" | tr -d ' ')
    echo "PASS  baseline snapshot taken: $LINES files at $BASELINE"
    ;;
  --help|-h)
    sed -n '2,16p' "$0"
    exit 0
    ;;
  *)
    echo "Unknown argument: $1" >&2
    exit 2
    ;;
esac
