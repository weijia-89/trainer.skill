---
name: multi_region
version: 2.0.0
parent_skill: form-check
gate: forcing-constraint-required
---

# Multi-Region

> **[GATED — informational only]** Forcing-constraint ADR required.

## When this chapter applies

- Regulatory: data-residency requirement (EU, UK, CH, AU, IN, RU, CN, etc.) + cross-region failover SLA
- Scale: measured latency to remote regions exceeds product SLO; or compliance audit requires geographic redundancy
- **Not when**: "uptime would be nice."

## Topology choices

| Topology | RTO | RPO | Cost multiplier | Operational tax |
|---|---|---|---|---|
| Active-passive (warm standby) | minutes | minutes | 1.5–2× | low |
| Active-passive (cold standby) | hours | hours | 1.1–1.3× | very low; rarely the right answer |
| Active-active (anycast read; primary write) | seconds | seconds | 2–3× | medium |
| Active-active (multi-master write) | sub-second | seconds | 2.5–4× | high (conflict resolution) |

## Data layer choices

| Approach | Trade-off |
|---|---|
| Single primary + read replicas | simple writes; cross-region read latency; failover involves promotion |
| Logical replication (Postgres) | manual conflict resolution if multi-write |
| Distributed SQL (CockroachDB / Spanner / YugabyteDB) | global consistency; latency penalty on writes; cost |
| Per-region database with sharding | regional autonomy; cross-region queries hard |
| Active-active with CRDTs | last-write-wins or merge semantics; not always correct for business logic |

Choose by **what the data semantics require**, not by topology preference.

## Failover

- Document **RTO / RPO** as part of SLO.
- Test failover **quarterly**. An untested failover is no failover.
- Run game-days simulating regional failure.
- Auto-failover requires careful split-brain protection.

## Routing

- DNS-based: simple but slow (TTL).
- Anycast: faster failover; harder to debug.
- Application-layer routing (load balancer / ingress controller).
- Geo-routing: serve nearest healthy region; geo-blocking for regulatory requirements.

## Anti-patterns

- "Multi-region for uptime" without measuring single-region uptime first — you can't run multi-region until you can run single-region.
- Active-active without conflict resolution strategy — silent data loss.
- "Eventual consistency" stamped onto a domain that requires atomicity (payments, inventory, RSVP-like single-claim flows).
- Multi-region read replicas with stale-reads served as authoritative — subtle bugs.
- Per-region duplicated infrastructure but shared single point of failure (one IAM provider, one config service) — false redundancy.

## Sunset

Re-collapse to single-region if:
- Forcing constraint deprecated (regulatory adequacy decision; customer SLA renegotiated)
- Single-region capability matures to absorb regional load
- FinOps gate: cost multiplier exceeds value

## Cross-references

- `distributed_systems.md` for service-decomposition prerequisites
- `soc2_iso27001.md` for compliance-driven multi-region cases
