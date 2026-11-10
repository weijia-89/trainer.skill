# trainer.skill ROADMAP

**Current version:** v1.0.0 (2026-11-01)
**Status:** active development. Trainer routing logic plus eleven specialist
gym-family skills under `specialists/`.

## Shipped in v0.14.0

- Default **code review** loop (`references/trainer-autonomous-code-review.md`) with mechanical routing gate (Invariant 12) and anti-theater PR comment harness (Invariant 13).
- `trainer_pr_review_post.sh` PATCH-only canonical comment; strips duplicate HTML markers; deletes stray duplicates.
- User-facing docs gate (R-6): PRs that change operator prose run the full **deai** skill before merge.

## Done in the CHANGELOG drift CI wave (2026-11-09/PR #50)

- `scripts/check_changelog_drift.sh` with `tests/test_check_changelog_drift.sh`:
  when a diff touches `SKILL.md`, `scripts/`, or `tests/`, it must also touch
  `CHANGELOG.md`; otherwise CI fails with an operator-plain message that names
  the rule and lists every triggering path.
- Docs-only diffs are exempt (R-6) and may still update `CHANGELOG.md`.
- CI wiring: a separate `Check CHANGELOG drift` step in
  `.github/workflows/python-package-conda.yml`, after `bash -n` and before
  `verify_trainer_sync.sh` (D21 placement constraint, recorded in `context.md`).
  PR #50 also moved this workflow's checkout to `fetch-depth: 0`, which
  fetches full history so the base commit resolves.
- Base resolution fails closed: the step passes the PR base SHA (or the push
  `before` SHA) as `BASE_SHA`; an all-zero `before` SHA on a new branch counts
  as unset; an unresolvable base is a FAIL, never a silent pass. Local
  fallback: `git merge-base origin/main HEAD`, else `origin/main`.

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
- Offline synthesis gates (`scripts/verify_phase11_synthesis_gates.sh`) — WP-0..WP-5 mechanical completion.
- Implementation babysitter ref for ChatPRD plan-row execution.
- Layer C mutation heat map run (offline) — no load-bearing section drops at trainer N.

### Done in the model-agnostic adapter wave (2026-11-08)

- `scripts/harness_adapters/openai_compatible.py`: any OpenAI-compatible endpoint via stdlib urllib. No provider SDK, no new dependency. Dated-snapshot and missing-key fail-closed come from the shared `_repro` protocol.
- `scripts/harness_adapters/_common.py`: shared preamble, untrusted-data wrapper, skill-file prompt builder, and offline stub. `anthropic_opus.py` imports them now; its behavior stays the same.
- Adapter unit tests (`tests/harness_adapters/test_openai_compatible.py`) and the per-script smoke test (`tests/test_verify_phase11_synthesis_gates.py`).
- `verify_phase11_synthesis_gates.sh` carries OpenAI adapter coverage. It is the first strict-clean script in `scripts/` (8 pre-existing strict-gate warnings fixed).

### Done in the reference-pointer + CI wiring wave (2026-11-09)

- The three dead reference pointers become real files (QA-2 finding closed):
  `references/chatprd-opus-implementation-plan-gate.md`,
  `references/chatprd-plan-adversarial-template.md`,
  `references/trainer-phase-implementation-gate.md`. Content stays grounded in
  what `SKILL.md` and the babysitter reference already claim; no routing change.
- The OpenAI adapter unit suite runs inside `verify_trainer_sync.sh` (both
  blocks); the synthesis-gate smoke runs as its own CI workflow step.
  Placement constraint recorded in `context.md`: the gate's Gate 5 calls
  `verify_trainer_sync.sh`, so the smoke can never live inside that script
  without infinite recursion (the first wiring attempt hit exactly this).

### Deferred / operator-opt-in

- **Blind audit cycle.** Run the 3 trainer scenarios against a live dated model: Anthropic (`ANTHROPIC_MODEL` + `ANTHROPIC_API_KEY`) or any OpenAI-compatible endpoint (`OPENAI_BASE_URL` + `OPENAI_MODEL` + `OPENAI_API_KEY`). Indicative cost for an Opus-class run stays ~$3-5 per full k-repeat; other providers price lower. **Waived for offline synthesis close-out** - falsifiers remain in the `verify_phase11_synthesis_gates.sh` NOTE.
- **Cross-model run.** Same scenarios against a second provider for pass-rate delta. The OpenAI-compatible adapter makes cross-vendor runs possible. Harness-parity confound: keep load-bearing comparisons to like adapters.
- **Operator decision (2026-11-09): both live-run paths stay skipped.** The offline gates remain the shipped evidence layer. Skipped does not mean closed: the env contract stays valid if the operator reopens either later.
- ~~**Combined report driver for trainer-side scenarios.**~~ Shipped v0.15.0: `scripts/phase11_report.py`.

## Out of scope

- Public LLM-eval harness comparisons. Internal evidence first.
- Renaming the gym metaphor.
- Auto-routing decisions that lock the user out of the specialist
  manually.

## Open questions

- Whether to gate `git push` on `verify_trainer_sync.sh` by default
  (currently opt-in via `scripts/install_hooks.sh`).
