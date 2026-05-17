#!/usr/bin/env bash
# manual_audit.sh
#
# Usage:
#   bash manual_audit.sh <scenario_shortname> <model> <condition> <response_file>
#
# Args:
#   scenario_shortname  one of: 01_red-flag_upstream-constraint-missed
#                              02_test-as-spec_test-locks-in-bug
#                              03_hallucination_library-behavior-unverified
#   model               free-form label: gpt-5, gemini-2.5-pro, opus-4.5-web, etc.
#   condition           baseline | treatment
#   response_file       path to a .txt file containing ONLY the model's response
#
# Behavior:
#   1. Resolves the scenario shortname to a scenario directory.
#   2. Pipes <response_file> contents into that scenario's pass_criteria.py.
#   3. Reports PASS / FAIL.
#   4. Appends one JSONL line to runs/manual/results.jsonl with:
#      ts, scenario_shortname, model, condition, verdict, response_path
#
# Exit code: 0 on PASS, 1 on FAIL, 2 on misuse.

set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PS_DIR="$(dirname "$KIT_DIR")"

if [[ $# -ne 4 ]]; then
  sed -n '2,22p' "$0" >&2
  exit 2
fi

SHORTNAME="$1"
MODEL="$2"
CONDITION="$3"
RESPONSE_FILE="$4"

if [[ "$CONDITION" != "baseline" && "$CONDITION" != "treatment" ]]; then
  echo "ERROR: condition must be 'baseline' or 'treatment' (got '$CONDITION')" >&2
  exit 2
fi

if [[ ! -f "$RESPONSE_FILE" ]]; then
  echo "ERROR: response file not found: $RESPONSE_FILE" >&2
  exit 2
fi

case "$SHORTNAME" in
  01_red-flag_upstream-constraint-missed)
    SCENARIO_DIR="$PS_DIR/red_flag_detection/upstream_constraint_missed" ;;
  02_test-as-spec_test-locks-in-bug)
    SCENARIO_DIR="$PS_DIR/test_as_spec/test_locks_in_bug" ;;
  03_hallucination_library-behavior-unverified)
    SCENARIO_DIR="$PS_DIR/hallucination_floor/library_behavior_unverified" ;;
  *)
    echo "ERROR: unknown scenario shortname: $SHORTNAME" >&2
    echo "Valid: 01_red-flag_upstream-constraint-missed | 02_test-as-spec_test-locks-in-bug | 03_hallucination_library-behavior-unverified" >&2
    exit 2 ;;
esac

PASS_CRITERIA="$SCENARIO_DIR/pass_criteria.py"
if [[ ! -f "$PASS_CRITERIA" ]]; then
  echo "ERROR: pass_criteria.py not found at $PASS_CRITERIA" >&2
  exit 2
fi

# Run the criteria script. It reads response from stdin.
if cat "$RESPONSE_FILE" | python3 "$PASS_CRITERIA" >/dev/null 2>&1; then
  VERDICT="PASS"
else
  VERDICT="FAIL"
fi

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RUN_DIR="$KIT_DIR/runs"
mkdir -p "$RUN_DIR"
RESULTS="$RUN_DIR/results.jsonl"

# Use python to emit a robust JSONL line (handles paths with spaces, etc.).
python3 -c '
import json, sys
rec = {
  "ts":        sys.argv[1],
  "scenario":  sys.argv[2],
  "model":     sys.argv[3],
  "condition": sys.argv[4],
  "verdict":   sys.argv[5],
  "response":  sys.argv[6],
}
print(json.dumps(rec))
' "$TS" "$SHORTNAME" "$MODEL" "$CONDITION" "$VERDICT" "$RESPONSE_FILE" >> "$RESULTS"

echo "$VERDICT  $SHORTNAME  model=$MODEL  condition=$CONDITION"
[[ "$VERDICT" == "PASS" ]]
