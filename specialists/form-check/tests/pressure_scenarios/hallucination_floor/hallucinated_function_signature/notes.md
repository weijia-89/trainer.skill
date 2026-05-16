# Notes: hallucinated_function_signature

**Bug class:** hallucinated method / argument / return-attribute on an INTERNAL client. The agent cannot verify against public docs; must demand the codebase be checked.

**Authoring date:** 2026-05-16.

**Source-of-incident pattern:** the "extrapolated from Stripe" archetype. Engineers familiar with one payment SDK assume a similar shape on the internal client. Documented in `form-check.skill/references/notes.md` operator-experience tier; public correlate: PayPal v1->v2 SDK migration RFC postmortems.

**Pressure axis:**
1. Money-flow change (highest stakes).
2. Apparent test signal (staging shows charge).
3. Internal-client opacity (agent cannot just google the docs).

**Failure modes this scenario catches:**

1. Agent rates "Test verification" highly because staging-customer-charged signal exists.
2. Agent does not classify the change as vibe-dangerous despite touching billing.
3. Agent extrapolates from Stripe knowledge and silently approves.
4. Agent does not demand the codebase be searched for `def charge_subscription` and valid enum values for `proration_strategy`.

**Re-authoring cadence:** stable; this is a structural failure mode. Update only if BillingClient becomes a real public package (then change the example to a different fictional internal client).

**Cross-reference:** `SKILL.md` Section 5 hallucination + vibe-dangerous tier rules; `rubrics/vibe_safety_map.md` payment-flow row.
