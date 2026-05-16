---
name: forcing_constraint_adr_example
version: 2.0.0
parent_skill: form-check
status: example (non-normative)
---

# Example — Forcing-Constraint ADR (worked example)

This is what a *good* forcing-constraint ADR looks like. Use as a reference; the empty template is at `templates/forcing_constraint_adr.md`.

```markdown
# 0042 — Forcing Constraint: HIPAA-Compliant Multi-Region for ACME-Health Contract

- Status: accepted
- Type: forcing-constraint
- constraint_class: regulatory
- Date: 2026-04-12
- Deciders: Jane Doe (CTO), Sam Smith (Legal), Maya Lee (Security)
- Activates scale-up chapters: scale-up/multi_region.md, scale-up/soc2_iso27001.md
- Sunset trigger: ACME-Health contract terminated OR HIPAA covered-entity status revoked

## 1. The constraint

ACME-Health master services agreement signed 2026-03-30 includes Schedule C ("Technical Safeguards") clause 4.2 mandating: (a) PHI processed under our infrastructure must remain in two geographically-separated US regions with synchronous replication; (b) RTO ≤ 15 minutes; (c) RPO ≤ 1 minute; (d) HIPAA Business Associate Agreement attestation by 2026-09-30.

The relevant HIPAA Security Rule sections (45 CFR § 164.308–312) apply, and ACME-Health is a HIPAA covered entity passing PHI to us as a Business Associate. The two-region requirement is contractual; the BA agreement is regulatory.

Reference: `docs/contracts/acme-health-msa-2026-03-30.pdf` Schedule C, sections 4.2.a–d.

## 2. Default-mode alternative considered

Default mode: single-region modular monolith on Fly.io, `iad` region.

Why it fails: cannot meet the cross-region replication clause; cannot meet the 15-minute RTO under regional outage scenarios; cannot pass the BA attestation as currently architected (clause 4.2.d).

Cost of default mode: contract loss (~$2.4M ARR + $400K services); legal exposure on attempted partial compliance.

## 3. Chosen scale-up path

- **Topology**: active-passive across `us-east-1` (`iad`) and `us-west-2` (`sea`). PHI replicated synchronously via Postgres logical replication + WAL streaming.
- **Activated chapters**: `scale-up/multi_region.md` (topology), `scale-up/soc2_iso27001.md` (HIPAA control mapping; SOC2 Type 2 also pursued for audit-readiness).
- **Migration**: 90-day phased plan (`docs/migrations/0001-multi-region-phase-plan.md`).

## 4. Cost projection

| Dimension | Default | Scale-up | Multiplier |
|---|---|---|---|
| Compute (PaaS) | $4,200/mo | $7,800/mo | 1.86× |
| Network egress (cross-region replication) | $300/mo | $1,800/mo | 6× |
| Storage (replicated DB) | $800/mo | $1,600/mo | 2× |
| Observability (per-region tracing) | $1,200/mo | $2,800/mo | 2.33× |
| Security tooling (HIPAA-grade SIEM) | $0 | $4,500/mo | (new) |
| Operational headcount | 0.5 FTE | 1.0 FTE | 2× |
| **Total TCO** | $14,500/mo | $36,500/mo | 2.52× |

Annualized incremental cost: ~$264K. Contract value: $2.4M ARR. Payback: ~6 weeks.

## 5. Consequences

- ✅ Meets contract clause 4.2.a–d
- ✅ HIPAA BA attestation achievable by 2026-08-15 (target ahead of contract deadline)
- ✅ SOC2 Type 2 path opened (audit window: 2026-09 to 2027-03)
- ⚠ Operational tax: 0.5 FTE platform-team allocation; quarterly failover game-days
- ⚠ Recruiting: HIPAA-experienced security engineer (90-day search)
- ⚠ Cross-region-egress costs are sensitive to traffic patterns; quarterly cost-review cadence

## 6. Confirmation (90-day check)

- 2026-07-15: failover game-day passes (RTO ≤ 15 min in test, RPO ≤ 1 min)
- 2026-07-30: HIPAA risk assessment complete; gaps closed
- 2026-08-15: BA attestation submitted to ACME-Health legal
- 2026-09-15: monthly cost-review shows TCO multiplier within ±15% of projection

## 7. Sunset condition

Re-evaluate annually. Retreat to default-mode if:
- ACME-Health contract terminated or amended to remove clause 4.2
- HIPAA covered-entity status revoked
- We exit the healthcare segment entirely

If sunset condition met: file ADR-0099 closing this one; budget 2-quarter retreat plan; archive PHI per HIPAA retention policy before tearing down.

## 8. Approvals

- Jane Doe (CTO): 2026-04-10
- Sam Smith (Legal): 2026-04-11
- Maya Lee (Security): 2026-04-12
- Finance: 2026-04-12 (Q3 budget signed)
```

## What makes this a good example

- **Specific named constraint** (contract clause + regulator) — not vibes.
- **Default-mode alternative honestly considered** — not a strawman.
- **Cost projection with multiplier** — finance-checkable.
- **Confirmation criteria are dated and measurable** — not aspirational.
- **Sunset condition is real** (contract / regulator) — not "if we feel like it."
- **Approvers named** — accountability is on the record.

## Counterexamples (anti-patterns)

- "We're growing fast and will need this." — not a forcing constraint.
- "All the SaaS unicorns are multi-region." — not a forcing constraint.
- Status: proposed but invoked anyway — gate violation.
- No cost projection — finance can't review; future surprise.
- "Sunset: never" — implies the constraint is permanent; rare; suspicious.
