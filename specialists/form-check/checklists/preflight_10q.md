---
name: preflight_10q
version: 2.0.0
parent_skill: form-check
---

# 10-Question Pre-Flight Checklist

Answer **before any code is written**. Each unanswered question is a slot for a future incident.

1. **Who uses it?** One sentence. (Internal tool / public users / one engineer / regulated tenants.)
2. **What's the scariest thing it could do?** (Delete data, leak PII, charge money, post publicly.) → goes on the vibe-dangerous list (`rubrics/vibe_safety_map.md` Bucket 3).
3. **What are the 3 falsifiable success criteria?** (e.g. "p99 < 200ms at 1k RPS", "false-positive rate < 5% on golden set", "0 customer-data egress to third-party LLMs".)
4. **What's the data model?** Tables + key relationships, no ORM yet. **Plus data classification** (public / internal / confidential / PII / PHI / PCI / NPI / regulated).
5. **Where does it run?** One PaaS, one region, one DB. **Default mode**; if scale-up, name the forcing constraint and write the ADR (`templates/forcing_constraint_adr.md`).
6. **Where do secrets live?** Per env: dev / staging / prod. (Env-only / KMS / Vault / cloud secrets manager.) **Never in CLAUDE.md, never committed, never in prompts.**
7. **What's the LLM contract?** Provider, model (pinned, no "latest"), prompt template versioning (`templates/prompt_versioning.md`), eval gate, agent capability allowlist (`agent-runtime/harness_contract.md`). Or "no LLM" — Q7 is `n/a`.
8. **What's the rollback plan?** One paragraph. (Git revert is not a rollback for migrations or external side-effects.) **Plus deprecation policy** if any public surface.
9. **What's the eval baseline?** How will we know we regressed? Golden dataset (50–100 minimum, 200–500 prod-ready). Plus **CI fitness functions** baseline (≥3 lint-class).
10. **What is *not* in scope?** Three things minimum, named explicitly. (Anti-scope is more useful than scope.) **Plus** the won't-do list of vibe-impossible items (`rubrics/vibe_safety_map.md` Bucket 4).

## Refusal trigger

If 5+ of the 10 are unanswered or hand-wavy, **refuse to scaffold**. Push back: "we'll build a worse system if we start now."

## Cross-references

- Threat model template: `templates/threat_model.md`
- Stack decision: `rubrics/stack_decision.md`
- Multi-language tooling: `multi-language/matrix.md`
- Fitness functions baseline: `checklists/fitness_functions.md`
- Supply chain: `checklists/supply_chain_slsa.md`

## Cheat-sheet for the user

- Internal/CLI tools: Q5–6 may collapse to "local + .env (gitignored)".
- Tools without an LLM: Q7 is `n/a`.
- Greenfield: Q10 is the most valuable lever — biggest YAGNI saver.
- Regulated domains (healthcare, finance, government): add Q11 "which regulator + which controls?" before answering Q1–10.

## Common failure modes

- **Q3 answered with adjectives** ("fast", "scalable") — that's not falsifiable. Demand a numeric / measurable property.
- **Q4 missing data classification** — invites later GDPR / CCPA scramble. Always classify upfront.
- **Q7 says "we'll pin the model later"** — that's how you wake up to a behavioral break in production. Pin upfront.
- **Q10 vague** ("various things") — re-prompt for three specific won't-dos.
