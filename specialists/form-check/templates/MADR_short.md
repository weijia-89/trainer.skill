---
name: MADR_short_template
version: 2.0.0
parent_skill: form-check
status: template
---

# NNNN, {Title in imperative form}

- Status: {proposed | accepted | superseded by NNNN}
- Date: {YYYY-MM-DD}
- Deciders: {who}

## Context and Problem Statement

{One paragraph. Why are we deciding this now? What is the forcing function?}

## Considered Options

- Option A: {one line each}
- Option B
- Option C

## Decision Outcome

Chosen option: **{Option B}**, because {one or two sentences citing the strongest evidence, perf number, regulatory line, lock-in cost}.

### Consequences

- ✅ {good consequence}
- ✅ {good consequence}
- ⚠ {trade-off / cost we accept}

### Confirmation

How we will know if this was right (or wrong) in 90 days: {falsifiable check, e.g. "p99 < 200ms", "no rollback opened against this in 90d"}.

---

## Worked example, `0001-use-sqlite-wal-for-local-storage.md`

- Status: accepted
- Date: 2026-04-30

### Context and Problem Statement

Single-user CLI tool needs persistent storage for audit history. Multi-user concurrency is not in scope.

### Considered Options

- SQLite with WAL mode
- Postgres via local Docker
- Flat JSON files

### Decision Outcome

Chosen: **SQLite + WAL mode**, because zero ops cost, atomic transactions, and `sqlite-utils` gives us schema-on-read for ad-hoc queries.

### Consequences

- ✅ Zero infra to install
- ✅ Atomic writes via WAL
- ⚠ Single-writer limit (acceptable; CLI is single-user)
- ⚠ If we ever need multi-host, we migrate to Postgres (planned escape hatch)

### Confirmation

If we file >2 issues in 90 days about "SQLite isn't enough", revisit and write `0002-migrate-to-postgres.md`.
