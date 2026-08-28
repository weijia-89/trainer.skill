#!/usr/bin/env bash
# gate_skill_tree.sh — gate the audited skills tree before distribution.
# Exit 0 = GREEN (safe to sync); non-zero = RED (abort sync).
# Env-overridable: GATE_ROOT, GATE_AUDIT (for hermetic tests);
#                 SKILL_TREE_ROOT / SKILL_TREE_OUT (scanner I/O).
set -uo pipefail
AUDIT="$(cd "${GATE_AUDIT:-$(dirname "$0")/..}" && pwd)"
ROOT="${GATE_ROOT:-$HOME/.config/opencode/skills}"
FAIL=0

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
  python3 - "$FINDINGS" "$AUDIT/WAIVERS.json" <<'PYEOF'
import json, sys, fnmatch
try:
    findings = json.load(open(sys.argv[1]))
    waivers = json.load(open(sys.argv[2]))["waivers"]
except Exception as e:
    print("GATE RED: cannot read findings/WAIVERS:", e, file=sys.stderr); sys.exit(1)
def waived(f):
    for w in waivers:
        if f["id"] == w["id"] and fnmatch.fnmatch(f["path"], w["path_prefix"] + "*"):
            return True
    return False
open_f = [f for f in findings if f["sev"] in ("P0","P1","P2","P3") and not waived(f)]
print(f"open P0-P3 after waivers: {len(open_f)}")
for f in open_f[:15]:
    print("  OPEN:", f["sev"], f["id"], f["path"], "-", f["finding"][:90])
sys.exit(1 if open_f else 0)
PYEOF
  [ $? -eq 0 ] || FAIL=1
fi

echo "== gate: bash syntax =="
SH_N=$(find "$ROOT" -name '*.sh' -not -path '*/node_modules/*' | wc -l | tr -d ' ')
while IFS= read -r f; do bash -n "$f" 2>/dev/null || { echo "  SYNTAX FAIL: $f"; FAIL=1; }; done < <(find "$ROOT" -name '*.sh' -not -path '*/node_modules/*')
echo "  checked=$SH_N"

echo "== gate: python compile =="
python3 - "$ROOT" <<'PYEOF'
import pathlib, py_compile, tempfile, os, sys
root = pathlib.Path(sys.argv[1]); tmp = tempfile.mkdtemp(); bad = 0; n = 0
for p in root.rglob("*.py"):
    if "node_modules" in p.parts: continue
    n += 1
    try: py_compile.compile(str(p), doraise=True, cfile=os.path.join(tmp,"c.pyc"))
    except Exception as e: bad += 1; print("  PY FAIL:", p.relative_to(root))
print(f"  checked={n} failures={bad}")
sys.exit(1 if bad else 0)
PYEOF
[ $? -eq 0 ] || FAIL=1

echo "== gate: harness compile (the audit tooling itself) =="
python3 - "$AUDIT/tools" <<'PYEOF'
import pathlib, py_compile, tempfile, os, sys
root = pathlib.Path(sys.argv[1]); tmp = tempfile.mkdtemp(); bad = 0; n = 0
for p in root.rglob("*.py"):
    n += 1
    try: py_compile.compile(str(p), doraise=True, cfile=os.path.join(tmp,"c.pyc"))
    except Exception as e: bad += 1; print("  HARNESS PY FAIL:", p.name, "-", e)
print(f"  checked={n} failures={bad}")
sys.exit(1 if bad else 0)
PYEOF
[ $? -eq 0 ] || FAIL=1

echo "== gate: fences (stateful, fixture-validated, waiver-aware) =="
python3 - "$ROOT" "$AUDIT/WAIVERS.json" <<'PYEOF'
import sys, json, fnmatch
from pathlib import Path
root = Path(sys.argv[1]); wv = sys.argv[2]
try:
    waivers = json.load(open(wv)).get("waivers", [])
except Exception:
    waivers = []
def waived(rel):
    return any(w["id"] == "FENCE" and fnmatch.fnmatch(rel, w["path_prefix"] + "*")
               for w in waivers)
B = chr(96)
def balanced(text):
    opener = None
    for line in text.splitlines():
        s = line.lstrip()
        if not s.startswith(B*3): continue
        st = s.rstrip(); ticks = len(st) - len(st.lstrip(B))
        if opener is None:
            opener = ticks
        elif ticks >= opener and st == B*ticks and ticks <= 40:
            opener = None
    return opener is None
raw = []
for p in root.rglob("*.md"):
    try: t = p.read_text(errors="ignore")
    except Exception: continue
    if not balanced(t):
        rel = str(p.relative_to(root))
        if not waived(rel): raw.append(rel)
print(f"  unclosed-fence files (unwaived)={len(raw)}")
for b in raw: print("   ", b)
sys.exit(1 if raw else 0)
PYEOF
[ $? -eq 0 ] || FAIL=1

echo "== gate: secrets quick-scan =="
if grep -rqE --exclude-dir=.git 'gh[posu]_[A-Za-z0-9]{20,}|BEGIN [A-Z ]*PRIVATE KEY' "$ROOT" --include='*.py' --include='*.sh' --include='*.js' --include='*.cjs' --include='*.mjs' 2>/dev/null; then echo "  SECRET-LIKE MATCH IN CODE"; FAIL=1; else echo "  clean"; fi

echo
[ $FAIL -eq 0 ] && echo "GATE: GREEN ✅" || echo "GATE: RED ❌"
exit $FAIL
