# SDK merge gate — codereview surfaced on GitHub

Canonical scripts live in `~/Projects/cursor-sdk-playground/scripts/`.

## Pipeline order

1. `_sdk_verify_and_pr.sh` — product verify (+ optional `CHANGELOG.md` / `README.md` commit)
2. `_sdk_trainer_codereview.sh` — `run_agent.py` + `prompts/_sdk_codereview.txt` (trainer → form-check + review-rigor)
3. `git push`
4. `_sdk_surface_codereview_to_pr.sh` — mirror review + PR body embed + `gh pr comment`

## Artifacts

| Location | Purpose |
| -------- | ------- |
| `<repo>/localonly/sdk-reviews/{SDK_QUEUE_ID}-{branch-slug}.md` | Canonical review (gitignored) |
| `cursor-sdk-playground/prompts/reviews/*.md` | Durable mirror for orch / history |
| GitHub PR body | Short verdict + summary (`--variant short`) |
| GitHub PR comment | Full findings (`--variant full`), marker `<!-- sdk-codereview-… -->` |

## Environment

| Variable | Effect |
| -------- | ------ |
| `SDK_QUEUE_ID` | **Required** in job scripts; names the review file |
| `SDK_CODEREVIEW_SKIP=1` | Skip codereview + surfacing (document in queue SSOT) |
| `SDK_CODEREVIEW_STRICT=1` | Fail hook on `REQUEST_CHANGES` (not only `BLOCK`) |
| `SDK_STAKES_TIER` | Passed into codereview prompt |

## Worker rule

Workers do **not** push. The hook owns merge gate + GitHub surfacing. See `prompts/_trainer-worker-preamble.txt` §5–6.
