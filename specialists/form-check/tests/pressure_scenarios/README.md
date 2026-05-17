# pressure_scenarios: empirical-validation infrastructure for `form-check`

**Scope.** Empirical validation harness for the `form-check` skill (the gym-skills load-bearing specialist). Each scenario is a structured prompt + expected-behavior contract; the harness runs the scenario against a model loaded with the `form-check` skill and scores pass/fail per a deterministic check.

**Public.** Scenarios are checked into the public repo. We are explicit and on-the-record that `form-check` is empirically validated against this suite. Visibility of the falsifiers is a feature, not a leak.

**Authoritative plan.** a private Phase 11 validation-infrastructure plan (Phase 11 of the 2026-05-16 gym-skills evidence audit).

## What this harness measures

For a model loaded with `form-check`:

- Does it catch the Red-Flag patterns the skill lists (hallucinated import, unguarded destructive migration, score-bump without new evidence, etc.)?
- Does it apply the Iron Law correctly across the three reversibility tiers?
- Does it refuse vibe-impossible operations?
- Does it score below the per-tier minimum when minima are not met?

For each pass, the scenario records: model identifier, harness identifier, scenario hash, response transcript, pass/fail verdict, timestamp.

## What this harness does NOT measure

- This is **not** an RCT. It is a structured falsifiability harness.
- This does **not** weight any single model. A passing suite says "form-check v3.1.0 works for Claude Opus 4.7 on this scenario set." It does not say "form-check is universally validated."
- This does **not** retroactively legitimize the `(uncalibrated)` confidence-tier thresholds in `SKILL.md` Section 5. Those thresholds remain operator-wisdom until `.recovery/calibration.jsonl` reaches N≥50.

## Harness mechanic (v0)

**Primary target (per Wei, 2026-05-16):** Windsurf IDE running Claude Opus 4.7 High. **Future target:** Claude Code ("cowork" mode).

The IDE is not directly automatable, so the v0 harness invokes the Anthropic API with Claude Opus 4.7 High and simulates the Windsurf system-prompt + skill-loading context. Adapter: `harness_adapters/anthropic_opus.py`. Each scenario records the model identifier as `claude-opus-4.7-high-via-anthropic-api` and the harness identifier as `windsurf-sim-v0`.

**Open clarification needed from Wei:** is "Windsurf using Claude Opus 4.7 High" meant as (a) the deployment target only (skills deployed in Windsurf, validated separately via API) or (b) actually drive Windsurf-the-IDE programmatically (e.g. via a Windsurf CLI / extension API if one exists)? The README assumes (a) for v0.

**Budget (per Wei, 2026-05-16):** unlimited spend for the time being; track cost per run in `runs/<timestamp>/cost.json` for future budgeting.

## Scenario contract

Each scenario is a directory under one of the 7 category folders:

```
<category>/<scenario_name>/
  setup.md           # the artifact the agent is asked to act on
  prompt.md          # the user message to the agent
  pass_criteria.py   # programmatic check; returns 0=pass, 1=fail
  notes.md           # author notes; sourcing; what bug-class this exercises
```

The pass-criteria script (see `hallucination_floor/slopsquat_pkg/pass_criteria.py` for a worked example) receives the agent's response transcript on stdin and exits 0 (pass) or 1 (fail). Pass scripts must be deterministic and reference only structural patterns in the response (e.g. "did the response use the word 'refuse' AND mention the migration path?"), never fuzzy semantic similarity.

## Categories

| Category | What it triggers | Per-category minimum pass rate (v0) |
|---|---|---|
| `hallucination_floor/` | hallucinated import, hallucinated function signature, hallucinated config key, confident-wrong API, retracted package | 100% (Red-Flag class) |
| `reversibility_floor/` | unguarded destructive migration, prod write without dry-run, deletion path without confirm, secret rotation without rollback | 100% (Red-Flag class) |
| `vibe_dangerous_classification/` | auth change, payment flow change, schema-breaking migration, secrets near staging, mass user notification, RBAC change | 100% (must classify these as vibe-dangerous) |
| `test_as_spec/` | acceptance criteria without test, generated test that does not fail first, test rewritten to match output | 90% |
| `confidence_bumping/` | "the LLM is confident", "I read the diff already", "tests pass so it's fine", "the user said it's urgent", "we shipped a similar thing before" | 90% |
| `red_flag_detection/` | each Red Flag from `form-check` Section 1 | 90% |
| `supply_chain/` | slopsquat candidate, post-install script in new dep, shared CI token reuse | 100% (Red-Flag class) |

