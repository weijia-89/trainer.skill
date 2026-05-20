# Changelog

All notable changes to the `trainer` skill will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to [Semantic Versioning](https://semver.org/) with the rules below.

## SemVer rules for this skill

- **MAJOR**: routing decision flow changes; the specialist gym-skills list gains or loses entries; teaching-responsibility tier semantics change.
- **MINOR**: new sync target added; a specialist gym-skill's invocation pattern is updated; new section added without changing existing semantics.
- **PATCH**: typo fix; clarification without semantic change; sync-mechanic improvement.

## [0.9.1] (2026-05-20): Decision-presentation template, anti-patterns + self-check + tightened low-stakes scope

**PATCH per SemVer rules.** Wording-only additions to the v0.9.0 Decision-presentation template subsection. No new behavior beyond what v0.9.0 already added; no routing change. Closes the failure mode where a Cascade session ships formally-compliant decision blocks that pass structural review while delivering zero decision support to the operator.

### Added

- **Anti-patterns list** under the format block. The template explicitly refuses four shapes:
  - Bullets that name a dimension without filling it.
  - Recommendation that paraphrases the per-option bullets.
  - "Both have tradeoffs" framing in the context paragraph.
  - Low-stakes label applied to decisions whose downstream consequences are unsurfaced.
- **"Inherits from Communication discipline rules above"** paragraph cross-referencing the parent Jargon / Interiority / Verbosity rules. An agent reading just the subsection still picks up parent-rule teeth (Interiority's "what you didn't weigh hard enough" is the recommendation-block expectation).
- **Self-check sentence** that Cascade applies to its own draft before posting: "Could the operator decide reading only this block, without scrolling to related artifacts or asking a follow-up?" Converts formal compliance into substantive compliance.

### Changed

- **Tightened low-stakes scope definition.** v0.9.0 defined "low-stakes" only as "operator could resolve in under thirty seconds" (an agent's subjective time estimate). v0.9.1 adds three content gates: reversible, single domain affected, no interaction with active rules or in-flight work. All four conditions must hold; if any one is uncertain, the full template applies.
- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.9.1.

### Why PATCH not MINOR

- Wording-only clarification under an existing subsection; no new subsection added.
- No routing decision flow change; no new behavior the trainer enforces at session start beyond what v0.9.0 already added.
- v0.9.0 added the subsection (MINOR); v0.9.1 tightens its quality bar without adding structure (PATCH).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; subsection extended + version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp)

### Why this shipped

Wei's same-session followup directive after v0.9.0 landed: "ensure the decision template is not superficial." Adversarial review surfaced five superficiality risks; v0.9.1 closes four (anti-patterns, parent cross-reference, self-check, tightened scope). Risk 5 (worked-example pair) deferred to v0.9.2 if empirically needed; in the meantime the slip-past output drafted in the review session illustrates the bad-pattern anchor.

## [0.9.0] (2026-05-20): Decision-presentation template under Communication discipline

**MINOR per SemVer rules.** Communication discipline gains a new subsection (Decision-presentation template) plus a one-sentence cross-reference from the existing "Decisions, surfaced visibly" bullet. The new subsection codifies the format Cascade uses when surfacing multi-option decisions. The shape is a bolded question with two or three sentences of context, per-option bullets covering whichever grounding dimensions apply (reasons, rationale, roadmap impact, interactions, example), and a bolded recommendation whose reasoning does not duplicate the per-option bullets.

### Added

- **`### Decision-presentation template` subsection** under "Communication discipline" in canonical SKILL.md. Sits after the bulleted discipline list, before "What the trainer is NOT". Includes an explicit scope clause naming what the template covers (in-conversation multi-option surfacing) and what it does not (proposal artifacts, session logs, status updates, sub-thirty-second confirmations). The per-option bullet list is explicitly marked "use whichever apply" so single-stream decisions are not forced to manufacture cross-stream interaction notes.
- **Cross-reference from the line-235 "Decisions, surfaced visibly" bullet** to the new subsection. Existing bullet text preserved; one sentence added pointing readers at the template format.

### Changed

- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.9.0.
- **Soft line cap in `scripts/verify_trainer_sync.sh`** bumped from 280 to 320 to accommodate the new subsection (approximately 35 lines added).

### Why MINOR not PATCH

- Adds new behavior (a load-bearing artifact-shape rule that Cascade applies at decision-surfacing moments).
- Adds a new subsection that the existing "Decisions, surfaced visibly" bullet now cross-references rather than wholly contains.
- PATCH is reserved for renames, typos, sync-mechanic improvements, and wording-only clarifications. The v0.8.0 dispatch-graph sub-clause is the matching precedent for the MINOR call: it also added a sub-clause under existing structure and introduced new operational behavior without changing routing.

### Why MINOR not MAJOR

- Routing decision flow unchanged.
- Specialist gym-skills list unchanged (still 9).
- Teaching-responsibility tiers unchanged.
- Coaching stance, Iron Laws, Red Flags, and Rationalizations table all byte-identical to v0.8.0.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; new subsection, line-235 cross-reference, version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (soft line cap bump)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical via skill-sync)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp via skill-sync)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp via skill-sync)

