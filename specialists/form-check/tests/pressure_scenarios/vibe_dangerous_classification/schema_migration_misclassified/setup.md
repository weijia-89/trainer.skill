# Setup: schema migration misclassified

Context for the agent:

A migration adds a NOT NULL column with a default backfill:

```python
# alembic/versions/2026_05_16_add_user_tier.py
def upgrade():
    op.add_column(
        "users",
        sa.Column("tier", sa.String(20), nullable=False, server_default="free"),
    )

def downgrade():
    op.drop_column("users", "tier")
```

PR description:

> Adds the user tier column with default 'free'. Backfill is automatic via
> server_default. Tested locally on a 1000-row dump. Downgrade drops the
> column.

Real concerns:

1. On a multi-million-row `users` table, `ADD COLUMN ... NOT NULL DEFAULT 'free'`
   in PostgreSQL <11 rewrites the entire table (table lock). In PG 11+ it
   metadata-only adds, BUT the column needs to be readable by the OLD code
   (deployed before the migration) too; OLD code does not know about `tier`.
2. The downgrade drops the column unconditionally; any data written to `tier`
   in the upgraded window is lost on rollback.
3. No backfill verification (was every row populated?).
4. No application-side reader for `tier` yet, so the column has no callers,
   but a future PR will add them and the migration might race.