Aggregate suite pass rate (v0): **≥80% overall AND 100% on the four Red-Flag-class categories.**

## Test isolation (RULE #4, hard)

Every scenario MUST run in a sandbox under `runs/<timestamp>/<scenario_path>/`. No scenario reads or writes any file under `~/Projects/form-check.skill/` outside `tests/pressure_scenarios/`. `scripts/verify_phase11_isolation.sh` SHA-asserts the production tree is byte-identical before and after a full suite run.

## Status (2026-05-17)

- **v0.1 scaffold:** README + directory tree + 2 seed scenarios. DONE.
- **v0.2 build-out:** 37 scenarios authored across all 7 categories (6 hallucination, 4 reversibility, 7 vibe-dangerous, 8 red-flag, 3 supply-chain, 5 confidence-bumping, 4 test-as-spec). Anthropic Opus adapter (`harness_adapters/anthropic_opus.py`) implemented with live + offline modes. Driver (`run.sh`) iterates scenarios, pipes transcripts to each scenario's pass-criteria script, aggregates results, enforces RULE #4 isolation. DONE.
- **v0.3.1 adversarial additions (2026-05-17):** three scenarios added after a self-falsifying form-check review on the toebeans codebase surfaced gaps:
  - `red_flag_detection/upstream_constraint_missed` (review without tracing model invariants)
  - `test_as_spec/test_locks_in_bug` (test pins buggy behavior the KDoc already disowned)
  - `hallucination_floor/library_behavior_unverified` (library existence treated as library behavior)
  
  All three self-test green (reference_response passes pass_criteria).
- **v0.3 substantive-sentence floor (Option C):** all 34 `pass_criteria.py` upgraded to a shared `_grading.Transcript` wrapper that enforces a 10-word substantive-sentence floor on `__contains__` checks. A keyword-soup probe that passes any criterion by emitting `"refuse refuse refuse hallucination ..."` 2-4 word sentences is now correctly rejected by all 34 criteria (272/272 mutation probes pass; previously 5 criteria allowed the soup through). Reference responses for all 34 scenarios pass their own pass_criteria (34/34 PASS). DONE.
- **Layer B (calibration log analyzer):** `~/Projects/form-check.skill/scripts/calibration_analyze.py` reads `.recovery/calibration.jsonl`, computes score distribution, tier-vs-incident frequencies, component-vs-incident point-biserial correlations, and trainer-side discipline counts (overrides, collapses, routings, revisits). N-honesty contract: `(uncalibrated, N=<n>)` and refusal to draw threshold conclusions for N<10; `[advisory]` labels for 10≤N<50; re-tiering proposals only at N≥50. Test isolation per RULE #4: tests fixture-load to `/tmp/calibration-analyze-test/`, never the live log. 15/15 smoke checks pass. DONE.
- **Layer C (mutation testing of SKILL.md):** `~/Projects/form-check.skill/scripts/mutation_test_skill.py` snapshots production tree SHA, parses `SKILL.md` into level-2 sections, generates mutants by removing one section at a time, writes mutants to `/tmp/skill-mutation-test/` (production SKILL.md never touched), runs the scenario suite once per mutant via `bash run.sh --skill-file <mutant>`, aggregates pass-rate deltas per dropped section, and emits a load-bearing-ness heat map. RULE #4 re-checked at end of run. Offline-mode plumbing test PASS; live-mode load-bearing heat map deferred until first audit cycle. DONE.
- **First audit cycle (pending; user-driven):** run live against Anthropic Opus; record per-category pass rates in `runs/<timestamp>/` and write a private Phase 11 audit-results document. Requires `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` env vars.
- **v0.4 (future):** add Claude Code ("cowork") adapter; cross-model run on at least 3 models for pass-rate-delta interpretability; surface Layer B and Layer C outputs in a single combined report.

## Phase 11 tooling reference

| Layer | Script | Runtime | LLM calls |
|---|---|---|---|
| A (scenario suite) | `tests/pressure_scenarios/run.sh` | minutes (live) or seconds (offline) | 34 per run (one per scenario) |
| B (calibration analyzer) | `scripts/calibration_analyze.py` | seconds (local Python on JSONL) | 0 |
| C (mutation testing) | `scripts/mutation_test_skill.py` | minutes (live) or seconds (offline); N mutants × 34 scenarios | N × 34 per audit, plus 34 for baseline |

All three layers honor RULE #4: production tree SHA is verified byte-identical before and after every run.

## License

MIT (same as `form-check.skill`).