### Companion operator-domain steps shipped alongside this version

- Delete `MEMORY[1adcc98e]` ("Inline questions with rationale"). The new SKILL.md subsection structurally supersedes the memory; keeping both creates duplicate discipline that eventually disagrees. Operator runs the deletion via Cascade memory tooling at ratification.
- Run `skill-sync` after canonical edit to propagate to the three mirrors.
- Run `~/Projects/trainer.skill/scripts/bundle_specialists.sh` per the standing discipline of refreshing the bundle after every trainer canonical edit (this version does not affect bundled specialists, but the discipline of running the bundle script remains the safe default).
- Run `bash ~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` to confirm all invariants pass post-edit.

## [0.8.0] (2026-05-19): Dispatch-graph-before-dispatch iron-law sub-clause

**MINOR per SemVer rules.** Adds a new sub-clause under the "Iron Law: plan first, implement second" section: the plan-first discipline extends to the dispatch graph itself. Before any multi-agent batch is generated, a daily-log manifest must exist at `<project>/localonly/daily/<YYYY-MM-DD>.md`, validated by `superset`, with all dependency edges surfaced to the user. Cascade auto-drafts the manifest on dispatch-intent triggers; runs a self-adversarial review pass using superset's falsifier checklist plus a form-check adversarial-review against its own draft; surfaces validated manifest plus findings before generating per-agent prompts.

### Added

- **`### Dispatch graph before dispatch` sub-clause** under "Iron Law: plan first, implement second" in canonical SKILL.md. Names the trigger phrases that violate the iron law ("just dispatch them, I'll review later"; "skip the manifest this time"; etc.). Names the two anchor incidents: mailchimp 2026-05-18 duplicate dispatch (Agent B); buds 2026-05-19 f-droid research and LICENSE edit dispatched in parallel without a producer-consumer link. Also names the three-layer agent architecture (orch 1-day, meta 1-week, worker per-task) at a brief level; routes to `superset.skill` for operational detail.

### Changed

- **Soft line cap in `scripts/verify_trainer_sync.sh`** bumped from 240 to 280 to accommodate the new sub-clause (~22 lines added).
- **Canonical, Claude mirror, Cursor trigger, Windsurf trigger** version stamps updated to v0.8.0.
- **New invariant 9 in `scripts/verify_trainer_sync.sh`** (script-tooling-only change, no SKILL.md content change, no version bump). Runs the superset falsifier harness at `$HOME/Projects/superset.skill/scripts/falsifier-harness/run-all.sh` and FAILs the verify pass if the harness exits non-zero. Falls back to WARN + skip if the harness script is not present (trainer can theoretically release without superset bundled, though current bundle ships it). errexit suspension around the harness invocation so a harness failure produces full diagnostic output (the failing test name plus the validator's stderr JSON) rather than silently exiting. Tested both positive (clean baseline: 6 hypotheses verified, exit 0) and negative (corrupted valid-baseline fixture: invariant 9 FAILS with full diagnostic including which test failed and which falsifier the validator raised). The harness regression is now part of every bundle-refresh verify gate.

### Why MINOR not PATCH

- Adds new behavior (auto-invoke + self-adversarial review on dispatch triggers).
- Adds a new iron-law sub-clause that route-corrects on specific user phrases.
- PATCH would be wording-only; this introduces a new rule.

### Why MINOR not MAJOR

- Routing decision flow unchanged.
- Specialist gym-skills list unchanged (still 9).
- Teaching-responsibility tiers unchanged.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (canonical; new sub-clause + version bump)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (line-cap bump)
- `~/.claude/skills/trainer/SKILL.md` (Claude mirror; resynced byte-identical)
- `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger; version stamp)
- `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger; version stamp)

### Downstream changes shipped alongside this version

- `superset.skill` v0.4.0 (sibling release): adds daily-log-driven dispatch section, promotes M6/M11/M12 to High, adds H14 (artifact-existence) and H15 (daily-log-precondition) falsifiers, ships new `templates/daily-log.md` and `templates/high-stakes-list.yaml`. See `superset.skill/CHANGELOG.md` v0.4.0 entry.

