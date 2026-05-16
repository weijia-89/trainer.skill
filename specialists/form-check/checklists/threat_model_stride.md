---
name: threat_model_stride
version: 2.0.0
source: STRIDE-WIKI (Garg & Kohnfelder, 1999; modernized for cloud + LLM)
---

# STRIDE Threat-Model Checklist

Apply to any vibe-dangerous change. Walk all 6 categories per data-flow boundary.

## Process

1. Draw a data-flow diagram (DFD): processes, data stores, data flows, trust boundaries.
2. For each *trust boundary crossing* in the DFD, walk the 6 categories below.
3. Record findings per row in `templates/threat_model.md`.

## Categories

### S — Spoofing
**Question**: Can an attacker pretend to be someone they're not?

**Examples**:
- Forged JWT with weak signature
- Session fixation
- DNS rebinding
- Email-based account recovery without secondary verification

**Mitigations**: strong auth, mTLS for service-to-service, signed tokens, replay-protection (nonce / timestamp), HSTS, secure cookies.

### T — Tampering
**Question**: Can an attacker modify data in flight or at rest?

**Examples**:
- HTTP without TLS
- Unsigned package install
- Direct DB write bypassing the API
- Modifying client-stored state (cookie, JWT, localStorage)

**Mitigations**: TLS 1.2+, signed releases (sigstore/cosign), integrity-protected encryption (GCM/ChaCha20-Poly1305), server-side validation, SLSA Build Track L2+.

### R — Repudiation
**Question**: Can an actor deny taking an action?

**Examples**:
- Admin actions without audit log
- Mutable logs
- Shared service accounts

**Mitigations**: append-only audit log, signed log lines, per-user service identities, time-synced clocks.

### I — Information Disclosure
**Question**: Can data leak to unauthorized parties?

**Examples**:
- Verbose error messages with stack traces
- PII in INFO-level logs
- Debug endpoints exposed
- Side-channel timing attacks
- LLM system-prompt leakage (LLM07:2025)

**Mitigations**: structured errors, log redaction, per-tier endpoint exposure, constant-time comparison for tokens.

### D — Denial of Service
**Question**: Can the service be made unavailable?

**Examples**:
- Unbounded recursion (zip bombs, billion-laughs XML, regex catastrophic backtracking)
- Slow-loris
- Subprocess without timeout
- Unbounded LLM context fills

**Mitigations**: timeouts everywhere, body-size limits, regex DoS scan, rate-limit, circuit-breaker.

### E — Elevation of Privilege
**Question**: Can a low-privilege actor gain higher privileges?

**Examples**:
- Missing authorization check (CWE-862)
- IDOR (BOLA, API1:2023)
- Privilege escalation in the host (kernel exploit)
- LLM agent tool grant beyond intended scope (LLM06:2025)

**Mitigations**: default-deny authorization, principle of least privilege, sandboxing, capability allowlisting (`agent-runtime/harness_contract.md`).

## Per-boundary worksheet

Use `templates/threat_model.md`. One worksheet per trust-boundary-crossing; rows = STRIDE category × specific surface.

## When to apply

- All vibe-dangerous changes (mandatory for confidence-score component 9).
- Major design decisions (record outcome in MADR ADR).
- Pre-launch hardening pass.
- After every security-relevant CVE in a dependency that we use.

## Output

For each STRIDE row that's not "n/a-with-reason":
- Threat description
- Impact (P0/P1/P2)
- Mitigation in place / planned
- Test that would catch a regression
