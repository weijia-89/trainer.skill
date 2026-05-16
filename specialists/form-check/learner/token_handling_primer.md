---
name: token_handling_primer
version: 2.0.0
parent_skill: form-check
audience: learner
---

# Token handling — the highest-stakes 15 minutes you will spend

If you are 6–18 months into coding and you ship something that leaks a token, you might:

- Get charged hundreds-to-thousands of dollars by your cloud provider (someone spun up GPUs on your bill)
- Have your Mailchimp / Stripe / GitHub account taken over
- Lose access to your own account while attackers exploit it
- Show up on a public dump of breached credentials
- Make the news (small consolation: you'd join 25,000 other repos from the September 2025 Shai-Hulud incident)

The good news: nearly every token leak is preventable with **eight habits**. Spend 15 minutes setting them up once, and you are protected for the life of the project.

This file is load-bearing. Read it before you write any code that touches an API.

**Tractability note:** Habits 1–4 can be done in one 15-minute setup session and apply to every project you'll ever build. Habits 5–8 are progressive — start them when you start the relevant practice (your first deployment, your first CI workflow, your first real production traffic). Don't let the list intimidate you; the *first four* are the floor.

---

## What is a "token"?

A **token** (also called an **API key**, **secret**, **credential**, **access token**, **personal access token (PAT)**, **service account key**) is a long random-looking string that proves you are allowed to do something. Examples:

- `sk_live_51H...` — Stripe live API key
- `ghp_abc123...` — GitHub personal access token
- `xkeysib-abc...` — Mailchimp API key (newer keys use this prefix)
- `AKIAIOSFODNN7EXAMPLE` — AWS access key ID
- An entire `.env` file's contents — usually a bundle of multiple tokens

**The mental model:** a token is functionally equivalent to your password for that service, except:

1. It usually has narrower permissions (e.g. read-only, or one-project-only) — *if* you scoped it
2. It can be rotated (deleted and replaced) without changing your account
3. **It cannot be "hashed" the way passwords are.** If anyone sees the token in plaintext, they have it. There is no "I'll just change my password" recovery.

This last point is why token leaks are so dangerous. The moment a token appears in a log, in a screenshot, in a git commit, in a Slack message, in an AI chat — assume it's compromised. The only safe response is **rotate immediately**.

---

## The eight habits

### 1. Never paste a token into chat — including AI chats

This includes:

- Slack, Discord, Teams
- ChatGPT, Claude, Gemini, your IDE's AI assistant
- GitHub issues, PR descriptions, code comments
- Email, SMS
- Stack Overflow questions (with edits — "edit history is forever")

**Why AI chats especially:** AI providers log prompts. Some retain transcripts for safety review or model training. If you paste a token into ChatGPT, OpenAI now has a copy. Even if the provider deletes it, it traveled the network, sat in a buffer, was logged on a load balancer. **Treat it as compromised the moment you hit Enter.**

**What to do instead:**

- Mask the token: `sk_live_51H...REDACTED...`
- Or describe the shape: "a Stripe live secret key (starts with `sk_live_`)"
- If the AI needs to debug an auth issue: share the *error message*, not the token

**If you already pasted one:** go to the issuing service, rotate the token (delete it, generate a new one), and update your `.env` file. The old token is dead to you. The five minutes it takes to rotate is cheaper than the alternative.

### 2. `.env` is gitignored; `.env.example` is committed

This is the canonical pattern:

```
# .gitignore
.env
.env.local
.env.*.local
```

```
# .env  (NEVER COMMITTED — has real values)
STRIPE_SECRET_KEY=sk_live_51Hxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILCHIMP_API_KEY=xkeysib-abc123real-value-here
```

```
# .env.example  (COMMITTED — has placeholder values)
STRIPE_SECRET_KEY=sk_live_replace-me-with-your-key
MAILCHIMP_API_KEY=xkeysib-replace-me-with-your-key
```

**Test that `.env` is actually ignored** *before* writing any real value to it:

```bash
git check-ignore .env
# If it prints ".env", you're safe. If it prints nothing, the file is NOT ignored — STOP.
```

**Why both files:** `.env.example` documents what variables your app needs so collaborators (and your future self) know what to put in their `.env`. The placeholders are safe to commit; the real `.env` is local-only.

### 3. Enable secret scanning + push protection on GitHub

In your repo settings: **Settings → Code security → Secret scanning** → enable both:

- **Secret scanning** — scans existing code for leaked tokens
- **Push protection** — blocks commits containing detected secrets *before* they reach the remote

Push protection has caught real leaks for tens of thousands of developers. It's free. Enable it.

**Limitations:** GitHub's scanner recognizes ~200 known token formats (Stripe, AWS, GitHub, Slack, etc.). Custom-format tokens may not be detected. Use a pre-commit hook (next habit) as a second line of defense.

### 4. Install a pre-commit hook: `gitleaks` or `trufflehog`

Pre-commit hooks run *before* git lets you commit. If a hook detects a secret, the commit is rejected — the secret never enters your git history.

**Install gitleaks (recommended for simplicity):**

```bash
# macOS
brew install gitleaks

# In your project root:
gitleaks protect --staged
# (or set up as a pre-commit hook via the pre-commit framework)
```

**With the `pre-commit` framework** (cross-platform, language-agnostic):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

Then `pre-commit install` once, and every `git commit` will run gitleaks first.

**Why this matters:** GitHub's push protection only triggers on push. A pre-commit hook catches secrets before they ever enter your local history. If a secret gets committed locally and *then* gets pushed without secret scanning catching it, you have to do a history rewrite to remove it (annoying and error-prone). Stop the leak earlier.

### 5. Scope every token to the narrowest permission + shortest TTL you can

**Scope:** the set of permissions a token has.
**TTL:** time-to-live, i.e. how long until the token expires automatically.

**Examples of scoping done right:**

- **GitHub PAT** (personal access token): when GitHub asks "what scopes?", check the *fewest* boxes you need. If your script only reads one repo, pick the **fine-grained PAT** option and limit it to that single repo with read-only permissions — not the classic PAT with the full `repo` scope (which is read/write to *all* your repos).
- **AWS access key**: pick the "principle of least privilege" path. AWS calls this an IAM policy. For a script that reads one S3 bucket: create a policy allowing only `s3:GetObject` on `arn:aws:s3:::my-bucket/*`. Resist anything labelled `*` or `s3:*` — those are full access. Ask the AI to *generate* the minimum policy; don't write it freehand if you're new to IAM.
- **Stripe API key**: in your Stripe dashboard, use **Restricted keys** rather than the full secret key. Each restricted key lists every API resource and you tick read / write / none per resource.
- **Mailchimp API key**: Mailchimp's API keys are bundle-scoped per-account, so use a *separate* Mailchimp account (a "free" tier sandbox) for development, and only put the production key in your production environment.

**TTL examples:**

- GitHub PAT: pick the dropdown "30 days" or "60 days", not "no expiration." You'll be prompted to renew, which is annoying and exactly the point.
- AWS: for production workloads, look up "AWS STS" (Security Token Service) — it issues temporary credentials that expire in hours instead of forever. Setup is non-trivial; defer until you have a real production deploy.
- Production deploy tokens: rotate quarterly minimum. Set a calendar reminder.

**Why this matters:** if a token leaks, the **blast radius** (everything the token can do) is bounded by its scope. A read-only Mailchimp key that leaks lets an attacker steal your subscriber list (bad). A full-access Mailchimp key that leaks lets them delete your audience and send emails as you (catastrophic). The work to create the scoped key is the same; the consequences are not.

### 6. Treat shared CI tokens as a single point of failure

**Jargon-defined:** "**Single point of failure**" means one component that, when it breaks, brings down everything depending on it. The whole point of *not* having single points of failure is so a small compromise doesn't cascade into a big one.

**CI** = Continuous Integration = the system that runs your tests / build / deploy automatically when you push code. GitHub Actions is the most common CI for hobby and small-team projects.

**The Shai-Hulud lesson** (September 2025, November 2025, May 2026 cross-ecosystem incidents):

> Attackers compromised a small number of npm maintainers' GitHub Actions tokens. Those tokens had write access to the npm package registry. The malware used the token to publish poisoned versions of legitimate packages. Within hours, the malware spread to **~25,000 repositories**.

The reason it spread so fast: **one compromised CI token was equivalent to publish access on hundreds of downstream packages.** All the developers who installed those packages (`npm install`) automatically got the malware.

**What to do (in order of effort):**

1. **Audit each CI token's scope.** If one of your CI tokens has access to "everything," narrow it. Don't worry about being perfect; just reduce the worst case.
2. **Don't reuse one PAT across multiple projects.** Make a separate token per project so a leak from one project doesn't compromise all of them.
3. **Enable branch protection on `main`** in GitHub: Settings → Branches → Add rule for `main` → require pull request reviews before merging. Even if a CI token leaks, an attacker can't push directly to `main` without a human approving.
4. **Later, when you have time:** look into GitHub Apps instead of PATs. GitHub Apps issue short-lived tokens automatically; even if leaked, they expire fast. Don't tackle this until you've done steps 1–3.

### 7. If you ever see a token in plaintext somewhere it shouldn't be: rotate first, scrub second

**Rotate first** because:

1. The moment you discovered it, others may have already discovered it. Bots scrape GitHub commits in real time looking for tokens.
2. Rewriting git history (to remove the token from past commits) is slow, error-prone, and **does nothing** for clones that already happened. Anyone who cloned the repo before you scrubbed it still has the token in their local copy.
3. Rotation is fast: go to the service's dashboard, delete the old token, generate a new one, update `.env`, restart your app. 5 minutes.

**Then scrub (optional, secondary):** if the leak was in a *public* repo, rewriting history is hygiene. Tools that do this include `git filter-repo` and BFG Repo-Cleaner. **Do not attempt this without reading the tool's documentation first** — bad history rewrites have lost people years of commits. If you're alone in the repo, you can also just delete and recreate the repo. The leaked token is already dead from step 1; scrubbing is just public-hygiene.

**Common places tokens end up by accident:**

- `.env` accidentally committed (catch with habits 2-4)
- A debug `print(API_KEY)` left in code
- A `console.log({apiKey})` in a JS handler
- A test fixture that uses a real token instead of `sk_test_...`
- A Postman collection exported and committed
- A Jupyter notebook output cell with a token in stdout
- A `curl -H "Authorization: Bearer ..."` example in a README

### 8. Audit token usage at least weekly for early-stage projects

Most platforms expose API-call logs:

- **Stripe**: Dashboard → Developers → Logs
- **Mailchimp**: Dashboard → Profile → Account → Extras → API keys (shows last-used + IP)
- **AWS**: CloudTrail
- **GitHub**: User settings → Personal access tokens (shows last-used + scope)
- **OpenAI**: Platform → Usage

**What you're looking for:**

- Calls you didn't make (e.g. API hits at 3am from an IP you don't recognize)
- Calls from an IP geography you've never used
- Sudden spikes in usage you can't explain
- Endpoints you don't use in your code being called

