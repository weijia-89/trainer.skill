# Orchestrator handoff prompt template

Use this template when the current orchestration chat hits context-window
pressure (IDE slowing, accumulated history > ~50% of window, multi-day
multi-batch coordination needs a fresh start) and the orchestrator role
needs to migrate to a new chat.

Distinct from `agent-prompt.md`: an *agent* prompt spawns a worker for a
scoped task. A *handoff* prompt transfers a long-running coordination role
to a fresh chat without losing context.

The handoff prompt is itself a superset-shaped artifact. The orchestrator
chat is a long-running coordination "body" that, like a worker agent,
has its own task scope and gets handed off cleanly when the chat saturates.
The handoff is the rest interval between two orchestrator chats.

---

## When to use

Spin up a fresh orchestrator chat when any of these fire:

- The current chat is visibly slowing the IDE (UI lag, slow tool calls).
- The current chat has been coordinating a multi-batch parallel-agent
  push across multiple days and accumulated 30+ tool calls.
- The current chat's context contains noise the new orchestrator does
  not need (e.g., long debugging detours that are now resolved).
- The operator explicitly asks for a fresh chat.

Do NOT spin up a fresh orchestrator just because a single batch
returned with one surprise. Surprises are normal; the existing
orchestrator can handle them. Spin up fresh only when the chat itself
has become a bottleneck.

## Structure of a handoff prompt

The handoff prompt has eight required sections plus embedded artifacts.

### 1. Role declaration

State explicitly: "You are the new orchestration Cascade chat for
`<project>`. The previous orchestration chat is being retired because
`<reason>`; you take over coordination from here. Operator is
`<operator-name>`."

State the no-autonomy rule: "You have no autonomy between Wei's turns.
Never say 'I'll check back,' 'I'll poll,' 'pinging you when the agents
finish.' All false. When work is in flight in the agent chats, the
operator pings you back when something needs your attention."

State the role boundary: "You ORCHESTRATE. You DO NOT EXECUTE the agent
work. Each parallel agent runs in its own fresh Cascade chat that the
operator opens and pastes the prompt into. The operator is the channel
between you and the agent chats; you cannot message between chats
directly."

### 2. First steps (mandatory, in order)

1. Invoke `trainer` skill.
2. Invoke `superset` skill.
3. Declare tier (orchestration is typically vibe-careful: coordination
   decisions blast across multiple parallel branches and operator
   review-bandwidth, but no source-edit authority).
4. Read project's AGENTS.md / CLAUDE.md in full.
5. Read project's ROADMAP.md or equivalent plan document.
6. Run state-verification commands and report back to operator.

### 3. State-verification commands

The fresh chat runs these as its first action. Treat live state as
canonical. The handoff states what was true at authoring time; the live
commands establish what state is now.

Minimum command set for git-based projects:
```
git -C <project-root> fetch --prune
git -C <project-root> log --oneline -10 main
git -C <project-root> worktree list
git -C <project-root> status --short
gh -R <owner>/<repo> pr list --state all --limit 12 --json number,state,headRefName,mergedAt --jq '.[] | "\(.number) \(.state) \(.headRefName) \(.mergedAt // "open")"'
```

Adapt for non-git projects: equivalent state pulls for whichever
artifact stores match the project's truth.

### 4. Stated context at handoff time

Every fact the new chat needs that cannot be re-derived from live
state. Includes:

- HEAD SHA at handoff authoring time (live state may have advanced).
- Open PR list at handoff authoring time.
- Worktree state at handoff authoring time.
- Rollback SHA if the next batch goes sideways.
- Any project-specific deviations from superset defaults (e.g., the
  push-vs-no-push policy; CI architecture; calibration-log discipline).

Every fact must be one live state can confirm or refute. Flag any fact
that was "true at handoff time but un-verifiable later".

#### Per-fact confidence-tier tagging

Each fact in section 4 carries one of four epistemic tags from the
`epistemic-planning` skill. The new orchestrator reads the tag to know
which facts to re-verify first.

- `[verified]`: the orchestrator confirmed by running a command or
  reading a file within the last 30 minutes.
