---
name: lesson_01_code_read_depth
version: 2.0.0
parent_skill: form-check
audience: learner
rubric_component: 1
---

# Lesson 1 — Code-read depth

**The pitch.** Reading the diff feels like a chore. **Self-assessed productivity is systematically miscalibrated** (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, `[T1-replicated]`). One preliminary RCT (`METR-2025`, n=16, METR-self-redesigned-for-unreliability) measured senior developers, when they *don't* read the diff, ending up 19% slower while *feeling* 20% faster. The specific magnitude is preliminary; the perception-vs-measurement gap is the actionable signal. The reading is where the trustworthy speed comes from.

---

## The 90-second version

Before merging any AI-generated change:

1. **Read every line of the diff.** Not skim — read.
2. **Read every direct caller of every changed function.** ("Find references" in your IDE.)
3. **Read scope-out** — did the AI change anything you didn't ask for?

If you skipped any of those: you haven't done a code-read.

---

## Why this matters

**Two evidence streams converge:**

1. **Metacognitive miscalibration is established** (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, `[T1-replicated]`): people systematically over-predict their own performance. METR-2025 is *one preliminary RCT* (n=16; METR redesigned the follow-up for unreliability) consistent with this in software-engineering specifically. Numbers from that study, with the load-bearing caveats:
   - n=16 experienced open-source developers on their own large repos.
   - Random condition: AI-allowed vs. not.
   - AI-allowed group was 19% slower (95% CI: +2% to +37%).
   - They believed they were 20% faster.
   - **Specific magnitude is preliminary**; the perception-vs-measurement gap is the actionable signal, anchored in the broader metacognition literature.

2. **AI-generated code carries elevated security defects** (`PEARCE-2022`, `KHOURY-2023`, `ACM-COPILOT-SEC`, replicated by `MAJDINASAB-2024`, all peer-reviewed). This is cross-replicated evidence, not a single study. Reading the diff is what catches the elevated defect rate before merge.

The hypothesis follow-ups converge on: developers who trust AI output too readily, don't read carefully enough, then spend the saved-coding-time in extra debugging when the AI has subtly mis-recalled the codebase's conventions or introduced known-pattern vulnerabilities.

**The cure is mundane: read the diff.** It is mundane work, and it is also the work that does it.

