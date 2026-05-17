# Changelog — gymbuddy

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

- MAJOR: §1 (the writing-to-verifying shift thesis) changes. That thesis is the skill's organizing principle; breaking it means the rest of the skill stops cohering.
- MINOR: new prompt-hygiene patterns (§3), new drift signs (§7), new composition entries (§8).
- PATCH: wording, citation updates, example refinements.

## [2.0.0] — 2026-05-16 — Iron Law layering + composes-pin bump

MAJOR because composes pin to form-check changed from `>=2.0.0,<3.0.0` to `>=3.0.0,<4.0.0`.

- Added Iron Law: "NO AI-GENERATED CODE MERGED WITHOUT FRESH VERIFICATION EVIDENCE IN THIS SESSION."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.
- METR-2025 de-loaded (no longer load-bearing for magnitude); replaced with `LICHTENSTEIN-1982` + `KORIAT-BJORK-2005` for the established metacognitive-miscalibration phenomenon. METR-2025 retained as one preliminary RCT example with `[T1-verified, n=16, preliminary]` tags.
- Slopsquatting evidence strengthened: cross-replicated by Snyk + Aikido + Mend independent measurements, range 5–22%.
- AI-code security defects strengthened: cross-replicated across `PEARCE-2022`, `KHOURY-2023`, `ACM-COPILOT-SEC`, `MAJDINASAB-2024`.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed] — 2026-05-15

This skill was renamed from `ai-helper` to `gymbuddy` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `ai-helper.skill/` → `gymbuddy.skill/`
- `name:` frontmatter: `ai-helper` → `gymbuddy`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.0.0] — 2026-05-15

### Added

- Initial release. Nine sections covering the writing-to-verifying shift, when to use AI and when not, prompting hygiene, calibration applied to AI output, the destructive-suggestion protocol, the AI session as an artifact, drift signs, composition with the rest of the ecosystem, and anti-patterns.
- §1 establishes the organizing thesis: AI shifts work from writing to verifying, and many failure modes come from doing the prompting but skipping the verifying. METR-2025's perception-reality gap is the macro-scale evidence; this skill is the per-session corrective.
- §5 (destructive-suggestion protocol) is the anti-Replit/Lemkin section. When an AI suggests a destructive command, the protocol is: read aloud, read twice, ask "if this goes wrong, what is the recovery?", execute only if the recovery is immediately obvious.
- §7 (drift signs) is the longitudinal corrective. Self-check every 30 days; if two or more signs are present, do one substantial task per week without AI assistance to maintain the underlying skill.

### Rationale

AI assistants are now the dominant tool for the beginner persona, and the failure modes are well-documented but were not assembled in one place. METR-2025, USENIX 2025 slopsquatting, the Lovable BOLA incidents, the Replit/Lemkin destructive-action case — each maps to a specific point in the workflow this skill describes. The skill exists to make those connections explicit rather than asking beginners to derive them from scattered cautionary tales.

The drift framing (§7) treats cognitive offloading as a real and reversible pattern rather than a moral failing. The corrective is structural: maintain underlying skill through deliberate non-AI practice. The literature on cognitive offloading (Risko & Gilbert 2016; Sparrow et al. 2011 on the "Google effect") supports this framing.
