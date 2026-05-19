# Worker session-log template (compaction-ready format)

Each dispatched worker writes its own session log at `<project>/localonly/session-logs/<YYYY-MM-DD>-agent<X>-<task>.md` on task close. The orch ingests these on worker DONE status and compacts them into the daily log's Section 3 (per-agent entries) and the daily log's "For meta" appendix.

This format prioritizes compaction. The first three sections survive ingestion; Section 4 is compactable.

## Schema

```markdown
# Worker session log, agent <X>, task <slug>, <YYYY-MM-DD>

## 1. Status

1-2 lines. One of: `shipped` (clean DONE), `blocked` (BLOCKED with reason), `in-flight` (still running; include PID + log path if detached via `/run-long-job`), `failed` (FAILED with caught failure surfaced).

Example:
- `shipped. HEAD f3a9b21. Commits: f3a9b21, e8c3d44.`
- `blocked. Waiting on A-fdroid-research signoff (precondition: research-complete).`
- `in-flight. PID 47291, log /tmp/agent-X-2026-05-19.log. Expected ~25 min remaining.`

## 2. Key learnings

≤5 bullets, bold title each. Durable patterns, gotchas, or process notes the orch should carry forward to next workers or to skill edits. Skip pure noise (one-off command output, transient state).

- **<bold title>:** <one-sentence learning that generalizes beyond this task>
- **<bold title>:** ...

## 3. Audit findings

≤5 bullets if any. Each tagged with severity (P0 / P1 / P2) and target audience (orch / meta / Wei). Each must be actionable.

- **[P1, orch]** <actionable finding; what the orch should do next>
- **[P2, meta]** <pattern signal for weekly meta review>
- **[P0, Wei]** <decision-level finding requiring operator sign-off>

Omit this section entirely if there are no findings.

## 4. Details

Everything else: commands run, files touched, decisions made, error traces, intermediate scratch. The orch may compact this away on hand-off; the three sections above are what survives ingestion.

- **Files touched:** <list>
- **Files READ:** <list>
- **Commands run:** <list of consequential commands>
- **Decisions made:** <list with one-line rationale>
- **Errors encountered:** <list with cost in wall-clock min>
- **Tool + skill usage notes:** <which skills loaded; which were noise>
- **Prompt-improvement signal:** <what would have made this prompt better>
```

## Compaction discipline

The orch deduplicates Key Learnings against the running notes-for-next-orch section. Once a learning is ratified into a skill (the meta agent's process-improvement candidate gets accepted by Wei), the corresponding bullet here can be dropped as deduplicated; the skill itself encodes the rule now.

Audit findings with P0/P1 severity propagate immediately to the daily log's running notes (orch acts on them this session). P2 findings carry to the daily log's "For meta" appendix for weekly review.

Section 4 (Details) is purely for the worker's own audit trail and for hand-off-time deep-context if needed. The orch may discard it on compaction; the raw worker session-log file at `localonly/session-logs/` remains on disk as the historical record.

## What the orch does with a worker session log

On worker DONE:

1. Read sections 1-3 (skip section 4 unless compaction needs it).
2. Append to daily log Section 3 (per-agent entries): a one-line status + the bulleted Key Learnings + any P0/P1 audit findings.
3. Append P2 audit findings to daily log's "For meta" appendix.
4. Update manifest STATUS field for this worker to DONE.
5. If Key Learnings include something that fires across 2+ workers this week, prefix it `PROMOTE?` and copy to the "For meta" appendix as a skill-edit candidate.
