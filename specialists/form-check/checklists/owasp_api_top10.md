---
name: owasp_api_top10
version: 2.0.0
source: OWASP-API-2023
url: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
---

# OWASP API Security Top 10 (2023) — review checklist

Apply to any code that exposes or consumes HTTP APIs (REST, GraphQL, gRPC-Web).

## API1:2023 — Broken Object Level Authorization (BOLA)

**Question**: Does the endpoint accept an object ID from the client and return data without verifying the caller may access *that specific object*?

**Defenses**:
- Per-request authorization check against `(caller, object_id)`.
- Use opaque IDs (UUIDs) not sequential integers when possible.
- Never trust client-asserted ownership.

**Anti-pattern**: `GET /orders/:id` that loads the order without checking `order.customer_id == auth.user_id`.

## API2:2023 — Broken Authentication

**Defenses**:
- OIDC or SAML for human auth; mTLS or signed JWT for service-to-service.
- No homemade JWT signing; use a vetted library (jose, jjwt, golang-jwt).
- Rotate signing keys; publish JWKS.
- Rate-limit auth endpoints.
- 2FA for sensitive operations.

## API3:2023 — Broken Object Property Level Authorization (BOPLA)

(Merges 2019's Mass Assignment + Excessive Data Exposure.)

**Defenses**:
- Allowlist input properties on write (don't just `Object.assign(user, body)`).
- Allowlist output properties on read (per-role response shaping).
- For GraphQL: per-field auth; depth-limit + cost-limit queries.

## API4:2023 — Unrestricted Resource Consumption

**Defenses**:
- Pagination on all list endpoints (max-page-size enforced server-side).
- Per-tenant rate limits (requests/sec + bandwidth + DB-row budget).
- Timeout on every external dependency call.
- Body-size limits at ingress.

## API5:2023 — Broken Function Level Authorization (BFLA)

**Question**: Can a user-tier caller invoke admin-tier endpoints?

**Defenses**:
- Per-endpoint role check; default-deny.
- Use a centralized policy engine (OPA, Cedar, Casbin) instead of scattered `if`s.
- Distinguish authentication from authorization in middleware.

## API6:2023 — Unrestricted Access to Sensitive Business Flows

**Question**: Could an attacker abuse a legitimate API path at scale (ticket scalping, account creation farming, free-tier abuse)?

**Defenses**:
- Rate limits keyed by behavioral signal, not just IP.
- CAPTCHA on suspicious patterns.
- Fraud / bot detection layer.
- Per-flow quota beyond per-endpoint quota.

## API7:2023 — Server Side Request Forgery (SSRF)

**Question**: Does any endpoint fetch a URL the caller controls?

**Defenses**:
- Block link-local (169.254.0.0/16, 127.0.0.0/8), private (10/8, 172.16/12, 192.168/16, fc00::/7), file://, gopher://, etc.
- Egress-only outbound proxy with allowlist.
- Cross-ref CWE-918.

## API8:2023 — Security Misconfiguration

**Defenses**:
- Default-secure framework configs (Helmet, secure cookies, HSTS, CSP).
- No verbose errors in prod; structured error codes only.
- TLS 1.2+ only; HSTS preload.
- IaC linted (`tfsec`, `cfn-lint`, `checkov`).

## API9:2023 — Improper Inventory Management

**Defenses**:
- Maintain `docs/api-inventory.md` listing every endpoint, version, deprecation status.
- Sunset old API versions per RFC 8594 (`checklists/deprecation_policy.md`).
- Block or auth-gate "v0/internal" / staging endpoints in prod.

## API10:2023 — Unsafe Consumption of APIs

**Question**: When *your* code consumes a third-party API, do you treat its responses as trusted?

**Defenses**:
- Validate third-party responses against a schema.
- Timeout, retry-with-backoff, circuit-breaker pattern.
- Vuln-scan the SDK / client library.
- TLS verify; cert pinning where appropriate.

## Cross-references

- Auth deep dive: STRIDE Spoofing + Elevation of Privilege (`threat_model_stride.md`)
- Supply chain (API10): `supply_chain_slsa.md`
- API deprecation (API9): `deprecation_policy.md`

## Output

Per finding: P0/P1/P2 row referencing the API0N:2023 ID + endpoint + reproduction step + proposed fix.
