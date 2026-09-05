#!/usr/bin/env python3
# Zero-dependency unit tests for form-check/tools/gate_subs.py.
# Run: python3 tests/test_gate_subs.py   (exit non-zero on any failure)
#
# Covers the three sub-checks the gate delegates here:
#   - waivers  : P0-P3 findings vs waiver id+path_prefix globs
#   - compile  : python byte-compile of a tree (node_modules excluded)
#   - fence    : stateful code-fence balance across .md files
# Pure helpers are tested directly; the CLI exit-code contract is locked with
# real subprocess invocations so a behavior regression in gate_skill_tree.sh
# cannot slip through.
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
GATE_SUBS = TOOLS / "gate_subs.py"

sys.path.insert(0, str(TOOLS))
import gate_subs  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILS.append(name)


def _write(tmp, name, data):
    p = Path(tmp) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")
    return p


def _findings_file(tmp, findings):
    return _write(tmp, "findings.json", json.dumps(findings))


def _waivers_file(tmp, waivers):
    return _write(tmp, "waivers.json", json.dumps({"waivers": waivers}))


def _run(args):
    return subprocess.run(
        [sys.executable, str(GATE_SUBS), *args],
        capture_output=True, text=True,
    )


# --------------------------------------------------------------------------
# Importability: importing the module must NOT run the CLI dispatch.
# --------------------------------------------------------------------------
def test_module_import_has_no_side_effects():
    check("import: main callable + helpers present",
          callable(gate_subs.main) and hasattr(gate_subs, "open_findings")
          and hasattr(gate_subs, "fence_balanced"))


# --------------------------------------------------------------------------
# waivers
# --------------------------------------------------------------------------
def test_waived_finding_exact_id_and_path():
    w = [{"id": "C1", "path_prefix": "specialists/foo"}]
    f = {"id": "C1", "sev": "P2", "path": "specialists/foo/bar.md"}
    check("waivers: exact id+path waived", gate_subs.waived_finding(f, w) is True)


def test_waived_finding_path_glob_prefix():
    w = [{"id": "C2", "path_prefix": "specialists/foo*"}]
    f = {"id": "C2", "sev": "P2", "path": "specialists/foo/nested/deep.md"}
    check("waivers: glob path_prefix matches nested", gate_subs.waived_finding(f, w) is True)


def test_waived_finding_nonmatching_path():
    w = [{"id": "C2", "path_prefix": "specialists/foo*"}]
    f = {"id": "C2", "sev": "P2", "path": "specialists/bar/x.md"}
    check("waivers: nonmatching path not waived", gate_subs.waived_finding(f, w) is False)


def test_waived_finding_nonmatching_id():
    w = [{"id": "C2", "path_prefix": "specialists/foo*"}]
    f = {"id": "C9", "sev": "P2", "path": "specialists/foo/x.md"}
    check("waivers: nonmatching id not waived", gate_subs.waived_finding(f, w) is False)


def test_open_findings_excludes_p4():
    waivers = []
    findings = [
        {"id": "C1", "sev": "P4", "path": "a.md", "finding": "info only"},
        {"id": "C2", "sev": "P2", "path": "b.md", "finding": "blocker"},
    ]
    open_f = gate_subs.open_findings(findings, waivers)
    check("waivers: P4 excluded from open set", [x["id"] for x in open_f] == ["C2"])


def test_open_findings_empty_waivers_keeps_all_p0_p3():
    findings = [
        {"id": "S1", "sev": "P0", "path": "a.md"},
        {"id": "S8", "sev": "P3", "path": "b.md"},
        {"id": "C1", "sev": "P4", "path": "c.md"},
    ]
    open_f = gate_subs.open_findings(findings, [])
    check("waivers: P0+P3 open when no waivers", {x["id"] for x in open_f} == {"S1", "S8"})


def test_open_findings_empty_findings():
    check("waivers: empty findings -> empty open",
          gate_subs.open_findings([], [{"id": "X", "path_prefix": "*"}]) == [])


def test_open_findings_p0_unwaived_blocks():
    findings = [{"id": "S1", "sev": "P0", "path": "a.md"}]
    check("waivers: unwaived P0 blocks gate", bool(gate_subs.open_findings(findings, [])))


# --------------------------------------------------------------------------
# fence_balanced
# --------------------------------------------------------------------------
def test_fence_balanced_simple():
    check("fence: simple balanced", gate_subs.fence_balanced("```\ncode\n```\n") is True)


def test_fence_balanced_unclosed():
    check("fence: unclosed detected", gate_subs.fence_balanced("```\ncode\n") is False)


def test_fence_balanced_nested():
    # Valid CommonMark nesting: inner fence carries an info string so it opens
    # (not closes) the outer; both close in order.
    text = "```python\nouter\n````rust\ninner\n````\n```\n"
    check("fence: nested balanced (info strings)", gate_subs.fence_balanced(text) is True)


def test_fence_balanced_bare_nested_unbalanced():
    # Without info strings the inner 4-tick line closes the outer 3-tick fence,
    # leaving the trailing 3-tick line as an unclosed opener -> unbalanced.
    check("fence: bare nested unbalanced",
          gate_subs.fence_balanced("```\nouter\n````\ninner\n````\n```\n") is False)


def test_fence_balanced_indented():
    check("fence: indented balanced", gate_subs.fence_balanced("  ```\n  code\n  ```\n") is True)


def test_fence_balanced_info_string():
    check("fence: info-string balanced", gate_subs.fence_balanced("```python\nx=1\n```\n") is True)


def test_fence_balanced_mismatched_ticks():
    check("fence: 4-open/3-close unbalanced", gate_subs.fence_balanced("````\ncode\n```\n") is False)


