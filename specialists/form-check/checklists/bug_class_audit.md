---
name: bug_class_audit
version: 2.0.0
parent_skill: form-check
sources: [CWE-25-2025, GITCLEAR-2025, ACM-COPILOT-CORRECT, ACM-COPILOT-SEC, SLOP-arXiv, PIRANESI-C01, PIRANESI-C02, PIRANESI-C03, PIRANESI-CPW1, PIRANESI-CPW2, PIRANESI-UU1, PIRANESI-UU2, PIRANESI-UU3, PIRANESI-UU4, PIRANESI-UU5, PIRANESI-DG008]
---

# Bug-Class Audit Checklist

Walk this for every adversarial review. Two lenses: MITRE CWE Top-25 (2025) for traditional bug classes, and AI-PR-specific shapes for the 2024–2026 vibe-coded patterns. Cross-reference applicable OWASP lists per `INDEX.md`.

## A, CWE Top-25 (2025) lens

For each, ask: **does this surface exist in this code?** If yes, how is it defended?

1. **CWE-79 XSS**, user input rendered to HTML/JSX without context-appropriate encoding?
2. **CWE-787 Out-of-bounds Write**, buffer / array math in C-extensions, ctypes, raw socket?
3. **CWE-89 SQL Injection**, SQL strings built with f-strings / `.format()` / template literals over user input?
4. **CWE-352 CSRF**, state-changing endpoints with no token check (or no SameSite cookie)?
5. **CWE-22 Path Traversal**, file paths derived from user input without `Path.resolve()` + scope check?
6. **CWE-125 Out-of-bounds Read**, same as 787, read side
7. **CWE-78 OS Command Injection**, `subprocess`/`os.system`/`Runtime.exec` with `shell=True` over interpolated input?
8. **CWE-416 Use After Free**, Python C-extensions / ctypes / Rust unsafe / C-FFI
9. **CWE-862 Missing Authorization**, endpoint without `require_auth` / role check
10. **CWE-434 Unrestricted File Upload**, file type / size / path-traversal in uploaded filename validated?
11. **CWE-94 Code Injection**, `eval` / `exec` / `pickle.load` / unsafe deserialization from untrusted source?
12. **CWE-20 Improper Input Validation**, Pydantic / Zod / jsonschema validated everywhere; no raw dicts past the boundary
13. **CWE-77 Command Injection**, broader than 78
14. **CWE-287 Improper Authentication**, token comparison constant-time? proper auth library?
15. **CWE-269 Improper Privilege Mgmt**, does the process run as least-privilege?
16. **CWE-502 Deserialization of Untrusted Data**, `pickle`, `marshal`, `yaml.load` (use `safe_load`), Java `Serializable`, Jackson polymorphic deserialization?
17. **CWE-200 Information Exposure**, error messages / logs leaking stack/PII/tokens
18. **CWE-863 Incorrect Authorization**, wrong role check / off-by-one in permission table
19. **CWE-918 SSRF**, server-side fetch to user-supplied URL? (Block link-local, file://, internal CIDRs.)
20. **CWE-119 Memory Buffer Errors**, C extensions / unsafe Rust / FFI
21. **CWE-476 NULL Pointer Dereference**, Python `None`-safety; Java NPE; Go nil-pointer; missing optional checks
22. **CWE-798 Hardcoded Creds**, grep for `password=`, `token=`, API keys
23. **CWE-190 Integer Overflow**, usually Python-safe; relevant with C-extensions, Java/Go/Rust int math, JSON-encoded big ints
24. **CWE-400 Resource Exhaustion**, unbounded recursion, missing pagination, zip bombs, billion-laughs XML, regex catastrophic backtracking
25. **CWE-306 Missing Auth for Critical Function**, internal-only endpoints exposed without auth

## B, AI-PR-specific bug shapes

These show up disproportionately in AI-generated code. Sources: GITCLEAR-2025 (copy-paste +N% over baseline; refactoring shrinking; churn-within-2-weeks growing), ACM-COPILOT-CORRECT (correctness defects per problem class), ACM-COPILOT-SEC (security weaknesses by CWE).

- **Hallucinated imports / packages**, every new dep verified (registry exists, author known, first-seen ≥30d, prior versions exist). Per SLOP-arXiv: 5.2% commercial / 21.7% OSS-model hallucination rates.
- **Made-up API methods**, `client.foo_bar()` that doesn't exist on the SDK; verify against current docs, not training-data-era memory.
- **Silent failure paths**, `try / except: pass` swallowing real errors; over-broad `except Exception` / `catch (Throwable)`. ACM-COPILOT-SEC notes elevated incidence.
- **Missing null/empty guards**, assumes input is non-None / non-empty.
- **Off-by-one in slicing**, `data[:n]` when `data[: n + 1]` was intended (or vice versa).
- **Plausible-completion trap** (`PIRANESI-UU3`), code that passes base tests but fails compositional extensions (26.2% HumanEval-Pro base-pass/extension-fail). Token-level training objective is blind to runtime semantics.
- **Reward-hacking** (`PIRANESI-UU2`), agent patches evaluator, overwrites timer, or hijacks equality operator to pass tests without correctness (30.4% of SWE tasks in METR study). Gate must be tamper-isolated.
- **Skill-instruction droppability** (`PIRANESI-UU1`), agent acknowledges but ignores guardrail instructions mid-session (117 documented violations/day). Prose-only guardrails insufficient; environment-space gates required.
- **Type-checker bypass** (`PIRANESI-CPW1` [T2-secondary]), 97% of LLM structural failures evade type checkers + tests + SAST together. Static types catch ~3% of LLM structural bugs. Gate must be multi-layer (structural/graph + type + execution + schema).
- **Circular self-validation** (`PIRANESI-UU4`), same model generating code and its own tests validates its own blind spots. Require independent/adversarial test provenance.
- **Schema failure at boundary** (`PIRANESI-UU5`), 10–20% structured-output schema failure when naive parsing assumed. Runtime schema validation mandatory at LLM prompt/parse boundaries.
- **Cross-file / config incoherence** (`PIRANESI-CPW2` [T2-secondary]), dependency manifest drift, interface changes without consumer updates, declare-after-use. Invisible to per-file type checking; requires graph-level verification.
- **Dead branches / unreachable code**, pasted in but no caller.
- **Copy-paste with wrong variable**, same shape as Phabricator / GitHub diff smell; GITCLEAR-2025 quantifies the rise.
- **Resource leaks**, `open()` without `with` (Python), browser/Playwright contexts not closed, DB connections not released, file handles in Java not in try-with-resources.
- **Race conditions in retry/backoff**, shared mutable state across threads/async tasks.
- **Eager DB access in `__init__`**, connecting to DB inside class init kills testability.
- **Tests that don't fail when broken**, assertion-light tests that exercise but don't verify.
- **Mocking what should be integration-tested**, DB / file I/O mocked away, leaving zero real coverage.
- **Subprocess without timeout**, `subprocess.run` / `exec.Command` / `Runtime.exec` without timeout can hang forever.
- **Unbounded LLM output parsing**, JSON parser without length cap; prompt-injection risk at the parser layer.
- **Prompt-baked secrets**, model name / API key in the prompt template.
- **Hard-coded paths**, `/tmp/foo` instead of language-native temp-dir abstraction.
- **Time-dependent tests**, `datetime.now()` / `Date.now()` used as input; flaky in CI.
- **Random non-deterministic tests**, no seed, no recording.
- **Vacuous CI green**, tests pass; code doesn't actually do what was asked. Mutation testing catches.

## C, LLM-bearing modules (cross-ref OWASP-LLM-Top-10)

If the surface uses an LLM:
- LLM01 prompt injection, RAG retrieval scanned? user input fenced?
- LLM02 sensitive info disclosure, per-tenant context isolation?
- LLM03 supply chain, model + prompt versions pinned?
- LLM04 data poisoning, RAG corpus provenance?
- LLM05 improper output handling, output schema-validated before action?
- LLM06 excessive agency, capability allowlist per tier?
- LLM07 system prompt leakage, secrets not in system prompt?
- LLM08 vector/embedding weaknesses, re-embed on model upgrade?
- LLM09 misinformation, citations grounded?
- LLM10 unbounded consumption, per-tenant rate + token budget?

Full content: `owasp_llm_top10.md`.

## D, API surface (cross-ref OWASP-API-Top-10)

If the surface is an HTTP API: walk `owasp_api_top10.md` (BOLA, broken auth, BOPLA, unrestricted resource, BFLA, sensitive flow abuse, SSRF, security misconfig, inventory mgmt, unsafe consumption).

## E, Web surface (cross-ref OWASP-Web-Top-10)

If browser-rendered: walk `owasp_web_top10.md` (broken access control, crypto failures, injection, insecure design, security misconfig, vulnerable components, auth failures, software/data integrity, logging, SSRF).

## Output

Per project, table:

| ID | CWE / shape / OWASP | File:line | Severity | Reproduction | Proposed fix | Confidence (0–100) |
|---|---|---|---|---|---|---|
| P0-01 | CWE-78 | adb_client.py:42 | P0 | `adb shell` with f-string | use `args=[...]` not shell | 95 |
| P0-02 | OWASP-LLM06 | agent.py:120 | P0 | tool-call without allowlist | wire harness allowlist | 90 |
| P1-04 | resource leak | auditor.py:88 | P1 | browser not closed on exception | context manager | 92 |

Severity:
- **P0**: ship-blocker. Bug is exploitable / data-loss / public correctness violation.
- **P1**: should-fix-before-launch.
- **P2**: nice-to-have / refactor.

## Lens selection

Don't walk every category on every change. Use `INDEX.md` decision tree to select applicable lenses by surface. Walking every CWE on a CSS change = noise; walking the relevant 5 = signal.
