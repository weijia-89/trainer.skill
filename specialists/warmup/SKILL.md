---
name: warmup
description: |
  Use as front-desk routing when uncertain which gym skill applies, when a learner is new to the ecosystem, or when a request spans multiple skill scopes. Symptoms: "where do I start," "is this safe to ship," ambiguous task spanning ideate/build/review/deploy/operate/recover, learner with <10 invocations of any specific skill.
type: project-skill
version: 2.0.0
authors: Wei Jia (1.0, 2026-05-15; 1.1 expanded routing for 5 new skills, 2026-05-15; v2 Iron Law layering + composes-pin updates 2026-05-16)
license: MIT
required_tools: [file_read]
recommended_tools: []
optional_tools: []
composes:
  - skill: program
    version: ">=2.0.0,<3.0.0"
    role: routed-to for vague-idea-to-scoped-spec (pre-build)
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: routed-to for single-change review / planning
  - skill: recovery
    version: ">=3.0.0,<4.0.0"
    role: routed-to for full-project quality engagement
  - skill: pr
    version: ">=2.0.0,<3.0.0"
    role: routed-to for the deploy-mechanics phase
  - skill: diet
    version: ">=2.0.0,<3.0.0"
    role: routed-to for steady-state ops AND incident response
  - skill: safetybar
    version: ">=1.1.0,<2.0.0"
    role: routed-to for "I broke git" recovery
  - skill: gymbuddy
    version: ">=2.0.0,<3.0.0"
    role: routed-to for AI-assisted-development workflow patterns
---

# warmup, front desk; tell me what's broken and I'll route you

```
IRON LAW: NO DIRECT ACTION FROM WARMUP, ROUTE FIRST, THEN ACT IN THE DOWNSTREAM SKILL.
```

Violating the letter of this rule is violating the spirit of this rule. "I'll just answer this here" is the rationalization that turns a triage skill into a generalist, generalists give worse advice than specialists. This skill routes; it does not score, plan, fix, deploy, recover, or coach.

## Red Flags, STOP and route

- "This is a quick one, no need to route."
- "I'll route AND give a partial answer."
- "The downstream skill is overkill for this."
- "Routing wastes a turn."
- "I know which skill applies, but I'll handle it myself."

Each red flag means: stop. Pick the row in the routing table. Hand off.

## Rationalizations

| Excuse | Reality |
|---|---|
| "Quick answers don't need routing" | Quick answers degrade to generalist quality. The downstream skill exists because routing produces the calibrated answer. |
| "I'll route AND answer" | Choose one. Both = pollution of the routing skill with content. |
| "Routing is friction" | Friction toward the right skill is not friction toward the goal. |

## Keywords for discovery

For trigger-keyword indexing: is my code okay, should I ship this, what should I check before shipping, how do I review my own code, is this PR safe, my project feels broken, audit my repo, prepare to launch, am I doing this right, I'm new to coding, just started learning to code, scared to push to main, AI wrote this should I trust it, where do I start, I have an idea, prod is broken, I broke git, help me think this through.

## Scope

You walked into a community health clinic. The volunteer at the front desk doesn't treat you, they triage and route you to the right specialist. This skill is that front desk.

It does not score code, plan architecture, run engagements, deploy, operate, recover git, or coach AI workflow. **Its only job is to route you to the right downstream skill.**

If you already know which skill you need, skip this one, invoke the downstream skill directly. If you don't know, or you're learning the ecosystem, start here.

## The intake, pick the row that matches what you're doing

