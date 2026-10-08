---
name: code_shape
version: 1.0.0
parent_skill: form-check
source: YUAN-2014; CASALNUOVO-2015; POWER-OF-TEN-2006; TIGER-STYLE; PYTHON-ASSERT-DOCS
---

# Code shape: error paths, assertions, bounds, size

Use this checklist when reviewing or planning **program code** (Python, TypeScript, Go, Rust, shell). Skip it for prose, skill files, and throwaway scripts. It covers how code is shaped, which `bug_class_audit.md` does not.

Two terms used throughout:

- **Assertion**: a check that stops the program when something impossible has happened. Example: `assert balance >= 0` right after your own arithmetic. Right response to failure: crash.
- **Validation**: a check on input that can legitimately be bad. Example: rejecting a blank email field. Right response to failure: handle it and tell the caller.

Evidence is uneven, so each item carries a tier. Items 1 and 2 have empirical backing. Items 3 to 7 are expert-opinion rules of thumb: raise them as P2 findings, never as merge blockers.

## Walk

1. **Error paths are handled and tested** (`YUAN-2014`, `[T1-verified]`, confidence 65).
   - Question: for each call that can fail, is the failure handled, and does a test force that failure?
   - Sample defense: no empty `except` or `catch`; one test per failure branch. When you log a failure, leave out secrets (tokens, passwords, full request bodies).
   - Scope: the study covered 198 failures in five distributed data systems. It found 92% of catastrophic failures came from mishandled non-fatal errors. Do not quote it as a rate for all software.
   - Severity: P1 on money, data, or auth paths; otherwise P2.

2. **Assertions and validation stay separate** (`CASALNUOVO-2015`, `[T1-verified]`, confidence 60).
   - Question: for each check, is it an impossible state (assert, crash) or expected bad input (validate, handle)?
   - Evidence: in C and C++ projects, functions with assertions had significantly fewer defects. This is a correlation. It supports asserting impossible states. It does not support a target count.
   - Do not import "two assertions per function" as a gate. Treat it as a convention from `POWER-OF-TEN-2006` and `TIGER-STYLE`.
   - Sources disagree on failure: `POWER-OF-TEN-2006` says return an error to the caller; `TIGER-STYLE` says crash. Crash on internal invariants; return an error at any boundary where the caller can act.
   - Python: `assert` lines are removed under the optimize flag (`-O`) (`PYTHON-ASSERT-DOCS`). A check that must survive in production needs an explicit `raise`.
   - Never crash on bad input from users, files, or other services. That is validation. A crash that outside input can trigger is a denial-of-service hole.

3. **Loops, queues, and retries have a fixed upper limit** (`POWER-OF-TEN-2006`, `TIGER-STYLE`, `[normative]`, confidence 45).
   - Question: what stops this loop, queue, or retry? Example: a retry that gives up after 5 tries.
   - Cross-reference: `bug_class_audit.md` item 24 covers unbounded input as a security risk. This item covers design-time bounds.
   - Severity: P2. If input from outside the program sets the size, report it under `bug_class_audit.md` item 24 instead.

4. **Function size is about one screen** (confidence 45; no study found tying function length to defects).
   - Question: can a reader see the whole function without scrolling? Sources give about 60 lines (`POWER-OF-TEN-2006`) and 70 (`TIGER-STYLE`).
   - Rule of thumb only. Long and clear beats short and tangled.

5. **Control flow stays shallow** (`TIGER-STYLE`, `[normative]`, confidence 45).
   - Push `if` decisions up into the parent function and `for` loops down into helpers. The parent decides; helpers calculate and stay free of branching.
   - State conditions in the positive form (`if index < count`). Split `a and b` into nested checks.

6. **Names carry meaning** (`TIGER-STYLE`, `[normative]`, confidence 45).
   - Keep index (position, starts at 0), count (how many), and size (bytes) as separate ideas. Index to count adds one. Count to size multiplies by the unit.
   - Put units last in names: `latency_ms_max`, not `max_latency_ms`.

7. **One copy of each piece of state** (`TIGER-STYLE`, `[normative]`, confidence 45).
   - Question: is any value stored twice, so the copies can drift apart? Declare variables as late and as narrowly as you can.

## Cross-references

- `bug_class_audit.md` item 24: unbounded input as a security risk (pairs with item 3).
- `bug_class_audit.md`: the main code-review walk; run it first, then this one.
- `INDEX.md`: routes code-review work here.

## Does not apply to

- Prose, skill files, and one-off scripts.
- Language-specific `TIGER-STYLE` rules: no recursion, fixed-size integers, allocating memory once at startup, 100-column lines, zero dependencies.

## Output format

Same table as `bug_class_audit.md`. Confidence for each finding is capped by the evidence behind its item: 70 for a single study, 60 for a correlation, 45 for expert opinion.

| ID | Item | File:line | Severity | Reproduction | Proposed fix | Confidence (0–100) |
|---|---|---|---|---|---|---|
| P1-01 | 1 | sync.py:88 | P1 | `except Exception: pass` around the write | handle, log, add failure test | 65 |
