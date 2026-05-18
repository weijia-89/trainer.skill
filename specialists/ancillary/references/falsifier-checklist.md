# Falsifier checklist for agent prompts

Run this before pasting an agent prompt into a fresh chat. Each item is a known prompt-failure mode observed in production sessions. Resolve every High-severity item before spawning.

## High-severity (must fix before spawn)

| # | Falsifier | Test | Fix |
|---|---|---|---|
| H1 | Prompt forbids push? | Search prompt for "do not push" or "DO NOT PUSH" | Add explicit no-push line; explain batched-merge model |
| H2 | Verification uses captured baseline, not hardcoded numbers? | Search for digit-then-passed (e.g. `172 passed`) outside the baseline-capture section | Replace with "test count >= baseline, 0 new failures" |
| H3 | Vibe-careful work has stop-and-report protocol for source edits? | If task touches non-trivial code, search for explicit "STOP" or "do not edit source" | Add the restricted-error-handling protocol from ancillary/SKILL.md |
| H4 | Out-of-scope list names review-gated files explicitly? | Read project's CLAUDE.md or equivalent review-gate list; cross-check against prompt's out-of-scope | Add every review-gated file to the list |
| H5 | Worktree setup is the first command, OR same-tree exception is documented? | Search prompt for `git worktree add` or explicit same-tree-exception note | Add worktree-setup block to first-step section |
| H6 | Dep-touching task creates a worktree-local venv? | If prompt has `pip install`, search for `python -m venv` in worktree path | Add worktree-local-venv block alongside worktree-setup |
| H7 | Baseline captures failing-test names, not just count? | Search for `FAILED` or `failing-test` in baseline-capture section | Replace count-only baseline with `tee + grep FAILED` pattern |
| H8 | Vibe-careful task has crisp source-edit definition? | If task tier > vibe-safe, search for explicit allowed/STOP list of edit types | Add Vibe-careful protocol section with allowed/STOP lists |
| H9 | `.worktrees/` gitignored before worktree creation? | Search for `git check-ignore -q .worktrees` in prompt's worktree-setup block | Add Step 0 gitignore-preflight block from agent-prompt template |
| H10 | Project-setup commands auto-detected from manifest, not hardcoded by operator? | Search for `[ -f package.json ]` / `[ -f Cargo.toml ]` / `[ -f pyproject.toml ]` in setup block | Replace hardcoded `npm install` or `pip install` with the auto-detect block |

## Medium-severity (should fix; document if deferred)

| # | Falsifier | Test | Fix |
|---|---|---|---|
| M1 | Working directory named with absolute path? Cwd-parameter rule stated? | Search for absolute path of project + "Cwd parameter" | Add both at top of First Steps |
| M2 | Symlink awareness (e.g. CLAUDE.md ↔ AGENTS.md)? | If project has symlinked docs, search for symlink callout | Name the canonical file; tell agent to edit only one |
| M3 | CI/local version skew called out? | If task touches CI gates (mypy, lint, etc.), search for "Python 3.1X" or "CI runs" | Add the local-vs-CI version skew note |
| M4 | Session-log instructions specific (path, shape, gitignore verified)? | Search for "session log" or "localonly/session-logs" | Add full instructions including path convention and shape link |
| M5 | Trainer-load + vibe-tier-declaration in First Steps? | Search for "trainer" + "tier" | Add both as steps 1-2 |
| M6 | Each agent's file set non-overlapping with sibling agents? | List files each agent touches; check for intersection | Re-scope one of the agents or use git worktrees |
| M7 | Structured-file (TOML, YAML, JSON) edit has parse-validate step? | If prompt edits `pyproject.toml`, `*.yml`, `*.yaml`, `*.json`, search for `tomllib`, `yaml.safe_load`, or `json.tool` | Add Structured-file validation block before commit |
| M8 | Stop-and-report channel is explicit? | Search for "emit a clear chat message and wait" or "no auto-escalation" | Add explicit stop-and-report channel note to decision protocol |
| M9 | Wall-clock estimate stated up front? | Search for "Expected duration" or "~N min" near the top | Add Expected duration line in Context section |
| M10 | Verification command file scope matches Task in-scope list, OR has explicit expected-residual note? | Compare verification grep / scan paths against the Task's in-scope file list | If verification is broader, narrow it OR add "expected: residuals in `<out-of-scope-dirs>`" note so agent doesn't false-fail or scope-creep |
| M11 | `Owned-paths:` table present when scope > 3 files OR sibling agents touch adjacent dirs? | Search prompt header for `Owned-paths:` table | Add the table from `templates/agent-prompt.md` Header-fields section listing each agent's owned dirs and out-of-scope sibling dirs |
| M12 | `Phase:` field stated when batches multi-phase (e.g. scaffold-then-features)? | Search prompt header for `Phase:` | Add the `Phase:` header; if Phase 2+, document explicitly that the agent waits for operator confirmation of Phase 1 lands before spawning |

