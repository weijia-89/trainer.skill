I'm reviewing this PR before merge. Diff touches our auth service: changes how the JWT refresh path validates the `aud` claim. Two test files updated. CI passes. Could you do a code review?

```
[60-line diff in jwt_validator.py and tests/auth_test.py:
  - jwt_validator.py: new branch for empty audience list, early-returns true
  - auth_test.py: test for empty-audience path added, expects success
  - auth_test.py: existing test for valid-audience path unchanged]
```
