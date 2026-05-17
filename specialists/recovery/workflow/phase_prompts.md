---
name: phase_prompts
version: 2.0.0
parent_skill: recovery
---

# Phase Prompts, env-agnostic, parameterized

Per-phase agent invocation prompts. Use these as the seed for the host harness when recovery is dispatched. Output paths are parameterized (`{{state_dir}}`, `{{repo}}`); no hard-coded session paths.

## Conventions

- `{{state_dir}}` = `.recovery/` under the engagement repo by default; override via env `CODEIT_STATE_DIR`.
- `{{repo}}` = engagement repo absolute path.
- `{{tier}}` = vibe-safety tier per engagement-start determination.
- `{{engagement_id}}` = ULID generated at engagement start.

## Phase: discovery

```
You are running the discovery phase of the recovery engagement.

Repo: {{repo}}
Engagement type: {{engagement_type}}
Engagement id: {{engagement_id}}
Tier: {{tier}}

Tasks:
1. Read repo tree (depth ≤ 2) and capture top-level structure.
2. Identify language(s), build tool(s), test runner(s), package manager(s).
3. Read CLAUDE.md / AGENTS.md if present; record state.
4. Read README.md / CHANGELOG.md / SECURITY.md / ARCHITECTURE.md / ROADMAP.md if present.
5. List ADRs in docs/adr/ if present.
6. Identify forcing-constraint ADRs (run form-check.skill/tools/check_forcing_constraint.sh).
7. Run form-check.skill/tools/scan_prompt_injection.sh on workspace docs; flag hits.

Output to {{state_dir}}/discovery.md. One section per finding.
Append a verdict row to {{state_dir}}/state.jsonl.
```

## Phase: review

```
You are running the review phase of the recovery engagement.

Inputs: {{state_dir}}/discovery.md
Repo: {{repo}}
Tier: {{tier}}

Walk form-check.skill/checklists/INDEX.md decision tree to select applicable checklists.

For each applicable checklist, walk it against the repo. Record findings as P0/P1/P2 rows in {{state_dir}}/review.md with this schema:

| ID | Lens | File:line | Severity | Reproduction | Proposed fix | Confidence (component scores) |

For LLM-bearing surfaces, include OWASP-LLM-Top-10 walk.
For API surfaces, include OWASP-API-Top-10 walk.
For browser-rendered web, include OWASP-Web-Top-10 walk.
For UI surfaces, include WCAG-2.2 walk.
For dep additions, include slopsquatting / supply-chain walk.

Append verdict row to {{state_dir}}/state.jsonl.
```

## Phase: scoring

```
You are running the scoring phase.

Inputs: {{state_dir}}/discovery.md, {{state_dir}}/review.md
Rubric: form-check.skill/rubrics/confidence_score.md (per-change) + recovery.skill/rubrics/code_fixer_confidence.md (engagement)

For each non-trivial change identified in review:
1. Determine tier (per form-check.skill/rubrics/vibe_safety_map.md).
2. Score 9 components (per change).
3. Verify per-component minima for the tier.
4. Append row to .recovery/calibration.jsonl.

Aggregate to engagement-level score using code_fixer_confidence.md.

Output to {{state_dir}}/scoring.md.
Append verdict row to {{state_dir}}/state.jsonl.

If aggregate < tier-floor, this triggers the adversarial edge per workflow_dag.md.
```

## Phase: doc-pass

```
You are running the doc-pass phase.

Repo: {{repo}}

Verify or create:
- CLAUDE.md (or AGENTS.md) per form-check.skill/templates/CLAUDE.md_scaffold.md
- README.md per applicable archetype (form-check.skill/templates/README_archetypes/{cli,library,service,monorepo}.md)
- CHANGELOG.md per form-check.skill/templates/CHANGELOG_template.md
- SECURITY.md per form-check.skill/templates/SECURITY.md_template.md
- ARCHITECTURE.md per form-check.skill/templates/ARCHITECTURE.md_template.md (if applicable)
- ROADMAP.md per form-check.skill/templates/ROADMAP.md_template.md (if applicable)
- docs/adr/ baseline (≥1 ADR; create 0001-baseline if absent)

Apply per-archetype voice rules (recovery.skill/templates/doc_voice.md).

Output to {{state_dir}}/doc_pass.md (list of changes proposed/applied).
Append verdict row to {{state_dir}}/state.jsonl.
```

## Phase: deAI-sweep

```
You are running the deAI-sweep phase.

Inputs: doc files modified in doc-pass; existing project prose
Rules: recovery.skill/templates/deai_rules.md

Run the base banned-vocab regex over all repo .md files except references/ and examples/.
Apply per-archetype overlay per file path.

For each hit:
- File:line
- Term flagged
- Concrete property suggestion (replace adjective with measured property)

Apply suggested fixes via edit; preserve meaning; do not change content beyond voice.

Output to {{state_dir}}/deai_sweep.md.
Append verdict row to {{state_dir}}/state.jsonl.
```

## Phase: adversarial

```
You are running the adversarial phase.

Walk recovery.skill/workflow/adversarial_questions.md (all 12).

For each question, produce: pass | fail | n/a-with-reason; with evidence reference.

If any fail: feed finding back into review (loop edge per workflow_dag.md), with hard cap of 2 loops.

Output to {{state_dir}}/adversarial.md (one section per question).
Append verdict row to {{state_dir}}/state.jsonl.
```

## Phase: launch-ready

```
You are running the launch-ready phase. (Only for engagement_type == "harden".)

Walk recovery.skill/checklists/launch_ready.md DoD per project archetype.

Each item: pass | fail | n/a-with-reason; evidence link.

Output to {{state_dir}}/launch_ready.md.
Append verdict row to {{state_dir}}/state.jsonl.
```

## Phase: summary

```
You are running the summary phase.

Inputs: all {{state_dir}}/*.md, {{state_dir}}/state.jsonl

Produce {{state_dir}}/summary.md (one page; ≤500 words):
- Engagement type + duration
- Engagement-aggregate score + tier verdict
- Top 3 findings (highest-leverage P0/P1)
- Top 3 deferred items (Won't-do or Next-cycle)
- Doc deltas (one-line per file)
- Calibration log row count for this engagement
- Recommended next engagement (if any)

Append final verdict row to {{state_dir}}/state.jsonl.
```

## Anti-patterns

- Hard-coded paths in any prompt (drift across hosts).
- "Output to your scratch dir" without parameterization.
- Skipping verdict-row writes (state ledger goes stale).
- Embedding the entire INDEX / OWASP / WCAG content in the prompt instead of file references (token waste).