A more visceral piece of evidence: the Replit production-DB-deletion incident (Cautionary Tale #1) happened in part because the agent made a destructive change that nobody read line-by-line. The destructive command was in the diff. Reading would have caught it.

---

## The full process

### Step 1: open the diff

Whatever your tool — GitHub PR view, `git diff`, VS Code's "git lens", IntelliJ's compare view — open it.

If the diff is too big to read (>200 lines for a learner, >500 for a senior): **the AI's task was scoped too broadly.** Reject and reprompt with a smaller scope. Big diffs are unreviewable in practice and unreviewable diffs become unread diffs.

### Step 2: read every line, not just the changed lines

The diff shows `+` and `-` lines plus a few lines of context above and below each hunk. **Read the context too.** Why?

- The context shows you what the change *replaces* or *fits into*.
- A 2-line change in a 200-line function may make sense in isolation and break the function in context.
- The AI may have generated correct-in-isolation code that contradicts a convention 5 lines above the hunk.

### Step 3: for each changed function, find every caller

Open your IDE's "Find references" or `git grep` for each changed function's name. **For each caller, ask:**

- Does this caller still work with the new signature?
- Does this caller still get the same return value semantics?
- Was the caller relying on a behavior the new code no longer provides?

If a function is called from 8 places and you've checked 2: you've checked 25%. Be honest about that. You either commit to checking the rest or you bump the change's tier (because the blast radius is larger than you have time to verify).

### Step 4: read scope-out — did the AI change anything you didn't ask for?

This is the lesson most learners miss. AI assistants sometimes "helpfully" do things adjacent to the requested change — add a logging line, change a variable name to match a convention they perceive, add an import that isn't needed.

**Each off-scope change is potentially a bug.** Each off-scope change is also potentially harmless. You don't know which without reading.

Scan the diff once for: "did anything change that wasn't part of the request?" Common targets:

- New imports at the top of files
- Changes to test files you didn't ask to change
- Changes to docs or comments you didn't ask to change
- Changes to *unrelated* functions in the same file
- New files entirely

Each of these may be fine. Each is a place to ask: "why did this change?"

### Step 5: write the one-sentence summary

Before you merge, write (in your head or in the PR description): **"This change does X by modifying Y, which is called by Z, and I checked Z still works."**

If you can't fill in X, Y, Z: you haven't read enough yet.

---

## What goes wrong

### Failure mode A: "the diff is long, I'll skim"

The Replit case had a destructive command in the diff. Skimming misses destructive commands. **There is no skim-mode that catches what reading-mode catches.** If the diff is too long, the answer is "split the change," not "skim faster."

### Failure mode B: trusting the test suite to catch what you don't read

Tests cover what they cover. They don't cover what they don't cover. The AI's change may pass all current tests *and* introduce a regression in a code path with no test. Reading the diff is the second filter.

### Failure mode C: reading code, not behavior

You read the line `if user.is_admin:` and accept it as "checks admin." But the question is *what does `is_admin` return* for the user shape the caller passes? Reading code means looking up unfamiliar functions, types, return values — not pattern-matching on familiar shapes.

For learners, this is the most insidious failure mode. The fix: when you see a method you don't recognize on a type you've seen before, **look up the method**. Don't assume.

### Failure mode D: reading once, not after revisions

You ask the AI to change something. You read the diff. You ask for a tweak. The AI regenerates the diff. **You only read the new lines.** But the regenerated diff may have changed an unrelated line you didn't ask to touch.

**Rule:** every revision is a new diff. Read all of it, every time.

---

## When code-read depth gets relaxed

The full procedure (every line + every caller + scope-out) is **Floor 1** for vibe-safe, and it's the only step you don't get to skip. There's no relaxation for "trivial" changes — most production outages started as trivial changes.

The only place this gets *intensified* is Floor 3 (vibe-dangerous), where you also:

- Read every test file involved
- Trace data flow through 2-3 levels of callers, not just direct callers
- Read the docs of any external library involved

---

## Exercises

### Exercise 1: time yourself

Find a small AI-generated PR (in your own work, or in a public repo you contribute to). Open the diff. Time yourself reading it carefully. **Note the total time.**

Most learners do this in 3–7 minutes. The goal isn't speed; the goal is calibrating "what reading really takes."

### Exercise 2: catch a planted error

Ask the AI to make a small change to a function. After you get the diff, **before reading**, ask the AI: "regenerate the diff with one subtle bug introduced — change a `>=` to `>`, or use the wrong variable name in one line."

Now read the diff and find the bug. If you find it: you're reading well. If you don't: read more slowly.

(This is a self-test you can do anytime. The bug is a known-good calibration target.)

### Exercise 3: trace one caller

Pick any changed function in a recent PR. Find every caller in the codebase (your IDE's "Find references" or `git grep -n "function_name(" .`). Read each one. **Note any caller you wouldn't have thought to check.** That note teaches you what your reading missed.

---

## Cross-references

- **Rubric component 1** in `rubrics/confidence_score.md` — weight 15, the highest single-component weight.
- **Cautionary tale #5** (METR perception gap) in `learner/cautionary_tales.md`.
- **First-PR walkthrough Step 4** in `learner/first_pr_walkthrough.md` — concrete demonstration of reading scope-out.
- **The mini-runbook in `SKILL.md` Section 10** — code-read is steps 2 and 4.

---

## Retrieval prompts

Per `learner/study_protocol.md` Habit 1 (retrieval beats re-reading): **close this file** and answer the questions below in writing or aloud. Then re-open and check.

If you miss two or more, schedule a re-read for **+3 days** (Habit 2 — spacing).

1. Close this file. Name the two read-protocols (full-diff vs caller-trace) and when each is the right one.
2. What is the **established phenomenon** (with citations) and what is the **preliminary RCT** that one example of it draws on? Why doesn't this lesson load-bear on the RCT's specific magnitude?
3. What is the *scope-out* signal, and what's the first move when you see it?
4. Give an example PR where reading the full diff would catch a bug that reading only the touched files would miss.

When you've answered all four cold (no peeking) on two separate occasions ≥1 week apart, this lesson has stuck. Move it to your spaced-review monthly cadence.
