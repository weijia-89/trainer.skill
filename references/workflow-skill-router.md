# Workflow skill router (replaces agent-requestable .mdc rules)

**Purpose:** Thin `.mdc` workflow rules were removed to save context (~17 rules). **Trainer** routes single-agent work; **superset** embeds the same route in each worker prompt. Rules = iron laws + path globs only; skills = bodies.

**Iron law:** Naming a row is not invocation — `file_read` the **Skill canon** path before acting.

## Single-agent (trainer)

On trigger match, load **Skill canon** in full. If **Verify** is set, run before claiming done.

## Multi-agent (superset)

Orchestrator: map each manifest row `role` → **Skill canon** below; paste into worker prompt under `## Workflow skill (mandatory)`:

```markdown
## Workflow skill (mandatory)
- **Route:** <row from table>
- **Canon:** <full absolute SKILL.md path>
- **Verify:** <command or —>
Load canon in first steps (after trainer). Do not substitute glob rules for the skill body.
```

Validator: every worker with `role` matching a row must cite canon path; missing canon = dispatch blocked (form-check on manifest).

---

## Router table

| Trigger / task | Skill canon | Verify (mechanical) | Notes |
|----------------|-------------|----------------------|-------|
| Interview prep router; post-apply pipeline | `/Users/dubs/Projects/toren/justice-of-toren.skill/SKILL.md` | — | Routes anaander / tisarwat / breq |
| Recruiter screen; TA call; Calendly | `/Users/dubs/.cursor/skills/anaander/SKILL.md` | — | Alias: startup-recruiter-prep |
| Tech assessment; take-home; Stage A–D cram | `/Users/dubs/Projects/toren/tisarwat.skill/SKILL.md` | `python3 /Users/dubs/Projects/toren/applications/.scripts/validate_prep_layout_v2.py --slug <slug>` | HTML via assessment-prep-site |
| Code review; audit; remediation plan; @review-rigor | `/Users/dubs/.cursor/skills/review-rigor/SKILL.md` | — | Pair with form-check on PRs |
| Research; investigate; fact-check; lit review | `/Users/dubs/Projects/palamedes/skill/SKILL.md` | — | Also `palamedes.mdc` requestable pointer |
| Piranesi export; ChatPRD Opus 4.8; NotebookLM packet | `/Users/dubs/Projects/piranesi.skill/SKILL.md` | `bash …/verify_piranesi_export.sh --dir … --strict` + `python3 …/verify_prompts_md.py --project-dir …` (PIR-20) | Export-only · one sequenced `prompts.md` |
| Full research; deep dive; persona ILS/JFS | `/Users/dubs/Projects/toren/breq.skill/workflows/full_research.md` | — | After pre-assessment |
| Engram dossier; POI map | `/Users/dubs/.cursor/skills/engram/SKILL.md` | `python3 /Users/dubs/Projects/toren/applications/.scripts/verify_engram_slug_gates.py --slug <slug>` | Elicitation gate on slug |
| Granola interview; post-call ingest | Granola MCP + `/Users/dubs/.cursor/skills/anaander/SKILL.md` | — | No in-Cursor fake ingest |
| Significant refactor; >5-file canon | `/Users/dubs/Projects/trainer.skill/references/chatprd-opus-implementation-plan-gate.md` | — | ChatPRD Opus plan before code |
| Epistemic planning; stakes L0–L4 | `/Users/dubs/.cursor/skills/epistemic-planning/SKILL.md` | — | Before large initiatives |
| Skill audit; slopsquat; fitness | `/Users/dubs/.cursor/skills/skill-fitness/SKILL.md` | `bash /Users/dubs/Projects/scholia/scripts/verify_skill_fitness.sh` (if present) | Explicit invoke |
| README/CHANGELOG user docs | `/Users/dubs/Projects/deai.skill/SKILL.md` | — | Voice prime before ship |
| FOSS tool pick | `/Users/dubs/Projects/trainer.skill/references/trainer-runtime-compactness.md` + form-check | — | Security > stars |
| Application index KPI / channel rows | `/Users/dubs/Projects/toren/applications/_guides/INDEX_HTML_VERIFY.md` | `python3 /Users/dubs/Projects/toren/scripts/verify_application_index_html.py` | Glob: `applications-index-html.mdc` |
| Materials prep; story elicitation | `/Users/dubs/Projects/toren/breq.skill/references/materials-prep-workflow.md` | `python3 /Users/dubs/Projects/toren/applications/.scripts/validate_materials_prep.py --slug <slug>` | Glob: `career-materials-prep.mdc` |
| Research doc write/compress | `/Users/dubs/Projects/.cursor/skills/research-doc-style/SKILL.md` | `python3 /Users/dubs/Projects/toren/applications/.scripts/validate_research_doc_shape.py --slug <slug>` | Glob: `research-doc-token-style.mdc` |
| NotebookLM bootstrap | `/Users/dubs/Projects/.cursor/skills/notebooklm-prep/SKILL.md` | `python3 /Users/dubs/Projects/toren/applications/.scripts/validate_prep_layout_v2.py --slug <slug>` | Glob: `notebooklm-prep.mdc` |
| Magic Patterns HTML layout | Magic Patterns MCP + `/Users/dubs/Projects/toren/tisarwat.skill/SKILL.md` | — | Pedagogy: assessment-prep-pedagogy.md |
| Clean session / close session | Operator wrap-up (restore `clean-session.mdc` if needed) | — | Remove session cruft |
| Manual QA automation | Product-specific QA runbooks | — | No global .mdc |

**Glob-covered (no skill-only substitute):** career-ats-honesty, cl-elicitation, outreach OL-1/OL-3, prep placement, pipeline cruft — see project glob rules under `/Users/dubs/Projects/.cursor/rules/`.

---

## Negative space

| Do not load | When |
|-------------|------|
| palamedes | Implementation, git ops, single-file fix |
| piranesi | Ingest/reconcile turns (unless export) |
| full trainer.skill body | Inside buds/toebeans product paths |
| superset + gymbuddy | Same turn — pick one |

---

## Maintenance

- SSOT: this file. Trainer + superset link here; do not restore duplicate `.mdc` bodies.
- Mechanical check: `python3 /Users/dubs/Projects/scripts/cursor/verify_workflow_skill_router.py`
