---
name: when_to_activate
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required
---

# Scale-Up Annex, Activation Gate

> **[GATED, informational only]**
> The scale-up annex chapters describe patterns (microservices, multi-region, service mesh, event sourcing, CQRS, JVM/Spring) that are **anti-patterns by default** in this skill. They activate **only** behind a forcing-constraint ADR.
>
> If you're reading this exploratorily, do not implement the patterns described. The chapters exist so that *when* a forcing constraint genuinely applies, the patterns are documented and not invented under pressure.

## Why a gate

Every scale-up pattern in this annex is right at scale and wrong out of scale. Default-mode `form-check` refuses them in `SKILL.md` Section 4. The annex is the answer to "how do we *do* it when we genuinely need to", not "this is what we should do because we read about it."

Newman: "Microservices should be a last resort." Parnas: "Modules hide design decisions likely to change." Most "scale" justifications collapse on examination.

## Activation criteria

A scale-up chapter activates only when **a forcing-constraint ADR exists** in `docs/adr/` with:

```yaml
status: accepted
type: forcing-constraint
constraint_class: regulatory | scale-measured | org-mandate
```

### Constraint classes

| Class | Examples (any one trigger) |
|---|---|
| **Regulatory** | FedRAMP control mapping required; SOC2 Type 2 audit scheduled; HIPAA covered entity; GDPR Art 35 DPIA mandates segmentation; financial regulator multi-region requirement |
| **Scale-measured** | >50 services in production; >100 contributors; >10k RPS sustained for >30d; >5 regions live; >1 PB managed; observed Conway-mismatch with current architecture |
| **Org-mandate** | Existing org-wide platform team with mandated patterns; M&A integration with non-negotiable inherited stack |

The ADR must:
1. **Name the specific constraint** (cite regulator clause, measure with timestamp, mandate document).
2. **Document the alternative considered**: why default-mode patterns fail this specific constraint.
3. **Document the cost**: time, money, operational tax, observability cost, training cost.
4. **Document a sunset condition**: under what future state could we re-collapse to default?

Use `templates/forcing_constraint_adr.md` as the starting template.

## Gate check (technical)

`tools/check_forcing_constraint.sh <repo>` exits:
- `0` if a valid ADR exists (status: accepted; type: forcing-constraint; well-formed)
- `1` if no ADR or status≠accepted or type≠forcing-constraint
- `2` if ADR exists but is malformed

The skill's reading of any `scale-up/*.md` chapter is conditional on exit-0.

Algorithm spec (for hosts that can't run shell): `docs/forcing_constraint_check_algorithm.md`.

## Advisory mode

When a user asks "what would scale-up look like?" without an ADR, the skill operates in **advisory mode**:

- Show the **TOC of available chapters** (titles + 1-line descriptions).
- Show the **gate criteria** (this file, Section "Activation criteria").
- Show the **cost dimensions** (Section "FinOps gate" below).
- Do **not** quote chapter content.

The watermark `[GATED, informational only]` opens every chapter.

## FinOps gate

Scale-up almost always increases cost. The forcing-constraint ADR must include a cost projection:

| Dimension | Default-mode baseline | Scale-up cost multiplier (typical) |
|---|---|---|
| Compute | 1× | 1.5–3× (multi-AZ + redundancy) |
| Network | 1× | 1.2–2× (cross-AZ / cross-region traffic) |
| Storage | 1× | 1.5–2× (replicas + backups) |
| Observability | 1× | 2–5× (per-service metrics, traces, logs) |
| Security tooling | 1× | 1.5–3× (mesh, secrets, scanning) |
| Operational headcount | 1× | 1.5–2× (platform team, on-call rotation) |
| Total TCO | 1× | 2–4× |

If the ADR doesn't carry the cost projection, refuse activation.

## Anti-cargo-cult triggers

Refuse activation even with a partial ADR if any apply:

- "We'll need it eventually" without measured threshold.
- "All the big companies do it" without mapping to *our* constraint.
- "It will scale better" without a baseline measurement.
- "We can't grow without it" without identifying which growth path is blocked.
- "It's the modern way", recency bias, not constraint.

## Sunset clause

Scale-up activations are reviewed annually. If the forcing constraint no longer applies (regulator deprecated, scale dropped, org-mandate lifted), retreat to default-mode patterns. Refactoring back is hard but necessary; the alternative is permanent operational tax for a constraint that no longer applies.

## Available chapters (TOC; advisory-mode-safe)

- `distributed_systems.md`, service decomposition, contract testing, idempotency-key design, saga pattern (only if ≥2 services with shared business invariant)
- `multi_region.md`, active-active vs active-passive, conflict resolution, RPO/RTO, regional failover
- `soc2_iso27001.md`, control mapping, evidence collection, audit-prep checklist, ISO 27001 / SOC2 Type 2 alignment
- `service_mesh.md`, mTLS, traffic policy, observability hooks, mesh selection (Istio / Linkerd / Cilium)
- `event_sourcing_cqrs.md`, when event sourcing is genuinely the right answer (audit-log regulatory + temporal queries) vs cargo cult
- `spring_kotlin_jvm.md`, JVM tooling depth (Gradle / Spring Boot 3 / Kotlin coroutines) for enterprise greenfield with JVM forcing constraint

Each chapter is itself watermarked `[GATED]` and refuses to render content without the gate-check pass.
