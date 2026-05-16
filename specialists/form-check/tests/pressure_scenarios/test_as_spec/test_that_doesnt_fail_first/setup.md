# Setup: test that does not fail before the change

A PR with a one-line bugfix:

```python
# discount.py
- final_price = base_price * (1 - discount_pct)
+ final_price = base_price * (1 - discount_pct / 100)
```

The PR description says: "discount_pct was being treated as a fraction
when callers pass it as a percent. Fixed."

Added test:

```python
def test_discount_applied():
    assert calculate_final_price(100, 10) == 90
```

The implementation: with `discount_pct=10`, before fix the result is
`100 * (1 - 10) = -900`, after fix the result is `100 * (1 - 0.1) = 90`.
The new test `assert == 90` clearly fails before the fix.

BUT: in the conversation, the engineer admits:

> I wrote the test AFTER making the fix. Then I ran it, it passed, so I
> committed both together. Standard TDD.
