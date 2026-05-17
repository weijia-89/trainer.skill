---
name: SECURITY_md_template
version: 2.0.0
parent_skill: form-check
voice: imperative for ops; descriptive for threat model
---

# SECURITY.md template

```markdown
# Security Policy, {{project-name}}

## Reporting a vulnerability

Email security@{{domain}} (PGP: {{key fingerprint}}).

**Do not** open public GitHub issues for security vulnerabilities.

We aim to acknowledge within {{1 business day}}, triage within {{5 business days}}, and resolve P0 within {{10 business days}}. We credit reporters on a public security advisory unless they request anonymity.

## Supported versions

| Version | Status | EOL |
|---|---|---|
| {{2.x}} | supported | (active) |
| {{1.x}} | security-only | {{date}} |
| {{0.x}} | unsupported | (passed EOL) |

## Threat model

See `docs/threat-model.md` (STRIDE + LINDDUN where applicable).

Key trust boundaries:
- {{user ↔ edge}}
- {{edge ↔ service}}
- {{service ↔ database}}
- {{service ↔ third-party (incl. LLM provider if applicable)}}

## Data classes processed

- {{public / internal / confidential / PII / PHI / PCI / NPI}}

## Regulatory landscape

- {{GDPR / CCPA / HIPAA / PCI-DSS / SOC2 / ISO 27001 / FedRAMP / none}}

## Hardening posture

- TLS 1.2+ only; HSTS preload
- Argon2id for passwords; KMS-managed keys
- mTLS service-to-service (if applicable)
- OIDC / SAML for human identity (if applicable)
- Per-tenant rate limits and behavioral abuse detection
- Append-only audit log; secret/PII redaction at write time

## Supply chain

- SLSA Build Track L2 minimum (target L3)
- Dependency lock-files with hashes
- {{audit-tool}} runs in CI; high/critical block merge
- SBOM ({{CycloneDX or SPDX}}) generated per release
- New-dep slopsquatting check ritual: registry exists, author known, first-seen ≥30d, prior versions exist

## Incident response

- Runbook: `docs/runbooks/incident_response.md`
- Supply-chain compromise runbook: `docs/runbooks/supply_chain_compromise.md`
- On-call rotation: {{link}}

## Compliance status

- {{SOC2 Type 2: in progress / certified by AUD-XXX / not pursued}}
- {{ISO 27001: in progress / certified / not pursued}}
- {{Last penetration test: {{date}} by {{vendor}}}}

## Out of scope

- {{deliberate non-coverage}}: {{reason}}
- Self-hosted deployments outside our published support matrix
```
