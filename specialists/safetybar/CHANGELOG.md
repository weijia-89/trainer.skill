# Changelog, safetybar

Format: Keep a Changelog with SemVer.

## SemVer rules for this skill

- MAJOR: §1 (the "I think I lost my work" protocol) changes its recovery order. That order is muscle memory; breaking it costs users data.
- MINOR: new commands documented in §2, new conflict-resolution patterns in §3, new branch-surgery patterns in §5.
- PATCH: wording, example refinements, clarifications.

## [1.1.0], 2026-05-16. Iron Law layering

MINOR (no breaking changes; added discipline content).

- Added Iron Law: "NO DESTRUCTIVE GIT COMMAND BEFORE READING ITS RECOVERY PATH IN THIS FILE."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.

Full audit: a private gym-skills evidence-audit document (working notes).

## [Renamed], 2026-05-15

This skill was renamed from `git-recovery` to `safetybar` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `git-recovery.skill/` → `safetybar.skill/`
- `name:` frontmatter: `git-recovery` → `safetybar`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [1.0.0], 2026-05-15

### Added

- Initial release. Seven sections covering the lost-work protocol, undo paths for seven destructive commands, conflict resolution, detached HEAD, branch-surgery patterns, anti-patterns, and prevention habits.
- §1 establishes reflog-first as the universal recovery strategy. Nothing in §2 contradicts §1; every undo path eventually points back to the reflog.
- The seven destructive commands covered in §2 are the ones beginners most commonly run before realizing what they do: `reset --hard`, `push --force`, `clean -fd`, `branch -D`, `checkout -- <file>`, `rebase -i`, `stash drop` / `stash clear`. For each, the recovery path appears before the safer alternative; this ordering reflects the fact that users read this skill *after* they have already run the command.
- Composition: no `composes:` entries because the skill is self-contained. Other skills (`code-operator`, `code-deployer`) reference git-recovery for rollback mechanics.

### Rationale

Git mistakes are the highest-frequency low-grade emergency for beginners, and existing git documentation assumes you already know what is happening. The "I think I lost my work" protocol is the single most-asked beginner question; reflog-first is the single most-effective answer. The skill exists to put both in one place.
