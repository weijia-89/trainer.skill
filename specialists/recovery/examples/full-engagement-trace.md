---
name: full_engagement_trace_example
version: 2.0.0
parent_skill: recovery
status: example (non-normative)
---

# Example — Full recovery Engagement Trace

A worked example of a `recovery --engagement-type=harden` run on a synthetic project. Captures phase-by-phase artifacts so reviewers and contributors know what "good output" looks like.

## Setup

- **Project**: `northwind-qa` (Playwright test harness; ~3000 LOC; existing in workspace)
- **Engagement type**: `harden`
- **Tier**: vibe-careful (default; no auth/payments/secrets in scope)
- **Host harness**: agent harness with file-read, grep, shell, web-search, and edit tools

## Phase: discovery

`.recovery/discovery.md` (excerpt):

```markdown
# Discovery — northwind-qa @ 2026-05-14T19:24:00Z

## Tree

- bugs/ (5 markdown bug reports)
- docs/ (4 markdown reference docs)
- lib/ (2 helper files: helpers.js, locators.ts)
- tests/ (8 test files: a11y, auth, auth.setup, ...)
- package.json, playwright.config.ts, tsconfig.json

## Stack

- Language: TypeScript ~5.4
- Test runner: Playwright
- Linter: not detected (gap)
- CHANGELOG.md: present
- README.md: present, conversational tone, archetype unclear (CLI-shaped header but service-shaped content)

## Forcing-constraint ADRs

None found. Default mode applies.

## Prompt-injection scan

0 hits across project markdown.
```

## Phase: review

`.recovery/review.md` (excerpt — 5 of ~20 findings):

```markdown
| ID | Lens | File:line | Severity | Reproduction | Proposed fix |
|---|---|---|---|---|---|
| P0-01 | OWASP-API-2023 API4 | tests/auth.spec.ts:42 | P0 | unbounded retry on 503; can DoS auth endpoint | bound retries + jittered backoff |
| P1-02 | CWE-352 | tests/auth.setup.ts:18 | P1 | login flow doesn't include CSRF token | add token to setup payload |
| P1-03 | AI-PR shape | lib/helpers.js:104 | P1 | bare catch swallows errors silently | scope to expected exceptions; rethrow others |
| P2-04 | smell #11 | docs/COVERAGE.md:- | P2 | doc states "100% coverage" without source | replace with measured number or omit |
| P2-05 | doc voice | README.md:1 | P2 | mixed README archetype (CLI/service) | choose archetype per templates/README_archetypes/ |
```

## Phase: scoring

`.recovery/scoring.md` excerpt:

```markdown
| Change | Tier | Score | Components (read/test/halluc/bug/adv/rev/doc/blast/threat) | Verdict |
|---|---|---|---|---|---|
| add jittered backoff | vibe-careful | 91 | 95/85/100/90/80/95/95/85/85 | ship |
| CSRF token in setup | vibe-careful | 89 | 90/80/100/95/75/95/90/80/85 | iterate (Adversarial < 80) |
| narrow exception | vibe-safe | 86 | 95/80/100/85/85/90/80/85/70 | ship |

Engagement aggregate: 91.5 (vibe-careful). Threshold met. No adversarial loop required.
```

## Phase: doc-pass

`.recovery/doc_pass.md` excerpt:

```markdown
- README.md → rewritten as `service` archetype
- CHANGELOG.md → existing format kept; added `[Unreleased]` block
- SECURITY.md → created from template
- ARCHITECTURE.md → created from template (≤2 pages)
- ROADMAP.md → not created (project at end-of-life; documented in summary)
- docs/glossary.md → created with 8 terms
- docs/threat-model.md → created with STRIDE + LINDDUN walks
- docs/runbooks/incident_response.md → created from template
- docs/adr/0001-baseline.md → created
```

## Phase: deAI-sweep

`.recovery/deai_sweep.md` excerpt:

```markdown
| File | Hits before | Hits after | Notes |
|---|---|---|---|
| README.md | 4 | 0 | "robust", "scalable", "leverage", "seamless" replaced with concrete properties |
| docs/COVERAGE.md | 1 | 0 | "world-class" removed |
| ARCHITECTURE.md | 0 | 0 | clean baseline |
| CHANGELOG.md | 0 | 0 | clean (impersonal-factual archetype baseline applies) |
```

## Phase: adversarial

