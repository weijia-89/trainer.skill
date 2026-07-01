# Pressure scenarios for the trainer skill

Each scenario is a structured prompt + expected-behavior contract designed to put the trainer under empirical pressure. Per the Phase 11 plan at a private Phase 11 validation-infrastructure plan:

> A scenario specifies setup (the artifact the agent is asked to act on), forcing function (which Iron Law / Red Flag / Rationalization the scenario is designed to trigger), pass criteria (what the agent must do), fail criteria (what counts as the rationalization winning), and trapdoor (the embedded "wrong-but-tempting" path).

These scenarios are runnable via `bash scripts/run.sh` (offline or live adapter). Layer A harness shape ships in-repo; blind audit and Layer B/C are operator-driven follow-ups.

## Scenario index

| ID | Title | Forcing function | Status |
|---|---|---|---|
| `S01_ceremonial_routing` | Agent names form-check without reading it | Iron Law clause 1 + Red Flag "I named the specialist; that counts as invoking it" | harness + pass_criteria |
| `S02_coaching_collapse_on_i_know` | Agent treats "I know" as demonstrated understanding | Defer-clause + Red Flag "User said 'I know'; I'll defer" | harness + pass_criteria |
| `S03_bypass_for_small_task` | Agent skips trainer for a "small" CSS tweak that touches auth | Iron Law clause 1 + Red Flag "User said it's small / urgent, so we'll skip" | harness + pass_criteria |

## How to run the harness

```bash
bash scripts/run.sh --offline --k 3          # deterministic stub; scenarios FAIL by design
ANTHROPIC_MODEL=claude-opus-4-5-YYYYMMDD ANTHROPIC_API_KEY=... bash scripts/run.sh --k 3
python3 scripts/phase11_report.py --stdout
```

Manual human-in-the-loop review (optional):

1. Open a fresh agent session with `trainer.skill` loaded.
2. Paste the scenario's **Setup** as the user message.
3. Observe the agent's response.
4. Compare against **Pass criteria** and **Fail criteria**.
5. If the agent took the **Trapdoor**, log a `coaching_collapse` event in the calibration log per `form-check.skill/.recovery/SCHEMA.md`.

## Pass/fail mapping to the SKILL.md

Each scenario references a specific clause in the trainer `SKILL.md`. If a scenario fails, the SKILL.md clause is unenforced and needs tightening, or the trainer's load-bearing claims are theater for that pattern.
