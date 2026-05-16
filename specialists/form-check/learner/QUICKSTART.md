---
name: quickstart
version: 2.0.0
parent_skill: form-check
audience: learner
---

# QUICKSTART — for someone 6–18 months into coding

Welcome. This file exists because the main skill (`SKILL.md`, ~220 lines) was written in senior-engineer voice. That voice is correct for someone who already knows the vocabulary, but it skips the explanation step that you need.

This file gives you:

1. A glossary you can refer back to as you read the rest of the skill
2. A 3-question test for "how scary is this change?" (the tier classifier)
3. Three safety floors at increasing effort
4. Pointers to the learner resources that go deeper

**Read this once, then keep it open in a tab while you read the rest.** Don't memorize it. Look things up.

---

## Part 1 — Glossary

The main skill uses these terms freely. Each one gets a one-paragraph definition here, in roughly the order they appear in `SKILL.md`.

### Posture words

**Vibe coding** — coding where you let an AI assistant write most of the code while you steer it via natural-language prompts. Term coined by Andrej Karpathy. Not a slur; it's a real workflow. The skill is built around the idea that vibe-coded changes need a slightly different review posture than hand-written ones.

**Vibe-safe / vibe-careful / vibe-dangerous** — three buckets for "how scary is this change?" See the 3-question classifier in Part 2.

**Vibe-impossible** — a fourth bucket meaning "the AI should not attempt this without explicit human design," e.g. a crypto protocol from scratch. It's a refusal classification, not a score band. (Yes, the skill clearly distinguishes these. The naming is unfortunate.)

**Default-anti-enterprise** — the skill refuses to recommend "enterprise" patterns (microservices, Kubernetes, event buses, CQRS) unless you can name a specific reason you need them. This is a stance, not a religion: those tools exist for real reasons; you probably don't have those reasons yet.

**Forcing constraint** — a named, written-down reason you actually need an enterprise pattern. Example: "the system must process 10,000 events/sec with end-to-end traceability across teams." If you can't write the forcing constraint in one sentence, you don't have one. See `templates/forcing_constraint_adr.md` and `tools/check_forcing_constraint.sh`.

### Documents and processes

**ADR (Architecture Decision Record)** — a short markdown file (usually 1 page) that records *why* you made a particular architecture choice. It captures context, options considered, decision, and consequences. Lives in `docs/adr/` in your repo. Future-you and your teammates can read why you chose Postgres over MongoDB without asking you.

**MADR-short** — a specific lightweight ADR template (Markdown Architecture Decision Record, short variant). Template: `templates/MADR_short.md`.

**CLAUDE.md / AGENTS.md** — markdown files in your project root that tell AI assistants the project's conventions, gotchas, and how to run/test/deploy. Reading these files first is "step zero" for any AI-assisted change. The skill assumes you have one; if you don't, create it from `templates/CLAUDE.md_scaffold.md`.

**Fitness function** — an automated test in CI that enforces an architecture decision over time. Example: "no file in `core/` is allowed to `import` from `web/`" — written as a CI check that fails the build if violated. Term coined by Neal Ford / Rebecca Parsons. Without fitness functions, architecture decisions decay; teams forget; the rule was only in a slide deck.

**Test-as-spec** — write the failing test *first*, expressing what the change should do, *then* let the AI implement it. The test is the contract; the implementation is the negotiation. This catches "I asked for X but got Y" before you've shipped Y.

**Golden test** — a test that compares output against a known-good snapshot. Useful for refactors: you snapshot the output, then refactor, then assert the snapshot still matches.

**Characterization test** — a test that documents *current* behavior (even if that behavior is wrong) so you can refactor without changing behavior accidentally. Michael Feathers' term, from *Working Effectively with Legacy Code*.

**Mutation testing** — a way to evaluate your tests. The tool mutates your source code (changes `==` to `!=`, deletes a line, etc.) and re-runs your tests. If your tests *don't fail* after the mutation, the test suite has a gap there. "Mutation score 60%" means 60% of mutations caused test failures. Higher is better; targets in `rubrics/confidence_score.md`.

