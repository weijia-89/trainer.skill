# Trainer — code review loop (default)

**When:** operator requests **code review** (PR review, review the diff, review before merge, adversarial review on a branch).

This is the **default** trainer behavior for code review — not a separate mode. Trainer routes; agent executes the loop until the stop condition.

## Routing (mandatory)

1. **trainer** — coach stance; scope = PR diff + contract surfaces if export delta (`trainer-contract-surfaces.md`).
2. **form-check** — **`file_read` `~/Projects/trainer.skill/specialists/form-check/SKILL.md`** before reviewing; run **`code-review`** or **`adversarial-review`** on the diff per form-check Section 7. Naming form-check without loading the specialist leaf is theater.
3. **review-rigor** — SEC, COR, ARC, PRF, TST scorecard per finding (`~/Projects/trainer.skill/references/trainer-codereview.md` routing).
4. **Skill-only / artifact PRs** — explicit **phylax** per `trainer-codereview.md` R-5.

Read `trainer-codereview.md` + `trainer-github-pr-commentary.md` before posting on GitHub.

## Review loop (iron law)

**Novelty gate (mandatory):** every pass MUST call the surface tracker. Before
POST/PATCH and before claiming a stop, run:

```bash
python3 ~/Projects/trainer.skill/scripts/reviewer_surface_tracker.py \
    --branch <branch-slug> --pass N check --novelty-min 0.50
```

and `--record` a manifest of the surface touched (paths, `path:symbol`,
`verify_exit_codes`) each pass. The gate fails (exit 2) if the pass re-traces
≥50% already-seen surface. A pass that does not call `--check` is not a pass.

Repeat until the stop condition below is explicitly satisfied:

```
PASS N:
  1. READ   — diff HEAD vs base; read every changed file body (not stat-only)
  2. EXPLORE — grep/codebase_search for callers, mirrors, scripts, tests of new symbols
  3. TRACE  — follow new logic paths; list falsifiers and bypass routes
  4. TEST   — run repo verify scripts + new/changed unit tests
  5. RECORD — reviewer_surface_tracker.py --record (surface touched this pass)
  6. CHECK  — reviewer_surface_tracker.py --check (novelty >= 0.50 else re-trace)
  7. FIND   — ranked Bug inventory (P0–P4); no "LGTM" without evidence
  8. FIX    — fix every non-waived finding in-tree; add tests for bug classes found
  9. VERIFY — re-run tests; confirm fixes on disk
 10. STOP?  — evaluate stop condition below; else PASS N+1
```

**Stop condition:** terminate ONLY when the tracker reports
`unexplored == 0` (the union of all pass surfaces covers the diff+seed
universe — requires each `record` to pass `--seed` from `git diff --name-only`
so the universe is known), OR two consecutive passes each satisfy ALL of:
(a) tracker `--check` novelty ≥ 0.50, (b) zero new findings, (c) all verify
commands exit 0. A STOP claimed without the tracker reporting
novelty-satisfied + zero findings is invalid. Without `--seed` the `unexplored`
branch is unreachable and the loop falls back to the two-consecutive-pass bar.

**Forbidden:**

- Single-pass review when operator asked for code review.
- Findings without file:line or runnable falsifier.
- Approving with failing verify scripts.
- Stopping at "no issues in the diff" without exploring new code paths (step 2).
- Posting APPROVE before fixes land on the branch when REQUEST_CHANGES items remain.
- A PASS that does not call the tracker `--check`.
- A STOP claimed without the tracker reporting novelty-satisfied + zero findings.

## Deliverables

| Artifact | When |
|----------|------|
| **PR** | Operator asked for PR — create branch, commit, push, `gh pr create` |
| **User-facing docs** | Diff touches README / CHANGELOG / ROADMAP / SECURITY / operator `docs/` — full **deai** pass (R-6) before APPROVE |
| **PR comment** | Canonical trainer format — `trainer-github-pr-commentary.md`; PATCH on each remediate round |
| **Bug inventory** | Every round; final round lists **fixed in HEAD** with commit or file refs |
| **Automated verification** | `### Automated verification` section with command output summaries |

Comment marker: `<!-- trainer-codereview-{repo}-{branch-slug} -->`  
Meta: `<!-- head={7-char-sha} verdict=APPROVE|REQUEST_CHANGES|BLOCK round={N} -->`

## Verify commands (default)

Run all that apply to the repo:

```bash
# Code review contract (form-check routing + anti-theater)
bash ~/Projects/trainer.skill/scripts/verify_trainer_codereview.sh

# Per-repo harness
python3 scripts/test_*.py
bash scripts/test_*.sh
bash scripts/verify_*.sh --strict   # when present
```

Record exit codes in PR comment **Automated verification** block.

**Mechanical gate (anti-theater):** before POST/PATCH use `bash ~/Projects/trainer.skill/scripts/trainer_pr_review_post.sh` (runs full contract). CI: `ci-trainer-pr-review-gate.sh` on product repos and trainer.skill PRs.

APPROVE is **rejected** when:
- Bug inventory uses placeholder `—` rows + vacuous findings
- Automated verification is grep/`test -f` only (no `verify_*` / `test_*.py` harness)
- PR body Test plan lacks checked harness rows (when gate fetches PR body)

## Severity / merge bar

Per `trainer-github-pr-commentary.md`: buds P0–P4 fix or waive; toebeans P0–P3. Skill/artifact repos: same discipline; no rubber-stamp on harness gaps.

## Related triggers

| Operator says | Behavior |
|---------------|----------|
| code review / review PR / review the diff | **This loop** (default) + PR comment updates |
| @review-rigor | Rubric emphasis; still run full loop for merge bar |
| Bugbot / security review | Additive pass; trainer loop still owns merge bar |
