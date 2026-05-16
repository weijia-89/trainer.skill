---
name: event_sourcing_cqrs
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required
---

# Event Sourcing + CQRS

> **[GATED — informational only]** Forcing-constraint ADR required.
>
> Event sourcing is right for a narrow range of problems. The wider use of CQRS is *some* read-write separation; full event-sourcing-as-source-of-truth is a different beast.

## When this chapter applies

- **Audit-log-as-spec**: regulator requires reconstructable history of every state change (financial trades, healthcare records, voting systems)
- **Temporal queries are core**: "what did state X look like on date Y" is a primary query, not a one-off
- **Multi-system consistency** via event-driven outbox pattern (with a forcing constraint)

**Not when**:
- "We want better debugging" — event sourcing is *not* a debugger upgrade
- "We want to be event-driven" — you can have async messaging without event sourcing
- "Microservices need events" — they need contracts; events are one option, RPC is another

## CQRS without event sourcing (lighter alternative)

CQRS = Command Query Responsibility Segregation. Separate the model that handles writes from the model that handles reads. Useful when:

- Read/write scaling profiles differ wildly
- Read model is denormalized for query performance
- Write side enforces complex invariants

CQRS does **not** require event sourcing. Most "CQRS" projects are write-side-with-invariants + read-replica or denormalized-projection.

## Event sourcing as source of truth

State is a *projection* of an event log; events are the only source of truth. Implications:

- Append-only event store (Kafka, EventStoreDB, Postgres+outbox, Marten, MongoDB-with-conventions)
- Projections (read models) rebuilt by replaying events
- Event versioning is a discipline (Greg Young's "versioning in an event-sourced system")
- Snapshots for performance on long event histories
- Event upcasting / downcasting for schema evolution

## Cost dimensions

- Storage growth: events are immutable; you keep them all (compaction is project-specific)
- Replay cost: rebuilding projections takes time proportional to event volume
- Cognitive load: developers think in events, not state — meaningful learning curve
- Tooling: many off-the-shelf admin tools assume state-shaped data; event-shaped systems often build their own
- Schema evolution: every event version must be replayable; renames / removals cost more than in state-shaped systems

## Patterns

- **Outbox pattern**: write to the event store + business state in a single local transaction; ship to subscribers async.
- **Saga**: orchestration vs choreography for cross-service flows.
- **Snapshot strategy**: take snapshots every N events; replay only post-snapshot.
- **Event versioning**: include `event_version` in every event payload; explicit upcasters.

## Anti-patterns

- Event sourcing because microservices ⇒ events. Microservices need *contracts*; events are one option.
- "Replay all events to fix a bug" without snapshots — multi-hour outage.
- Treating events as RPC ("user-created-event" with all the data the consumer needs) — this is RPC with extra steps.
- Updating events after they're emitted (mutating history) — defeats the purpose.
- Per-event-type-per-schema rigidity that prevents evolution — design the schema-evolution strategy upfront.

## Sunset

If the forcing constraint goes away (audit requirement deprecated; temporal queries no longer core), migrate read models out of event-sourced topology. Costly but possible: project current state, switch to CRUD, archive event log per retention requirement.

## Cross-references

- `distributed_systems.md` (saga + outbox patterns)
- `soc2_iso27001.md` (audit-log-as-source regulatory cases)
- `multi_region.md` (event-store replication patterns)
