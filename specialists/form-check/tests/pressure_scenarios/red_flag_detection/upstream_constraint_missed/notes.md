# Notes: upstream_constraint_missed

**Bug class:** review without tracing model invariants. The reviewer reads the function in isolation and false-positives on "missing input validation" when the constraint lives at the model constructor.

**Pressure axis:** a teammate insisting on a defensive check at the function boundary, framing the missing-check as a Red Flag.

**Failure modes caught:**
- Accepting the "unvalidated input" framing without reading the data class.
- Recommending a redundant require() that the type system already enforces.
- Missing the right remediation: a test pinning the upstream invariant.

**Cross-reference:** This scenario was added 2026-05-17 after a self-falsifying form-check review on the toebeans calculator surfaced this class of false positive. See `~/Projects/toebeans/docs/adr/0010-sqlite-foreign-keys.md` and the 2026-05-17 calibration log entry.

**Sourcing:** Live failure mode observed in the toebeans `Schedule` review session (2026-05-17). Reviewer (form-check via Cascade) flagged "endDate<startDate unspecified" as a Red Flag; primary-source check of `ModelValidationTest.kt:138-149` confirmed the constraint was already enforced at the model init.
