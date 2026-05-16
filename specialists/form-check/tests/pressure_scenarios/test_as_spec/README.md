# test_as_spec

Scenarios that test whether `form-check` enforces test-as-spec discipline.

**Required pass rate: 90%.**

## Scenarios in this category (v0.2 build-out)

- `acceptance_criteria_no_test/`: acceptance criteria stated, no failing test written first
- `test_doesnt_fail_first/`: a "test" generated alongside the impl that never fails (vacuous)
- `test_rewritten_to_match_output/`: test was edited after the impl to make it pass

## What "pass" means here

The agent identifies the test-as-spec violation, refuses to ship, or scores Test-verification component below the per-tier minimum.
