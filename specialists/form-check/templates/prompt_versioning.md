---
name: prompt_versioning
version: 2.0.0
parent_skill: form-check
addresses: smell_catalog "prompt rev drifted; eval gate didn't catch"
---

# Prompt Versioning

Treat LLM prompts as a versioned artifact. Without versioning + eval gating, prompt drift is silent, model behavior changes between PRs and the eval baseline can't tell you which change caused the regression.

## File layout

```
prompts/
  generate_summary/
    v1.md             # archived
    v2.md             # archived
    v3.md             # current (active)
    CHANGELOG.md
    schema.json       # output JSON schema
    eval/
      golden.json     # golden dataset (50–100 cases)
      baseline.json   # last-accepted metrics
```

## SemVer for prompts

| Level | Trigger | CI behavior |
|---|---|---|
| **PROMPT-MAJOR** | Behavior change (output shape changes; new capability; removed capability) | Blocks merge until human reviews the new baseline; full eval re-run; staged rollout 1%→10%→50%→100% |
| **PROMPT-MINOR** | Accuracy improvement; same output shape; non-breaking new instruction | Eval re-run; baseline updated with PROMPT-MINOR delta noted |
| **PROMPT-PATCH** | Typo, formatting, instruction-tone wording | Light eval re-run; baseline unchanged |

Mirrors SemVer for libraries. The reasoning is the same: consumers (downstream code, tests, fitness functions, eval baselines) need to know whether an update is safe to take silently.

## Per-prompt CHANGELOG

```markdown
# CHANGELOG, generate_summary prompt

## [v3] - 2026-05-12
### MAJOR
- Output shape changed: now includes `confidence_score` field per item.
- Eval baseline reset; new baseline at `eval/baseline.json` after re-run.
- Migration: consumers must update their JSON schema validator.

## [v2] - 2026-04-01
### MINOR
- Added "do not invent citations" instruction.
- Eval improvement: hallucination rate 8% → 2% on golden set.

## [v1] - 2026-03-15
### Initial
- Generate executive-summary bullets from input document.
```

## Eval-gate semantics

For PROMPT-MAJOR or PROMPT-MINOR PRs:

```yaml
# .github/workflows/prompt-eval.yml
name: prompt-eval
on: [pull_request]
jobs:
  eval:
    if: contains(github.event.pull_request.changed_files, 'prompts/')
    steps:
      - uses: actions/checkout@v4
      - run: |
          python tools/run_eval.py \
            --prompt prompts/generate_summary/v3.md \
            --golden prompts/generate_summary/eval/golden.json \
            --baseline prompts/generate_summary/eval/baseline.json \
            --regression-threshold 0.02
      # CI fails if any metric regressed > 2pp vs baseline.
```

Baseline updates require:
- Manual review of the new metrics
- Justification in the PR description
- A row in the prompt's CHANGELOG

## Anti-patterns

- **Inline prompt strings in code**: prompts not versioned; can't roll back.
- **Auto-update of baseline by CI**: defeats the gate. Manual review only.
- **Patch-level prompt edits with no eval run**: risk of silent regression.
- **Single-prompt project with no CHANGELOG**: every change is silent drift.
- **Eval golden set committed but never re-evaluated**: stale; defeats its purpose. Quarterly review or trigger-based.
- **Asserting on exact prompt strings in tests**: brittle; tests should assert *behavior*, not prompt text.

## Cross-references

- Smell catalog month-3: "Prompt rev drifted; eval gate didn't catch"
- OWASP-LLM03 (Supply Chain): treat prompts as versioned dependencies
- OWASP-LLM04 (Data and Model Poisoning): golden-set provenance matters
