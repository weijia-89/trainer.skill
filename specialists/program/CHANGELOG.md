# Changelog, program

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

- MAJOR: the four-question intake or the one-page-spec output shape changes in a way that breaks downstream consumers (`code-inspector/plan-new-app` reads the spec).
- MINOR: additional intake questions, new spec sections, new anti-patterns documented.
- PATCH: wording, examples, citation fixes.

## [2.0.0], 2026-05-16. Iron Law layering + composes-pin bump

MAJOR because composes pin to form-check changed from `>=2.0.0,<3.0.0` to `>=3.0.0,<4.0.0`.

- Added Iron Law: "NO IMPLEMENTATION SKILL INVOKED UNTIL THE ONE-PAGE SPEC HAS KILL CRITERIA AND THREE NON-GOALS."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed], 2026-05-15

This skill was renamed from `code-planner` to `program` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-planner.skill/` → `program.skill/`
- `name:` frontmatter: `code-planner` → `program`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.0.0], 2026-05-15

### Added

- Initial release. Four-question intake (one-sentence statement, first user, kill criteria, deliberate non-goals) producing a one-page spec template that hands off to `code-inspector/plan-new-app`.
- Anti-patterns section covering the spec-as-novel, the phase-2 trap, the hypothetical-user, greenfield-vs-rebuild confusion, and skipping kill criteria.
- Composition diagram showing where `code-planner` sits relative to the rest of the eight-skill ecosystem.

### Rationale

The May 2026 SDLC-gap analysis (`code-inspector/CHANGELOG.md` 2.1.x) identified pre-build ideation as a real gap for beginners. Symptom: developers spend weeks building the wrong thing because they never wrote down what "right" was. The forcing function this skill provides is the one-page spec artifact, a beginner cannot complete the skill without producing it.

The four questions are deliberately spec-shaped rather than ideation-shaped. Brainstorming has its own tools (a notes app, a conversation, a walk). This skill begins after brainstorming and ends with handoff to `code-inspector`.
