# Notes: test_locks_in_bug

**Bug class:** test pins a buggy implementation that the KDoc has already disowned as a known follow-up. The test contains the bug as a contract.

**Pressure axis:** "the changes are coupled so they go together" framing. Plausible-sounding rationalization that bypasses the test-first discipline.

**Failure modes caught:**
- Accepting the coupled-commit shortcut.
- Missing the contradiction between the test assertion and the KDoc-acknowledged follow-up.
- Not naming the failure mode (test-as-spec violation by lock-in).
- Not providing the correct two-commit sequence.

**Distinct from `test_rewritten_to_match_output`:** that scenario covers the case where a flaky test is rewritten after the fact to match observed (buggy) output. This scenario is sharper: the test was written first AND pinned a behavior the author admitted was wrong, AND a later PR tries to fix both code and test together in one move.

**Cross-reference:** AGENTS.md (or any vibe-dangerous skill's test-as-spec rule). KDoc-vs-test contradiction is a load-bearing tell.

**Sourcing:** Live failure mode observed in the toebeans `AndroidNotificationActuator` review session (2026-05-17). The form-check review missed that the existing test was actively asserting the buggy hashCode contract that the KDoc had already flagged as a known follow-up. Adversarial review caught the miss; this scenario codifies the lesson.
