---
name: program
description: |
  Use when a project idea is vague, unscoped, or scope-creeping; or when starting a new project without a one-page spec. Symptoms: "I want to build X," topic without project shape, no kill criteria, multi-page spec without acceptance criteria, can't name the first user.
type: project-skill
version: 2.0.0
authors: Wei Jia (1.0, 2026-05-15); v2 Iron Law layering 2026-05-16
license: LicenseRef-IronLaw-NC-1.0
required_tools: [file_read]
recommended_tools: [shell, web_search]
optional_tools: []
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: handoff target after spec is scoped (form-check handles plan-new-app)
---

# program — vague idea → scoped spec; the plan before the work

```
IRON LAW: NO IMPLEMENTATION SKILL INVOKED UNTIL THE ONE-PAGE SPEC HAS KILL CRITERIA AND THREE NON-GOALS.
```

Violating the letter of this rule is violating the spirit of this rule. "I'll add the kill criteria after I start building" is the rationalization that produces 100-hour projects that should have been killed at hour 10. The kill criteria + non-goals are not optional decorations; they are the calibration that makes the build phase finite.

## Red Flags — STOP and finish the spec

- "I have the idea, I'll figure out kill criteria as I go."
- "Non-goals are too restrictive, I want to keep options open."
- "The first user is 'everyone who likes X.'"
- "I'll write a multi-page design doc, that's the spec."
- "Phase 2 will be where the cool stuff lives."
- "I don't need a kill criterion, I'm committed."

Each red flag means: stop. Re-walk the four-question intake. Spec on one page. Then hand off to `form-check/plan-new-app`.

## Rationalizations — what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "Kill criteria sound pessimistic" | Kill criteria are *calibration training* — predict what done looks like, then measure. Without them, you can't tell if you're making progress. |
| "Non-goals limit creativity" | They focus it. "Phase 2" features are usually never re-justified — meaning they were never needed. |
| "I'll know the first user when I build the MVP" | Reverse it: name the user *first*, then build for them. Aspirational users produce unbuildable specs. |
| "My one sentence is a paragraph" | If you can't compress to one sentence, you don't have a project — you have a topic. Topics aren't scopable. |

## Keywords for discovery

For trigger-keyword indexing: I want to build, I have an idea, scope this project, MVP definition, what should I build first, where do I start, project ideation, vague spec, fuzzy requirements, I'm not sure what I'm building, help me think this through, what's the smallest version, kill criteria, what to NOT build, scope creep, feature creep, am I building the right thing.

## Scope

You have an idea. It is too big, too vague, or too vague-and-too-big. This skill triages it into something you can actually start building this week.

**Scope.** This skill ends where `form-check/plan-new-app` begins. program produces the spec; form-check validates it against the rubric, picks the stack, and writes the ADRs. They are sequential: program → form-check.

