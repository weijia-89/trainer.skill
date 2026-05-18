---
name: superset
description: Use when spawning 2+ fresh-context agents on the same git repo for isolated parallel work; symptoms include same-tree shared-state risk (.pytest_cache / pyproject collisions), agents overstepping scope, intermediate commits pushed by accident, session learnings lost between iterations, prompt quality drifting between agents.
type: project-skill
version: 0.3.0
authors: Wei Jia (2026-05-18)
license: MIT
composes:
  - dispatching-parallel-agents
  - using-git-worktrees
  - requesting-code-review
  - safe-terminal
  - trainer
---

# superset

## Overview

Named for the weightlifting superset: two or more exercises performed back-to-back, often on different muscle groups, so the lifter sustains higher total volume in less wall-clock time. This skill is the dispatch discipline that lets one operator run multiple AI agents the same way. Each agent works its own task in isolation; the operator is the rest interval that coordinates the next round; total throughput beats sequential single-agent work, provided the isolation, scope, and merge discipline hold.

Parallel agents on the same git repo collide on shared state (caches, pyproject, lock files) and lose their session learnings unless you build the prompt for isolation. This skill is a prompt-template generator plus a falsifier checklist for catching prompt-quality drift before spawning.

**Core principle:** every dispatched agent gets a self-contained prompt with (a) **isolated worktree by default** (per-agent `.git` index, caches, optional venv), (b) baseline capture (test count, failing-test list, HEAD SHA, lint state), (c) explicit scope + out-of-scope, (d) commit-only no-push, (e) post-session log to `localonly/session-logs/`. Without all five, agents drift or collide.

**REQUIRED BACKGROUND:** You MUST understand `dispatching-parallel-agents` (the general dispatch pattern). This skill adds isolation discipline and post-session logging.

## When to use

Spawn isolated agents when:

- 2 or more tasks have non-overlapping file sets
- Each task fits in <90 min of agent wall-clock
- The operator's critical-path work is NOT one of the agents (operator-bottleneck case kills the parallel speedup)
- Git worktrees are set up per agent (the default; see Worktree discipline below)

Do NOT spawn isolated agents when:

