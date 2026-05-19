# Daily-log template

The daily log is the single coordination artifact for a multi-agent day on a project. One file per project per day, at `<project>/localonly/daily/<YYYY-MM-DD>.md`. The orchestrator (Cascade) and every dispatched agent read from and write to this file.

Replaces the older two-artifact pattern (per-batch dispatch manifest plus per-agent session log) with one document. Producer-consumer dependencies, in-flight status, end-of-day metrics, and per-agent session-log content all live here.

This template ships annotated. Copy the structure, fill bracketed sections, remove the inline guidance comments before the daily log is first surfaced to the user.

---

## Schema

The daily log has five sections in this order:

0. **Orch hand-off summary** (written by outgoing orch on rotation; absent on day-start)
1. **YAML front-matter manifest** (mandatory)
2. **Wave narrative** (mandatory; markdown)
3. **Per-agent entries** (each agent appends its subsection at end-of-task)
4. **End-of-day summary** (Cascade fills at user request or natural end-of-day)

---

## Section 0, Orch hand-off summary (top of file)

Lives at the very top of the daily log, above the YAML front-matter manifest. Written by the outgoing orch on rotation; absent until then. Target: ≤1000 tokens for a typical day; ≤1500 for a heavy day. The new orch reads this section alone in its first turn.

```markdown
# Orch hand-off summary, <YYYY-MM-DD HH:MM>

**Headline:** <one sentence: where we are at hand-off time>

**In-flight agents:**
- <name> (status: STATUS, phase: N): <one-clause where they are; what's blocking them if BLOCKED>
- <name> ...

**Decisions awaiting operator sign-off (top 3):**
1. <decision> (urgency: now | this-session | next-batch)
2. ...
3. ...

**Today's patterns (top 3 signals for meta):**
1. <pattern; cite specific agent entries> (count: N occurrences)
2. ...
3. ...

**Next-action recommendation for new orch:**
1. <immediate next step>
2. <follow-up>
3. <less urgent but should not slip>

**Carries to tomorrow:**
- <blocked agent + reason>
- <unresolved decision>
- <follow-up surfaced today but not yet dispatched>

**Pointers:**
- Full daily log: `localonly/daily/<YYYY-MM-DD>.md` (start at Wave <N> for current context)
- Current weekly meta log: `localonly/meta-logs/<YYYY-WW>-meta.md`

---
```

The new orch's first turn:

1. Read this Section 0 only. Not the full daily log yet.
2. Cross-check against the manifest STATUS column. If any worker is `IN_PROGRESS` per the manifest but not in the in-flight list above, halt and ask the operator.
3. Read the most-recent weekly meta log's "Process-improvement candidates" section.
4. Acknowledge: "Hand-off ingested. Next action per outgoing orch: <action>. Proceed or revise?"

---

## Section 1, YAML front-matter manifest

```yaml
---
project: <project-name>             # e.g., buds, mailchimp-r-and-a-qa-suite, lodestar
date: <YYYY-MM-DD>                  # ISO date; matches the filename
operator: <name>                    # who is at the keyboard today
batch_id: <YYYY-MM-DD>-<slug>       # one-line label for the day's theme

agents:
  - name: <single-letter or short slug>      # A, B, F, fdroid-research, license-edit
    role: <code | research | sweep | prose-audit>
    phase: <integer; 0 for async pre-baseline; 1 for first wave; 2+ for dependents>
    owned_paths:                             # files or dirs this agent may write
      - <path1>
      - <path2>
    consumes:                                # producer-agent deliverables this agent reads at start
      - <producer-deliverable-path>
    produces:                                # artifacts this agent writes that may be consumed downstream
      - <deliverable-path>
    depends_on:                              # explicit named-agent dependencies (sibling-aware; optional if covered by consumes)
      - <agent-name>
    precondition:                            # required only when owned_paths intersects high-stakes-list.yaml
      research-complete                      # ONE of: research-complete | spec-locked | schema-frozen | (project-defined)
    worktree: <.worktrees/<task-slug> | none-with-justification>
    wall_clock_min: <integer minutes>
    status: <PLANNED | CLAIMED | IN_PROGRESS | DONE | FAILED | BLOCKED>
    # Status transitions: PLANNED at Cascade's draft; CLAIMED when agent picks up; IN_PROGRESS optional midpoint;
    # DONE on clean completion; FAILED on caught failure with chat-surface; BLOCKED when precondition unmet.

# Optional: dispatch-level overrides
review_budget_min: <integer; default 10 * N agents>     # operator's expected review wall-clock
load_band_target: <light | steady | heavy | overloaded>  # operator's planned band; Cascade compares actual against this at end-of-day
---
```