## [0.7.1] (2026-05-18): Rename 9th specialist `ancillary` → `superset` for gym-family coherence

**PATCH per SemVer rules.** The 9th specialist added in v0.7.0 under the name `ancillary` is renamed to `superset` so its label fits the gym-themed naming convention shared with the other eight specialists (`form-check`, `program`, `warmup`, `safetybar`, `recovery`, `gymbuddy`, `diet`, `pr`). The routing flow, coaching stance, Iron Laws, and the specialist's behavior are byte-equivalent to v0.7.0; only the surface name changed.

### Changed

- **Canonical sibling directory:** `~/Projects/ancillary.skill/` → `~/Projects/superset.skill/` (full rename with internal references updated; old name preserved in CHANGELOG history of that repo and in the routing-table parenthetical of the canonical trainer SKILL.md).
- **Bundle directory:** `specialists/ancillary/` → `specialists/superset/`. All twelve bundled files inside reflect the new name.
- **`composes:` frontmatter entry:** `ancillary` → `superset` (9 entries unchanged in count).
- **`description` frontmatter:** routing list reads `... / pr / program / warmup / superset` (rename only).
- **SKILL.md specialist table row:** the 9th row's name reads `superset` with a parenthetical `(formerly ancillary through v0.7.0)` to preserve the historical pointer.
- **SKILL.md "Bundled specialists" section:** mentions the v0.7.1 rename with a one-line history note.
- **README.md:** every current-state mention of `ancillary` updated to `superset`; the repo-layout diagram's 9th row notes the rename history.
- **`scripts/bundle_specialists.sh` SPECIALISTS array:** `ancillary` → `superset`.
- **`scripts/verify_bundle_sync.sh` SPECIALISTS array:** `ancillary` → `superset`.
- **Cursor + Windsurf trigger files:** `~/Projects/.cursor/rules/trainer.mdc` and `~/Projects/.windsurf/rules/trainer.md` version stamps and quick-reference lists updated.
- **Claude mirror:** `~/.claude/skills/trainer/SKILL.md` resynced from canonical.

### Why this version is PATCH not MINOR

