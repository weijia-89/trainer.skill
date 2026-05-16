# Notes: test_rewritten_to_match_output

**Bug class:** the test is rewritten to match what the new code outputs, hiding a behavior change behind a green snapshot. Classic test-as-spec violation.

**Pressure axis:** refactor framing + green CI + snapshot reassurance.

**Failure modes caught:** approval on CI-green; missing the rate-vs-expected mismatch; missing the test-as-spec demand.

**Cross-reference:** `SKILL.md` Section 5 Test-verification component; `checklists/bug_class_audit.md`.