**Not for.** Single-PR scoping (that's `form-check` directly). Already-scoped specs (skip to `form-check`). Pure brainstorming with no commitment (use a notes app).

## When to invoke

- "I want to build a thing that tracks my reading."
- "I have a side project but I keep adding features and never shipping."
- "Should I rebuild this in Rust?" (No — `program` says no, then sends you to `form-check/refactor-prep` if a real refactor case exists.)
- "I'm three months in and not sure what I'm building anymore."
- Your idea has more than **5 sentences** of description but no acceptance criteria.

## The four-question intake

### 1. What is the *one* sentence?

Write the project in one sentence, in this shape: **"A [thing] that helps [who] do [action] without [pain point]."**

If you can't write the one sentence, you don't have a project yet — you have a topic. Topics aren't scopable. Examples:

- ❌ "Something with AI and books" — topic.
- ✅ "A CLI that summarizes my Kindle highlights into a weekly digest without me having to copy/paste." — project.

If you produced the one-sentence version, continue. If you produced a topic, the answer to "what should I build?" is "more thinking; don't open an editor yet."

### 2. Who is the *first* user?

Not "everyone." Not "people who like books." A specific person — ideally you, ideally identified by a behavior you've already exhibited within the last 30 days.

Examples:

- ❌ "Anyone who reads on Kindle." (Aspirational user; you don't know what they want.)
- ✅ "Me, last Sunday, when I spent 40 minutes manually copying highlights into a Notion page and gave up halfway." (Specific, recent, observable.)

If you can't name the first user, your kill-criteria will be wrong. Stop and identify them.

### 3. What is the kill criterion?

Most beginner projects die slowly because nothing tells the builder "this isn't working — stop." A *kill criterion* is the observable signal that says: ship something else, or shelve this entirely.

Examples:

- "If I've spent 10 hours and don't have a working v0 of the digest, I kill it."
- "If after 5 weekly digests I haven't opened the resulting page, I kill it."
- "If I cannot get a free Kindle highlights export within 2 hours of research, I kill it." (Real one — Amazon makes this hard; the project may not be feasible without paid tooling.)

Write at least two kill criteria. If you can't write any, you're probably not committed to actually shipping — you want a *hobby*, which is fine but doesn't need this skill.

### 4. What are the three deliberate non-goals?

Things you will **not** build, even if tempting. The non-goals are more important than the goals for beginners — without them, scope creep kills the project before it ships once.

Examples (for the Kindle-digest project):

- ❌ "Multi-user support" — not until I'm the user successfully.
- ❌ "Web UI" — the CLI digest works for the persona (me).
- ❌ "Authentication / accounts" — single user, local-only.

A useful heuristic: **for every "yes" feature, name two "no" features.** Beginners are systematically biased toward yes.

## The output: a one-page spec

After answering the four questions, write a one-page spec with exactly these sections:

```markdown
# [Project name]

**One sentence.** ...

**First user.** ...

**MVP (v0).** [The smallest thing that delivers value to the first user.]

**Acceptance criteria for MVP.**
- [ ] ...
- [ ] ...
- [ ] ...

**Kill criteria.**
1. ...
2. ...

**Deliberate non-goals (v0).**
- ...
- ...
- ...

**First three concrete tasks.** (Not "build the parser" — "spend 30 min researching kindle-export libraries, take notes in `research.md`.")
1. ...
2. ...
3. ...

**Timebox to v0.** [a week / a weekend / 10 work-hours]. If you blow the timebox, that's a kill-criterion trigger.
```

This spec is the **handoff** to `form-check/plan-new-app`. Take the spec, invoke form-check, and let it route to `templates/CLAUDE.md_scaffold.md`, `rubrics/stack_decision.md`, and `checklists/preflight_10q.md` to validate the spec against the rubric.

## Anti-patterns

**The spec-as-novel.** Multi-page specs are a sign the writer hasn't decided. Force yourself to one page.

**The "phase 2" trap.** Any feature labeled "phase 2" in the v0 spec actually goes in the deliberate-non-goals list, with the understanding that it will be **explicitly re-justified** before being built. Most "phase 2" features are never re-justified, which means they were never needed.

**The hypothetical-user.** Describing what "users would want" without a real first user produces unbuildable specs. Either name a real user (often yourself, recently) or stop.

**Greenfield-vs-rebuild confusion.** If the urge is "rewrite this thing I have in a different language/framework," the answer is almost always "no" — invoke `form-check/refactor-prep` instead. program is for genuinely new projects.

**Skipping kill criteria.** This is the most common failure. Without kill criteria, you'll spend 100 hours instead of 10 on a project that wasn't going to work. The kill criteria are not pessimism; they're calibration.

## How program pairs with the rest of the ecosystem

| Phase | Skill |
|---|---|
| Vague idea | **program** ← you are here |
| Scoped spec → validated plan + stack + ADRs | `form-check/plan-new-app` |
| Build (the agent + you write code) | (outside the skill ecosystem) |
| Single change → review | `form-check` |
| Whole-project quality pass | `recovery` |
| Deploy | `pr` |
| Operate + incident response | `diet` |
| When the AI assistant is your collaborator | `gymbuddy` |

## Provenance

This skill exists because the May 2026 SDLC-gap analysis (see `form-check/CHANGELOG.md` 2.1.x notes) identified pre-build ideation as the gap that costs beginners the most time. Symptom: builders spend weeks on the wrong project because they never wrote down what "right" was. Forcing-function: this skill produces a one-page artifact a beginner cannot avoid producing.

The cognitive-science basis is `form-check/learner/study_protocol.md` Habit 7 (calibration): the kill-criteria + timebox + acceptance-criteria triple is calibration training for project scope — predict what done looks like, then measure against it.
