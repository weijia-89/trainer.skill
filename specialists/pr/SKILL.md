---
name: pr
description: |
  Use when deploying code to production for the first time, doing a routine re-deploy, rolling back a bad deploy, or troubleshooting a deploy that won't build/start/serve. Symptoms: "how do I deploy this," secrets/env-var handling at deploy time, missing rollback path, post-deploy verification, deploy-pipeline failures.
type: project-skill
version: 2.0.0
authors: Wei Jia (1.0, 2026-05-15); v2 Iron Law layering + composes-pin updates 2026-05-16
license: MIT
required_tools: [file_read, shell]
recommended_tools: [git, web_search]
optional_tools: []
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: composes reversibility / blast-radius rubric components for deploy decisions
  - skill: diet
    version: ">=2.0.0,<3.0.0"
    role: hands off to diet after a successful deploy (steady-state) or during an incident (rollback)
  - skill: safetybar
    version: ">=1.1.0,<2.0.0"
    role: routed-to when a deploy needs a code-level rollback (revert vs reset)
  - skill: cruft
    version: ">=1.0.0,<2.0.0"
    role: post-merge deterministic cleanup of session scratchpads (`.cruft.md`), gated on review completion
---

# PR, max-effort day; passes-tests → in-production

```
IRON LAW: NO DEPLOY WITHOUT A ROLLBACK COMMAND YOU CAN STATE IN ONE LINE.
```

Violating the letter of this rule is violating the spirit of this rule. "I'll figure out the rollback if I need it" is the rationalization that turns a 5-minute incident into a 5-hour outage. Before pressing deploy: write the rollback command in the PR description. If you can't, you are not ready.

## Red Flags, STOP before deploying

- "I'll write the rollback note after the deploy."
- "Rollback is just `git revert HEAD`, no need to document."
- "It's a small change, doesn't need rollback planning."
- "I'll deploy first and watch the logs after."
- "I'm bundling these unrelated changes to save a deploy."
- "The platform's rollback button is good enough, no need for code rollback."
- "Friday afternoon is fine for this one."
- "I'll skip the smoke test, the platform said it deployed."

Each red flag means: stop. Walk §1 pre-deploy checklist. Then §3.

## Rationalizations, what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "I know how to roll this back" | Then write it down. If you can't write it down, you don't know it under stress. |
| "Bundling changes saves CI minutes" | And triples your incident-investigation time when something breaks. Deploy one logical change. |
| "Platform rollback handles everything" | It does not handle DB migrations, third-party side effects, sent emails. Plan for the worst case. |
| "Smoke test from outside is overkill" | The platform's health check checks `/health`. Smoke test checks the *user path*. Different things. |
| "I'll deploy now and roll forward later if needed" | "Roll forward" mid-incident is `safetybar §6` territory. The deploy without rollback path *is* the bad scenario. |

## Keywords for discovery

For trigger-keyword indexing: how do I deploy, deploy this, ship to prod, deploy to vercel, deploy to netlify, deploy to render, deploy to fly, deploy to railway, deploy to heroku, deploy a static site, deploy a node app, deploy a python service, github actions deploy, env vars for production, where do I put my secrets, deployment pipeline, CI/CD, rollback deployment, undo deploy, the deploy made it worse, blue-green, staged rollout.

## Scope

You have working code locally. You need it running somewhere users can reach it. This skill covers the *deploy* phase, the gap between `recovery/launch-ready` and `diet/steady-state`.

**Scope.** First-deploy mechanics, env-var and secrets handling at deploy time, the pre-deploy checklist, rollback procedure, deploy-related incident response.

**Not for.** Build / test (`recovery`). Operate / monitor (`diet`). Architecture decisions about which platform to use (`form-check/plan-new-app` should have set that).

## How to invoke

- **First deploy of a new project**: §1 (pre-deploy checklist) → §2 (platform-specific patterns) → §4 (post-deploy verification).
- **Routine re-deploy** of an existing project: §3 (the deploy itself) only; assume §1 was done at first-deploy.
- **Rollback** (a deploy made things worse): §5.
- **The deploy is failing** (won't build / won't start / health check failing): §6.

## §1, Pre-deploy checklist

Run through this **before** the first deploy. Skipping it is how beginners ship something that "works on my machine" but doesn't work anywhere else.

