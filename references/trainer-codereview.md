# Trainer — code review (form-check + review-rigor)

Canonical spec for **all** trainer-routed PR reviews (Cursor sessions, product repos, CI-gated PRs). **Not** tied to `cursor-sdk-playground`.

**Default loop:** also load `trainer-autonomous-code-review.md` — explore callers, trace logic, run harnesses, fix until clean (not single-pass skim).

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

1. **PR body (at open)** — granular `## Test plan`: setup commands + scenario checkboxes. See `trainer-github-pr-commentary.md` and `templates/buds-pr-test-surfaces.md`.
2. **PR comment** — one canonical comment per PR:
   - Marker: `<!-- trainer-codereview-{repo}-{branch-slug} -->`
   - Meta: `<!-- head={7-char-sha} verdict=… round={N} -->`
   - `### Bug inventory` (every P0–P4 row or explicit none) + `### Trainer notes` (**Program notes**, **Your form**, **Next session**)
   - Never `### Pedagogy` or `### Cool-down`
3. **Post / PATCH:** `<repo>/scripts/trainer_pr_review_post.sh` (copy from `trainer.skill/scripts/`).
4. **Post-comment verify (after step 3):** Run automated commands from the PR test plan; **PATCH** the same comment with `### Automated verification` checked + `### Sign-off` automated `[x]`; check off PR body automated boxes. Detail: `trainer-github-pr-commentary.md` § Post-comment automated verify loop.

## Mechanical enforcement

Product repos wire `scripts/ci-trainer-pr-review-gate.sh` in CI. Detail: `trainer-codereview-gate.md`.

**R-6 (user-facing docs):** On APPROVE, `ci-trainer-pr-review-gate.sh` and `trainer_pr_review_post.sh` call `trainer_pr_r6_validate.py`. If the PR diff touches `SKILL.md`, `scripts/`, `references/`, `prompts/`, `.github/`, `specialists/`, or `mirrors/` (excluding `tests/` only), at least one of `CHANGELOG.md`, `README.md`, `ROADMAP.md`, `SECURITY.md`, or `docs/` must change, or the review comment must include an explicit R-6 waive row. APPROVE with doc updates requires R-6/deai closure text in the canonical comment.

## Artifact vs product code (R-5)

| PR touches | Route | Codereview rubric (SEC/COR/ARC/PRF/TST) |
|------------|-------|----------------------------------------|
| Product code (with or without skill files) | `form-check code-review` on **code diff**; explicit **phylax** on skill/prompt/packet diff if present | Yes — on product code |
| **Only** skill/prompt/packet paths (`.cursor/skills/`, `*.skill/`, piranesi packets) | Explicit **phylax** artifact review — load `~/Projects/phylax.skill/references/trainer-routing.md` | **No** — phylax deliverable replaces product rubric on skill-only diffs |
| `AGENTS.md` / `CLAUDE.md` | `form-check` + gate comment still required (`ci-trainer-pr-review-gate-exempt.sh` never exempts these) | Yes |

## User-facing docs (R-6)

When the PR diff touches operator prose, update and deai-edit **before** APPROVE:

| Path (typical) | Required action |
|----------------|-----------------|
| `README.md` | Routing table, layout diagram, install steps match shipped behavior |
| `CHANGELOG.md` | `[Unreleased]` or version section documents every user-visible change |
| `ROADMAP.md` | Current version + shipped vs deferred items |
| `SECURITY.md` | Supported version table when the release line moves |
| Other operator-facing Markdown at repo root or `docs/` | Same bar when the diff changes how operators install, verify, or report issues |

**deai (full skill, iron law):** `file_read` `~/Projects/deai.skill/SKILL.md` (or `~/.cursor/skills/deai/` after sync). Run voice-prime → restructure → re-scan until voice holds. Running `deai-scan.py` alone is **not** sufficient and does not satisfy R-6.

**PR workflow:** step 1 in `trainer-codereview-gate.md` pipeline. List updated doc paths in the PR comment Bug inventory or Trainer notes when non-obvious.

Mixed PRs: one trainer PR comment + separate phylax output when skill files change; do not apply SEC/COR rubric to YAML frontmatter in skill trees.

## Forbidden

- Test plans or manual QA that name UI states demo/fixtures cannot reach (see `trainer-test-data.md`).
- Approving without reading changed bodies for behavior PRs.
- **APPROVE** on export delta without obligation **B** closure or explicit Bug inventory waive row (file list per `trainer-contract-surfaces.md`).
- Skipping review-rigor on P1/P2.
- Drive-by refactors or new deps.
- Device-touching PRs whose **initial body** says "cold start" without copy-paste setup commands.
- Trainer remediate comments that repeat full launch boilerplate without a testing reason.
- PR comments without Trainer notes on trainer-gated repos.
- Applying product codereview rubric (SEC/COR/ARC) to **skill-only** PRs without explicit phylax artifact review (R-5).
- Routing context-budget or runtime context-% questions to `diet` — use `check_context_budget.py` (build-time) or Cursor native breakdown.

## Agent prompt template

`~/Projects/trainer.skill/prompts/trainer-codereview.txt` (substitute repo/branch paths when spawning agents).
