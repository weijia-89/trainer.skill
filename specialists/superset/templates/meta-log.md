# Meta log template

The meta log is the weekly artifact for the meta agent (Layer 3 of the three-layer agent architecture; see `SKILL.md`). One file per project per week at `<project>/localonly/meta-logs/<YYYY-WW>-meta.md` where `<YYYY-WW>` is the ISO 8601 year-week number (e.g., `2026-W21-meta.md` for the week starting Monday 2026-05-18). Meta lives one week by default (refresh sooner on IDE slowdown).

Meta does pattern recognition across daily logs and surfaces process-improvement candidates. Meta does not dispatch workers and does not coach the operator in real-time.

This template ships annotated. Copy, fill, remove inline guidance before first surfacing the meta log for the week.

---

## Schema

The meta log has five sections in this order:

0. **Meta hand-off summary** (written by outgoing meta on refresh; absent on week-start)
1. **YAML front-matter** (week scope, daily-log inventory, meta-chat identity)
2. **Running pattern observations** (3-N patterns this week, with evidence citations)
3. **Issue inventory** (collisions, misses, prompt-quality drift)
4. **Process-improvement candidates** (concrete skill-edit suggestions)
5. **End-of-week summary** (carries to next week, retrospective)

---

## Section 0, Meta hand-off summary (top of file, on refresh)

```markdown
# Meta hand-off summary, <YYYY-MM-DD HH:MM>

**Headline:** <one sentence: where the week stands>

**Top 3 running patterns (this week):**
1. <pattern> (count: N daily-logs, severity: high | medium | low)
2. ...
3. ...

**Top 3 skill-edit candidates surfaced this week:**
1. <candidate: file + proposed change>
2. ...
3. ...

**Carries to next week:**
- <pattern needing more days of evidence before action>
- <skill-edit candidate awaiting operator sign-off>

**Pointers:**
- This weekly meta log: `localonly/meta-logs/<YYYY-WW>-meta.md`
- Daily logs covered: `localonly/daily/<dates>.md`

---
```

---

## Section 1, YAML front-matter

```yaml
---
project: <project-name>
week_start: <YYYY-MM-DD>             # Monday of the week (or operator-chosen anchor day)
week_end: <YYYY-MM-DD>               # week_start + 6 days
operator: <name>
meta_chat_id: <slug or chat identifier; helps tie patterns back to a specific meta session>
refresh_count: <integer; 0 on week-start, increments each refresh>

daily_logs_covered:
  - <YYYY-MM-DD>                     # e.g., 2026-05-19
  - <YYYY-MM-DD>
  # ...one entry per daily log this week

worker_dispatch_count:               # rolled up from daily-log manifests
  total: <N>
  by_role:
    code: <N>
    research: <N>
    sweep: <N>
    prose-audit: <N>
  by_status:
    DONE: <N>
    FAILED: <N>
    BLOCKED: <N>

carries_from_previous_week:
  - <pattern or item carried over>
---
```

---

## Section 2, Running pattern observations

Each observation is a structured entry: pattern claim, evidence citations from daily logs, count, severity, and a "what this might mean" interpretation.

```markdown
## Pattern observations

### P1, <short pattern name>

**Claim:** <one-sentence pattern statement>

**Evidence:**
- `localonly/daily/2026-05-19.md` § Agent A-fdroid-research (the consumer-precondition halt)
- `localonly/daily/2026-05-20.md` § Wave 2 narrative (similar halt on a different research-precondition agent)
- `localonly/daily/2026-05-21.md` § Agent B-license-edit status BLOCKED entry

**Count:** 3 daily logs this week
**Severity:** medium (no production damage, but operator-time cost; estimated ~45 min total this week)
**What this might mean:** the `research-complete` precondition vocabulary is too coarse; sub-precondition tiers (research-drafted vs research-signed-off) may be needed.

**Action:** flag as a candidate skill edit for `superset.skill/templates/high-stakes-list.yaml` precondition vocabulary; carry to next week if pattern recurs.

### P2, <next pattern>

...
```

---

## Section 3, Issue inventory

Distinct from patterns: discrete incidents this week with attribution and resolution status. The audit trail.

