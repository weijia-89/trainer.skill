---
name: review_gate_checklist
version: 2.0.0
parent_skill: form-check
---

# Review-Gate Checklist (irreversible / vibe-dangerous ops)

Use for any change classified vibe-dangerous (`rubrics/vibe_safety_map.md` Bucket 3). Print → tick → commit → only then proceed.

## When this applies

Any of:
- DB migration that drops/renames a column or table, backfills data, or changes a unique constraint
- Production write at scale (mass update / mass delete)
- File deletion (especially recursive)
- External API call with side effects (sends email/SMS, charges card, posts publicly, files a ticket)
- Secrets rotation
- Code that reads or writes secrets / tokens
- Change to authentication / authorization
- Update to `eval_baseline.json`
- Change that disables a CI gate or fitness function
- LLM agent gaining a new tool capability
- Removing a public API path

## Pre-merge checklist

- [ ] **Failing test exists** that captures the spec (test-as-spec)
- [ ] **Diff fully read by a human** (no skim)
- [ ] **STRIDE walk** completed on the changed surface (`checklists/threat_model_stride.md`)
- [ ] **Reversibility plan** documented in PR body (one-paragraph rollback)
- [ ] **Idempotent**: running the operation twice does not double-effect (or has a documented one-shot guard, e.g. idempotency-key)
- [ ] **Dry-run mode** exists and was exercised
- [ ] **Feature flag** wraps the new path, default off
- [ ] **Staged rollout sequence** documented (per archetype: web 1%→10%→50%→100%; CLI/library semver; mobile staged ring)
- [ ] **Observability hooked**: metric / log / alert in place to detect failure inside one deploy cycle
- [ ] **Audit trail** captured (who/when/what)
- [ ] **Backups verified within last 24h** (DB ops only)
- [ ] **Slopsquatting check on any new deps** (`checklists/supply_chain_slsa.md` ritual)
- [ ] **Bug-class lens walked** for the touched surface (CWE Top-25 + applicable OWASP-LLM/API/Web)
- [ ] **Mutation score** ≥ tier-target on touched lines (vibe-dangerous: ≥75–80% per language)
- [ ] **Hallucination check**: every dep, API, flag, env var verified against current docs
- [ ] **Confidence score ≥95** with breakdown attached AND per-component minima met
- [ ] **CHANGELOG.md** entry added (with reproduction or migration if breaking)
- [ ] **CLAUDE.md / AGENTS.md** updated if surface area changed

## Rollback verification

For any vibe-dangerous merge: within 1 hour of deploy, **execute the rollback in a staging env** and confirm it works. A rollback path that has never run is a rollback path that doesn't exist.

## "Won't auto-apply" rule

For tools that *recommend* destructive actions (a hardener, a fixer, a migrator):
- Default behavior is **suggest only**, output to stdout / file / report
- Apply mode requires `--i-really-mean-it` AND interactive confirm AND audit-table log
- Never make `apply` the default verb in a CLI

## Refusal protocol

If the AI agent is asked to skip any of the above, the refusal is not negotiable:

> "This is a vibe-dangerous surface. I will not skip {{item}}. To proceed, write the failing test / document the rollback / run the dry-run / get the threshold-met score."

## Escalation

If 3 attempts at the gate fail (score won't reach floor; missing test cannot be written; rollback path cannot be defined):
- Stop the agent
- Escalate to user with structured gap report
- Do not back-channel ("OK we'll skip the gate just this once"), that is the failure mode the gate exists to prevent

## Cross-references

- Confidence rubric: `rubrics/confidence_score.md`
- Vibe-safety axis: `rubrics/vibe_safety_map.md`
- Threat models: `checklists/threat_model_stride.md`, `checklists/threat_model_linddun.md`
- Supply chain (new deps): `checklists/supply_chain_slsa.md`
- Deprecation: `checklists/deprecation_policy.md`
- Agent-runtime constraints: `agent-runtime/harness_contract.md`