def test_fence_balanced_ignores_overlong_41_ticks():
    long = chr(96) * 41
    check("fence: 41-tick line ignored", gate_subs.fence_balanced(f"{long}\ncode\n") is True)


def test_fence_balanced_closes_only_when_ticks_ge_opener():
    check("fence: stray 3-tick stays open", gate_subs.fence_balanced("```\n````\n```\n") is False)


# --------------------------------------------------------------------------
# fence_waived
# --------------------------------------------------------------------------
def test_fence_waived_match():
    w = [{"id": "FENCE", "path_prefix": "docs/*"}]
    check("fence-waive: matching path waived", gate_subs.fence_waived("docs/guide.md", w) is True)


def test_fence_waived_nonmatch():
    w = [{"id": "FENCE", "path_prefix": "docs/*"}]
    check("fence-waive: nonmatching path not waived",
          gate_subs.fence_waived("specialists/x.md", w) is False)


def test_fence_waived_requires_fence_id():
    w = [{"id": "C1", "path_prefix": "*"}]
    check("fence-waive: only FENCE id waives", gate_subs.fence_waived("anything.md", w) is False)


# --------------------------------------------------------------------------
# compile_python
# --------------------------------------------------------------------------
def test_compile_python_clean():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "good.py", "def f():\n    return 1\n")
        n, bad = gate_subs.compile_python(d)
        check("compile: clean tree (1,0)", n == 1 and bad == 0)


def test_compile_python_syntax_error():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "bad.py", "def f(\n")
        n, bad = gate_subs.compile_python(d)
        check("compile: syntax error counted (1,1)", n == 1 and bad == 1)


def test_compile_python_excludes_node_modules():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "good.py", "x=1\n")
        _write(d, "node_modules/pkg/bad.py", "def f(\n")
        n, bad = gate_subs.compile_python(d)
        check("compile: node_modules excluded", n == 1 and bad == 0)


# --------------------------------------------------------------------------
# CLI contract (exit codes) — locks gate_skill_tree.sh behavior.
# --------------------------------------------------------------------------
def test_cli_waivers_exit_nonzero_when_open():
    with tempfile.TemporaryDirectory() as d:
        f = _findings_file(d, [{"id": "C1", "sev": "P2", "path": "a.md", "finding": "x"}])
        w = _waivers_file(d, [])
        r = _run(["waivers", str(f), str(w)])
        check("cli waivers: open -> rc=1", r.returncode == 1, f"rc={r.returncode}")
        check("cli waivers: prints open count", "open P0-P3 after waivers: 1" in r.stdout)


def test_cli_waivers_exit_zero_when_clean():
    with tempfile.TemporaryDirectory() as d:
        f = _findings_file(d, [{"id": "C1", "sev": "P4", "path": "a.md", "finding": "info"}])
        w = _waivers_file(d, [])
        r = _run(["waivers", str(f), str(w)])
        check("cli waivers: clean -> rc=0", r.returncode == 0)


def test_cli_fence_exit_nonzero_on_unclosed():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "broken.md", "```\nunclosed\n")
        w = _waivers_file(d, [])
        r = _run(["fence", str(d), str(w)])
        check("cli fence: unclosed -> rc=1", r.returncode == 1)
        check("cli fence: names offending file", "broken.md" in r.stdout)


def test_cli_fence_exit_zero_when_balanced():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "ok.md", "```\nclosed\n```\n")
        w = _waivers_file(d, [])
        r = _run(["fence", str(d), str(w)])
        check("cli fence: balanced -> rc=0", r.returncode == 0)


def test_cli_compile_exit_nonzero_on_bad():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "bad.py", "def f(\n")
        r = _run(["compile", str(d)])
        check("cli compile: bad -> rc=1", r.returncode == 1)
        check("cli compile: reports failures", "failures=1" in r.stdout)


def test_cli_compile_exit_zero_when_clean():
    with tempfile.TemporaryDirectory() as d:
        _write(d, "good.py", "x=1\n")
        r = _run(["compile", str(d)])
        check("cli compile: clean -> rc=0", r.returncode == 0)


def test_cli_unknown_subcommand_exits_two():
    r = _run(["bogus"])
    check("cli: unknown subcommand -> rc=2", r.returncode == 2)


def main():
    test_module_import_has_no_side_effects()
    test_waived_finding_exact_id_and_path()
    test_waived_finding_path_glob_prefix()
    test_waived_finding_nonmatching_path()
    test_waived_finding_nonmatching_id()
    test_open_findings_excludes_p4()
    test_open_findings_empty_waivers_keeps_all_p0_p3()
    test_open_findings_empty_findings()
    test_open_findings_p0_unwaived_blocks()
    test_fence_balanced_simple()
    test_fence_balanced_unclosed()
    test_fence_balanced_nested()
    test_fence_balanced_indented()
    test_fence_balanced_info_string()
    test_fence_balanced_mismatched_ticks()
    test_fence_balanced_ignores_overlong_41_ticks()
    test_fence_balanced_closes_only_when_ticks_ge_opener()
    test_fence_waived_match()
    test_fence_waived_nonmatch()
    test_fence_waived_requires_fence_id()
    test_compile_python_clean()
    test_compile_python_syntax_error()
    test_compile_python_excludes_node_modules()
    test_cli_waivers_exit_nonzero_when_open()
    test_cli_waivers_exit_zero_when_clean()
    test_cli_fence_exit_nonzero_on_unclosed()
    test_cli_fence_exit_zero_when_balanced()
    test_cli_compile_exit_nonzero_on_bad()
    test_cli_compile_exit_zero_when_clean()
    test_cli_unknown_subcommand_exits_two()
    if FAILS:
        print(f"\nFAILURES: {FAILS}")
        sys.exit(1)
    print("\ntest_gate_subs: GREEN")


if __name__ == "__main__":
    main()
