---
name: adversarial_questions
version: 2.0.0
parent_skill: recovery
---

# Adversarial Questions, 12 axis-segmented

The adversarial phase walks 12 questions across 12 axes. Each must produce a verdict: `pass`, `fail`, or `n/a-with-reason`. **Five passes is not enough**; the original 5-question set missed too many bug classes that 2025–2026 vibe-coding incidents exposed.

## The 12

### 1. Severity inflation (P0 → P1 demotion check)

Did any P0 finding get demoted to P1 to make the engagement look better? Re-classify with this filter: would I page someone at 3 AM for this? If yes → P0.

### 2. Coverage gap

What did this review *not* look at? List the surfaces, modules, integrations, and bug classes that fell outside scope. State explicitly; do not paper over.

### 3. Reversibility

For every action this engagement recommends or applies: is the rollback documented and tested? Has the rollback path been *executed* in a staging environment? Untested rollback = no rollback.

### 4. Score gaming

Did anyone re-weight the rubric to make a score pass? Did anyone claim a perfect 100? Did anyone bump a score without new evidence? Walk the calibration log; flag any anomaly.

### 5. Month-3 projection

What will fail 90 days after this engagement? Walk `form-check.skill/checklists/smell_catalog.md` for the project archetype. Identify ≥3 specific failure modes; record them as ROADMAP "Now / Next" or "Won't-do."

### 6. Threat model

Was STRIDE applied to every changed boundary? Was LINDDUN applied to every personal-data flow? Was OWASP-LLM/API/Web applied per surface? List the boundaries you walked and the ones you skipped.

### 7. Blast radius

For each non-trivial change: were transitive callers walked? Was the privilege axis assessed? Was secret-handling accounted for? Re-compute via `form-check.skill/tools/blast_radius.py`; flag if heuristic disagrees with reviewer estimate.

### 8. Hallucination integrity

For every dep added: registry exists, author known, first-seen ≥30d, prior versions exist, no malicious post-install? For every API used: matches current SDK docs (not invented)? For every flag / env var: documented? List the verification trail per item.

### 9. Fitness functions

Are the project's architecture decisions enforced in CI? List active functions; cross-reference to ADRs. Identify ADRs without an enforcing function (gap → action item).

### 10. Accessibility

If the project has UI: was WCAG 2.2 walked for the changed surface? Were vibe-impossible accessibility decisions (ARIA pattern selection, focus-management, screen-reader copy) routed to a qualified reviewer?

### 11. Privacy / LINDDUN

If the change touches personal data: was the data-classification taxonomy applied? Are retention, regional transfer, and DSAR-tooling implications considered? Is a DPIA required (GDPR Art 35)?

### 12. Agent self-attack

Did the agent scan its own inputs for prompt-injection patterns? Was untrusted content fenced? Did the agent quote external sources without quarantine? Walk `form-check.skill/agent-runtime/prompt_injection.md`.

## Per-question outputs

Each question produces a row in `.recovery/adversarial.md`:

```markdown
### Q{{N}}, {{title}}

- Verdict: pass | fail | n/a-with-reason
- Evidence: {{specific reference; file:line; calibration log row; ADR id; ...}}
- If fail: action item with owner + due date
- If n/a: justification (not "doesn't apply"; specific reason)
```

## When to invoke

The adversarial phase activates per `workflow_dag.md` when engagement-aggregate score is below tier-floor. May also be invoked deliberately by the user (`--force-adversarial`).

## Loop budget

Each adversarial pass:
- Walks all 12 questions
- Produces verdict per
- If any `fail`: feeds finding back into review phase

Loop cap: 2 (per `workflow_dag.md`). After 2 loops without crossing tier-floor, escalate to user with structured gap report.

## Anti-patterns

- "Q1 → pass" without examining a single P0/P1 finding, perfunctory.
- Marking every question `n/a` for a small change, review fatigue, not vibe budget.
- Flagging every `fail` as P2, defeats the severity-inflation check.
- Skipping Q12 because "the agent isn't an attack surface", every agent-consumed text is an attack surface.
- Loop without new evidence between passes, anti-gaming rule violation.