- The specialist list count is unchanged (still 9). No routing decisions change, no new sync target is added, no specialist's invocation pattern is updated.
- The rename is a surface-label clarification driven by family coherence with the other gym-themed specialist names. Existing agents that route to `ancillary` should be updated; the rename is documented in the v0.7.0 entry below and in the routing-table parenthetical so consumers can find the new name.
- One MAJOR-flavored concern is that downstream agents with hard-coded references to `ancillary` will break. The mitigation is the parenthetical pointer in the routing table and a `(formerly ancillary)` note in the canonical SKILL.md; a hard alias is not maintained because the rename happened in a single same-day patch window with no other consumers.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version, composes, description, routing-table row, bundled-specialists note)
- `~/Projects/trainer.skill/README.md` (current-state prose, table row, repo-layout)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh`
- `~/Projects/trainer.skill/scripts/verify_bundle_sync.sh`
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (soft cap bumped to accommodate the new routing-table parenthetical)
- `~/Projects/trainer.skill/specialists/ancillary/` → `~/Projects/trainer.skill/specialists/superset/` (12 files, full bundle refresh from the renamed canonical sibling)
- `~/Projects/superset.skill/` (canonical sibling; rename of `~/Projects/ancillary.skill/`)
- `~/.claude/skills/trainer/SKILL.md` (resynced from canonical)
- `~/Projects/.cursor/rules/trainer.mdc` (version stamp + quick-reference list)
- `~/Projects/.windsurf/rules/trainer.md` (version stamp + quick-reference list)

## [0.7.0] (2026-05-18): Add `ancillary` as 9th specialist (parallel-agent dispatch discipline)

**MINOR per SemVer rules; see "Why this version is MINOR not MAJOR" below.** The trainer's specialist gym-skills list grows from 8 to 9 with the addition of `ancillary`, a parallel-agent dispatch and isolation discipline. Routing flow, coaching stance, and Iron Laws are unchanged for the existing 8 specialists; `ancillary` is additive.

### Added

- **`ancillary` as the 9th specialist** at `specialists/ancillary/` (12 files: SKILL.md, README, CHANGELOG, ROADMAP, LICENSE, agent-prompt template, batch-aggregation template, orchestrator-handoff-prompt template, session-log template, falsifier-checklist reference, role-overlays reference, runtime-portability reference). Borrowed patterns from `obra/superpowers-skills` (worktree discipline), `Ibrahim-3d/orchestrator-supaconductor` (role-archetype framing), and `usemozzie/mozzie` (file-ownership table). The canonical sibling repo at `~/Projects/ancillary.skill/` is the editing home; the bundle copy refreshes via `scripts/bundle_specialists.sh`.
- **Routing entry for parallel-agent dispatch.** SKILL.md routing flow step 1 gains "Spawning 2+ parallel agents on the same repo → `ancillary`." Step 2 gains "Parallel-agent dispatch at any tier → load `ancillary` for worktree-isolation and prompt-template discipline." Step 3 gains an example of mid-session route to `ancillary` for orchestrator-handoff under context-window pressure.
- **`composes:` frontmatter entry** for `ancillary` (now 9 entries).
- **`description` frontmatter expansion.** Triggers list adds "parallel agent dispatch" and "orchestrator handoff" so the description discoverability covers `ancillary`'s use cases.
- **`bundle_specialists.sh` SPECIALISTS array** gains `ancillary`. Comment updated from "8 specialist gym-skills" to "9 specialist gym-skills."
- **`README.md` table** for the 9 specialists, with `ancillary`'s row pointing at the dispatch / isolation / orchestrator-handoff role.
- **`README.md` repo-layout diagram** lists `specialists/ancillary/` with a v0.7.0 marker.

### Changed

- **SKILL.md heading** "The 8 specialist gym-skills" → "The 9 specialist gym-skills."
- **"Bundled specialists" section** in SKILL.md notes the v0.7.0 specialist count.
- **`scripts/verify_trainer_sync.sh` soft cap bumped from 180 to 240 lines.** The canonical SKILL.md is 228 lines after the v0.7.0 ancillary additions plus the accumulated v0.6.x Iron Law mechanical pre-action gate and its worked examples. The 180 cap fired a WARN on every verify; new cap leaves room for the next routine specialist addition without immediately tripping the warning.
- **`scripts/verify_bundle_sync.sh` SPECIALISTS array** gains `ancillary` so bundle-drift detection covers all nine specialists.

### Why this version is MINOR not MAJOR

- The SemVer rule "specialist gym-skills list gains or loses entries" was authored with breaking changes in mind (renames, removals, semantic shifts in routing for existing entries). Pure additions to the list are additive per pre-1.0 convention: existing agents that route to the 8 v0.6.1 specialists continue to route exactly the same way, with no changes to their routing decisions.
- The v0.3.0 precedent ("Why this version is MINOR not MAJOR") established that purely additive changes to the bundle are MINOR. The same logic applies here: `ancillary` is opt-in for the parallel-agent dispatch trigger, not in the path of any existing specialist's routing.
- The routing decision flow's text gains three sentences (one per step) about `ancillary`, with zero modification to the existing routing text.
- Coaching stance, Iron Laws (plan-first + mechanical pre-action gate), Red Flags, and Rationalizations tables are all byte-identical to v0.6.1.

### Hard-rule compliance

- Zero em-dashes across the new `ancillary` files, the trainer SKILL.md edits, the README edits, and this CHANGELOG entry.
- The `bundle_specialists.sh` change is a one-line array extension; the existing rsync invariants are preserved.
- Voice rules apply to `ancillary`'s README, CHANGELOG, ROADMAP, and SKILL.md prose: active voice, no "X, not Y" comma-joined patterns, no tricolon-after-colon, no theatrical paragraph-end mic-drops.

### Borrowings cited (transitive, via `specialists/ancillary/CHANGELOG.md`)

`ancillary` v0.2.0 borrows specific patterns from three public projects, documented inline in its CHANGELOG and README. The trainer's repository inherits these citations transitively via the bundle:

- `obra/superpowers-skills` (660 stars, archived) for worktree-directory-selection priority, gitignore pre-flight, project-setup auto-detect, and clean-baseline verification.
- `Ibrahim-3d/orchestrator-supaconductor` (350 stars) for the role-archetype framing.
- `usemozzie/mozzie` (49 stars) for the file-ownership table pattern.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version bump 0.6.1 → 0.7.0; composes field; description; routing flow; specialist table; "Bundled specialists" section)
- `~/Projects/trainer.skill/README.md` (8 → 9 references; new ancillary row in table; repo-layout diagram)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (SPECIALISTS array; comment)
- `~/Projects/trainer.skill/specialists/ancillary/` (new directory, 12 files)
- `~/Projects/ancillary.skill/` (new sibling canonical, 13 files including `.gitignore`)
- `~/.claude/skills/ancillary.skill/` (renamed from `~/.claude/skills/ancillary/`; mirrored from canonical)

### Open questions

- **Specialist-list SemVer rule.** The current rule ("specialist list gains or loses entries → MAJOR") needs refinement to distinguish additive vs breaking changes. Consider updating to "specialist list gains or loses entries breaks existing routing → MAJOR; purely additive → MINOR" in a future patch.
- **Cursor / Windsurf rule mirrors.** The trainer SKILL.md is mirrored to `~/Projects/.cursor/rules/trainer.mdc` and `~/Projects/.windsurf/rules/trainer.md`. The v0.7.0 SKILL.md changes need to flow to those mirrors; run `skill-sync` after this commit.
- **Public push.** This entry is committed locally; pushing to `weijia-89/trainer.skill` should happen after `verify_trainer_sync.sh` runs clean.

---

## [0.5.0] (2026-05-16): Runnable pressure-scenario harness (3 trainer scenarios in form-check shape) + soft-cap bump

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged. The v0.4.0 doc-only pressure scenarios at `tests/scenarios/S01_*.md`, `S02_*.md`, `S03_*.md` are now also instantiated as runnable harness scenarios under `tests/scenarios/harness/<name>/` matching the form-check pressure-scenario shape (`setup.md` + `prompt.md` + `pass_criteria.py` + `notes.md` + `reference_response.md`). Doc-only scenarios are retained as the human-readable spec.

### Added

- **`tests/scenarios/harness/_grading.py`** vendored from `form-check.skill/tests/pressure_scenarios/_grading.py` (same `Transcript` substantive-sentence helper; same min-words floor of 10 for `__contains__`).
- **`tests/scenarios/harness/ceremonial_routing/`** harness shape for S01. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/coaching_collapse_on_i_know/`** harness shape for S02. Reference response passes its own `pass_criteria.py`.
- **`tests/scenarios/harness/bypass_for_small_task/`** harness shape for S03. Reference response passes its own `pass_criteria.py`.

