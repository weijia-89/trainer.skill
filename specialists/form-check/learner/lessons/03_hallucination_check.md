---
name: lesson_03_hallucination_check
version: 2.0.0
parent_skill: form-check
audience: learner
rubric_component: 3
---

# Lesson 3 — Hallucination check

**Why this is lesson #1 to read.** The 30 seconds it takes to verify a single new import is the single highest-value habit in this entire skill. If you do nothing else from the rubric, do this.

---

## The 90-second version

Every time you see an AI-suggested code change that adds a new `import` / `require` / `use` / `include` / dependency:

1. **Open the registry page** for the package (npmjs.com, pypi.org, crates.io, etc.).
2. **Check four things** on the page:
   - It exists.
   - The author has other packages or a reasonable history.
   - First published at least 30 days ago.
   - The README describes the API the AI used.
3. **If any check fails: do not install.** Ask the AI for an alternative. Don't argue with the AI — just don't install.

That's it. 30 seconds per import. Non-negotiable.

---

## Why this matters

In 2025, researchers at the University of Texas (Spracklen et al., USENIX Security) measured how often AI assistants invent package names that don't exist. They tested several commercial models (Claude, OpenAI's flagship model, others) and several open-source models (CodeLlama, others) on tens of thousands of coding prompts.

The result:

- **Commercial models hallucinate package names 5.2% of the time.**
- **Open-source models hallucinate package names 21.7% of the time.**

Translate that into your daily life: if your AI assistant suggests 20 imports in a week, **one of them is fake.**

The follow-up threat is called **slopsquatting**. An attacker reads the research, looks at which package names are commonly hallucinated, registers those names on npm/PyPI for real, and puts malware in them. Then the next developer asks an AI to write similar code, the AI suggests the (now real, malicious) package, the developer installs it without checking, and the malware runs.

This is happening in the wild. As of 2026, there are documented cases of attackers profiting from this exact loop.

**Why beginners are at higher risk than seniors:**

- Seniors have rough intuitions for which packages are real. They've worked with the ecosystem long enough that "did I ever hear of that?" is a meaningful filter.
- Beginners don't have that filter yet. To a beginner, every package name is novel, so a hallucinated name feels just as plausible as a real one.

The 30-second check restores the filter.

---

## The full process — what to actually do

### Step 1: identify "new" imports in the diff

A "new" import is one that:

- Wasn't in your codebase before this change
- Wasn't in your `package.json` / `requirements.txt` / `Cargo.toml` / `pyproject.toml`

Look at the `+` lines in the diff. For each `import foo` / `from foo import bar` / `const foo = require('foo')` / etc., ask: is `foo` already in the lockfile (`package-lock.json`, `poetry.lock`, `Cargo.lock`)?

- **Yes, already pinned**: skip. It's verified.
- **No, new**: it's a candidate for verification.

### Step 2: open the registry page

For each new dependency:

- npm: `https://www.npmjs.com/package/<name>`
- PyPI: `https://pypi.org/project/<name>/`
- crates.io: `https://crates.io/crates/<name>`
- Maven Central: `https://central.sonatype.com/artifact/<group>/<artifact>`
- RubyGems: `https://rubygems.org/gems/<name>`
- Go: `https://pkg.go.dev/<full/import/path>`
- NuGet: `https://www.nuget.org/packages/<name>`

If the URL 404s: **the package doesn't exist**. The AI hallucinated it. Don't install. Ask the AI for the real name (it may say "I confused that with X — here's the right name").

### Step 3: check the four signals

Once the registry page loads:

**Signal 1: Author / publisher legitimacy.**

- Click into the publisher's profile.
- Do they have other packages? Are those packages also legitimate-looking?
- Is the email or contact info there?
- Look for a GitHub link; does the GitHub user have a normal activity pattern?

**Red flags:**

- Anonymous publisher with no other packages
- The only contact is a brand-new free-email-provider address
- The package is the publisher's first and only release
- The GitHub repo (if any) has zero stars and one commit

**Signal 2: First-publish date.**

- Look for "Published" / "Created" / "First release" on the package page.
- **If it's less than 30 days old**, treat as suspect. Slopsquatting attacks register fresh.
- Exceptions exist (legitimate new packages happen) — pair this signal with the others.

**Signal 3: README / docs match.**

- Read the package's README (it's on the registry page).
- Does the README describe the API the AI used?
- If the AI wrote `mypackage.do_thing(x, y)`, does the README mention `do_thing`?
- **If the docs don't describe the API the AI used: the AI hallucinated either the package or the method.** Don't proceed.

**Signal 4: Download / star count (sanity check).**

- npm packages: weekly downloads. Real popular packages have thousands-to-millions.
- GitHub stars on the linked repo, if any.
- **This is a sanity check, not a security check.** Low downloads don't mean malicious. High downloads don't mean safe (Shai-Hulud poisoned high-download packages). Use as a contextual signal only.

### Step 4: if anything's off, refuse and reprompt

Don't try to "verify deeper" if signal 1, 2, or 3 fails. Just don't install. Reprompt:

> The package `xyz-utils` you suggested doesn't exist (or: has no README / is 3 days old / etc.). What's the real package you meant, if any? If there isn't one, can we do this without a new dependency?

