---
name: vibe_safety_map
version: 2.0.0
parent_skill: form-check
---

# Vibe-Safety Map (v2 — adds vibe-impossible bucket)

For every plan or review, classify each module/surface into one of **four** buckets. The bucket determines the confidence-score tier and the per-component minima.

## Bucket 1 — Vibe-safe (AI ships unread, score ≥80)

Criteria (all must hold):
- Pure functions / deterministic transforms / read-only views
- No side effects beyond the local process
- Tests exist and pass after the change
- No new dependencies introduced
- No secrets touched
- Reversible by `git revert`
- No public API surface change

Examples:
- New CLI flag that toggles formatting (`--json` vs `--table`)
- Adding a unit test fixture
- Renaming an internal helper
- Adding a Pydantic / Zod field with default

## Bucket 2 — Vibe-careful (human reads diff, score ≥90)

Criteria (any one):
- Touches a public API surface or CLI shape
- Adds a new dependency (always slopsquatting-check + author + first-seen ≥30d)
- Changes test fixtures used by eval baseline
- Modifies retry / timeout / concurrency knobs
- Touches DB schema in a backward-compatible way (additive column with default)
- Changes an LLM prompt or model selection
- Modifies fitness-function thresholds

Process:
- Human reads the full diff
- New deps verified against registry + checked with vuln scanner (`pip-audit` / `npm audit` / `govulncheck` / `cargo-audit`)
- Eval baseline re-run; regression gate must hold
- API change → `Deprecation` and `Sunset` headers (RFC 8594) added if removing surface

## Bucket 3 — Vibe-dangerous (human writes test + reads diff + staged rollout, score ≥95)

Criteria (any one):
- Auth, sessions, tokens, cryptography
- Payments, billing, money
- DB migrations that drop or rename columns/tables, or backfill
- Production writes at scale (mass update / mass delete)
- External API calls with side effects (sending email, SMS, billing, public publication)
- Code paths that read or write secrets
- File deletion paths (especially recursive)
- Anything touching customer data deletion or export (GDPR/CCPA)
- LLM agent tool grants (especially shell / DB / network-write tools)

Process:
1. **Human writes the failing test** that encodes the spec.
2. AI implements; types check; lint clean; test passes; mutation score ≥ tier-target.
3. **Human reads the full diff** — no skim.
4. STRIDE walked on the changed surface (`checklists/threat_model_stride.md`).
5. Ship behind a feature flag. **Staged rollout** (web): 1% → 10% → 50% → 100%; (CLI/library): semver patch with explicit changelog entry; (mobile): staged release ring.
6. Monitor for one full deploy cycle before flag-cleanup.
7. ADR written and merged (`templates/MADR_short.md`).
8. Score logged with incident-tracking link.

## Bucket 4 — Vibe-impossible (AI must not ship, even with all gates)

These require a qualified human author, not just a reviewer:

- **Accessibility decisions affecting marginalized groups**: ARIA-pattern choices, focus-management decisions, screen-reader copy. Require audit by an accessibility consultant or the user with disability-aware tooling (`checklists/accessibility_wcag22.md`).
- **Localization beyond pre-translated copy**: machine translation may not preserve legal/medical/financial nuance. Require qualified translator.
- **Legal / medical / financial-advice copy**: disclaimers, terms, regulated language. Require qualified review.
- **Cryptographic primitives implementation**: never invent. Use audited libraries (libsodium, ring, BoringSSL); never roll your own AES, HMAC, RNG.
- **Compliance attestation language**: SOC2, ISO 27001, HIPAA, FedRAMP, PCI-DSS, GDPR Art 30 records. Auditor-reviewed.
- **Incident-response decisions during a live security incident**: runbooks pre-written; live decisions human-led.

If an AI agent attempts to produce vibe-impossible content, the harness must refuse and prompt the user.

## Per-archetype map (initial pass — replace with project-specific)

| Project archetype | Vibe-safe | Vibe-careful | Vibe-dangerous | Vibe-impossible |
|---|---|---|---|---|
| **Internal CLI** | output formatting, internal helpers | new flags, dep adds, retry/timeout knobs | shell-out with side effects, file-delete paths | crypto primitives |
| **Read-only library** | examples, type docstrings, internal refactors | public API additions, dep adds | breaking API removals, security-critical helpers | compliance copy |
| **Web service** | UI templates, copy text | API request shapes, scheduler cadence | auth, deletion paths, PII logging, prompt changes | accessibility-affecting-marginalized-users decisions |
| **Hardener tool** (applies config) | report rendering, dry-run output | rule mapping, parser changes | anything that *applies* config; subprocess with side effects | compliance attestation |
| **LLM-bearing app** | UI, copy | prompt template, model selection (within family), eval fixtures | model-family swap, agent tool grants, RAG retrieval scope | medical/legal/financial output unreviewed |

## Refusal triggers

When AI is about to ship something that should be vibe-dangerous **without** the gates above, refuse and ask:
> "I'm about to {action}. This is a vibe-dangerous surface. Confirm you have written the failing test, walked STRIDE on the changed surface, and read the diff?"

When AI is about to ship something vibe-impossible:
> "This change touches {bucket-4 category}. AI cannot author this. Please assign to a qualified human author and provide the deliverable for me to review."
