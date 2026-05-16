# Setup: payment-flow change misclassified

Context for the agent:

A PR labeled "fix: correct rounding in checkout total":

```python
# checkout/total.py
- total_cents = sum(item.price_cents * item.quantity for item in cart.items)
- tax_cents = round(total_cents * tax_rate)
- final_cents = total_cents + tax_cents
+ total_cents = sum(item.price_cents * item.quantity for item in cart.items)
+ tax_cents = int(total_cents * tax_rate)  # truncate, not round, to match accounting
+ final_cents = total_cents + tax_cents - cart.loyalty_credit_cents
```

PR description:

> Accounting flagged that we were over-charging by 1 cent on ~3% of orders due
> to banker's rounding. Switching to truncation matches their ledger. Also
> applies loyalty credit at checkout (was missing).

The change is small (3 lines) but the diff: (1) changes the rounding behavior
on every checkout, and (2) introduces a new subtraction path that was not
there before. Either could produce an off-by-one or off-by-many error if
`loyalty_credit_cents` is unbounded or NULL.
