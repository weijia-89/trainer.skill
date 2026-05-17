# trainer.skill ROADMAP

**Current version:** v0.5.0 (2026-05-16)
**Status:** active development. Trainer routing logic plus eight specialist
gym-family skills (form-check, recovery, gymbuddy, safetybar, diet, pr,
program, warmup) bundled under `specialists/`.

## Phase 11 (empirical validation infrastructure)

The trainer routing logic and the gym specialists need evidence behind
their behavior claims. Phase 11 is building that evidence layer.

### Done in v0.5.0

- Three trainer-specific scenarios converted from doc-only to the full
  pressure-scenario harness (`tests/scenarios/harness/`).
- Soft cap on `SKILL.md` raised to 180 lines to fit the Red Flags and
  Rationalizations sections added in v0.4.0.
- License posture clarified: trainer itself ships under PolyForm
  Noncommercial + Iron Law Addendum; the eight bundled specialists revert
  to MIT.
- Eight verification invariants in `scripts/verify_trainer_sync.sh`,
  including the private-path leak scanner added 2026-05-16.

### Deferred to v0.6.0

- **Blind audit cycle.** Run all 37 pressure scenarios (34 form-check + 3
  trainer) against a live Anthropic Opus call. Needs an `ANTHROPIC_API_KEY`
  and roughly $3-5 per full run.
- **Cross-model run.** Same scenarios against a second vendor for
  pass-rate delta. Surfaces whether a scenario tests skill behavior or
  model behavior.
- **Combined report driver for trainer-side scenarios.** form-check.skill
  has `scripts/phase11_report.py`; trainer needs the equivalent.

## Out of scope

- Public LLM-eval harness comparisons. Internal evidence first.
- Renaming the gym metaphor.
- Auto-routing decisions that lock the user out of the specialist
  manually.

## Open questions

- Should the eight gym standalones get their own GitHub mirrors, or stay
  bundle-only? Currently the standalones at `$HOME/Projects/<name>.skill/`
  are local-only git repos.
- Whether to gate `git push` on `verify_trainer_sync.sh` by default
  (currently opt-in via `scripts/install_hooks.sh`).