**If you see anything suspicious:** rotate the token immediately (habit 7). The audit doesn't prove a leak occurred — but rotation is cheap and fixes any leak whether you can prove it or not.

---

## Quick-reference checklist (print this; pin it above your monitor)

Before writing **any** code that touches an API token:

- [ ] `.env` is in `.gitignore` — verified with `git check-ignore .env`
- [ ] `.env.example` exists with placeholder values, committed
- [ ] GitHub secret scanning + push protection enabled (for repos that will be pushed)
- [ ] Pre-commit hook (`gitleaks` or equivalent) installed
- [ ] Token is scoped to minimum needed permissions
- [ ] Token has a TTL set (not "no expiration") wherever the service supports it
- [ ] Audit log location for this service is bookmarked

Before pasting **any** string into an AI chat:

- [ ] Does it match a known token format? (`sk_live_`, `ghp_`, `xkeysib-`, `AKIA`, etc.)
- [ ] If yes: redact it. If you've already pasted it: rotate immediately.

---

## When you do everything right and a leak still happens

It will happen eventually. A library you trust gets compromised. A credential gets exposed in a way you couldn't have predicted (the December 2024 Microsoft Power Pages indexing incident — a feature working as designed leaked thousands of secrets). A teammate copies a `.env` to the wrong place.

