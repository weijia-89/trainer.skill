---
name: stack_decision
version: 2.0.0
parent_skill: form-check
---

# Stack Decision Rubric (v2, multi-language; cite or `[normative]`)

Always state **chosen + rejected alternative + 1-sentence why each**, anchored to a citation OR explicitly tagged `[normative, operator wisdom]`. Section 2 of `SKILL.md` summarizes; this file is the full template.

## Decision tree

```text
Is this a single binary or CLI tool?
  └─ yes → Go (stdlib + chi or cobra) OR Rust (clap + std).
        Go default unless memory/perf budget is the spec; then Rust.
        [normative, operator wisdom]

Is the team Python-comfortable or is this data/ML-adjacent?
  └─ yes → Python + FastAPI + Postgres + Next.js (only if web UI).
        Reject Django **unless** the team values batteries-included admin/ORM more than async-first contracts.
        [normative, operator wisdom + FastAPI vs Django stylistic call]

Is the team JS-comfortable, or is this a one-person greenfield?
  └─ yes → TS everywhere (Next.js App Router + Drizzle + Postgres via Neon/Supabase + Tailwind).
        Reject Python full-stack ("single language, single deploy, type-safety end-to-end").
        [normative, operator wisdom]

Forms-heavy CRUD, regulated, or "boring web app"?
  └─ yes → Rails 8 (Solid stack) OR Django.
        Rails: Solid Queue/Cache/Cable removed Redis dep; Django: stronger admin and ORM ecosystem.
        [normative]

**Enterprise greenfield, JVM org, regulated** (gated)?
  └─ yes → Kotlin + Spring Boot 3 + Postgres + Gradle (see scale-up/spring_kotlin_jvm.md)
        Reject Java + Spring **only on stylistic preference** (Kotlin null-safety + coroutines wins; Java is fine if team owns it).
        [normative, gated by forcing-constraint ADR]

Embedded / safety-critical?
  └─ yes → Rust (no_std + embassy) OR C with MISRA + frama-c.
        Default Rust unless toolchain availability blocks (e.g. niche MCU without Rust target).
        [normative]
```

## DB decision

| Use case | Default | Justify only if |
|---|---|---|
| OLTP | Postgres | Stick to it. |
| Local / single-user | SQLite (WAL mode) | Need concurrent writers across processes |
| Analytics / OLAP | DuckDB | >100 GB or distributed |
| Cache | "skip the cache, profile first" | Measured p99 says you must |
| Search | Postgres FTS | Need >1M docs or relevance tuning |
| Time-series | TimescaleDB (Postgres ext) | >1B rows or true streaming workload |
| Graph | Postgres + recursive CTE OR pg_age | Truly graph-shaped queries dominate |
| Vector | pgvector | >10M embeddings AND latency-bound |

## Infra decision

- **One PaaS.** Fly, Render, Railway, Vercel.
- **No k8s** until forced. **Forcing constraints** (any one, written into an ADR before scale-up content is consulted):
  - Regulatory multi-cloud requirement
  - >50 services in production
  - Existing org-wide platform team
  - Measured >10k RPS sustained for >30 days requiring horizontal pod scaling
- See `scale-up/when_to_activate.md`.

## ORM decision

| Stack | Default ORM | Reject |
|---|---|---|
| Python | SQLAlchemy 2.x + Alembic | Django ORM (couples models to framework); raw SQL strings (injection risk) |
| TypeScript | Drizzle | Prisma (heavier query layer; harder migration ergonomics) |
| Java/Kotlin | Spring Data JPA + Flyway | jOOQ (great but less batteries); raw JDBC |
| Go | sqlc + pgx | GORM (magic; harder to optimize) |
| Rust | sqlx | Diesel (great types but compile-time burden); SeaORM (newer, fewer prod hours) |
| Rails | ActiveRecord | n/a |

## When to break the rule

Document as an **ADR** (`templates/MADR_short.md`). Title format: `NNNN-{verb}-{thing}.md`. Example: `0007-use-clickhouse-for-event-analytics.md`. Required sections: Context, Considered Options, Decision Outcome, Consequences, Confirmation.

## Anti-checklist (refuse-by-default)

Reject these defaults at project start (default mode):
- "Microservices because we'll scale", Newman: last resort; name the forcing constraint
- "GraphQL because mobile", REST + good cache headers + JSON:API or HATEOAS-lite solves 95% of cases; GraphQL adds federation cost without measured benefit
- "Event bus because async", start with Postgres LISTEN/NOTIFY or a pg-backed queue (River, pgmq, Sidekiq)
- "Service mesh because zero-trust", start with mTLS + a single ingress; mesh is operational tax for solving problems you don't have yet
- "Multi-region because uptime", start single-region; you can't run multi-region until you can run single-region

## Multi-language tooling references

Per-concern × language matrix: `multi-language/matrix.md`.
Per-language deep dive (test runner, mutation, lint, audit, lockfile, fuzz, format, secrets-scan, IaC-lint, SBOM): `multi-language/{python,typescript,java,go,rust}.md`.

## Cite-or-normative discipline

Every row in this file is either:
- **Cited** to a primary source (RFC, official spec, peer-reviewed paper, vendor canonical doc)
- **Tagged `[normative]`** as operator wisdom

If you find a row that is neither, flag it and either find the cite or downgrade to `[normative]`. **Do not silently treat taste as canon.**
