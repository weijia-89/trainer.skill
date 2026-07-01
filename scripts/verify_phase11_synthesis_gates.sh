#!/usr/bin/env bash
# verify_phase11_synthesis_gates.sh — ChatPRD synthesis plan offline gates (WP-0..WP-5).
# Live blind audit (--k 3 without --offline) is operator-opt-in; not required here.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
FAIL=0

say() { echo "$@"; }
pass() { say "PASS $*"; }
fail() { say "FAIL $*"; FAIL=1; }

say "=== Phase 11 synthesis gates (offline) ==="

# 0.4 post-placement
say "--- Gate 0.4 post-placement ---"
if bash -n scripts/*.sh 2>/dev/null; then pass "bash -n scripts/*.sh"; else fail "bash -n scripts/*.sh"; fi
if python3 -c "
import ast, pathlib
for p in [
    'scripts/calibration_analyze.py','scripts/mutation_test_skill.py','scripts/phase11_report.py',
    'tests/scenarios/harness/_repro.py','tests/scenarios/harness/_grading.py',
    'scripts/harness_adapters/anthropic_opus.py',
]:
    ast.parse(pathlib.Path(p).read_text())
print('python parses')
"; then pass "python ast parse"; else fail "python ast parse"; fi
if python3 tests/scenarios/harness/_repro.py >/dev/null 2>&1; then pass "_repro.py"; else fail "_repro.py"; fi
if echo '{"skill_files":[],"user_message":"hi","seed":1}' | PHASE11_OFFLINE=1 python3 scripts/harness_adapters/anthropic_opus.py \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "stub" in d["response_transcript"]; print("adapter ok")' 2>/dev/null; then
  pass "adapter offline stub"
else
  fail "adapter offline stub"
fi
grep -q 'with_floor' tests/scenarios/harness/_grading.py && pass "with_floor present" || fail "with_floor missing"
grep -q '_SENTENCE_BREAK' tests/scenarios/harness/_grading.py && pass "_SENTENCE_BREAK present" || fail "_SENTENCE_BREAK missing"

# Gate 1 — T1.1 with_floor
say "--- Gate 1 WP-1 ---"
if python3 - <<'PY'
import sys
sys.path.insert(0, "tests/scenarios/harness")
from _grading import Transcript
t = Transcript("Commit 1: test. Commit 2: fix.")
assert "commit 1" not in t
assert "commit 1" in t.with_floor(2)
soup = Transcript("refuse. hallucination. blast radius. safetybar.")
assert "safetybar" not in soup
print("with_floor ok")
PY
then pass "T1.1 with_floor"; else fail "T1.1 with_floor"; fi

# T1.3 calibration
mkdir -p /tmp/trainer-calib-test
printf '{"e":1}\n{"e":2}\n{"e":3}\n' > /tmp/trainer-calib-test/c.jsonl
if python3 scripts/calibration_analyze.py --log /tmp/trainer-calib-test/c.jsonl >/dev/null 2>&1; then
  pass "T1.3 calibration_analyze"
else
  fail "T1.3 calibration_analyze"
fi
if grep -q "Explicitly NO sequential" scripts/calibration_analyze.py && \
   grep -q "refuse threshold conclusions" scripts/calibration_analyze.py; then
  pass "T1.3 honest-empty Layer B contract"
else
  fail "T1.3 honest-empty Layer B contract"
fi

# T1.4 reference self-pass
for s in ceremonial_routing coaching_collapse_on_i_know bypass_for_small_task; do
  d="tests/scenarios/harness/$s"
  if python3 "$d/pass_criteria.py" < "$d/reference_response.md" >/dev/null 2>&1; then
    pass "T1.4 $s"
  else
    fail "T1.4 $s"
  fi
done

# Gate 2 — offline run produces summary (scenarios fail by design)
say "--- Gate 2 WP-2 ---"
if bash scripts/run.sh --offline --k 3 >/dev/null 2>&1; then
  fail "run.sh --offline --k 3 should exit 1 when scenarios fail"
else
  pass "run.sh --offline --k 3 exits non-zero on scenario fail"
fi
if compgen -G "tests/scenarios/harness/runs/*/summary.txt" >/dev/null; then
  pass "summary.txt exists"
else
  fail "summary.txt missing"
fi
report="$(python3 scripts/phase11_report.py --stdout 2>/dev/null || true)"
if echo "$report" | grep -q "Layer A"; then
  pass "phase11_report.py renders Layer A"
else
  fail "phase11_report.py"
fi

# Gate 3
say "--- Gate 3 WP-3 ---"
if bash scripts/verify_phase11_isolation.sh >/dev/null 2>&1; then pass "isolation"; else fail "isolation"; fi

# Gate 4 prose grep targets (honest-scope)
say "--- Gate 4 WP-4 ---"
grep -q "falsifiability" README.md && pass "README falsifiability" || fail "README falsifiability"
grep -q "measured behavioral-delta" README.md && pass "README not delta claim" || fail "README delta disclaimer"
test -f references/trainer-implementation-babysitter.md && pass "babysitter ref exists" || fail "babysitter ref"

# Gate 5 WP-5 integration (offline)
say "--- Gate 5 WP-5 ---"
if GITHUB_ACTIONS=true GITHUB_WORKSPACE="$REPO_ROOT" bash scripts/verify_trainer_sync.sh >/dev/null 2>&1; then
  pass "verify_trainer_sync.sh"
else
  fail "verify_trainer_sync.sh"
fi

if [[ "$FAIL" -ne 0 ]]; then
  say ""
  say "VERDICT: FAIL"
  exit 1
fi
say ""
say "VERDICT: PASS (offline synthesis gates)"
say "NOTE: live blind audit waived unless operator sets ANTHROPIC_MODEL + ANTHROPIC_API_KEY"
