# Trainer — PR codereview gate (product repos)

**Default path for buds, toebeans, and normal Cursor PR work.** Does not require `cursor-sdk-playground`.

## Iron law

If a change is going to **merge into `buds` or `toebeans`**, it must have a **fresh trainer code review** posted on the PR **HEAD** in the canonical format (see pipeline below). No exceptions.

## Pipeline (product PR)

1. Implement on feature branch; run repo verify.
2. **trainer** → **form-check** `code-review` per `trainer-codereview.md`.
3. Post canonical PR comment: `bash scripts/trainer_pr_review_post.sh <pr#> <verdict> <round> review.md` **before** the push that should pass CI (round 1: post then push; remediate: PATCH `head=` then push).
4. Push; CI job **Trainer PR review comment gate** must pass (`ci-trainer-pr-review-gate.sh`). **Gradle/build jobs must not `needs:` the gate** — run in parallel (see toebeans/buds `ci.yml`) so compile/test signal is not skipped while the comment is missing or stale.
5. Human merge after PR body manual scenarios pass and all required checks green.

## Canonical files (trainer.skill)

| File | Role |
|------|------|
| `references/trainer-codereview.md` | Review routing, verdicts, findings shape |
| `references/trainer-github-pr-commentary.md` | PR body test plan + Trainer notes comment template |
| `scripts/ci-trainer-pr-review-gate.sh` | Copy to product repo `scripts/` |
| `scripts/trainer_pr_review_post.sh` | Copy to product repo `scripts/` |
| `scripts/test_ci_trainer_pr_review_gate.sh` | Copy to product repo `scripts/` |

## Reference install

**toebeans** — CI wired in `.github/workflows/ci.yml`; contract in `AGENTS.md` / `CLAUDE.md`. `build-and-test` depends only on `fitness-functions`, not the trainer gate.

**buds** — gate job parallel to `flutter-test` (no `needs` edge); same scripts when enabling elsewhere.

## Remediate rounds

1. Fix P0–P(n) per repo policy (toebeans P0–P3; buds P0–P4).
2. Push; re-run verify.
3. **PATCH** same PR comment (`trainer_pr_review_post.sh`); update `head=` and verdict.

## SDK weekend playground (archived one-off)

`~/Projects/cursor-sdk-playground/` was a **batch orchestration** repo (`_sdk_verify_and_pr.sh`, `weekend-queue.md`, `run_agent.py`). **Do not** route daily product PRs or global trainer rules through it.

If replaying SDK weekend mechanics, read playground `sdk-ssot-2.md` — but new work should use this document + product-repo scripts above.

Legacy playground prompt `_sdk_codereview.txt` is deprecated; canonical prompt is `trainer.skill/prompts/trainer-codereview.txt`.
