---
name: gymbuddy
description: |
  Use when working with an AI coding assistant, evaluating AI-generated code, writing prompts, deciding whether to delegate to AI, or noticing signs of over-reliance on AI output. Symptoms: hallucinated imports, AI-suggested destructive commands, diffs accepted unread, confident-but-wrong AI explanations, perception of AI speed exceeding measured speed.
type: project-skill
version: 2.0.0
authors: Wei Jia (1.0, 2026-05-15); v2 Iron Law layering + composes-pin to form-check@>=3 2026-05-16
license: MIT
required_tools: [file_read]
recommended_tools: []
optional_tools: []
composes:
  - skill: form-check
    version: ">=3.0.0,<4.0.0"
    role: AI-generated code goes through the same rubric as human-generated; this skill is the lens, form-check is the verifier
---

# gymbuddy. AI trains alongside you; you still do the reps

```
IRON LAW: NO AI-GENERATED CODE MERGED WITHOUT FRESH VERIFICATION EVIDENCE IN THIS SESSION.
```

Violating the letter of this rule is violating the spirit of this rule. "I verified something *like* this last week" does not satisfy the rule; the verification must be on *this* diff in *this* session. The slopsquatting evidence (`SLOP-arXiv` `[T1-replicated]`, cross-replicated by Snyk/Aikido/Mend; commercial models hallucinate package names ~5%, OSS models ~22%) means **every new import in every AI-generated diff** is a potential supply-chain attack until verified.

## Red Flags. STOP and verify before merging

If any of these thoughts is in your head:

- "The AI sounds confident, that's a signal."
- "The diff is small, it's probably fine."
- "I'll verify the imports later."
- "I've done this kind of change before, no need to re-check."
- "This is just boilerplate, I'll skim."
- "The AI's explanation makes sense, so the code probably works."
- "I tested the happy path, that's enough."
- "I'll just trust the AI on this one."
- "The package name looks reasonable." (Slopsquatting attackers register the names that *look reasonable*.)

Each red flag means: stop. Open the diff. Walk `learner/lessons/03_hallucination_check.md` (30-second hallucination check) for every new import. Then run the form-check tier-floor check before merge.

