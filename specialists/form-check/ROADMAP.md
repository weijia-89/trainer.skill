# form-check.skill ROADMAP

**Current version:** v0.4.0 (Phase 11 infrastructure track v0.3)
**Status:** pilot for the Phase 11 empirical validation work. The skill
content is stable; the validation tooling is the active surface.

## Phase 11 layers

| layer | what it measures | tool | state |
|---|---|---|---|
| A | per-scenario pass/fail under adversarial prompts | `tests/pressure_scenarios/run.sh` + per-scenario `pass_criteria.py` | green; 32 of 34 scenarios PASS on the self-test baseline |
| B | calibration log honesty (N-honesty rules) | `scripts/calibration_analyze.py` | green; smoke-tested |
| C | section-level load-bearing-ness of the skill text | `scripts/mutation_test_skill.py` | green; offline plumbing verified |
| combined | one-view dashboard across A+B+C | `scripts/phase11_report.py` | green |

## Near-term (next minor)

- Run a real blind audit cycle once `ANTHROPIC_API_KEY` is in place.
  Target: 34 scenarios against live Opus, log per-call cost, compare to
  the reference-response distribution.
- Investigate the two self-test FAILs:
  `confidence_bumping/tests_pass_so_fine` and
  `red_flag_detection/prompt_injection_in_input`. Both look like prompt
  framing tuning, not skill-content defects.
- Make the Layer C mutation generator support per-rule mutants in
  addition to per-section.

## Mid-term

- Cross-model pass-rate delta (Anthropic Opus vs. Gemini 2.5 vs. GPT-5).
  Same scenarios, different vendor; the delta is the interpretability.
- Promote the substantive-sentence floor (Option C) from a `pass_criteria`
  helper into a documented contract any future skill harness can adopt.
- Wire Layer B real calibration data once `.recovery/calibration.jsonl`
  has at least 50 score events.

## Out of scope

- LLM-eval benchmark integration. The pressure scenarios are bespoke; the
  point is skill-specific evidence, not generic benchmarks.
- Auto-fix proposals from the harness. Pressure scenarios surface
  failures; the human fixes the skill text.

## Open questions

- Whether to publish the pressure-scenario corpus as a standalone artifact
  or keep it co-located with the skill.
- How aggressive to be about the substantive-sentence threshold; 10 words
  is the current floor, but some categories may need a higher bar.
