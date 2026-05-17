---
name: runbook_incident_response
version: 2.0.0
parent_skill: form-check
voice: imperative; pre-written for incident-time use
---

# Runbook, General Incident Response

> Use for any P0/P1 production incident. Specialized runbooks (supply-chain compromise, data leak, auth breach) link from here.

## Severity definitions

| Sev | Definition | Page on-call? |
|---|---|---|
| P0 | service down OR active data loss OR active security breach | yes, immediately |
| P1 | major degradation OR known vulnerability with active exploitation potential | yes, business hours; immediately if active exploit |
| P2 | minor degradation OR latent bug needing fix | next business day |
| P3 | cosmetic / nice-to-have | normal triage |

## Pre-flight (open the runbook)

- [ ] Confirm you have access: `{{verification command}}`
- [ ] Open incident channel: `#incident-{{ts}}-{{slug}}`
- [ ] Page on-call (P0/P1): `{{paging command}}`
- [ ] Pair confirmed (P0: required; P1: strongly recommended)
- [ ] Status page (P0/P1): set "investigating"

## Phase 1, Detect

- What's the symptom? Which dashboards / alerts?
- What's the user impact? (How many users? Which regions? Which features?)
- When did it start? (Correlate with recent deploys, dep updates, infra changes.)

Capture in incident channel; pin the summary message.

## Phase 2, Contain

Stop the bleeding. Containment ≠ fix; containment = prevent further damage.

Common containments:
- Roll back the last deploy: `{{deploy-tool}} rollback`
- Disable a feature flag
- Block a misbehaving client (rate limit, IP, API key)
- Drain traffic from an unhealthy region
- Quiesce a misbehaving job

Do **not** apply a fix until containment is verified.

## Phase 3, Eradicate

Remove the cause:
- If config: revert config + deploy
- If code: hotfix branch → review → deploy (compress review per severity but don't skip)
- If data: corrective migration with dry-run + double-check + rollback path
- If credential / token: rotate (see `supply_chain_compromise.md` if applicable)

Hotfix gate (even compressed):
- [ ] Failing test exists for the bug (encode the bug as a regression spec)
- [ ] Pair-reviewed
- [ ] Rollback plan documented in PR
- [ ] Communicated to incident channel

## Phase 4, Recover

Restore service:
- Verify metrics back in SLO
- Verify customer-facing flows
- Lift containments (rollouts, rate limits, regional drains)

Status page: "monitoring" → "resolved" once metrics hold for {{N}} minutes.

## Phase 5, Postmortem

Within 5 business days:

```markdown
# Postmortem, {{date}} {{slug}}

- Severity: P0
- Duration: {{ts-detect}} → {{ts-resolved}} ({{minutes}})
- Customers impacted: {{count or scope}}

## What happened (timeline)

| ts | event |
|---|---|
| ts | first signal |
| ts | paged |
| ts | contained |
| ts | eradicated |
| ts | recovered |

## Root cause

(Plain language. Single root cause if known; multiple contributing factors named.)

## Why our system allowed it

(Defense-in-depth analysis. Where did the gates fail?)

## What we did well

## What we didn't do well

## Action items

| # | item | owner | due |
|---|---|---|---|
| 1 | | | |

## Notes

(Anything else.)
```

Postmortems are **blameless**. Action items are owned and dated. Track to closure.

## Communication templates

### During (every {{30 min}} or significant change)

```
[STATUS] {{investigating | identified | mitigating | monitoring}}
Impact: {{}}
Working on: {{}}
Next update: {{ts}}
```

### Resolved

```
Resolved at {{ts}}.
Root cause (preliminary): {{}}
Customer impact: {{}}
Postmortem will be published by {{date}}: {{ticket link}}
```

### Customer-facing (if applicable)

(Per breach-notification policy. Run by communications + legal before sending external.)

## Specialized runbooks

- Supply-chain compromise: `supply_chain_compromise.md`
- {{Add as built}}: data leak, auth breach, regional outage, DB corruption, ...

## Anti-patterns

- Skipping containment to "just fix it", common path to worsening incidents.
- Communication updates timestamped but no actual content, operator fatigue.
- "It's resolved" before metrics held, status flap; trust loss.
- Postmortem with no action items, symptom of blame culture or unwillingness to invest.
- "Hero culture" rewarded, paper over the systems gaps that allowed the incident.
