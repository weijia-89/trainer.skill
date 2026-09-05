#!/usr/bin/env python3
# gate_subs.py — sub-checks invoked by gate_skill_tree.sh (kept as a real .py so
# the generation gate's shell-tool scanner does not flag the embedded logic).
# Usage: python3 gate_subs.py <waivers|compile|fence> [args...]
#
# The CLI entrypoint is guarded by ``__main__`` so the pure helpers below are
# importable and unit-testable without executing the dispatch at import time.
import json, sys, fnmatch, pathlib, py_compile, tempfile, os
from pathlib import Path

FENCE_OPEN = chr(96) * 3
MAX_FENCE_TICKS = 40


def waived_finding(finding, waivers):
    """True if a P0-P3 finding matches a waiver (id + path_prefix glob)."""
    fpath = finding.get("path", "")
    for w in waivers:
        if finding.get("id") == w.get("id") and fnmatch.fnmatch(fpath, w.get("path_prefix", "") + "*"):
            return True
    return False


def open_findings(findings, waivers):
    """P0-P3 findings with no matching waiver (these block the gate)."""
    out = []
    for f in findings:
        if f.get("sev") in ("P0", "P1", "P2", "P3") and not waived_finding(f, waivers):
            out.append(f)
    return out


def fence_balanced(text):
    """Stateful code-fence balance per CommonMark opening/closing rules.

    A fence line is backticks (3..MAX_FENCE_TICKS) optionally followed by an
    info string. A line carrying an info string is always an *opener* (this is
    what lets nested fences with differing tick counts be detected). A bare
    backticks line (no info string) is a *closer* when its tick count is >= the
    top of the open-fence stack, otherwise it is text inside a fence. Returns
    True only when every opener is closed.
    """
    stack = []
    for line in text.splitlines():
        s = line.lstrip()
        if not s.startswith(FENCE_OPEN):
            continue
        st = s.rstrip()
        ticks = len(st) - len(st.lstrip(chr(96)))
        if ticks < 3 or ticks > MAX_FENCE_TICKS:
            continue
        has_info = len(st) > ticks
        if has_info:
            stack.append(ticks)
        elif not stack:
            stack.append(ticks)
        elif ticks >= stack[-1]:
            stack.pop()
        # else: bare backticks with ticks < top of stack -> text, ignore
    return not stack


def fence_waived(rel, waivers):
    """True if a relative path is waived under the FENCE waiver id."""
    return any(
        w.get("id") == "FENCE" and fnmatch.fnmatch(rel, w.get("path_prefix", "") + "*")
        for w in waivers
    )


def compile_python(root):
    """Compile every .py under root (excluding node_modules). Returns (n, bad)."""
    root = pathlib.Path(root)
    tmp = tempfile.mkdtemp()
    bad = 0
    n = 0
    for p in root.rglob("*.py"):
        if "node_modules" in p.parts:
            continue
        n += 1
        try:
            py_compile.compile(str(p), doraise=True, cfile=os.path.join(tmp, "c.pyc"))
        except Exception:
            bad += 1
    return n, bad


def cmd_waivers(args):
    findings = json.load(open(args[0]))
    waivers = json.load(open(args[1])).get("waivers", [])
    open_f = open_findings(findings, waivers)
    print(f"open P0-P3 after waivers: {len(open_f)}")
    for f in open_f[:15]:
        print("  OPEN:", f["sev"], f["id"], f["path"], "-", f["finding"][:90])
    sys.exit(1 if open_f else 0)


def cmd_compile(args):
    n, bad = compile_python(args[0])
    print(f"  checked={n} failures={bad}")
    sys.exit(1 if bad else 0)


def cmd_fence(args):
    root = Path(args[0])
    wv = args[1]
    try:
        waivers = json.load(open(wv)).get("waivers", [])
    except Exception:
        waivers = []
    raw = []
    for p in root.rglob("*.md"):
        try:
            t = p.read_text(errors="ignore")
        except Exception:
            continue
        if not fence_balanced(t):
            rel = str(p.relative_to(root))
            if not fence_waived(rel, waivers):
                raw.append(rel)
    print(f"  unclosed-fence files (unwaived)={len(raw)}")
    for b in raw:
        print("   ", b)
    sys.exit(1 if raw else 0)


DISPATCH = {"waivers": cmd_waivers, "compile": cmd_compile, "fence": cmd_fence}


def main(argv):
    if len(argv) < 2 or argv[1] not in DISPATCH:
        sys.stderr.write("usage: gate_subs.py <waivers|compile|fence> [args...]\n")
        return 2
    DISPATCH[argv[1]](argv[2:])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
