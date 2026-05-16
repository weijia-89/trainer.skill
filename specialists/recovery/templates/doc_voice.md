---
name: doc_voice
version: 2.0.0
parent_skill: recovery
---

# Doc Voice — per-archetype rules

Different docs serve different consumers and tooling conventions. One voice across all docs is wrong. Use this table to pick the voice per artifact.

## Voice matrix

| Archetype | Voice | Person | Tone | Docstring shape | Examples allowed in entry |
|---|---|---|---|---|---|
| API reference (Sphinx, typedoc, Javadoc, godoc, rustdoc) | impersonal, descriptive | third-person; imperative for parameters | precise, dry | uniform required | yes, in dedicated examples section |
| README | conversational, archetype-driven (CLI / library / service / monorepo) | second-person | inviting, code-led | n/a | yes, throughout |
| SECURITY.md | imperative for ops; descriptive for threat model | second-person (ops) / third-person (architecture) | precise, no marketing | n/a | minimal |
| CHANGELOG.md | impersonal factual (Keep-a-Changelog) | none (use action verb) | dated, terse | n/a | no |
| ARCHITECTURE.md | descriptive third-person | third-person | precise; tag normative claims | n/a | minimal; cross-link to docs |
| ROADMAP.md | dated, blunt; "won't-do" load-bearing | first-person plural acceptable | committal language only when committed | n/a | no |
| Runbook | imperative, role-segregated | "you" addressed to operator | no hedging during incident | n/a | yes, in command examples |
| Glossary | precise definitions, no examples in entry | none | terse | n/a | no — examples in cookbook |
| Source comments (non-docstring) | mixed density; deAI base rules apply | first-person plural sparingly | concise | n/a | when the comment IS the example |
| ADR (MADR) | descriptive past tense | first-person plural ("we") for decision rationale | dated | n/a | yes |
| Cookbook / user docs | conversational, code-led | second-person | inviting | n/a | yes, every entry |

## When voices conflict

A single file may carry multiple archetypes (e.g. `SECURITY.md` has both descriptive threat-model sections and imperative reporting-procedure sections). Apply the overlay per section, not per file.

## API-reference docstring conventions per language

| Language | Format |
|---|---|
| Python | Google-style, NumPy-style, or reST (one chosen project-wide; never mixed). Sphinx + MyST. |
| TypeScript | TSDoc (`@param`, `@returns`, `@throws`); typedoc consumes. |
| Java | Javadoc (`@param`, `@return`, `@throws`, `@since`, `@deprecated`). |
| Kotlin | KDoc (similar to Javadoc). Dokka consumes. |
| Go | godoc convention: first sentence is summary; full sentence form. |
| Rust | rustdoc: Markdown; `///` for items; `//!` for modules. |

The choice is project-wide; document in `CLAUDE.md` Stack section. Mixing styles within a project breaks docs-gen.

## Cross-references

- Banned vocabulary: `templates/deai_rules.md`
- README archetype templates: `form-check.skill/templates/README_archetypes/`
- All other doc templates: `form-check.skill/templates/*_template.md`

## Anti-patterns

- One voice across all docs → some docs read wrong (academic README, alarming SECURITY).
- API reference written in conversational README voice → tooling can't extract clean reference.
- Runbook in passive voice → operator hesitation during incident.
- CHANGELOG entries with first-person "we" → drifts toward marketing copy.
- README that's autobiographical instead of user-led → reader-unfriendly.
- "Voice consistency" used as a euphemism for "everything sounds like the loudest contributor" → diversity of contributor voice is fine within an archetype's rules.
