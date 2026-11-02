---
name: logbook
description: |
  Use when work spans sessions, resumes after a break, or needs a proof trail: "what did I do last," "pick up where I left off," "log this work," "did we already try this," "what is next," "prove that work happened," "session handoff." The logbook keeps one per-project, append-only training log: every work slice is a set with a weight, a proof, an outcome, and the next set on the bar. Composes with warmup (open the logbook at session start) and program (multi-session plans). Not a spec-execution loop and not a replacement for the session scratchpad.
type: project-skill
version: 1.0.0
authors: Wei Jia (2026-11-01)
license: LicenseRef-IronLaw-NC-1.0
required_tools: [file_read, shell]
recommended_tools: [git, grep]
optional_tools: []
composes:
  - skill: warmup
    version: ">=2.0.0,<3.0.0"
    role: opens the project logbook before work starts
---

# logbook: the training log for work that spans sessions

```
IRON LAW: IF IT ISN'T IN THE LOGBOOK, IT DIDN'T HAPPEN

A set without proof is not progress. Run verify before you claim any.
```

## What this specialist does

- Keeps one append-only record per project: the objective, every work slice, the proof behind it, the outcome, and the next slice.
- Makes proof checkable: `verify` is the form check. A slice without an evidence path reports `EV_UNVERIFIED`; a path that moved reports `EV_MISSING`. Neither counts as progress.
- Refuses to rewrite history: a missed slice is logged as missed, never deleted.
- Stays local: one gitignored folder in the project, standard library only, no network, no installs.

## When to use it, and when not to

Use it when the work outlives one session, when you are resuming, when someone asks what was already tried, or when a claim needs proof.

Do not use it for one-shot lookups that leave no artifact, and do not use it as the source of truth for repo state - git owns that. It does not replace the session scratchpad (`.agent/scratchpad.md` is session working memory; the logbook is the durable record you carry into the next session).

## The seven steps of a logged session

1. **Open the logbook once per project** (skip if `.workledger/` already exists).
2. **Read the state before working** - objective, non-goals, next set on the bar, recent sets.
3. **Log each set as you finish it**, not at the end of the session.
4. **Tag the outcome**: `logged` (done and proved), `missed` (tried, did not land), `pr` (the milestone).
5. **Name the next set** before you stop, so the next session starts warm.
6. **Verify before you claim progress** - run the form check, report its classes as they are.
7. **Close out** with the last verify result and the next set on the bar.

## Commands

```bash
LB="python3 ~/Projects/trainer.skill/specialists/logbook/scripts/logbook.py"

# 1. open (once per project)
$LB init --objective "ship the parser" --authority "the spec in docs/" --non-goal "no UI work"

# 2. read state
$LB status

# 3. log a set (proof is a path, never file contents)
$LB record slice --what "wrote the tokenizer" --scope "one function" --evidence "src/parse.py"

# a set with nothing to point at is allowed, but it stays unverified
$LB record slice --what "read the old module" --scope "30 minutes" --no-evidence "reading only"

# 4. tag the outcome
$LB record outcome --outcome logged --id <slice id>

# 5. name the next set
$LB record next --what "wire the tokenizer into the CLI"

# 6. form check
$LB verify
```

`--project PATH` points the command at a specific project; without it, the nearest git root above the working directory is used.

## Failure modes

| What you see | What happened | What to do |
|---|---|---|
| `refused: that set is already logged` | the same set (same work, same scope) is already in the log | log a different set, or tag the existing one by `--id` |
| `checkpoint-tail-unknown` | the last record was cut off mid-write | run any `record` command to repair the tail, then `status` |
| `EV_MISSING` | the proof path no longer exists | fix the path or log a new set with the current path |
| `EV_UNVERIFIED` | the set was logged without proof | progress is not claimed; log the artifact, or say why there is none |
| `no sets logged yet` (exit 2) | the logbook is empty | log a set first; an empty logbook never passes |
| `refused: pass --evidence or --no-evidence, not both` | both proof flags were given | pass one |

## Rules

- Evidence fields carry paths only. Never put file contents, tokens, or secrets into the log.
- Never edit `ACTIVE_STATE.md` by hand. It is generated after every write; use `record next` and `status`.
- Never edit or delete `ledger.jsonl`. The log is append-only, and repairs happen only through the tool.
- The `.workledger/` folder ignores itself (`.gitignore` holds `*`), so notes stay on this machine. If a team wants the run history in git, that is a deliberate choice, not a default.
- One writer at a time is enforced by a file lock; two agents in the same project cannot interleave records. If a set is logged twice by a race, one write wins and the other is refused.
