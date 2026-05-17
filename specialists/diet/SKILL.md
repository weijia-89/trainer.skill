---
name: diet
description: |
  Use when production is broken, when setting up steady-state observability for a deployed app, or during/after an incident. Symptoms: alarm fired, users reporting errors, deploy made things worse, server crashed, no idea whether app is working, post-mortem to write.
type: project-skill
version: 2.0.0
authors: Wei Jia (1.0, 2026-05-15); v2 Iron Law layering + composes-pin to form-check@>=3 2026-05-16
license: MIT
required_tools: [file_read, shell]
recommended_tools: [grep, web_search, git]
optional_tools: [browser]
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: composes the threat-model and reversibility checklists during incident response
  - skill: safetybar
    version: ">=1.1.0,<2.0.0"
    role: routed-to when the incident response requires a code rollback
---

# diet — the daily discipline that supports the lifts

```
IRON LAW: NO DESTRUCTIVE ACTION DURING AN INCIDENT WITHOUT A SECOND HUMAN'S EYES.
```

Violating the letter of this rule is violating the spirit of this rule. "Just this one command, it's quick" is the rationalization that produced the Replit production-DB-deletion incident (`REPLIT-FORTUNE`, `AIID-1152`). The second human is non-negotiable on vibe-dangerous incident moves. **If solo: pause 10 minutes, re-read §3.3, then act — or revert/disable rather than delete/migrate.**

## Red Flags — STOP and re-read §3 before doing anything

If any of these thoughts is in your head during an incident:

