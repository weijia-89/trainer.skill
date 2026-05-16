---
name: distributed_systems
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required
---

# Distributed Systems

> **[GATED — informational only]**
> Read only with an accepted forcing-constraint ADR (`docs/adr/`) of type `forcing-constraint`. Without it, default-mode says: *modular monolith on one PaaS in one region with one DB*.
>
> Verify the gate via `tools/check_forcing_constraint.sh` before consuming this content.

## When this chapter applies

- **Forcing constraints**: ≥2 services with a shared business invariant + measured latency budget that monolith can't meet, OR organizational mandate for service decomposition.
- **Not when**: "we'll need to scale eventually," "microservices are best practice," "the team prefers it."

## Decomposition strategy

1. **Start by hiding decisions, not flow steps** (Parnas). Each service should own a *decision likely to change*, not a step in a request lifecycle.
2. **Map services to bounded contexts** (DDD), not to UI screens or DB tables.
3. **Conway's law applies**: services mirror team structure. Map team boundaries before service boundaries.
4. **Strangler fig over big-bang**: extract one service at a time from a monolith.

## Contracts

- **Schema-first**: OpenAPI / gRPC / GraphQL SDL. Generate code, not the other way.
- **Versioning**: per-service SemVer; deprecation with `Sunset` headers (RFC 8594).
- **Contract testing**: Pact / consumer-driven; fail CI on contract break.

## Resilience patterns

- **Idempotency keys**: every write endpoint accepts an `Idempotency-Key` header (Stripe canon; see `STRIPE-IDEMP`, `BRANDUR-IDEMP`).
- **Timeouts everywhere**: never call a peer without a timeout.
- **Circuit breakers**: trip on N% failure over T seconds.
- **Retry with jittered exponential backoff**: bounded; idempotent ops only.
- **Bulkheading**: separate connection pools per dependency.
- **Saga pattern** for cross-service workflows: compensating transactions over distributed locks.

## Observability

- **Distributed tracing** (OpenTelemetry) — every service emits spans; trace IDs propagated.
- **Structured logs** with trace correlation.
- **RED metrics** per endpoint (Rate, Errors, Duration); USE metrics per resource (Utilization, Saturation, Errors).

## Anti-patterns

- **Distributed monolith**: services so coupled that a change requires coordinated deploys → loses every benefit of distribution. Re-collapse.
- **Database-per-service ignored**: services sharing a database = distributed monolith with extra steps.
- **Synchronous chains** beyond depth 2 — latency multiplies; reliability multiplies (multiplicatively).
- **Eventual consistency where atomic was needed** — pick patterns deliberately.
- **Service mesh as the first answer** — see `service_mesh.md` (also gated).

## Sunset condition

Re-collapse to monolith if:
- Forcing constraint deprecated
- Operational tax exceeds business value (measured per FinOps gate)
- Conway-mapping stabilized; service boundaries no longer match team structure → re-decompose

## Cross-references

- Idempotency: `form-check.skill/templates/prompt_versioning.md` (analogous pattern for prompts) and `STRIPE-IDEMP` references
- Multi-region: `multi_region.md` (gated)
- Service mesh: `service_mesh.md` (gated)
- Event-driven: `event_sourcing_cqrs.md` (gated)
