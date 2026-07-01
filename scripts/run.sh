#!/usr/bin/env bash
# run.sh: Phase 11 pressure-scenario driver for trainer.skill.
# Ported from specialists/form-check run.sh. Adds --k repeat (stability gate).
#
# Usage:
#   bash scripts/run.sh [--adapter anthropic_opus] [--category all] [--scenario all]
#                       [--offline] [--skill-file <path>] [--run-dir <path>] [--k N]
#
# RULE #4: production tree SHA snapshotted before/after; any mutation fails loudly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HARNESS_DIR="$REPO_ROOT/tests/scenarios/harness"

ADAPTER="${ADAPTER:-anthropic_opus}"
CATEGORY="${CATEGORY:-all}"
SCENARIO="${SCENARIO:-all}"
OFFLINE="${OFFLINE:-}"
SKILL_FILE_OVERRIDE="${SKILL_FILE_OVERRIDE:-}"
RUN_DIR_OVERRIDE="${RUN_DIR_OVERRIDE:-}"
K="${PHASE11_K:-3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --adapter) ADAPTER="$2"; shift 2 ;;
    --category) CATEGORY="$2"; shift 2 ;;
    --scenario) SCENARIO="$2"; shift 2 ;;
    --offline) OFFLINE="1"; shift 1 ;;
    --skill-file) SKILL_FILE_OVERRIDE="$2"; shift 2 ;;
    --run-dir) RUN_DIR_OVERRIDE="$2"; shift 2 ;;
    --k) K="$2"; shift 2 ;;
    --help|-h) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

ADAPTER_SCRIPT="$SCRIPT_DIR/harness_adapters/${ADAPTER}.py"
[[ -f "$ADAPTER_SCRIPT" ]] || { echo "FAIL adapter not found: $ADAPTER_SCRIPT" >&2; exit 1; }

SKILL_FILE="${SKILL_FILE_OVERRIDE:-$REPO_ROOT/SKILL.md}"
[[ -f "$SKILL_FILE" ]] || { echo "FAIL expected SKILL.md at $SKILL_FILE" >&2; exit 1; }
[[ -n "$SKILL_FILE_OVERRIDE" ]] && echo "  NOTE: override skill file: $SKILL_FILE_OVERRIDE" >&2

SNAP_PRE="$(mktemp)"
SNAP_POST="$(mktemp)"
trap 'rm -f "$SNAP_PRE" "$SNAP_POST"' EXIT INT TERM
snapshot() {
  (
    cd "$REPO_ROOT"
    find . -type f -not -path './tests/scenarios/harness/runs/*' -not -path './.git/*' -not -path '*/__pycache__/*' -print0 \
      | xargs -0 shasum -a 256 2>/dev/null | sort > "$1"
  )
}
snapshot "$SNAP_PRE"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR_OVERRIDE:-$HARNESS_DIR/runs/$TIMESTAMP}"
mkdir -p "$RUN_DIR"
RESULTS="$RUN_DIR/results.jsonl"
: > "$RESULTS"
[[ -n "$OFFLINE" ]] && export PHASE11_OFFLINE=1

echo "Phase 11 trainer run  adapter=$ADAPTER k=$K out=$RUN_DIR ${OFFLINE:+(OFFLINE)}"

declare -a SCEN=()
while IFS= read -r d; do
  [[ -f "$d/setup.md" && -f "$d/prompt.md" && -f "$d/pass_criteria.py" ]] && SCEN+=("$d")
done < <(find "$HARNESS_DIR" -mindepth 1 -maxdepth 2 -type d -not -path "*/runs/*" | sort)

total=0
fail_any=0
for s in "${SCEN[@]}"; do
  name="$(basename "$s")"
  [[ "$SCENARIO" != "all" && "$name" != "$SCENARIO" && "$s" != "$SCENARIO" ]] && continue
  total=$((total + 1))
  out_dir="$RUN_DIR/$name"
  mkdir -p "$out_dir"
  passes=0
  for i in $(seq 1 "$K"); do
    req="$(python3 -c 'import json,sys; print(json.dumps({
      "scenario_dir": sys.argv[1], "skill_files":[sys.argv[2]],
      "user_message": open(sys.argv[3]).read(), "seed": int(sys.argv[4])}))' \
      "$s" "$SKILL_FILE" "$s/prompt.md" "$i")"
    echo "$req" | python3 "$ADAPTER_SCRIPT" > "$out_dir/transcript.$i.json" 2>"$out_dir/adapter.$i.err" || true
    python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.stdout.write(d.get("response_transcript",""))' \
      "$out_dir/transcript.$i.json" > "$out_dir/transcript.$i.txt" 2>/dev/null || true
    if python3 "$s/pass_criteria.py" < "$out_dir/transcript.$i.txt" >/dev/null 2>&1; then
      passes=$((passes + 1))
    fi
  done
  rate="$(python3 -c "print(f'{$passes/$K:.2f}')")"
  [[ "$passes" -lt "$K" ]] && fail_any=1
  printf '{"scenario":"%s","k":%s,"passes":%s,"pass_rate":%s}\n' "$name" "$K" "$passes" "$rate" >> "$RESULTS"
  echo "  [$name] pass-rate $passes/$K ($rate)"
done

python3 - "$RESULTS" "$RUN_DIR/summary.txt" "$TIMESTAMP" "$ADAPTER" "$K" <<'PY'
import json
import sys

res, summ, ts, adapter, k = sys.argv[1:6]
rows = [json.loads(line) for line in open(res) if line.strip()]
lines = [f"Phase 11 trainer summary  ts={ts} adapter={adapter} k={k}", "", "Per-scenario pass-rate:"]
for r in rows:
    lines.append(f"  {r['scenario']}: {r['passes']}/{r['k']} ({r['pass_rate']})")
open(summ, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
PY

snapshot "$SNAP_POST"
if ! diff -q "$SNAP_PRE" "$SNAP_POST" >/dev/null; then
  echo "FAIL production tree changed during run (RULE #4):"
  diff "$SNAP_PRE" "$SNAP_POST" | head -20
  exit 1
fi
echo "PASS RULE #4 (prod tree byte-identical)"
[[ "$total" -eq 0 ]] && { echo "NO-OP"; exit 0; }
[[ "$fail_any" -ne 0 ]] && exit 1
echo "VERDICT: ALL-PASS across k=$K"
