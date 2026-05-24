# SDK merge gate — codereview surfaced on GitHub

Canonical scripts live in `~/Projects/cursor-sdk-playground/scripts/`.

## Pipeline order

1. `_sdk_verify_and_pr.sh` — product verify (+ optional `CHANGELOG.md` / `README.md` commit)
2. `_sdk_trainer_codereview.sh` — `run_agent.py` + `prompts/_sdk_codereview.txt` (trainer → form-check + review-rigor)
3. `git push`
4. `_sdk_surface_codereview_to_pr.sh` — mirror review + PR body embed + **post or in-place update** of the canonical PR comment

## Artifacts

| Location | Purpose |
| -------- | ------- |
| `<repo>/localonly/sdk-reviews/{SDK_QUEUE_ID}-{branch-slug}.md` | Canonical review (gitignored) |
| `cursor-sdk-playground/prompts/reviews/*.md` | Durable mirror for orch / history |
| GitHub PR body | Short verdict + summary (`--variant short`) |
| GitHub PR comment | Full findings; marker `<!-- sdk-codereview-{queue}-{branch} -->` + meta `head=` / `verdict=` |

## PR comment updates (remediate rounds)

After remediate + re-review, `_sdk_surface_codereview_to_pr.sh` **PATCHes** the existing canonical comment when **HEAD** or **verdict** changes (e.g. `REQUEST_CHANGES` → `APPROVE`). It does **not** leave a stale first-pass comment. Skip only when meta matches current branch tip and verdict (`SDK_CODEREVIEW_FORCE_REPOST=1` or `--force` to always PATCH).

Orch re-run on an open PR: `./scripts/_sdk_verify_and_pr.sh` (existing-PR path) or job `*_finish.sh` after remediate.

## Environment

| Variable | Effect |
| -------- | ------ |
| `SDK_QUEUE_ID` | **Required** in job scripts; names the review file |
| `SDK_CODEREVIEW_SKIP=1` | Skip codereview + surfacing (document in queue SSOT) |
| `SDK_CODEREVIEW_STRICT=1` | Fail hook on `REQUEST_CHANGES` (not only `BLOCK`) |
| `SDK_CODEREVIEW_FORCE_REPOST=1` | Always PATCH PR comment even if head+verdict unchanged |
| `SDK_STAKES_TIER` | Passed into codereview prompt |

## Worker rule

Workers do **not** push. The hook owns merge gate + GitHub surfacing. See `prompts/_trainer-worker-preamble.txt` §5–6.
