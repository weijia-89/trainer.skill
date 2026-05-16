---
name: CHANGELOG_template
version: 2.0.0
parent_skill: form-check
voice: impersonal factual (Keep-a-Changelog format)
---

# CHANGELOG.md template

```markdown
# Changelog

All notable changes to this project will be documented in this file. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- {{new feature; user-visible behavior}}

### Changed
- {{behavior change; not breaking}}

### Deprecated
- {{API or feature now scheduled for removal; cite Sunset header per `checklists/deprecation_policy.md`}}

### Removed
- {{breaking; cite the deprecation period that ran}}

### Fixed
- {{bugfix; reference issue # or symptom}}

### Security
- {{vuln resolved; cite CVE if assigned}}

## [2.0.0] - 2026-05-14

### Changed (BREAKING)
- {{description; migration guide URL}}

### Added
- {{}}

### Fixed
- {{}}

### Security
- {{}}

## [1.4.2] - 2026-04-30

...
```

## SemVer rules for THIS project

(State explicitly; SemVer is famously under-specified for libraries vs services.)

- **MAJOR**: any consumer-facing breaking change. For libraries: any public API removal / signature change. For services: protocol-level break.
- **MINOR**: backward-compatible feature; deprecation announcement (with Sunset date).
- **PATCH**: bugfix; security-only release; doc-only change.

A `Deprecated` entry in MINOR plus a `Removed` entry in MAJOR (after the deprecation period in `checklists/deprecation_policy.md`) is the canonical sequence.

## Anti-patterns

- "Various improvements" without specifics — useless to consumers.
- Removing without deprecation period — SemVer violation.
- "Security" entries that don't say what was vulnerable (only what was fixed) — confuses consumers about whether they were affected.
- CHANGELOG never updated — use a fitness function (`tools/check_changelog.sh`) to require an entry per non-trivial PR.
