---
name: ROADMAP_md_template
version: 2.0.0
parent_skill: form-check
voice: dated, blunt; "won't-do" load-bearing
---

# ROADMAP.md template

```markdown
# Roadmap — {{project-name}}

> Last reviewed: {{date}} • Next scheduled review: {{date + 90d}}
> Items here are **directional**, not commitments. Commitments live in milestones / sprints.

## Now (in flight; <30 days)

- {{item}} — owner: {{name}} — target: {{date}}
- {{item}} — owner: {{name}} — target: {{date}}

## Next (planned; 30–90 days)

- {{item}} — driver / forcing function: {{why now}}
- {{item}} — driver: {{why}}

## Later (90+ days; speculative)

- {{item}} — open questions: {{}}
- {{item}} — open questions: {{}}

## Won't-do (explicit anti-scope)

> The won't-do list is load-bearing. State explicitly to prevent drift.

- **Microservices decomposition**: ruled out until forcing-constraint ADR (`scale-up/when_to_activate.md`)
- **Multi-region**: not in scope; current SLO is single-region; next review {{date}}
- **{{specific framework / pattern / abstraction}}**: rejected because {{reason}}; revisit only if {{condition}}

## Recently shipped (deltas; supersedes older roadmap rows)

- {{date}} — {{item}} — moved to ARCHITECTURE.md / CHANGELOG.md
- {{date}} — {{item}} — moved to "won't-do" with reason: {{}}

## Decision log integration

Every "Now" / "Next" item that survives 30 days becomes an MADR ADR. Roadmap items without an ADR by 30 days expire and re-enter "Later" or "Won't-do."
```

## Anti-patterns

- Speculative items in "Now" — they belong in "Later."
- Vague "Won't-do" without reason — re-litigated every quarter.
- ROADMAP that duplicates ARCHITECTURE / CHANGELOG content — stays in sync via human; almost always drifts. Cross-link instead.
- "Roadmap" used to communicate commitments — that's a milestones doc; keep separate.
