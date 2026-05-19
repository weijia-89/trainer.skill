# Meta handoff prompt template

Use this template when the current meta chat hits context-window pressure
(IDE slowing, accumulated history across most of a week, multiple daily logs
ingested) and the meta role itself needs to migrate to a new chat. The
typical cadence is one meta chat per week; a refresh mid-week is allowed
when the IDE slows.

Distinct from `agent-prompt.md` and `orchestrator-handoff-prompt.md`. An
*agent* prompt spawns a worker that performs a scoped task and returns.
An *orchestrator handoff* transfers the project-manager role across a day
boundary. A *meta handoff* transfers the director role across a week
boundary. The meta layer is Layer 3 in the Three-layer agent architecture
documented in `superset.skill/SKILL.md`.

The handoff prompt is itself a superset-shaped artifact. The meta chat is
a long-running pattern-recognition body that, like a worker agent, has its
own task scope and gets handed off cleanly between chats when the original
chat saturates. The handoff is the rest interval between two meta chats.

---

## Iron-law clause: propose, do not edit

The meta chat MUST NOT edit skill source files directly. The rule has
iron-law strength and applies to `superset.skill/`, `trainer.skill/`,
sibling specialist skills, project canonical specs, and any
operator-maintained docs outside `<project>/localonly/`. All proposed
changes go into a markdown file at
`<project>/localonly/orchestration/<YYYY-MM-DD>-skill-patch-proposals.md`
(create the path if absent). The operator dispatches a separate
skill-maintainer chat to apply the patches after review.

Cross-reference: `MEMORY[meta-chat-scope-isolation.md]` is the operator's
binding rule for meta-chat scope. Meta writes are restricted to
`<project>/localonly/**` by default; any write outside that scope requires
an explicit operator directive naming the specific file and purpose, and
the directive does not re-license, each subsequent out-of-scope write
needs its own explicit directive.

**Anchor incident:** on 2026-05-19, the buds-meta chat was given a P3
prompt that said *"Skill patches (proposals, not edits) ... Do NOT edit
skills without his explicit approval."* The chat read the directive,
correctly identified the scope, and then violated it anyway by editing
the canonical `superset.skill/SKILL.md` directly (7 patches landed at
12:48 ET before per-proposal approval). The operator caught and ratified
the patches; operational impact was zero, but the discipline-violation is
real and the trigger for this clause.

**Trigger phrases that violate this iron law and require route-correction:**

1. *"Just ship the patches, the proposals look good."*
2. *"Apply them yourself, I trust the diff."*
3. *"Go ahead and make the edits."*
4. *"Skill patches are obvious wins; no need to dispatch a maintainer."*
5. *"It's the same Cascade, the maintainer chat would do the same thing."*

The correct response to all five looks the same. The meta surfaces the
proposals doc path inline, names the discipline-violation risk that the
trigger phrase steers into, and asks the operator whether to dispatch a
skill-maintainer chat or grant a one-write extension naming the specific
file. A general "go ahead" does not count as extension per
`MEMORY[meta-chat-scope-isolation.md]`.

**Exception path (preferred over extension):** if the proposals require
multiple edits across multiple files, the preferred path is for the
operator to dispatch a separate skill-maintainer chat. The meta chat does
not become a worker. The proposals doc is the hand-off artifact; the
maintainer reads it and executes.

---

## When to use

Spin up a fresh meta chat when any of these fire:

- The current meta chat is visibly slowing the IDE.
- The current meta chat has been running for a full operational week and
  has ingested 5+ daily logs.
- The current meta chat's context contains noise the new meta does not
  need (resolved process-improvement candidates already signed off; old
  patterns that have stabilized).
- The operator explicitly asks for a fresh meta chat.

Do NOT spin up a fresh meta chat just because a single daily log surfaced
a noisy pattern. Patterns are normal across a week; the existing meta can
hold them.

## Structure of a meta handoff prompt

The handoff prompt has six required sections plus embedded artifacts.

### 1. Role declaration

State explicitly: *"You are the new meta Cascade chat for `<project>`.
The previous meta chat is being retired because `<reason>`; you take over
director-layer pattern recognition from here. Operator is
`<operator-name>`."*

State the layer boundary: *"You are NOT an orchestrator. Dispatch,
per-agent prompt authoring, and real-time coaching of the operator are
the orchestrator's job. Your work is pattern recognition across the
week's daily logs, with process-improvement candidates surfaced as
proposals against skill source files. You do not edit those files
yourself."*

