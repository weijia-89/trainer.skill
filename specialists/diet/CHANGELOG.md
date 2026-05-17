# Changelog, diet

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

- MAJOR: the incident protocol (§3) changes in load-bearing ways (the four-question triage shape, the forbidden-moves list, the rollback decision rule). These changes break the muscle memory the skill is designed to build.
- MINOR: new sections, new instrumentation patterns, new platform-specific guidance, new anti-patterns.
- PATCH: wording, citations, example refinements.

## [2.0.0], 2026-05-16. Iron Law layering + composes-pin bumps

MAJOR because composes pin to form-check changed from `>=2.0.0,<3.0.0` to `>=3.0.0,<4.0.0`, and pin to safetybar changed from `>=1.0.0,<2.0.0` to `>=1.1.0,<2.0.0`.

- Added Iron Law: "NO DESTRUCTIVE ACTION DURING AN INCIDENT WITHOUT A SECOND HUMAN'S EYES."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.
- Composes-pin: form-check `>=3.0.0,<4.0.0`; safetybar `>=1.1.0,<2.0.0`.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed], 2026-05-15

This skill was renamed from `code-operator` to `diet` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-operator.skill/` → `diet.skill/`
- `name:` frontmatter: `code-operator` → `diet`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.0.0], 2026-05-15

### Added

- Initial release. Five sections covering minimum-viable instrumentation (logs, error tracking, four golden signals, uptime check), steady-state cadence, incident response, post-mortem template, and when-to-escalate to a real ops team.
- §3 incident protocol with explicit forbidden-moves list (no destructive commands, no force-push, no in-incident migrations, no deletes, no instrumentation disables) anchored to the Replit/Lemkin July 2025 cautionary tale.
- Composition with `code-inspector` (threat-model + reversibility), `git-recovery` (code-level rollback), and `code-deployer` (deploy-level rollback).

### Rationale

The May 2026 SDLC-gap analysis flagged ops and incident response as **the highest-leverage gap** for the beginner persona. The failure mode is well-documented: ship → break → panicked destructive action → make it worse. Most beginner curricula skip operate-and-respond entirely; this skill closes the gap.

The §3 incident protocol borrows from the Google SRE Book chapter 14 (Managing Incidents), the PagerDuty incident-response training, and the Etsy/Allspaw blameless post-mortem tradition. Adapted for solo and small-team contexts: simpler triage, fewer roles, stronger emphasis on do-not-make-it-worse.
