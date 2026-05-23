---
name: superset
description: Use when spawning 2+ fresh-context agents on the same git repo for isolated parallel work; symptoms include same-tree shared-state risk (.pytest_cache / pyproject collisions), agents overstepping scope, intermediate commits pushed by accident, session learnings lost between iterations, prompt quality drifting between agents.
type: project-skill
version: 0.8.3
authors: Wei Jia (2026-05-19)
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

Parallel agents on the same git repo collide on shared state (caches, pyproject, lock files) and lose their session learnings unless the prompt is built for isolation. This skill is a prompt-template generator plus a falsifier checklist for catching prompt-quality drift before spawning.

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

## Daily-log-driven dispatch (added v0.4.0, 2026-05-19)

The coordination primitive for multi-agent days is a single per-project daily log at `<project>/localonly/daily/<YYYY-MM-DD>.md`, replacing the older pattern of per-batch dispatch manifests plus per-agent session logs as separate artifacts. One file holds the manifest, in-flight status broadcast, each agent's session-log content, end-of-day summary, and work-in-a-day metrics. The orchestrator (Cascade) and every dispatched agent read and append to it; producer-consumer dependencies surface in the manifest header, so the consumer reads the producer's session-log entry before starting (content-precondition checking). Wei reviews one document per project per day instead of N prompts plus N session logs.

### The artifact, end to end

The daily log has four sections, in order:

1. **Manifest (YAML front-matter).** Each agent declared with `name | role | owned_paths | depends_on | produces | consumes | phase | wall_clock | status | precondition`. Status values: `PLANNED | CLAIMED | IN_PROGRESS | DONE | FAILED | BLOCKED`. Cascade auto-drafts this at dispatch-intent triggers per the trainer iron law "Dispatch graph before dispatch".
2. **Wave narrative.** Markdown sections per wave (Wave 0 async, Wave 1, Wave 2, etc.) describing the dispatch shape, dependency edges, and surprises. Cascade writes this alongside the manifest draft.
3. **Per-agent entries.** Each dispatched agent appends its own session-log content to its named subsection of the daily log when it finishes. This is the per-agent session log; there is no separate `localonly/session-logs/<date>-agent<N>-<slug>.md` artifact anymore. The agent writes status transitions (CLAIMED at start, IN_PROGRESS at midpoint optional, DONE or FAILED at end) by editing the manifest's `status` field on its own row.
4. **End-of-day summary.** Cascade fills this at user's request or at natural end-of-day. Work-in-a-day metrics (see below) plus carries-to-tomorrow plus blocked items.

The template at `templates/daily-log.md` ships the full schema with an annotated example. The per-section spec lives there, not here, to keep SKILL.md focused on the discipline.

### Auto-invoke and self-adversarial review

Cascade automatically drafts the daily-log manifest on any user phrase implying multi-agent dispatch. The user does not say "draft a manifest"; the trigger is the dispatch intent itself ("spawn N agents", "let's run these in parallel", "kick off a wave", "run these tasks today", etc.). Before surfacing the draft, Cascade self-adversarially reviews using:

- This skill's falsifier checklist (especially H11 through H15 for dispatch hazards).
- A `form-check adversarial-review` pass scoped to the manifest, scanning for owned-path overlaps, missing producer-consumer links, freeze-list violations, duplicate dispatches against existing artifacts, and Cwd-race risks in same-tree dispatches.
- The project's freeze list at `localonly/daily/high-stakes-list.yaml` (Option 4b gate; see Freeze list below).

Adversarial review findings surface alongside the proposed manifest under "Decisions awaiting user sign-off" before per-agent prompts are generated. The user approves or revises one document; Cascade then generates the prompts from the manifest using the template renderer.

### Producer-consumer artifact contract

