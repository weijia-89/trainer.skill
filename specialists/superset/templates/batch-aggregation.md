# Batch aggregation template

The operator runs this playbook after all dispatched agents in a parallel batch return. Runs before any push or PR. Budget ~10 minutes per agent on top of the agent's wall-clock.

This is the operator's job, not the agents'. Agents have already committed inside their worktrees and written session logs; the operator decides what to ship.

---

## Step 1: Read N session logs in order

For each dispatched agent N:

```bash
cat <PROJECT>/localonly/session-logs/<DATE>-agent<N>-<task-slug>.md
```

What to look for:

- **Outcome line.** Success, partial, or blocked? Partial and blocked agents go through the failure decision matrix below.
- **Surprises section.** Did the agent encounter prompt-assumptions that diverged from reality? Capture for the next falsifier-checklist iteration.
- **Files touched.** Cross-check against the agent's stated Owned-paths in the prompt. Drift means scope-creep; the next batch's prompts need tighter scopes.
- **Commit SHA(s).** Confirm the SHA list matches what you see in the worktree branch.

If a log section is missing or the agent crashed before writing it, the worktree itself is the source of truth. `git log` on the branch tells you what was committed.

---

## Step 2: Cross-check failing-test lists

Per the baseline-capture-then-compare discipline, every agent produces two files in `/tmp`:

```
/tmp/<task-slug>-baseline-failing.txt
/tmp/<task-slug>-after-failing.txt
```

For each agent:

```bash
diff /tmp/<task-slug>-baseline-failing.txt /tmp/<task-slug>-after-failing.txt
```

Expected: no diff. The agent did not introduce new failures and did not fix unrelated pre-existing failures (which would mean scope-creep).

After reviewing all agents, run the suite on the would-be-merged state:

```bash
# In a scratch branch off main
git checkout -b scratch/<batch-slug>
for branch in <agent-branches>; do git merge --no-ff $branch; done
.venv/bin/pytest --timeout 30 -q 2>&1 | tail -5
```

If the union test count differs from the sum of agent baselines, an agent introduced a hidden conflict. Bisect by reverting one agent at a time.

---

## Step 3: Merge-order decision

For agents with overlapping or adjacent file sets:

- Identify the dependency direction. Agent A writes a new module; Agent B imports it. Merge A first.
- For Phase-tagged work, merge Phase 1 before Phase 2. The `Phase:` field in each agent's prompt header tells you the intended order.
- For agents in the same Phase with non-overlapping files, merge order does not matter; pick alphabetical for reviewer-cognitive simplicity.

State the order in your coordination notes:

```
Merge order: agent-A, agent-C, agent-B (A creates contracts B imports; C is independent)
```

---

## Step 4: Failure decision matrix

For each agent that returned partial, blocked, or with a STOP-and-report message:

| Agent state | Decision |
|---|---|
| Blocked on a question only the operator can answer | Answer; re-dispatch agent with the answer added to its prompt; one retry max. |
| Blocked on a missing dependency or upstream agent | Wait for the upstream agent's branch to land; re-dispatch with the updated baseline. |
| Partial: completed some deliverables, stopped on others | If completed work is valuable on its own, merge it and re-dispatch a follow-up for the rest. Otherwise rollback the worktree and rescope. |
| Crashed or returned incoherent state | Rollback the worktree (`git worktree remove`), salvage the session log for falsifier-checklist updates, do not re-dispatch with the same prompt. Rewrite first. |
| Returned with scope-creep (touched files outside Owned-paths) | Cherry-pick only the in-scope commits; reject the rest. Add the out-of-scope drift to next batch's falsifier review. |

Two retries per agent is the cap, matching the trainer's coached-override pattern. Beyond that, the prompt is wrong; rewriting beats redispatching.

---

## Step 5: Final-review subagent dispatch

After the scratch merge is green, dispatch a code-review subagent against the union diff. Use the `requesting-code-review` skill's template at `~/.claude/skills/requesting-code-review/`.

Pass:

- **BASE_SHA:** the pre-batch SHA (the operator's rollback target, stated in the coordination notes)
- **HEAD_SHA:** the scratch-merge SHA
- **DESCRIPTION:** one paragraph describing what each agent did
- **PLAN_OR_REQUIREMENTS:** the top-level task description that motivated the batch

The reviewer's output goes in the operator's coordination notes alongside the merge-order decision.

---

## Step 6: Push or PR

Two paths:

- **Push directly:** for trunk-based projects with no PR gate. Fast-forward `main` to the scratch-merge SHA, push, watch CI. Rollback path: `git push origin <pre-batch-SHA>:main --force-with-lease` if CI fails irrecoverably.
- **Open a PR:** for projects with mandatory PR review. Push the scratch branch, open a PR, link the session logs (rendered to a gist or pasted into the PR description), and the reviewer's report.

For PR-bound work, use `gh pr create --body-file <path>` to avoid multi-line shell quoting (safe-terminal Tier-1 #1).

---

## Step 7: Cleanup

After the merge lands (push or PR-merge):

```bash
for slug in <task-slugs>; do
  git worktree remove <project>/.worktrees/$slug
  git branch -D agent-$slug   # if branch is not needed for history
done
```

Verify with `git worktree list` that no orphans remain.

---

## Notes

- The aggregation pass is the operator's bottleneck. Batches larger than 3-4 agents make this pass take longer than the agents themselves take. Cap batches accordingly.
- Capture session-log surprises into the next falsifier-checklist iteration. The checklist grows by observing real failure modes; the aggregation pass is when those modes are visible.
- Rollback SHA: state it in your coordination notes at the start of the batch ("If anything goes sideways, `git reset --hard <SHA>` returns to pre-batch state"). The aggregation pass references this if the merge fails.
