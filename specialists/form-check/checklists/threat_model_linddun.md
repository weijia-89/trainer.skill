---
name: threat_model_linddun
version: 2.0.0
source: LINDDUN (KU Leuven imec-DistriNet)
url: https://linddun.org/
---

# LINDDUN Privacy Threat-Model Checklist

Apply to any change touching personal data flows. STRIDE covers security threats; LINDDUN covers privacy threats, they are complementary, not redundant.

## Process

1. Draw a DFD focused on personal-data flows.
2. For each PII-bearing flow, walk all 7 LINDDUN categories.
3. Cross-reference applicable regulations (GDPR, CCPA/CPRA, HIPAA, PIPEDA).
4. Record findings in `templates/threat_model.md` (privacy section).

## Categories

### L, Linkability
**Question**: Can two records about the same person be linked across contexts?

**Examples**:
- Persistent UUIDs shared across services
- Cross-context IDs (e.g. user email used as login + analytics + marketing)

**Mitigations**: per-context pseudonyms, salted hash for cross-context joins, separate analytics ID from auth ID.

### I, Identifiability
**Question**: Can a person be identified within a dataset?

**Examples**:
- "Anonymous" data with quasi-identifiers (zip + DOB + gender → 87% reidentification)
- Free-text fields containing names

**Mitigations**: k-anonymity (k≥5 typical), generalization, suppression, differential privacy for aggregates.

### N, Non-repudiation (privacy sense)
**Question**: Could someone *prove* a person did/said something they shouldn't have to prove?

**Examples**:
- Signed messages used for non-repudiation in domains where deniability is desirable (whistleblower, harassment-survivor support)

**Mitigations**: ring signatures, deniable encryption, separate audit-log channel from user-facing channel.

### D, Detectability
**Question**: Can an attacker detect the *existence* of an item even without reading it?

**Examples**:
- "User X has an account on platform Y" leakage via account-recovery side channel
- Per-user file-size patterns

**Mitigations**: generic responses that don't disclose existence, padding, decoy traffic.

### D, (Information) Disclosure
**Question**: Can personal data leak?

(Cross-listed with STRIDE-I.)

**Mitigations**: encryption at rest + in transit, access controls, output redaction, secure deletion.

### U, Unawareness
**Question**: Are users unaware of what data is collected, processed, stored, shared?

**Examples**:
- Missing privacy notice
- Hidden tracking
- Data shared with third parties without disclosure

**Mitigations**: clear privacy notice, just-in-time consent, transparency dashboard, data-subject-access tooling (GDPR Art 15).

### N, Non-compliance
**Question**: Does the design comply with applicable privacy regulations?

**Examples**:
- Data retention beyond legal limits
- Cross-border transfer without adequate safeguards
- Children's data without COPPA/AADC compliance
- Health data without HIPAA / GDPR Art 9 protections

**Mitigations**: data-classification taxonomy (`templates/threat_model.md`), retention policy with automated deletion, transfer mechanism (SCCs, BCRs), DPIA on high-risk processing (GDPR Art 35).

## When to apply

- Any change to data collection, storage, processing, sharing.
- Adding a new PII field.
- Changing retention policy.
- Cross-border data transfer.
- Sharing with new third party (incl. LLM providers).
- Pre-launch.

## Cross-references

- Data classification: `templates/threat_model.md`
- LLM-specific privacy: OWASP LLM02:2025 (Sensitive Information Disclosure), LLM04:2025 (Data Poisoning)
- Supply chain (third-party data flows): `supply_chain_slsa.md`

## Output

Per finding:
- Privacy threat (LINDDUN category)
- Affected data class (PII / PHI / PCI / NPI / sensitive-personal)
- Regulatory anchor (GDPR Art X, CCPA §X, HIPAA §X)
- Mitigation in place / planned
- DPIA needed? (GDPR Art 35 trigger criteria)
