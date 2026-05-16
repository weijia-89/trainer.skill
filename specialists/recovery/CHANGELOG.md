# Changelog — recovery

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: workflow DAG topology changes; engagement output schema changes; pinned `code-inspector` MAJOR upgrade with breaking changes consumed.
- **MINOR**: new phase added; new adversarial question; new launch-ready DoD section; new template.
- **PATCH**: citation, typo, doc-voice tweak, prompt-text refinement.

## [3.0.0] — 2026-05-16 — Iron Law layering + composes-pin bump to form-check@>=3

MAJOR because composes pin to form-check changed from `>=2.0.0,<3.0.0` to `>=3.0.0,<4.0.0`.

- Added Iron Law: "NO LAUNCH-READY VERDICT WITHOUT TIER-FLOOR MET *AND* `.recovery/state.jsonl` COMPLETE."
- Added "Violating the letter is violating the spirit" framing; Red Flags list; Rationalizations table.
- Description hygiene: triggers-only frontmatter; keyword block relocated to `## Keywords for discovery` body section.
- Composes-pin: form-check `>=3.0.0,<4.0.0`; `references/notes.md@3.0.0` added to pinned components.
- Below `form-check`'s calibration N=10, recovery renders `advisory` only — not launch-ready.

Full audit: `~/Projects/reviews/GYM_SKILLS_EVIDENCE_AUDIT_2026-05-16.md`.

## [Renamed] — 2026-05-15

This skill was renamed from `code-fixer` to `recovery` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-fixer.skill/` → `recovery.skill/`
- `name:` frontmatter: `code-fixer` → `recovery`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in `~/Projects/reviews/RENAME_PLAN_2026-05-15.md`.

## [2.0.0] — 2026-05-14

### Changed (BREAKING)
- Composes `code-inspector@>=2.0.0,<3.0.0` (was unpinned in v1).
- Engagement-level confidence rubric rebalanced: 11 components total (9 inherited from code-inspector at 0.9× weights + 2 code-fixer-specific at 10 weight units).
- Workflow restructured from waterfall to **DAG** with explicit activation criteria per phase (`workflow/workflow_dag.md` is canonical; SKILL.md and other workflow files reference by phase ID).
- `templates/deai_rules.md` introduces **per-archetype overlays** (api-reference / readme / changelog / architecture / runbook / glossary / source-comments / roadmap). One-voice-everywhere is removed.
- `templates/doc_voice.md` defines voice per archetype; uniform docstring shape required for API reference (Sphinx/typedoc/Javadoc/godoc/rustdoc compatibility).
- `workflow/adversarial_questions.md` expanded from 5 to **12** axis-segmented questions.

### Added
- Engagement output spec: `.code-fixer/state.jsonl` + `.code-fixer/calibration.jsonl` + `.code-fixer/summary.md`.
- Idempotent re-runs (skips phases whose inputs haven't changed; force via `--rerun=phase`).
- Abort protocol with structured exit (`Section 9` of SKILL.md).
- `workflow/phase_prompts.md` with env-agnostic, parameterized output paths (no hardcoded `/sessions/...` paths).
- `examples/full-engagement-trace.md` worked example.
- `tests/test_deai_regex.py` + `tests/test_workflow_idempotent.sh` skill self-tests.
- README.md, CONTRIBUTING.md, LICENSE.

### Changed
- `rubrics/code_fixer_confidence.md` rewritten as a composition over duplication.
- `checklists/launch_ready.md` rewritten with multi-language tooling and 11 sections (incl. agent-runtime contract, accessibility, compliance hooks).
- `workflow/phase_prompts.md` rewritten env-agnostic.

### Fixed
- Hardcoded `/sessions/.../scratch/...` paths replaced with parameterized `{{state_dir}}`.

### Removed
- Original named-projects engagement traces (moved to `examples/`).
- v1 `*.skill` zip artifact from source tree.

### Self-review polish (post-implementation, still 2.0.0)

Two fresh adversarial-review loops surfaced these fixes; all skill self-tests still pass.

- **Section 3 weight mismatch** in `SKILL.md`: component 10 (Workflow completeness) corrected to weight 7 (was 5); rubric file `rubrics/code_fixer_confidence.md` was already correct at 7.
- **Cross-skill path references**: rewrote `code-inspector/...` → `code-inspector.skill/...` throughout (12 files); the actual directory names carry the `.skill` suffix.
- **Bare-filename refs**: expanded bare *workflow_dag.md* → `workflow/workflow_dag.md` in `CONTRIBUTING.md`; bare *confidence_score.md* → `code-inspector.skill/rubrics/confidence_score.md` in `rubrics/code_fixer_confidence.md`.
- **Frontmatter coverage**: added minimal frontmatter to `examples/full-engagement-trace.md`.

## [1.0.0] — 2026-04-30

### Initial release
- 7-phase waterfall workflow.
- Composition with code-inspector + deAI (informal text reference).
- 9-component engagement-level rubric.
- 5-question adversarial review.
- Launch-ready DoD per project.
