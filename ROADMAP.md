# trainer.skill ROADMAP

**Current version:** v0.15.0 (2026-07-01)
**Status:** active development. Trainer routing logic plus nine specialist
gym-family skills bundled under `specialists/`.

## Shipped in v0.14.0

- Default **code review** loop (`references/trainer-autonomous-code-review.md`) with mechanical routing gate (Invariant 12) and anti-theater PR comment harness (Invariant 13).
- `trainer_pr_review_post.sh` PATCH-only canonical comment; strips duplicate HTML markers; deletes stray duplicates.
- User-facing docs gate (R-6): PRs that change operator prose run the full **deai** skill before merge.

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

### Done in v0.15.0 (Layer A driver — 2026-07-01)

- `scripts/run.sh` with `--k` pass-rate stability gate and RULE #4 isolation.
- `scripts/harness_adapters/anthropic_opus.py` (dated snapshot fails closed; USER-DATA fence).
- `scripts/phase11_report.py` (trainer pass-rate summary parser).
- `scripts/calibration_analyze.py` (Layer B honest-empty; no mSPRT).
- `scripts/mutation_test_skill.py` (Layer C tiny-N noise band).
- `scripts/verify_phase11_isolation.sh` + Invariants 15/16 in `verify_trainer_sync.sh`.
- README honest-scope updated: falsifiability suite, not measured delta.

### Deferred

- **Blind audit cycle.** Run the 3 trainer scenarios against a live dated Opus call (`ANTHROPIC_MODEL` + `ANTHROPIC_API_KEY`). Indicative cost ~$3-5 per full k-repeat run; unverified.
- **Cross-model run.** Same scenarios against a second vendor for
  pass-rate delta. Harness-parity confound: compare like adapters only.
- ~~**Combined report driver for trainer-side scenarios.**~~ Shipped v0.15.0: `scripts/phase11_report.py`.

## Out of scope

- Public LLM-eval harness comparisons. Internal evidence first.
- Renaming the gym metaphor.
- Auto-routing decisions that lock the user out of the specialist
  manually.

## Open questions

- Should the nine gym standalones get their own GitHub mirrors, or stay
  bundle-only? Currently the standalones at `$HOME/Projects/<name>.skill/`
  are local-only git repos.
- Whether to gate `git push` on `verify_trainer_sync.sh` by default
  (currently opt-in via `scripts/install_hooks.sh`).
- Mechanical CHANGELOG drift check in CI when `SKILL.md` or `scripts/` change without `CHANGELOG.md` update.
