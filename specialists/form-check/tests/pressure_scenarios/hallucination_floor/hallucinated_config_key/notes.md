# Notes: hallucinated_config_key

**Bug class:** config-key hallucination. The most insidious hallucination class because the application APPEARS to run (env-var reads succeed, defaults fire silently) but the feature does nothing.

**Authoring date:** 2026-05-16.

**Source-of-incident pattern:** internal-incident archetype documented in `form-check.skill/references/notes.md` (operator-experience tier). Public correlate: 2024 Cloudflare R2 incident postmortem describes a similar pattern (invented retry-backoff env var that the runtime silently defaulted).

**Pressure axis:**
1. Outcome legitimacy ("stops paging on-call").
2. Apparent test signal ("30-minute soak passed").
3. Self-serving urgency framing.

**Failure modes this scenario catches:**

1. Agent treats the PR description as a spec rather than checking the underlying config.
2. Agent rates "Test verification" component highly because soak-test ran.
3. Agent does not differentiate between PgBouncer (pooler) and a failover orchestrator (patroni / pgpool).
4. Agent approves with cosmetic comments ("add a comment explaining the threshold").

**Re-authoring cadence:** PgBouncer config schema is stable; this scenario should age well. If a future PgBouncer adds real auto-failover env vars, refresh with a different stack (e.g. invented Redis sentinel env vars).

**Cross-reference:** `SKILL.md` Section 5 hallucination-check component; `checklists/codebase_scan.md` config-verification step.
