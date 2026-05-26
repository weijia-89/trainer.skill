# Status check + CHANGELOG / README (orch iron law)

Use on every **status check** (operator says "check status", "refresh queue", "where are we", or equivalent). Canonical spec: `superset.skill` § **Status check + changelog/README iron law**.

## Chat reply (orch window)

- **One line only:** point to the coordination SSOT path (e.g. `<repo>/localonly/daily/<YYYY-MM-DD>.md`). Do not rehash tables, accomplishments, or kickoff blocks in chat.

## Required updates (same turn, before claiming status check done)

For each repo whose shipped state **changed** since the last status check or job closeout (merge, PR opened/merged, local commit ready for review):

| Artifact | Action |
| -------- | ------ |
| `CHANGELOG.md` | Add or extend `[Unreleased]` (or dated section) with user-facing bullets: what changed, why it matters, verification command if non-obvious |
| `README.md` | Update "Recent work" / "Development status" (or create ≤8 lines there) — same facts, shorter than CHANGELOG |
| Roadmap doc(s) | Grep per repo (`rg -l -i roadmap docs/ .`); edit `docs/strategy/ROADMAP.md`, `docs/ROADMAP.md`, or project path — **shipped vs planned** must match merge/PR evidence after closeout |
| Coordination SSOT | Refresh daily log or project queue (§ **Changelog source** + status tables + **Accomplishment** column) |
| `localonly/daily/<YYYY-MM-DD>.md` | If multi-agent day active: append status row or EOD bullets under the track |

**Prose gate:** Draft changelog/README/roadmap copy with **deai** discipline (voice prime, no RLHF residue, facts from git/PR only). Changelog source blocks in the queue are the staging area; product `CHANGELOG.md`, `README.md`, and roadmap files are what ship to contributors.

## Evidence (run before writing claims)

```bash
# Per repo touched
git -C <repo> fetch origin -q
git -C <repo> status -sb
git -C <repo> log origin/main -1 --oneline
# If PR involved
gh pr view <n> --repo <owner/repo> --json state,mergeCommit,title,mergeable,mergeStateStatus
# Before spawning a 2nd agent on same repo: mergeable must be MERGEABLE (superset v0.8.4 § main integration gate)
```

## Accomplishment note shape (for queue / daily log)

Each shipped or review-ready item gets **three layers** (copy into work history or § Changelog source):

1. **Behavior** — what the user or operator can do now that they could not before.
2. **Scope** — primary files/modules; explicit "not included" when scope creep is likely.
3. **Verification** — exact command(s) that passed before merge or review.

## Worker handoff

Workers do **not** edit product `CHANGELOG.md`, `README.md`, or roadmap files unless the job prompt says so. On DONE, workers append proposed changelog and roadmap deltas to `localonly/daily/<date>.md` under their track; **orch** folds into product docs and roadmap on the next status check or closeout.