Each agent declares `produces: [paths]` and `consumes: [paths]`. The orchestrator validates that consumer agents sit in a later phase than their producers. The validator refuses to render the prompt if a `consumes` entry has no matching `produces` in any earlier-phase agent. This catches the buds 2026-05-19 f-droid case: the LICENSE-editing agent declares `consumes: docs/strategy/fdroid-fsl-acceptance.md`, the research agent declares `produces: docs/strategy/fdroid-fsl-acceptance.md`, the validator places the LICENSE agent in Phase 2. At agent start, the consumer's first-steps block reads the producer's daily-log entry (session-log subsection plus `produces` paths' content) before doing its own work; if the producer's status is not `DONE` or any `produces` artifact is absent, the consumer halts and sets its own status to `BLOCKED`.

### Status broadcast (single-file flavor)

Each agent updates its `status` field in the manifest header at three moments: `CLAIMED` immediately after picking up its task (first commit Cascade makes on the agent's behalf), `IN_PROGRESS` at any natural midpoint (optional), `DONE` or `FAILED` at end. Sibling agents and the orchestrator read the manifest header on demand. No separate `.status.json` file is needed; the daily log is the single source of truth.

### Freeze list (high-stakes file gate)

Each project ships `<project>/localonly/daily/high-stakes-list.yaml` (or symlinks an org-wide default). The validator refuses to render a prompt for any agent whose `owned_paths` intersect the freeze list unless that agent's manifest entry declares `precondition: research-complete` and a sibling-or-earlier-phase agent has `produces:` covering the research artifact. The template at `templates/high-stakes-list.yaml` ships an annotated schema with buds and mailchimp starter entries.

### Work-in-a-day metrics

End-of-day-summary section reports (Set B per the 2026-05-19 research doc decision; Set A is a strict subset; Set C is a Phase 3 escalation):

- **Agent count.** Dispatched, completed, failed, blocked carrying to tomorrow.
- **Commit count.** Across all worktrees merged today.
- **Decision count.** Decisions surfaced under "awaiting user sign-off" plus how many user signed off.
- **Agent wall-clock hours.** Sum of completed-agent wall-clock estimates.
- **Operator review wall-clock hours.** Sum of estimated review time the user spent on the day's batches (~10 min per agent per `superset` batch-aggregation defaults).
- **Load band verdict.** `light | steady | heavy | overloaded`. Computed against Wei's coached calibration (initial thresholds: light ≤ 2 hr operator review, steady 2-4 hr, heavy 4-6 hr, overloaded > 6 hr; subject to revision per `.recovery/calibration.jsonl` after N ≥ 10 days of data). On `heavy` or `overloaded`, Cascade surfaces a coaching nudge: "you're at heavy load; want to defer the next batch to tomorrow?".

The verdict is descriptive plus advisory; not a hard cap. Wei holds the override.

### What replaces what

| Before v0.4.0 | After v0.4.0 |
|---|---|
| `localonly/session-logs/<date>-agent<N>-<slug>.md` (one file per agent) | Single per-agent subsection inside `localonly/daily/<YYYY-MM-DD>.md` |
| Per-batch dispatch manifest at `localonly/dispatch/<date>-batch-<slug>.md` (proposed in research doc, never shipped) | Same manifest content as the daily log's front-matter |
| User reads N prompts to spot collisions | User reads one manifest with adversarial-review findings already surfaced |
| User dispatches by request ("draft me a manifest") | Cascade auto-drafts on dispatch intent; user reviews and approves |
| File collisions caught by Owned-paths table (Medium severity, M11) | Caught by validator at dispatch time (High severity, H12) |
| Producer-consumer dependencies not caught at all (the buds 2026-05-19 case) | Caught by `consumes` declaration plus topological wave-ordering |
| Duplicate dispatch caught by agent at start (the mailchimp 2026-05-18 case) | Caught by validator before dispatch (H14, artifact-existence) |

### Migration notes

Existing projects with `localonly/session-logs/` keep their historical logs as-is; the directory becomes archival after v0.4.0 adoption. New session logs land inside the daily log. The transition is per-project, not flag-day; a project adopts v0.4.0 the next time it runs a multi-agent batch.

## Three-layer agent architecture (orch + meta + worker)

The dispatch system operates across three named agent layers, each with a distinct lifespan and responsibility. The trainer iron law "Dispatch graph before dispatch" routes here for operational detail.

### Layer 1, worker

Per-task, fresh-context agents covered by the five-pillar prompt discipline (worktree + baseline + scope + no-push + session log to daily log). Spawned by orch; killed at task completion. Worker session logs live as named subsections inside the daily log.

### Layer 2, orch (project manager, 1-day default)

The chat the operator talks to. Lives for one operational day by default. Refresh sooner if the IDE slows under accumulated history or context window gets tight.

**Orch responsibilities:**

- **Dispatch.** Read user dispatch intent; auto-draft the daily-log manifest; self-adversarially review; surface decisions awaiting operator sign-off; generate worker prompts from the manifest after sign-off.
- **Status broadcast.** Track in-flight worker status; surface blockers; coordinate review-order on merge-back.
- **Coaching.** Per the trainer's coaching stance: push back when worker decisions trip iron-law concerns; defer when operator demonstrates understanding; log overrides.
- **Narration.** Tell the operator where the day is, what landed, what's stuck, what's next. This is the value the orch provides over the operator coordinating workers themselves.
- **Hand-off authorship.** On rotation, write the token-optimized hand-off summary at the top of the daily log so the next orch can ingest it.
- **Status check + docs.** On status refresh, update coordination SSOT and each affected repo's `CHANGELOG.md` + `README.md` per the iron law below; chat points to SSOT only (no rehash). Template: `templates/status-check-changelog.md`.

**Orch rotation triggers** (operator phrases that fire the hand-off iron law):

- "wrap up the day" / "let's call it a day" / "I'm starting fresh tomorrow"
- "this chat is getting slow" / "the IDE is laggy" / "this context is heavy"
- "hand off the orch" / "rotate the orchestrator" / "spawn a new orch"
- "spin up tomorrow's orch" / "give me a fresh orch chat"

On any of these, Cascade auto-drafts the hand-off summary (see schema below) and writes it to the top of the daily log without being asked. The user gets one document to scan; approving the summary signals to spin up the new orch chat.

### Layer 3, meta (director, 1-week default)

The pattern-recognition and skill-improvement layer. Lives for one operational week by default. Refresh sooner if context bloats the IDE.

**Meta responsibilities:**

- **Read daily logs.** Cover the 5-7 daily logs for the current week across the project Meta is scoped to.
- **Pattern recognition.** Surface 3-N patterns per week. Examples: "Worker X has been blocked on schema-frozen precondition three times this week; the precondition vocabulary needs work" or "Phase-2 dispatches consistently overestimate wall-clock by 2x; the calibration needs revision" or "Owned-paths overlaps caught by adversarial review fired six times this week; H12 is doing real work".
- **Issue inventory.** Collisions, misses, prompt-quality drift across the week's dispatches.
- **Process-improvement candidates.** Concrete suggestions for skill edits. Names specific files and proposed diffs where possible.
- **Weekly summary write.** Output lands at `<project>/localonly/meta-logs/<YYYY-WW>-meta.md` (ISO 8601 year-week format; e.g., `2026-W21-meta.md`) using `templates/meta-log.md` as the schema.
- **PROMOTE? ingestion.** Reads each daily log's Section 5 "For meta" appendix. Any pattern flagged `PROMOTE?` that fired 2+ times within the week becomes a Process-Improvement Candidate (Section 4 of the meta log) with the specific skill-edit proposal. On Wei ratification, the orch deletes the PROMOTE? bullet from the daily log (the skill itself encodes the rule now).

**Meta does NOT:**

- Dispatch workers. Orch's job.
- Coach the operator in real-time. Trainer's job.
- Make decisions on its own. Suggests; operator decides.

**Meta invocation triggers** (operator phrases that summon meta):

- "what patterns are we seeing" / "what's the meta view" / "meta review"
- "is this approach working" / "is the process holding up"
- "should we update the skill" / "what should the skill learn from this week"
- "let's reflect on the week" / "weekly retrospective"

On any of these, Cascade either spawns a new meta chat (with the meta-prompt template, pointing it at the week's daily logs) or hands off the current meta-thread's running notes.

**Meta refresh.** Same triggers as orch hand-off but applied to the meta chat: when the meta context bloats or the IDE slows, the outgoing meta writes a hand-off summary at the top of the current weekly meta log; the new meta ingests it as its first turn.

## Orchestrator-role discipline: in-chat fix vs. spawn an agent

The orchestrator's read-only-on-source default is sometimes asked to bend. When the operator asks for a small CI fix, a comment typo, or a one-line config change, the orchestrator decides between two paths:

1. **In-chat fix** (orchestrator makes the edit directly).
2. **One-shot agent prompt** (spawn a tiny agent for the fix).

### Decision criteria (apply in order)

1. **Is the fix mechanical and prescribed?** If the analyzer or test framework names the exact change to make (e.g., "remove unused import on line 42"), and the change is single-file, the in-chat fix is acceptable. If judgment is required ("what should this error message say?"), spawn an agent.
2. **Does spawning an agent cost more wall-clock than the fix itself?** A 2-line mechanical fix takes 60 seconds in-chat; a one-shot agent prompt takes 5-10 minutes of orchestrator authoring + agent spawn + agent return. If the spawn-cost exceeds the fix-cost by >5x, in-chat is the right call.
3. **What is the operator's stated preference?** If the operator explicitly says "just fix it inline", the in-chat path is approved. If the operator says "spawn for this", spawn.

### Exception logging

When the orchestrator makes an in-chat fix, the exception is logged in the session at the time (not retroactively). The log entry includes: what was edited, what files, the analyzer command that prescribed the fix (if applicable), and the operator's explicit approval. Codified as precedent for the next orchestrator session.

**Exception log entry template** (paste into the session log at the moment of the in-chat fix):

```
- **Date/time:** YYYY-MM-DD HH:MM ZZZ
- **What was edited:** [brief description, e.g. "CI-unblock lint fixes"]
- **Which files:** [exact paths, one per line]
- **Analyzer command (if applicable):** [the prescribed-fix source, e.g. `flutter analyze`]
- **Operator approval:** [exact quote from operator's message]
- **Spawn-cost alternative considered:** [why in-chat won over spawn, citing the 3 criteria above]
- **Commit SHA(s):** [if the fix was committed]
```

The scaffold fields force the orchestrator to articulate each decision criterion at the moment of acting, making the precedent legible and disambiguating "the operator said go ahead" (insufficient; exact phrasing matters) from "the operator authorized this specific scope" (sufficient).

Worked example: buds 2026-05-19 commits `20f703b` + `091a268` on `rpd2/flutter-copy-sweep` were CI-unblock lint fixes (drop deprecated `avoid_returning_null_for_future`, clear 16 info-level analyzer issues). Scope was mechanical, CI was blocking, operator approved. Logged in the orchestrator handoff at `localonly/orchestration/handoffs/2026-05-19-orchestrator-handoff.md` Section 6 as a precedent exception.

## Status-claim evidence iron law (added 2026-05-19, post-buds-orch-handoff incident)

Any orch assertion about an in-flight or completed track — in a handoff
summary, daily-log update, end-of-day close-out, or chat reply — MUST
be backed by ≥2 evidence sources, of which ≥1 is a primary source.

### Evidence taxonomy

**Primary sources** (the artifact itself, empirically inspectable now):
- Git commits on the track's named branch: `git log --oneline -n 5 <branch>` 
- Branch existence: `git rev-parse --verify <branch>` (exit 0 = exists)
- Files at declared `produces:` paths: `ls -la <path>` 
- Content head at `produces:` paths: `head -20 <path>` (for non-empty check)
- CI status on the branch (when applicable)

**Secondary sources** (inference about the artifact; never sufficient alone):
- The daily-log manifest's `status` field
- The handoff doc's narrative claim
- A previous orch's recollection or end-of-day summary
- Cascade's own memory of prior turns

### Validation rule

A status claim is valid only if:
- ≥2 evidence sources support it
- ≥1 of those is a primary source
- The two sources are independently verifiable (not both derived from the
  same upstream claim — e.g., a handoff narrative and Cascade's memory of
  reading that handoff are not two independent sources)

### Required check-in moments (token-cheap by design)

1. **Outgoing orch handoff, before writing summary.**
   Run `bash scripts/validate-track-status.sh <today's daily log>`.
   The summary cites evidence rows from the script, not narrative.

2. **Incoming orch first turn, before acting on any track.**
   Re-run the same script. Divergence from outgoing summary halts and
   routes to operator.

3. **Daily-log end-of-day close-out.**
   Validate every track marked DONE has produces-artifact evidence on
   disk. Tracks with status claims but no primary evidence get marked
   `STATUS UNVERIFIED` and surfaced.

4. **Any chat reply that makes a status claim.**
   "Track X is [in-flight | done | blocked]" requires the orch to have
   run the validator within the current turn or cite a timestamp ≤30 min
   old. No "I recall from the handoff" claims allowed.

### Validator script shape

`scripts/validate-track-status.sh` parses the daily-log manifest, extracts
each track's branch + produces path + manifest status, and emits ~5 lines
per track:

    Track: license-audit-wei-repos
      Branch HEAD: <no branch named license-audit-*>  [PRIMARY: no dispatch evidence]
      Produces: /tmp/license-audit-2026-05-19.md: ABSENT  [PRIMARY: no completion evidence]
      Manifest status: NOT DISPATCHED  [SECONDARY]
      Last activity: never  [PRIMARY: derived from above]
      VERDICT: undispatched

Output ~5N lines for N tracks. Typical day = 4-8 tracks = 20-40 lines.
Token cost ~100-200 tokens per validation cycle. Cheap.

### What this catches (worked example: 2026-05-19 license-audit miss)

Outgoing orch wrote "Track A status: UNCLEAR, verify with Wei." A
validator run would have emitted the three-line block above. Three
sources, two primary, all pointing at: track was never live in buds
context. The orch's correct conclusion: "Track A was undispatched and
out of scope for buds-orch. Surfacing for drop, not for check-in."

## Status check + changelog/README iron law (added 2026-05-23, SDK weekend orch)

Every orch **status check** updates contributor-facing docs in the same turn as the coordination SSOT. The operator should not have to ask twice for README/CHANGELOG hygiene at end of day.

**Trigger phrases** (fire the full checklist; do not answer from memory):

- "check status" / "status check" / "refresh queue" / "where are we"
- "update the queue" / "sync status"
- End-of-day: "wrap up" / "EOD" / "changelog pass" (runs this iron law plus daily-log close-out if applicable)

### Iron law (orch)

1. **Evidence first.** Per repo in the active set: `git fetch`, `git status -sb`, `git log origin/main -1`, `gh pr view` when a PR row exists. Same bar as [Status-claim evidence](#status-claim-evidence-iron-law-added-2026-05-19-post-buds-orch-handoff-incident); no narrative without primary sources.
2. **Coordination SSOT.** Write the full status picture to the project's queue or daily log (SDK weekend: `cursor-sdk-playground/weekend-queue.md` only for queue state; push playground). Include § **Changelog source** blocks with deai-quality prose: behavior, file scope, verification, ready-made changelog bullets, and explicit "do not claim" lines where scope is easy to overstate.
3. **Product docs per repo touched.** For every repo whose merge or review-ready commit changed since the last check, edit that repo's `CHANGELOG.md` and `README.md` in the same session. Use Keep a Changelog shape for `CHANGELOG.md`; keep README to a short "Recent work" stanza that matches the changelog entry. If nothing shipped since last check, skip product doc edits (do not bump version noise).
4. **Chat discipline.** Reply with one line: path to SSOT (+ playground git SHA if pushed). Never paste the status table or changelog source into the orch window.
5. **deai before commit.** Changelog and README prose pass the deai pre-output gate (voice prime, meaning preserved, no fabricated specifics). Queue § Changelog source is the draft; product files are the publish target.
6. **Workers stay narrow.** Workers append proposed changelog bullets to `localonly/daily/<YYYY-MM-DD>.md` on DONE unless the job prompt owns `CHANGELOG.md`. Orch merges worker bullets into product docs on status check.

### Accomplishment note shape (required in SSOT work history)

For each queue row or track that merged or reached review-ready, record:

| Layer | Content |
| ----- | ------- |
| Behavior | What works now that did not before (operator- or user-visible) |
| Scope | Primary paths/modules; what is explicitly out of scope |
| Verification | Commands that passed before merge or before review |

### SDK weekend binding

| Artifact | Path |
| -------- | ---- |
| Queue SSOT | `~/Projects/cursor-sdk-playground/weekend-queue.md` |
| Checklist template | `templates/status-check-changelog.md` (this repo) |
| Ops script | `cursor-sdk-playground/scripts/queue_status.sh` |

Orchestrator brief may restate paths; **this section is canonical** for status-check + changelog discipline.

### What this prevents

- EOD scramble to reconstruct what shipped from agent memory.
- Queue and product README diverging (queue says merged, README still silent).
- Long status dumps in chat that duplicate SSOT and burn context.

**Anchor:** 2026-05-23 SDK weekend — operator asked for changelog-ready queue notes and iron-law adoption in superset, not trainer-only.

**SDK affordances (same iron law):** `cursor-sdk-playground/palamedes-ui/` + `scripts/palamedes_serve.sh` for local palamedes research UI; queue SSOT `weekend-queue.md`. Iron-law excerpt: `prompts/status-check-changelog-iron-law.md`.

## Hand-off summary schema (token-optimized)

The orch hand-off summary lives at the very top of the daily log (above the YAML front-matter manifest, in a fenced section that survives the manifest's parser ignoring it). Target: ≤1000 tokens for a typical day; ≤1500 for a heavy day with many in-flight items. The new orch reads this section alone in its first turn and gets ~90% of the day's context without parsing the full log.

### Required fields (per the template at `templates/daily-log.md` Section 0)

1. **Headline.** One sentence: "where we are at hand-off time".
2. **In-flight agents.** Bulleted list of workers not in `DONE` status. Each line: name + status + one-clause "where they are".
3. **Decisions awaiting operator sign-off (top 3).** Each: one-line decision + urgency tier (`now | this-session | next-batch`).
4. **Today's patterns (top 3 signals for meta).** Each: one-line pattern + count of occurrences today.
5. **Next-action recommendation for new orch.** Numbered list, ≤3 items, ordered by immediacy.
6. **Carries to tomorrow.** Bulleted: blocked workers, unresolved decisions, follow-up work surfaced but not yet dispatched.
7. **Pointers.** `localonly/daily/<YYYY-MM-DD>.md` (current daily log) + section anchors for deep context; `localonly/meta-logs/<current-YYYY-WW>-meta.md` (most recent meta log).

### Authorship discipline

Outgoing orch writes the summary AFTER ingesting all worker session-log subsections in the day's daily log. The summary is a synthesis, not a dump. Cascade's self-adversarial review pass on the summary checks for:

- Missing in-flight workers (cross-reference manifest STATUS field against the summary's in-flight list)
- Missing decisions (cross-reference any "Decisions awaiting user sign-off" sections in the wave narrative)
- Pattern claims unsupported by the day's evidence (each pattern line must cite at least one specific worker entry or wave-narrative anchor)
- Token bloat (target ≤1000 tokens; if exceeded, rewrite tighter or split into "headline summary" + "appendix")

### What the new orch does in its first turn

1. Read the hand-off summary section of the daily log. ONLY this section. Not the full daily log yet.
2. Cross-check the summary against the manifest STATUS column. If any worker is `IN_PROGRESS` per the manifest but not mentioned in the summary's in-flight list, halt and ask the operator for clarification before proceeding.
3. Read the most-recent meta log's "Process-improvement candidates" section; flag anything that might affect today's dispatch.
4. Acknowledge to the operator: "I've ingested the hand-off summary. Next action per the outgoing orch's recommendation: <action>. Want me to proceed or revise?"

### What the new meta does on refresh

Same pattern, reading the weekly meta log's hand-off summary at the top of the file. New meta's first action is to acknowledge the week's running patterns and the carries-to-next-week list.

## Empirical falsifier harness (added v0.4.0, Mozilla-mythos style)

Every manifest-level falsifier ships with a deterministic test script that constructs a violating input and asserts the validator catches it. The harness lives at `scripts/falsifier-harness/`.

**Shipped tests** (run `bash scripts/falsifier-harness/run-all.sh`):

- `valid-baseline`: clean manifest passes
- `H11-owned-path-overlap`: same-phase owned_paths collision caught
- `H13-missing-phase`: missing `phase` field caught
- `H14-artifact-exists`: pre-existing artifact at a `produces` path caught
- `H15-missing-producer`: orphan `consumes` without earlier-phase producer caught
- `freeze-list precondition required`: owned_path on freeze list without precondition caught

**Validator** at `scripts/validate-daily-log.py` (stdlib-only; no PyYAML dep needed). Auto-invoked as part of the iron law "Dispatch graph before dispatch" pre-dispatch check.

Adding a new falsifier requires (a) the check in the validator, (b) a fixture under `scripts/falsifier-harness/fixtures/<test-name>/`, (c) a `run_test` line in `run-all.sh`. The falsifier is not considered shipped until its harness test passes.

## Private-path leak scan (iron-law severity, added 2026-05-19)

Empirical scan, not inferred. Before any commit, bundle refresh, or push of any specialist skill or its templates, run the trainer's verify script (`scripts/verify_trainer_sync.sh`); invariant 8 checks for operator-local absolute paths and gitignored-workspace prefixes across tracked files. The exact grep pattern lives in the script, not here, so this rule body does not trigger the scanner.

If any match returns, halt and route to the operator for explicit acknowledgement. No "I read the file and there shouldn't be a path" overrides; the verify script is the gate.

## Quick reference: the five-pillar prompt

Every prompt MUST contain:

1. **Worktree setup** as the first command the agent runs (or a documented exception when scope is single-file and read-mostly)
2. **Baseline capture** (test count, **failing-test names**, HEAD SHA, lint state, mypy state if applicable)
3. **Scope + out-of-scope** as explicit file lists, including review gates
4. **Commit + DO NOT PUSH** discipline; operator pushes at end of batch
5. **Post-session log** appended to the project's daily log at `localonly/daily/<YYYY-MM-DD>.md` under the agent's named subsection (v0.4.0+). Legacy per-agent path `localonly/session-logs/<date>-agent<N>-<slug>.md` remains valid for projects not yet adopting daily-log dispatch.

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

For v0.4.0+ daily-log dispatch, the daily-log template at `templates/daily-log.md` is the single artifact containing manifest, wave narrative, per-agent entries, and end-of-day summary. The freeze-list schema at `templates/high-stakes-list.yaml` defines the project's high-stakes files. Both templates ship with annotated buds and mailchimp examples.

For handing off the *orchestrator role itself* to a fresh chat when context-window pressure or IDE slowdown forces rotation, see `templates/orchestrator-handoff-prompt.md`. The orchestrator handoff is a distinct pattern: it transfers a long-running coordination role rather than spawning a scoped worker. Same five-pillar discipline plus eight orchestrator-specific falsifiers (HO1-HO8 in the template).

## Run the falsifier checklist before spawning

Before pasting the prompt to a fresh chat, run the falsifier checklist at `references/falsifier-checklist.md`. Each falsifier is a known prompt-failure mode observed in real sessions. Resolve every High-severity item; document any deferred Med/Low items in the agent's "Surprises" log section so the next iteration of the prompt can address them.

## Worktree discipline

Default: every dispatched agent works in its own git worktree at `<project>/.worktrees/<task-slug>/`. The worktree gives each agent its own `.git/index.lock`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, and optionally `.venv/`. Without it, parallel agents collide on shared state.

### Directory-selection priority

Pick the worktree directory in this order:

1. **Existing `.worktrees/` directory.** Use it. (Hidden, project-local; the strong default.)
2. **Existing `worktrees/` directory.** Use it. (Visible alternative; some projects prefer it.)
3. **Existing `<project>.worktrees/` sibling directory.** Use it. The sibling pattern (worktrees live alongside the project, not inside) avoids the gitignore preflight entirely because the worktree directory is outside the project tree. Some operators prefer this for cross-project worktree management or to keep IDE file-watchers from picking up worktree content. If the project already has a `<project>.worktrees/` sibling, use it; do not migrate to the inside pattern without operator direction.
4. **CLAUDE.md or AGENTS.md preference.** If the project's agents doc names a worktree directory, use that without asking.
5. **Ask the operator.** No directory exists and no doc preference: ask whether to create `.worktrees/` (project-local hidden) or a global location like `~/.config/superpowers/worktrees/<project>/`.

Borrowed from `obra/superpowers-skills` `using-git-worktrees`. The priority matters because mixing locations across batches creates ghost worktrees the operator forgets to clean up.

### Gitignore pre-flight (project-local only)

Before creating a project-local worktree, verify the directory is gitignored:

```bash
git -C <project> check-ignore -q .worktrees 2>/dev/null
```

If not ignored, add it to `.gitignore` and commit before proceeding. Skipping risks the next `git add .` pulling worktree contents into the main checkout. Global worktree locations outside the project skip this check.

### Project-setup auto-detect

After `git worktree add`, run the right install command from the worktree manifest, not from operator memory:

```bash
[ -f package.json ] && npm install
[ -f Cargo.toml ] && cargo build
[ -f pyproject.toml ] && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
[ -f requirements.txt ] && python -m venv .venv && .venv/bin/pip install -r requirements.txt
[ -f go.mod ] && go mod download
```

The first match wins; the agent runs one install path. Worktree-local venv is required for any Python project that mutates `.venv`; without it the shared venv corrupts mid-flight and the operator's parallel work breaks.

### Clean-baseline verification

Before declaring the worktree ready, run the test suite once to verify a green baseline. If tests fail, the agent stops and reports rather than attributing failures to its own work later. Pattern from `using-git-worktrees`.

Baseline capture also includes branch verification and dirty-state inspection. The agent's first two `run_command` calls in any same-tree dispatch:

```bash
git -C <project> branch --show-current
git -C <project> status --short
```

The prompt names the expected base branch (typically `main`); if `branch --show-current` returns anything else, the agent stops to avoid committing on top of a sibling's in-flight feature branch. `git status --short` reports pre-existing dirty state: any non-empty output is foreign-leak from a prior session or sibling agent, flagged as not-mine, never `git add .`'d, never reset, excluded from commits.

### Worktree setup, compact form

The agent's first-step block, end to end:

```bash
git -C <project> check-ignore -q .worktrees 2>/dev/null || { echo "add .worktrees/ to .gitignore first"; exit 1; }
git -C <project> worktree add <project>/.worktrees/<task-slug>
# Auto-detect install (see above)
# Run baseline tests; report count + failing-test names
```

**Operationalization.** The pre-spawn check is enforced empirically by running `python3 ~/Projects/superset.skill/scripts/validate-daily-log.py <project>/localonly/daily/<YYYY-MM-DD>.md` on the daily-log manifest. The validator enforces hard falsifiers (H11 owned-paths non-overlap within phase, H13 phase field required, H14 artifact-existence pre-dispatch, H15 producer-consumer chain or live-tree fallback, DAG acyclicity, freeze-list precondition) and emits soft warnings (PV-1 owned_paths live-tree existence, S1 typed-signals presence). Exit 0 means no hard falsifiers fired; warnings appear on stderr but do not block. The Mozilla-mythos falsifier harness at `scripts/falsifier-harness/run-all.sh` is the regression gate that asserts the validator itself catches the violations it claims to catch; `verify_trainer_sync.sh` invariant 9 wires the harness into every bundle refresh.

**Retro-authored manifest support (Q03, v0.7.0).** Frontmatter key `retro_authored: true` declares that the manifest was written after the work was done, for the purpose of Track B1 format-coverage validation. The validator skips H14 (artifact-existence pre-dispatch) when this flag is set, because produced artifacts exist by definition in retro manifests. H15 (producer-consumer chain) still applies but now accepts live-tree-existing consumed paths as valid producers, which means retro manifests with cross-phase dependencies on pre-existing project files validate cleanly without fabricating producer entries. Retro manifests are evidence for format-coverage validation, NOT for pre-dispatch enforcement evidence; the distinction matters for Phase 3 compression gates.

**Path-verify soft warning (Q02 / PV-1, v0.7.0).** The validator emits a PV-1 warning for every `owned_paths` entry that does not exist in the live project tree at validation time (literal paths) or matches zero files (glob patterns). PV-1 is a soft warning, not a hard fail, because forward batches legitimately name not-yet-created paths in `owned_paths`. The warning surfaces dispatch-time vs action-time path drift: when an orchestrator-handoff doc says "the file is at X" but a recent rename moved it, PV-1 catches the orchestrator's stale-path copy-paste before the worker hits a missing-file error mid-dispatch. The agent-prompt template's worker-side complement is a Step 0 grep-verify block (deferred to a future v0.7.1 template patch).

**Typed signals soft warning (Q01 / S1, v0.7.0).** The validator emits an S1 warning for every agent row missing a `signals:` key. The convention is: declare `signals: []` to explicitly opt out, or populate with `[{kind: violation_caught | no_op | retrospective | other, description: ..., promoted_to?: ...}]` for non-commit-producing work. The warning prompts orchestrators to either explicitly opt out or populate, catching the per-commit-ledger blind spot where violations caught mid-flight, no-op dispatches, and retrospective insights drop on the floor of the daily-log if the operator only thinks in terms of commits.

All subsequent commands run with `Cwd=<project>/.worktrees/<task-slug>`.

**Same-tree exception:** when scope is BOTH single-file AND read-mostly AND the operator has no parallel work AND no `docs/specs/*` (or equivalent project-gated) file is touched, skip the worktree. Document the skip in the prompt's worktree section. The H5 falsifier check still applies, with the same-tree note as the resolution. If the task escalates mid-flight from read-mostly to edit (e.g., an audit discovers a row that needs adding), the exception voids: the agent stops, escalates to operator, and moves to a worktree before committing the edit.

**No-git exception:** when the project is not a git repository, worktrees are unavailable and the same-tree exception's read-mostly precondition does not fit author-tasks. Parallel-collision risk is mitigated instead by disjoint `owned_paths` across sibling workers, enforced by the daily-log manifest validator's H11 check. The agent's prompt states the no-git context once near the worktree section and names the mitigation strategy. Worked example: the 2026-05-19 self-bootstrap batch on `superset.skill` itself, which dispatched three parallel workers (A1 templates, A2-A3 templates, A4a scripts) under no-git context with disjoint owned_paths across templates and scripts directories.

The H5 falsifier accepts three resolutions: Shape A (worktree setup is the first command), Shape B (same-tree exception with all four preconditions plus the mandatory first two commands and the escalation-void clause), or Shape C (no-git exception with stated parallel-collision-mitigation strategy). The prompt-level harness at `scripts/prompt-level-harness/` enforces the disjunction.

### Pre-spawn check (orchestrator-side)

Before dispatching a parallel batch, the orchestrator verifies EVERY agent in the batch has its own worktree, OR an explicit same-tree exception with all four preconditions (single-file, read-mostly, no parallel work, no gated-doc edits). If any agent is unworktreed without exception, the batch waits or the unworktreed agent moves to a worktree first. Mixed batches (some worktreed, some same-tree without exception) accumulate live state changes in the main checkout that break baseline capture for the same-tree agents.

Anti-pattern: dispatching agents one at a time without worktrees, accumulating multiple in the same main checkout. The race is silent until two agents write to the same file. Worked example: buds 2026-05-19 voice-scatter agent ran in its worktree while at least three other agents wrote to main checkout concurrently; live git status rotated across three consecutive checks as commits landed mid-session. The race was contained by byte-range-disjoint edits; next recurrence may not be so lucky.

### Cross-checkout artifact dependencies

When an agent uses BOTH a worktree AND a `localonly/` artifact (audit doc, plan, decision log) in the main checkout, the prompt notes the cross-checkout dependency. Two patterns:

- **Hard-link**: `ln <main>/localonly/<file>.md <worktree>/localonly/<file>.md` so the agent can read/edit from either checkout.
- **Operator-facing record**: commit the localonly file's path into the session log so the next agent finds it without searching.

Without the note, a reader in the worktree cannot see the audit doc in main, and a reader in main cannot see the worktree's commit; the audit-and-commit pair becomes invisible from either single vantage. Worked example: buds 2026-05-19 voice-scatter `localonly/plans/voice-scatter-audit.md` lived in main checkout while the OQ16 commit lived in `buds.worktrees/voice-scatter-audit-oq16/`; the audit's Phase 3 ship-log section had to be edited in main checkout to point at the worktree branch.

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
- **Parallel `run_command` Cwd race in same-tree dispatch.** When the agent issues multiple `run_command` calls in a single parallel batch and a sibling agent is concurrently active in the same checkout, some calls land in the wrong working directory. Symptom: one git call in the batch returns a valid SHA, a sibling git call in the same batch reports "not a git repository", and `ls tests/foo.spec.js` reports the file missing while subsequent sequential calls confirm it exists. Worked example 2026-05-18: Agent E (TC-9030 oracle-pilot move on `mailchimp-r-and-a-qa-suite`) dispatched without a worktree (H5 failure); the parallel batch failed sporadically during baseline capture, recovered by switching to sequential calls. A separate symptom of the same root cause: `git add` succeeded but the subsequent `git commit` failed with "no changes added to commit" because a sibling agent's concurrent git operation cleared the index between the two calls. Prevention: comply with H5 (worktree per agent). Defense-in-depth: sequence baseline-capture calls instead of parallelizing them, combine `git add` + `git commit` into a single script invocation when same-tree is unavoidable, and use `git -C <path>` form for path-explicit invocations. Recurrence count buds 2026-05-19: ≥2 in a single session despite documentation.
- **Live-run mobile-app screenshot is harder than it looks.** `xcrun simctl` has no tap-by-coordinate command. Live-run navigation requires either `idb` (Meta's iOS debug bridge, separate install + config) or the Flutter VM-service protocol (`flutter drive` + Dart-side driver code that talks to the running app). The naive framing "spawn a simulator, navigate by tap, capture screenshots" costs 4-8 hours to implement correctly; the static-baseline framing (one `integration_test` per screen, `flutter drive` captures each) costs 1-2 hours. When a prompt asks for screenshots and the operator frames it as 30-min work, the orchestrator surfaces the simctl limitation before authoring the prompt. Worked example: buds 2026-05-19 `screenshots-v5-baseline` prompt was revised from live-run framing to static-baseline framing after the operator asked clarifying questions; the static framing is what shipped.

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
