# Changelog — form-check

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: rubric weights change; threshold tier numbers change; vibe-safety bucket criteria change; required `composes` version bump for downstream skills.
- **MINOR**: new checklist added; new template; new multi-language file; new scale-up chapter.
- **PATCH**: citation fix; typo; doc-voice tweak; algorithm-spec clarification without semantic change.

Downstream skills (e.g. `code-fixer.skill`) pin a `composes.version` range. PATCH-level upstream changes are auto-compatible; MINOR triggers a recommended bump; MAJOR breaks the constraint.

## [3.1.0] — 2026-05-16 — Phase 9 token trim

MINOR (no breaking changes; compression only).

- `SKILL.md` trimmed from 290 → 240 lines (the `tests/test_skill_format.sh` cap), regaining the budget consumed by v3.0.0 Iron Law / Red Flags / Rationalizations / calibration-honesty / paradox additions.
- Compressed: Onboarding paths intro merged onto one line; How-to-invoke routing collapsed; Section 1 evidence bullets tightened; Section 4 refusal list folded to a paragraph; Section 5 prose beneath the calibration-honesty block compacted; Section 6 numbered list condensed (13 → 10 items, no semantic loss); Section 7 phases compressed; Section 9 evidence posture collapsed (was a 17-line list duplicating `references/notes.md`); Section 10 mini-runbook compressed (10 steps → 5); Section 11 anti-scope folded to one paragraph.
- **Verification harness at `/tmp/verify_trim.py`**: pre-trim snapshot + post-trim diff confirms 100% retention of citation tags (29), file references (30), required H2 sections (4), and 13 load-bearing verbatim anchors (Iron Law, Red Flags header, Rationalizations header, calibration-honesty `Below N=10:` / `N=10 to N=49:` / `N≥50:`, pure-refactor sub-row, TDD evidence caveat, all three component minima rows). Semantic concept retention (unique non-stopword tokens ≥4 chars): **99.81% (1076/1078)**. Two tokens dropped: `study`, `task` (sentence-glue, not load-bearing).
- **No content changes**, only compression. Iron Law block, Red Flags list, Rationalizations table, calibration-honesty quote block, and TDD evidence caveat are byte-identical to v3.0.0.
- All 13 form-check tests pass post-trim.

## [3.0.0] — 2026-05-16 — Evidence-base audit + Iron Law layering + pedagogy upgrades

This is a MAJOR bump because thresholds gained `(uncalibrated)` annotations and new gating semantics (advisory-only below N=10) — downstream `recovery.skill` composes-pin needs to bump to `>=3.0.0,<4.0.0`.

