# Phase 3 behavioral A/B spec (Criterion (c))

**Purpose.** Validate behavioral equivalence between the original superset SKILL.md and a compressed v0.7.1-draft body. Run by a fresh-context chat reading this spec and the candidate compressed body.

**Scope.** This is criterion (c) in the three-criterion fidelity protocol. Criteria (a) structural-preservation and (b) section-similarity are tooled separately in this directory; (c) is the behavioral check that catches drift those tools cannot.

## Why (c) cannot be tooled like (a) and (b)

(a) and (b) operate on the document. (c) operates on what the document produces when read by an agent. There is no way for the document to test itself; only an agent reading it can produce evidence about behavioral equivalence. Hence the asynchronous, fresh-chat protocol.

## Equivalence criterion

Two SKILL.md bodies are behaviorally equivalent if a fresh agent reading either one and given the same task produces:

1. **Same number of agents in the dispatch.** Off by one is acceptable if and only if the difference is explained by a documented decision (e.g., "compressed body led me to consolidate agents X and Y because their owned_paths overlap").
2. **Same role archetypes assigned.** Code vs. research vs. prose-audit vs. sweep assignments match.
3. **Same number of phases.** Phase boundaries fall at the same producer-consumer transitions.
4. **All H1-H15 + PV-1 + S1 falsifiers triggered or not-triggered consistently.** A falsifier that fires for the original body must also fire for the compressed body (and vice versa) when given the same near-miss input.
5. **Same worktree-vs-same-tree-exception-vs-no-git-exception choices.** When given a project state that should trigger Shape A, both bodies produce Shape A; same for Shape B and Shape C.

**Allowable differences (NOT equivalence violations):**

- Worker prompt prose differs in wording while producing structurally equivalent prompts
- Section ordering in the daily-log manifest differs (as long as schema fields are equivalent)
- Agent names differ (since they're orchestrator-chosen)
- Time estimates differ

## Test protocol (5 task-type dispatches)

The fresh-context chat runs the following 5 dispatches twice each: once with the original SKILL.md as the only superset reference, once with the compressed v0.7.1-draft. Then compares outputs against the equivalence criterion.

### Task 1: 3-agent parallel-worker batch on git repo

**Input:** "Dispatch 3 parallel workers to add coverage to module X in <example-e-commerce-website project>. Each worker takes a disjoint slice of the codebase. Wei has not pre-decided phase ordering."

**Expected behavior:** Produces a daily-log manifest with 3 agents, all worktreed (Shape A), all single phase. owned_paths disjoint. signals: [] declared per agent.

**Equivalence test:** Original and compressed bodies both produce a 3-agent / 1-phase / Shape A / disjoint owned_paths manifest. Differences in agent names / wording / time estimates are allowed.

### Task 2: 2-agent batch with producer-consumer dependency

**Input:** "Dispatch a 2-agent batch where worker A produces a registry file and worker B consumes that registry. Project is <example-e-commerce-website project>."

**Expected behavior:** Daily-log manifest with 2 agents in 2 phases. Phase 1 has worker A with produces: [registry-path]. Phase 2 has worker B with consumes: [registry-path]. H15 validation PASSES.

**Equivalence test:** Original and compressed both produce 2-phase / producer-consumer / H15-valid manifest.

### Task 3: Same-tree exception (Shape B)

**Input:** "Dispatch a single research agent to audit <superset.skill SKILL.md> for falsifier-checklist completeness. Read-mostly, single file, no other parallel work."

**Expected behavior:** Same-tree exception declared, all four preconditions stated, escalation-void clause included. NO worktree setup.

**Equivalence test:** Both bodies produce the same Shape B declaration with the same four preconditions.

### Task 4: No-git exception (Shape C)

**Input:** "Dispatch 2 parallel agents on <ai-governance-report project>. The project has no .git/ directory (it's a localonly research workspace, not a git repo)."

**Expected behavior:** No-git exception declared (Shape C). Parallel-collision-mitigation strategy explicit (disjoint owned_paths via H11). NO worktree setup attempted.

**Equivalence test:** Both bodies produce Shape C with disjoint owned_paths mitigation.

### Task 5: H14 near-miss (artifact-existence)

**Input:** "Dispatch worker A to produce file lib/oracle/metric-registry.js in <mailchimp-r-and-a-qa-suite project>. Note: that file already exists with current-baseline metadata."

**Expected behavior:** Validator fires H14 ("would produce X but that file already exists"). Orchestrator either (a) marks the manifest retro_authored: true if work was already done, or (b) chooses overwrite/v2/skip and documents.

**Equivalence test:** Both bodies trigger H14 and surface the choice point. The specific resolution may differ as long as both surface it.

## Measurement procedure

For each task:

1. Open a fresh-context chat with ONLY the candidate body (original or compressed) accessible as superset.
2. Run the task input verbatim.
3. Capture the full output (daily-log manifest, agent prompts, all stated decisions).
4. Score against the equivalence criterion bullets above.
5. Record results in a comparison table.

The comparison table has columns: task # / bullet # / original output / compressed output / equivalence verdict (yes / no / partial). 5 tasks × 5 bullets = 25 cells.

Equivalence is declared if >= 23 of 25 cells PASS (>= 92% — speculative prior, refine after first run).

## Fail-safe rollback

If equivalence fails (< 92% cell pass), DO NOT promote the compressed body. Roll back to the prior version. Document the failure modes in `localonly/orchestration/<date>-phase3-ab-failures.md`. Revise the compressed draft to address those modes, then re-run.

## Cost estimate

- 5 tasks × 2 dispatches each = 10 dispatches
- Each dispatch ~5-10 minutes of fresh-chat agent time
- Plus ~30 minutes for the comparator chat to write the comparison table
- Total: ~80-120 minutes of fresh-chat time

## Authored

- Spec authored 2026-05-19 by the superset skill-maintainer chat as part of v0.7.0 Phase 3 compression infrastructure.
- Designed for a fresh-context chat to execute. The skill-maintainer chat does NOT self-execute (the test would be circular: the same chat that authored the compression cannot validate its own behavioral equivalence).

## Open questions for the fresh chat that runs this

1. Should the 5-task suite expand to cover more falsifier classes (M-series too, not just H)?
2. Is 92% a defensible equivalence floor or should it be higher (e.g., 95%)?
3. Should partial-equivalence (the "partial" verdict) count as half a cell or zero?
4. If the original body is itself ambiguous on a given task, how is "equivalence" defined?

These are decisions for the fresh chat to make and document before running, then revisit after.
