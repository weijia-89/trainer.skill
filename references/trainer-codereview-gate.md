# Trainer — PR codereview gate (product repos)

**Default path for buds, toebeans, and normal Cursor PR work.** Does not require `cursor-sdk-playground`.

## Iron law

If a change is going to **merge into `buds` or `toebeans`**, it must have a **fresh trainer code review** posted on the PR **HEAD** in the canonical format (see pipeline below).

**Exception (mechanical, CI):** PRs that touch **only** `docs/**` or `research/**` paths ending in `.md` or `.txt` skip the comment gate (`ci-trainer-pr-review-gate-exempt.sh`). Roadmap-only edits are the intended case. Mixed PRs (docs + Kotlin/Swift/workflows/agent files) still require the comment.

## Pipeline (product PR)

0. **User-facing docs (R-6):** If the diff touches `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `SECURITY.md`, or other operator prose, load **`~/Projects/deai.skill/SKILL.md`** and run the full deai loop (voice-prime → restructure → re-scan) on each touched file. Update version tables and layout diagrams to match shipped behavior. `deai-scan.py` alone does not satisfy this step.
1. Implement on feature branch; run repo verify.
2. **trainer** → **form-check** `code-review` per `trainer-codereview.md` (real review body — never empty/stub). On **export delta**, also close obligation **B** per `trainer-contract-surfaces.md` or waive in Bug inventory before APPROVE.
3. Post canonical PR comment: `bash scripts/trainer_pr_review_post.sh <pr#> <verdict> <round> review.md`
4. **Push order (critical):**
   - **Round 1 (preferred):** post comment with `head=` = local `HEAD`, **then** push so the first CI run sees a matching comment.
   - **Remediate:** PATCH comment (`head=` + verdict), **then** push fixes.
   - **Post-after-push:** `trainer_pr_review_post.sh` auto-reruns only the gate job; CI on `main` also reruns gate on `issue_comment` when the marker is present (see below).
5. Push; CI job **Trainer PR review comment gate** must pass (`ci-trainer-pr-review-gate.sh`). **Gradle/Flutter jobs must not `needs:` the gate** — run in parallel (toebeans `build-and-test`, buds `flutter-test`) so build/test signal is not blocked while the comment is missing or stale.
6. Human merge after PR body manual scenarios pass and all required checks green.

## Auto-rerun (durable fix)

| Mechanism | When |
|-----------|------|
| `trainer_pr_review_post.sh` → `trainer_pr_review_gate_rerun.sh` | After every successful POST/PATCH; reruns **only** job `Trainer PR review comment gate` if not already green (idempotent). |
| `.github/workflows/trainer-gate-rerun.yml` | On PR `issue_comment` create/edit containing `trainer-codereview-{repo}-`; belt-and-suspenders when comment is edited in the UI. Uses workflow file on **default branch** once merged. **Security:** `author_association` OWNER\|MEMBER only; wait loop keyed to PR `headRefOid` (SHA), not branch — template `references/templates/trainer-gate-rerun.yml`. |

**Manual dry-run (no API rerun):**

```bash
TRAINER_GATE_RERUN_DRY_RUN=1 bash scripts/trainer_pr_review_gate_rerun.sh <pr#> owner/repo
```

**Skip rerun (tests):** `TRAINER_GATE_RERUN_SKIP=1`

## Canonical files (trainer.skill)

| File | Role |
|------|------|
| `references/trainer-codereview.md` | Review routing, verdicts, findings shape |
| `references/trainer-contract-surfaces.md` | Export delta; obligations A/B/C; contract-surface closure bounds |
| `references/trainer-github-pr-commentary.md` | PR body test plan + Trainer notes comment template |
| `scripts/trainer_manual_test_block.sh` | Canonical device cold-start + launch (`buds` iOS-first from `localonly/trainer/` when present; `toebeans` Gradle); `--scenario` for in-app paths; errors on stack vs git-root mismatch. See `references/buds-manual-testing.md`. |
| `scripts/ci-trainer-pr-review-gate.sh` | Copy to product repo `scripts/` |
| `scripts/ci-trainer-pr-review-gate-exempt.sh` | Docs/research text-only exempt check |
| `scripts/trainer_pr_review_post.sh` | Rejects cross-repo launch commands before POST/PATCH; copy to product repo `scripts/` |
| `scripts/trainer_review_bug_inventory_validate.py` | P0–P4 + full comment contract via `--full`; copy beside gate/post scripts |
| `scripts/trainer_review_comment_validate.py` | Local validate review comment file |
| `scripts/trainer_pr_body_validate.py` | PR body Test plan gate |
| `scripts/verify_trainer_codereview.sh` | Self-test: round-1 theater fixture must FAIL |
| `scripts/trainer_pr_r6_validate.py` | R-6 user-facing docs coverage (code diff vs CHANGELOG/README/ROADMAP/SECURITY) |
| `.github/workflows/trainer-pr-review-gate.yml` | trainer.skill PR CI gate |
| `scripts/trainer_pr_review_gate_rerun.sh` | Copy to product repo `scripts/` |
| `scripts/test_ci_trainer_pr_review_gate.sh` | Copy to product repo `scripts/` |
| `scripts/test_trainer_pr_review_gate_rerun.sh` | Optional smoke test (skip/dry-run) |
| `references/templates/trainer-gate-rerun.yml` | Hardened workflow template (P1-2: author_association + SHA pin) |

## Reference install

**toebeans** — CI in `.github/workflows/ci.yml`; gate rerun workflow `trainer-gate-rerun.yml`; contract in `AGENTS.md` / `CLAUDE.md`. `build-and-test` depends only on `fitness-functions`.

**buds** — gate parallel to `flutter-test`; same scripts + `trainer-gate-rerun.yml`.

## Remediate rounds

1. Fix P0–P(n) per repo policy (toebeans P0–P3; buds P0–P4).
2. Push; re-run verify.
3. **PATCH** same PR comment (`trainer_pr_review_post.sh`); update `head=` and verdict; script reruns gate if needed.

## SDK weekend playground (archived one-off)

`~/Projects/cursor-sdk-playground/` was a **batch orchestration** repo (`_sdk_verify_and_pr.sh`, `weekend-queue.md`, `run_agent.py`). **Do not** route daily product PRs or global trainer rules through it.

If replaying SDK weekend mechanics, read playground `sdk-ssot-2.md` — but new work should use this document + product-repo scripts above.

Legacy playground prompt `_sdk_codereview.txt` is deprecated; canonical prompt is `trainer.skill/prompts/trainer-codereview.txt`.