### Changed — citation hygiene (Phase 1)
- `references/notes.md` rewritten v3.0.0: every citation carries a tier tag per `~/Projects/palamedes/skill/references/source-grading.md` (`[T1-replicated]`, `[T1-verified]`, `[T1-mixed]`, `[T1-vendor, COI:X]`, `[T1-contested]`, `[T2-incident]`, `[T2-secondary]`, `[normative]`, `[stylistic-norm]`).
- New citation hygiene rules section: trace press releases to T1; demand effect size + CI; decline-effect prior; industry-funded adjustment per Lundh Cochrane; do not aggregate T3 by counting agreement; single low-N RCT cited at most once per skill.
- METR-2025 downgraded from load-bearing rhetoric to one preliminary RCT consistent with the established metacognitive-miscalibration phenomenon (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`). Cited at most once per skill.
- Dunning-Kruger 1999 dropped as load-bearing; `GIGNAC-ZAJENKOWSKI-2020` and `GIGNAC-2024` show D-K is mostly a statistical artifact.
- GitClear-2025 explicitly tagged `[T2-vendor, COI:GitClear, unreplicated]`.
- TDD evidence flagged `[T1-mixed]` per `RAFIQUE-MISIC-2013`, `KOLLANUS-2010`. Pair programming flagged with `HANNAY-2009` cost-vs-quality tradeoff.
- New citations added with full provenance: `KIRSCHNER-SWELLER-CLARK-2006`, `BISRA-2018`, `SINHA-KAPUR-2021`, `MARGULIEUX-CATRAMBONE-2016`, `JOENTAUSTA-HELLAS-2022`, `ROHRER-2012`, `CARVALHO-GOLDSTONE-2015`, `BJORK-BJORK-2011`, `GUSKEY-2010`, `HATTIE-TIMPERLEY-2007`, `SLAMECKA-GRAF-1978`, `BACCHELLI-BIRD-2013`, `COHEN-2010`, `PETROVIC-2018`, `BELLER-2016`, `KITCHENHAM-EFFECT-SIZE`, `LUNDH-COCHRANE`, `SIMMONS-2011`, `GELMAN-LOKEN-2013`, plus `SLOP-arXiv` cross-replication tags.

### Changed — Iron Law layering (Phase 3)
- Added Iron Law block at top of `SKILL.md`: "NO SHIPPING WITHOUT TIER-FLOOR SCORE *AND* PER-COMPONENT MINIMA MET. A HEADLINE PASS WITH A FAILED MINIMUM IS A FAIL."
- Added "Violating the letter of this rule is violating the spirit of this rule" framing.
- Added Red Flags list: thoughts that mean STOP and re-score.
- Added Rationalizations table: verbatim excuses with rebuttals.

### Changed — calibration threshold honesty (Phase 7)
- §5 thresholds annotated `(uncalibrated)` until N≥50 calibration-log entries with linked incident outcomes.
- Below N=10: `advisory` verdicts only; no ship/no-ship gating on headline number.
- N=10 to N=49: numeric verdicts permitted but tagged `(uncalibrated, N=<n>)`.
- N≥50: retiering required per `KITCHENHAM-EFFECT-SIZE` methodology.
- Mastery-learning anchor (`GUSKEY-2010` `[T1-replicated]`) cited as basis for tier-floor concept; specific thresholds remain operator wisdom.

### Changed — TDD evidence honesty (Phase 8)
- §1 test-as-spec rule annotated with empirical caveat: TDD evidence is mixed (`RAFIQUE-MISIC-2013`, `KOLLANUS-2010`); treat as discipline-shaping default with operator-wisdom backing, not as proven productivity lever.
- Added evidence-tagged paragraph on adjacent practices: code review (strong evidence per `BACCHELLI-BIRD-2013`), mutation testing (`PETROVIC-2018`), static analysis (`BELLER-2016`), pair programming (`HANNAY-2009` cost-vs-quality tradeoff).

### Changed — description hygiene (Phase 4)
- Frontmatter `description:` rewritten to triggers-only, third-person, ≤350 chars.
- Keyword stuffing relocated to `## Keywords for discovery` section in body.

### Changed — `learner/study_protocol.md` (Phases 5 + 6)
- Habit 3 (interleaving): added boundary conditions per `ROHRER-2012`, `CARVALHO-GOLDSTONE-2015` — works only for related-but-distinct concepts; does NOT work for unrelated topics or true beginners with no prior schema.
- Habit 4 (worked examples): anchored on `KIRSCHNER-SWELLER-CLARK-2006` "Why Minimal Guidance During Instruction Does Not Work"; added programming-specific subgoal-labeling extension per `MARGULIEUX-CATRAMBONE-2016`.
- Habit 5 (self-explanation): replaced Wylie & Chi 2014 with `BISRA-2018` meta-analysis (g=0.55, k=20 moderators).
- Habit 6 (productive failure): added explicit boundary conditions per `SINHA-KAPUR-2021`: prior knowledge floor, problem affordances, consolidating instructional follow-up. PF without these conditions is just failure.
- Habit 7 (calibration): replaced Dunning-Kruger anchor with `LICHTENSTEIN-1982` + `KORIAT-BJORK-2005`; added explicit note that D-K is mostly statistical artifact per `GIGNAC-ZAJENKOWSKI-2020` / `GIGNAC-2024`.
- New Habit 9: "Direct instruction for novices (the anti-discovery finding)" — anchored on `KIRSCHNER-SWELLER-CLARK-2006`. For learners without strong schema, unguided exploration underperforms direct instruction; do not invert the order for wholly novel concepts.
- New section: "The pedagogy paradox" — addresses the central design failure that AI assistants close the retrieval-practice / self-explanation / prediction loop *for* the learner, removing the conditions for learning. Names the protocol for AI-loaded vs. study-mode sessions; flags red flags for cognitive offloading.
- Updated retrieval prompts at end to cover the new boundary conditions.

### Changed — METR-2025 de-loading (Phase 2)
- Removed load-bearing METR-2025 citations from `SKILL.md §1, §9`, `learner/study_protocol.md`, `learner/QUICKSTART.md`, `learner/lessons/01_code_read_depth.md`, `learner/lessons/06_reversibility.md`.
- Replaced with anchor on the established metacognitive-miscalibration phenomenon (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`); METR-2025 retained as one preliminary example RCT (n=16, METR-self-redesigned-for-unreliability) but no longer load-bearing for magnitude.

### Methodology
This audit followed `~/Projects/palamedes/skill/references/replication-and-validity.md` + `source-grading.md`. Adversarial review of the citation triage was performed in three passes (primary-source check, known-best-practices check, falsifier generation). Verdict: ~85% confidence in the triage; 7 papers verified via abstract or summary; 1 correction made (Causey 2017 → Rafique & Mišić 2013 for TDD meta-analysis). Audit summary in a private gym-skills evidence-audit document (working notes) (deferred — to be written if needed).

## [Renamed] — 2026-05-15

This skill was renamed from `code-inspector` to `form-check` as part of the gym-metaphor
migration. The 8-skill ecosystem moved from bureaucratic category labels
(`code-clinic`, `code-inspector`, etc.) to plain-English gym vocabulary
(`warmup`, `form-check`, `recovery`, `PR`, `diet`, `safetybar`, `gymbuddy`,
`program`) so the names are easier to recall. Contents are unchanged;
only the name on the door changed.

- Directory: `code-inspector.skill/` → `form-check.skill/`
- `name:` frontmatter: `code-inspector` → `form-check`
- All cross-references in other skills' `composes:` blocks updated.

The H1 of this CHANGELOG and earlier version entries retain the old name
deliberately, for historical clarity. The rename plan and full rationale
are in a private rename-plan document (working notes).

## [2.1.1] — 2026-05-15

### Changed — maintainability hardening

- `tests/test_cross_refs.py` added — promoted the wave-9 ref-check from a session artifact (`code-skills-overhaul/wave9-…/ref_check.py`) into a permanent skill test. Closes the gap where the cross-skill ref check could go stale or be lost. Self-discovers `code-inspector.skill` + `code-fixer.skill`; skips templates/, examples/, README_archetypes/, runbooks/, and consumer-side placeholder filenames.
- `tests/run_all.sh` added to both skills — single entry point that clears `__pycache__` (pycache poisoning bit us during v2.1.0 implementation), discovers every `tests/test_*.{sh,py}` by glob, prints per-test PASS/FAIL, and prints re-run-with-output hints for failures. Auto-wires new tests dropped into `tests/`.
- `tests/test_learner_rubric_drift.py` added — verifies each lesson in `learner/lessons/` is consistent with `rubrics/confidence_score.md`. Checks frontmatter `rubric_component:`, filename↔component-name alignment, and weight numbers cited in lesson prose. Closes the v2.1.0 documented gap: "no automated check enforces lesson↔rubric weight consistency."
- `learner/cautionary_tales.md` — every incident's References block now uses backticked citation tags (e.g. `WIZ-SHAIHULUD-1`, `SLOP-USENIX`, `METR-2025`, `POWERPAGES-APPOMNI-2023`, `LEFT-PAD-2016`) instead of free-text prose. `tests/test_citations.py` now enforces that every referenced tag exists in `references/notes.md`, catching incident-citation drift.
- `references/notes.md` — added `POWERPAGES-APPOMNI-2023` and `LEFT-PAD-2016` so the cautionary-tales references resolve to tagged entries. Total tracked tags: 45 (was 43).

### Why a PATCH bump
None of the above changes the rubric, vibe-safety buckets, threshold tiers, or composes-version compatibility. Test harness improvements + reference-tag tightening + no semantic change → PATCH per the SemVer rules above.

## [2.1.0] — 2026-05-15

### Added — learner track (persona-driven enhancements)
- `learner/QUICKSTART.md` — single-page on-ramp: glossary, three-question tier classifier, three graduated safety floors (Floor 1 / 2 / 3 by reversibility tier), pointers to the rest of the learner track, behavioral graduation signals.
- `learner/token_handling_primer.md` — eight-habit primer for preventing token leaks, with "you have already leaked one" framing, file-permissions guidance, secret-scanning hooks, and a five-step incident-response runbook for `git push`-after-leak.
- `learner/cautionary_tales.md` — seven real incidents in plain language: Replit production-DB deletion, Shai-Hulud npm worm chronology, slopsquatting (USENIX 2025), Lovable BOLA/PII exposure, METR-2025 perception–reality gap, low-code default-public exposure incidents, left-pad / supply-chain fragility. Each entry ends with the actionable lesson and links to the relevant checklist.
- `learner/first_pr_walkthrough.md` — end-to-end worked example (adding `--quiet` to a CLI), narrating decision-making, CLAUDE.md usage, test-as-spec, prompt construction, diff-reading, hallucination check, blast-radius assessment, doc updates, commit message, and the "what to write down for next time" step.
- `learner/lessons/03_hallucination_check.md` — lesson on rubric component 3 (highest-impact-per-minute habit). Four-signal verification (registry / author / 30-day age / docs match), failure modes, exercises.
- `learner/lessons/01_code_read_depth.md` — lesson on rubric component 1, anchored in METR-2025. Read-the-whole-diff and read-the-callers protocols, scope-out detection, exercises.
- `learner/lessons/02_test_verification.md` — lesson on rubric component 2. Test-as-spec, before/after comparison, mutation testing, common failure modes.
- `learner/lessons/06_reversibility.md` — lesson on rubric component 6. Three-way classification (idempotent/reversible/irreversible), gate selection (human approval / dry-run / explicit confirm / backup-first / staged rollout), rollback-before-forward rule, six failure modes.
- `learner/MODE_CONFIG.md` — forward-looking spec for `.code-inspector.yaml` config (`mode: learner` vs `mode: default`). Honest about current harness support gap; documents the prompt-based fallback and the graduation signals.
- `SKILL.md` "Onboarding paths" section — six pointers into the learner track plus a non-negotiable rule for the token primer. Acknowledges the senior-engineer voice shift after the section.

### Changed
- `tests/test_skill_format.sh` line cap raised from 220 → 240 to accommodate the onboarding-paths section. Allowed-prefix list extended with `learner/` so the ref-check verifies learner files exist when SKILL.md cites them.
- `tests/test_skill_version_compat.py` upgraded from string-match-only to also verify that pinned components named in `code-fixer.skill/SKILL.md` exist on disk *and* their frontmatter `version:` declarations match the pinned versions. (Bug #3 from the persona-driven adversarial review.)
- `rubrics/confidence_score.md` tier-count row aligned with `SKILL.md` Section 5 (3 tiers + Pure-refactor sub-row, not 4 tiers). (Bug #1 from the persona-driven adversarial review.)
- `tests/test_banned_vocab.sh` rewritten as a thin wrapper around `tests/test_banned_vocab.py`. The Python implementation narrows the base regex to unambiguous AI-marketing terms and adds a quoted-form exclusion (so meta-discussion of banned words in the skill's own prose doesn't trigger the test).
- `tests/test_citations.py` `SKIP_PREFIX` list extended to reduce false positives on common non-citation patterns (CWE sub-IDs, OWASP sub-IDs, license identifiers, ticket placeholders, etc.).

### Mentor-voice notes
- The learner track is opt-in via `learner/MODE_CONFIG.md`; the senior-engineer voice in `SKILL.md` and the rubrics is unchanged. No backwards-incompatible shift in tone.
- The lessons cite back to existing rubric components rather than creating a parallel rubric. Single source of truth, two reading depths.
- Cautionary-tale framing uses real incidents rather than abstract risk catalogs because the persona internalizes stories and *reasons backward* from them faster than from principles.

## [2.0.0] — 2026-05-14

### Changed (BREAKING)
- Confidence-score threshold is now **tiered by reversibility** (vibe-dangerous ≥95, vibe-careful ≥90, vibe-safe ≥80, refactor ≥70) with per-component minima, replacing the flat 93.
- Confidence-score components rebalanced: 9 components (added blast-radius and threat-model; reweighted hallucination-check upward).
- Stack-decision rule now requires a citation OR explicit `[normative — operator wisdom]` tag per row. Adds Java/Kotlin/Spring as a gated row.
- Vibe-safety map adds a fourth bucket: **vibe-impossible** (qualified human author required).
- deAI rules now apply per-archetype (overlays for API-reference / runbook / README / architecture / changelog / roadmap / glossary / source-comments) instead of one voice across all docs.
- Banned-vocab list expanded; `tests/test_self_voice.sh` enforces the skill obeys its own rules.
- `SKILL.md` capped at ≤220 lines; sub-content lazy-loaded.

### Added
- `agent-runtime/harness_contract.md` — capability allowlist by tier, state ledger schema, rollback contract, scope confinement, reasoning provenance tags. Addresses OWASP-LLM06 (Excessive Agency).
- `agent-runtime/prompt_injection.md` — defense layered approach. Addresses OWASP-LLM01.
- `checklists/owasp_llm_top10.md` — OWASP LLM Top 10 (2025).
- `checklists/owasp_api_top10.md` — OWASP API Top 10 (2023).
- `checklists/owasp_web_top10.md` — OWASP Top 10:2025 (web).
- `checklists/threat_model_stride.md` — STRIDE process.
- `checklists/threat_model_linddun.md` — LINDDUN privacy process.
- `checklists/fitness_functions.md` — architectural fitness functions chapter (lint-class default; runtime-class scale-up gated).
- `checklists/accessibility_wcag22.md` — WCAG 2.2 walk.
- `checklists/supply_chain_slsa.md` — slopsquatting, SLSA mapping, Shai-Hulud chronology, runbook reference.
- `checklists/deprecation_policy.md` — RFC 8594 + sunset timeline + per-language deprecation marks.
- `checklists/skill_antipatterns.md` — failure modes when applying this skill.
- `checklists/INDEX.md` — decision tree to leaf checklists; prevents walking-every-checklist fatigue.
- `multi-language/matrix.md` + `multi-language/python.md` + `multi-language/typescript.md` + `multi-language/java.md` + `multi-language/go.md` + `multi-language/rust.md` — full per-language tooling depth (test runner, mutation, lint, audit, lockfile, fuzz, format, secrets, IaC, SBOM, concurrency).
- `scale-up/` annex with `scale-up/when_to_activate.md` (gate criteria + FinOps gate); chapter skeletons `scale-up/distributed_systems.md`, `scale-up/multi_region.md`, `scale-up/soc2_iso27001.md`, `scale-up/service_mesh.md`, `scale-up/event_sourcing_cqrs.md`, `scale-up/spring_kotlin_jvm.md`.
- `templates/AGENTS.md_scaffold.md` (alias for hosts using AGENTS.md filename).
- `templates/threat_model.md`, `templates/runbook.md`, `templates/SECURITY.md_template.md`, `templates/CHANGELOG_template.md`, `templates/ARCHITECTURE.md_template.md`, `templates/ROADMAP.md_template.md`, `templates/glossary.md_template.md`.
- `templates/README_archetypes/{cli,library,service,monorepo}.md` — archetype-driven README templates.
- `templates/runbooks/{supply_chain_compromise,incident_response}.md`.
- `templates/calibration_log_render.md` — schema + jq queries for `.code-fixer/calibration.jsonl`.
- `templates/forcing_constraint_adr.md` — ADR template that gates scale-up annex.
- `templates/prompt_versioning.md` — SemVer for prompts; eval-gate semantics.
- `tools/` (with `docs/<tool>_algorithm.md` markdown equivalents): `tools/blast_radius.py`, `tools/check_forcing_constraint.sh`, `tools/scan_prompt_injection.sh`, `tools/pin_skill_version.sh`.
- `tests/` skill self-tests with fixtures: `tests/test_banned_vocab.sh` (+ `tests/test_banned_vocab.py`), `tests/test_rubric_arithmetic.py`, `tests/test_citations.py`, `tests/test_skill_format.sh`, `tests/test_scaleup_gate.sh`, `tests/test_blast_radius.py`, `tests/test_self_voice.sh`, `tests/test_skill_version_compat.py`. Plus `tests/integration/smoke_real_project.md`.
- `examples/` worked examples: forcing-constraint ADR, full engagement trace.

### Changed
- `rubrics/stack_decision.md` rewritten with multi-language anchor or `[normative]` tag per row; Java/Kotlin/Spring added as gated row.
- `rubrics/confidence_score.md` rewritten with tiered thresholds, 9 components, mutation-score targets per language, calibration-log requirement.
- `rubrics/vibe_safety_map.md` rewritten with vibe-impossible bucket and per-archetype examples.
- `checklists/bug_class_audit.md` rewritten: cross-references to OWASP-LLM/API/Web; AI-PR shapes anchored to GITCLEAR-2025 / ACM-COPILOT-CORRECT / ACM-COPILOT-SEC.
- `checklists/preflight_10q.md` rewritten: data classification added to Q4; multi-language Q5; LLM contract Q7 references prompt_versioning + harness_contract.
- `checklists/smell_catalog.md` rewritten: archetype-segmented (CLI / web / library / monorepo / LLM-bearing); generic project examples (per-archetype examples in `examples/`).
- `templates/CLAUDE.md_scaffold.md` rewritten: multi-language; SLSA target; agent-runtime contract section.
- `templates/review_gate_checklist.md` rewritten: STRIDE / mutation-score / hallucination-check / fitness-function items added.
- `templates/test_as_spec.md` rewritten: multi-language patterns; mutation testing; fuzzing.

### Fixed
- **Citation integrity**: METR-2025 generalization caveat made explicit; slopsquatting framing sharpened (model-hallucination rate × attacker-publishing rate × dev-copy-paste); 75% logic-defect claim removed (citation laundering); Lovable 10.3% claim removed (no traceable primary); Shai-Hulud chronology updated to Sept 2025 / Nov 2025 / May 2026 with Wiz / Unit 42 / CISA / Microsoft sources.

### Removed
- Original research/notes.md location (renamed to `references/notes.md`; old name had drift connotation).
- Inlined named-projects examples from main checklist text (moved to `examples/per_archetype_smells.md`).
- `*.skill` zip artifacts from source tree (build outputs do not belong in source).

### Security
- New supply-chain runbook (`templates/runbooks/supply_chain_compromise.md`) with Shai-Hulud-class playbook including token-rotation list, exfil-repo audit, customer-comm template.

### Self-review polish (post-implementation, still 2.0.0)

Two fresh adversarial-review loops surfaced these fixes; all skill self-tests still pass.

- **Section numbering** in `SKILL.md`: Mini-runbook is now Section 10; Anti-scope is Section 11 (was unnumbered + Section 10).
- **Tier axis disambiguation** in `SKILL.md` Section 5: clarified that vibe-impossible is a refusal classification in `rubrics/vibe_safety_map.md`, not a score-threshold tier; "Pure refactor" is now a sub-row of vibe-safe with explicit behavior-preservation condition.
- **Cross-skill path references**: rewrote `code-inspector/...` → `code-inspector.skill/...` and `code-fixer/...` → `code-fixer.skill/...` throughout (12 files; the actual directory names carry the `.skill` suffix).
- **CHANGELOG bare-filename refs**: expanded to full skill-relative paths so readers can navigate (e.g. bare *python.md* → `multi-language/python.md`; bare *blast_radius.py* → `tools/blast_radius.py`; etc.).
- **REFERENCES.md** in `SKILL.md` Section 9: qualified as living in the upstream development bundle, not shipped with the skill.
- **`examples/per_archetype_smells.md`**: created (was referenced from `checklists/smell_catalog.md` and CHANGELOG but missing).
- **Nonexistent-tool refs**: *tools/check_boundaries.py* and *tools/check_module_boundaries.py* are project-local scripts the consumer creates, not skill files; prose clarified and backticks dropped to italics.
- **Worked-example fictional filenames** in `rubrics/confidence_score.md` (*cli.py*, *auditor.py*): italicized instead of backticked to remove false-positive reference signals.
- **Frontmatter coverage**: added minimal frontmatter to 7 files that lacked it (`checklists/INDEX.md` — load-bearing because `code-fixer` pins it; `docs/*_algorithm.md` × 3; `examples/forcing_constraint_adr_example.md`; `templates/MADR_short.md`; `tests/integration/smoke_real_project.md`).

### Tooling test depth (post-implementation, still 2.0.0)

Wave-9 follow-up: lift the tool scripts from "smoke-tested" to "mutation-equivalent test coverage" before any real-world use.

- **`tests/test_blast_radius.py`** expanded from 5 → 35 cases. Every `PRIVILEGE_PATTERNS` row covered (internal / public-api / write-effect-db / write-effect-migrations / write-effect-schema / write-effect-admin / secret-handling-path / secret-handling-filename × 4 keywords / styles / docs). First-match precedence verified (api beats admin, secret beats docs). `env_var_bonus` covered for every supported runtime (Python `os.environ`, Python `getenv`, Node `process.env`, Java `System.getenv`, PHP `$_ENV[`). `call_paths_estimate` empty-input and irrelevant-extension paths. `compute` empty-diff short-circuit + score-clamp + components-schema. CLI main: non-existent path → exit 2; valid empty dir → exit 0 + valid JSON.
- **`tests/test_scan_prompt_injection.sh`** added (9 assertions). Each of the 11 patterns in a positive .md fixture → exit 1 with hits. Negative corpus of plausible technical writing → exit 0. Excluded subdirs (`references/`, `examples/`, `tests/fixtures/`) carrying injection content → exit 0 (excludes honored). Mixed dir → exit 1 with needle found. Non-existent path → exit 2. Non-markdown content (`.py`, `.txt`) ignored.
- **`tests/test_forcing_constraint.sh`** added (12 assertions). Non-existent repo, empty `docs/adr/`, ADRs without `type: forcing-constraint`, valid ADR (hyphen-prefixed keys), `status: proposed` (rejected), missing `constraint_class` (exit 2 malformed), multiple ADRs with one valid (exit 0), no `Status` line (exit 2), case-insensitive `Status: ACCEPTED`, YAML-style lowercase keys, non-`.md` files in `docs/adr/` ignored.

Test count: 11 → 13 test files; combined assertion count: ~10 → ~70 individual cases.

## [1.0.0] — 2026-04-30

### Initial release
- Senior-engineer / tech-lead posture skill for vibe-coding loop.
- 7-component confidence rubric; flat 93 threshold.
- Vibe-safety 3-bucket model.
- Stack decision rule (TS / Python / Go / Rails defaults).
- CWE Top-25 + AI-PR-specific bug shapes.
- 10-question preflight checklist.
- MADR-short + CLAUDE.md scaffold.
- 4 specific QA-portfolio project specializations.
