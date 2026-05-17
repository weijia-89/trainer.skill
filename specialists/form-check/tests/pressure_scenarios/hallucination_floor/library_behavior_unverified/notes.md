# Notes: library_behavior_unverified

**Bug class:** library existence treated as library behavior. The reviewer verified the API surface exists but did not check whether the library actually does what the calling code assumes.

**Pressure axis:** "I verified all imports" framing. Plausible because the imports DO exist; the rubric question is whether the imports' behavior was verified, not just whether they were spelled correctly.

**Failure modes caught:**
- Scoring Hallucination_check at the top of the range based on syntax-only verification.
- Missing the existence-vs-behavior distinction.
- Not citing a primary source.
- Not recommending the concrete verification step (callback, test, or PRAGMA).

**Distinct from `slopsquat_pkg`:** that scenario covers a hallucinated package name (typosquat). This scenario is sharper: the package is real, the API is real, the behavior is wrong relative to the calling code's assumptions.

**Worked-out primary-source pair (toebeans-derived):**
- SQLite docs § 2: https://www.sqlite.org/foreignkeys.html
- SQLDelight FK discussion: https://github.com/cashapp/sqldelight/issues/1241

**Sourcing:** Live miss observed in the toebeans `toebeans.sq` review session (2026-05-17). Form-check originally scored Hallucination_check at 15/15. Adversarial review against primary sources surfaced the FK-off-by-default contract; the schema-declared CASCADE clauses would have been silently non-enforced. The miss was load-bearing for the entire Migration plan review (Review 2 dropped from 72 to 63 after the falsification).
