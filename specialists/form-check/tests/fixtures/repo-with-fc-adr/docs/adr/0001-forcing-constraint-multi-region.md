# 0001 — Forcing Constraint: Multi-Region for Regulatory Audit

- Status: accepted
- Type: forcing-constraint
- constraint_class: regulatory
- Date: 2026-04-01

## 1. The constraint

EU customer contract signed 2026-03-15 requires data-residency in EU + cross-region failover SLA of 99.95% per quarter. Specific regulator: ENISA-aligned audit by 2026-09-30.

## 2. Default-mode alternative considered

Single-region in `eu-west-1`. Fails the cross-region failover SLA — a single-region availability zone failure exceeds the budget.

## 3. Chosen scale-up path

Active-passive across `eu-west-1` and `eu-west-2`. Activates `scale-up/multi_region.md` chapter for implementation guidance.

## 4. Cost projection

| Dimension | Default | Scale-up | Multiplier |
|---|---|---|---|
| Compute | $X/mo | $1.7X/mo | 1.7× |
| Network | $Y/mo | $1.3Y/mo | 1.3× |

## 5. Consequences

- ✅ Meets contract SLA
- ⚠ Operational tax: ~0.5 FTE for failover game-days

## 6. Confirmation

In 90 days: failover game-day passes; SLA report green.

## 7. Sunset

Re-evaluate if customer contract terminated or amended.
