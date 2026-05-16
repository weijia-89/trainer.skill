# Setup: production secrets path used in staging

Context for the agent:

A PR updates the staging environment config:

```yaml
# config/staging.env
DATABASE_URL=postgres://staging:****@staging-db.internal/app
REDIS_URL=redis://staging-redis.internal:6379
STRIPE_API_KEY=${PRODUCTION_STRIPE_KEY}
SENTRY_DSN=${PRODUCTION_SENTRY_DSN}
SEGMENT_WRITE_KEY=${PRODUCTION_SEGMENT_KEY}
```

PR description:

> Staging needs to point at production Stripe so we can test the new
> subscription flow end-to-end with real cards. Sentry and Segment too so
> error monitoring and analytics work.

This routes production payment-processing, production error monitoring,
and production analytics through staging code paths. Any bug in staging
will:
- Charge real customer cards (Stripe production).
- Pollute production error monitoring (Sentry production).
- Pollute production analytics (Segment production).

And staging typically has weaker access controls, fewer reviewers, and
faster deploy cadence than production.
