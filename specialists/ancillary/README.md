# ancillary

A skill for orchestrating parallel fresh-chat agents on a single git repository without losing isolation, scope discipline, or session learnings between batches.

The name is from Ann Leckie's Imperial Radch novels: a Radchaai warship is one consciousness running in many bodies (ancillaries) at once, each acting autonomously inside its scope, all coordinating through a shared channel. The skill is the dispatch and isolation discipline that lets one human operator orchestrate parallel AI agents the same way.

## What this skill does

Parallel agents on the same git repo collide on shared state (`.pytest_cache/`, `.ruff_cache/`, `.venv/`, `.git/index.lock`, `pyproject.toml`, lock files). Without isolation, the second agent to commit either merge-conflicts or silently corrupts the first agent's work. Without a structured prompt, agent quality drifts batch-to-batch and the operator loses the cumulative session learning that should make the next batch better.

`ancillary` covers both:

- **Isolation:** worktree-per-agent by default, gitignore pre-flight, project-setup auto-detect from manifest, worktree-local venv for Python.
- **Prompt discipline:** five-pillar template (worktree, baseline, scope, no-push, log) plus a falsifier checklist that catches known prompt-failure modes before spawning.
- **Batch aggregation:** an operator-facing playbook for end-of-batch merge-order, failure decision matrix, final-review dispatch, and push.
- **Orchestrator handoff:** a separate template for when the orchestrating chat itself needs to migrate to a fresh chat under context-window pressure.

The skill is a prompt-template generator plus a checklist, not a runtime. The agents are fresh chats; the operator is the only coordination channel between them.

## When to invoke

- Spawning 2+ fresh-context agents on the same git repo, with non-overlapping file sets, fitting in <90 minutes of agent wall-clock each.
- A scaffold-then-features dispatch: one sequential agent lays down scaffolding, then 2-3 parallel agents fill in features against the scaffold.
- A sweep across many files (em-dash sweep, voice-rule audit, import rename) where the work is mechanical and the verification is grep-based.
- Any time the orchestrating chat is slowing the IDE or accumulated noise is starting to bleed across batches.

## When to skip

- The bottleneck is operator writing or judgment work; agents do not unblock that.
- Tasks share files or review-gated config; parallelism creates merge conflicts.
- Operator is mid-incident or mid-MVP-push and has no review bandwidth.
- The work needs full-system context the prompt cannot carry; single fresh chat with the operator beats N parallel agents with partial views.

## Quick reference: the five-pillar prompt

Every dispatched agent's prompt MUST contain:

1. **Worktree setup** as the first command (or a documented same-tree exception)
2. **Baseline capture** (test count + failing-test names + HEAD SHA + lint state)
3. **Scope + out-of-scope** as explicit file lists, including review-gated files
4. **Commit + DO NOT PUSH** discipline; operator pushes at end of batch
5. **Post-session log** to `localonly/session-logs/<date>-agent<N>-<slug>.md`

Full discipline in `SKILL.md`; agent prompt template at `templates/agent-prompt.md`; falsifier checklist at `references/falsifier-checklist.md`.

## Composes with

This skill assumes the `dispatching-parallel-agents` general pattern from `obra/superpowers-skills` is loaded (or the equivalent in your runner). It also composes with:

- `using-git-worktrees` for the worktree discipline (directory-selection priority, gitignore pre-flight, project-setup auto-detect, clean-baseline verification).
- `requesting-code-review` for the final-review subagent dispatch in the batch-aggregation playbook.
- `safe-terminal` for the shell-hazard rules that apply to both agent `run_command` calls and the operator setup commands handed alongside the agent prompts.
- `trainer` as the always-on routing skill that loads `ancillary` when it sees a parallel-dispatch trigger.

## What this skill protects against

The recurring failure modes observed across real dispatched-agent sessions:

- **Shared-state corruption.** Two agents `pip install` into the same `.venv` and break each other. The worktree-per-agent default plus worktree-local venv block prevents it.
- **Silent push to main.** Agents trained on public repos default to `git push` after committing. The explicit DO-NOT-PUSH discipline forces the batched-merge model.
- **Baseline-by-count masking.** "172 passed before, 172 passed after" passes verification but hides a swap (pre-existing failure left while new failure introduced). The failing-test-names capture catches it.
- **Verification-scope drift.** A grep over more directories than the agent was scoped to either false-fails or licenses scope-creep. The M10 falsifier and the role overlays make the check tight.
- **Cwd race in same-tree dispatch.** Parallel `run_command` batches in the same checkout exhibit a sporadic working-directory race when a sibling agent is concurrently active. H5 (worktree-per-agent) is the canonical fix; the common-mistakes section documents the failure mode.

## Files

- `SKILL.md`, the skill body: overview, when-to-use, five-pillar reference, role archetypes, worktree discipline, race-condition reference, batch-aggregation reference, runtime portability, common mistakes, red flags
- `templates/agent-prompt.md`, the agent prompt template with bracketed placeholders
- `templates/batch-aggregation.md`, the operator's end-of-batch playbook
- `templates/orchestrator-handoff-prompt.md`, for migrating the orchestrator role itself to a fresh chat
- `templates/session-log.md`, the shape the dispatched agent writes before returning
- `references/falsifier-checklist.md`, the prompt-quality check (H1-H10 high, M1-M12 medium, L1-L4 low, plus cross-cutting concerns)
- `references/role-overlays.md`, the `code` / `sweep` / `prose-audit` archetype substitutions
- `references/runtime-portability.md`, tool-name mapping for Cascade-on-Windsurf, Claude Code, Cursor, Codex, Gemini CLI

## Install

Bundled inside [`weijia-89/trainer.skill`](https://github.com/weijia-89/trainer.skill) at `specialists/ancillary/`. To use standalone, copy the contents of this directory into your runner's skill directory (e.g., `~/.claude/skills/ancillary.skill/`).

The skill triggers when an agent recognizes a parallel-dispatch context. The `trainer` skill's routing flow names `ancillary` as the load target for "spawning 2+ parallel agents" triggers.

## Relationship to the public ancillary-pattern ecosystem

The skill borrows specific patterns from three public projects:

- **`obra/superpowers-skills`** (660 ⭐, archived) is the foundational Claude Code superpowers ecosystem. `using-git-worktrees` is the source of the directory-selection priority, gitignore pre-flight, project-setup auto-detect, and clean-baseline verification.
- **`Ibrahim-3d/orchestrator-supaconductor`** (350 ⭐) is a more elaborate orchestrator with DAG-based parallel groups, file-lock coordination, deadlock detection, retry-with-escalation, and a JSON message bus. `ancillary` deliberately does not adopt the message-bus or DAG-execution layers; the fresh-chat dispatch model treats agents as one-shot and assumes the operator is the only coordination channel. The role-archetype framing borrows from supaconductor's worker-template differentiation.
- **`usemozzie/mozzie`** (49 ⭐) is a desktop app for parallel agent orchestration with git worktrees and dependency tracking. The file-ownership table in the `Owned-paths:` header field borrows from mozzie's CLAUDE.md.

The deliberate non-adoptions are documented in SKILL.md. ancillary stays at the prompt-template-and-checklist layer; the operator's human review is the rate-limit, and a live message-bus would reinvent supaconductor at a layer where the human is already the coordinator.

## License

MIT. See [`LICENSE`](./LICENSE).