- `[inferred]`: the orchestrator derived from another verified fact
  or from the daily log, but did not directly verify.
- `[speculative]`: the orchestrator's best guess; the new orch
  should prioritize verifying this before acting on it.
- `[unknown]`: the orchestrator does not know; the new orch must
  establish.

When a fact's tag is ambiguous, default to the weaker tag. A fact
that might be `[verified]` but rests on a 45-minute-old check
becomes `[inferred]`.

Worked example, four lines of stated context:

```
HEAD SHA on main: 3a7f1b2 [verified] (git log -1 main, 12:04)
Open PRs: #41 (Agent B), #43 (Agent C) [verified] (gh pr list, 12:04)
Operator's intensity expectation for the rest of the day: light review only [inferred from daily log entry at 09:30]
Whether CI cleared on #43 after the last rebase: [unknown]
```

### 5. Plan ahead

The next 3-5 calendar days of planned work, calibrated to operator
intensity. Show parallel-vs-sequential structure so the new chat
understands which batches can fire when.

### 6. Role discipline

A two-column "YOU DO / YOU DO NOT" table. Examples of YOU DO NOT:

- Execute agent-level work yourself.
- Push commits.
- Modify production source (read-only references only).
- Claim "I'll check back" or "I'll poll."
- Skip verification before claiming an agent's work is done.
- Edit embedded agent prompts when passing them to the operator (copy
  verbatim; drift introduced by paraphrase has bitten projects before).

### 7. Decision protocol for surprises

What the new chat does when an agent returns with a STOP-and-report
state, or when two agents conflict on a file the prompts said was
disjoint, or when CI gates fire unexpectedly. Surface the canonical
escalation path.

### 8. Iron-law restatement

The always-on rules reload automatically in the new chat, but a brief
restatement near the top helps the orchestrator recall them at the
moment of relevance:

- safe-terminal (no newlines in run_command, no heredocs, single-line
  or write-to-tmp-first).
