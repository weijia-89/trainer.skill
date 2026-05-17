# Changelog, pr

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

- MAJOR: pre-deploy checklist (§1) or post-deploy verification (§4) drops a load-bearing item. These checklists are the contract; weakening them increases incident rates.
- MINOR: new platform pattern added in §2, new failure-mode entry in §6.
- PATCH: wording, link updates, example refinements.

## [2.0.0], 2026-05-16. Iron Law layering + composes-pin bumps

MAJOR because composes pins changed: form-check `>=2 → >=3`, diet `>=1 → >=2`, safetybar `>=1.0 → >=1.1`.

- Added Iron Law: "NO DEPLOY WITHOUT A ROLLBACK COMMAND YOU CAN STATE IN ONE LINE."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed], 2026-05-15

This skill was renamed from `code-deployer` to `pr` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-deployer.skill/` → `pr.skill/`
- `name:` frontmatter: `code-deployer` → `pr`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.0.0], 2026-05-15

### Added

- Initial release. Seven sections covering pre-deploy checklist, platform-specific patterns, the deploy itself, post-deploy verification, rollback procedure (platform-rollback and code-rollback paths), failure-mode triage, and anti-patterns.
- The pre-deploy checklist (§1) and post-deploy verification (§4) are the load-bearing sections. Beginners who skip them ship broken deploys; beginners who walk them produce reliable deploys regardless of platform sophistication.
- Platform-specific patterns (§2) deliberately favor boring beginner-friendly platforms (Vercel, Netlify, Render, Fly.io, Railway, GitHub Pages, Cloudflare Pages). The Kubernetes/multi-region/service-mesh territory is gated behind a forcing-constraint ADR in `code-inspector/scale-up/`.
- Composition with `code-inspector` (reversibility and blast-radius rubric components), `code-operator` (handoff after successful deploy or during deploy-caused incident), `git-recovery` (code-level rollback when platform-rollback is not enough).

### Rationale

The SDLC-gap analysis classified deployment as a medium-priority gap. Beginners often get a "good enough" deploy path from their platform's tutorial, but the tutorial does not help once something is broken at deploy time. This skill picks up where the tutorial leaves off: what to do when the build fails, what to check before a deploy, how to roll back without making things worse.

The rollback procedure (§5) is the single most-referenced section by other skills. `code-operator §3.4` and `git-recovery §2.2` both link to it.
