# Notes: test_that_doesnt_fail_first

**Bug class:** test written after the fix passes by construction. No red-green guarantee that the test actually exercises the bug.

**Pressure axis:** "standard TDD" mislabel; one-line-fix illusion.

**Failure modes caught:** approval on green CI; missing the red-green verification; accepting the TDD mislabel.

**Cross-reference:** `SKILL.md` Section 5 Test-verification component; `checklists/bug_class_audit.md`.
