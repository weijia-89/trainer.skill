# recovery, vibe-coded → shippable; the conditioning back to form

End-to-end "vibe-coded to shippable" engagement skill. Composes [`form-check.skill`](../form-check.skill) with a deAI sweep under a single DAG workflow.

## What this is (and isn't)

- **Is**: an opinionated workflow that takes a project from "needs hardening" to shippable. Discovers, reviews, scores, doc-passes, voice-cleans, declares launch-ready (or escalates a gap report).
- **Is**: a composition skill, pins `form-check@>=2.0.0,<3.0.0` and adds workflow on top.
- **Is not**: a code generator. Does not write feature code.
- **Is not**: a substitute for security audit on vibe-dangerous surfaces.

## Install

Place under your agent's skills directory alongside `form-check.skill/`. The two are co-deployed.

## Use

`apply recovery on /path/to/project [--engagement-type {harden|new-app|review|deprecate}]`

Default engagement type: `harden`.

## Workflow

DAG (single source of truth in `workflow/workflow_dag.md`):

```
discovery ─┐
           ├─→ scoring ─→ doc-pass ─→ deAI-sweep ─→ launch-ready ─→ summary
review ────┘                                       ↑
                                                   └── adversarial (loops if score < tier-floor)
```

Each phase emits one artifact and one verdict row to `.recovery/state.jsonl`.

## Layout

```
SKILL.md                        # ≤200 lines; pinned to form-check@>=2.0.0,<3.0.0
references/notes.md             # extends form-check's references
rubrics/code_fixer_confidence.md    # composes form-check rubric + 2 engagement-specific
checklists/launch_ready.md      # DoD per archetype
templates/
  deai_rules.md                 # base banned-vocab + per-archetype overlays
  doc_voice.md                  # per-archetype voice rules
workflow/
  workflow_dag.md               # canonical DAG
  adversarial_questions.md      # 12 axis-segmented
  phase_prompts.md              # env-agnostic; parameterized output paths
examples/
  full-engagement-trace.md
tests/                          # skill self-tests
```

## Versioning

Semantic Versioning. The composes pin in `SKILL.md` declares the compatible `form-check` range. CHANGELOG documents what triggers MAJOR / MINOR / PATCH.

## Compose with `form-check`

`recovery` does not duplicate `form-check`'s rubrics or checklists. It pins a version range and references files by path. If `form-check`'s pinned components change MAJOR version, `tests/test_skill_version_compat.py` fails.

## Output spec

Every engagement produces:

```
<project>/
  .recovery/
    state.jsonl         # structured per-phase verdicts
    calibration.jsonl   # per scored change (feeds form-check's calibration log)
    summary.md          # one-page human summary
  docs/
    [archetype-specific docs created/updated]
```

## Contributing

See `CONTRIBUTING.md`.

## License

MIT, see `LICENSE`.
