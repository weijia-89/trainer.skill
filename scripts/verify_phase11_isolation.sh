#!/usr/bin/env bash
# verify_phase11_isolation.sh: assert prod tree byte-identical around a suite run.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
snap() {
  (
    cd "$REPO_ROOT"
    find . -type f \
      -not -path './tests/scenarios/harness/runs/*' -not -path './.git/*' -not -path '*/__pycache__/*' -print0 \
      | xargs -0 shasum -a 256 2>/dev/null | sort
  )
}
PRE="$(snap)"
bash "$REPO_ROOT/scripts/run.sh" --offline --k 1 >/dev/null 2>&1 || true
POST="$(snap)"
if [[ "$PRE" != "$POST" ]]; then
  echo "FAIL prod tree changed during suite run"
  diff <(echo "$PRE") <(echo "$POST") | head
  exit 1
fi
echo "PASS phase11 isolation (prod tree byte-identical)"