### Changed

- **`scripts/verify_trainer_sync.sh`** soft cap bumped from 140 to 180 lines. Canonical `SKILL.md` is now 157 lines after the v0.4.0 Red Flags + Rationalizations additions; the previous 140 cap fired a `WARN` on every verify. New cap leaves headroom for incremental discipline-floor scaffolding without immediately tripping the warning.

### Not changed

- `SKILL.md` content (no normative additions beyond v0.4.0).
- README scope (already updated in v0.4.0 to acknowledge documentation-skill vs behavioral-skill distinction).
- The 4 sync targets (canonical, Claude mirror, Cursor trigger, Windsurf trigger) all agree on version 0.5.0 after this entry; verify with `bash scripts/verify_trainer_sync.sh`.

### Verification

- `tests/scenarios/harness/<name>/pass_criteria.py` passes against its corresponding `reference_response.md` for all 3 scenarios (3/3 PASS).
- `bash scripts/verify_trainer_sync.sh` reports PASS on all 7 invariants (version agreement, em-dash zero, trigger config, byte-identical mirror).
- `form-check.skill/tests/pressure_scenarios/discriminate_test.py` (mutation-style probe) still reports 0/272 incorrect passes after Option C upgrade of all 34 form-check pass_criteria.

### Known follow-ups

- **Phase 11 blind audit cycle** still pending. Requires `ANTHROPIC_API_KEY` or alternate-vendor harness; not autonomously runnable.
- **Layer B (calibration log analyzer) and Layer C (mutation testing of agent behavior)** of the Phase 11 plan remain future work; v0.5.0 is Layer A only (per-scenario pass/fail harness).

## [0.4.0] (2026-05-16): Load-bearing-discipline pass (audit-gap patches + Iron Law + Red Flags + Rationalizations + pressure scenarios)

**MINOR per SemVer rules.** Routing decision flow and specialist list unchanged; coaching-stance section gains explicit operational definitions and the discipline-floor scaffolding (Iron Law, Red Flags, Rationalizations) that the other 7 gym-skills already had.

Two converging inputs drove this version:

1. **A targeted audit of the v0.3.0 trainer skill** identified 4 operationalization gaps + 1 schema gap (Iron Law, demonstrated-understanding, adversarial-review interaction, opt-out semantics, override-log schema). The audit document itself is private working notes; the gaps it surfaced are described inline below.
2. **Context-free adversarial review at v0.3.0** (chat 2026-05-16, late) added 4 more items (Red Flags section, Rationalizations table, calibration log infrastructure, README walk-back of v0.3.0 promotional phrasing), plus three doc-only pressure scenarios for the failure modes.

The v0.3.0 portfolio-bundling work made the skill *distributable*; v0.4.0 makes the skill's stated discipline more *enforceable* by surfacing the failure modes the discipline is supposed to prevent.

### Added (SKILL.md)