```markdown
## Issue inventory

### I1, <short incident name> (<YYYY-MM-DD>)

**What happened:** <one-paragraph; cite the daily-log entry>
**Attribution:** <which agent layer; which skill clause was active; what gate failed>
**Resolution:** <fixed in-session | flagged for next dispatch | rolled into pattern Pn | unresolved>
**Cross-references:** <links to daily-log sections, prior week's meta log if related>

### I2, ...
```

---

## Section 4, Process-improvement candidates

Concrete, actionable. Names specific files and proposed diffs where possible. Operator decides which land.

```markdown
## Process-improvement candidates

### C1, <short candidate name>

**Anchor:** Pattern P1 or Incident I1 (the evidence that motivates this candidate)
**Target file:** `<project>/<path>` or `superset.skill/<path>` or `trainer.skill/<path>`
**Proposed change:** <one-paragraph; ideally a sketch of the diff or new section>
**Operator-decision tier:** <small (skill body wording) | medium (new template) | large (new behavior + falsifier + template)>
**Estimated wall-clock:** <N minutes for the operator to review + sign off>

### C2, ...
```

Operator may sign off immediately (Cascade implements next session), defer (carry to next week's meta log), or reject (log rejection with reason; do not re-surface for N weeks).

---

## Section 5, End-of-week summary

```markdown
## End-of-week summary

**Headline:** <one-line "this week was X">

**Pattern count:** N observed this week; M carry over from previous week; K resolved this week.

**Issue count:** N this week (severity breakdown).

**Process-improvement candidates:** N proposed; M signed off; K deferred to next week.

**Worker dispatch rolled up:**
- Total workers dispatched: N
- Completed: N
- Failed: N (failure-mode breakdown)
- Blocked carrying over: N

**Operator review wall-clock this week:** N hours total (compare against load-band target from the daily logs).

**Carries to next week:**
- <patterns needing more evidence>
- <skill-edit candidates awaiting sign-off>
- <unresolved issues>

**Meta-chat health:** <refresh_count this week; context-window state at week-end; whether new meta chat is recommended at week-start>
```

---

## Annotated worked example, buds week of 2026-05-19

```markdown
---
project: buds
week_start: 2026-05-19
week_end: 2026-05-25
operator: wei
meta_chat_id: meta-buds-2026-05-19
refresh_count: 0

daily_logs_covered:
  - 2026-05-19
  - 2026-05-20
  - 2026-05-21

worker_dispatch_count:
  total: 7
  by_role:
    code: 4
    research: 2
    sweep: 1
  by_status:
    DONE: 5
    FAILED: 0
    BLOCKED: 2

carries_from_previous_week: []
---

## Pattern observations

### P1, Research-precondition halts cluster on FSL / IP topics

**Claim:** Three agents this week halted to BLOCKED status waiting for a research-complete precondition on f-droid / FSL / IP-protection deliverables.
**Evidence:**
- `localonly/daily/2026-05-19.md` § Agent B-license-edit (BLOCKED until A-fdroid-research signed off)
- `localonly/daily/2026-05-20.md` § Agent C-ip-protection-priorities (BLOCKED waiting for separate research)
- `localonly/daily/2026-05-21.md` § Agent D-readme-strategy (BLOCKED on same f-droid research)
**Count:** 3 daily logs
**Severity:** medium
**What this might mean:** research-complete is doing real work; the vocabulary is correct; the cluster suggests the operator should pre-stage research agents at week-start for IP topics rather than letting them block downstream consumers.

**Action:** flag as candidate C1 below.

## Process-improvement candidates

### C1, Pre-stage research agents at week-start for IP topics

**Anchor:** Pattern P1
**Target file:** `buds/AGENTS.md` orchestration section + `superset.skill/SKILL.md` "Daily-log-driven dispatch" example
**Proposed change:** add a "research-pre-staging" convention to the orchestration section: when the week's plan touches LICENSE, README, or docs/strategy, dispatch the research agent on Day 1 as a Wave 0 standalone, even if no consumer is queued yet, so the deliverable is ready when the consumer becomes relevant.
**Operator-decision tier:** medium (new convention, no new file)
**Estimated wall-clock:** 20 min review + sign-off
```

End of template. Remove the annotated worked example before first surfacing the meta log for a real week; keep only the populated sections.
