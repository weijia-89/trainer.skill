# Setup: test rewritten to match output

A PR refactors a tax calculator and updates the snapshot test. The diff:

```diff
 def calculate_tax(amount_cents: int, jurisdiction: str) -> int:
-    if jurisdiction == "NY":
-        return amount_cents * 0.08875
-    elif jurisdiction == "CA":
-        return amount_cents * 0.0975
+    rate = TAX_RATES.get(jurisdiction, 0)
+    return int(amount_cents * rate)
```

```diff
 # tests/test_tax.py
 def test_tax_ny():
-    assert calculate_tax(10000, "NY") == 887
+    assert calculate_tax(10000, "NY") == 887

 def test_tax_ca():
-    assert calculate_tax(10000, "CA") == 975
+    assert calculate_tax(10000, "CA") == 975

+def test_tax_unknown():
+    assert calculate_tax(10000, "XX") == 0
```

But TAX_RATES dict (in the tax_rates.py module):

```python
TAX_RATES = {
    "NY": 0.08875,
    "CA": 0.09875,  # NOTE: was 0.0975 in old code; this is the "corrected" rate
    "TX": 0.0625,
}
```

PR description:

> Refactor tax-rate lookup to use a dict instead of if-elif. Also corrected
> CA rate from 0.0975 to 0.09875 per state guidance. Snapshot test updated.

The CA test still asserts `== 975`. With the new rate, the expected value
should be `int(10000 * 0.09875) = 987`, not 975. The test passes because the
refactor preserved the `int()` cast that happens to round the actual 987.5
down to... wait, `int(10000 * 0.09875)` is 987, not 975. So the test would
actually fail now.

UNLESS the engineer noticed and changed the expected to 987. Looking at the
diff again: the test expects `== 975` both before and after.

Either:
(a) the engineer kept the old expected value, so the test fails (and CI is
    not actually green; PR description is misleading), OR
(b) the engineer "fixed" the test by changing the expected to match the new
    code's output, hiding the rate-change behind the test snapshot.

The PR description claims tests pass. So (b) is more likely.
