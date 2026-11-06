# logbook

Per-project, append-only work ledger for the trainer ecosystem.

## What the logbook does

One project, one record. Every work slice lands as a set with a weight, a proof path, an outcome, and the next set on the bar. `verify` is the form check: a slice whose proof file is gone reports `EV_MISSING`, and a slice logged without proof reports `EV_UNVERIFIED`. Neither counts as progress.

The record is append-only. A missed slice is logged as missed, never deleted.

## When to load

- Work spans more than one session
- Resuming after a break: "what did I do last"
- Someone asks whether a thing was already tried
- A claim needs proof that the work happened
- Handing a session off, with the next slice named

## How it works

1. `init --objective TEXT` once per project (skips when the project already has a logbook)
2. `status` to read the state before working
3. `record slice --what ... --scope ... --evidence PATH` as each slice finishes
4. `record outcome --outcome logged|missed|pr --id ID` to tag it
5. `record next --what ...` before stopping, so the next session starts warm
6. `verify` before claiming progress

## Output cost

Default output stays proportional to the failures, not to the length of the log. On a clean log, `verify` prints one line (`EV_OK all N sets carry proof`); pass `--all` to list every set, which is the only mode whose cost grows with the log. `status` prints three lines. The generated `.workledger/ACTIVE_STATE.md` caps each field and shows the last ten sets, so its size does not grow with the project.

## Files

- `SKILL.md` - the specialist body (iron law, seven-step flow, failure modes, rules)
- `scripts/logbook.py` - the CLI, standard library only, no network
- `../../tests/logbook/test_logbook.py` - 31 unit tests