- async-handoff (no self-check-in claims).
- wei-voice (or project's equivalent voice rules).
- superset (the very skill the orchestrator is operating under).
- Any project-specific iron laws.

### Embedded artifacts: the agent prompts themselves

The handoff embeds the full text of each agent prompt the new
orchestrator will dispatch. Use `===AGENT N PROMPT START===` /
`===AGENT N PROMPT END===` markers so the orchestrator can locate them
programmatically. Do NOT abbreviate or paraphrase; copy verbatim.

Why embed and not persist-to-disk: gitignored paths block
`write_to_file` in some IDE configs; persistence-to-disk via
python-script-to-/tmp adds complexity. Embedding is the most reliable
artifact transfer.

### When verbatim vs reference-by-path

Verbatim embedding (the `===AGENT N PROMPT START===` block) is the
default. Reference-by-path is the documented exception when
verbatim is impractical.

**Verbatim embedding is required when all of these hold:**

- The agent prompt is 200 lines or fewer.
- The agent prompt will be used as-is by the operator with no
  further customization expected.
- The handoff is the primary artifact preserved across the
  rotation, so the prompt body must travel inside it.

**Reference-by-path is acceptable when any of these hold:**

- The agent prompt exceeds 200 lines and embedding bloats the
  handoff past usable length.
- The agent prompt is ephemeral, intended for one-time use (a
  CI-unblock worker, a single-shot scope correction).
- The agent prompt was authored in a separate worker chat and the
  file already exists at a stable path the operator can find.
- The agent prompt is being actively revised between handoff and
  dispatch.

When using reference-by-path, the handoff MUST include:

- The exact absolute path to the prompt file.
- A one-paragraph summary (so the new orchestrator can dispatch
  without reading the full file).
- The explicit rationale, citing one of the conditions above.
- An expected-state note: "If this file does not exist when you
  reach this step, STOP and report to operator."

Worked example, one verbatim block and one reference-by-path
block:

```
===AGENT 1 PROMPT START===
Role declaration: ...
First steps: ...
Task: ...
[full prompt body, 140 lines]
===AGENT 1 PROMPT END===

===AGENT 2 PROMPT (reference)===
Path: $HOME/Projects/<project>/localonly/agent-prompts/2026-05-19-agent2-rebuild-index.md
Summary: Rebuilds the corpus index after the schema change in PR #41 landed. Single-file scope; out-of-scope guard on everything else under data/.
Rationale: prompt is 612 lines (above the 200-line verbatim threshold) and lives at a stable path the operator already knows.
Expected state: if the file does not exist when you reach this step, STOP and report to operator.
===AGENT 2 PROMPT (reference) END===
```

## Falsifier checklist additions for handoff prompts

In addition to the general falsifier-checklist for agent prompts, the
handoff prompt must pass:

| # | Falsifier | Test | Fix |
|---|---|---|---|
| HO1 | State facts are verifiable against live state? | Every fact in "Stated context" has a corresponding command in "State verification"? | Add the missing verify command |
| HO2 | "Treat live state as canonical" stated explicitly? | grep handoff for the phrase or equivalent | Add it |
| HO3 | YOU DO / YOU DO NOT scope table present? | grep for the table | Add the table |
| HO4 | Agent prompts embedded verbatim OR reference-by-path with stated rationale? | Each agent prompt has either a `===AGENT N PROMPT START===` block (verbatim) OR a `===AGENT N PROMPT (reference)===` block citing the file path and stating why reference-by-path is appropriate? | Re-paste verbatim OR add reference-block with rationale |
| HO5 | Rollback SHA stated explicitly? | grep for "rollback" or "reset --hard" | Add the rollback line |
| HO6 | Trainer + superset load as steps 1 and 2? | First-steps section ordering | Reorder |
| HO7 | No-autonomy / no-poll discipline stated? | grep for "no autonomy" or async-handoff reference | Add restatement |
| HO8 | Initial action is "verify state, report, wait" not "spawn"? | Last section of handoff | Rewrite the close |
| HO9 | Every fact in "Stated context" carries a `[verified\|inferred\|speculative\|unknown]` tag? | grep handoff for tag count vs fact count | Tag each fact |
| HO10 | Status-claim evidence iron law: outgoing-handoff `validate-track-status.sh` run in the same turn as summary authoring? | `bash scripts/validate-track-status.sh <today's daily log>`; every status claim in the summary cites a row from the output, not narrative recall | Run the validator; replace narrative claims with cited evidence rows; route any `status-unverified` or `planned-but-evidence-present` verdict to operator before handoff |

## Common mistakes

- **Paraphrasing the embedded agent prompts.** The handoff is long;
  the temptation is to summarize each prompt to one paragraph. Do not.
  The fresh orchestrator passes prompts verbatim to the operator.
  Paraphrase = drift = the agent's worktree assumptions go subtly
  wrong.
- **Stating "as of handoff time" facts as if they are current.** The
  fresh chat may not run for hours after authoring. Mark every
  time-sensitive fact with the authoring timestamp and the "verify
  against live state" reminder.
- **Forgetting the rollback SHA.** If a batch goes sideways, the
  orchestrator needs to know the pre-batch HEAD to reset main to.
  State it once in "Stated context."
- **Missing the no-autonomy reminder.** A fresh orchestrator inherits
  the always-on async-handoff rule from memory, but the long handoff
  gives the chat plenty of opportunities to drift into "I'll check
  back" framings. State the rule near the top, restate near the close.
- **Initial action says "spawn the four agents."** The orchestrator
  is not a Cascade-internal scheduler; only the operator can open
  agent chats. The orchestrator's initial action is "report verified
  state to operator and wait." Spawn happens when the operator
  copy-pastes the prompts into agent chats.

## Worked example

A reference worked example lives at
`<PROJECT>/localonly/orchestration/<DATE>-<batch-slug>.md` in the
operator's working notes. The reference batch was a multi-day MVP push
with four parallel Day-1 agents and two additional sequential batches
across Days 2-3, including a project-specific push-then-PR deviation
documented inline. Adapt the worked-example path to your own project's
convention.