(Not invoked — engagement aggregate cleared the threshold without it.)

## Phase: launch-ready

`.recovery/launch_ready.md` excerpt:

```markdown
| Section | Status |
|---|---|
| Documentation baseline | pass |
| Code quality | partial (mutation testing not configured — fail; tracked) |
| Supply chain | pass (SBOM gap acknowledged for tooling-only project) |
| Security baseline | pass |
| Operational readiness | n/a (test harness, not a service) |
| Architectural fitness functions | pass (3 lint rules wired) |
| Vibe-safety inventory | pass |
| Agent-runtime contract | n/a |
| LLM-bearing | n/a |
| Accessibility | n/a (no UI) |
| Compliance hooks | n/a |

Verdict: launch-ready *with* one acknowledged gap (mutation-testing wiring). Filed as ROADMAP "Next."
```

## Phase: summary

`.recovery/summary.md` (full):

```markdown
# Codeit Summary — northwind-qa @ 2026-05-14T20:14Z

- Engagement type: harden
- Duration: 50 minutes
- Engagement-aggregate: 91.5 (vibe-careful, threshold 90 met)

## Top 3 findings

1. P0-01 — unbounded auth retries (lib/helpers.js); fix shipped at 91 confidence.
2. P1-02 — CSRF token absent in auth setup; fix iterated to 92 after adversarial pass on threat-model.
3. P2-05 — README archetype mismatch; rewritten as `service`.

## Top 3 deferred

1. Mutation-testing wiring (Stryker) — Roadmap "Next."
2. Per-test-file ARIA pattern review (n/a — tests target an app we don't own).
3. SBOM generation (gap acknowledged for tooling project; tracked).

## Doc deltas

- README.md, SECURITY.md (new), ARCHITECTURE.md (new), docs/glossary.md (new), docs/threat-model.md (new), docs/runbooks/incident_response.md (new), docs/adr/0001-baseline.md (new), CHANGELOG.md.

## Calibration

3 rows added to `.recovery/calibration.jsonl` (one per scored change). Engagement-level row also added with `engagement_level: true`.

## Recommended next engagement

`review` after Stryker wired in; mutation scores will let test-verification component reach full credit.
```

## Final state.jsonl

```jsonl
{"phase": "discovery", "ts": "...", "verdict": "pass", "score": null, "tier": "vibe-careful", "artifacts": [".recovery/discovery.md"], "duration_seconds": 180, "notes": ""}
{"phase": "review", "ts": "...", "verdict": "pass", "score": null, "tier": "vibe-careful", "artifacts": [".recovery/review.md"], "duration_seconds": 720, "notes": "20 findings: 1 P0, 6 P1, 13 P2"}
{"phase": "scoring", "ts": "...", "verdict": "pass", "score": 91.5, "tier": "vibe-careful", "artifacts": [".recovery/scoring.md"], "duration_seconds": 540, "notes": "3 changes scored"}
{"phase": "doc_pass", "ts": "...", "verdict": "pass", "score": null, "tier": "vibe-careful", "artifacts": [".recovery/doc_pass.md"], "duration_seconds": 600, "notes": "8 docs created/updated"}
{"phase": "deai_sweep", "ts": "...", "verdict": "pass", "score": null, "tier": "vibe-careful", "artifacts": [".recovery/deai_sweep.md"], "duration_seconds": 180, "notes": "5 hits fixed"}
{"phase": "launch_ready", "ts": "...", "verdict": "advisory", "score": null, "tier": "vibe-careful", "artifacts": [".recovery/launch_ready.md"], "duration_seconds": 360, "notes": "1 acknowledged gap (mutation testing)"}
{"phase": "summary", "ts": "...", "verdict": "pass", "score": 91.5, "tier": "vibe-careful", "artifacts": [".recovery/summary.md"], "duration_seconds": 120, "notes": "engagement complete"}
```

## What this trace illustrates

- DAG activation: review → scoring → doc-pass → deAI → launch-ready → summary; adversarial skipped because aggregate cleared threshold.
- Per-phase verdicts are `pass | fail | advisory` — `advisory` for launch-ready when there's a documented gap that doesn't block the engagement.
- Calibration log accumulates per-change rows for future retiering.
- Voice rules applied per-archetype: README's `service` archetype voice differs from CHANGELOG's impersonal-factual voice.
- No scale-up content consulted (no forcing-constraint ADR; default mode).
