# Changelog, superset

Format: Keep a Changelog with SemVer.

Renamed from `ancillary` to `superset` at v0.3.0 for trainer-family coherence (all sibling specialists use gym-themed names: form-check, program, warmup, safetybar, recovery, gymbuddy, diet, pr). The v0.2.0 and earlier entries below describe the project under its previous name and are preserved verbatim as historical record.

## SemVer rules for this skill

- **MAJOR:** the five-pillar prompt shape changes (worktree, baseline, scope, no-push, session log). These are the load-bearing pillars; changing them breaks every prompt downstream of this skill.
- **MINOR:** new falsifiers, new role archetypes, new templates, new references, new cross-cutting concerns, new patterns borrowed from the public ecosystem; pure renames at the skill level (since `name:` frontmatter changes break existing `Skill: <name>` invocations even if the body is unchanged).
- **PATCH:** wording, citation updates, example refinements, falsifier rewordings without semantic change.

## [0.3.0], 2026-05-18, rename `ancillary` to `superset` for trainer-family coherence

**MINOR per the rename clause in SemVer rules above.** Pure rename with no behavioral changes; existing prompt-template shape, falsifier checklist, role archetypes, and batch-aggregation playbook are byte-equivalent to v0.2.0 modulo the `s/ancillary/superset/` and `s/Ancillary/superset/` substitutions in prose. The frontmatter `name:` field changes, so any existing `Skill: ancillary` invocation in operator notes will need updating to `Skill: superset`.

### Changed

- **Skill name** `ancillary` → `superset` in the frontmatter, all in-body references across SKILL.md, README.md, ROADMAP.md, templates, and references. The trainer bundle path moves from `trainer.skill/specialists/ancillary/` to `trainer.skill/specialists/superset/`.
- **Top-of-README metaphor** rewritten from Ann Leckie's *Imperial Radch* ancillaries (one consciousness, many bodies) to the weightlifting superset (two or more exercises back-to-back, higher total volume in less wall-clock time). The new metaphor maps onto the dispatch + isolation pattern at the same conceptual depth and fits the gym-themed trainer family.
- **Section heading** in README.md from "Relationship to the public ancillary-pattern ecosystem" to "Relationship to the public parallel-dispatch ecosystem" (semantic accuracy; the section was always about parallel-dispatch implementations, the previous heading was stem-tied to the old name).
- **Naming history** section added to README.md documenting the rename and preserving the Radch metaphor as historical record.

### Why a pure rename is MINOR not PATCH

- Existing operator notes, agent prompts, or skill-tool invocations that reference `Skill: ancillary` or `~/.claude/skills/ancillary/` or `~/Projects/ancillary.skill/` will fail under the new name. That's a breaking change for downstream callers, however few there are.
- PATCH per Keep-a-Changelog is for backwards-compatible bug fixes; this is not a bug fix and is not backwards-compatible at the invocation level.
- MAJOR is reserved for five-pillar prompt-shape breaks; the prompt shape is unchanged.
- MINOR captures "new feature, may require minor consumer adjustments" which fits the rename pragmatically.

### Hard-rule compliance

- Zero em-dashes across the renamed README, SKILL.md, ROADMAP, CHANGELOG, templates, and references (verified with `grep`).
- Voice rules apply to the new README intro paragraph: active voice, no "X, not Y" comma-joined patterns, no tricolon-after-colon, no theatrical paragraph-end mic-drops.
- The new weightlifting metaphor opens with a definition (X is Y), not a short-fragment opener.

### Files touched

- `~/Projects/superset.skill/SKILL.md` (frontmatter `name:` and version, heading, overview paragraph)
- `~/Projects/superset.skill/README.md` (heading, intro, naming-history section, all in-body references)
- `~/Projects/superset.skill/ROADMAP.md` (heading, current-version line, validation-status rows, all references)
- `~/Projects/superset.skill/CHANGELOG.md` (this entry plus the file-header rename note)
- `~/Projects/superset.skill/templates/agent-prompt.md` (session-log path reference)
- `~/Projects/superset.skill/templates/orchestrator-handoff-prompt.md` (multiple in-body references and the Radch-metaphor paragraph)
- `~/Projects/superset.skill/references/runtime-portability.md` (multiple in-body references)
- `~/Projects/superset.skill/references/falsifier-checklist.md` (one in-body reference)

