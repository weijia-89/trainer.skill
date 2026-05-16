# gymbuddy — AI trains alongside you; you still do the reps

A skill for using AI coding assistants well — when to ask, how to prompt, when not to delegate, and the calibration discipline applied to AI output.

## What it does

`gymbuddy` is the workflow lens for AI-assisted development. It does not generate code; it teaches the patterns that make AI-generated code safe to ship.

The organizing thesis (§1): AI shifts work from writing to verifying. Most beginner AI disasters come from doing the prompting but skipping the verifying. The skill exists to make that shift explicit and actionable.

Nine sections:

1. The writing-to-verifying shift (the organizing thesis)
2. When to use AI and when not (strong fit, caution fit, bad fit)
3. Prompting hygiene (three-part prompt shape, in-prompt verification, narrowing iteration)
4. Calibration applied to AI output (predict, measure, observe the gap)
5. The destructive-suggestion protocol (when the AI suggests `rm -rf`, `--force`, etc.)
6. The AI session as an artifact
7. Drift signs (you are becoming dependent)
8. Composition with the rest of the ecosystem
9. Anti-patterns

## When to invoke

- You are about to start an AI-assisted coding session and want to use it well.
- The AI just wrote something and you do not feel like reading it carefully.
- The AI suggested a destructive command.
- You are 30 days in to heavy AI use and want a drift check.

## When to skip

- You already use AI assistants effectively and the §7 drift signs do not apply to you.
- You are in an incident. `diet §3` overrides; do not let AI drive incident response.

## Composes with

- `form-check` — AI-generated code goes through the same rubric as human-generated code. This skill is the lens; `form-check` is the verifier.
- `form-check/learner/lessons/03_hallucination_check.md` — the canonical check for hallucinated package names.
- `diet §3` — overrides this skill during incidents.
- `safetybar` — every AI-suggested git command with `--force`, `--hard`, `-D`, or `clean -f` gets read here before execution.

## What this skill protects against

Four documented failure modes the literature has converged on:

- **METR-2025 perception-reality gap.** Experienced developers felt 20% faster with AI; they were 19% slower. The calibration habit in §4 is the corrective.
- **Slopsquatting (USENIX 2025).** Commercial models hallucinate package names at 5.2%; open-source models at 21.7%. The §3 prompting hygiene puts the verification list inside the prompt.
- **Lovable BOLA (2025-2026).** AI generates authentication but skips authorization. §2.2 names this as a caution-fit case and prescribes the cross-user test as the verification.
- **Replit/Lemkin July 2025.** AI suggested a destructive command; user ran it. §5 is the protocol that exists to prevent the same shape of failure.

## Files

- `SKILL.md` — the nine sections
- `CHANGELOG.md` — version history
- This file

## License

MIT.