Often the AI will say "I conflated two packages — the real one is `actual-name`." Then re-verify *actual-name*.

If the AI insists `xyz-utils` is correct after you've shown it doesn't exist: stop. The AI is confidently wrong. Implement what you need without that dependency, or ask the AI to write the function inline.

---

## What goes wrong — named failure modes

### Failure mode A: skipping the check because "the AI sounded confident"

This is the most common failure. The AI's tone is confident on hallucinations and confident on facts equally. **Tone is not evidence.** The 30 seconds is non-negotiable.

### Failure mode B: half-verifying

You opened the registry page, saw it existed, and installed. You didn't read the README. The package exists but its API is completely different from what the AI wrote. You spend two hours debugging "why doesn't `mypackage.do_thing` work" before realizing the real method is `mypackage.process`.

**Rule:** if you don't check signal 3 (docs match), you haven't really verified.

### Failure mode C: trusting low-download-count signal alone

You found a package with 12 weekly downloads and concluded "this is malicious." But it might just be new and niche. Conversely, a package with 1M weekly downloads might be compromised (Shai-Hulud). **No single signal is sufficient.** Use the four together.

### Failure mode D: not noticing the registry namespace

`react-router` is the well-known npm package. `react-routerx` is something else entirely. `react.router` doesn't exist as a single package. **Typosquatting** is when an attacker registers `react-routerr` (extra `r`) hoping someone fat-fingers it. AI hallucinations + typosquatting = compound risk.

**Rule:** when you copy the package name from the AI suggestion, paste it into the registry URL exactly. Don't retype it.

### Failure mode E: AI insists, you cave

The AI says "yes, the package is correct" after you've shown it doesn't exist. You start to doubt your own check. **Don't.** The AI does not have real-time knowledge of npm. It is hallucinating with confidence. Trust the registry, not the AI.

---

## When you can skip the check (rare)

You can skip the four-signal check **only** when:

- The dependency is already in your lockfile (you've verified it before)
- The dependency comes from your organization's private registry where every package was vetted by humans
- The "import" is from your project's own files (e.g. `import { foo } from './utils'`)

You **cannot** skip the check when:

- The AI suggested the package by name (always check, even on familiar-sounding names)
- The package looks "obviously real" (the most-likely-real-looking packages are the most-attacked targets)
- You're in a hurry (the asymmetry — 30 seconds now vs. weeks of recovery — doesn't change because you're rushed)

---

## Exercises

These are real practice tasks. Do them once.

### Exercise 1: verify a real package

Ask your AI: "what's the most popular HTTP request library for Python?"

It'll say `requests`. Now walk the four signals:

1. https://pypi.org/project/requests/ — exists
2. Author: Kenneth Reitz / Python Software Foundation — well-known
3. First published: 2011 — old, fine
4. README: methods like `requests.get(url)` are described — matches what the AI said

Total time: 45 seconds. You've now done the check correctly once.

### Exercise 2: spot a fake one (safely)

Ask your AI to write a Python utility that uses an obscure package — make up a context like "compute the molecular weight of a chemistry formula." See what package it suggests.

Verify it. If it's real (and well-known like `rdkit`), great — you've practiced. If it's something you've never heard of, walk the four signals before you would have installed it. Either outcome teaches you the procedure.

### Exercise 3: trace one Shai-Hulud-class compromise

Read the Shai-Hulud cautionary tale (`learner/cautionary_tales.md` story #2). Now imagine your project depends on a package whose maintainer was compromised. Which of your habits would catch it *before* you installed the poisoned update?

- Lockfile? (Pins exact versions so an automatic update can't happen.)
- Reviewing version bumps in PRs? (`package-lock.json` diff shows what changed.)
- `npm audit` / `pip-audit`? (Catches *known* vulnerabilities — not zero-days, but published ones.)
- Pinning + waiting 1–2 days after a release before updating? (Lets the community catch obvious malware.)

You should be able to name 2-3 layers. If you can only name 1, you're under-defended.

---

## Cross-references

- **Rubric component 3** in `rubrics/confidence_score.md` — this is the rubric this lesson teaches.
- **Cautionary tale #2** (Shai-Hulud) and **#3** (slopsquatting) in `learner/cautionary_tales.md`.
- **Supply-chain checklist** in `checklists/supply_chain_slsa.md` — the broader hygiene around dependencies (SBOM, SLSA, audit tools).
- **Token primer habit 6** (CI tokens as single point of failure) in `learner/token_handling_primer.md`.

---

## Retrieval prompts

Per `learner/study_protocol.md` Habit 1 (retrieval beats re-reading): **close this file** and answer the questions below in writing or aloud. Then re-open and check.

If you miss two or more, schedule a re-read for **+3 days** (Habit 2 — spacing).

1. Close this file. List the four signals you check for a hallucinated package.
2. What was the hallucination rate Spracklen et al. found for commercial models? For open-source models?
3. Define *slopsquatting* in your own words.
4. Why is the '30 days old' threshold load-bearing — what is it actually testing?

When you've answered all four cold (no peeking) on two separate occasions ≥1 week apart, this lesson has stuck. Move it to your spaced-review monthly cadence.