### Downstream changes shipped alongside this version

- `~/.claude/skills/ancillary.skill/` removed; `~/.claude/skills/superset.skill/` populated from the canonical sibling.
- `trainer.skill v0.7.1` (sibling commit): `specialists/ancillary/` renamed to `specialists/superset/`; trainer SKILL.md, README, CHANGELOG, Cursor mirror, Windsurf mirror, bundle scripts all updated. See `trainer.skill/CHANGELOG.md` v0.7.1 entry for the trainer-side rename details.

---

## [0.2.0], 2026-05-18, public-ecosystem borrowings + role archetypes + batch aggregation

### Added

- **Role archetypes.** Three archetypes (`code` default, `sweep`, `prose-audit`) documented in `SKILL.md`. The base agent-prompt template is `code`-flavored; overlays for `sweep` and `prose-audit` live at `references/role-overlays.md` with substitutions for the Task, Vibe-careful protocol, and Verification sections.
- **Header fields in the agent prompt:** `Role:` (archetype declaration), `Phase:` (multi-phase batch ordering), `Owned-paths:` (file-ownership table for scope > 3 files or sibling-adjacent dispatch).
- **Worktree discipline expansion** in `SKILL.md`:
  - Directory-selection priority (existing `.worktrees/` > `worktrees/` > CLAUDE.md preference > ask operator), borrowed from `obra/superpowers-skills` `using-git-worktrees`.
  - Gitignore pre-flight (`git check-ignore -q .worktrees`) before worktree creation.
  - Project-setup auto-detect block (npm / cargo / pip / poetry / go) replacing operator-memorized install commands.
  - Clean-baseline verification before declaring the worktree ready.
- **Batch-aggregation template** at `templates/batch-aggregation.md`: operator-facing playbook for end-of-batch session-log review, failing-test cross-check, merge-order decision, failure decision matrix (retry / escalate / skip per agent), final-review subagent dispatch via `requesting-code-review`, push or PR.
- **Runtime portability reference** at `references/runtime-portability.md`: tool-name mapping for Cascade-on-Windsurf, Claude Code, Cursor, Codex, Gemini CLI. Cross-runner invariants (worktree-per-agent, gitignore pre-flight, baseline capture, commit-no-push, session-log write) called out explicitly.
- **Falsifier additions:**
  - H9: `.worktrees/` gitignored before creation
  - H10: project-setup auto-detected from manifest, not hardcoded by operator
  - M11: `Owned-paths:` table for >3-file scope
  - M12: `Phase:` field for multi-phase batches
  - Cross-cutting concern: batch-aggregation template referenced in coordination notes

### Changed

- Frontmatter: replaced inline `status:` notes with `version: 0.2.0`, added `composes:` list (`dispatching-parallel-agents`, `using-git-worktrees`, `requesting-code-review`, `safe-terminal`, `trainer`), declared `license: MIT`.
- `templates/agent-prompt.md` Worktree-setup section: restructured into Step 0 (gitignore pre-flight), Step 1 (create worktree), Step 2 (project-setup auto-detect), Step 3 (clean-baseline). The dep-touching venv block is folded into Step 2.
- Bundled as the 9th specialist in `weijia-89/trainer.skill` at `specialists/ancillary/`. Trainer SKILL.md and README updated to reference the 9-specialist roster.

### Borrowings cited

The 0.2.0 additions cite specific provenance to the public ecosystem:

- `obra/superpowers-skills` (Jesse Vincent, 660 ⭐, archived) for directory-selection priority, gitignore pre-flight, project-setup auto-detect, and clean-baseline verification.
- `Ibrahim-3d/orchestrator-supaconductor` (350 ⭐) for the role-archetype framing of worker templates (code / sweep / test / integration).
- `usemozzie/mozzie` (49 ⭐) for the file-ownership table pattern in `Owned-paths:`.