### 1.1 Environment variables documented

`README.md` (or `.env.example`) lists every env var the app reads, with: name, what it's for, what shape (URL? secret string? boolean? integer?), and which environments need it (local / staging / prod).

If you don't have this list, your deploy will fail on the first missing variable, and you won't know which one.

### 1.2 Secrets are not in the repo

Run a quick scan:

```bash
git log --all -p | grep -E "(api[_-]?key|secret|password|token)\s*[=:]" | head
```

If anything matches a real-looking value, **stop and read `form-check/learner/token_handling_primer.md` §5** before doing anything else. Rotate any exposed credentials *before* deploying, the deploy is a forcing event for rotation.

### 1.3 Dependency lockfile committed

- Node: `package-lock.json` (npm) / `pnpm-lock.yaml` / `yarn.lock`
- Python: `poetry.lock` / `requirements.txt` with pinned versions / `uv.lock`
- Ruby: `Gemfile.lock`
- Rust: `Cargo.lock`

Without a lockfile, your prod deploy will resolve dependency versions independently from your local resolve. This is a primary source of "works on my machine."

### 1.4 Build runs clean from scratch

```bash
rm -rf node_modules .venv build dist  # nuke local caches
npm install / pip install -r requirements.txt / etc.
npm run build / make build / etc.
npm test / pytest
```

If this sequence fails locally, it will fail in CI / on the platform. Fix locally first.

### 1.5 Health check endpoint exists

Your app exposes an HTTP endpoint (typically `/health` or `/_health`) that returns 200 quickly without touching the database or external services. The platform uses it to decide whether the deploy succeeded. Beginners often skip this and then can't tell if a "deployed" service is actually serving traffic.

### 1.6 You have a way to view logs

Whatever platform you deploy to, confirm you can read its logs *before* you depend on them. The middle of an incident is the wrong time to discover you've never configured log access.

## §2, Platform-specific patterns

This skill assumes you've already chosen a platform per `form-check/rubrics/stack_decision.md`. Patterns below are for the most common beginner-friendly choices.

### 2.1 Static site (Vercel, Netlify, GitHub Pages, Cloudflare Pages)

- Connect repo → platform auto-deploys on push to main.
- Env vars set in platform UI (Vercel/Netlify projects > Environment Variables).
- Custom domain: set DNS CNAME / ALIAS to platform's target; platform auto-issues certificate.
- Rollback: platform UI shows previous deploys; one click to promote.

### 2.2 Node service (Render, Fly.io, Railway, Vercel functions)

- Same connect-repo flow.
- `Procfile` or `package.json` `"start"` script declares how to run.
- Env vars in platform UI.
- Health check endpoint: typically `/health` returning `200 OK`.
- Rollback: platform UI.

### 2.3 Python service (Render, Fly.io, Railway, Heroku)

- `Procfile` declares `web: gunicorn app:app` or `uvicorn app:app --host 0.0.0.0 --port $PORT`.
- `requirements.txt` or `pyproject.toml` + lock file.
- Same health check / env var / rollback patterns.

### 2.4 Containerized (Fly.io, AWS ECS, GCP Cloud Run)

- `Dockerfile` in repo; platform builds the image.
- Multi-stage build to keep image small: build stage with full toolchain, runtime stage with just artifacts.
- Health check declared in Dockerfile or platform config.
- Env vars (and secrets) injected at runtime via platform's secret store.

### 2.5 What to skip at the beginner stage

- **Kubernetes** unless your `form-check/scale-up/` annex says you actually need it (very rarely true for the persona).
- **Custom CI/CD** when the platform's built-in deploy-from-git suffices.
- **Multi-region active-active** until single-region is provably insufficient.
- **Service meshes, sidecars, ingress controllers**, these are scale-up tools; using them at the persona's scale is `form-check/forcing-constraint-ADR-required` territory.

## §3, The deploy itself

Default deploy flow for any platform:

1. **Push to main** (or merge a PR into main).
2. **Platform auto-builds and deploys.** Watch the build log.
3. **Health check passes.** Platform's "this deploy is live" indicator turns green.
4. **Smoke test from outside.** `curl https://yourdomain.com/health` and one real user-facing endpoint. From a different network than your dev machine.
5. **Glance at error tracking / logs** (per `diet` §1) for the next ~5 minutes. New error groups in error tracking? Spike in 5xx? Roll back; investigate.

