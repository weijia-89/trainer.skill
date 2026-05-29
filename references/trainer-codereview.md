# Trainer — code review (form-check + review-rigor)

Canonical spec for **all** trainer-routed PR reviews (Cursor sessions, product repos, CI-gated PRs). **Not** tied to `cursor-sdk-playground`.

## Routing (mandatory)

1. **trainer** — coach stance; do not expand scope beyond the diff **except** contract-surface closure per step 3 when export delta (see `trainer-contract-surfaces.md`).
2. **form-check** — `code-review` / `adversarial-review` on the PR diff. Stakes from repo `AGENTS.md` / `CLAUDE.md`.
3. **contract surfaces** — when export delta: obligation **B** in `trainer-contract-surfaces.md` (declared surfaces only; bounded grep/read for OLD public symbols).
4. **review-rigor** — opening audit + rubric (SEC, COR, ARC, PRF, TST). Per-finding scorecard; ship threshold per stakes tier.

Read `~/Projects/trainer.skill/SKILL.md` and `~/Projects/trainer.skill/references/trainer-github-pr-commentary.md` before posting on GitHub.

## Inputs

| Input | Source |
|-------|--------|
| Repo root | Engagement repo (e.g. `~/Projects/toebeans`) |
| Branch | Current PR branch |
| Diff | `git diff origin/main...HEAD` or `gh pr diff` |
| Verify | Repo script (`./gradlew …`, `bash scripts/verify_*.sh`) |

## Review artifact (local, optional)

For multi-round work, write:

`<repo>/localonly/trainer-reviews/<branch-slug>-round<N>.md`

Use ranked findings `### T{n} · P{0-4} · {rubric} · conf N%`. **buds:** fix or waive every **P0–P4** before APPROVE. **toebeans:** **P0–P3** before APPROVE.

## Verdict rules

| Verdict | When |
|---------|------|
| **BLOCK** | Data loss, crypto/event corruption, missing tests on vibe-careful+ behavior, invented APIs, scope violation, COR ≥90% |
| **REQUEST_CHANGES** | Should fix before merge; no active corruption (spec drift, weak UX, missing widget test) |
| **APPROVE** | Meets tier floor; residual nits non-blocking; if export delta, obligation **B** closed or explicitly waived in Bug inventory with contract-surface file list |

## GitHub surfaces (mandatory for buds / toebeans)

1. **PR body** — granular `## Test plan` (numbered manual steps: repo path, launch, cold start, expected UI). See `trainer-github-pr-commentary.md`.
2. **PR comment** — one canonical comment per PR:
   - Marker: `<!-- trainer-codereview-{repo}-{branch-slug} -->`
   - Meta: `<!-- head={7-char-sha} verdict=… round={N} -->`
   - `### Bug inventory` (every P0–P4 row or explicit none) + `### Trainer notes` (**Program notes**, **Your form**, **Next session**)
   - Never `### Pedagogy` or `### Cool-down`
3. **Post / PATCH:** `<repo>/scripts/trainer_pr_review_post.sh` (copy from `trainer.skill/scripts/`).

## Mechanical enforcement

Product repos wire `scripts/ci-trainer-pr-review-gate.sh` in CI. Detail: `trainer-codereview-gate.md`.

## Forbidden

- Approving without reading changed bodies for behavior PRs.
- **APPROVE** on export delta without obligation **B** closure or explicit Bug inventory waive row (file list per `trainer-contract-surfaces.md`).
- Skipping review-rigor on P1/P2.
- Drive-by refactors or new deps.
- Test plans that only say "cold start" without launch steps.
- PR comments without Trainer notes on trainer-gated repos.

## Agent prompt template

`~/Projects/trainer.skill/prompts/trainer-codereview.txt` (substitute repo/branch paths when spawning agents).
