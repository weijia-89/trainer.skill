# Pressure scenarios for the trainer skill

Each scenario is a structured prompt + expected-behavior contract designed to put the trainer under empirical pressure. Per the Phase 11 plan at `~/Projects/reviews/PHASE_11_VALIDATION_INFRA_PLAN_2026-05-16.md`:

> A scenario specifies setup (the artifact the agent is asked to act on), forcing function (which Iron Law / Red Flag / Rationalization the scenario is designed to trigger), pass criteria (what the agent must do), fail criteria (what counts as the rationalization winning), and trapdoor (the embedded "wrong-but-tempting" path).

These scenarios are documentation-grade for v0.4.0. A runnable harness that submits them to an agent and parses behavior comes later (Phase 11 implementation).

## Scenario index

| ID | Title | Forcing function | Status |
|---|---|---|---|
| `S01_ceremonial_routing` | Agent names form-check without reading it | Iron Law clause 1 + Red Flag "I named the specialist; that counts as invoking it" | doc-only |
| `S02_coaching_collapse_on_i_know` | Agent treats "I know" as demonstrated understanding | Defer-clause + Red Flag "User said 'I know'; I'll defer" | doc-only |
| `S03_bypass_for_small_task` | Agent skips trainer for a "small" CSS tweak that touches auth | Iron Law clause 1 + Red Flag "User said it's small / urgent, so we'll skip" | doc-only |

## How to use these scenarios manually

Until the harness exists, the test is a human-in-the-loop one:

1. Open a fresh agent session with `trainer.skill` loaded.
2. Paste the scenario's **Setup** as the user message.
3. Observe the agent's response.
4. Compare against **Pass criteria** and **Fail criteria**.
5. If the agent took the **Trapdoor**, log a `coaching_collapse` event in the calibration log per `form-check.skill/.recovery/SCHEMA.md`.

## Pass/fail mapping to the SKILL.md

Each scenario references a specific clause in the trainer `SKILL.md`. If a scenario fails, the SKILL.md clause is unenforced and needs tightening, or the trainer's load-bearing claims are theater for that pattern.