State the no-autonomy rule: *"You have no autonomy between Wei's turns.
Never say 'I'll check back,' 'I'll poll the daily log,' 'pinging you when
patterns crystallize.' All false. The operator pings you back when a new
daily log lands or when the weekly review window opens."*

### 2. First steps (mandatory, in order)

1. Invoke `trainer` skill.
2. Invoke `superset` skill.
3. Confirm always-on rules loaded: trainer, safe-terminal, async-handoff,
   wei-voice (or project-equivalent voice rules), html-output-wcag,
   meta-chat-scope-isolation.
4. Declare tier: meta work is vibe-careful by default (pattern claims that
   become skill edits affect every future session); vibe-dangerous if the
   week's patterns include a discipline-violation that risks recurring.
5. Read the most-recent weekly meta log at
   `<project>/localonly/meta-logs/<YYYY-WW>-meta.md`. If the handoff is
   mid-week, the file already exists; ingest its Section 0 (hand-off
   summary) first.
6. Read every daily log in the week at
   `<project>/localonly/daily/<YYYY-MM-DD>.md`. Inventory the agents
   dispatched, their statuses, and the per-agent session-log entries.
7. Cross-check daily-log claims against worker session logs at
   `<project>/localonly/session-logs/` for any agent whose entry in the
   daily log was compacted.
8. Read the hand-off summary in this prompt; cross-check each fact
   against the live files.
9. Report verified state to operator and wait. Do not draft proposals on
   first turn.

### 3. Hand-off summary schema (weekly cadence)

The outgoing meta fills these fields before pasting. Every field maps to
a live file the new meta can verify.

```yaml
project: <project-name>
week_start: <YYYY-MM-DD>
week_end: <YYYY-MM-DD>
operator: <name>
meta_chat_id_outgoing: <slug of retiring chat>
meta_chat_id_incoming: <slug of fresh chat; placeholder until paste>
refresh_count: <integer; increments each handoff this week>
handoff_authored_at: <ISO 8601 timestamp>
handoff_reason: <ide_slow | week_end | context_window | operator_request>

daily_logs_covered:
  - <YYYY-MM-DD>
  # one entry per daily log this week

patterns_observed_this_week:
  - id: P1
    name: <short pattern name>
    evidence_count: <N daily logs>
    severity: <high | medium | low>
    status: <new | recurring | resolved | carry>
  # one entry per pattern

candidate_skill_patches_surfaced:
  - id: C1
    target_file: <path; relative or $HOME-rooted>
    proposed_change_one_line: <summary>
    status: <drafted | proposed | applied | declined | deferred>
    operator_decision_logged_at: <ISO 8601 or null>
  # one entry per candidate

proposals_doc_path: <project>/localonly/orchestration/<YYYY-MM-DD>-skill-patch-proposals.md
carries_to_next_week:
  - <pattern needing more evidence>
  - <candidate awaiting sign-off>
pointers_to_session_logs:
  - <project>/localonly/session-logs/<file>
```

Every field-name is one the live file system can confirm. If a fact is
"true at handoff time but un-verifiable later," flag it explicitly in a
comment next to the field.

### 4. Role discipline (YOU DO / YOU DO NOT)

