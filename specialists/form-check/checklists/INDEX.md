---
name: checklists_index
version: 2.0.0
parent_skill: form-check
status: decision tree
---

# Checklists, INDEX (decision tree)

Use this as the routing layer. Pick the checklist(s) that match your task. Don't walk every checklist on every change, that wastes vibe budget and produces fatigue-shaped noise.

## Decision tree

```
What are you doing?

├─ Reviewing existing code?
│   ├─ → codebase_scan.md             (cross-cutting comprehension protocol, run FIRST for unfamiliar code)
│   ├─ → bug_class_audit.md           (CWE Top-25 + AI-PR shapes + LLM-specific bug classes)
│   ├─ → smell_catalog.md             (month-3 failure modes per archetype)
│   ├─ Touches LLM / agent?
│   │   ├─ → owasp_llm_top10.md
│   │   ├─ → references/llm_code_correctness_gate.md  (mechanical gate for LLM-generated code)
│   │   ├─ → templates/structural_semantic_trigger.md  (when to apply the gate)
│   │   └─ → tools/generation_gate.sh  (validate bash scripts at generation time)
│   ├─ Web app / public API?
│   │   ├─ → owasp_web_top10.md
│   │   └─ → owasp_api_top10.md
│   ├─ Touches accessibility surface?
│   │   └─ → accessibility_wcag22.md
│   └─ Adding a dep?
│       └─ → supply_chain_slsa.md     (slopsquatting, SLSA targets)
│
├─ Planning a new app?
│   ├─ → preflight_10q.md             (10 questions before code)
│   ├─ → fitness_functions.md         (architecture decisions enforced in CI)
│   ├─ Stores user data?
│   │   └─ → threat_model_linddun.md  (privacy threats)
│   └─ Auth / payments / multi-tenant?
│       └─ → threat_model_stride.md
│
├─ Touching auth / payments / deletes / secrets / migrations?
│   ├─ → ../templates/review_gate_checklist.md  (mandatory)
│   ├─ → threat_model_stride.md
│   └─ → bug_class_audit.md (P0 sections)
│
├─ Deprecating an API?
│   └─ → deprecation_policy.md        (RFC 8594 + sunset timeline)
│
├─ Hardening for security audit (SOC2 / ISO 27001 / FedRAMP)?
│   └─ activates ../scale-up/soc2_iso27001.md (requires forcing-constraint ADR)
│
└─ Reviewing the skill itself?
    └─ → skill_antipatterns.md
```

## Cross-reference: which OWASP list applies

| Surface | Use |
|---|---|
| LLM / agent / RAG | OWASP LLM Top 10 (2025) |
| HTTP API (REST / GraphQL / gRPC-Web) | OWASP API Top 10 (2023) |
| Browser-rendered web app | OWASP Top 10 (2025 web) |
| All applicable above | walk all three |

## Cross-reference: bug-class lens by surface

| Surface | Add to bug_class_audit walk |
|---|---|
| File I/O | CWE-22 (path traversal), CWE-434 (file upload), CWE-400 (resource exhaustion: zip bombs) |
| Subprocess | CWE-78 (OS command injection), CWE-77 (command injection broader) |
| Network in | CWE-918 (SSRF), CWE-352 (CSRF), CWE-444 (request smuggling) |
| Auth | CWE-287 (improper auth), CWE-862/863 (missing/incorrect authorization), CWE-269 (privilege mgmt) |
| Crypto | CWE-327 (weak algo), CWE-330 (weak random), CWE-321 (hard-coded key) |
| Deserialization | CWE-502 |
| LLM | OWASP-LLM01–10 (parallel taxonomy) |
| Concurrency | CWE-362 (race), CWE-665 (improper init) |

## How to invoke during a review

1. Read `bug_class_audit.md` and select applicable lenses by surface.
2. Walk the OWASP list(s) per the table above.
3. Walk `smell_catalog.md` for the project archetype (CLI / library / web / LLM-bearing).
4. For vibe-dangerous changes, add `threat_model_stride.md` (security) and `threat_model_linddun.md` (privacy if data flows).
5. Compute confidence score (`../rubrics/confidence_score.md`) per change.
6. Walk `skill_antipatterns.md` once per engagement to ensure you're not gaming the rubric.
