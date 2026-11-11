#!/usr/bin/env bash
# Smoke tests for scripts/verify_trainer_sync.sh (the CI invariant harness).
# Env-independent by design: asserts the script's own structure rather than
# running the full mirror sync, which needs the operator's home layout.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VERIFY="$HERE/../scripts/verify_trainer_sync.sh"
fails=0

ok() { echo "PASS  $1"; fails=$((fails + 0)); }
bad() { echo "FAIL  $1"; fails=$((fails + 1)); }

# 1. It parses and keeps the safety header.
if bash -n "$VERIFY" 2>/dev/null; then
  ok "bash -n parses the verify script"
else
  bad "verify script has syntax errors"
fi
if head -25 "$VERIFY" | grep -q 'set -euo pipefail'; then
  ok "safety header present"
else
  bad "safety header missing"
fi

# 2. The version-stamp greps are guarded: an absent stamp must FAIL loudly
#    below (mismatch checks) instead of aborting the run under pipefail.
if grep -qE 'CANONICAL_VERSION=.*\| true' "$VERIFY" && grep -qE 'WINDSURF_VERSION=.*\| true' "$VERIFY"; then
  ok "version-stamp greps are guarded against silent abort"
else
  bad "version-stamp greps are not guarded"
fi

# 3. Dependency guards exist for the two external tools needed mid-script.
if grep -q 'command -v python3' "$VERIFY" && grep -q 'command -v mkdir' "$VERIFY"; then
  ok "python3 and mkdir guards present"
else
  bad "dependency guards missing"
fi

# 4. The logbook suite is wired as an invariant (17) and its file exists.
if grep -q "tests/logbook/test_logbook.py" "$VERIFY"; then
  ok "logbook suite wired into verify"
else
  bad "logbook suite not wired"
fi
if [[ -f "$HERE/logbook/test_logbook.py" ]]; then
  ok "logbook test file exists"
else
  bad "logbook test file missing"
fi

# 5. The deleted workflow stays deleted; its name must not reappear in CI files.
if [[ ! -f "$HERE/../.github/workflows/logbook-tests.yml" ]]; then
  ok "no standalone logbook workflow"
else
  bad "logbook workflow should stay deleted"
fi

# 6. The opt-in pre-push gate surfaces its absence on every local run
#    (operator decision 2026-11-10: gate stays opt-in; the harness reports it).
if grep -q 'pre-push gate is NOT installed' "$VERIFY" && grep -q 'install_hooks.sh' "$VERIFY"; then
  ok "pre-push gate status note present"
else
  bad "pre-push gate status note missing"
fi
if grep -qE 'core\.hooksPath' "$VERIFY" && grep -q '\.git/hooks/pre-push' "$VERIFY"; then
  ok "hook status checks both core.hooksPath and .git/hooks/pre-push"
else
  bad "hook status check incomplete"
fi

if [[ "$fails" -eq 0 ]]; then
  echo "OK test_verify_trainer_sync"
else
  echo "FAILED test_verify_trainer_sync ($fails failures)" >&2
  exit 1
fi