### Front-matter constraints (validator enforces)

- Each agent's `name` is unique within the manifest.
- `phase` is a non-negative integer.
- `consumes` paths must each have a matching `produces` entry in an earlier-phase sibling agent.
- `owned_paths` may not overlap with any sibling agent in the same `phase`.
- If any `owned_paths` entry intersects the project's `localonly/daily/high-stakes-list.yaml`, the agent's `precondition` field is mandatory and must be satisfied by a sibling-or-earlier-phase producer.
- `produces` paths must not already exist with current-baseline metadata at dispatch time (H14 artifact-existence check).
- The DAG implied by `phase` + `consumes` must be acyclic.

---

## Section 2, Wave narrative

One markdown subsection per wave, in `phase` order. Each wave's narrative explains the dispatch shape, the dependency edges, and any surprises Cascade or the operator should watch for. Cascade drafts this alongside the manifest.

```markdown
## Wave 0 (async, runs first)

<one paragraph: what's in this wave, why it runs first, what unblocks if it succeeds>

## Wave 1

<paragraph per agent in this wave: scope, why it's here, what it produces for Wave 2>

## Wave 2 (after Wave 1 lands)

<...>
```

Cascade's self-adversarial review findings (per the SKILL.md auto-invoke section) get appended to the relevant wave narrative under "Adversarial review findings". Surface high-severity findings under "Decisions awaiting user sign-off" at the top of the wave section.

---

## Section 3, Per-agent entries (orch-authored, compacted from worker session logs)

Workers write their own session logs at `<project>/localonly/session-logs/<YYYY-MM-DD>-agent<X>-<task>.md` using the 4-section compaction-ready format defined in `templates/worker-session-log.md`. The orch ingests each worker's session log on DONE status and compacts it into this Section 3 entry.

Shape per worker entry:

```markdown
## Agent <name>, <role>, <task-slug>

**Status:** <shipped | blocked | in-flight | failed>. <one-line context: HEAD SHA, commits, or blocking reason>

**Key learnings (from worker session log § 2):**
- **<bold title>:** <learning>
- **<bold title>:** ...

**Audit findings, P0/P1 only (from worker session log § 3; P2 routed to "For meta"):**
- **[P1, orch]** <actionable finding>

**Worker session log:** `localonly/session-logs/<YYYY-MM-DD>-agent<X>-<task>.md` (full audit trail; orch may have compacted away Details on ingestion)
```

The orch updates the manifest STATUS field to DONE at the moment it finishes writing this entry. The worker's raw session log stays at `localonly/session-logs/` as the historical record.

---

## Section 4, End-of-day summary

Cascade fills this at user request or natural end-of-day. Set B work-in-a-day metrics per `SKILL.md` "Work-in-a-day metrics":

