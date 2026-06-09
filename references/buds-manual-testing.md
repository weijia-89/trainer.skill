# Buds manual testing (trainer carveout)

When reviewing **`weijia-89/buds`** PRs, manual QA launch commands belong in the **initial PR body**, not in every code-review comment.

## Default PR template (2026-06)

| When | Where commands live |
| ---- | ------------------- |
| **PR open** | **PR body** — `### Manual — setup` with full copy-paste bullets |
| **Trainer round 1** | Comment pointer to PR body (+ one-liner `flutter run` for post script) |
| **Trainer round 2+** | Delta commands only when testing needs them |
| **Cycle comments** | Commands only when assisting that round’s test |

| File | Role |
| ---- | ---- |
| `docs/trainer/pr-test-plan-template.md` | Tracked copy (buds repo) |
| `~/Projects/trainer.skill/references/templates/buds-pr-test-surfaces.md` | Canonical (trainer.skill) |

Run `bash scripts/pr_body_validate.sh` on PR body files before `gh pr edit`.

## Snippet helper (on demand)

```bash
bash ~/Projects/trainer.skill/scripts/trainer_manual_test_block.sh buds --platform ios
```

Use when drafting PR body setup or when a remediate round needs a **delta** block — not pasted into every trainer PATCH.

## PR rules

1. **Load** `docs/trainer/pr-test-plan-template.md` when opening a PR or when a review round changes how you test.
2. **PR body at open:** automated checkboxes + **setup commands** + scenario checkboxes.
3. **Trainer canonical comment:** Bug inventory + Trainer notes; Manual QA = PR body pointer unless catch-up/delta needed.
4. **Forbidden:** repeating full cold-start boilerplate on every remediate PATCH.
5. **Forbidden** on buds PRs: toebeans Gradle launch paths.

See: `references/trainer-github-pr-commentary.md`.