- "I just need to drop this table to fix it." (You don't.)
- "Force-push will undo the bad deploy faster than revert." (No — see `safetybar §2.2`. Use `git revert`.)
- "Let me run this migration to clean up the data state." (Migrations during incidents are forbidden — §3.3.)
- "The user data looks corrupted, I'll just delete it." (The "junk" might be the only evidence. §3.3.)
- "I'll disable the noisy alert so I can focus." (You're blinding yourself. §3.3.)
- "It's been 25 minutes, I just need to fix it now." (The 30-minute timer means *escalate*, not *escalate-the-risk*.)
- "I know what's wrong, I'll skip the four-question triage." (You don't. §3.2.)
- "The agent suggested this command, it's probably right." (The agent has no skin in the game. You do. Ask a human.)

Each red flag means: stop. Re-acknowledge the incident in writing ("we're investigating an issue affecting X"). Set the 30-minute timer. Walk §3.2 four-question triage. Then act.

## Rationalizations — what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "I have to fix it now, no time for the protocol" | The protocol *is* the fastest path. Skipping triage is how you turn a 5-minute incident into a 5-hour incident. |
| "Rolling back is admitting defeat" | Rolling back is admitting *information*. The deploy may be fine; you don't know yet. Roll back, then investigate. |
| "I'm the only one on call, no second human is possible" | A second human asynchronous (Slack, text, anyone) for a 30-second sanity check is still better than zero. If genuinely zero: revert/disable rather than mutate state. |
| "The agent / AI assistant is my second human" | No. The agent does not bear consequences. It is a *tool*; the second human is a *witness*. |
| "I just need to disable this one alert to focus" | The alert is the data. Disable it after the incident, never during. |
| "The error tracking shows new errors, those are unrelated" | They are not unrelated. Treat as related until proven otherwise. |

## Keywords for discovery

For trigger-keyword indexing: production is broken, prod is down, prod is on fire, my server crashed, users are reporting errors, alarm went off, I'm getting errors, observability, logging, monitoring, SLO, SLI, alerting, incident response, post-mortem, RCA, root cause analysis, debugging production, how do I know my app is working, what should I log, error tracking, sentry, datadog, observability stack, my deploy broke things, rollback, the deploy made it worse.

## Scope

You shipped something. Now you need to know it's working, notice when it isn't, and respond without making things worse. This skill covers the *operate* phase of the SDLC, which most beginner curricula skip entirely.

**Scope.** From "code is running in production" to "I understand what it's doing and can intervene safely." Two modes:

- **Steady-state mode** — instrumentation, observability, daily/weekly checks.
- **Incident mode** — production is on fire; what to do in the next 30 minutes.

**Not for.** Pre-deploy work (`form-check`, `recovery`). Deployment mechanics (`pr`). Architecture decisions (`form-check/plan-new-app`).

## How to invoke

- **Steady-state setup** (new project): "I just deployed; what should I instrument?" → §1.
- **Steady-state check** (existing project): "Is my app behaving normally?" → §2.
- **Incident** (something is broken right now): **go directly to §3** — do not read §1 first.

## §1 — Minimum-viable instrumentation

For a beginner-scale project (one service, ≤1k users, single environment), the *minimum* observable surface is:

### 1.1 Structured logs

Every request, every error, every meaningful state change emits a single line of structured (JSON) log. The line includes: timestamp, severity, request-id, user-id (if known), event-name, latency-ms, and any error string.

- **Tool floor.** `console.log` with JSON is acceptable for v0; pipe to a file with rotation. Beyond v0: a log-aggregation service (the free tier of Better Stack, Logflare, or your cloud provider's native log service).
- **Anti-pattern.** Unstructured prose logs (`"Got request from John for /api/foo at 3pm"`) cannot be queried. Always structured.

### 1.2 Error tracking

Every uncaught exception is captured *separately* from logs and grouped by signature.

- **Tool floor.** Sentry free tier is the standard. Bugsnag, Rollbar, or your cloud's native equivalent all fine.
- **Why separately from logs.** Errors are the high-signal stream; mixing them into general logs means you'll miss the signal in noise.

### 1.3 The four golden signals (Google SRE book)

For each user-facing surface, track:

- **Latency** — p50, p95, p99 of request duration.
- **Traffic** — requests per second / per minute.
- **Errors** — % of requests returning 5xx (or app-level errors).
- **Saturation** — how full is the most-constrained resource (CPU, RAM, DB connections, queue depth)?

For a beginner project, this is one dashboard with four charts. Update interval: 1 minute. Retention: 30 days minimum.

### 1.4 Uptime check

A scheduled external probe (Uptime Kuma, Better Uptime free tier, Cron-job.org) hits a health-check endpoint every 1–5 minutes from outside your infrastructure. **External** is load-bearing: if your monitoring is inside the same box as the service, an outage takes both down and you learn nothing.

### 1.5 What to skip at the beginner stage

- **Distributed tracing** (Jaeger, Honeycomb). Useful when you have ≥3 services calling each other. For one service, overkill.
- **Custom metrics infrastructure** (Prometheus + Grafana self-hosted). The setup cost exceeds the value at this scale; use a hosted service.
- **APM agents** (DataDog APM, New Relic). Free tiers are tight; the four golden signals from your platform are usually enough.

## §2 — Steady-state operating cadence

Once instrumented, the operating habit is:

| Cadence | What you do | Time |
|---|---|---|
| Daily | Glance at error tracking; any new error groups? | 2 min |
| Weekly | Walk the dashboard: have the four golden signals drifted? | 10 min |
| Monthly | Review uptime; review alert noise; review what almost-broke. | 30 min |
| Per-incident | Post-mortem (see §4). | 1–2 hr |

**Calibration component** (per `form-check/learner/study_protocol.md` Habit 7): predict what the next week's traffic / errors / latency will be, write the prediction down, measure the gap. Production operations is the single best calibration-training surface in software work because the ground truth shows up on its own.

## §3 — Incident response: the next 30 minutes

Something is broken. **Read this section before doing anything.** If you act first and read later, you risk the Replit-cautionary-tale failure mode (panicked destructive action).

### 3.1 Stop. Acknowledge. Triage.

Before touching anything:

1. **Stop the bleed.** Is the broken thing actively making things worse (e.g. corrupting data, sending wrong emails to users)? If yes, **disable that surface first** before debugging. Roll back, turn off the feature flag, scale to zero — whichever you have. **You cannot debug a moving target.**
2. **Acknowledge.** If you have users / a team / a status page, post a one-sentence acknowledgment: "We're investigating an issue affecting [X]. Updates in 30 min." Acknowledgment costs nothing and buys you focus.
3. **Set a 30-minute timer.** Do not exceed without escalating (in a beginner solo context, "escalate" means: pause and ask a senior, switch to a known-safe state, or post a longer status update).

### 3.2 The four-question incident triage

1. **What changed?** Most outages follow a deploy, a config change, or a dependency upgrade. Check the last 24 hours of: deploys, env-var changes, dependency updates, infrastructure changes, expired credentials, expired SSL certs.
2. **What is the user-visible symptom?** Not the error string — the *symptom*. "Users cannot log in" vs. "Stack trace shows a JWT decode error." The symptom drives priority; the error string drives the fix.
3. **Is the symptom widespread or scoped?** All users? One user? One region? One endpoint? The scope tells you the layer to investigate.
4. **Is it getting worse?** Static (broke and stayed broken) vs. accelerating (broke and is now affecting more users). Accelerating is **always** stop-the-bleed-first.

### 3.3 The forbidden moves during an incident

Per the Replit / Lemkin July 2025 cautionary tale (see `form-check/learner/cautionary_tales.md`):

- ❌ **Never run a destructive command** during an incident without a second human's eyes.
- ❌ **Never `git push --force`** during an incident. If a rollback is needed, use `git revert` (creates a new commit) — see `safetybar`.
- ❌ **Never run database migrations** during an incident. If a migration is the cause, *roll back the migration*; if it isn't, leave migrations alone.
- ❌ **Never delete data** during an incident, even data that looks like junk. The "junk" might be the only evidence of what went wrong.
- ❌ **Never disable instrumentation** during an incident — you are blinding yourself.

If any of those moves is the obvious fix, *write it down* and ask a second human (or wait 10 minutes and re-read this list) before executing.

### 3.4 The rollback decision

Default to rollback if all three are true:

1. The incident started after a known deploy/change.
2. Rollback is *reversible* (you can deploy forward again later).
3. The data-shape didn't change irrevocably (no destructive migrations).

If any of those isn't true, **rollback is itself an incident** — proceed with the same triage above.

For the rollback mechanic: `pr/runbooks/rollback.md` if it exists; otherwise the platform's native rollback (`git revert HEAD && deploy`, `kubectl rollout undo`, `vercel rollback`, etc.).

### 3.5 When you fix it, write the lesson

Before closing the incident, write *two sentences* in `incidents/[date]-[short-name].md`:

- "What broke and why." (One sentence, no blame.)
- "What I'll change so this can't happen the same way again." (One sentence, concrete.)

The two-sentence version becomes the seed for the full post-mortem (§4) within 48 hours.

## §4 — Post-mortem template

```markdown
# Post-mortem — [incident short name] — [date]

## What happened (user-visible)
[1 paragraph: what users saw and for how long.]

## Timeline
- HH:MM — [event]
- HH:MM — [event]
- HH:MM — resolved

## Root cause
[1–2 sentences. Be honest. Almost never "human error" — usually "the system allowed a human to make this error in this situation."]

## What worked
[1–3 things from the response that helped.]

## What didn't
[1–3 things that slowed the response or made it worse.]

## Action items
- [ ] [Concrete, owned, dated. Not "be more careful."]
- [ ] ...

## How could the same class of incident happen again?
[The deepest question — answer it honestly.]
```

**Blame-free** is non-negotiable. Post-mortems written to assign blame produce defensive future post-mortems, which produce no learning. The Etsy / Google SRE / John Allspaw literature converges hard on this point.

## §5 — When to escalate to a real ops team

This skill is calibrated for solo / small-team beginner contexts. Escalate (hire SRE, adopt managed platform, switch to a stack with stronger operational defaults) when:

- You have ≥3 services with inter-service calls and a real outage in the last 30 days.
- Your dashboard has ≥10 charts and you don't look at most of them.
- The four golden signals are insufficient (you need real distributed tracing).
- You are the only person who can debug production and you cannot take a vacation safely.

The exit signal is not "the skill stops being useful" — it's "the *complexity of production* has outgrown the skill's assumed scope." `form-check/scale-up/operational_maturity.md` covers what's beyond.

## Provenance

This skill exists because the SDLC-gap analysis (`form-check/CHANGELOG.md` 2.1.x) identified ops + incident response as **the highest-leverage gap** for the beginner persona. The failure mode (shipping something → it breaks → panicked destructive action → makes it worse) is concrete, recurring, and well-documented (Replit/Lemkin, Power Pages exposure, countless smaller cases).

The §3 incident protocol borrows from Google SRE Book chapter 14 (Managing Incidents), the PagerDuty incident-response training, and the Etsy / John Allspaw blameless post-mortem tradition. Adapted for a beginner solo context: simpler triage, fewer roles, stronger emphasis on "don't make it worse."