If your deploys take more than ~10 minutes, that's a separate problem, it slows your incident response and pushes you toward `--force` shortcuts. Address it.

## §4, Post-deploy verification

Within the first 30 minutes of any production deploy:

- [ ] Health check responding (you saw the green checkmark).
- [ ] Smoke test from outside passed (you `curl`ed a real endpoint).
- [ ] No new error groups in error tracking.
- [ ] Latency / traffic / errors on the four golden signals dashboard look normal.
- [ ] If the deploy changed a database schema: spot-check that the migration ran and the data is intact.
- [ ] If the deploy changed an env-handling code path: spot-check that the env var is being read correctly (often: log a sanity line that shows config got loaded, but **never log the secret values themselves**).

## §5, Rollback procedure

Two kinds of rollback:

### 5.1 Platform rollback (preferred when available)

Vercel, Netlify, Render, Railway, Fly, Heroku, and most cloud platforms keep the last N deploys and let you promote a previous one to "current" with one click. This is the rollback path you want, it does not change the code, it changes which build is serving traffic.

Use the platform UI: "Deploys" → select previous successful deploy → "Promote" / "Redeploy."

### 5.2 Code-level rollback (when platform rollback isn't enough)

If the bad deploy made changes that the platform rollback won't reverse (a database migration ran, an external system was called with new behavior), you need a *code* rollback:

```bash
git revert <bad-commit-sha>           # creates a NEW commit undoing the bad one
git push origin main                  # triggers a fresh deploy
```

**Never `git push --force` to roll back production.** Use `git revert`. (See `safetybar` §2.2 for why.)

### 5.3 Rollback decision triggers

Per `diet §3.4`, roll back when:
1. The incident started after a known deploy.
2. Rollback is reversible (you can deploy forward again later).
3. No data shape changed irrevocably.

If any of those fails, *rollback is itself an incident*, escalate to `diet §3` triage.

## §6, When the deploy is failing

Common failure modes and the recovery path for each:

| Symptom | Likely cause | Fix |
|---|---|---|
| Build fails: missing dependency | Lockfile mismatch, or platform's Node/Python version differs from yours | Pin the platform's runtime version explicitly (`.nvmrc`, `runtime.txt`, `engines` in `package.json`) |
| Build succeeds but app won't start | Missing env var | Check platform's env var config; cross-reference against your `.env.example` |
| App starts but health check fails | Health endpoint touches DB / external service before app is ready | Make the health endpoint a pure `200 OK` with no dependencies |
| Build succeeds, health check passes, but real endpoints 500 | Production env differs from dev (file paths, DB connection, secrets) | Tail the error tracking; the first 500 will tell you |
| Build is fine, deploy is fine, but the change isn't taking effect | Browser cache, CDN cache, platform cache | Hard-refresh (cmd-shift-R); platform "purge cache" if available |
| Deploy succeeds intermittently and fails intermittently | Flaky build infrastructure, race condition in build step | Re-run; if persistent, investigate platform status page; consider pinning more aggressively |

## §7, Anti-patterns

- ❌ **Deploying on Friday afternoon.** Beginner version of this rule: don't deploy when you can't roll back in the next hour. (Day-of-week is the heuristic; the underlying rule is rollback-window-availability.)
- ❌ **Bundling unrelated changes in one deploy.** "I'll just include this small fix too." Now if anything breaks, you don't know which change caused it. Deploy one logical change at a time.
- ❌ **Skipping the smoke test because "the platform said it was deployed."** The platform's health check only knows your app responds to `/health`. The smoke test is *you* exercising a real user path.
- ❌ **Putting secrets in environment variables in the platform UI and then committing a `.env` file with placeholders.** Either approach is fine alone; mixing them produces "which one is real?" confusion. Pick one source of truth.
- ❌ **Deploying without knowing the rollback path.** Before pressing the deploy button, you should be able to answer: "If this breaks, what command / button do I use to undo it?" If you can't answer, don't deploy yet.

## §8, Post-merge cruft cleanup (the close-out gate)

After a PR merges to `main` and the code-review verification has passed:

