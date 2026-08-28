---
type: checklist
purpose: cross-cutting codebase comprehension protocol
composes_into:
  - form-check (code-review, refactor-prep, deprecate engagements)
  - recovery (discovery phase)
  - diet (incident triage §3)
  - gymbuddy (verification that AI-suggested changes fit the codebase)
  - pr (rollback blast-radius assessment)
---

# Codebase scan, comprehension protocol for unfamiliar code

Use this checklist whenever you must understand an unfamiliar codebase (or unfamiliar area of a familiar codebase) before acting on it. It is the underlying capability behind: PR review of code you didn't write, refactor-prep, incident triage, AI-suggestion verification, and merge vetting.

**Timebox.** 30 minutes for a small project (one service, ≤50 files). 2 hours for a medium project (≤500 files). 1 day for a large unfamiliar codebase. If you exceed the timebox, *stop and re-scope*, you're either trying to learn too much at once or the codebase has fundamental comprehension blockers (missing docs, dense indirection) that need separate work.

## §1, The orientation pass (always run first)

Before reading any code:

- [ ] **`README.md`**, what does the project claim to be? What does it claim *not* to be?
- [ ] **`package.json` / `pyproject.toml` / equivalent**, what's the runtime, what are the dependencies, what scripts exist?
- [ ] **Directory tree at depth 2**, `tree -L 2` or equivalent. Where does code live? Where do tests live? Where does config live?
- [ ] **`CHANGELOG.md` / recent git log**, what's changed in the last 30 days? Last 90 days? Is the project active?
- [ ] **`CONTRIBUTING.md` / `AGENTS.md` / `CLAUDE.md`** if present, what are the conventions you're expected to follow?

Write **three sentences** at the end of this pass:
1. What is this project's *purpose*?
2. What is its *shape* (monorepo? single service? library? CLI?)?
3. What's the *one thing* I'd need to understand more before touching it?

If you can't write those three sentences, do the orientation pass again, you read but didn't comprehend.

## §2, The entry-point scan (find where execution starts)

Every codebase has at least one entry point. Find them:

- [ ] **CLI / executable**, look in `bin/`, `scripts/`, `package.json` `bin:` field, the file referenced in `Procfile` or `Dockerfile CMD`.
- [ ] **Web service**, look for `app.py` / `index.js` / `main.go` / `server.ts` at the project root or one level in.
- [ ] **Library**, look at the `main:` / `exports:` field of `package.json`, or the `__init__.py` of the top-level package.
- [ ] **Tests**, `tests/`, `test/`, `__tests__/`, or `*_test.go` files. The tests are often the most readable documentation of the codebase's behavior.

For each entry point: read the first ~50 lines. Trace one execution path two function calls deep. The goal is "I know what happens when this runs," not "I understand the whole code path."

## §3, The data-shape pass

Most code is moving data from somewhere to somewhere else. Identify:

- [ ] **Input boundaries**, where does external data enter? (HTTP endpoints, CLI args, file reads, database queries, message queue consumers.)
- [ ] **Output boundaries**, where does data leave? (HTTP responses, file writes, database writes, message queue produces, external API calls.)
- [ ] **Persistence model**, what's the database schema (look at migration files), what's stored in flat files, what's cached in memory?
- [ ] **Configuration surface**, what env vars are read? (`grep -RE 'process\.env|os\.environ|getenv'`.)

A codebase you can describe by its data shape ("HTTP POSTs come in, get validated, get written to Postgres, an async worker reads them and calls an external API") you can reason about. A codebase you can't describe this way is one you don't understand yet.

## §4, The risk-surface pass

Three quick scans:

- [ ] **Auth / authz code**, `grep -RE 'auth|require_user|@login_required|isAuthenticated|hasPermission'`. Note the patterns; auth is the highest-leverage area for both bugs and security issues.
- [ ] **Destructive operations**, `grep -RE 'delete|DROP|TRUNCATE|rm -rf|os\.remove|shutil\.rmtree'`. Know where these are before any incident.
- [ ] **External calls**, `grep -RE 'fetch|axios|requests\.|http\.|urlopen'`. Each external call is a failure mode you can't unit-test.
- [ ] **Secrets / credentials**, `grep -RE 'gh[op]?_<token>|sk-<token>|AKIA<id>|BEGIN ... PRIVATE KEY|Bearer |api[_-]?key|password|token'`. Any literal credential is a leak waiting to happen; flag and rotate, never commit.
- [ ] **Outbound egress**, `grep -RE 'https?://|ftps?://'` and review each host. Unpinned/unexpected destinations are exfil or supply-chain risk; an egress allowlist beats an allowlist-of-none.
- [ ] **Sensitive / dotfiles**, `find . -name '.env*' -o -name 'id_*' -o -name '*secret*'`. These must never ride along into a published bundle or a prompt context.