- The bottleneck is operator writing or judgment work (agents don't unblock that)
- Tasks share files or review-gated config (pyproject mutmut section, calibration logs, prose-locked docs)
- Operator is mid-incident, mid-MVP-push, or otherwise has no review bandwidth
- The work needs full-system context the prompt can't carry

## Quick reference: the five-pillar prompt

Every prompt MUST contain:

1. **Worktree setup** as the first command the agent runs (or a documented exception when scope is single-file and read-mostly)
2. **Baseline capture** (test count, **failing-test names**, HEAD SHA, lint state, mypy state if applicable)
3. **Scope + out-of-scope** as explicit file lists, including review gates
4. **Commit + DO NOT PUSH** discipline; operator pushes at end of batch
5. **Post-session log** to `localonly/session-logs/<date>-agent<N>-<slug>.md`

Plus six cross-cutting safeguards:

- Working directory stated; `Cwd` parameter required; no `cd a && b`
- Iron laws referenced (trainer, safe-terminal, wei-voice or equivalent, async-handoff)
- Vibe-tier declared after trainer loads (cuts coaching rounds for mechanical work)
- Verification compares against captured baseline list, not hardcoded numbers (count + failing-test names)
- Wall-clock estimate stated up front so the operator can plan coordination
- Multi-phase batches: Phase 1 = sequential scaffold (one agent), Phase 2+ = parallel features after the operator confirms Phase 1 lands. The `Phase:` header field in the prompt template enforces ordering.

## Role archetypes

Three archetypes cover the typical workload. Each is a thin overlay on the base agent prompt, documented at `references/role-overlays.md`.

| Archetype | Use case | Verification shape |
|---|---|---|
| `code` (default) | Implement a feature, fix a bug, refactor with TDD | Tests pass, lint clean, baseline-failing-test list unchanged |
| `sweep` | Narrow-scope text or file edits across many files (em-dash sweep, voice-rule audit, import rename) | grep-based residual check + tests still pass |
| `prose-audit` | Voice-rule or corpus-grounded prose review and rewrite (cover letter, README, doc) | `deai-scan` score at or below corpus baseline + spot-check |

Add a `Role:` header field to the agent prompt to declare the archetype. The base template at `templates/agent-prompt.md` is `code`-flavored by default; the overlays document the substitutions for `sweep` and `prose-audit`.

## Use the template

The prompt template is at `templates/agent-prompt.md`. Copy, fill the bracketed sections, paste into a fresh chat. The session-log template is at `templates/session-log.md`; the agent uses it automatically per the prompt instructions.

For handing off the *orchestrator role itself* to a fresh chat when the current orchestration chat hits context-window pressure or the IDE slows under accumulated history, see `templates/orchestrator-handoff-prompt.md`. The orchestrator handoff is a distinct pattern: it transfers a long-running coordination role rather than spawning a scoped worker. Same five-pillar discipline plus eight orchestrator-specific falsifiers (HO1-HO8 in the template).

## Run the falsifier checklist before spawning

Before pasting the prompt to a fresh chat, run the falsifier checklist at `references/falsifier-checklist.md`. Each falsifier is a known prompt-failure mode observed in real sessions. Resolve every High-severity item; document any deferred Med/Low items in the agent's "Surprises" log section so the next iteration of the prompt can address them.

## Worktree discipline

Default: every dispatched agent works in its own git worktree at `<project>/.worktrees/<task-slug>/`. The worktree gives the agent its own `.git/index.lock`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, and (optionally) `.venv/`. Without a worktree, parallel agents collide on shared state.

### Directory-selection priority

Pick the worktree directory in this order:

1. **Existing `.worktrees/` directory.** Use it. (Hidden, project-local; the strong default.)
2. **Existing `worktrees/` directory.** Use it. (Visible alternative; some projects prefer it.)
3. **CLAUDE.md or AGENTS.md preference.** If the project's agents doc names a worktree directory, use that without asking.
4. **Ask the operator.** No directory exists and no doc preference: ask whether to create `.worktrees/` (project-local hidden) or a global location like `~/.config/superpowers/worktrees/<project>/`.

Borrowed from `obra/superpowers-skills` `using-git-worktrees`. The priority matters because mixing locations across batches creates ghost worktrees the operator forgets to clean up.

### Gitignore pre-flight (project-local only)

Before creating a project-local worktree, verify the directory is gitignored:

```bash
git -C <project> check-ignore -q .worktrees 2>/dev/null
```

If not ignored, add the directory to `.gitignore` and commit before proceeding. Skipping the pre-flight risks the next `git add .` pulling worktree contents into the main checkout, which the operator may not catch until much later. Global worktree locations outside the project skip this check.

### Project-setup auto-detect

After `git worktree add`, run the right install command based on the manifest in the worktree, not based on operator memory of which language is at play:

```bash
[ -f package.json ] && npm install
[ -f Cargo.toml ] && cargo build
[ -f pyproject.toml ] && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
[ -f requirements.txt ] && python -m venv .venv && .venv/bin/pip install -r requirements.txt
[ -f go.mod ] && go mod download
```

The first command that matches wins; the agent runs only one install path. Worktree-local venv is required for any Python project that mutates `.venv`; without it, the shared venv is corrupted mid-flight and the operator's parallel work breaks.

### Clean-baseline verification

Before declaring the worktree ready, run the project's test suite once to verify a green baseline. If tests fail at this step, the agent stops and reports rather than attributing the failures to its own work later. Pattern from `using-git-worktrees`.

### Worktree setup, compact form

The agent's first-step block, end to end:

```bash
git -C <project> check-ignore -q .worktrees 2>/dev/null || { echo "add .worktrees/ to .gitignore first"; exit 1; }
git -C <project> worktree add <project>/.worktrees/<task-slug>
# Auto-detect install (see above)
# Run baseline tests; report count + failing-test names
```

All subsequent commands run with `Cwd=<project>/.worktrees/<task-slug>`.

**Same-tree exception:** when scope is single-file and read-mostly AND the operator has no parallel work, skip the worktree. Document the skip in the prompt's worktree section so the agent understands the deliberate choice. The H5 falsifier check still applies, with the same-tree note as the resolution.

### Merge-back (operator)

End of batch:

```bash
git -C <project> merge <agent-branch>
git -C <project> worktree remove <project>/.worktrees/<task-slug>
```

## Race-condition reference

Parallel agents in the same checkout collide on:

| Shared state | What collides | Worktrees solve? |
|---|---|---|
| `.git/index.lock` | Concurrent commits race; second fails | Yes |
| `.pytest_cache/` | Concurrent pytest corrupts cache, flakes | Yes |
| `.ruff_cache/` and `.mypy_cache/` | Concurrent runs stale or slow | Yes |
| `.venv/` site-packages | Concurrent `pip install` corrupts | Only with worktree-local venv |
| `mutants/` and `.mutmut-cache/` | Concurrent mutmut destroys state | Yes |
| `pyproject.toml`, lock files | Concurrent edits conflict | Yes (merge at end) |

## Batch aggregation (end of parallel batch)

After all dispatched agents return, the operator runs a batch-aggregation pass before deciding to push. The playbook lives at `templates/batch-aggregation.md` and covers:

- Reading the N session logs in order
- Cross-checking commits against the captured baseline failing-test list (per-agent and merged)
- Merge-order decision (does Agent A's commit cleanly precede Agent B's; which branch goes first)
- Failure decision matrix (retry vs escalate vs skip for any agent that returned blocked or partial)
- Final-review subagent dispatch via `requesting-code-review` for the merged batch
- Push (or PR) decision

The aggregation pass is the operator's job, not the agents'. Budget roughly 10 minutes per agent for review and integration on top of the agent's own wall-clock.

## Runtime portability

The prompt template assumes Cascade-on-Windsurf tool semantics (`run_command`, `Cwd` parameter, `read_file` and `edit` tools, gitignored-write guard). For Claude Code, Cursor, Codex, or Gemini CLI, tool names and constraints differ; the per-runner mapping lives at `references/runtime-portability.md`. The template's first-steps block should be adapted per runner.

## Common mistakes

- **Hardcoded test counts in verification.** "Expected: 172 passed" breaks if any other agent changes test count between baseline and verify. Capture baseline at agent start; compare against captured count, not a hardcoded number.
- **Symlink confusion.** If the project has `CLAUDE.md` symlinked to `AGENTS.md`, the prompt must name one file as canonical or the agent edits both with conflicting diffs.
- **Push enabled by default.** Agents trained on public repos default to push after commit. The prompt must explicitly forbid push and explain the batched-merge model.
- **CI version skew.** Local mypy passes on Python 3.14; CI runs 3.11/3.12. Prompts that lift gates must note the skew so the operator watches CI after merge.
- **Loose "fix if it's a real bug" instructions.** Type errors and small refactors often slip from "type-only" to "behavior-changing." Vibe-careful tasks need a crisp source-edit definition (see `templates/agent-prompt.md` Vibe-careful protocol section): comment-only suppression with error code is allowed; non-comment changes require operator review.
- **Shared-venv mutation.** Dep-touching agent (`pip install`) without a worktree-local venv breaks operator's parallel work. Always pair `pip install` with worktree-local venv setup.
- **Structured-file edits without validation.** TOML, YAML, JSON edits should parse-and-validate before commit. A botched `pyproject.toml` leaves the project un-buildable until rollback.
- **Baseline by count alone.** "172 passed before, 172 passed after" passes verification but masks a swap (pre-existing failure left unfixed while new failure introduced). Capture failing-test names too.
- **Verification scope wider than sweep scope.** If the agent's verification grep covers directories that weren't in the Task's in-scope list, the agent fails verification when those directories have residuals it was told not to touch (or, worse, decides to silently fix them, violating scope). Worked example 2026-05-18: Agent 1's em-dash verification grep included `voc/`, but `voc/` was out-of-scope for the sweep. (Saved by `voc/` being em-dash-clean already; would have been a false-failure or scope-creep otherwise.) Either narrow the verification or add explicit "expected residuals in `<dir>`" notes.
- **Operator setup commands fragility.** When Cascade provides setup commands (pipeline runs, env exports, mkdir) to the operator alongside agent prompts, apply the same discipline as `run_command` rules: one logical command per line, no angle-bracket placeholders (zsh parses `<foo>` as input/output redirection), no multi-statement `;` chains, no implicit pwd assumptions. Pattern observed 2026-05-18: a multi-line block containing `export GITHUB_TOKEN=<your_pat>   # if you have one; else expect ...` triggered zsh parse error near `else`; the operator had also run an earlier command from `~` thinking they were in the project dir, leading to a 15-min silent pipeline failure. Single-line, full-absolute-path, no-placeholder-special-chars commands prevent both.
- **Parallel `run_command` Cwd race in same-tree dispatch.** When the agent issues multiple `run_command` calls in a single parallel batch and a sibling agent is concurrently active in the same checkout, some calls land in the wrong working directory. Symptom: one git call in the batch returns a valid SHA, a sibling git call in the same batch reports "not a git repository", and `ls tests/foo.spec.js` reports the file missing while subsequent sequential calls confirm it exists. Worked example 2026-05-18: Agent E (TC-9030 oracle-pilot move on `mailchimp-r-and-a-qa-suite`) dispatched without a worktree (H5 failure); the parallel batch failed sporadically during baseline capture, recovered by switching to sequential calls. A separate symptom of the same root cause: `git add` succeeded but the subsequent `git commit` failed with "no changes added to commit" because a sibling agent's concurrent git operation cleared the index between the two calls. Prevention: comply with H5 (worktree per agent). Defense-in-depth: sequence baseline-capture calls instead of parallelizing them, and combine `git add` + `git commit` into a single script invocation when same-tree is unavoidable.

## Red flags, stop and revise the prompt

- The agent must read >5 files to understand scope. (Scope is too broad.)
- The agent must make a judgment call the prompt does not preauthorize. (Add explicit authorization or stop-and-report.)
- Two agents' file sets overlap by any file. (Collision risk; pick one or use worktrees.)
- The verification step does not test the work product (only tests adjacent state).
- The session-log instructions are absent or vague. (Defeats the iteration loop.)
- The prompt doesn't specify worktree setup or document the same-tree exception. (Default missing.)
- The agent will `pip install` and the prompt doesn't require worktree-local venv. (Shared-venv mutation risk.)
- The prompt has a vibe-careful tier but no crisp source-edit definition. (Slippage risk.)
- The prompt edits structured files (TOML, YAML, JSON) but has no parse-validate step. (Botched-edit risk.)
- The verification grep checks files broader than the Task's in-scope list, with no expected-residual note. (False-failure or scope-creep risk.)
- Operator setup commands (alongside the agent prompts) contain angle-bracket placeholders, `;`-separated statements, or implicit pwd assumptions. (Copy-paste fragility risk on the operator's side.)