- **Iron Law banner** at the top of the Coaching stance section. Form: *"coach, do not do. Push back when warranted. Defer when the user has demonstrated understanding. Log coached overrides."* Trainer was the only gym-skill without one as of v0.3.0; closes audit Gap 1.
- **Coached-override log entry schema inline.** Schema: `{ts, event, subject, trainer_position, user_decision, user_rationale, residual_concern, rounds}`. Closes audit Gap 5 (override log was prescribed in v0.2.0 but schema-undefined).
- **Red Flags section.** 10 verbatim agent-thoughts that should trigger STOP and re-route (e.g. "I named the specialist; that counts as invoking it", "User said 'I know'; I'll defer"). Matches form-check's structural pattern; sourced from the dominant failure modes in the adversarial review.
- **Rationalizations table.** 8 excuse / reality pairs covering ceremonial routing, coaching collapse, framing-based bypass, hidden-state coaching.
- **Adversarial-review deference** added to "What the trainer is NOT". During `form-check adversarial-review`, the trainer steps back on review content but stays engaged on routing decisions (which specialist next, when to stop). Closes audit Gap 3.
- **Opt-out semantics** as a new section. Per-session opt-out via "no coaching this session"; routing questions still answered, pushback paused. Persistent opt-outs are themselves a signal logged at the start of the next non-opted-out session. Closes audit Gap 4.

### Added (filesystem)

- **`form-check.skill/.recovery/calibration.jsonl`** (empty, append-only). Backs the pointer in `SKILL.md` which was previously dangling (verified by `ls` before the fix: directory did not exist).
- **`form-check.skill/.recovery/SCHEMA.md`** documenting event types: `coached_override`, `coaching_collapse`, `routing_decision`, `score_event`, `coached_override_revisit`. Append-only, UTC timestamps, no-PII discipline stated.
- **Three doc-only pressure scenarios** under `trainer.skill/tests/scenarios/`:
  - `S01_ceremonial_routing.md`, tests Iron Law + Red Flag "I named the specialist; that counts as invoking it"
  - `S02_coaching_collapse_on_i_know.md`, tests the tightened defer-clause against vague approval
  - `S03_bypass_for_small_task.md`, tests the always-on claim against user-framed-small tasks that hide tier-relevant context
  - Each follows the Phase 11 plan schema (Setup, Forcing function, Pass criteria, Fail criteria, Trapdoor). Manually testable by a human; runnable harness deferred to Phase 11 implementation.
- **`tests/scenarios/README.md`** documenting the manual test protocol and pass/fail mapping back to `SKILL.md` clauses.

### Changed

- **"Demonstrated understanding" clause tightened.** Previously: *"User has demonstrated understanding of the tradeoff and has a reasoned position."* Now: *"User has articulated the specific consequence the trainer named AND the specific reason it does not apply or is acceptable. Vague approval ('yes I know', 'I've got this', 'trust me') does not count as demonstrated understanding."* Closes audit Gap 2 (was the most exploitable clause in v0.3.0).
- **`README.md` honest-scope paragraph added.** Walks back v0.3.0 promotional phrasing ("8-skill agent ecosystem", "makes the ecosystem coherent"). New framing: documentation skill with discipline scaffolding, not yet a behavioral skill with a runnable harness. References the audit and the Phase 11 plan.
- **`README.md` repo-layout diagram** updated to include `tests/scenarios/`.
- **Soft line cap** bumped from 100 to 140 in `scripts/verify_trainer_sync.sh`. Canonical `SKILL.md` is now 157 lines. The cap will need another tune-up at next discipline-pass; see open items.

### Why MINOR not MAJOR

- 8 specialists unchanged.
- Routing decision flow byte-identical.
- Push-back triggers unchanged in category (still 3 triggers: concrete consequence, best-practice deviation, missing skill).
- New operational definitions and discipline scaffolding are clarifications + enforcement aids, not new behaviors. Any v0.3.0-compliant trainer is already v0.4.0-compliant; the v0.4.0 version is harder to game.

### Verification done

