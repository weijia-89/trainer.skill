---
name: README_service_archetype
version: 2.0.0
parent_skill: form-check
voice: operator-led; what it does, how to run it, how to debug
---

# README archetype: Service / API server

```markdown
# {{service-name}}

> What it does. Who consumes it. ≤2 sentences.

[![CI](badge)](url) [![Coverage](badge)](url) [![Deploy](badge)](url)

## What this serves

- **Consumers**: {{which clients / services}}
- **Public surface**: {{HTTP / gRPC / GraphQL, endpoint or schema link}}
- **Trust boundary**: {{which network zone}}

## Local development

### Prerequisites

- {{language toolchain}} version {{exact}}
- Docker (for local Postgres / Redis / etc.)
- `direnv` or equivalent

### Running

```bash
make dev    # starts Postgres + service in dev mode
make test
make lint
```

Service starts on `:{{port}}`. Health check: `GET /healthz`. Readiness: `GET /readyz`.

### Test data

```bash
make seed   # loads minimal dataset for local development
```

## Configuration (12-factor)

- Env vars: see `config.example.env`. Validated on startup; service refuses to boot on missing required vars.
- Secrets: `{{tool}}` (Vault / KMS / cloud secrets manager). Never in env files committed to git.
- Per-environment overrides: `config/dev.yaml`, `config/staging.yaml`, `config/prod.yaml`.

## Deployment

- **Platform**: {{Fly / Render / Railway / Vercel / Cloud Run}}
- **CI/CD**: {{GitHub Actions workflow link}}
- **Rollout**: {{trunk-based, deploy-on-merge, with feature flags}}
- **Rollback**: {{procedure, last-known-good redeploy, or `flyctl deploy --image=:prev`, or DB-aware rollback runbook}}

## Observability

- **Metrics**: {{Prometheus / Datadog / Cloud Monitoring}}, dashboard link
- **Tracing**: {{OpenTelemetry exporter}}
- **Logging**: structured JSON; PII redacted at write time
- **Alerts**: {{alertmanager / PagerDuty}}, runbook links per alert

## SLOs

| Metric | Target |
|---|---|
| Availability | {{99.9% / month}} |
| p99 latency | {{<200ms}} |
| Error rate | {{<0.1%}} |

Error budget policy: {{link}}.

## Documentation

- **API reference (consumers)**: {{OpenAPI URL or schema repo}}
- **Architecture**: `ARCHITECTURE.md`
- **Security**: `SECURITY.md`
- **Runbooks**: `docs/runbooks/`
- **Changes**: `CHANGELOG.md`

## On-call

- Rotation: {{link}}
- Common issues + runbooks: `docs/runbooks/`
- Postmortem template: `docs/postmortem-template.md`

## Contributing

See `CONTRIBUTING.md`. Especially: `docs/adr/` for proposing architectural changes.

## License

{{SPDX identifier}}
```

## Notes

- **Service README is operator-led.** Local dev → config → deploy → observe.
- **Runbook links from alerts** in the README, operators land here at 3 AM.
- **SLOs are a section, not a footnote.** They define the contract.
- **No "vision" sections** in service READMEs. Vision belongs in ROADMAP or company docs.
