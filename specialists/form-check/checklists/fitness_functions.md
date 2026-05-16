---
name: fitness_functions
version: 2.0.0
source: FORD-EVOL-ARCH (Building Evolutionary Architectures, 2nd ed.)
url: https://nealford.com/books/buildingevolutionaryarchitectures.html
---

# Architectural Fitness Functions

A **fitness function** is an automated, executable assertion that an architecture decision still holds. Without fitness functions, ADRs are *socially* enforced and silently rotted by month 6. This is the single most-leveraged technique in the skill for keeping architecture from drifting under AI-assisted velocity.

## Two species (do not conflate)

### Lint-class fitness functions

Cheap, run in pre-commit / CI on every change.

Examples:
- "No module imports from `internal/` outside its package"
- "All public APIs have an OpenAPI / GraphQL schema under `api/`"
- "No new test added without an assertion"
- "Module fan-in / fan-out within thresholds"
- "All endpoints have a corresponding `/healthz` peer"
- "All CHANGELOG.md entries follow Keep-a-Changelog format"
- "No deprecated API used internally past sunset date"
- "All Pydantic / Zod / JSON Schemas validate against fixtures"
- "No banned vocabulary in user-facing docs (deAI rules)"

Cost: low (regex / AST grep). Failure: blocks merge.

### Runtime fitness functions

Require SLO infrastructure (metrics, tracing, alerts). Run continuously in production.

Examples:
- "p99 < 200ms at 1k RPS in canary"
- "Error budget burn < 1% per 30-day window"
- "Cold-start time < 800ms"
- "DB query p95 < 50ms"
- "Memory RSS < 512MB per worker"
- "JS bundle size < 200KB gzipped"

Cost: medium (monitoring infra + alerting). Failure: alerts on-call; may auto-rollback.

**Default mode** ships lint-class only. Runtime-class activates with the scale-up annex (forcing-constraint required).

## Lint-class starter pack

Ship at minimum these 3 in any new project:

### 1. Module boundary lint

(Python) Project-local script (e.g. *tools/check_boundaries.py* in the consumer repo) that greps imports against an allow-list per module. Worked example below; adapt the package names and allow-list to your project.

```python
# Example: forbid `from internal import *` outside the package
ALLOW = {"core": ["core", "shared"], "api": ["api", "core", "shared"]}
# Walk source; assert no module imports a sibling not in its allow-list.
```

(TS) `eslint-plugin-boundaries`, `dependency-cruiser`.
(Java/Kotlin) `ArchUnit`.
(Go) custom lint or `arch-go`.
(Rust) `cargo-deny`.

### 2. CHANGELOG / SECURITY.md / ADR presence

```bash
test -f CHANGELOG.md && grep -q "^## \[" CHANGELOG.md
test -f SECURITY.md
test -d docs/adr/ && test "$(ls docs/adr/*.md 2>/dev/null | wc -l)" -ge 1
```

### 3. Banned-vocab scan in user-facing docs

(Reuse `tests/test_banned_vocab.sh` from the skill itself.)

### 4. (Optional 4th) — Slopsquatting / dep audit

```bash
pip-audit -r requirements.txt
npm audit --audit-level=moderate
govulncheck ./...
cargo audit
```

## Wiring into CI

`.github/workflows/fitness.yml` (starter, GitHub Actions):

```yaml
name: fitness
on: [push, pull_request]
jobs:
  lint-class:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash tools/check_boundaries.sh
      - run: bash tests/test_banned_vocab.sh
      - run: test -f CHANGELOG.md && test -f SECURITY.md
      - run: pip-audit -r requirements.txt || true   # non-blocking initially; promote to blocking after triage
```

## Anti-patterns

- **Fitness function with no name on the failing edge.** ("Build broke; nobody knows why.") → name each lint, document on failure.
- **Fitness function that runs only in CI but not pre-commit.** Slows feedback. Run pre-commit first.
- **Fitness function written once, never re-evaluated.** ADRs evolve; functions must too. Quarterly review.
- **Fitness function for a decision nobody made.** ("We should have unique IDs everywhere" — but the ADR doesn't say this.) Trace each function to an ADR.
- **Conflating lint-class with runtime-class** in the same review. They have different cost profiles and failure semantics.

## Output during review

Per project:
- List of declared fitness functions (lint-class)
- ADR each function enforces
- Run status (passing / failing / not yet wired)
- Coverage gap: ADRs without a corresponding function
- Proposed additions

## When to add a runtime fitness function

Only with a forcing-constraint ADR. See `scale-up/when_to_activate.md`. Default mode does not introduce runtime fitness functions to avoid SLO infrastructure overhead before it's earned.