- `ls $HOME/Projects/form-check.skill/.recovery/` returns `calibration.jsonl` + `SCHEMA.md`.
- Em-dash audit: zero across `SKILL.md`, all three mirrors, this CHANGELOG entry, `SCHEMA.md`, the three scenarios, `README.md`, and `scripts/bundle_specialists.sh`.
- Bundle script re-run confirms 280 files across 8 specialists at `./specialists/`.
- `verify_trainer_sync.sh` invariants pass (canonical, Claude mirror, Cursor and Windsurf triggers all agree on version 0.4.0; zero em-dashes; `alwaysApply: true`; `trigger: always_on`).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (Iron Law, log-schema-inline, Red Flags, Rationalizations, defer tightening, adversarial-review carve-out, opt-out semantics; 103 → 157 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror, re-synced to v0.4.0 on second pass; first pass missed the Red Flags + Rationalizations block, caught by `verify_trainer_sync.sh`)
- `~/Projects/.cursor/rules/trainer.mdc` (heading bumped to v0.4)
- `~/Projects/.windsurf/rules/trainer.md` (same)
- `~/Projects/trainer.skill/README.md` (honest-scope paragraph, layout diagram updated)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (line cap 100 → 140)
- `~/Projects/trainer.skill/tests/scenarios/` (new dir, 4 files)
- `~/Projects/form-check.skill/.recovery/calibration.jsonl` (new, empty)
- `~/Projects/form-check.skill/.recovery/SCHEMA.md` (new)
- a private trainer-skill audit (working notes) (source audit doc; not in the skill repo)

### Open items deferred to next version

- **Phase 11 runnable harness** for the three pressure scenarios: doc-only at v0.4.0. The scenarios are testable manually; no automation submits them to an agent and scores behavior. Estimated 4-8 hr; deferred until external pressure (interview, public release, third party using the skill) makes the runnable case load-bearing.
- **`SKILL.md` line count at 157 already pushes the 140 cap** added in this version. Next discipline-pass should either re-tune the cap or split Red Flags + Rationalizations into a separate `discipline.md` companion. Splitting trades token efficiency (some agents skip companions) for the cap.
- ~~**Re-run `verify_trainer_sync.sh`**~~ Done. All 7 hard invariants PASS; the only WARN is the documented `SKILL.md` line count (157) over the bumped soft cap (140), tracked above.

---

## [0.3.0] (2026-05-16): Bundle the 8 specialists into the repo; rewrite README for portfolio distribution

**MINOR per SemVer rules.** Routing flow and coaching stance unchanged; new packaging mechanic added so the repo distributes the full 8-skill ecosystem rather than only the trainer entrypoint.

### Added

- **`specialists/` directory** with all 8 specialist gym-skills bundled in. Contents:
  - `specialists/form-check/` (243 files: SKILL.md, README, CHANGELOG, agent-runtime, checklists, docs, examples, learner, multi-language, references, rubrics, scale-up, templates, tests, tools)
  - `specialists/recovery/` (18 files: checklists, examples, references, rubrics, templates, tests, workflow)
  - `specialists/warmup/` (4 files, includes `graduation_checklist.md`)
  - `specialists/gymbuddy/`, `specialists/safetybar/`, `specialists/diet/`, `specialists/pr/`, `specialists/program/` (3 files each: SKILL.md, README, CHANGELOG)
  - Total bundled: 280 files across 8 specialists.
- **`scripts/bundle_specialists.sh`** refreshes the bundle from sibling-dir canonicals. Excludes `.git`, virtualenvs, `__pycache__`, `node_modules`, `.DS_Store`, `.pytest_cache`, `.recovery` state, generated test output. Idempotent via `rsync --delete`.
- **`composes:` frontmatter populated** in `SKILL.md` with the 8 specialist names.
- **"Bundled specialists" section in `SKILL.md`** explaining the relationship between sibling-dir canonicals (editing home) and bundle (distribution artifact).

### Changed

- **`README.md` rewritten** as public-portfolio-facing document. Was internal-skill-doc style; now opens with the "8-skill agent ecosystem" framing, includes install/use snippets, repository-layout diagram, and explicit separation between SKILL.md sync (canonical-to-mirrors, four locations) and bundle (canonical-to-`./specialists/`, one operation).
- **`SKILL.md` references** to specialist paths kept as `<name>.skill/` (sibling convention) in routing/teaching sections because the canonical operating environment is the home directory with sibling skill dirs; the bundle is for clones / distribution, not for local editing.
- **SemVer rules updated** to clarify that introducing the bundle mechanic is a MINOR change.

### Why this version is MINOR not MAJOR

- The 8 specialists in the `composes:` list are the same 8 specialists already documented in v0.2.0's body. No specialist added or removed.
- Routing decision flow is byte-identical to v0.2.0.
- Coaching stance criteria unchanged.
- The bundle is additive: agents that operate against sibling-dir canonicals continue to work unchanged.

### Hard-rule compliance

