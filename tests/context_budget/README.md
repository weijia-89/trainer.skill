# Context budget (trainer root SKILL.md)

**Scope:** build-time linter on root `trainer.skill/SKILL.md` file size — **not** runtime context %, **not** `diet` routing. For runtime skills % in chat, use Cursor 3.3+ native context breakdown; for phylax pre-audit budget, use `phylax.skill/scripts/token_budget_audit.sh` (operator paste).

## Why this exists

Broad always-loaded context often increases cost and steps without improving outcomes (AGENTS.md synthesis; SkillsBench paired-treatment critique; SMART overuse measurement). Root `SKILL.md` must stay **route and gate** content only; operational depth belongs in specialist leaf files loaded on demand.

## Run

```bash
cd ~/Projects/trainer.skill
python3 tests/context_budget/measure_context.py SKILL.md
python3 tests/context_budget/check_context_budget.py
python3 tests/context_budget/test_check_context_budget.py
bash scripts/verify_trainer_sync.sh
```

## Interpret warnings

- `VERDICT=WARN` with `WARN_ONLY=true`: budget exceeded but CI does not fail.
- Section-level warnings flag headings that grew too large for always-on load.
- Est tokens are **heuristic**, not exact tokenizer counts.

## Rule for new root content

Before adding prose to root `SKILL.md`, ask:

1. Is it needed for first-pass routing or gating without opening a specialist?
2. Can it live in `~/Projects/trainer.skill/references/trainer-runtime-compactness.md` or a specialist `references/` file?
3. Does the token cost beat loading the specialist on demand?

If (2) applies, do not add to root.

## Ratification

Set `warn_only = false` in `budget.toml` only after Wei explicitly approves hard caps.