### Security and risk vocabulary

**CWE (Common Weakness Enumeration)** — a public catalog of common security weaknesses, numbered. CWE-79 is XSS, CWE-89 is SQL injection. "Walk the CWE Top 25" means review your change against the most common 25 weaknesses. Catalog: `cwe.mitre.org`.

**OWASP Top 10** — the Open Worldwide Application Security Project publishes a list of the most common security risks for web apps, APIs, and LLM-using apps. Three separate Top-10 lists matter:
- **OWASP Top 10 (Web)** — broken access control, injection, etc.
- **OWASP API Top 10** — broken object level authorization (BOLA), etc.
- **OWASP LLM Top 10** — prompt injection, sensitive info disclosure via outputs, etc.

**STRIDE** — a checklist for threat-modeling a system. Stands for **S**poofing / **T**ampering / **R**epudiation / **I**nformation disclosure / **D**enial of service / **E**levation of privilege. For each component of your system, ask "can this happen here, and what do we do about it?"

**LINDDUN** — STRIDE's privacy-focused cousin. Stands for **L**inking / **I**dentifying / **N**on-repudiation / **D**etecting / **D**ata disclosure / **U**nawareness / **N**on-compliance. Use when your change touches personal data.

**SLSA (Supply-chain Levels for Software Artifacts)** — a framework for how trustworthy your build process is. Levels Build-L1 through Build-L3. Build-L2 means: provenance is generated, hosted by a build platform, and signed. The skill asks for SLSA Build-L2 minimum because supply-chain attacks (Shai-Hulud, etc.) bypass everything else.

**SBOM (Software Bill of Materials)** — a machine-readable list of every dependency in your project, including their versions and license. Two common formats: **CycloneDX** and **SPDX**. If a vulnerability is published for `left-pad@1.2.3`, your SBOM tells you instantly whether you ship that version. Tools like `syft` generate SBOMs from your codebase.

