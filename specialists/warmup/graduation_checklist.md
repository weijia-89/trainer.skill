---
type: self-assessment
parent_skill: warmup
purpose: operationalize the outgrow signal mentioned in SKILL.md
---

# Graduation checklist

`warmup` is a front desk. The point of a front desk is to be unnecessary once you know the building. This file makes "do I still need this skill?" answerable instead of vibes.

## How to use this file

Read it once a month while you're still actively using `warmup`. When you can answer **yes** to all six items on two consecutive monthly reviews, stop invoking `warmup` and go directly to the downstream skills.

## The six items

### 1. Routing recall (cold)

Without looking at `SKILL.md`, write down which downstream skill handles each of the following situations:

- You just had an idea for a side project. (Answer below.)
- You opened a PR and want a 5-minute review of one change. (Answer below.)
- Your deploy made things worse and you need to roll back. (Answer below.)
- You think you ran `git reset --hard` on uncommitted work. (Answer below.)
- The AI just wrote 200 lines and you do not feel like reading them all. (Answer below.)

Then check against the routing table in `SKILL.md`. Pass = 5/5 correct from memory.

Expected answers: program; form-check (Floor 1 or Floor 2); pr §5 then diet §3 if symptoms persist; safetybar §1; gymbuddy §3.4.

### 2. Tier classification under 30 seconds

Pick a recent PR or change you made. Without looking at `form-check/learner/QUICKSTART.md`, classify it as vibe-safe, vibe-careful, or vibe-dangerous. Time yourself.

Pass = correct classification in under 30 seconds. ("Correct" here means it matches what the QUICKSTART would say; cross-check after.)

### 3. Incident reflex test

Imagine: it is 2am, prod is throwing 500s, users are complaining in Slack. What is the first sentence of your response? Where do you go for the next 30 minutes of work?

Pass = your answer references `diet §3` (or its content) without you reaching for the routing table. Bonus: you mention "stop the bleed" or "acknowledge before debugging."

### 4. Ecosystem map without prompting

Draw the eight-skill graph on a piece of paper (or describe it aloud) without looking at the ASCII diagram in `SKILL.md`. Get all eight names. Note which two are pre-build (warmup, program), which is the central library (form-check), which is the engagement runner (recovery), which two are post-deploy (pr, diet), which two are cross-cutting (safetybar, gymbuddy).

Pass = all eight present, with their phase correctly identified.

### 5. AI workflow self-check

Honest answer: In the last 30 days, did any of these happen?

- I accepted an AI diff in under 5 seconds without reading it.
- I shipped code I could not explain to another developer.
- The AI suggested a destructive command and I ran it before reading it.
- I delegated an architectural choice to the AI without checking it against the stack-decision rubric.

Pass = no, or yes-but-I-noticed-and-corrected. If yes-and-I-just-shipped, you have not graduated from `gymbuddy §3.4` yet, even if the rest of this checklist is solid.

### 6. The honesty item

Without consulting `SKILL.md` or this file: what is the *most useful* thing `warmup` ever did for you? What is the thing you most often *bypass* it for?

Pass = you can answer both. If the most-useful thing was a one-time setup (early invocations) and the bypass list is "most things now," you have already outgrown the skill in practice and this file just confirmed it.

## What "graduated" looks like

- You stop invoking `warmup` as a routing step. You go directly to the downstream skill you need.
- You still keep `warmup` installed. It costs nothing to keep loaded; the next developer in your shared environment may not have graduated yet, and you may regress on the cross-cutting items (item 5 especially) and want to re-check.
- You re-read this checklist if any of the following happen: you onboard onto a new codebase, you switch primary AI assistants, you have an incident you handled poorly, or any 90-day period has passed since the last review.

## What "not graduated yet" looks like

- You answer 4 of 6 items correctly. Stay with `warmup` for another month; re-read the failed items' downstream skills with deliberate practice (per `form-check/learner/study_protocol.md` Habits 1 and 2).
- You answer 6 of 6 once but 3 of 6 the next month. The earlier pass was likely false familiarity (Habit 7 calibration: you over-predicted). Stay with `warmup`; the spaced-repetition cadence is doing its job.

## For the agent harness (optional logging contract)

The skill does not require logging. If a harness implementer wants to track invocations to surface this checklist automatically, the contract is:

- Each invocation appends one JSONL line to `~/.warmup/invocations.jsonl`:
  ```json
  {"ts": "2026-05-15T15:30:00-04:00", "trigger_keyword": "should I ship this", "routed_to": "form-check", "user_outcome": null}
  ```
- After 5 invocations with consistent routing (e.g. user always picks form-check for the same kind of trigger), the harness prompts: "You have routed to `form-check` 5 times in a row from this keyword. Want to invoke it directly next time and skip the front desk?" The user accepts or declines.
- After 15 invocations total, the harness surfaces this checklist regardless of routing pattern.

The logging is local-only. No telemetry leaves the machine. The `.warmup/` directory is gitignored in any skill consumer's project (see `warmup.skill/.gitignore.template` if added).

## Provenance

This checklist exists because `SKILL.md`'s original "outgrow within 5–10 invocations" prose was descriptive, not operational. A self-assessable checklist replaces the vibes-based graduation signal with one the user can actually run. Item 6 (the honesty item) is the load-bearing one; the rest are corroborating evidence.
