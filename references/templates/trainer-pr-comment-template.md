<!-- trainer-codereview-trainer.skill-{branch} -->
<!-- head={7-char-sha} verdict={APPROVE|REQUEST_CHANGES|BLOCK} round={1|2} -->

## Trainer / form-check code review (round {N})

**Stakes:** {vibe-safe|vibe-careful|vibe-dangerous} · **Verdict:** {APPROVE|REQUEST_CHANGES|BLOCK}

### Bug inventory

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| B-01 | P2 | ... | fixed in `{sha}` / waived: ... / open |

**Zero findings:** `No P0–P4 findings  -  full diff read; verify green.`

### Trainer notes

1. **Program notes:** what we were protecting / invariant (consequence if waived).
2. **Your form:** reusable pattern from this PR (what to repeat next time).
3. **Next session:** what to watch on the next change or merge (one concrete hook).

### Why these severities

One short paragraph: what would have broken in production or in the next PR if we had waived P1/P2.

### Round {N} remediation

- Commit(s): `{sha}`  -  {one-line summary}
- Verify: `{command}` - {pass|fail}

### Manual QA

**Default (round 1):** point at PR body test plan.

**Add shell blocks** only when: PR body lacks setup; new/changed test path in this round; operator needs a **delta** re-test command after a fix.

### Sign-off

- [x] **Automated tests (CI)**  -  [{job name}]({link to passing Actions run on this PR HEAD}) green on `{short_sha}`
- [ ] **Manual testing**  -  operator: PR body scenarios (+ comment `### Manual QA` when device QA applies)