For each found pattern: note the file, line, and a one-phrase description. This becomes your reference map for *any future intervention* in this codebase.

> **Standing skill-tree audit.** The skill tree itself is a codebase. `form-check/tools/scan_skill_tree.py` automates the four scans above (plus SWE/QA/DevOps postures) as a zero-dependency, waiver-aware, fail-closed scanner; `tools/gate_skill_tree.sh` turns its output into a distribute/refuse decision. Run `tests/run_all.sh` after any change to skill tooling. See `docs/skill-tree-audit.md`.

## §5, The test-coverage scan

Tests are the spec the codebase is committed to. Scan:

- [ ] **How many tests exist?** (`find . -name '*test*' -type f | wc -l`)
- [ ] **What's tested?** Skim test names, they reveal the spec.
- [ ] **What's *not* tested?** Critical paths without tests are the parts of the codebase where AI assistants and confident-juniors do the most damage.
- [ ] **Test execution.** Can you run `npm test` / `pytest` / equivalent right now? If not, that's the highest-priority unblocker for any further work.

If tests are sparse or absent, treat the codebase as *higher-risk* than its complexity alone would suggest. The lack of tests is a maintainability red flag.

## §6, The "what would I break?" pre-mortem

Before touching anything:

- [ ] **What's the smallest change I'm trying to make?** Name it in one sentence.
- [ ] **What three other parts of the codebase could my change break?** (If you can't name three, you haven't scanned enough.)
- [ ] **What's the rollback path if my change makes things worse?**
- [ ] **Is there any code in the risk-surface (§4) that my change touches directly?**

This is the bridge from "I understand this codebase" to "I can act on it safely." Per `rubrics/confidence_score.md` Component 1 (code-read depth) and Component 9 (blast radius).

## §7, Output: the scan note

At the end of the scan, write a `codebase_scan_notes.md` (one page, in your project's notes folder, not committed to the codebase you're scanning unless you're a contributor):

```markdown
# Codebase scan, [project name], [date]

## What it is
[3 sentences from §1]

## Shape
- Entry points: [list]
- Inputs: [list]
- Outputs: [list]
- Persistence: [one line]

## Risk surface
| File:line | Pattern | Note |
|---|---|---|
| ... | auth | ... |
| ... | delete | ... |

## Test posture
[# of tests; what's covered; what's not; can I run them?]

## My intended change
[1 sentence]

## Three things my change could break
1. ...
2. ...
3. ...

## Rollback path
[concrete: git revert? feature flag? platform rollback?]
```

This artifact is the *handoff* to whichever skill invoked you:
- → `form-check/code-review` walks the rubric with this context loaded
- → `recovery/discovery` uses this as the first phase deliverable
- → `diet §3` uses this to locate the failure during incident triage
- → `gymbuddy §2.2` uses this to check whether AI-suggested changes fit
- → `pr §5` uses this for blast-radius assessment

## §8, Anti-patterns

- ❌ **Reading top-to-bottom.** Codebases aren't books. Start from entry points and follow execution; don't read in alphabetical order.
- ❌ **Skipping the tests directory.** Tests are the highest-information-density part of most codebases.
- ❌ **Asking the AI to summarize the codebase as the *first* step.** Do your own orientation pass first. AI summaries of unfamiliar codebases are confidently approximate, read them after you have ground truth, not as ground truth.
- ❌ **Acting before completing §6.** You might be right; you'll also occasionally be the Replit/Lemkin cautionary tale.
- ❌ **Treating this checklist as one-time-only.** Re-scan when the codebase has had ≥30 days of changes since your last scan, or before any high-blast-radius intervention.

## Composition notes for skill authors

If you're building a skill that needs codebase comprehension, *don't duplicate this content*. Reference it:

> See `checklists/codebase_scan.md` (in `form-check`) for the codebase-comprehension protocol. [Skill name]'s [phase name] invokes this checklist with the timebox set to [N] minutes/hours.

The skill being referenced can then constrain *which sections* are mandatory for its purposes. Example: `diet §3` requires §1 + §4 + §6 (orientation, risk surface, pre-mortem) and treats the rest as optional in incident mode.

## Provenance

This checklist exists because codebase comprehension is the lowest-rung capability that *every* downstream skill assumes you have. Promoting it to a cross-cutting checklist (rather than a standalone skill) avoids the composition-graph collapse documented in the May 2026 SDLC-gap analysis (`CHANGELOG.md` 2.1.x). Inspired by the Boris-Cherny "fast-context" sub-agent pattern, the "Reading Other People's Code" tradition (Petricek 2014; Vihavainen 2014), and the SRE-incident-triage habit of "find the change before fixing the symptom."
