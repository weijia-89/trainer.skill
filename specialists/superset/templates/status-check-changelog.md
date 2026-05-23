# Status check + CHANGELOG / README (orch iron law)

Use on every **status check** (operator says "check status", "refresh queue", "where are we", or equivalent). Canonical spec: `superset.skill` § **Status check + changelog/README iron law**.

## Chat reply (orch window)

- **One line only:** point to the coordination SSOT path (e.g. `~/Projects/cursor-sdk-playground/weekend-queue.md`). Do not rehash tables, accomplishments, or kickoff blocks in chat.

## Required updates (same turn, before claiming status check done)

For each repo whose shipped state **changed** since the last status check (merge, PR opened/merged, local commit ready for review):

| Artifact | Action |
| -------- | ------ |
| `CHANGELOG.md` | Add or extend `[Unreleased]` (or dated section) with user-facing bullets: what changed, why it matters, verification command if non-obvious |
| `README.md` | Update "Recent work" / "Development status" (or create ≤8 lines there) — same facts, shorter than CHANGELOG |
| Coordination SSOT | Refresh queue section (SDK: `weekend-queue.md` § **Changelog source** + status tables + work history **Accomplishment** column) |
| `localonly/daily/<YYYY-MM-DD>.md` | If multi-agent day active: append status row or EOD bullets under the track |

**Prose gate:** Draft changelog/README copy with **deai** discipline (voice prime, no RLHF residue, facts from git/PR only). Changelog source blocks in the queue are the staging area; product `CHANGELOG.md` / `README.md` are what ship to contributors.

## Evidence (run before writing claims)

```bash
# Per repo touched
git -C <repo> fetch origin -q
git -C <repo> status -sb
git -C <repo> log origin/main -1 --oneline
# If PR involved
gh pr view <n> --repo <owner/repo> --json state,mergeCommit,title
```

## Accomplishment note shape (for queue / daily log)

Each shipped or review-ready item gets **three layers** (copy into work history or § Changelog source):

1. **Behavior** — what the user or operator can do now that they could not before.
2. **Scope** — primary files/modules; explicit "not included" when scope creep is likely.
3. **Verification** — exact command(s) that passed before merge or review.

## SDK weekend (cursor-sdk-playground)

1. `./scripts/queue_status.sh`
2. `git status` on buds, toebeans, oncology-rag-lab
3. `gh pr view` for any open PRs in Active table
4. Update **only** `weekend-queue.md` + push playground; update each affected product repo `CHANGELOG.md` + `README.md` when merges land
5. Chat: "Queue @ `<sha>` — open `weekend-queue.md`."

## Worker handoff

Workers do **not** edit product `CHANGELOG.md` / `README.md` unless the job prompt says so. On DONE, workers append proposed changelog bullets to `localonly/daily/<date>.md` under their track; **orch** folds into product docs on the next status check.
