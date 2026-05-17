# program, vague idea → scoped spec; the plan before the work

A pre-build skill that turns a vague idea into a scoped one-page spec you can actually start executing on.

## What it does

You have an idea. It is too big, too vague, or too vague and too big. `program` runs a four-question intake on it and produces a one-page spec that hands off to `form-check/plan-new-app`.

The four questions:

1. What is the one sentence?
2. Who is the first user?
3. What is the kill criterion?
4. What are the three deliberate non-goals?

The output is a one-page spec template covering the project's name, one-sentence statement, first user, MVP definition, acceptance criteria, kill criteria, deliberate non-goals, first three concrete tasks, and a timebox.

## When to invoke

- You want to build something but cannot describe it in one sentence.
- You have a side project that keeps growing features and never ships.
- You are three months into a project and no longer sure what you are building.
- Your spec is longer than one page.

## When to skip

- You already have a scoped spec. Go directly to `form-check/plan-new-app`.
- You want to refactor or rewrite existing code. That is `form-check/refactor-prep`, not `program`.
- You are pre-ideation and just brainstorming. Use a notes app or a conversation first; come back here when you have something concrete enough for the four questions.

## Composes with

- `form-check`, receives the scoped spec produced by this skill and walks it through the `plan-new-app` engagement (stack decision, ADRs, preflight 10 questions).

## What this skill protects against

The most common beginner project-death pattern: spending 100 hours on a project that was always going to fail, because there was no kill criterion to surface that fact at hour 10. The kill criteria in the spec template are the forcing function. They are not pessimism; they are calibration. The spec also includes deliberate non-goals, the features you commit to *not* building, which fight scope creep the way kill criteria fight sunk cost.

## Files

- `SKILL.md`, the four questions, the spec template, anti-patterns
- `CHANGELOG.md`, version history
- This file

## License

MIT.