Deliberately not borrowed: supaconductor's live JSON message-bus and DAG-execution layers. The fresh-chat dispatch model treats agents as one-shot; the operator is the only coordination channel between them. Adopting a runtime message-bus would reinvent supaconductor.

## [0.1.2], 2026-05-18 afternoon

H5 fired in production. Agent E (TC-9030 oracle-pilot move on `mailchimp-r-and-a-qa-suite`) was dispatched same-tree without a worktree; a concurrent sibling agent (`lib/ai-*.js` Phase 2 work) raced the `.git/index.lock`, and parallel `run_command` batches in the same checkout exhibited a sporadic Cwd race. Recovery was switching to sequential `run_command` calls in baseline capture and combining `git add` + `git commit` into a single script invocation.

### Added

- Common-mistakes entry for the parallel-batch Cwd race pattern in `SKILL.md`. Worked example: Agent E's git baseline-capture batch returning inconsistent SHA / "not a git repository" responses depending on call ordering. Prevention: comply with H5 (worktree per agent). Defense-in-depth: sequence baseline-capture calls instead of parallelizing them.

## [0.1.1], 2026-05-18

Adversarial review of the v0.1.0 prompts themselves yielded 8 more falsifiers and refinements to the agent-prompt template.

### Added

- **High-severity falsifiers** H5-H8: worktree setup is first command, dep-touching task creates worktree-local venv, baseline captures failing-test names not just count, vibe-careful task has crisp source-edit definition.
- **Medium-severity falsifiers** M7-M10: structured-file edit has parse-validate step, stop-and-report channel is explicit, wall-clock estimate stated up front, verification command file scope matches Task in-scope list.
- **Cross-cutting concern:** operator setup commands (handed to the operator alongside agent prompts) must follow the same shell-hazard rules as agent `run_command` (one logical command per line, no angle-bracket placeholders, no multi-statement `;` chains, no implicit pwd). Pattern observed: a multi-line `export GITHUB_TOKEN=<your_pat>` block triggered a zsh parse error near `else`; the operator had also run an earlier `nohup` from the wrong directory.
- **Vibe-careful protocol** section in `templates/agent-prompt.md` with explicit Allowed and STOP lists for source edits.

## [0.1.0], 2026-05-18 morning, initial draft

### Added

- **Five-pillar prompt template** at `templates/agent-prompt.md`: worktree setup, baseline capture, scope plus out-of-scope, commit-and-do-not-push, post-session log.
- **Falsifier checklist** at `references/falsifier-checklist.md` with 12 initial falsifiers (H1-H4 high, M1-M6 medium, L1-L4 low) plus cross-cutting concerns (shared state map, operator review bandwidth, coordination overhead, recovery path).
- **Session-log template** at `templates/session-log.md` for the agent's post-commit write before returning.
- **Orchestrator-handoff template** at `templates/orchestrator-handoff-prompt.md` for migrating the orchestrator role to a fresh chat under context-window pressure, with eight orchestrator-specific falsifiers (HO1-HO8).
- **SKILL.md** with overview (Imperial Radch metaphor), when-to-use guidance, five-pillar quick reference, worktree discipline, race-condition reference, runtime portability note, common mistakes, red flags.

### Rationale

Drafted in a 2026-05-18 session that ran two parallel-agent prompts on `lodestar` (em-dash sweep + mypy stub uplift). The first prompt-quality issues observed during that session (hardcoded test counts, symlink confusion, push-enabled-by-default, CI version skew, loose "fix if it's a real bug" instructions) became the initial falsifier set. Subsequent adversarial review of the prompts themselves produced 7 more falsifiers (the 0.1.1 set), and a same-day production failure (Agent E, TC-9030) produced the 0.1.2 parallel-batch Cwd race pattern.

The skill's organizing metaphor (Ann Leckie's Imperial Radch ancillaries) was chosen because it captures the actual relationship: one operator running many bodies in parallel, each acting autonomously inside its scope, all coordinating through a shared channel the operator controls. The metaphor is not load-bearing; the discipline is.
