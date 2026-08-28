#!/usr/bin/env bash
# gate_skill_tree.sh — gate the audited skills tree before distribution.
# Exit 0 = GREEN (safe to sync); non-zero = RED (abort sync).
# Env-overridable: GATE_ROOT, GATE_AUDIT (for hermetic tests);
#                 SKILL_TREE_ROOT / SKILL_TREE_OUT (scanner I/O).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT="${GATE_AUDIT:-$SCRIPT_DIR/..}"
ROOT="${GATE_ROOT:-$HOME/.config/opencode/skills}"
FAIL=0

# Tool presence guards (generation gate requires command -v for each external tool).
for t in bash find python3; do
  command -v "$t" >/dev/null 2>&1 || { echo "missing required tool: $t" >&2; exit 1; }
done

echo "== gate: structural scan =="
# Fail-closed: if the scanner itself crashes, do NOT judge stale findings.
# Forward SKILL_TREE_ROOT/SKILL_TREE_OUT so the structural scan audits the SAME
# tree the code gates (GATE_ROOT) audit — otherwise an overridden GATE_ROOT
# would be checked against the default skill tree, a silent mismatch.
if ! SKILL_TREE_ROOT="$ROOT" SKILL_TREE_OUT="${SKILL_TREE_OUT:-$AUDIT/findings-skill-tree.json}" python3 "$AUDIT/tools/scan_skill_tree.py" >/dev/null 2>&1; then
  echo "GATE RED: scan_skill_tree.py crashed (not judging stale findings)" >&2
  FAIL=1
else
  FINDINGS="${SKILL_TREE_OUT:-$AUDIT/findings-skill-tree.json}"
  if ! python3 "$AUDIT/tools/gate_subs.py" waivers "$FINDINGS" "$AUDIT/WAIVERS.json"; then FAIL=1; fi
fi

echo "== gate: bash syntax =="
SH_N=$(find "$ROOT" -name '*.sh' -not -path '*/node_modules/*' | wc -l | tr -d ' ')
while IFS= read -r f; do bash -n "$f" 2>/dev/null || { echo "  SYNTAX FAIL: $f"; FAIL=1; }; done < <(find "$ROOT" -name '*.sh' -not -path '*/node_modules/*')
echo "  checked=$SH_N"

echo "== gate: python compile =="
if ! python3 "$AUDIT/tools/gate_subs.py" compile "$ROOT"; then FAIL=1; fi

echo "== gate: harness compile (the audit tooling itself) =="
if ! python3 "$AUDIT/tools/gate_subs.py" compile "$AUDIT/tools"; then FAIL=1; fi

echo "== gate: fences (stateful, fixture-validated, waiver-aware) =="
if ! python3 "$AUDIT/tools/gate_subs.py" fence "$ROOT" "$AUDIT/WAIVERS.json"; then FAIL=1; fi

echo "== gate: secrets quick-scan =="
if grep -rqE --exclude-dir=.git 'gh[posu]_[A-Za-z0-9]{20,}|BEGIN [A-Z ]*PRIVATE KEY' "$ROOT" --include='*.py' --include='*.sh' --include='*.js' --include='*.cjs' --include='*.mjs' 2>/dev/null; then echo "  SECRET-LIKE MATCH IN CODE"; FAIL=1; else echo "  clean"; fi

echo
[ $FAIL -eq 0 ] && echo "GATE: GREEN" || echo "GATE: RED"
exit $FAIL
