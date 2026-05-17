# form-check, someone watches one rep and tells you what's off

A senior-engineer / tech-lead posture skill for AI agents planning, building, and reviewing software in a vibe-coding loop. Default-anti-enterprise; scale-up annex behind a forcing-constraint ADR.

> **Posture-adaptive**: default mode refuses microservices / k8s / event bus / CQRS. Scale-up annex chapters activate only with a documented forcing constraint (regulatory, scale-measured, or org-mandate).

## What this is (and isn't)

- **Is**: a *review and planning* skill that guides AI agents.
- **Is**: an opinionated checklist of bug classes, threat models, supply-chain hygiene, and confidence scoring.
- **Is not**: a code generator. The skill guides agents that write code; it does not write code itself.
- **Is not**: a CI runner. It defines what to run; the host harness runs it.

## Install

Clone or vendor this directory under your agent's skills location.

For Claude / Cursor / similar agent harnesses with skill-loader support: place under `~/.claude/skills/form-check.skill/` (or equivalent path) and invoke via the trigger phrases listed in `SKILL.md`.

## Use

Read `SKILL.md` first (~220 lines; meant to be loaded into the agent's context). Sub-files are lazy-loaded via `checklists/INDEX.md`.

Common engagements:

- **Plan a new app** → `templates/CLAUDE.md_scaffold.md` + `rubrics/stack_decision.md` + `checklists/preflight_10q.md`
- **Code review** / **adversarial review** → `checklists/INDEX.md` (decision tree)
- **Refactor prep** → `rubrics/confidence_score.md` + `checklists/smell_catalog.md`
- **Harden** (security pass) → `checklists/threat_model_stride.md` + `checklists/owasp_*_top10.md` + `checklists/supply_chain_slsa.md`

## Layout

```
SKILL.md                       # ≤220 lines; canonical posture
references/notes.md            # citation tags
rubrics/
  confidence_score.md          # tiered thresholds + 9 components
  stack_decision.md            # multi-language; cite-or-normative
  vibe_safety_map.md           # 4 buckets (incl. vibe-impossible)
checklists/
  INDEX.md                     # decision tree
  bug_class_audit.md           # CWE Top-25 + AI-PR shapes
  owasp_llm_top10.md           # OWASP LLM (2025)
  owasp_api_top10.md           # OWASP API (2023)
  owasp_web_top10.md           # OWASP Web (2025)
  threat_model_stride.md       # security
  threat_model_linddun.md      # privacy
  fitness_functions.md         # architectural fitness functions
  accessibility_wcag22.md      # WCAG 2.2
  smell_catalog.md             # month-3 failure modes
  preflight_10q.md             # 10 questions before code
  deprecation_policy.md        # RFC 8594 + sunset
  supply_chain_slsa.md         # slopsquatting + SLSA + Shai-Hulud
  skill_antipatterns.md        # how this skill gets misused
templates/
  CLAUDE.md_scaffold.md        # agent-context scaffold
  AGENTS.md_scaffold.md        # alias for hosts that prefer this filename
  MADR_short.md                # ADR template
  review_gate_checklist.md     # vibe-dangerous gate
  test_as_spec.md              # multi-language
  threat_model.md              # STRIDE+LINDDUN combined worksheet
  runbook.md
  SECURITY.md_template.md
  CHANGELOG_template.md
  ARCHITECTURE.md_template.md
  ROADMAP.md_template.md
  glossary.md_template.md
  calibration_log_render.md
  forcing_constraint_adr.md
  prompt_versioning.md
  README_archetypes/{cli,library,service,monorepo}.md
  runbooks/{supply_chain_compromise,incident_response}.md
multi-language/
  matrix.md
  python.md typescript.md java.md go.md rust.md
agent-runtime/
  harness_contract.md          # capability allowlist + ledger + rollback
  prompt_injection.md          # OWASP-LLM01 defense
scale-up/                      # GATED, forcing-constraint ADR required
  when_to_activate.md
  distributed_systems.md multi_region.md soc2_iso27001.md service_mesh.md event_sourcing_cqrs.md spring_kotlin_jvm.md
tools/                         # optional automation; markdown algorithms in docs/
docs/                          # algorithm specs paired with tools/
examples/                      # worked examples
tests/                         # skill self-tests (banned-vocab, citations, format, ...)
```

## Versioning

Semantic Versioning. See `CHANGELOG.md` for explicit MAJOR / MINOR / PATCH rules tailored to skill content.

## Compose with other skills

`recovery.skill` composes this skill (rubric + checklists + templates) under a workflow DAG. See `recovery.skill/SKILL.md`.

## Contributing

See `CONTRIBUTING.md` for the extension protocol (adding a new bug-class lens, a new checklist, a new template).

## License

MIT, see `LICENSE`.

## References

Primary sources cited via tags in `references/notes.md`. Original research dossier archived in a private local-only directory (historical, not maintained).

## Acknowledgments

Original v1 by Wei Jia (2026-04, FY26 perf-review portfolio). v2 rewrite 2026-05-14: posture-adaptive overhaul; multi-language tooling; OWASP-LLM/API/Web integration; fitness functions; agent-runtime contract; threat-model templates; supply-chain Shai-Hulud-aware updates.
