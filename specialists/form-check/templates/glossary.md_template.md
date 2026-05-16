---
name: glossary_template
version: 2.0.0
parent_skill: form-check
voice: precise definitions; no examples in entries; alphabetized
---

# Glossary template

```markdown
# Glossary — {{project-name}}

Canonical names for domain concepts. Use these terms consistently across code, docs, and discussions ("ubiquitous language" per Eric Evans). Update when the domain language evolves.

## Conventions

- One sentence per term where possible.
- No examples in the entry — examples belong in user docs / cookbook.
- Cross-references in `*italics*`.
- Distinguish *domain* terms from *technical* terms; both belong here.

## Terms

**Account**
A billing entity owning one or more *workspaces*. One human user may have multiple accounts.

**Audit Log**
Append-only record of state-changing actions, indexed by *actor*, target, and timestamp. Retained per regulatory requirement.

**Workspace**
A logical container for *resources* owned by an *account*. Workspaces are tenant boundaries; cross-workspace access is explicit.

**Resource**
The atomic ownership unit. See `docs/data-model.md` for the resource taxonomy.

**Actor**
The principal who performed an action. May be a human user, a service account, or an automated agent. Actor identity is signed and recorded in the *audit log*.

**...**

## Deprecated terms

| Old term | Replaced by | Since |
|---|---|---|
| Tenant | Workspace | 2025-08-01 |
| Item | Resource | 2024-11-15 |

When you encounter a deprecated term in code or docs, update it as a side-quest of your current change.
```

## When to use

- Onboarding new contributors / agents — readers reference the glossary, not Slack history.
- During a doc-pass — terminology consistency is a fitness function (`tools/check_glossary.sh` lint candidate).
- During an architecture review — glossary drift is an early signal that the domain model is shifting.

## Anti-patterns

- Glossary that's stale — runs counter to its own purpose. Quarterly review.
- Definition-by-example only ("an Account is, like, when a user signs up...") — fails the precision test.
- Multiple terms for the same concept — pick one and deprecate the others.
- "Helper", "manager", "service" in the glossary — these are usually code-shape terms, not domain terms; if they're in the glossary, the domain language has gaps.