## Rationalizations, what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "I read the diff carefully" | If you didn't open every direct caller of every changed function, you skimmed the diff. `learner/lessons/01_code_read_depth.md`. |
| "Slopsquatting is rare" | 5–22% hallucination rate cross-replicated by 4 independent research groups (`SLOP-arXiv`, `SNYK-SLOP-2025`, `AIKIDO-SLOP-2025`, `MEND-SLOP-2025`). One in five OSS-model imports is fake. The 30-second registry check is non-negotiable. |
| "The AI is more careful than me" | The AI is *more confident* than you, which feels like more careful but isn't. Self-assessed AI quality is also miscalibrated; verify every output. |
| "Verification slows me down" | The METR-2025 RCT (`[T1-verified, n=16, preliminary]`) plus broader metacognitive-miscalibration evidence (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`) suggest the *feeling* of speed is unreliable. The verification is where trustworthy speed comes from. |
| "I'll set up better verification next sprint" | Every "next sprint" PR is also under the same rule. There is no exemption for in-flight work. |

## Keywords for discovery

For trigger-keyword indexing (does not affect frontmatter behavior): how should I use AI for this, AI wrote this, AI suggested, copilot wrote this, claude wrote this, gpt wrote this, vibe coding, should I trust this AI code, the AI is confidently wrong, hallucinated import, prompt engineering, prompting, how do I prompt, am I leaning on AI too much, when not to use AI, AI pair programming, AI pair, AI-assisted, AI-generated.

## Scope

You use an AI to write code. The question this skill answers is *how to do that without absorbing the failure modes the literature has documented*: metacognitive miscalibration of self-assessed productivity (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, with the METR-2025 RCT as one preliminary example), slopsquatting (cross-replicated, see above), hallucinated APIs, AI-generated security defects (`PEARCE-2022`, `KHOURY-2023`, `MAJDINASAB-2024`), AI-confidence-shaped destructive commands (`REPLIT-FORTUNE`).

**Scope.** Workflow patterns for AI-assisted development, prompting hygiene, the calibration discipline applied to AI suggestions, when *not* to delegate to AI.

**Not for.** Replacing thinking. AI assistants are leverage on your existing judgment, not a substitute for it. If this skill becomes a way to outsource the parts you don't want to learn, it's not working, see `form-check/learner/study_protocol.md` "The pedagogy paradox."

## §1. The core insight: AI shifts work from *writing* to *verifying*

Pre-AI software work was roughly: 30% thinking, 60% writing, 10% reviewing.

AI-assisted work is roughly: 50% thinking-and-prompting, 10% writing-AI-prompts, **40% reviewing AI output**.

The total time isn't necessarily lower. **Self-assessed productivity is systematically miscalibrated** (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, both `[T1-replicated]`); the METR-2025 RCT (n=16, preliminary, METR's follow-up redesigned for unreliability) is one example consistent with this, experienced devs felt +20% faster while measurably −19% slower on familiar repos. The specific magnitude is preliminary; the perception-vs-measurement gap is the actionable signal. The *shape* of the work shifts: the skill is not "write code" but "form clear intent, prompt for it, and verify the result."

A lot of beginner AI-assisted disasters come from doing the *prompting* but skipping the *verifying*. Verifying isn't optional. It's where the work moved.

## §2. When to use AI (and when not)

### 2.1 Strong fit (use AI confidently)

- **Boilerplate generation.** Test scaffolds, CRUD endpoints, config files, type definitions, frontmatter conversions.
- **Translation between formats.** JSON ↔ YAML, regex ↔ prose, SQL ↔ ORM, English ↔ commit messages.
- **Recall of standard library / framework usage** you've used before but forgotten the exact API.
- **First-pass refactoring** of code you can read fluently. (You read; AI proposes; you accept what you can verify.)
- **Writing tests for behavior you've already specified.** Spec first, tests second.
- **Explaining unfamiliar code** at a high level. (Verify the explanation against the code; AI sometimes invents a story that doesn't match.)

### 2.2 Caution fit (use AI but require explicit verification)

- **Code that calls external libraries.** Hallucinated imports (`form-check/learner/lessons/03_hallucination_check.md`) are the highest-incidence failure mode. Verify every new import on the registry before installing.
- **Code that touches authentication / authorization.** Lovable BOLA. AI generates auth (which is easy) but skips authz (which it conflates with auth). Verify with a test that calls the endpoint as a *different* user and asserts 403.
- **Code that does destructive operations.** Deletes, drops, truncates, force-pushes, migrations. Treat AI-generated destructive code as *advisory only*, read it line by line; never execute it directly.
- **Anything in production at 2am.** Hallucination + sleep deprivation + AI confidence = Replit/Lemkin cautionary tale (`form-check/learner/cautionary_tales.md` Tale 1). The AI doesn't know it's an incident; you do; act accordingly.

### 2.3 Bad fit (AI is the wrong tool)

- **Initial architectural decisions** at the scope of a project. (Use `program` for ideation; `form-check/plan-new-app` for design.)
- **Debugging weird production behavior.** AI confidently generates plausible explanations that don't match reality. Use `diet §3` instead.
- **Anything where you can't verify the output.** If you can't tell whether the AI was right, the AI was not helpful. Find a way to verify *or* don't delegate.
- **Learning a new domain.** The AI's explanation might be wrong in ways you can't detect because you don't know the domain yet. Read a textbook / docs / talk to a person.

## §3. Prompting hygiene

### 3.1 The three-part prompt shape

A prompt that gets useful AI output usually has three parts:

1. **Context.** What's the codebase, what's the situation, what's been tried.
2. **Goal.** Specifically what you want, output format included.
3. **Constraints.** What to avoid, what to assume, what the rubric is.

Example (bad): "Write a function that parses CSV."

Example (better): "In a Python 3.11 project using only standard library, write a function `parse_csv(path: Path) -> list[dict]` that returns each row as a dict keyed by the header row. Skip blank lines. Raise `ValueError` with a clear message on malformed rows. No external dependencies."

The better version produces output you can verify (does the function match the signature? does it skip blank lines? does it raise on malformed?).

### 3.2 The verification list goes IN the prompt

Don't ask the AI to write the code, then mentally compose a separate checklist for verification. Ask the AI for the code *and* the test cases that would prove it correct. Then run the tests.

This produces two benefits: the AI generates code that *passes its own test cases* (smaller surface for hallucination), and you have the tests to verify against the spec (smaller surface for "AI passed wrong tests").

### 3.3 Iterate by narrowing, not by re-asking

When the AI's first output is wrong, the worst response is "no, do it again." That re-rolls the dice. The better response is "this part was right; this part was wrong; here's the specific change I want." This anchors the next output to the good parts.

### 3.4 Stop when you stop reading

If you've stopped reading the AI's diffs because they're "fine," you've stopped reviewing. This is the *perception–reality gap* (the same failure mode METR-2025 measured at n=16; the mechanism is the load-bearing finding, not the specific effect size). Three signals:

- You're approving each suggested diff in under 5 seconds.
- You've stopped writing self-explanation prompts (`form-check/learner/study_protocol.md` Habit 5).
- You couldn't write a test that would fail if the AI got the next answer wrong.

When you hit any of those: **stop the AI session, walk away for 10 minutes, come back and review the last 5 changes from scratch.** The AI's outputs feel uniformly competent; that's the illusion to fight.

## §4. Calibration applied to AI output

Per `form-check/learner/study_protocol.md` Habit 7: predict, measure, observe the gap.

Three concrete calibrations:

| Prediction | Measurement | Habit |
|---|---|---|
| "How confident am I that this AI code is correct (0–100)?" | Run it; run mutation testing; let it sit in prod for a week | Note the gap |
| "Will this AI-suggested package install cleanly?" | `npm install` / `pip install` and check for errors / verify it's the right package | Note the gap |
| "Will the AI's proposed refactor actually compile / pass tests on the first try?" | Run it | Note the gap |

The calibration on AI output is *harder* than on human output because AI's surface confidence is uniformly high. The gap you're training against is: "feels confident" vs. "is correct." Senior engineers carry a healthy "this seems too clean" instinct that beginners haven't developed yet, this is how you develop it.

## §5. The "AI suggested I do something destructive" protocol

When the AI suggests:

- `rm -rf` of anything you don't intend to delete
- `git push --force` or `git reset --hard` on any branch
- A database migration during an incident
- Disabling a security check, an auth check, or a test
- A library you've never heard of (especially with a generic name)
- Hardcoding a credential "for now"

**Stop.** Read the suggestion *out loud*. Read it *twice*. Ask yourself: "If I do this and it goes wrong, what's the recovery?" If the recovery isn't immediately obvious, don't execute. *Especially* don't execute because the AI sounded confident.

The asymmetric failure mode: AI is confidently wrong faster than you can verify. Your only defense is the protocol: read, pause, verify, *then* execute.

## §6. The AI session as an artifact

For non-trivial AI sessions (anything beyond a single isolated PR), keep the prompt history. Most tools do this automatically.

Why: when something breaks two weeks later, "what did I tell the AI to do?" is a useful question. The session log is the answer. Treat it like git history, version it, refer back to it, write commit messages that reference what was prompted.

Anti-pattern: deleting AI sessions to "tidy up." You're deleting the evidence trail.

## §7. Drift signs (you're becoming dependent)

Self-check every 30 days. If you can answer "yes" to two or more, recalibrate:

- I can't write the same code without the AI in a similar time, even when I know the domain.
- I've stopped reading the AI's diffs carefully because "it's usually right."
- I'm using the AI to *decide* (architecture, library choice) rather than to *execute*.
- I've shipped code I couldn't explain in detail to a colleague.
- I get anxious when the AI is unavailable for a session.
- My calibration log (per §4) shows AI predictions are getting *worse*, not better.

Drift is not a moral failing; it's a real cognitive pattern (the literature calls it *cognitive offloading*). The corrective is: do one substantial task per week *without* AI assistance. Maintain the underlying skill.

## §8. Composition with the rest of the ecosystem

| Situation | Skill |
|---|---|
| Vague AI idea, no plan | `program` |
| AI-generated change → review | `form-check` |
| AI-generated package import → verification | `form-check/learner/lessons/03_hallucination_check.md` |
| AI-generated destructive command → wait | This skill §5 |
| AI session for a whole project (multi-day) | `recovery` engagement, with this skill governing the *use* |
| AI session in production / incident | `diet §3` overrides; do not let AI drive incident response |
| AI-generated git commands | `safetybar`, read every git command with `--force`, `--hard`, `-D`, or `clean -f` before running |

## §9. Anti-patterns

- ❌ **Accepting an AI diff because it's small.** Hallucinated imports are small. BOLA bugs are small. Smallness is not a safety signal.
- ❌ **Asking the AI "is this code correct?"** The AI will say yes. AI self-evaluation of code correctness is unreliable (this is documented; not contested). Run the tests instead.
- ❌ **Using the AI to write code in a domain you don't understand at all.** You will not be able to detect the hallucinations because you have nothing to compare them against.
- ❌ **Using AI for git operations during an incident.** AI confidently generates `--force` commands. Read every git command in incident mode.
- ❌ **Letting the AI choose the library / framework.** Use `form-check/rubrics/stack_decision.md` for that, it encodes the boring-technology and forcing-constraint posture, which the AI does not.

## Provenance

This skill exists because AI assistants are now the dominant tool for the beginner persona, and the failure modes are well-documented but not assembled in one place. METR-2025 (the perception–reality gap, n=16, awaiting replication), USENIX 2025 slopsquatting, the Lovable BOLA incidents, the Replit/Lemkin destructive-action case, all map to specific points in the workflow this skill describes. Treat the named studies as illustrative of mechanisms rather than as load-bearing evidence; the mechanisms hold whether or not any individual study replicates.

The structural insight (§1. AI shifts work from writing to verifying) is the thesis; everything else is the application. If you take only one section, take §1.