| Your situation | Skill to use |
|---|---|
| I have a vague idea; I don't even have a spec yet | **`program`** (then it hands off to `form-check/plan-new-app`) |
| I have a scoped spec and need the architecture / stack decision | **`form-check`** → `plan-new-app` engagement |
| I'm about to make, review, or scope a single change | **`form-check`** → `code-review` / `refactor-prep` / `harden` / `deprecate` |
| I want a multi-day quality pass on a whole project | **`recovery`** (engagement; composes `form-check`) |
| I'm ready to ship and need the deploy mechanics | **`pr`** |
| My app is running and I want to know it's healthy / it's broken now | **`diet`** (steady-state §1–2 or incident §3) |
| I think I broke git / lost work / scared of `--force` | **`safetybar`** |
| I'm working with an AI assistant and want to use it well | **`gymbuddy`** |
| I need to understand an unfamiliar codebase before acting on it | (not a skill, use `form-check/checklists/codebase_scan.md` as part of whatever skill you're in) |

**If your situation spans two rows** (most do, you're often planning + reviewing, or deploying + operating), invoke the *earlier* row first. The earlier skill hands off to the later one when its work is done.

**If you're not sure**, default to **`form-check`** with the smallest piece of work you're worried about. You can always escalate. *Smaller-scope-first* is the right move for learners: it builds the habit of applying the rubric to something specific.

**If production is on fire right now**, skip this intake entirely. Go directly to **`diet §3`**. Routing tables are not appropriate during an incident.

## The tier question (when you've picked `form-check` or `recovery`)

Read `form-check/learner/QUICKSTART.md` Part 2 to classify your change as vibe-safe / vibe-careful / vibe-dangerous. That tier determines which **floor** of `form-check` you walk:

- Vibe-safe → **Floor 1** (3 quick checks, ~5 min)
- Vibe-careful → **Floor 2** (Floor 1 + worst-case scenarios + checklist walk, ~30 min)
- Vibe-dangerous → **Floor 3** (Floor 2 + threat model + human reviewer + feature flag + rollback runbook, ≥2 hr)

If you're new to coding, **always start at Floor 1** even for trivial changes. The five-minute cost is the *encoding* (per `form-check/learner/study_protocol.md`, retrieval practice + spaced repetition). Skipping it because "this change is small" is the perception–reality gap that METR-2025 documented in senior engineers.

## The full ecosystem at a glance

```
                  warmup  (you are here if you don't know which to invoke)
                       │
       ┌───────────────┼───────────────┬─────────────┬──────────────┬──────────────┬────────────┐
       ▼               ▼               ▼             ▼              ▼              ▼            ▼
  program   form-check   recovery   pr   diet  safetybar  gymbuddy
   (ideate)      (review/plan)   (engagement)    (deploy)       (operate)       (git)      (AI workflow)
                       ▲                          ▲                ▲                ▲
                       │ composes                 │ composes       │ composes       │ composes
                       └────────── form-check/checklists/codebase_scan.md ──────┘
                                  (cross-cutting comprehension protocol)
```

## When to come back to this skill

You should outgrow `warmup` within 5–10 invocations. The graduation signal is operationalized in `graduation_checklist.md`, a six-item self-assessment with concrete pass criteria for each item. Run it once a month while you are actively using `warmup`.

You have graduated when you can answer all six items correctly on two consecutive monthly reviews. At that point, stop invoking `warmup` and route directly. You do not need to uninstall the skill; it costs nothing to keep loaded, and you may regress on the cross-cutting items (especially the AI-workflow item) and want to re-check.

For agent harness implementers: `graduation_checklist.md` also documents an optional local-only logging contract (`~/.warmup/invocations.jsonl`) for surfacing the checklist automatically after enough usage. The skill works without logging; the logging is a convenience. **No current agent harness implements this contract; treat it as a forward-looking specification.**

## What this skill does NOT do

- It does not score code. (`form-check` does.)
- It does not plan or scope projects. (`program` does.)
- It does not run an engagement. (`recovery` does.)
- It does not deploy code. (`pr` does.)
- It does not handle incidents. (`diet §3` does.)
- It does not recover broken git states. (`safetybar` does.)
- It does not teach AI workflow. (`gymbuddy` does.)
- It does not teach the rubric. (`form-check/learner/` does.)
- It does not classify changes for you. (You read QUICKSTART Part 2 and classify them yourself, that's the encoding step.)

If you find yourself trying to do any of those with this skill, you're using the wrong skill. Go to the one above that handles it.

## For agent harness implementers (forward-looking specification)

**Status: aspirational.** No current agent harness (Cascade, Claude Code, Cursor, etc.) implements selective load/unload semantics, automatic skill pinning by trigger keyword, or post-decision unloading. The skill works today as static reference markdown the agent reads into context. The behavior below is what the skill *would* do under a richer runtime.

If a future harness implements selective loading, the expected behavior is:

1. User triggers `warmup` on any of the keywords in `description`.
2. The harness reads this file (one read; no further state).
3. The harness presents the routing table to the user.
4. On the user's answer, the harness loads the chosen downstream skill and unloads `warmup`.
5. If user picked `form-check` or `recovery`, the harness *also* pins `form-check/learner/QUICKSTART.md` for the tier classification.
6. If user picked `diet` and the trigger keywords contained "fire", "down", "broken", "outage", "incident": skip routing-table presentation and load `diet` directly with §3 pinned. The user does not need a routing table during an incident.

Until that runtime exists, the routing table in §3 is the load-bearing artifact and the rest is decoration. The skill is usable today as a human-readable router.

## Provenance

This skill exists because adversarial-review of `form-check` + `recovery` (May 2026) identified a discoverability gap for beginners: multiple skills cover different scopes but a beginner doesn't know which to invoke. The compromise (rather than merging skills, which would collapse the composition graph) is this thin front-desk skill. See `form-check/CHANGELOG.md` 2.1.x entries for the design discussion that produced this skill.

The v1.1 expansion (May 2026) adds routing for five additional skills built after the original SDLC-gap analysis: `program` (ideation), `pr` (deploy mechanics), `diet` (ops + incident), `safetybar` (git recovery), `gymbuddy` (AI workflow patterns).