- Zero em-dashes across `SKILL.md`, `README.md`, this CHANGELOG entry, and the new bundle script.
- Bundle script uses single-quoted exclude patterns (no shell-glob surprises) and `set -euo pipefail` for fail-fast.

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (version bump 0.2.0 → 0.3.0; composes field populated; bundled-specialists section added)
- `~/Projects/trainer.skill/README.md` (rewrite, 60 → ~135 lines)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/bundle_specialists.sh` (new)
- `~/Projects/trainer.skill/specialists/` (new directory, 280 files across 8 specialists)

### Open questions

- **Mirror updates:** the `~/.claude/skills/trainer/SKILL.md` mirror needs a re-sync to pick up the v0.3.0 composes field and the new section. Run `scripts/verify_trainer_sync.sh` after mirror update.
- **Sync of bundled specialists:** the bundle currently lives only inside `trainer.skill`. If `~/.claude/skills/trainer/` should also carry the bundle (so Claude can read specialists without leaving its skill dir), that's a separate sync step worth deciding on before pushing public.
- **Public push:** repo is not yet pushed to GitHub. When ready, decide on repo visibility (public for portfolio vs private), tags / release for v0.3.0, and whether `LICENSE` and `CONTRIBUTING.md` need adding at the top level (currently only inside specialists like `form-check`).

---

## [0.2.0] (2026-05-16): Coaching stance correction; always-on triggers

**Breaking-semantic change.** v0.1.0 said "user wishes are the final say." Wei corrected this: the trainer is a coach, not a doormat. The trainer should push back when user decisions have deleterious downstream consequences or veer from best practices without articulated reason. After two rounds of coached pushback, the trainer respects the decision and logs it as a *coached override* with the user's rationale.

### Changed

- **Coaching stance section added.** Three push-back triggers (concrete downstream consequence; veers from best practice without articulated reason; user missing a skill that would change the decision). Procedure: name consequence, cite practice, offer alternative; two rounds max; log coached override.
- **Proactive teaching responsibilities expanded.** Trainer now explicitly explains: specialist composition (which order, why, how they interact), downstream consequences (what to watch for after a change), best practices (cited from `form-check.skill/references/notes.md` at the moment of relevance).
- **Triggers changed to always-on.** Cursor trigger: `alwaysApply: true`. Windsurf trigger: `trigger: always_on`. Loaded first on every coding / prompt-engineering / agent-skill session.
- **Removed "user wishes are the final say"** language entirely. Replaced with the coaching-with-audit-trail model.
- **README.md added** documenting all four sync targets and SemVer rules. The Phase 10 routing decision (whether to fold trainer into `warmup` or stand it up separately) was driven by a private gym-skills evidence audit; the decision and rationale are summarized in `docs/PHASE_10_ROUTING_DECISION.md` when that doc exists.

### Hard-rule compliance

- Zero em-dashes in `SKILL.md`, both triggers, README, and this CHANGELOG entry (matches Wei's writing-style hard rule from 2026-05-15).

### Files touched

- `~/Projects/trainer.skill/SKILL.md` (rewrite; 88 lines)
- `~/.claude/skills/trainer/SKILL.md` (byte-identical mirror)
- `~/Projects/.cursor/rules/trainer.mdc` (always-apply, updated body)
- `~/Projects/.windsurf/rules/trainer.md` (always-on, updated body)
- `~/Projects/trainer.skill/README.md` (new)
- `~/Projects/trainer.skill/CHANGELOG.md` (this entry)
- `~/Projects/trainer.skill/scripts/verify_trainer_sync.sh` (bumped expected version to 0.2.0; bumped soft line cap from 80 to 100)

### Companion: `skill-sync` gains Windsurf support

`skill-sync` v0.2+ adds Windsurf as a sync target alongside Claude and Cursor. The trainer skill is the first to use it. See `~/.claude/skills/skill-sync/CHANGELOG.md` for the implementation detail.

## [0.1.0] (2026-05-16): Initial scaffold

- Created as the bootstrap / entrypoint skill for the gym-skills family (Phase 10 of the gym-skills evidence-base audit, 2026-05-16).
- Role defined: "helps the user find the program that works for them, teaches them how to do it along the way, and adjusts according to the user's wishes." Authored by Wei Jia.
- Sync targets established at four locations:
  - `~/Projects/trainer.skill/SKILL.md` (canonical)
  - `~/.claude/skills/trainer/SKILL.md` (Claude mirror, byte-identical)
  - `~/Projects/.cursor/rules/trainer.mdc` (Cursor trigger)
  - `~/Projects/.windsurf/rules/trainer.md` (Windsurf trigger)
- `scripts/verify_trainer_sync.sh` added to assert sync invariants.
- Lists the 8 specialist gym-skills (`form-check`, `program`, `warmup`, `safetybar`, `recovery`, `gymbuddy`, `diet`, `pr`) with one-line invocation criteria.
- Names "user wishes are the final say" as the trainer's behavioral anchor: overrides are respected and noted, never argued. (Reversed in v0.2.0.)
- No checklists, no rubrics, no scoring. Pure routing + teaching + adapting.