1. **Verify the review gate is GREEN** — `scripts/verify_trainer_codereview.sh` exits 0 (or a human has signed off). If RED, do not proceed; cruft is evidence until the finding is resolved.
2. **Write the sentinel:** `mkdir -p .trainer && touch .trainer/reviews-complete` (this is the deterministic signal `cruft`'s `prune_cruft.sh` trusts).
3. **Run the cleanup:** `bash "<trainer.skill root>/scripts/prune_cruft.sh" --root "$(git rev-parse --show-toplevel)" --apply` (TRAINER_ROOT resolves to the trainer.skill repo root via the script's own location). It deletes only `*.cruft.md` files and only because the gate is GREEN.
4. **Session-close variant:** on opencode "clean cruft" / close-session, run the same `prune_cruft.sh --apply` (the gate still applies). This is the superset of the request-cap contract's R4c webfetch-cache cleanup for `.cruft.md` session scratchpads.

The point: cleanup is **deterministic and gated**, never a hand-wave. See `cruft` specialist for the slug + header convention.

## §9, Writing the PR

Every PR gets two artifacts: a **description** (the body) and a **code review comment** (the findings). Both follow fixed templates. Both get a Simple English and deAI pass before posting.

```
IRON LAW: NO PR POSTED WITHOUT TEST EVIDENCE YOU CAN POINT TO.
```

### 9.1 PR description template

Every PR body follows this structure. Sections are mandatory unless noted.

```markdown
## Summary

<One paragraph. BLUF: what this PR does and why. No jargon. A non-engineer should understand the intent.>

## Changes

- **<file_or_module>**: What changed and why. One bullet per logical change.
- **<file_or_module>**: What changed and why.

## Test plan

The agent ran these tests and confirms all pass:

- [x] `command` — what it checks, what the result was
- [x] `command` — what it checks, what the result was

**Coverage notes:** <What the tests cover. What they do not cover. Why the gaps are acceptable or what the remaining risks are.>

## Notes

- <Known limitations, false positives, or deferred work.>
- <Hardware-gated or environment-gated items that remain untested.>
```

#### Test plan rules

1. Check only the boxes for tests you actually ran. Do not check boxes for tests you plan to run.
2. Each test line must include: the command, what it validates, and the result.
3. The **Coverage notes** subsection is mandatory. State what the tests cover, what they do not cover, and your judgment on remaining risk. Do not just say "tests cover everything."
4. Run as many tests as you can before writing the plan. Unit tests, linting, type checking, shellcheck, JSON validation, syntax checks — run them all.
5. If a test fails, fix it before writing the plan. Do not document failing tests in the plan.

#### Summary rules

1. One paragraph, 3 to 5 sentences.
2. Start with the verb: "Fixes...", "Adds...", "Refactors...", "Hardens...".
3. Name the affected area: scripts, tests, schemas, CI, docs.
4. State the outcome: what works now that did not before.
5. No acronyms without expansion on first use. No internal skill names.

#### Changes rules

1. One bullet per file or logical unit.
2. Format: `**path/to/file**: What changed and why.`
3. Group related changes in one bullet. Do not split a single fix across multiple bullets.
4. Include line numbers only when the change is non-obvious from the file name.
5. Maximum 10 bullets. If you have more, group related changes.

### 9.2 Code review comment template

Every code review comment follows this structure.

```markdown
## Code Review

<One line: how many checks, what they targeted.>

| # | Severity | Finding | Fix |
|---|----------|---------|-----|
| 1 | P1 CRITICAL | What is wrong | What was done to fix it |
| 2 | P2 MAJOR | What is wrong | What was done to fix it |
| 3 | P3 MINOR | What is wrong | What was done to fix it |
| 4 | P4 NIT | What is wrong | Why no change was needed |

**Result:** <Count of findings by severity.>

### Edge case verification

- <What was tested and the result.>
```

#### Table rules

1. Columns are mandatory: `#`, `Severity`, `Finding`, `Fix`. No other columns.
2. Severity uses P1 CRITICAL, P2 MAJOR, P3 MINOR, P4 NIT.
3. The Fix column states what was done. For accepted NITs, state why no change was needed.
4. Sort by severity (P1 first, P4 last).
5. Maximum 10 rows. If you have more, batch into multiple comments.

#### Severity definitions

| Level | Meaning | Action required |
|-------|---------|----------------|
| P1 CRITICAL | Security hole, data loss, silent corruption | Must fix before merge |
| P2 MAJOR | Correctness bug, broken test, schema violation | Must fix before merge |
| P3 MINOR | Missing validation, incomplete coverage, stale config | Fix or document why deferred |
| P4 NIT | Style, naming, cosmetic, accepted risk | Document and move on |

### 9.3 Writing quality gates

Every PR description and code review comment passes these gates before posting.

**Simple English (ASD-STE100 pragmatic mode):**

1. No sentence over 25 words (descriptive) or 20 words (procedural).
2. One topic per paragraph. Maximum 6 sentences per paragraph.
3. Active voice. Passive only when the agent is unknown.
4. No contractions.
5. Conditions before commands: "If X, do Y." not "Do Y if X."
6. Pick one verb for each concept and stick with it (check not verify/confirm/validate).
7. No filler: "it is worth noting", "importantly", "simply", "just", "easily".

**deAI pass (run deai skill before posting):**

1. Voice prime: match the register of technical documentation, not marketing or academic.
2. Scan for RLHF residue: em-dashes, tricolons, "not X but Y", synonym rotation, abstract hedging.
3. Fix hierarchy: restructure > swap > cut. A swap that still reads AI is a failed fix.
4. Read-aloud test: if a sentence drags or stumbles, revise the rhythm.

**Factual accuracy:**

1. Every claim in the test plan must match actual command output.
2. Every file path referenced must exist.
3. Every line number must be accurate within 5 lines.
4. No fabricated test results. If you did not run a test, do not check the box.

### 9.4 Agent reminders

When writing a PR at any time:

1. **You are the tester.** Run the tests yourself before writing the plan. Do not write "should pass" or "tests cover this." Run them and record the actual output.
2. **You are the reviewer.** Run the code review yourself. Do not write "needs review." Review it, record findings, apply fixes.
3. **You are the writer.** Write the PR body yourself. Do not write "TODO" or "WIP." Complete the template.
4. **Coverage notes are mandatory.** Every test plan must state what the tests do not cover and your judgment on remaining risk.
5. **No internal names.** Do not reference skill names, prompt numbers, or internal tooling in PR prose.
6. **No Gate Evidence table.** The test plan already contains the evidence. A separate Gate Evidence table is redundant.
7. **Fix column is mandatory.** Every review finding must state what was done to fix it or why no change was needed. "Accepted" alone is not enough.

### 9.5 Test harness

Validate PR artifacts before posting:

```bash
bash <trainer.skill root>/specialists/pr/test-pr-format.sh <pr-body-file> [review-comment-file]
```

Checks: section structure, checkbox presence, coverage notes, banned words, internal names, table format, severity values, fix column completeness.

Exit codes: 0 = all pass, 1 = mandatory failures, 2 = usage error (missing arguments or file not found).

The harness runs as a pre-post gate. Wire it into CI or run manually before posting any PR description or code review comment.

## Composition with other skills

- **Before PR:** `form-check` reviews the change; `recovery` runs the engagement.
- **Writing PR prose:** §9 of this skill. `deai` for voice quality, `simple-english` for clarity.
- **At deploy time:** §1–§8 of this skill.
- **After deploy, steady state:** `diet §1–2` for instrumentation and cadence.
- **After deploy, incident:** `diet §3` for triage; §5 of this skill for rollback; `safetybar §2.2` for git-level recovery if needed.
- **If a deploy exposed secrets:** `form-check/learner/token_handling_primer.md §5` for the leak-response runbook.

## Provenance

The deployment gap was the *medium-priority* finding in the SDLC-gap analysis (see `form-check/CHANGELOG.md` 2.1.x). It's not the highest-leverage gap because beginners often get a "good enough" deploy path from their platform's tutorial. But once something is broken at deploy time, the platform tutorial doesn't help, that's where this skill picks up.

The pre-deploy checklist (§1) and post-deploy verification (§4) are the load-bearing sections. The rest is reference. The platform sections (§2) intentionally err toward "boring, beginner-friendly" choices, see `form-check/rubrics/stack_decision.md` for the underlying posture.