**Have an incident plan, even a 5-line one:**

1. Rotate every token in the suspected leak
2. Audit usage on each token for the last 30 days; look for unauthorized calls
3. If you find unauthorized calls: contact the service's support (Stripe, GitHub, etc. have abuse teams) and your bank if money was moved
4. Write down what happened (a single paragraph is fine) so you don't repeat it
5. Update this primer or your team's runbook with the new lesson

You will never reach zero leaks. You can reach zero *consequences* by being fast.

---

## Sources cited

- **Shai-Hulud (npm worm)**: Wiz Research, "Inside Shai-Hulud", September 2025; Microsoft Defender for Cloud advisory November 2025; CISA NPM advisory November 2025
- **Slopsquatting**: Spracklen et al., "We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs", USENIX Security 2025 (5.2% commercial / 21.7% OSS-model package-name hallucination rates)
- **GitHub secret scanning push protection**: GitHub Docs, "About push protection", 2024–2026 ongoing
- **Lovable BOLA incidents**: Wired, "The hottest AI app of 2025…", April 2025; "Lovable Register" incident report

Full citation list: `references/notes.md`.

---

## What this primer is not

- **Not a substitute for a real security review** on production / vibe-dangerous systems. If you handle medical records, financial data, or anything regulated: hire a security engineer.
- **Not exhaustive.** It covers tokens. There's more (SQL injection, XSS, CSRF, supply-chain attacks beyond Shai-Hulud, social engineering). See `checklists/owasp_*_top10.md` for the broader surface.
- **Not optional.** If you're building anything that touches a paid API or a user's data, this primer is the floor. The eight habits are not "best practices"; they're "the minimum bar to not get owned in your first year."
