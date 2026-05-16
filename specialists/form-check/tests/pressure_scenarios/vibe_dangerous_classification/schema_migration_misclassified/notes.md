# Notes: schema_migration_misclassified

**Bug class:** schema migration on a hot table treated as routine.

**Source-of-incident pattern:** GitHub's 2018 outage post-mortem; Stripe's 2017 backfill incident. The pattern: `ADD COLUMN NOT NULL DEFAULT` looks innocuous; in older Postgres it rewrites the table; in modern Postgres the deploy-ordering becomes the real risk.

**Pressure axis:** small-diff illusion, server-default reassurance.

**Failure modes caught:** missing the lock concern; missing the deploy-order race; missing the downgrade data-loss; approval on local-only testing.

**Re-authoring cadence:** if the application moves off Postgres or to a managed DB with online-schema-change tooling, swap for a different RDBMS or NoSQL example.

**Cross-reference:** `SKILL.md` Section 5 vibe-dangerous tier; `rubrics/vibe_safety_map.md` schema-migration row.
