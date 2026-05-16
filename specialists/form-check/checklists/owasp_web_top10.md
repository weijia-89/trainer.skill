---
name: owasp_web_top10
version: 2.0.0
source: OWASP-WEB-2025
url: https://owasp.org/Top10/2025/en/
---

# OWASP Top 10 (2025 web) — review checklist

Apply to any browser-rendered web application or service serving HTML / JS / cookies.

## A01:2025 — Broken Access Control

**Question**: Are authorization checks consistent and centralized?

**Defenses**:
- Default-deny; explicit grant per resource × action.
- Centralized policy (OPA / Cedar / Casbin / Spicedb) over scattered `if user.role ==`.
- Test forced browsing (URL guessing) against role tiers.
- For multi-tenant: row-level security (Postgres RLS) where data shape allows.

## A02:2025 — Cryptographic Failures

**Defenses**:
- TLS 1.2+ only; HSTS with preload.
- AES-256-GCM or ChaCha20-Poly1305 for symmetric; never DES, RC4, or unauthenticated CBC.
- Argon2id or scrypt for password hashing; never MD5/SHA-1 for passwords.
- KMS-managed keys; rotate on schedule + on incident.
- Never roll your own crypto. Use `libsodium`, `ring`, `cryptography`, BoringSSL, native platform APIs.

## A03:2025 — Injection

**Defenses**:
- Parameterized queries always (SQL, LDAP, OS-cmd, NoSQL filters).
- Output encoding by context (HTML attribute, JS, URL, CSS, JSON).
- Content Security Policy (CSP) with `default-src 'self'`; nonce-based for inline scripts.
- For LLM prompt injection: see `owasp_llm_top10.md` LLM01.

## A04:2025 — Insecure Design

**Defenses**:
- Threat-model the design *before* implementation (`templates/threat_model.md`, `threat_model_stride.md`).
- Define abuse cases alongside use cases.
- Establish security requirements per feature; make them part of acceptance.
- Reference architecture for sensitive flows (payment, account recovery, data export).

## A05:2025 — Security Misconfiguration

**Defenses**:
- Hardened defaults; explicit deny on missing config.
- Disable directory listing, default accounts, sample apps.
- Verbose errors only in dev; structured error codes in prod.
- IaC scanning (`tfsec`, `checkov`, `kics`, `kubesec`).

## A06:2025 — Vulnerable and Outdated Components

**Defenses**:
- Dependency vuln scan in CI (`pip-audit`, `npm audit`, `govulncheck`, `cargo-audit`, OWASP DC, Snyk).
- SBOM generation (CycloneDX or SPDX); track per-release.
- Pin with hashes (lockfile integrity).
- See `supply_chain_slsa.md` for SLSA target levels.
- Slopsquatting check on every new dep (`bug_class_audit.md` AI-PR section).

## A07:2025 — Identification and Authentication Failures

**Defenses**:
- OIDC / SAML for federation; SCIM for identity sync.
- 2FA / WebAuthn / passkeys for sensitive accounts.
- Session expiry + idle timeout; rotate session ID on auth.
- Generic error messages on login failure (don't reveal "user not found" vs "wrong password").

## A08:2025 — Software and Data Integrity Failures

**Defenses**:
- Signed releases (sigstore / cosign); verify signatures on install.
- CI pipeline integrity (SLSA Build Track L2+).
- No auto-update from untrusted sources.
- Treat third-party prompts and CDN-loaded JS as integrity-relevant.

## A09:2025 — Security Logging and Monitoring Failures

**Defenses**:
- Structured logs (JSON) with PII / secret redaction at write time.
- Log auth events, admin actions, data exports, schema migrations.
- Alert on anomalies (10x normal failed-auth rate, mass deletes, unusual data egress).
- Retain per regulatory requirement; rotate / encrypt at rest.

## A10:2025 — Server-Side Request Forgery (SSRF)

(See API7:2023 same content; cross-listed.)

## Cross-references

- Threat model: `threat_model_stride.md`
- Privacy: `threat_model_linddun.md`
- Supply chain: `supply_chain_slsa.md`
- Auth deep dive: cross-ref OIDC/SAML/SCIM pattern files in `templates/` (forthcoming)

## Output

Per finding: P0/P1/P2 row referencing A0N:2025 + impacted code path + reproduction + proposed fix.
