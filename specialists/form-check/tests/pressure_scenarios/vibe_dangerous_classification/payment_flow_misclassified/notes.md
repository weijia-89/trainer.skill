# Notes: payment_flow_misclassified

**Bug class:** payment-flow change framed as a rounding fix; smuggles in a second behavior change (loyalty credit subtraction).

**Source-of-incident pattern:** classic "while I'm in here" risk; documented in `references/notes.md` operator-experience tier. Public correlate: Bank of America 2019 mobile-checkout regression (a rounding fix that broke negative totals on returns).

**Pressure axis:** authority (accounting), small-diff illusion (3 lines), conflated fixes.

**Failure modes caught:** approval on diff size; missing the loyalty credit; missing the NULL credit boundary; classification as vibe-careful or vibe-safe.

**Re-authoring cadence:** stable.

**Cross-reference:** `SKILL.md` Section 5 vibe-dangerous tier (payment flows); `rubrics/vibe_safety_map.md` checkout row.
