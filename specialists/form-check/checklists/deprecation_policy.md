---
name: deprecation_policy
version: 2.0.0
source: RFC-8594; SemVer canon
---

# API Deprecation Policy

Removing or breaking a public API surface is irreversible from the consumer's perspective. Treat as vibe-dangerous (`rubrics/vibe_safety_map.md` Bucket 3). Use this checklist any time you sunset a flag, header, endpoint, response field, CLI option, library function, or config schema.

## Timeline (default)

| Audience | Minimum deprecation period |
|---|---|
| Internal (single team consumer) | 30 days |
| Internal (>1 team consumer) | 90 days |
| Public (free) | 180 days |
| Public (paid) | 12 months |
| Regulated / certified APIs | per regulator + min 18 months |

These are minima; longer for high-stakes integrations.

## HTTP API deprecation (RFC 8594 + Deprecation header draft)

Mark the deprecated response with both headers:

```
Deprecation: @1717200000   # IMF-fixdate or Unix timestamp of deprecation announcement
Sunset: Wed, 11 Jun 2026 23:59:59 GMT   # planned removal date
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="deprecation"
```

After Sunset:
- Old endpoint returns `410 Gone` with a body explaining the migration path.
- Or returns the new shape with a final `Deprecation` + `Sunset` (in the past) header.

## Library / SDK deprecation

| Language | Mechanism |
|---|---|
| Python | `@warnings.deprecated(...)` (3.13+) or `DeprecationWarning` |
| TypeScript | `/** @deprecated since 2.3.0, use Foo instead */` JSDoc + ESLint rule |
| Java/Kotlin | `@Deprecated(since="2.3.0", forRemoval=true, replacement="Foo")` |
| Go | comment `// Deprecated: use Foo instead.` (godoc convention) |
| Rust | `#[deprecated(since = "2.3.0", note = "use Foo instead")]` |

## CLI flag deprecation

```text
$ tool --old-flag X
warning: --old-flag is deprecated since 2.3.0; use --new-flag (will be removed in 3.0.0)
```

Provide a migration script when possible (`tool migrate-flags`).

## Database schema deprecation (expand-contract)

See EXPAND-CONTRACT pattern (PGROLL):

1. **Expand**: add the new column / table; backfill via a job; dual-write from app.
2. **Migrate**: clients switch reads + writes to new shape one by one.
3. **Contract**: remove old column / table after Sunset.

Never break-and-replace; never run a migration that loses data without a documented rollback path.

## Output for the deprecation PR

Required PR sections:
1. **What's deprecated** (one-line).
2. **Why** (driver / replacement).
3. **Sunset date** (must align with policy table above).
4. **Migration guide URL** (must exist before merge; link from CHANGELOG).
5. **Affected consumers** (internal teams; external partner status).
6. **Telemetry**: how usage of the deprecated path will be tracked (so we know it's safe to remove).
7. **Rollback plan**: what happens if the replacement breaks?

## Anti-patterns

- Deprecating without a replacement.
- Sunset date in the past at announcement time.
- Removing before Sunset.
- "Deprecated since the beginning of time", undocumented, never enforced.
- Migration guide that doesn't actually compile / run on the replacement.
- Silent breaking change in a "patch" version (SemVer violation).

## When to refuse

Refuse to remove a public API path on a vibe-coded change unless:
- The deprecation period elapsed (per policy table)
- Migration guide exists and was tested
- ADR documents the decision and Sunset date
- Telemetry confirms <1% remaining usage (or accepted exception)
