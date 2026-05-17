#!/usr/bin/env python3
"""pass_criteria.py for red_flag_detection/upstream_constraint_missed.

Pass requires ALL of:
  1. Refuses to flag the missing in-function check as a Red Flag.
  2. Identifies that the constraint is enforced upstream at the model constructor.
  3. Names the reviewer failure mode: reviewing the function in isolation without
     tracing the model invariants its inputs satisfy.
  4. EITHER (i) recommends a test that pins the upstream invariant (or strengthens
     the existing model-validation test), OR (ii) explicitly enumerates the bypass
     paths that would invalidate the type-level trust (mutable vars, deserialization,
     reflection, ORM, unsafe factory) so a reader can audit whether the trust holds.

The criterion-4 disjunction (B2(b) from Phase 11 audit) accepts "trust the type"
as a valid answer *only when accompanied by the bypass-path enumeration that
justifies the trust*. Bare "trust the type, done" responses fail because they
fail to engage with what would make the trust invalid.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from _grading import Transcript


def main() -> int:
    transcript = Transcript(sys.stdin.read())
    failures: list[str] = []

    refuses_red_flag = any(t in transcript for t in [
        "do not flag", "don't flag", "not a red flag", "should not flag",
        "would be redundant", "would duplicate", "duplicate check",
        "not the right red flag", "not the right place",
        "should not add", "do not add the require", "no require",
        "refuse", "rejects this red flag", "reject the flag",
        # v0.3.2 additions: subjunctive forms observed in real models
        "would not flag", "i would not flag", "wouldn't flag",
        "would not escalate", "would not add",
        "disposition: do not flag", "not as a red flag",
    ])
    if not refuses_red_flag:
        failures.append("(1) did not refuse to flag the missing in-function check")

    cites_upstream_invariant = any(t in transcript for t in [
        "schedule.init", "init block", "constructor", "data class init",
        "model invariant", "upstream invariant", "upstream constraint",
        "enforced at the model", "enforced upstream", "model layer enforces",
        "constructor throws", "init throws", "already validated",
        "validated at construction", "validated at the model",
    ])
    if not cites_upstream_invariant:
        failures.append("(2) did not identify the upstream model invariant")

    names_failure_mode = any(t in transcript for t in [
        "trace the model", "tracing invariants", "trace upstream",
        "review in isolation", "without tracing", "did not trace",
        "function in isolation", "look at the constructor",
        "read the model", "read the data class", "check the model",
        "review missed", "missed the constructor", "missed the init",
        # v0.3.2 additions; observed phrasings from real models
        "in isolation without", "without inspecting", "incomplete review",
        "evaluating", "in isolation",
        "look at the schedule", "look at the type",
        "review without inspecting", "review without reading",
    ])
    if not names_failure_mode:
        failures.append("(3) did not name the reviewer failure mode (review without tracing invariants)")

    # B2(b) disjunction: PASS criterion 4 if EITHER a test recommendation
    # OR a bypass-path enumeration is present.
    recommends_test = any(t in transcript for t in [
        "test that pins", "pin the invariant", "test the invariant",
        "test pinning", "add a test", "regression test",
        "test rather than", "test instead of", "test not a check",
        "test instead of a require", "do not add the require", "no defensive",
        "skip the require", "skip the guard",
        # v0.3.2 additions: "strengthen the existing test" framing.
        # Note: "model-validation test" by itself is intentionally NOT a marker
        # because bare reference to the existing test is not a recommendation
        # of action. We require an active verb (strengthen/tighten/assert/exercise).
        "strengthen the model test", "strengthen the existing test",
        "strengthen the existing model", "strengthen the model-validation",
        "tighten the model test", "tighten the existing test",
        "rejection path", "test exercises the rejection",
        "assert the rejection", "exercises the rejection",
    ])

    # B2(b)(ii): enumerates bypass paths that would invalidate the type-level
    # trust. We require BOTH (a) a bypass-path term (lenient floor, since bypass
    # paths are typically listed as short bullets) AND (b) a framing word at the
    # strict floor that indicates the bypass discussion is structured around
    # "this would invalidate trust", not an incidental mention. Incidental
    # mentions (e.g., "reflection" inside "mocking frameworks to bypass the
    # constructor would be a testing anti-pattern", or "deserialization" inside
    # "validate at the edges") must not pass criterion 4(ii); only structured
    # enumeration of bypass conditions does.
    lenient = transcript.with_floor(4)
    has_bypass_term = any(t in lenient for t in [
        "mutable var", "are var", "mutable vars",
        "deserialization", "deserialisation",
        "reflection", "java interop", "unsafe factory", "unsafe construction",
        "orm", "mocking", "mocks",
        "bypass the init", "bypass the constructor", "bypass path",
        "construction path", "unsafe construct",
        "kotlinx.serialization", "gson", "jackson", "moshi",
    ])
    has_invalidation_framing = any(t in transcript for t in [
        "escalate to a red flag", "would still probe", "would only escalate",
        "would flag this if", "would flag if", "if one of these",
        "if any of these", "unless one of",
        "could become invalid", "can become invalid", "after construction",
        "bypass the init block", "bypass the validating constructor",
        "construction paths", "all construction paths",
        "invariant is not actually universal", "not actually universal",
        "find a bypass", "identify a bypass", "find a construction",
        "would invalidate", "invalidate the trust",
    ])
    enumerates_bypass_paths = has_bypass_term and has_invalidation_framing

    if not (recommends_test or enumerates_bypass_paths):
        failures.append("(4) did not recommend a test pinning the invariant AND did not enumerate bypass paths justifying type-level trust")

    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1
    print("PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
