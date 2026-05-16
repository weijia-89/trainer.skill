---
name: forcing_constraint_adr_template
version: 2.0.0
parent_skill: form-check
gate_for: scale-up/*
---

# Forcing-Constraint ADR — template

Use this template to document a **forcing constraint** that activates a `scale-up/` chapter. Save as `docs/adr/NNNN-forcing-constraint-<short-name>.md`.

```markdown
# NNNN — Forcing Constraint: {{short title}}

- Status: accepted
- Type: forcing-constraint
- Constraint class: {{regulatory | scale-measured | org-mandate}}
- Date: {{YYYY-MM-DD}}
- Deciders: {{names + roles}}
- Activates scale-up chapters: {{which files in scale-up/}}
- Sunset trigger: {{condition under which we'd retreat to default-mode}}

## 1. The constraint

State the specific, named, verifiable constraint. Examples of acceptable statements:

- *Regulatory*: "FedRAMP Moderate authorization is mandated by contract with {{customer}}, signed {{date}}, with audit by {{date}}. Specific control families requiring multi-AZ separation: AC-X, SC-Y."
- *Scale-measured*: "Production p99 latency exceeded SLO (200ms) for 35 consecutive days at sustained 14k RPS. Measurement at `{{dashboard URL}}` from `{{date}}` to `{{date}}`."
- *Org-mandate*: "Platform team mandate dated `{{date}}` requires all new services to publish OpenTelemetry traces. Enforcement via CI starting `{{date}}`. Reference: `{{policy link}}`."

Examples that are **not** acceptable:

- "We expect to grow."
- "All the big companies do it."
- "The team would prefer microservices."
- "It's the modern way."

## 2. The default-mode alternative considered

- Default-mode pattern: {{e.g. "single-region modular monolith on Fly.io with Postgres"}}
- Why it fails this specific constraint: {{e.g. "FedRAMP control SC-Y requires separation of duty between auth subsystem and primary data store"}}
- Cost of default-mode under the constraint: {{e.g. "ATO denied; contract loss"}}

## 3. The chosen scale-up path

- Pattern(s): {{e.g. "service decomposition along auth boundary; mTLS via service mesh"}}
- Activated chapters: {{links to scale-up/*.md}}
- Why this beats the default for this constraint: {{1–2 sentences}}

## 4. Cost projection

| Dimension | Default-mode | Scale-up | Multiplier |
|---|---|---|---|
| Compute | {{$X/mo}} | {{$Y/mo}} | {{Y/X}} |
| Network | | | |
| Storage | | | |
| Observability | | | |
| Security tooling | | | |
| Operational headcount | | | |
| **Total TCO** | {{$X/mo}} | {{$Y/mo}} | {{Y/X}} |

If multiplier > 4× without explicit forcing constraint per dimension: re-examine. The default cost-projection table in `scale-up/when_to_activate.md` shows typical 2–4× envelope.

## 5. Consequences

- ✅ {{good outcome — addresses the constraint}}
- ✅ {{good outcome}}
- ⚠ {{trade-off accepted — operational tax}}
- ⚠ {{trade-off — recruiting / training cost}}

## 6. Confirmation (90-day check)

How will we verify this was the right decision in 90 days:
- {{measurable signal — e.g. "FedRAMP audit pass; >80% controls verified automated"}}
- {{measurable signal — e.g. "p99 latency < 150ms sustained at 20k RPS"}}

## 7. Sunset condition

This forcing constraint is reviewed annually. The annex retreats to default-mode if:
- {{condition — e.g. "FedRAMP requirement deprecated by customer or contract terminated"}}
- {{condition — e.g. "Sustained traffic drops below 5k RPS for 90 consecutive days"}}

If sunset condition is met, file an ADR closing this one and removing the activated chapters from active use.

## 8. Approvals

- Engineering lead: {{name}} • {{date}}
- Security / compliance owner (if regulatory): {{name}} • {{date}}
- Finance owner (if cost > $X threshold): {{name}} • {{date}}
- Operations owner: {{name}} • {{date}}
```
