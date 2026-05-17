#!/usr/bin/env bash
# run.sh: Phase 11 pressure-scenario driver for form-check. v0.3
#
# Usage:
#   bash run.sh [--adapter <name>] [--category <name>] [--scenario <path>]
#               [--offline] [--skill-file <path>] [--run-dir <path>]
#
# Defaults:
#   --adapter     anthropic_opus   (Claude Opus via Anthropic API; simulates Windsurf+Opus)
#   --category    all
#   --scenario    all
#   --skill-file  <prod-root>/SKILL.md  (override to test mutated skill text per Layer C)
#   --run-dir     runs/<timestamp>      (override to bucket results for Layer C aggregation)
#
# Each scenario produces:
#   runs/<timestamp>/<category>/<scenario>/transcript.json   (adapter output)
#   runs/<timestamp>/<category>/<scenario>/transcript.txt    (response text only)
#   runs/<timestamp>/<category>/<scenario>/verdict.txt       (PASS or FAIL with reasons)
#
# And one aggregate:
#   runs/<timestamp>/results.jsonl                            (one line per scenario)
#   runs/<timestamp>/summary.txt                              (totals + per-category rates)
#
# Production files under form-check.skill/ are NEVER touched.
# RULE #4 (test isolation): production tree SHA is snapshotted before the run and
# re-checked after. Any mutation fails the run loudly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="${ADAPTER:-anthropic_opus}"
CATEGORY="${CATEGORY:-all}"
SCENARIO="${SCENARIO:-all}"
OFFLINE="${OFFLINE:-}"
SKILL_FILE_OVERRIDE="${SKILL_FILE_OVERRIDE:-}"
RUN_DIR_OVERRIDE="${RUN_DIR_OVERRIDE:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --adapter)    ADAPTER="$2";             shift 2 ;;
    --category)   CATEGORY="$2";            shift 2 ;;
    --scenario)   SCENARIO="$2";            shift 2 ;;
    --offline)    OFFLINE="1";              shift 1 ;;
    --skill-file) SKILL_FILE_OVERRIDE="$2"; shift 2 ;;
    --run-dir)    RUN_DIR_OVERRIDE="$2";    shift 2 ;;
    --help|-h)
      sed -n '2,32p' "$0"; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

ADAPTER_SCRIPT="$SCRIPT_DIR/harness_adapters/${ADAPTER}.py"
if [[ ! -f "$ADAPTER_SCRIPT" ]]; then
  echo "FAIL  adapter not found: $ADAPTER_SCRIPT" >&2
  exit 1
fi

# Production root for SHA snapshot. Two levels up from this script:
# pressure_scenarios -> tests -> form-check.skill
PROD_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILL_FILE="${SKILL_FILE_OVERRIDE:-$PROD_ROOT/SKILL.md}"
if [[ ! -f "$SKILL_FILE" ]]; then
  echo "FAIL  expected SKILL.md at $SKILL_FILE" >&2
  exit 1
fi
if [[ -n "$SKILL_FILE_OVERRIDE" ]]; then
  echo "  NOTE: using override skill file: $SKILL_FILE_OVERRIDE" >&2
fi

# Snapshot production tree (excluding the runs/ dir which is the test output).
SNAPSHOT_PRE="$(mktemp)"
SNAPSHOT_POST="$(mktemp)"
trap 'rm -f "$SNAPSHOT_PRE" "$SNAPSHOT_POST"' EXIT INT TERM

(
  cd "$PROD_ROOT"
  find . -type f -not -path './tests/pressure_scenarios/runs/*' -not -path './.git/*' -print0 \
    | xargs -0 shasum -a 256 2>/dev/null \
    | sort > "$SNAPSHOT_PRE"
)

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR_OVERRIDE:-$SCRIPT_DIR/runs/$TIMESTAMP}"
mkdir -p "$RUN_DIR"
RESULTS="$RUN_DIR/results.jsonl"
: > "$RESULTS"

echo "Phase 11 pressure-scenario run"
echo "  adapter:    $ADAPTER"
echo "  category:   $CATEGORY"
echo "  scenario:   $SCENARIO"
echo "  output dir: $RUN_DIR"
if [[ -n "$OFFLINE" ]]; then
  echo "  mode:       OFFLINE (no API calls; all scenarios will FAIL by design)"
  export PHASE11_OFFLINE=1
else
  echo "  mode:       LIVE (will call Anthropic API; requires ANTHROPIC_API_KEY)"
fi
echo ""

# Discover scenarios. A scenario is a dir containing setup.md AND prompt.md AND pass_criteria.py.
declare -a SCENARIOS=()
while IFS= read -r dir; do
  if [[ -f "$dir/setup.md" && -f "$dir/prompt.md" && -f "$dir/pass_criteria.py" ]]; then
    SCENARIOS+=("$dir")
  fi
done < <(find "$SCRIPT_DIR" -mindepth 2 -maxdepth 3 -type d \
            -not -path "*/runs/*" -not -path "*/harness_adapters/*" -not -path "*/scripts/*" \
            | sort)