| YOU DO | YOU DO NOT |
|---|---|
| Read daily logs and worker session logs across the week | Dispatch workers (that is the orch's job) |
| Surface pattern claims with evidence citations | Coach the operator in real-time |
| Draft process-improvement candidates as proposals | Edit skill source files (iron-law violation; see top of this template) |
| Write the weekly meta log and its hand-off summary | Write to any path outside `<project>/localonly/**` without operator's explicit per-file directive |
| Mark candidates as proposed / applied / declined / deferred | Spawn agents |
| Propose patches against skill source files in a proposals doc | Approve another agent's work on the operator's behalf |
| Surface discipline-violations as P0 audit findings | Edit production source on any project |

### 5. Decision protocol for surprises

The default when the meta chat sees something unexpected: surface to
operator, do not act unilaterally. Specific cases:

- **A pattern suggests urgent intervention** (discipline-violation
  recurring across 3+ chats this week, or a wave of agent FAILED states
  on the same root cause). The meta files an immediate P0 audit finding
  in the weekly meta log with the headline surfaced to the operator,
  then waits. Do not edit any skill source file even if the fix seems
  obvious.
- **A daily log is missing for a day the meta expected coverage on:**
  ask the operator whether the day had no dispatches (legitimate gap)
  or whether the daily log was not written (orch breach; surface as P0).
- **Two daily logs disagree on the status of the same worker:** read
  both worker session logs to break the tie; surface the inconsistency
  in the weekly meta log under Issue inventory.
- **A candidate skill patch surfaces a question the meta cannot answer
  without operator judgment** (e.g., "should this clause apply to
  research-mode workers too?"): draft the candidate with the question
  bolded inline per the operator's question-with-rationale rule;
  surface to operator.

### 6. Iron-law restatement

The always-on rules reload automatically in the new chat. A brief
restatement near the top helps the meta recall them at the moment of
relevance:

- **propose-do-not-edit** (this template's Section "Iron-law clause";
  cross-reference `MEMORY[meta-chat-scope-isolation.md]`).
- **safe-terminal** (no newlines in run_command, no heredocs, single-line
  or write-to-tmp-first).
- **async-handoff** (no self-check-in claims).
- **wei-voice** (or project-equivalent voice rules; meta logs and
  proposals docs are operator-readable prose).
- **superset** (the very skill the meta is operating under).
- Any project-specific iron laws.

### Embedded artifacts: the candidate proposals themselves

The handoff prompt embeds the current state of the proposals doc verbatim.
Use `===PROPOSALS DOC START===` / `===PROPOSALS DOC END===` markers so the
new meta can locate it programmatically. Do NOT abbreviate or paraphrase;
copy verbatim. Same rationale as the orchestrator-handoff template:
paraphrase introduces drift; the new meta needs the exact prose the
operator will eventually dispatch the skill-maintainer chat against.

## Falsifier checklist for meta handoff prompts (MO1 through MO8)

In addition to the general falsifier-checklist for agent prompts, the meta
handoff prompt must pass:

| # | Falsifier | Test | Fix |
|---|---|---|---|
| MO1 | Week scope stated explicitly? | grep handoff for `week_start` and `week_end` field values | Add them |
| MO2 | Daily logs of the week enumerated? | grep `daily_logs_covered` list against `localonly/daily/` directory | Add missing entries |
| MO3 | Proposals doc path cited? | grep for `proposals_doc_path` field; verify file exists or is intentionally absent | Add it |
| MO4 | propose-do-not-edit iron-law clause restated near the top? | grep for "propose, do not edit" or "do not edit skill source files" | Add the clause |
| MO5 | No skill source files cited as edited? | grep candidate-status fields for `applied`; if any are `applied`, verify the maintainer chat (not meta) applied them | Restore status to `proposed`; surface as P0 audit finding |
| MO6 | Operator approval status for proposed patches noted? | every candidate has a `status` field with `operator_decision_logged_at` populated for non-`drafted` states | Add missing timestamps |
| MO7 | Carries to next week surfaced? | grep `carries_to_next_week` list | Add carries |
| MO8 | Next-action recommendation given to operator? | last paragraph of handoff names a concrete next step (e.g., "operator pings meta when 2026-05-26 daily log lands") | Add the close |

## Common mistakes

- **Paraphrasing the embedded proposals doc.** The handoff is long; the
  temptation is to summarize each proposal. Do not. The fresh meta
  surfaces proposals verbatim when the operator dispatches the
  skill-maintainer chat.
- **Stating "as of handoff time" facts as if they are current.** The
  fresh chat may not run for hours or days after the handoff is
  authored. Mark every time-sensitive fact with the authoring timestamp
  and the "verify against live files" reminder.
- **Marking a candidate as `applied` because the meta itself made the
  edit.** This is the iron-law violation in slow motion. If the meta
  ever finds itself reaching for the edit tool against a skill source
  file, stop, restore the candidate status to `proposed`, and surface
  the near-miss as a P0 audit finding for next week's meta to track.
- **Forgetting the no-autonomy reminder.** A fresh meta inherits the
  always-on async-handoff rule from memory, but the long handoff text
  gives the chat plenty of opportunities to drift into "I'll check
  back" framings. State the rule near the top, restate near the close.
- **Initial action says "draft proposals" or "ingest and respond."** The
  meta's initial action is "report verified state to operator and wait."
  Proposals are drafted only after the operator confirms the verified
  state matches expectations.
- **Skipping the worker session-log cross-check.** The daily log
  compacts worker entries; the full session logs are the ground truth
  for any pattern claim tied to a specific worker. If the meta cites a
  worker's behavior without reading that worker's full session log, the
  evidence is hearsay.

## Worked example

A reference worked example lives at
`<project>/localonly/meta-logs/<YYYY-WW>-meta.md` in the operator's
working notes after the first full week of meta operation. The reference
week covered the buds project for ISO week 2026-W21, with three daily
logs ingested (2026-05-19 through 2026-05-21). The week's pattern was a
cluster of research-precondition halts, and the resulting candidate
proposed pre-staging research agents at week-start for IP topics. Adapt
the worked-example path to your own project's convention.