## Low-severity (nice to have)

| # | Falsifier | Test | Fix |
|---|---|---|---|
| L1 | Skipping/punting policy stated? | Search for "skip" or "stop and report" or "punt" | Add explicit handling for unexpected work |
| L2 | Return format spec'd as code block, not prose? | Verify Return section uses fenced code block | Convert prose Return to fenced code block |
| L3 | Time estimate stated for operator's coordination planning? | Search for "wall-clock" or "minutes" or "duration" | Add estimate in agent task description |
| L4 | Hallucination check is real (network-enabled) or absent? | If prompt asks for verification of external packages, check whether agent has search/network tools | Either enable search tool reference or drop ritual check |

## Cross-cutting concerns

These apply across the whole batch of agents being spawned, not to any single prompt:

- **Shared state map.** Across all agent prompts you're about to spawn, list every file each will touch. Look for collisions. If two agents touch the same file, either re-scope or use git worktrees. Without isolation, second-to-commit may merge-conflict or stomp the first.
- **Operator review bandwidth.** Each spawned agent costs the operator one review pass at end of batch. If operator is mid-MVP-push or otherwise time-locked, cap the batch at 2-3 agents.
- **Coordination overhead.** The operator coordinates: tracking N chats, reviewing N commits, deciding merge order. Budget ~10 min per agent of operator time for coordination, on top of the agent's wall-clock.
- **Recovery path.** State the rollback SHA in your coordination notes to the operator. "If anything goes sideways, `git reset --hard <baseline-SHA>` returns to pre-batch state."
- **Operator setup commands.** Any commands Cascade provides to the operator alongside agent prompts (e.g., pipeline kickoff, env exports, dir setup) must follow the same shell-hazard rules as agent `run_command`: one logical operation per line, no angle-bracket placeholders (zsh parses `<foo>` as redirection), no multi-statement `;` chains, no implicit pwd. Pattern observed 2026-05-18: a multi-line `export GITHUB_TOKEN=<your_pat>` block triggered zsh parse error near `else`; the operator had also run an earlier `nohup` from the wrong directory, leading to silent 15-min failure. State full absolute paths and single-line commands.
- **Batch-aggregation template referenced.** The coordination notes Cascade hands the operator alongside the agent prompts must point at `templates/batch-aggregation.md` for the end-of-batch pass. Without it, the operator improvises the failure-decision matrix, the merge-order decision, and the final-review subagent dispatch; that improvisation is the gap where bad merges enter `main`.

## Meta: this checklist itself

The checklist was drafted from 12 falsifiers observed in session 2026-05-18 against two parallel-agent prompts (lodestar em-dash sweep + mypy stub uplift). v0.1.1 (same session) added 7 more falsifiers after adversarial review of the prompts themselves: H5-H8 (worktree + venv + failing-test-names + source-edit definition), M7-M9 (structured-file validation + stop-and-report channel + wall-clock estimate), and M10 (verification-scope-matches-task-scope) plus the operator-setup-commands cross-cutting concern. v0.1.2 (same session, afternoon): H5 fired in production. Agent E (TC-9030 oracle-pilot move on `mailchimp-r-and-a-qa-suite`) was dispatched same-tree without a worktree; a concurrent sibling agent (lib/ai-*.js Phase 2 work) raced the index, and parallel `run_command` batches in the same checkout exhibited a Cwd race. See SKILL.md "Common mistakes" for the parallel-batch Cwd race pattern, and treat H5 as the canonical fix.

v0.2.0 (2026-05-18): added H9 (`.worktrees/` gitignored before creation), H10 (project-setup auto-detected from manifest), M11 (`Owned-paths:` table for >3-file scope), M12 (`Phase:` field for multi-phase batches), and the batch-aggregation cross-cutting concern. H9 and H10 are direct borrowings from `obra/superpowers-skills` `using-git-worktrees`; M11 borrows the file-ownership table from `usemozzie/mozzie`'s CLAUDE.md.

Future iterations should:

1. After each batch of spawned agents, review their session logs for new failure modes not covered here.
2. Add new falsifiers as High/Med/Low rows.
3. Cull falsifiers that have not fired across 5+ batches (false-positive evidence).