# Filter by --category / --scenario.
FILTERED=()
for s in "${SCENARIOS[@]}"; do
  cat_name="$(basename "$(dirname "$s")")"
  scen_name="$(basename "$s")"
  if [[ "$CATEGORY" != "all" && "$cat_name" != "$CATEGORY" ]]; then continue; fi
  if [[ "$SCENARIO" != "all" && "$scen_name" != "$SCENARIO" && "$s" != "$SCENARIO" ]]; then continue; fi
  FILTERED+=("$s")
done

if [[ ${#FILTERED[@]} -eq 0 ]]; then
  echo "WARN  no scenarios matched filters (category=$CATEGORY scenario=$SCENARIO)"
fi

total=0; passed=0; failed=0

for s in "${FILTERED[@]}"; do
  cat_name="$(basename "$(dirname "$s")")"
  scen_name="$(basename "$s")"
  total=$((total + 1))

  out_dir="$RUN_DIR/$cat_name/$scen_name"
  mkdir -p "$out_dir"

  user_message="$(cat "$s/prompt.md")"

  # Build adapter request JSON via python (handles escaping robustly).
  req_json="$(python3 -c '
import json, sys
req = {
  "scenario_dir": sys.argv[1],
  "skill_files":  [sys.argv[2]],
  "user_message": open(sys.argv[3], "r", encoding="utf-8").read(),
}
print(json.dumps(req))
' "$s" "$SKILL_FILE" "$s/prompt.md")"

  # Call adapter.
  if ! echo "$req_json" | python3 "$ADAPTER_SCRIPT" > "$out_dir/transcript.json" 2> "$out_dir/adapter.err"; then
    verdict="ADAPTER_ERROR"
    failed=$((failed + 1))
    {
      echo "ADAPTER_ERROR"
      echo "see adapter.err for details"
    } > "$out_dir/verdict.txt"
    printf '{"scenario":"%s/%s","verdict":"%s"}\n' "$cat_name" "$scen_name" "$verdict" >> "$RESULTS"
    echo "  [$cat_name/$scen_name] $verdict"
    continue
  fi

  # Extract response_transcript into a plain text file for pass_criteria.py.
  python3 -c '
import json, sys
data = json.load(open(sys.argv[1]))
sys.stdout.write(data.get("response_transcript", ""))
' "$out_dir/transcript.json" > "$out_dir/transcript.txt"

  # Run pass_criteria.py with transcript on stdin.
  if python3 "$s/pass_criteria.py" < "$out_dir/transcript.txt" > "$out_dir/verdict.txt" 2>&1; then
    verdict="PASS"
    passed=$((passed + 1))
  else
    verdict="FAIL"
    failed=$((failed + 1))
  fi
  printf '{"category":"%s","scenario":"%s/%s","verdict":"%s"}\n' \
    "$cat_name" "$cat_name" "$scen_name" "$verdict" >> "$RESULTS"
  echo "  [$cat_name/$scen_name] $verdict"
done

# Aggregate summary (per-category rates computed by python over results.jsonl).
python3 - "$RESULTS" "$RUN_DIR/summary.txt" "$TIMESTAMP" "$ADAPTER" "$total" "$passed" "$failed" <<'PY'
import json, sys
from collections import defaultdict
results_path, summary_path, ts, adapter, total, passed, failed = sys.argv[1:]
cats = defaultdict(lambda: {"total": 0, "passed": 0})
with open(results_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        c = rec.get("category", "?")
        cats[c]["total"] += 1
        if rec.get("verdict") == "PASS":
            cats[c]["passed"] += 1
lines = [
    "Phase 11 run summary",
    f"  timestamp: {ts}",
    f"  adapter:   {adapter}",
    f"  total:     {total}",
    f"  passed:    {passed}",
    f"  failed:    {failed}",
    "",
    "Per-category pass rates:",
]
for c in sorted(cats):
    p, t = cats[c]["passed"], cats[c]["total"]
    lines.append(f"  {c}: {p} / {t}")
text = "\n".join(lines) + "\n"
sys.stdout.write(text)
with open(summary_path, "w") as f:
    f.write(text)
PY
echo ""

# RULE #4: verify production tree byte-identical.
(
  cd "$PROD_ROOT"
  find . -type f -not -path './tests/pressure_scenarios/runs/*' -not -path './.git/*' -print0 \
    | xargs -0 shasum -a 256 2>/dev/null \
    | sort > "$SNAPSHOT_POST"
)
if ! diff -q "$SNAPSHOT_PRE" "$SNAPSHOT_POST" >/dev/null; then
  echo "FAIL  production tree changed during run (RULE #4 violation):"
  diff "$SNAPSHOT_PRE" "$SNAPSHOT_POST" | head -40 | sed 's/^/  /'
  exit 1
else
  echo "PASS  production tree byte-identical before and after run (RULE #4 satisfied)"
fi

if [[ "$total" -eq 0 ]]; then
  echo "VERDICT: NO-OP (no scenarios matched filters)"
  exit 0
fi
if [[ "$failed" -gt 0 ]]; then
  exit 1
fi
echo "VERDICT: ALL-PASS"
