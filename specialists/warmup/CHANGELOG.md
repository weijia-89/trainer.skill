# Changelog, warmup

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

This skill is intentionally thin. Versioning is correspondingly simple.

- MAJOR: routing-table semantics change in a way that breaks downstream skills that compose against `code-clinic` (none currently exist).
- MINOR: routing-table gains or loses a row (a downstream skill is added or retired from the ecosystem).
- PATCH: wording, examples, or graduation-checklist refinement without changing routing behavior.

## [2.0.0], 2026-05-16. Iron Law layering + all composes-pins bumped

MAJOR because all 7 downstream composes pins changed: program `>=1 → >=2`, form-check `>=2 → >=3`, recovery `>=2 → >=3`, pr `>=1 → >=2`, diet `>=1 → >=2`, safetybar `>=1.0 → >=1.1`, gymbuddy `>=1 → >=2`.

- Added Iron Law: "NO DIRECT ACTION FROM WARMUP. ROUTE FIRST, THEN ACT IN THE DOWNSTREAM SKILL."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed], 2026-05-15

This skill was renamed from `code-clinic` to `warmup` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-clinic.skill/` → `warmup.skill/`
- `name:` frontmatter: `code-clinic` → `warmup`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.1.0], 2026-05-15

### Added

- Routing for five new downstream skills: `code-planner`, `code-deployer`, `code-operator`, `git-recovery`, `ai-helper`. The routing table grew from two rows to eight; the ASCII ecosystem diagram now shows all eight skills with the `codebase_scan.md` cross-cutting checklist underneath.
- Special-case incident handling in the harness contract. If the trigger keyword matches incident vocabulary ("fire", "down", "broken", "outage", "incident"), the harness skips the routing table and loads `code-operator §3` directly. Reading a triage table is not appropriate during an incident.
- `graduation_checklist.md`, operationalized six-item self-assessment for the outgrow signal. Replaces the original descriptive prose ("you should outgrow this within 5–10 invocations") with concrete pass criteria for each item and an optional local-only logging contract for harness implementers.

### Changed

- The intake question is now a single routing table instead of a sequential two-question dialog. The original two-question shape did not generalize past two downstream skills; the table does.

### Rationale

The v1.0 design assumed two downstream skills (`code-inspector`, `code-fixer`) and routed between them. The SDLC-gap analysis in `code-inspector/CHANGELOG.md` 2.1.x identified five additional gaps and motivated building five additional skills. The routing layer had to grow correspondingly. The MINOR bump rather than MAJOR reflects that no other skill composes *against* `code-clinic`, adding rows to its routing table does not break anything.

## [1.0.0], 2026-05-15

### Added

- Initial release. Single-page intake skill that triages a developer's request between `code-inspector` (single-change review and planning) and `code-fixer` (full-project quality engagement). Tier classifier handoff into `code-inspector/learner/QUICKSTART.md`.
- Provenance: created in response to a discoverability gap identified during adversarial review of `code-inspector` + `code-fixer`. Beginners did not know which of the two skills to invoke. The compromise that preserves the composition graph: a thin front-desk skill that routes.
- Out-of-scope by design: no scoring, no engagement-running, no rubric teaching. The skill is a router, nothing else.
