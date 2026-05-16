---
name: CLAUDE.md_scaffold
version: 2.0.0
parent_skill: form-check
---

# CLAUDE.md / AGENTS.md scaffold

Drop this file at `/CLAUDE.md` or `/AGENTS.md` (depending on which agent format the host uses). Replace `{{...}}` placeholders. Keep this concise — agents skim, not read.

```markdown
# CLAUDE.md / AGENTS.md — {{project-name}}

> Version: {{semver}} • Last updated: {{date}} • Owner: {{team}}

## Stack

| Layer | Choice | Version | Cite or `[normative]` |
|---|---|---|---|
| Language | {{e.g. Python 3.12.4}} | {{exact}} | `[normative]` |
| Package manager | {{uv | poetry | pnpm | gradle | go modules | cargo}} | {{exact}} | |
| Web framework | {{FastAPI | Next.js | Spring Boot | none}} | {{exact}} | |
| LLM backend | {{provider+model}} or "none" | {{model-version}} | |
| Data validation | {{Pydantic v2 | Zod | jsonschema}} | | |
| Database | {{Postgres 16 | SQLite WAL}} | {{exact}} | |
| Testing | {{pytest+Hypothesis | Vitest+fast-check | JUnit5+jqwik | go test+rapid | cargo test+proptest}} | | |
| Lint / format | {{ruff | Biome | detekt | golangci-lint | clippy+rustfmt}} | | |
| Mutation testing | {{mutmut | Stryker | pitest | go-mutesting | cargo-mutants}} | | |
| Dep audit | {{pip-audit | npm audit + Socket | OWASP DC | govulncheck | cargo-audit}} | | |
| SBOM | {{cyclonedx-py | cyclonedx-npm | cyclonedx-maven | cyclonedx-gomod | cyclonedx-rust-cargo}} | | |
| SLSA target | Build Track L2 (default) | {{}} | |

## Key Files

```
src/<pkg>/
  models.{{py|ts|java|go|rs}}   — boundary contracts (Pydantic / Zod / records)
  cli.{{ext}}                   — thin shell over the core
  <core>.{{ext}}                — domain logic; pure where possible
  database.{{ext}}              — persistence layer
  llm_client.{{ext}}            — LLM interface (Protocol + Mock + real impl)

tests/
  unit/         — fast, no network, no browser
  integration/  — touches local DB / disk
  eval/         — golden-dataset metric runs (only if LLM-bearing)
  fixtures/     — golden_dataset.json + per-feature inputs

docs/
  adr/          — MADR-short ADRs
  api-inventory.md  — endpoints + versions + deprecation status
  glossary.md
  threat-model.md   — STRIDE + LINDDUN per data-flow boundary
```

## Test Commands

```bash
{{cmd-unit}}            # fast
{{cmd-integration}}     # local deps only
{{cmd-eval}}            # MOCK_LLM=1 — CI-friendly
{{cmd-eval-full}}       # real LLM — manual / nightly
{{cmd-mutation}}        # mutation score on touched lines
{{cmd-lint}}
{{cmd-fitness}}         # architectural fitness functions
```

## Context Window / LLM Strategy (skip if no LLM)

- Provider + model pinned: {{exact}}
- Prompt template versioning: {{semver-of-prompt}}
- Eval baseline: {{path/to/eval_baseline.json}}; updated only on PROMPT-MAJOR
- Truncation strategy: {{rule}}

## Don't-Do List

- **Never** {{load X from CDN}}
- **Never** auto-apply destructive op
- **Never** add a new dep without slopsquatting check (`form-check.skill/checklists/supply_chain_slsa.md`)
- **Never** `subprocess`/`os.system`/`Runtime.exec` with shell=True over user input

## Vibe-Safety Map (per `form-check.skill/rubrics/vibe_safety_map.md`)

- **Vibe-safe (AI ships unread):** {{modules}}
- **Vibe-careful (read diff):** {{modules}}
- **Vibe-dangerous (write test + read diff + flagged rollout):** {{modules}}
- **Vibe-impossible (qualified human author required):** {{modules}}

## Review Gates (must be human-approved)

- Schema migrations
- Deletion paths
- LLM prompt changes that affect eval baseline
- Auth / payments / secrets / external-side-effect calls
- Any change touching {{project-specific irreversible}}

## Confidence-Score Posture

This project uses `form-check.skill` for changes. **Tier-floor per change** (see `rubrics/confidence_score.md`):
- Vibe-dangerous ≥95
- Vibe-careful ≥90
- Vibe-safe ≥80
- Pure refactor ≥70

If a change touches a vibe-dangerous surface, the score must include a verified test-run section + STRIDE walk + mutation score.

## Architecture Decisions

ADRs in `docs/adr/`. Active fitness functions in `tools/check_*` and `.github/workflows/fitness.yml`. Each ADR links to the function that enforces it.

## Eval Baseline (LLM-bearing only)

Located: `eval_baseline.json`. **Never** update via script; manual review only after dataset additions or intentional accuracy bump.

## Supply Chain

- Lockfile pinned with hashes ({{tool}})
- {{audit-tool}} runs in CI
- New deps: slopsquatting check (registry exists, author known, first-seen ≥30d, prior versions exist)
- SBOM ({{format}}) generated per release

## Security

- See `docs/threat-model.md` (STRIDE + LINDDUN as applicable)
- Vuln-disclosure: {{security@example.com}}
- See `SECURITY.md` for the full reporting policy

## Agent-runtime contract

This project is consumed by AI agents. The host harness must enforce:
- Capability allowlist by tier (`form-check.skill/agent-runtime/harness_contract.md`)
- State ledger at `.agent/ledger.jsonl`
- Rollback contract per tool
- Worktree confinement for vibe-careful and vibe-dangerous engagements
- Prompt-injection scan on load (`form-check.skill/agent-runtime/prompt_injection.md`)

If host harness lacks these, this project's agent-assisted changes are advisory-only.
```

## Notes

- This template is the **floor**, not the ceiling. Add project-specific sections.
- The Stack table doubles as slopsquatting defense — agents and humans confirm versions before generating code.
- The Don't-Do List is the negative space; cheaper than catching it in review.
- The Vibe-Safety Map is the explicit per-module budget for AI freedom.
- The Confidence-Score Posture links the project to the skill's scoring rule.
- Skip sections that don't apply (LLM, eval baseline) — half-filled sections are worse than absent ones.