```markdown
## End-of-day summary

**Headline:** <one-line "today was X" summary>

**Agent counts:**
- Dispatched: <N>
- Completed (DONE): <N>
- Failed: <N>
- Blocked carrying to tomorrow: <N>

**Commit counts:**
- Across all worktrees merged today: <N>
- Merged-to-main commits: <N>
- Commits still in worktrees pending review: <N>

**Decision counts:**
- Surfaced for operator sign-off: <N>
- Signed off today: <N>
- Carrying to tomorrow: <N>

**Wall-clock:**
- Agent wall-clock total: <N> hr
- Operator review wall-clock total: <N> hr (~10 min per agent default)

**Load band verdict:** <light | steady | heavy | overloaded>
<one-sentence reasoning>
<coaching nudge if heavy or overloaded>

**Carries to tomorrow:**
- <agent name, BLOCKED, reason> (if any)
- <decision awaiting sign-off> (if any)
- <follow-up work surfaced today but not yet dispatched>

**Pattern observations (optional):**
- <if 3+ similar surprises today, name the pattern as a candidate falsifier-checklist addition or skill-edit signal>
```

---

## Annotated worked example, two-agent buds licensing batch

```markdown
---
project: buds
date: 2026-05-19
operator: wei
batch_id: 2026-05-19-licensing-research-and-edit

agents:
  - name: A-fdroid-research
    role: research
    phase: 1
    owned_paths:
      - docs/strategy/fdroid-fsl-acceptance.md
    consumes: []
    produces:
      - docs/strategy/fdroid-fsl-acceptance.md
    worktree: .worktrees/fdroid-research
    wall_clock_min: 90
    status: PLANNED

  - name: B-license-edit
    role: code
    phase: 2
    owned_paths:
      - LICENSE
      - README.md
    consumes:
      - docs/strategy/fdroid-fsl-acceptance.md
    produces: []
    depends_on:
      - A-fdroid-research
    precondition: research-complete
    worktree: .worktrees/license-edit
    wall_clock_min: 60
    status: PLANNED

review_budget_min: 30
load_band_target: steady
---

## Wave 1

Agent A-fdroid-research: research F-Droid inclusion policy for FSL-1.1-MIT plus the Iron Law Addendum. Produces the research doc with confidence band, fallback options, and IP-protection priorities. Surfaces decisions awaiting Wei sign-off at the top of the doc.

**Adversarial review findings:** None. Read-only against research surface; produces a doc Wei will sign off on before Wave 2 spawns.

## Wave 2 (after Wei accepts A's findings)

Agent B-license-edit: edit LICENSE and README anchoring constraint #18 per Wei's decisions on A's research. Reads A's session-log entry and the four signed-off decisions before any edit. Halts to BLOCKED status if A's status is not DONE or if Wei has not signed off on the band, fallback option, inquiry decision, and IP-protection priorities.

**Adversarial review findings:** LICENSE is on buds' high-stakes-list.yaml; B's precondition `research-complete` is satisfied by A's produces. H14 artifact-existence check: README.md exists (expected); LICENSE exists (expected). B is editing in place, not creating new files. Owned-path overlap: none within Wave 2 (single agent). Cwd-race risk: none (separate worktree).
```

End of annotated example. Remove the schema-explanation prose before the daily log is surfaced for the first time on a given day.

---

## Section 5, For meta (orch-appended throughout the day)

The orch appends to this section throughout the day as cross-worker signals surface. Meta ingests these on weekly invocation. Once a `PROMOTE?` candidate gets ratified into a skill, the corresponding bullet here can be deleted as deduplicated.

```markdown
## For meta

**Cross-worker patterns observed today:**
- <collision, prompt-template drift, repeated halt trigger; cite the worker entries that fired>

**Process gaps:**
- <where the iron laws didn't catch something they should have; cite the incident>

**Skill-change candidates:**
- **PROMOTE?** <candidate; if this pattern fires 2+ times this week, meta should propose a skill edit> (evidence: `localonly/session-logs/...`)
```

Meta's weekly ingestion routine reads every daily log's Section 5 within the week's scope (5-7 daily logs). PROMOTE? candidates that fired 2+ times within the week become Process-Improvement Candidates in `localonly/meta-logs/<YYYY-WW>-meta.md`. Once a candidate is ratified by Wei into a skill, the orch deletes the PROMOTE? bullet from this section (the skill itself encodes the rule now).
