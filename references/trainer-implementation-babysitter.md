# Trainer — implementation babysitter (ChatPRD plan rows)

**Canonical:** `/Users/dubs/Projects/trainer.skill/references/trainer-implementation-babysitter.md`

**When:** Cursor executes a merged ChatPRD implementation plan (Phase 11 WP rows, dual-lane `POST_SYNTHESIS_INDEX`, or vendor placement map).

**Pair with:** `/Users/dubs/Projects/piranesi.skill/references/cursor-composer-implementation-handoff.md` (H1–H7) and `trainer-autonomous-code-review.md` (verify loops).

---

## Per-row gate (iron law)

Before marking any plan row **done**:

1. **READ** — whole target file(s); paste proof lines from edit region (H1).
2. **EDIT** — anchor by literal string, not line numbers (H2).
3. **RUN** — row falsifier command; paste stdout (H3). Self-reported PASS without output = FAIL.
4. **CAP** — max 3 attempts per row; then STOP and report (H4).
5. **SCOPE** — one work package per fresh session (H5).
6. **SHELL** — `bash -n` before executing new shell scripts (H6).
7. **ISOLATE** — harness runs must not mutate prod tree (RULE #4 / `verify_phase11_isolation.sh`) (H7).

---

## Trainer routing per row type

| Row kind | Load before edit | Verify after edit |
|----------|------------------|-------------------|
| Code / scripts | `form-check` stakes tier + surrounding files | Repo `verify_*` + row falsifier |
| Operator prose | **deai** full skill (R-6) | `verify_trainer_sync.sh` Inv 6 + `trainer_pr_r6_validate.py` on PRs |
| Harness / scenarios | Never edit `pass_criteria.py` to greenwash | Invariant 15 self-pass + `run.sh` |
| PR ship | `trainer-codereview.md` + autonomous loop | `verify_trainer_codereview.sh` |

---

## Phase 11 synthesis gates (offline)

```bash
bash /Users/dubs/Projects/trainer.skill/scripts/verify_phase11_synthesis_gates.sh
```

Live blind audit (`run.sh --k 3` without `--offline`) is **operator-opt-in** — requires dated `ANTHROPIC_MODEL` + `ANTHROPIC_API_KEY`. Offline gates satisfy WP-0..WP-5 mechanical completion.

---

## Forbidden

- Claiming a WP gate PASS without pasted falsifier stdout.
- Editing `pass_criteria.py` or reference responses to fake Inv 15.
- Skipping `verify_trainer_sync.sh` before merge.
- Merging README behavioral-delta claims when rollback triggers fire (see synthesis plan §I T5.1).
