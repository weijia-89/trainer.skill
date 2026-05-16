---
name: launch_ready
version: 2.0.0
parent_skill: recovery
---

# Launch-Ready Definition of Done

Walk for `engagement_type == "harden"`. Each item: pass | fail | n/a-with-reason. **Block engagement-summary "ready"** verdict on any unresolved fail.

## Section 1 — Documentation baseline (all archetypes)

- [ ] CLAUDE.md or AGENTS.md present, current, lists stack with exact versions
- [ ] README.md present, archetype-appropriate, no banned vocab in user-facing text
- [ ] CHANGELOG.md present, Keep-a-Changelog format, has at least one release entry
- [ ] SECURITY.md present, threat model linked, disclosure email valid
- [ ] LICENSE present, SPDX-identifiable
- [ ] ≥1 ADR in `docs/adr/` (baseline at minimum)

## Section 2 — Code quality

- [ ] All tests pass (unit + integration; eval if LLM-bearing)
- [ ] Mutation score ≥ tier target on changed code (per `form-check.skill/multi-language/matrix.md`)
- [ ] Lint passes with zero suppressed errors (or each suppression has a comment + ADR if persistent)
- [ ] Type checker passes (where applicable: mypy strict / tsc strict / -Werror in compiled)
- [ ] Test-as-spec coverage of acceptance criteria (≥1 failing-then-passing test per acceptance row)

## Section 3 — Supply chain

- [ ] Lockfile present and pinned with hashes
- [ ] Dep audit passes (`pip-audit` / `npm audit` / `govulncheck` / `cargo-audit` / OWASP DC) with zero high/critical OR documented exceptions
- [ ] SBOM generated (CycloneDX or SPDX)
- [ ] SLSA Build Track L2 minimum (default mode)
- [ ] Slopsquatting check trail in PR descriptions for new deps

## Section 4 — Security baseline

- [ ] Threat model walked (STRIDE for security; LINDDUN for privacy if data flows)
- [ ] Applicable OWASP Top 10 (LLM / API / Web) walked
- [ ] Secrets policy documented (no hardcoded secrets; secrets-manager named)
- [ ] Auth pattern documented (OIDC / API key / mTLS; per-tier authorization model)
- [ ] Logging redacts PII; audit log append-only
- [ ] Rate limits documented per public endpoint

## Section 5 — Operational readiness (services only)

- [ ] Health check endpoint (`/healthz`) and readiness (`/readyz`) implemented
- [ ] Metrics emitted (Prometheus/Datadog/CloudMonitoring) with named SLOs
- [ ] Tracing exporter wired (OpenTelemetry)
- [ ] On-call runbook present (`docs/runbooks/`)
- [ ] Incident-response runbook present
- [ ] Rollback procedure documented and tested in staging
- [ ] Status page / incident channel template ready
- [ ] Deploy CI/CD: trunk-based with feature flags

## Section 6 — Architectural fitness functions

- [ ] At least 3 lint-class fitness functions wired in CI
- [ ] Each ADR has a corresponding enforcing function OR documented gap
- [ ] CHANGELOG entry required per non-trivial PR (CI check)

## Section 7 — Vibe-safety inventory

- [ ] Vibe-safe / vibe-careful / vibe-dangerous / vibe-impossible map declared in CLAUDE.md
- [ ] Review gates wired for vibe-dangerous surfaces
- [ ] Calibration log (`.recovery/calibration.jsonl`) accumulating rows per scored change

## Section 8 — Agent-runtime contract (if AI agents consume the project)

- [ ] Capability allowlist enforced by host harness per tier
- [ ] State ledger at `.agent/ledger.jsonl`
- [ ] Prompt-injection scanner runs on agent-load (per `form-check.skill/agent-runtime/prompt_injection.md`)
- [ ] Untrusted-content fences applied in agent prompts
- [ ] Worktree confinement for vibe-careful and vibe-dangerous engagements

## Section 9 — LLM-bearing only

- [ ] Provider + model pinned (no "latest")
- [ ] Prompt versioning live (`form-check.skill/templates/prompt_versioning.md`)
- [ ] Eval baseline exists; ≥50 cases minimum (200+ for prod)
- [ ] Eval gate fails on >2pp regression
- [ ] OWASP-LLM Top 10 walked
- [ ] Cost guard: per-tenant rate + token budget

## Section 10 — Accessibility (if UI)

- [ ] WCAG 2.2 walked for changed surfaces
- [ ] Keyboard-only walkthrough done
- [ ] Screen-reader walkthrough done with at least one of NVDA / JAWS / VoiceOver / TalkBack
- [ ] Color contrast verified at AA minimum
- [ ] Reduced-motion alternative for animations
- [ ] Vibe-impossible accessibility decisions routed to qualified reviewer

## Section 11 — Compliance hooks (if applicable)

- [ ] Data-classification taxonomy documented
- [ ] Retention policy + automated deletion
- [ ] DPIA filed for high-risk processing (GDPR Art 35)
- [ ] Cross-border transfer mechanism documented (SCCs / BCRs / adequacy)
- [ ] Subject-access tooling (DSAR) tested

## Aggregate output

```markdown
# Launch-Ready Verdict — {{project}} {{ts}}

| Section | Status |
|---|---|
| Documentation baseline | pass / fail (gap: ...) |
| Code quality | ... |
| Supply chain | ... |
| Security baseline | ... |
| Operational readiness | ... |
| Architectural fitness functions | ... |
| Vibe-safety inventory | ... |
| Agent-runtime contract | ... / n/a |
| LLM-bearing | ... / n/a |
| Accessibility | ... / n/a |
| Compliance hooks | ... / n/a |

Engagement-aggregate score: NN.N (tier vibe-XX, threshold YY)
Verdict: launch-ready | not-yet-ready (gap report below)

## Gap report (if not-yet-ready)

| # | Section | Item | Owner | Due |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |
```