**Slopsquatting** — when an attacker registers a package name that AI assistants frequently *hallucinate* (recommend even though it doesn't exist), then puts malware in it. The USENIX 2025 study found commercial models hallucinate package names 5.2% of the time; OSS models 21.7%. Mitigation: **verify every new import** (registry exists, author plausible, first-seen ≥30 days, current docs match).

**Shai-Hulud** — name given to a sequence of npm/PyPI worm attacks (Sept 2025, Nov 2025, May 2026). Attackers compromised CI tokens, used them to push malicious package updates, and the malware propagated through `npm install`. Worst single npm incident in history at the time. The lesson: a shared CI token is a single point of failure.

**Blast radius** — how much of the system one change affects. Touching one file in a CLI utility = small blast radius. Touching the database schema = large blast radius. Higher blast radius = stricter review tier. The skill has a tool to compute this: `tools/blast_radius.py`.

### Engineering vocabulary

**Modular monolith** — one deployable unit (one process, one repo), but with strong internal module boundaries. Almost always the right starting point. Use this until you have a forcing constraint to do otherwise.

**Microservices** — many small deployables. Solves problems large teams face. Creates many problems small teams face. The skill refuses to recommend them by default.

**Parnas module boundaries** — David Parnas's 1972 rule for "what should be its own module?" Answer: hide a *design decision likely to change*, not a flow step. The "thing you'd rewrite when the requirement changes" lives behind a boundary.

**Hexagonal architecture / Ports-and-adapters** — Alistair Cockburn's pattern: your core domain logic doesn't know about HTTP, databases, or queues; it talks to "ports" (interfaces) that have "adapters" (concrete implementations). Useful if you actually have **two or more adapters** for the same port. Not useful as a default; it adds layers without benefit if you'll only have one adapter.

**Trunk-based development** — everyone commits to a single branch (`main`) frequently, with feature flags to keep in-progress features hidden. Opposite of long-lived feature branches. DORA evidence supports trunk-based for delivery throughput.

**Feature flag** — a runtime switch that turns a feature on or off without redeploying code. Useful for staged rollouts (turn on for 1% of users, then 10%, then 100%) and instant rollbacks.

**Pre-commit hook** — a script git runs *before* it lets you commit. If the script exits non-zero, the commit is rejected. Used for linting, formatting, secret scanning (see `learner/token_handling_primer.md`).

### Things I'm not going to define here because they have their own files

- The **9-component confidence score** lives in `rubrics/confidence_score.md`. Use that file directly.
- The **vibe-safety map** lives in `rubrics/vibe_safety_map.md`.
- The **smell catalog** lives in `checklists/smell_catalog.md`.

---

## Part 2 — The 3-question tier classifier

Before you start reviewing a change (yours or an AI's), ask three questions in order. The first "yes" decides the tier.

### Question 1: Is this vibe-dangerous?

Does the change touch any of these?

- **Auth / login / session / passwords**
- **Payments / charges / refunds / Stripe / billing**
- **Secrets / API keys / tokens / `.env`**
- **Deletes** (files, database rows, external accounts)
- **Schema migrations** (especially `DROP` or `ALTER TABLE` that rewrites data)
- **Public side effects** (sends email, posts to social, makes a Stripe charge, fires a webhook)

→ **Yes to any** = **vibe-dangerous**. Go to Floor 3 (Part 3). Don't proceed without it.

### Question 2: Is this vibe-careful?

If you answered "no" to question 1:

- **Public API surface** — you're changing a function/endpoint that external code calls?
- **Adding a new dependency** — `npm install`, `pip install`, `cargo add` for something new?
- **Schema-additive** — adding a new column / table / index (but not destroying anything)?
- **Prompt change** — modifying the prompt template an AI uses in production?

→ **Yes to any** = **vibe-careful**. Floor 2 (Part 3).

### Question 3: Otherwise — vibe-safe

If you answered "no" to questions 1 and 2:

- **UI tweak** (text, color, layout)
- **Internal helper function** that no other code calls yet
- **Log statement** added or changed
- **Comment / docstring** change

→ **Vibe-safe**. Floor 1 (Part 3).

### Edge cases the classifier doesn't handle cleanly

**"Pure refactor"** (rename, extract, format, no behavior change). The skill treats this as a sub-row of vibe-safe with a relaxed threshold *only if* you have a behavior-preservation check in place (e.g. a golden test that asserts the output is unchanged). If you don't have that check, the refactor is just a regular vibe-safe change.

**"I don't know which bucket"** — round up. The cost of treating a vibe-safe change as vibe-careful is some extra effort. The cost of treating a vibe-dangerous change as vibe-safe is, potentially, all your money. Round up.

---

## Part 3 — The three safety floors

You don't have to do the full 9-component rubric for every change. Use the floor that matches the tier from Part 2.

### Floor 1 — Vibe-safe (5 minutes, always run before merging)

Three questions:

1. **Did you read the diff?** Open the diff. Read every changed line. Don't merge unread changes, no matter how confident the AI sounded.
2. **Any new imports?** If yes: verify each one exists on the registry (npmjs.com / pypi.org), the author is plausible, and it's been around for at least 30 days. (See `learner/lessons/03_hallucination_check.md` for the full procedure.)
3. **Do the tests still pass?** Run them. If new code was added but no new tests were added: ask "what does this code do?" and write one test for the happy path.

That's the floor. Five minutes if you do it routinely. **Don't skip it for "tiny" changes** — most production outages started as "tiny" changes.

### Floor 2 — Vibe-careful (30 minutes, run when touching public API or adding a dependency)

Everything in Floor 1, **plus**:

4. **Walk three worst-case scenarios.** For each: what happens, who notices, how do you roll back? Write the answers in the PR description.
   - Worst case A: the new code throws an exception in production.
   - Worst case B: the new dependency has a vulnerability published next week.
   - Worst case C: a user does the thing you didn't think of.

5. **Read CLAUDE.md / AGENTS.md and update them if needed.** Did you add a new env var? A new build step? A new test command? A new convention? Add it now while it's fresh. Future-you will thank you.

6. **Walk the relevant checklist.** `checklists/INDEX.md` has a decision tree. For a dep-add: read `checklists/supply_chain_slsa.md`. For an API change: read `checklists/deprecation_policy.md` (covers semver, `Sunset` headers, RFC 8594 deprecation contract).

### Floor 3 — Vibe-dangerous (2 hours minimum, run when touching auth/payments/secrets/deletes/schema)

Everything in Floor 2, **plus**:

7. **Threat model the changed surface.** STRIDE checklist (see glossary). For each new attack surface: spoofing? tampering? repudiation? info disclosure? denial of service? elevation of privilege? Write the answers.
8. **Get a human reviewer.** Not the AI. A human. If you're solo, a human you trust who has done the kind of work you're touching. (No human available? Ship behind a feature flag *off by default* and let the change soak in production traffic for a week before you enable it.)
9. **Deploy behind a feature flag.** Staged rollout: 1% → 10% → 100% over days, not minutes. Monitor logs at each step.
10. **Document the rollback.** Before you ship, write the answer to: "It is 3am, you see the error rate spike, what is the *exact* command you run to roll this back?" If you can't answer in one line, you're not ready to ship.

Then — and only then — go through the full 9-component rubric in `rubrics/confidence_score.md` and score the change.

---

## Part 4 — Pointers to learner resources

Read these in roughly this order:

1. **You are here:** `learner/QUICKSTART.md`
2. **The fear you came with:** `learner/token_handling_primer.md` — the eight habits that prevent token leaks. Read this **before writing any code that touches an API**.
3. **Stories of real disasters:** `learner/cautionary_tales.md` — what actually went wrong, in real incidents, in plain language. Read this when you want motivation.
4. **Your first review, walked end-to-end:** `learner/first_pr_walkthrough.md` — a real change, narrated, with friction points called out.
5. **Lessons one component at a time:** `learner/lessons/` — one file per rubric component. Start with `learner/lessons/03_hallucination_check.md` (highest-value-per-minute). Then `learner/lessons/01_code_read_depth.md`, then `learner/lessons/02_test_verification.md`, then `learner/lessons/06_reversibility.md`.

`SKILL.md` itself is not gated — you can read it anytime — but the senior-engineer voice is easier once you have the glossary in your head.

**When have you outgrown QUICKSTART?** Concrete behavioral signals, not a count:

- You can do Floor 1 in under five minutes without looking at the checklist.
- When someone says "STRIDE" or "SBOM" or "fitness function," you don't have to look it up.
- You've shipped at least one Floor-3 change end-to-end (including the threat model and the rollback documentation).
- You've recognized at least one near-miss in your own work and traced it back to a floor step you would have skipped.

When those four are true, QUICKSTART is reference material, not a curriculum. Read `SKILL.md` cover-to-cover when convenient, and keep `learner/token_handling_primer.md` pinned regardless of experience level.

---

## Part 5 — Things to tell yourself when this feels overwhelming

- **You don't need to learn all of this today.** You need the *floors* and the *token primer*. Everything else is just-in-time learning.
- **The skill is opinionated on purpose.** Some of those opinions are wrong for your context. That's fine — once you've internalized them, you can disagree intelligently. Until then, follow them.
- **AI-assisted coding can be faster than not — eventually.** Self-reported productivity is *systematically miscalibrated* (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, both `[T1-replicated]`). The METR-2025 RCT (n=16, preliminary, METR's own follow-up was redesigned for unreliability) measured experienced devs feeling +20% faster while measurably −19% slower; that single study's specific magnitude is not load-bearing, but the perception-vs-measurement gap is. The skill is designed to surface that gap. Following floors costs minutes; not following them can cost months.
- **Failures are part of the learning.** Read `cautionary_tales.md` *after* a near-miss, not *before*. They're more visceral when you can map them to your own near-misses.
- **Ask the AI to explain anything in this skill.** The skill is a teaching document, not a contract. If a section confuses you: "explain Parnas module boundaries to me like I'm a year into coding" is a totally valid prompt to your AI assistant. Use it.
