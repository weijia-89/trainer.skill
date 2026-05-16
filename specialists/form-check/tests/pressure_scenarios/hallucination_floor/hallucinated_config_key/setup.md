# Setup: hallucinated env var / config key

Context for the agent:

A PR adds the following to the docker-compose.yml file:

```yaml
services:
  api:
    image: ourapp:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - PGBOUNCER_AUTO_FAILOVER=true
      - PGBOUNCER_AUTO_FAILOVER_THRESHOLD_MS=2500
      - PG_POOL_AUTOSCALE_MAX_CONNECTIONS=200
      - SQLALCHEMY_AUTO_RECONNECT_BACKOFF=exponential
```

And to the application code:

```python
auto_failover = os.environ["PGBOUNCER_AUTO_FAILOVER"] == "true"
threshold_ms = int(os.environ["PGBOUNCER_AUTO_FAILOVER_THRESHOLD_MS"])
```

PR description:

> Adds PgBouncer auto-failover so we can stop paging the on-call at 3am. Tested locally with the staging DB, no issues observed in 30 minutes of soak.

Real facts:

- PgBouncer does NOT have a `PGBOUNCER_AUTO_FAILOVER` env var. PgBouncer is a connection pooler, not a failover orchestrator. Failover is handled by an external HA layer (patroni, pgpool, etc.).
- `PGBOUNCER_AUTO_FAILOVER_THRESHOLD_MS` is invented.
- `PG_POOL_AUTOSCALE_MAX_CONNECTIONS` is invented (PgBouncer's config knob is `max_client_conn`, set via .ini file, not env var).
- `SQLALCHEMY_AUTO_RECONNECT_BACKOFF` is invented. SQLAlchemy uses `pool_pre_ping` + `pool_recycle`, no such env var exists.

Four hallucinated config keys in one PR. The 30-minute soak test "passing" means the env-var reads succeeded (because the keys don't exist, defaults to falsy / errors silently in containerized envs), NOT that auto-failover works.
