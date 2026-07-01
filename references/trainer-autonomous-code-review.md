# Trainer — autonomous code review

**Trigger:** operator says **autonomous code review** (or **autonomous review**, **review until clean**).

Default behavior for this phrase — not a single-pass skim. Trainer routes; agent executes the loop until the stop condition.

## Routing (mandatory)

1. **trainer** — coach stance; scope = PR diff + contract surfaces if export delta (`trainer-contract-surfaces.md`).
2. **form-check** — **`file_read` `~/Projects/trainer.skill/specialists/form-check/SKILL.md`** before reviewing; run **`code-review`** or **`adversarial-review`** on the diff per form-check Section 7. Naming form-check without loading the specialist leaf is theater.
3. **review-rigor** — SEC, COR, ARC, PRF, TST scorecard per finding (`~/Projects/trainer.skill/references/trainer-codereview.md` routing).
4. **Skill-only / artifact PRs** — explicit **phylax** per `trainer-codereview.md` R-5.

Read `trainer-codereview.md` + `trainer-github-pr-commentary.md` before posting on GitHub.

## Autonomous loop (iron law)

Repeat until **no new P0–P4 findings** in a full pass:

```
PASS N:
  1. READ   — diff HEAD vs base; read every changed file body (not stat-only)
  2. EXPLORE — grep/codebase_search for callers, mirrors, scripts, tests of new symbols
  3. TRACE  — follow new logic paths; list falsifiers and bypass routes
  4. TEST   — run repo verify scripts + new/changed unit tests
  5. FIND   — ranked Bug inventory (P0–P4); no "LGTM" without evidence
  6. FIX    — fix every non-waived finding in-tree; add tests for bug classes found
  7. VERIFY — re-run tests; confirm fixes on disk
  8. STOP?  — if PASS N found zero new issues → exit loop; else PASS N+1
```

**Stop condition:** two consecutive passes with **zero new findings** after fixes, and all verify commands exit 0.

**Forbidden:**

- Single-pass review when operator said autonomous.
- Findings without file:line or runnable falsifier.
- Approving with failing verify scripts.
- Stopping at "no issues in the diff" without exploring new code paths (step 2).
- Posting APPROVE before fixes land on the branch when REQUEST_CHANGES items remain.

## Deliverables

| Artifact | When |
|----------|------|
| **PR** | Operator asked for PR — create branch, commit, push, `gh pr create` |
| **PR comment** | Canonical trainer format — `trainer-github-pr-commentary.md`; PATCH on each remediate round |
| **Bug inventory** | Every round; final round lists **fixed in HEAD** with commit or file refs |
| **Automated verification** | `### Automated verification` section with command output summaries |

Comment marker: `<!-- trainer-codereview-{repo}-{branch-slug} -->`  
Meta: `<!-- head={7-char-sha} verdict=APPROVE|REQUEST_CHANGES|BLOCK round={N} -->`

## Verify commands (default)

Run all that apply to the repo:

```bash
# Trainer autonomous code review contract (form-check routing wired)
python3 ~/Projects/trainer.skill/scripts/verify_autonomous_code_review.py

# Python harness repos (*.skill)
python3 scripts/test_*.py
bash scripts/test_*.sh
bash scripts/verify_*.sh --strict   # when present

# Product repos
bash scripts/verify_<repo>.sh
```

Record exit codes in PR comment **Automated verification** block.

## Severity / merge bar

Per `trainer-github-pr-commentary.md`: buds P0–P4 fix or waive; toebeans P0–P3. Skill/artifact repos: same discipline; no rubber-stamp on harness gaps.

## Relation to other triggers

| Operator says | Behavior |
|---------------|----------|
| code review | Single rigorous pass; fix if asked |
| **autonomous code review** | Full loop until clean + PR comment updates |
| @review-rigor | Rubric only; compose with autonomous loop when both named |
| Bugbot / security review | Additive pass; autonomous loop still owns merge bar |
